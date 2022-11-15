from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Callable, Dict, Iterator, List, Tuple, Type, TypeVar, Union

from lxml import etree
from typing_extensions import Annotated

from pvi._schema_utils import desc
from pvi.device import (
    LED,
    CheckBox,
    ComboBox,
    Component,
    Generic,
    Grid,
    Group,
    ProgressBar,
    ReadWidget,
    SignalR,
    SignalRef,
    SignalRW,
    SignalW,
    SignalX,
    TextRead,
    TextWrite,
    Tree,
    WriteWidget,
)

T = TypeVar("T")


@dataclass
class Bounds:
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0

    def copy(self) -> Bounds:
        return Bounds(self.x, self.y, self.w, self.h)

    def split(self, width: int, spacing: int) -> Tuple[Bounds, Bounds]:
        """Split horizontally"""
        to_split = width + spacing
        assert to_split < self.w, f"Can't split off {to_split} from {self.w}"
        left = Bounds(self.x, self.y, width, self.h)
        right = Bounds(self.x + to_split, self.y, self.w - to_split, self.h)
        return left, right

    def square(self) -> Bounds:
        """Return the largest square that will fit in self"""
        size = min(self.w, self.h)
        return Bounds(
            x=self.x + int((self.w - size) / 2),
            y=self.y + int((self.h - size) / 2),
            w=size,
            h=size,
        )

    def added_to(self, bounds: Bounds) -> Bounds:
        return Bounds(
            x=self.x + bounds.x,
            y=self.y + bounds.y,
            w=self.w + bounds.w,
            h=self.h + bounds.h,
        )


class WidgetTemplate(Generic[T]):
    screen: T

    def search(self, search) -> T:
        """Search for a widget"""
        raise NotImplementedError(self)

    def set(self, t: T, bounds: Bounds = None, **properties) -> T:
        """Return a copy of the internal representation with the bounds and
        properties set"""
        raise NotImplementedError(self)

    def create_group(
        self,
        group_object: List[T],
        children: List[WidgetFactory[T]],
        padding: Bounds = Bounds(),
    ) -> List[T]:
        """Return a group widget with its children attached and appropritately padded"""
        raise NotImplementedError(self)


WF = TypeVar("WF", bound="WidgetFactory")


@dataclass
class WidgetFactory(Generic[T]):
    bounds: Bounds

    def format(self) -> List[T]:
        """Will be filled in by from_template"""
        raise NotImplementedError(self)

    @classmethod
    def from_template(
        cls: Type[WF],
        template: WidgetTemplate[T],
        search,
        sized: Callable[[Bounds], Bounds] = Bounds.copy,
        **attrs,
    ) -> Type[WF]:
        t = template.search(search)

        class FormattableWidgetFactory(cls):  # type: ignore
            def format(self) -> List[T]:
                properties = {k: getattr(self, v) for k, v in attrs.items()}
                return [template.set(t, sized(self.bounds), **properties)]

        return FormattableWidgetFactory


@dataclass
class LabelFactory(WidgetFactory[T]):
    text: str


@dataclass
class PVWidgetFactory(WidgetFactory[T]):
    pv: str


@dataclass
class ActionFactory(WidgetFactory[T]):
    label: str
    pv: str
    value: str


class GroupType(Enum):
    GROUP = "GROUP"
    SCREEN = "SCREEN"


@dataclass
class GroupFactory(WidgetFactory[T]):
    title: str
    children: List[WidgetFactory[T]]

    @classmethod
    def from_template(
        cls,
        template: WidgetTemplate[T],
        search: GroupType,
        sized: Callable[[Bounds], Bounds] = Bounds.copy,
        make_widgets: Callable[[Bounds, str], List[WidgetFactory[T]]] = None,
        **attrs,
    ) -> Type[GroupFactory[T]]:
        @dataclass
        class FormattableGroupFactory(GroupFactory[T]):
            def format(self) -> List[T]:
                padding = sized(self.bounds)
                texts: List[T] = []
                made_widgets: List[T] = []

                if search == GroupType.SCREEN:
                    properties = {k: getattr(self, v) for k, v in attrs.items()}
                    texts.append(
                        template.set(template.screen, self.bounds, **properties)
                    )
                    # Make screen title
                    if make_widgets:
                        for widget in make_widgets(self.bounds, self.title):
                            texts += widget.format()
                    for c in self.children:
                        c.bounds.x += padding.x
                        c.bounds.y += padding.y
                        texts += c.format()

                if search == GroupType.GROUP:
                    # Make group object
                    if make_widgets:
                        for widget in make_widgets(self.bounds, self.title):
                            made_widgets += widget.format()
                    texts += template.create_group(made_widgets, self.children, padding)
                return texts

            def __post_init__(self):
                padding = sized(self.bounds)
                self.bounds = replace(self.bounds, w=padding.w, h=padding.h)

        return FormattableGroupFactory


