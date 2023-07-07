from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Tuple, Type, TypeVar, Union

from typing_extensions import Annotated

from pvi._format.bob import is_table
from pvi._format.utils import Bounds, indent_widget
from pvi._format.widget import (
    GroupFormatter,
    SubScreenWidgetFormatter,
    WidgetFormatter,
    WidgetFormatterFactory,
    max_x,
    max_y,
    next_x,
    next_y,
)
from pvi._schema_utils import desc
from pvi.device import (
    Component,
    Generic,
    Grid,
    Group,
    Row,
    SignalR,
    SignalRef,
    SignalRW,
    SignalW,
    SignalX,
    SubScreen,
    TableWidgetTypes,
    Tree,
)

T = TypeVar("T")


@dataclass
class ScreenLayout:
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
class ScreenFormatterFactory(Generic[T]):
    screen_formatter_cls: Type[GroupFormatter[T]]
    group_formatter_cls: Type[GroupFormatter[T]]
    widget_formatter_factory: WidgetFormatterFactory
    layout: ScreenLayout
    prefix: str
    components: Dict[str, Component] = field(init=False, default_factory=dict)
    base_file_name: str = ""

    def create_screen_formatter(
        self, components: Tree[Component], title: str
    ) -> Tuple[GroupFormatter[T], List[Tuple[str, GroupFormatter[T]]]]:
        """Create an instance of `screen_cls` populated with widgets of `components`

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
        screen_widgets: List[WidgetFormatter[T]] = []
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
                # Create embedded group widget containing its components
                # Note: Group adjusts bounds to fit the components
                screen_widgets.extend(
                    self.create_group_formatters(
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
                    self.create_component_widget_formatters(
                        c,
                        column_bounds=last_column_bounds,
                        parent_bounds=screen_bounds,
                        next_column_bounds=next_column_bounds,
                        group_widget_indent=self.layout.group_widget_indent,
                    )
                )

            if next_column_bounds.y != 0:
                columns.append(next_column_bounds)

        sub_screens = self.create_sub_screen_formatters(screen_widgets)

        screen_bounds.w = max_x(screen_widgets)
        screen_bounds.h = max_y(screen_widgets)
        return (
            self.screen_formatter_cls(screen_bounds, title, screen_widgets),
            sub_screens,
        )

    def create_sub_screen_formatters(
        self, screen_widgets: List[WidgetFormatter[T]]
    ) -> List[Tuple[str, GroupFormatter[T]]]:
        """Create and return Screens from SubScreenFactorys in screen widgets

        Args:
            screen_widgets: List of WidgetFormatters containing 0-or-more
            SubScreenFactorys to be found and

        Returns:
            List of (file name, Screen) created from found SubScreenFactorys

        """
        sub_screen_factories = [
            # At the root
            widget_factory
            for widget_factory in screen_widgets
            if isinstance(widget_factory, SubScreenWidgetFormatter)
        ] + [
            # Nested in a Group
            group_widget_factory
            for widget_factory in screen_widgets
            if isinstance(widget_factory, GroupFormatter)
            for group_widget_factory in widget_factory.children
            if isinstance(group_widget_factory, SubScreenWidgetFormatter)
        ]

        sub_screen_formatters: List[Tuple[str, GroupFormatter[T]]] = []
        for sub_screen_factory in sub_screen_factories:
            factory = ScreenFormatterFactory(
                screen_formatter_cls=self.screen_formatter_cls,
                group_formatter_cls=self.group_formatter_cls,
                widget_formatter_factory=self.widget_formatter_factory,
                prefix=self.prefix,
                layout=self.layout,
            )
            screen_formatter, sub_screen_formatter = factory.create_screen_formatter(
                [sub_screen_factory.components], sub_screen_factory.components.name
            )
            assert not sub_screen_formatter, "Only one level of sub screens allowed"
            sub_screen_formatters.append(
                (sub_screen_factory.file_name, screen_formatter)
            )

        return sub_screen_formatters

    def create_group_formatters(
        self,
        c: Group[Component],
        screen_bounds: Bounds,
        column_bounds: Bounds,
        next_column_bounds: Bounds,
    ) -> List[WidgetFormatter[T]]:
        """Create widget formatters for a Group

        This could either be a list of widget formatters, or a single group formatter,
        depending on the layout.

        Args:
            c: Group of Component objects extracted from a device.yaml
            screen_bounds: Bounds of the top level screen
            column_bounds: Bounds of widget in current column
            next_column_bounds: Bounds of widget in next column should widgets exceed
                height limits

        Returns:
            Widget formatters representing the component

        Side Effect:
            One of {column_bounds,next_column_bounds}.y will be updated to fit the
            added widget

        """
        if is_table(c):
            # Make a sub screen button at the root to display this Group instead of
            # embedding the components within a Group widget
            return self.create_component_widget_formatters(
                Group(c.name, SubScreen(), c.children),
                column_bounds=column_bounds,
                parent_bounds=screen_bounds,
                next_column_bounds=next_column_bounds,
                group_widget_indent=self.layout.group_widget_indent,
                add_label=True,
            )

        group_formatter = self.create_group_formatter(
            c,
            bounds=Bounds(column_bounds.x, column_bounds.y, h=screen_bounds.h),
        )

        if group_formatter.bounds.h + group_formatter.bounds.y <= screen_bounds.h:
            # Group fits in this column
            group_formatter.bounds.w += self.layout.group_width_offset

            # Update y for current column
            column_bounds.y = (
                group_formatter.bounds.y
                + group_formatter.bounds.h
                + self.layout.spacing
            )
        else:
            # Won't fit in first column, recreate in next column
            group_formatter = self.create_group_formatter(
                c,
                bounds=Bounds(
                    next_column_bounds.x, next_column_bounds.y, h=screen_bounds.h
                ),
            )
            group_formatter.bounds.w += self.layout.group_width_offset

            next_column_bounds.y = (
                group_formatter.bounds.y
                + group_formatter.bounds.h
                + self.layout.spacing
            )

        return [group_formatter]

    def create_group_formatter(
        self, group: Group[Component], bounds: Bounds
    ) -> GroupFormatter[T]:
        """Convert components within groups into widgets and lay them out within a
        group object.

        Args:
            group: Group of child Components in a Layout
            bounds: The size and position of the group Widget (x,y,w,h).

        Returns:
            A group object containing child widgets
        """

        full_w = (
            self.layout.label_width + self.layout.widget_width + 2 * self.layout.spacing
        )
        column_bounds = Bounds(w=full_w, h=self.layout.widget_height)
        widget_factories: List[WidgetFormatter[T]] = []

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
                x=next_x(widget_factories, self.layout.spacing),
                w=full_w,
                h=self.layout.widget_height,
            )
            widget_factories.extend(
                self.create_component_widget_formatters(
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

        bounds.h = max_y(widget_factories)
        bounds.w = max_x(widget_factories)
        return self.group_formatter_cls(bounds, group.get_label(), widget_factories)

    def create_component_widget_formatters(
        self,
        c: Union[Group[Component], Component],
        column_bounds: Bounds,
        parent_bounds: Bounds,
        next_column_bounds: Bounds,
        add_label=True,
        group_widget_indent: int = 0,
    ) -> List[WidgetFormatter[T]]:
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
        widgets = list(
            self.generate_component_formatters(
                c, column_bounds, group_widget_indent, add_label
            )
        )
        if max_y(widgets) > parent_bounds.h:
            # Add to next column
            widgets = list(
                self.generate_component_formatters(
                    c, next_column_bounds, group_widget_indent, add_label
                )
            )
            next_column_bounds.y = next_y(widgets, self.layout.spacing)
        else:
            column_bounds.y = next_y(widgets, self.layout.spacing)

        return widgets

    def generate_component_formatters(
        self,
        c: Union[Group[Component], Component],
        bounds: Bounds,
        group_widget_indent: int,
        add_label=True,
    ) -> Iterator[WidgetFormatter[T]]:
        """Convert a component into its WidgetFormatter equivalents

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
                    yield self.widget_formatter_factory.heading_formatter_cls(
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
            if hasattr(c, "widget") and isinstance(c.widget, TableWidgetTypes):
                add_label = False  # Do not add row labels for Tables

        if add_label:
            # Insert label and reduce width for widget
            left, row_bounds = component_bounds.split(
                self.layout.label_width, self.layout.spacing
            )
            yield self.widget_formatter_factory.label_formatter_cls(
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
                yield self.widget_formatter_factory.action_formatter_cls(
                    indent_widget(row_bounds, group_widget_indent),
                    sc.get_label(),
                    self.prefix + sc.pv,
                    sc.value,
                )
            elif isinstance(sc, SignalR) and sc.widget:
                if (
                    isinstance(sc.widget, TableWidgetTypes)
                    and len(sc.widget.widgets) > 0
                ):
                    widget_bounds = row_bounds.copy()
                    widget_bounds.w = 100 * len(sc.widget.widgets)
                    widget_bounds.h *= 10  # TODO: How do we know the number of rows?
                else:
                    widget_bounds = row_bounds

                yield self.widget_formatter_factory.pv_widget_formatter(
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
                yield self.widget_formatter_factory.pv_widget_formatter(
                    sc.widget,
                    indent_widget(left, group_widget_indent),
                    sc.pv,
                    self.prefix,
                )
                yield self.widget_formatter_factory.pv_widget_formatter(
                    sc.read_widget,
                    indent_widget(right, group_widget_indent),
                    sc.read_pv,
                    self.prefix,
                )
            elif isinstance(sc, (SignalW, SignalRW)) and sc.widget:
                yield self.widget_formatter_factory.pv_widget_formatter(
                    sc.widget,
                    indent_widget(row_bounds, group_widget_indent),
                    sc.pv,
                    self.prefix,
                )
            elif isinstance(sc, SignalRef):
                yield from self.generate_component_formatters(
                    self.components[sc.name],
                    indent_widget(row_bounds, group_widget_indent),
                    add_label,
                )
            elif isinstance(sc, Group) and isinstance(sc.layout, SubScreen):
                yield self.widget_formatter_factory.sub_screen_formatter_cls(
                    indent_widget(row_bounds, group_widget_indent),
                    f"{self.base_file_name}_{sc.name}",
                    sc,
                )
            # TODO: Need to handle DeviceRef

            # Shift bounds along row for next widget
            row_bounds.x += row_bounds.w + self.layout.spacing
