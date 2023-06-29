from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Tuple, Type, TypeVar, Union

from typing_extensions import Annotated

from pvi._format.bob import is_table
from pvi._format.utils import Bounds
from pvi._format.widget import (
    ActionFactory,
    GroupFactory,
    LabelFactory,
    PVWidgetFactory,
    SubScreenFactory,
    WidgetFactory,
    max_x,
    max_y,
    next_x,
    next_y,
)
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
    Row,
    SignalR,
    SignalRef,
    SignalRW,
    SignalW,
    SignalX,
    SubScreen,
    TableRead,
    TableWrite,
    TextRead,
    TextWrite,
    Tree,
    WriteWidget,
)

T = TypeVar("T")


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
    heading_cls: Type[LabelFactory[T]]
    label_cls: Type[LabelFactory[T]]
    led_cls: Type[PVWidgetFactory[T]]
    progress_bar_cls: Type[PVWidgetFactory[T]]
    # TODO: add bitfield, progress_bar, plot, image
    text_read_cls: Type[PVWidgetFactory[T]]
    check_box_cls: Type[PVWidgetFactory[T]]
    combo_box_cls: Type[PVWidgetFactory[T]]
    text_write_cls: Type[PVWidgetFactory[T]]
    table_cls: Type[PVWidgetFactory]
    action_button_cls: Type[ActionFactory[T]]
    sub_screen_cls: Type[SubScreenFactory[T]]

    def pv_widget(
        self,
        widget_spec: Union[ReadWidget, WriteWidget],
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
            TableRead: self.table_cls,
            CheckBox: self.check_box_cls,
            ComboBox: self.combo_box_cls,
            TextWrite: self.text_write_cls,
            TableWrite: self.table_cls,
        }
        if isinstance(widget_spec, (TextRead, TextWrite)):
            bounds.h *= widget_spec.lines
        return widget_factory[type(widget_spec)](bounds, prefix + pv, widget_spec)