def max_x(widgets: List[WidgetFactory[T]]) -> int:
    """Given multiple widgets, calulate the maximum x position that they occupy"""
    if widgets:
        return max(w.bounds.x + w.bounds.w for w in widgets)
    else:
        return 0


def max_y(widgets: List[WidgetFactory[T]]) -> int:
    """Given multiple widgets, calulate the maximum y position that they occupy"""
    if widgets:
        return max(w.bounds.y + w.bounds.h for w in widgets)
    else:
        return 0


def next_x(widgets: List[WidgetFactory[T]], spacing: int = 0) -> int:
    """Given multiple widgets, calulate the next feasible location for an
    additional widget in the x axis"""
    if widgets:
        return max_x(widgets) + spacing
    else:
        return 0


def next_y(widgets: List[WidgetFactory[T]], spacing: int = 0) -> int:
    """Given multiple widgets, calulate the next feasible location for an
    additional widget in the y axis"""
    if widgets:
        return max_y(widgets) + spacing
    else:
        return 0


@dataclass
class LayoutProperties:
    spacing: Annotated[int, desc("Spacing between widgets")]
    title_height: Annotated[int, desc("Height of screen title bar")]
    max_height: Annotated[int, desc("Max height of the screen")]
    group_label_height: Annotated[int, desc("Height of the group title label")]
    label_width: Annotated[int, desc("Width of the labels describing widgets")]
    widget_width: Annotated[int, desc("Width of the widgets")]
    widget_height: Annotated[int, desc("Height of the widgets (Labels use this too)")]
    group_widget_indent: Annotated[
        int, desc("Indentation of widgets within groups. Defaults to 0")
    ] = 0
    group_width_offset: Annotated[
        int, desc("Additional border width when using group objects. Defaults to 0")
    ] = 0


@dataclass
class ScreenWidgets(Generic[T]):
    label_cls: Type[LabelFactory[T]]
    led_cls: Type[PVWidgetFactory[T]]
    progress_bar_cls: Type[PVWidgetFactory[T]]
    # TODO: add bitfield, progress_bar, plot, table, image
    text_read_cls: Type[PVWidgetFactory[T]]
    check_box_cls: Type[PVWidgetFactory[T]]
    combo_box_cls: Type[PVWidgetFactory[T]]
    text_write_cls: Type[PVWidgetFactory[T]]
    action_button_cls: Type[ActionFactory[T]]

    def pv_widget(
        self,
        widget: Union[ReadWidget, WriteWidget],
        bounds: Bounds,
        pv: str,
        prefix: str,
    ) -> PVWidgetFactory[T]:
        """Convert a component that reads or writes PV's into its WidgetFactory equivalent

        Args:
            widget: The read/write widget property of a component
            bounds: The size and position of the widget (x,y,w,h).
            pv: The process variable assigned to a component

        Returns:
            A WidgetFactory representing the component
        """

        widget_factory: Dict[type, Type[PVWidgetFactory[T]]] = {
            # Currently supported instances of ReadWidget/WriteWidget Components
            LED: self.led_cls,
            ProgressBar: self.progress_bar_cls,
            TextRead: self.text_read_cls,
            CheckBox: self.check_box_cls,
            ComboBox: self.combo_box_cls,
            TextWrite: self.text_write_cls,
        }
        if isinstance(widget, (TextRead, TextWrite)):
            bounds.h *= widget.lines
        return widget_factory[type(widget)](bounds, prefix + pv)


