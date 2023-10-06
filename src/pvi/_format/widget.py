from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable, Dict, List, Optional, Type, TypeVar, Union

from pvi._format.utils import Bounds, GroupType
from pvi.device import (
    LED,
    CheckBox,
    ComboBox,
    Generic,
    Group,
    ProgressBar,
    ReadWidget,
    TableRead,
    TableWrite,
    TextRead,
    TextWrite,
    WidgetType,
    WriteWidget,
)

T = TypeVar("T")


class UITemplate(Generic[T]):
    screen: T

    def search(self, search: str) -> T:
        """Extract a snippet from the template

        Args:
            search: The search expression
                This must be unique in the template so that there is only one match

        Returns:
            The snippet matching the search

        """
        raise NotImplementedError(self)

    def set(
        self,
        template: T,
        bounds: Optional[Bounds] = None,
        widget: Optional[WidgetType] = None,
        **properties,
    ) -> T:
        """Modify template elements with component data

        Args:
            template: A template element
            bounds: The size and position of the widget
            widget: A Widget to define some additional properties for the element
            **properties: The element properties in the form: {placeholder: value}
                placeholder is value to find in the template and value is the component
                value to replace it with

        Returns:
            The modified element

        """
        raise NotImplementedError(self)

    def create_group(
        self,
        group_object: List[T],
        children: List[WidgetFormatter[T]],
        padding: Bounds = Bounds(),
    ) -> List[T]:
        """Create a group widget with its children embedded and appropriately padded"""
        raise NotImplementedError(self)


WF = TypeVar("WF", bound="WidgetFormatter")


@dataclass
class WidgetFormatter(Generic[T]):
    bounds: Bounds

    def format(self) -> List[T]:
        """Instances should be created using `from_template`, which defines `format`"""
        raise NotImplementedError(self)

    @classmethod
    def from_template(
        cls: Type[WF],
        template: UITemplate[T],
        search,
        sized: Callable[[Bounds], Bounds] = Bounds.copy,
        widget_formatter_hook: Optional[
            Callable[[Bounds, str], List[WidgetFormatter[T]]]
        ] = None,
        property_map: Optional[Dict[str, str]] = None,
    ) -> Type[WF]:
        """Create a WidgetFormatter class from the given template

        Create a `format` method that searches the template for the `search` section and
        extract it as a formattable template for a single widget. Create a child class
        of `parent_cls` implementing the method.

        Args:
            parent_cls: The class of formatter to create
            template: UI template to search for formattable widget sections
            search: Search expression for the widget section to find
            sized: Function to pad or restrict the `Bounds` of the formatted widget
            widget_formatter_hook: Hook to add additional formatters.
                Currently this is unused and available for child classes to use in
                overrided `from_template` calls.
            property_map: Map of template macro string to `WidgetFormatter` property.
                Instances of the macro will be replaced with the value of the property.
        """

        def format(self: WidgetFormatter[T]) -> List[T]:
            properties = {}
            if property_map is not None:
                for placeholder, widget_property in property_map.items():
                    assert hasattr(
                        self, widget_property
                    ), f"{self} has no property {widget_property}"
                    properties[placeholder] = getattr(self, widget_property)

            return [
                template.set(
                    template.search(search),
                    sized(self.bounds),
                    self.widget if isinstance(self, PVWidgetFormatter) else None,
                    **properties,
                )
            ]

        return type(
            f"""{cls.__name__}<{search.strip('"')}>""",
            (cls,),
            {"format": format},
        )


@dataclass
class LabelWidgetFormatter(WidgetFormatter[T]):
    text: str


@dataclass
class PVWidgetFormatter(WidgetFormatter[T]):
    pv: str
    widget: Union[ReadWidget, WriteWidget]


@dataclass
class ActionWidgetFormatter(WidgetFormatter[T]):
    label: str
    pv: str
    value: str


@dataclass
class SubScreenWidgetFormatter(WidgetFormatter[T]):
    file_name: str
    components: Optional[Group] = None
    macros: Dict[str, str] = field(default_factory=dict)