@dataclass
class Screen(Generic[T]):
    screen_cls: Type[GroupFactory[T]]
    group_cls: Type[GroupFactory[T]]
    screen_widgets: ScreenWidgets
    layout: LayoutProperties
    prefix: str
    components: Dict[str, Component] = field(init=False, default_factory=dict)
    base_file_name: str = ""

    def screen(
        self, components: Tree[Component], title: str
    ) -> Tuple[WidgetFactory[T], List[Tuple[str, WidgetFactory[T]]]]:
        """Make the contents of the screen and determines the layout of widgets

        Args:
            components: A list of components that make up a device
            title: The title of the screen

        Returns:
            A constructed screen object and a list of zero or more sub screen objects

        """
        full_w = (
            self.layout.label_width + self.layout.widget_width + 2 * self.layout.spacing
        )
        screen_bounds = Bounds(h=self.layout.max_height)
        widget_dims = dict(w=full_w, h=self.layout.widget_height)
        screen_widgets: List[WidgetFactory[T]] = []
        columns: List[Bounds] = [Bounds(**widget_dims)]

        if len(components) == 1:
            # Expand single group as only component on screen
            # This is where the actual content of sub screens are created after being
            # replaced by a sub screen button in the original location
            component = components[0]
            if isinstance(component, Group) and is_table(component):
                components = component.children

        for c in components:
            last_column_bounds = columns[-1]
            next_column_bounds = Bounds(
                x=next_x(screen_widgets, self.layout.spacing),
                y=0,
                **widget_dims,
            )
            if isinstance(c, Group) and not isinstance(c.layout, Row):
                # Create group widget containing its components
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
                # Create top level single line widget or Row of widgets
                # Note: This will change columns in place
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

        sub_screens = self.create_sub_screens(screen_widgets)

        screen_bounds.w = max_x(screen_widgets)
        screen_bounds.h = max_y(screen_widgets)
        return self.screen_cls(screen_bounds, title, screen_widgets), sub_screens

    def create_sub_screens(
        self, screen_widgets: List[WidgetFactory[T]]
    ) -> List[Tuple[str, WidgetFactory[T]]]:
        """Create and return Screens from SubScreenFactorys in screen widgets

        Args:
            screen_widgets: List of WidgetFactorys containing 0-or-more
            SubScreenFactorys to be found and

        Returns:
            List of (file name, Screen) created from found SubScreenFactorys

        """
        sub_screen_factories = [
            # At the root
            widget_factory
            for widget_factory in screen_widgets
            if isinstance(widget_factory, SubScreenFactory)
        ] + [
            # Nested in a Group
            group_widget_factory
            for widget_factory in screen_widgets
            if isinstance(widget_factory, GroupFactory)
            for group_widget_factory in widget_factory.children
            if isinstance(group_widget_factory, SubScreenFactory)
        ]

        sub_screens: List[Tuple[str, WidgetFactory[T]]] = []
        for sub_screen_factory in sub_screen_factories:
            # Create a screen with just the table
            _screen = Screen(
                screen_cls=self.screen_cls,
                group_cls=self.group_cls,
                screen_widgets=self.screen_widgets,
                prefix=self.prefix,
                layout=self.layout,
            )
            sub_screen, sub_sub_screens = _screen.screen(
                [sub_screen_factory.components], sub_screen_factory.components.name
            )
            assert not sub_sub_screens, "Only one level of sub screens allowed"
            sub_screens.append((sub_screen_factory.file_name, sub_screen))

        return sub_screens

    def component(
        self,
        c: Union[Group[Component], Component],
        bounds: Bounds,
        group_widget_indent: int,
        add_label=True,
    ) -> Iterator[WidgetFactory[T]]:
        """Convert a component into its WidgetFactory equivalents

        Args:
            c: Component object extracted from a producer.yaml
            bounds: The size and position of the component widgets (x,y,w,h).
            add_label: Whether the component has an associated label. Defaults to True.

        Yields:
            A collection of widgets representing the component
        """

        # Widgets are allowed to expand bounds
        if not isinstance(c, (SignalRef, Group)):
            self.components[c.name] = c

        # Take a copy to modify in this scope
        component_bounds = bounds.copy()

        if isinstance(c, Group) and isinstance(c.layout, Row):
            # This Group should be formatted as a table - check if headers are required
            if c.layout.header is not None:
                assert len(c.layout.header) == len(
                    c.children
                ), "Header length does not match number of elements"

                # Create column headers
                for column_header in c.layout.header:
                    yield self.screen_widgets.heading_cls(
                        indent_widget(component_bounds, group_widget_indent),
                        column_header,
                    )
                    component_bounds.x += component_bounds.w + self.layout.spacing

                # Reset x and shift down y
                component_bounds.x = bounds.x
                component_bounds.y += self.layout.widget_height + self.layout.spacing

            add_label = False  # Don't add a row label
            sub_components = c.children  # Create a widget for each row of Group
        else:
            sub_components = [c]  # Create one widget for Group/Component
            if hasattr(c, "widget") and isinstance(c.widget, (TableRead, TableWrite)):
                add_label = False  # Do not add row labels for Tables

        if add_label:
            # Insert label and reduce width for widget
            left, row_bounds = component_bounds.split(
                self.layout.label_width, self.layout.spacing
            )
            yield self.screen_widgets.label_cls(
                indent_widget(left, group_widget_indent), c.get_label()
            )
        else:
            # Allow full width for widget
            row_bounds = component_bounds

        # Actual widgets
        sub_components = (
            c.children if isinstance(c, Group) and isinstance(c.layout, Row) else [c]
        )
        for sc in sub_components:
            if isinstance(sc, SignalX):
                yield self.screen_widgets.action_button_cls(
                    indent_widget(row_bounds, group_widget_indent),
                    sc.get_label(),
                    sc.pv,
                    sc.value,
                )
            elif isinstance(sc, SignalR) and sc.widget:
                if (
                    isinstance(sc.widget, (TableRead, TableWrite))
                    and len(sc.widget.widgets) > 0
                ):
                    widget_bounds = row_bounds.copy()
                    widget_bounds.w = 100 * len(sc.widget.widgets)
                    widget_bounds.h *= 10  # TODO: How do we know the number of rows?
                else:
                    widget_bounds = row_bounds

                yield self.screen_widgets.pv_widget(
                    sc.widget,
                    indent_widget(widget_bounds, group_widget_indent),
                    sc.pv,
                    self.prefix,
                )
            elif (
                isinstance(sc, SignalRW) and sc.read_pv and sc.read_widget and sc.widget
            ):
                left, right = row_bounds.split(
                    int((row_bounds.w - self.layout.spacing) / 2), self.layout.spacing
                )
                yield self.screen_widgets.pv_widget(
                    sc.widget,
                    indent_widget(left, group_widget_indent),
                    sc.pv,
                    self.prefix,
                )
                yield self.screen_widgets.pv_widget(
                    sc.read_widget,
                    indent_widget(right, group_widget_indent),
                    sc.read_pv,
                    self.prefix,
                )
            elif isinstance(sc, (SignalW, SignalRW)) and sc.widget:
                yield self.screen_widgets.pv_widget(
                    sc.widget,
                    indent_widget(row_bounds, group_widget_indent),
                    sc.pv,
                    self.prefix,
                )
            elif isinstance(sc, SignalRef):
                yield from self.component(
                    self.components[sc.name],
                    indent_widget(row_bounds, group_widget_indent),
                    add_label,
                )
            elif isinstance(sc, Group) and isinstance(sc.layout, SubScreen):
                yield self.screen_widgets.sub_screen_cls(
                    indent_widget(row_bounds, group_widget_indent),
                    f"{self.base_file_name}_{sc.name}",
                    sc,
                )
            # TODO: Need to handle DeviceRef

            # Shift bounds along row for next widget
            row_bounds.x += row_bounds.w + self.layout.spacing

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
            next_column_bounds: Bounds of widget in next column should widgets exceed
                height limits

        Returns:
            A collection of widgets representing the component

        Side Effect:
            One of {column_bounds,next_column_bounds}.y will be updated to fit the
            added widget

        """
        if is_table(c):
            # Make a sub screen button at the root to display this Group instead of
            # embedding the components within a Group widget
            return self.make_component_widgets(
                Group(c.name, SubScreen(), c.children),
                column_bounds=column_bounds,
                parent_bounds=screen_bounds,
                next_column_bounds=next_column_bounds,
                group_widget_indent=self.layout.group_widget_indent,
                add_label=True,
            )

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
            component: Union[Group[Component], Component]
            if isinstance(c, Group) and not isinstance(c.layout, Row):
                if len(c.children) > 1 and is_table(c):
                    # Make a sub screen to display this Group
                    component = Group(c.name, SubScreen(), c.children)
                else:
                    raise NotImplementedError(
                        "Only tables can be nested in a sub screen currently"
                    )
            else:
                # Make single line with a component or Row of components
                component = c

            next_column_bounds = Bounds(
                x=next_x(widgets, self.layout.spacing),
                w=full_w,
                h=self.layout.widget_height,
            )
            widgets.extend(
                self.make_component_widgets(
                    component,
                    column_bounds=column_bounds,
                    parent_bounds=bounds,
                    next_column_bounds=next_column_bounds,
                    add_label=group.layout.labelled,
                )
            )
            if next_column_bounds.y != 0:
                # We have moved onto the next column
                column_bounds = next_column_bounds

        bounds.h = max_y(widgets)
        bounds.w = max_x(widgets)
        return self.group_cls(bounds, group.get_label(), widgets)

    def make_component_widgets(
        self,
        c: Union[Group[Component], Component],
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


def indent_widget(bounds: Bounds, indentation: int) -> Bounds:
    """Shifts the x position of a widget. Used on top level widgets to align
    them with group indentation"""
    return Bounds(bounds.x + indentation, bounds.y, bounds.w, bounds.h)