@dataclass
class Screen(Generic[T]):
    screen_cls: Type[GroupFactory[T]]
    group_cls: Type[GroupFactory[T]]
    screen_widgets: ScreenWidgets
    layout: LayoutProperties
    prefix: str
    components: Dict[str, Component] = field(init=False, default_factory=dict)

    def screen(self, components: Tree[Component], title: str) -> WidgetFactory[T]:
        """Make the contents of the screen and determines the layout of widgets

        Args:
            components: A list of components that make up a device
            title: The title of the screen

        Returns:
            A constructed screen object

        """
        full_w = (
            self.layout.label_width + self.layout.widget_width + 2 * self.layout.spacing
        )
        screen_bounds = Bounds(h=self.layout.max_height)
        widget_dims = dict(w=full_w, h=self.layout.widget_height)
        screen_widgets: List[WidgetFactory[T]] = []
        columns: List[Bounds] = [Bounds(**widget_dims)]
        for c in components:
            last_column_bounds = columns[-1]
            next_column_bounds = Bounds(
                x=next_x(screen_widgets, self.layout.spacing),
                y=0,
                **widget_dims,
            )
            if isinstance(c, Group):
                # Create group widget
                # Note: Group adjusts bounds to fit the components
                screen_widgets.extend(
                    self.make_group_widget(
                        c,
                        screen_bounds=screen_bounds,
                        column_bounds=last_column_bounds,
                        next_column_bounds=next_column_bounds,
                    )
                )

            else:
                # Create top level widget - note this will change columns in place
                screen_widgets.extend(
                    self.make_component_widgets(
                        c,
                        column_bounds=last_column_bounds,
                        parent_bounds=screen_bounds,
                        next_column_bounds=next_column_bounds,
                        group_widget_indent=self.layout.group_widget_indent,
                    )
                )

            if next_column_bounds.y != 0:
                columns.append(next_column_bounds)

        screen_bounds.w = max_x(screen_widgets)
        screen_bounds.h = max_y(screen_widgets)
        return self.screen_cls(screen_bounds, title, screen_widgets)

    def component(
        self, c: Component, bounds: Bounds, group_widget_indent: int, add_label=True
    ) -> Iterator[WidgetFactory[T]]:
        """Convert a component into its WidgetFactory equivalents

        Args:
            c: Component object extracted from a producer.yaml
            bounds: The size and position of the component widgets (x,y,w,h).
            add_label: Whether the component has an associated label. Defaults to True.

        Yields:
            A collection of widgets representing the component
        """

        def indent_widget(bounds: Bounds, indentation: int) -> Bounds:
            """Shifts the x position of a widget. Used on top level widgets to align
            them with group indentation"""
            return Bounds(bounds.x + indentation, bounds.y, bounds.w, bounds.h)

        # Widgets are allowed to expand bounds
        if not isinstance(c, SignalRef):
            self.components[c.name] = c

        if add_label:
            left, bounds = bounds.split(self.layout.label_width, self.layout.spacing)
            yield self.screen_widgets.label_cls(
                indent_widget(left, group_widget_indent), c.get_label()
            )

        if isinstance(c, SignalX):
            yield self.screen_widgets.action_button_cls(
                indent_widget(bounds, group_widget_indent),
                c.get_label(),
                c.pv,
                c.value,
            )
        elif isinstance(c, SignalR) and c.widget:
            yield self.screen_widgets.pv_widget(
                c.widget, indent_widget(bounds, group_widget_indent), c.pv, self.prefix
            )
        elif isinstance(c, SignalRW) and c.read_pv and c.read_widget and c.widget:
            left, right = bounds.split(
                int((bounds.w - self.layout.spacing) / 2), self.layout.spacing
            )
            yield self.screen_widgets.pv_widget(
                c.widget, indent_widget(left, group_widget_indent), c.pv, self.prefix
            )
            yield self.screen_widgets.pv_widget(
                c.read_widget,
                indent_widget(right, group_widget_indent),
                c.read_pv,
                self.prefix,
            )
        elif isinstance(c, (SignalW, SignalRW)) and c.widget:
            yield self.screen_widgets.pv_widget(
                c.widget, indent_widget(bounds, group_widget_indent), c.pv, self.prefix
            )
        elif isinstance(c, SignalRef):
            yield from self.component(
                self.components[c.name],
                indent_widget(bounds, group_widget_indent),
                add_label,
            )
        # TODO: Need to handle DeviceRef

    def make_group_widget(
        self,
        c: Group[Component],
        screen_bounds: Bounds,
        column_bounds: Bounds,
        next_column_bounds: Bounds,
    ) -> List[WidgetFactory[T]]:
        """Generate widget from Group component data

        Args:
            c: Group of Component objects extracted from a device.yaml
            screen_bounds: Bounds of the top level screen
            column_bounds: Bounds of widget in current column
            parent_bounds: Size constraints from the object containing the widgets
            next_column_bounds: Bounds of widget in next column should widgets exceed
                height limits

        Returns:
            A collection of widgets representing the component

        Side Effect:
            One of {column_bounds,next_column_bounds}.y will be updated to fit the
            added widget

        """
        group = self.group(
            c,
            bounds=Bounds(column_bounds.x, column_bounds.y, h=screen_bounds.h),
        )

        if group.bounds.h + group.bounds.y <= screen_bounds.h:
            # Group fits in this column
            group.bounds.w += self.layout.group_width_offset

            # Update y for current column
            column_bounds.y = group.bounds.y + group.bounds.h + self.layout.spacing

        else:
            # Won't fit in first column, force it into next column
            group = self.group(
                c,
                bounds=Bounds(
                    next_column_bounds.x, next_column_bounds.y, h=screen_bounds.h
                ),
            )
            group.bounds.w += self.layout.group_width_offset

            next_column_bounds.y = group.bounds.y + group.bounds.h + self.layout.spacing

        return [group]

    def group(self, group: Group[Component], bounds: Bounds) -> WidgetFactory[T]:
        """Convert components within groups into widgets and lay them out within a
        group object.

        Args:
            group: Group of child components in a Layout
            bounds: The size and position of the group widget (x,y,w,h).

        Returns:
            A group object containing child widgets
        """

        full_w = (
            self.layout.label_width + self.layout.widget_width + 2 * self.layout.spacing
        )
        column_bounds = Bounds(w=full_w, h=self.layout.widget_height)
        widgets: List[WidgetFactory[T]] = []
        assert isinstance(group.layout, Grid), "Can only do grid at the moment"
        for c in group.children:
            if isinstance(c, Group):
                # TODO: make a new screen
                raise NotImplementedError(c)
            else:
                next_column_bounds = Bounds(
                    x=next_x(widgets, self.layout.spacing),
                    w=full_w,
                    h=self.layout.widget_height,
                )
                widgets = widgets + self.make_component_widgets(
                    c,
                    column_bounds=column_bounds,
                    parent_bounds=bounds,
                    next_column_bounds=next_column_bounds,
                    add_label=group.layout.labelled,
                )
                if next_column_bounds.y != 0:
                    # We have moved onto the next column
                    column_bounds = next_column_bounds

        bounds.h = max_y(widgets)
        bounds.w = max_x(widgets)
        return self.group_cls(bounds, group.get_label(), widgets)

    def make_component_widgets(
        self,
        c: Component,
        column_bounds: Bounds,
        parent_bounds: Bounds,
        next_column_bounds: Bounds,
        add_label=True,
        group_widget_indent: int = 0,
    ) -> List[WidgetFactory[T]]:
        """Generate widgets from component data and position them in a grid format

        Args:
            c: Component object extracted from a device.yaml
            column_bounds: Bounds of widget in current column
            parent_bounds: Size constraints from the object containing the widgets
            next_column_bounds: Bounds of widget in next column should widgets exceed
                height limits
            add_label: Whether the widget should have an associated label.
                Defaults to True.
            group_widget_indent: The x offset of widgets within groups.

        Returns:
            A collection of widgets representing the component

        Side Effect:
            One of {column_bounds,next_column_bounds}.y will be updated to fit the
            added widget

        """
        widgets = list(self.component(c, column_bounds, group_widget_indent, add_label))
        if max_y(widgets) > parent_bounds.h:
            # Add to next column
            widgets = list(
                self.component(c, next_column_bounds, group_widget_indent, add_label)
            )
            next_column_bounds.y = next_y(widgets, self.layout.spacing)
        else:
            column_bounds.y = next_y(widgets, self.layout.spacing)

        return widgets