@dataclass
class GroupFormatter(WidgetFormatter[T]):
    bounds: Bounds
    title: str
    children: List[WidgetFormatter[T]]

    def format(self) -> List[T]:
        """Instances should be created using `from_template`, which defines `format`"""
        raise NotImplementedError(self)

    def __post_init__(self):
        """Call post init hooks defined in dynamically created child classes"""
        self._post_init()

    def _post_init(self):
        pass

    @classmethod
    def from_template(
        cls: Type[GroupFormatter[T]],
        template: UITemplate[T],
        search: GroupType,
        sized: Callable[[Bounds], Bounds] = Bounds.copy,
        widget_formatter_hook: Optional[
            Callable[[Bounds, str], List[WidgetFormatter[T]]]
        ] = None,
        property_map: Optional[Dict[str, str]] = None,
    ) -> Type[GroupFormatter[T]]:
        """Create a WidgetFormatter class from the given template

        Create a `format` method that searches the template for the `search` section and
        extract it as a formattable template for a single widget. Create a child class
        of `parent_cls` implementing the method.

        Args:
            parent_cls: The class of formatter to create
            template: UI template to search for formattable widget sections
            search: Search expression for the widget section to find
            sized: Function to pad or restrict the `Bounds` of the formatted widget
            widget_formatter_hook: Callable to format widgets for the group itself, such
                as a label or a box around the group components.
            property_map: Map of template macro string to `WidgetFormatter` property.
                Instances of the macro will be replaced with the value of the property.
        """

        def format(self: GroupFormatter[T]) -> List[T]:
            padding = sized(self.bounds)
            texts: List[T] = []
            made_widgets: List[T] = []

            if search == GroupType.SCREEN:
                properties = {}
                if property_map is not None:
                    for placeholder, widget_property in property_map.items():
                        assert hasattr(
                            self, widget_property
                        ), f"{self} has no property {widget_property}"
                        properties[placeholder] = getattr(self, widget_property)

                texts.append(template.set(template.screen, self.bounds, **properties))
                # Make screen title
                if widget_formatter_hook:
                    for widget in widget_formatter_hook(self.bounds, self.title):
                        texts += widget.format()
                for c in self.children:
                    c.bounds.x += padding.x
                    c.bounds.y += padding.y
                    texts += c.format()

            if search == GroupType.GROUP:
                # Make group object
                if widget_formatter_hook:
                    for widget in widget_formatter_hook(self.bounds, self.title):
                        made_widgets += widget.format()
                texts += template.create_group(made_widgets, self.children, padding)
            return texts

        def _post_init(self):
            """Add padding around component widgets

            Called in __post_init__ by parent class.

            """
            padding = sized(self.bounds)
            self.bounds = replace(self.bounds, w=padding.w, h=padding.h)

        return type(
            f"{cls.__name__}<{search.name}>",
            (cls,),
            {"format": format, "_post_init": _post_init},
        )


@dataclass
class WidgetFormatterFactory(Generic[T]):
    header_formatter_cls: Type[LabelWidgetFormatter[T]]
    label_formatter_cls: Type[LabelWidgetFormatter[T]]
    led_formatter_cls: Type[PVWidgetFormatter[T]]
    progress_bar_formatter_cls: Type[PVWidgetFormatter[T]]
    # TODO: add bitfield, progress_bar, plot, image
    text_read_formatter_cls: Type[PVWidgetFormatter[T]]
    check_box_formatter_cls: Type[PVWidgetFormatter[T]]
    combo_box_formatter_cls: Type[PVWidgetFormatter[T]]
    text_write_formatter_cls: Type[PVWidgetFormatter[T]]
    table_formatter_cls: Type[PVWidgetFormatter]
    action_formatter_cls: Type[ActionWidgetFormatter[T]]
    sub_screen_formatter_cls: Type[SubScreenWidgetFormatter[T]]

    def pv_widget_formatter(
        self,
        widget: WidgetType,
        bounds: Bounds,
        pv: str,
        prefix: str,
    ) -> PVWidgetFormatter[T]:
        """Convert a component into its WidgetFormatter equivalent

        Args:
            widget: The read/write widget property of a component
            bounds: The size and position of the widget (x,y,w,h).
            pv: The process variable assigned to a component

        Returns:
            A WidgetFormatter representing the component
        """

        widget_formatter_classes: Dict[type, Type[PVWidgetFormatter[T]]] = {
            # Currently supported formatters of ReadWidget/WriteWidget Components
            LED: self.led_formatter_cls,
            ProgressBar: self.progress_bar_formatter_cls,
            TextRead: self.text_read_formatter_cls,
            TableRead: self.table_formatter_cls,
            CheckBox: self.check_box_formatter_cls,
            ComboBox: self.combo_box_formatter_cls,
            TextWrite: self.text_write_formatter_cls,
            TableWrite: self.table_formatter_cls,
        }
        if isinstance(widget, (TextRead, TextWrite)):
            bounds.h *= widget.lines

        widget_formatter_cls = widget_formatter_classes[type(widget)]
        return widget_formatter_cls(bounds, prefix + pv, widget)


def max_x(widgets: List[WidgetFormatter[T]]) -> int:
    """Given multiple widgets, calulate the maximum x position that they occupy"""
    if widgets:
        return max(w.bounds.x + w.bounds.w for w in widgets)
    else:
        return 0


def max_y(widgets: List[WidgetFormatter[T]]) -> int:
    """Given multiple widgets, calulate the maximum y position that they occupy"""
    if widgets:
        return max(w.bounds.y + w.bounds.h for w in widgets)
    else:
        return 0


def next_x(widgets: List[WidgetFormatter[T]], spacing: int = 0) -> int:
    """Given multiple widgets, calulate the next feasible location for an
    additional widget in the x axis"""
    if widgets:
        return max_x(widgets) + spacing
    else:
        return 0


def next_y(widgets: List[WidgetFormatter[T]], spacing: int = 0) -> int:
    """Given multiple widgets, calulate the next feasible location for an
    additional widget in the y axis"""
    if widgets:
        return max_y(widgets) + spacing
    else:
        return 0