def concat(items: List[List[T]]) -> List[T]:
    return [x for seq in items for x in seq]


def split_with_sep(text: str, sep: str, maxsplit: int = -1) -> List[str]:
    return [t + sep for t in text.split(sep, maxsplit=maxsplit)]


def with_title(spacing, title_height: int) -> Callable[[Bounds], Bounds]:
    return Bounds(
        spacing, spacing + title_height, 2 * spacing, 2 * spacing + title_height
    ).added_to


class EdlTemplate(WidgetTemplate[str]):
    def __init__(self, text: str):
        assert "endGroup" not in text, "Can't do groups"
        self.screen, text = split_with_sep(text, "\nendScreenProperties\n", 1)
        self.widgets = split_with_sep(text, "\nendObjectProperties\n")

    def set(self, t: str, bounds: Bounds = None, **properties) -> str:
        if bounds:
            for k in "xywh":
                properties[k] = getattr(bounds, k)
        for item, value in properties.items():
            multiline = re.compile(r"^%s {[^}]*}$" % item, re.MULTILINE | re.DOTALL)
            if multiline.search(t):
                pattern = multiline
                lines = str(value).splitlines()
                value = "\n".join(["{"] + [f'  "{x}"' for x in lines] + ["}"])
            else:
                # Single line
                pattern = re.compile(r"^%s .*$" % item, re.MULTILINE)
                if isinstance(value, str):
                    value = f'"{value}"'
            t, n = pattern.subn(f"{item} {value}", t)
            assert n == 1, f"No replacements made for {item}"
        return t

    def search(self, search: str) -> str:
        matches = [t for t in self.widgets if re.search(search, t)]
        assert len(matches) == 1, f"Got {len(matches)} matches for {search!r}"
        return matches[0]

    def create_group(
        self,
        group_object: List[str],
        children: List[WidgetFactory[str]],
        padding: Bounds = Bounds(),
    ) -> List[str]:

        texts: List[str] = []

        for c in children:
            c.bounds.x += padding.x
            c.bounds.y += padding.y
            texts += c.format()

        return group_object + texts


class AdlTemplate(WidgetTemplate[str]):
    def __init__(self, text: str):
        assert "children {" not in text, "Can't do groups"
        widgets = split_with_sep(text, "\n}\n")
        self.screen = "".join(widgets[:3])
        self.widgets = widgets[3:]

    def set(self, t: str, bounds: Bounds = None, **properties) -> str:
        if bounds:
            properties["x"] = bounds.x
            properties["y"] = bounds.y
            properties["width"] = bounds.w
            properties["height"] = bounds.h
        for item, value in properties.items():
            # Only need single line
            pattern = re.compile(r"^(\s*%s)=.*$" % item, re.MULTILINE)
            if isinstance(value, str):
                value = f'"{value}"'
            t, n = pattern.subn(r"\g<1>=" + str(value), t)
            assert n == 1, f"No replacements made for {item}"
        return t

    def search(self, search: str) -> str:
        matches = [t for t in self.widgets if re.search(search, t)]
        assert len(matches) == 1, f"Got {len(matches)} matches for {search!r}"
        return matches[0]

    def create_group(
        self,
        group_object: List[str],
        children: List[WidgetFactory[str]],
        padding: Bounds = Bounds(),
    ) -> List[str]:

        texts: List[str] = []

        for c in children:
            c.bounds.x += padding.x
            c.bounds.y += padding.y
            texts += c.format()

        return group_object + texts


class BobTemplate(WidgetTemplate[etree.ElementBase]):
    """Extract and modify elements from a template .bob file."""

    def __init__(self, text: str):
        """Parse an XML string to an element tree object."""

        self.tree = etree.parse(text)
        self.screen = self.search("Display")

    def set(
        self, t: etree.ElementBase, bounds: Bounds = None, **properties
    ) -> etree.ElementBase:
        """Modify template elements (widgets) with component data.

        Args:
            t: A template element.
            bounds: The size and position of the widget.
            **properties: The element properties (SubElements) to update.
                In the form: {[SubElement]: [Value]}

        Returns:
            The modified element.
        """
        t_copy = deepcopy(t)
        if bounds:
            properties["x"] = bounds.x
            properties["y"] = bounds.y
            properties["width"] = bounds.w
            properties["height"] = bounds.h
        for item, value in properties.items():
            try:
                t_copy.xpath(f"./{item}")[0].text = str(value)
            except IndexError as idx:
                name = t_copy.find("name").text
                raise ValueError(f"Failed to locate '{item}' in {name}") from idx
        return t_copy

    def search(self, search: str) -> etree.ElementBase:
        """Locate and extract elements from the Element tree.

        Args:
            search: The unique name of the element to extract.
                Can be found in its name subelement.

        Returns:
            The extracted element.
        """

        tree_copy = deepcopy(self.tree)
        # 'name' is the unique ID for each element
        matches = [
            element.getparent()
            for element in tree_copy.iter("name")
            if element.text == search
        ]
        assert len(matches) == 1, f"Got {len(matches)} matches for {search!r}"

        # Isolate the screen properties
        if matches[0].tag == "display":
            for child in matches[0]:
                if child.tag == "widget":
                    matches[0].remove(child)

        return matches[0]

    def create_group(
        self,
        group_object: List[etree.ElementBase],
        children: List[WidgetFactory[etree.ElementBase]],
        padding: Bounds = Bounds(),
    ) -> List[etree.ElementBase]:
        """Create an xml group object from a list of child widgets

        Args:
            group_object: Templated group xml element
            children: List of child widgets within the group
            padding: Additional placement data to fit the children to the group object.
                Defaults to Bounds().

        Returns:
            An xml group with children attached as subelements
        """
        assert (
            len(group_object) == 1
        ), f"Size of group_object is {len(group_object)}, should be 1"
        for c in children:
            group_object[0].append(c.format()[0])
        return group_object
