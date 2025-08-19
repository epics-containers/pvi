from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from typing import (
    Generic,
    TypeVar,
)

from pvi._format.utils import Bounds
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
from pvi.device import (
    ButtonPanel,
    Component,
    ComponentUnion,
    DeviceRef,
    Grid,
    Group,
    ImageRead,
    Row,
    SignalR,
    SignalRef,
    SignalRW,
    SignalW,
    SignalX,
    SubScreen,
    TableRead,
    TableWrite,
    Tree,
)

T = TypeVar("T")


@dataclass
class ScreenLayout:
    spacing: int
    title_height: int
    max_height: int
    group_label_height: int
    label_width: int
    widget_width: int
    widget_height: int
    group_widget_indent: int
    group_width_offset: int


@dataclass
class ScreenFormatterFactory(Generic[T]):
    screen_formatter_cls: type[GroupFormatter[T]]
    group_formatter_cls: type[GroupFormatter[T]]
    widget_formatter_factory: WidgetFormatterFactory[T]
    layout: ScreenLayout
    components: dict[str, ComponentUnion] = field(
        default_factory=dict[str, ComponentUnion]
    )
    base_file_name: str = ""

    def create_screen_formatter(
        self, components: Tree, title: str
    ) -> tuple[GroupFormatter[T], list[tuple[str, GroupFormatter[T]]]]:
        """Create an instance of `screen_cls` populated with widgets of `components`

        Args:
            components: A list of components that make up a device
            title: The title of the screen

        Returns:
            A `ScreenFormatter` plus a list of (file name, `ScreenFormatter`) for any
            nested `SubScreen`s in components

        """
        full_w = (
            self.layout.label_width + self.layout.widget_width + 2 * self.layout.spacing
        )
        screen_bounds = Bounds(h=self.layout.max_height)
        widget_dims = {"w": full_w, "h": self.layout.widget_height}
        screen_widgets: list[WidgetFormatter[T]] = []
        columns: list[Bounds] = [Bounds(**widget_dims)]

        match components:
            case [Group(layout=SubScreen()) as component]:
                # Expand single group sub screen as only component on screen
                # This is where the actual content of sub screens are created after
                # being replaced by a sub screen button in the original location
                components = component.children
            case _:
                pass

        for c in components:
            last_column_bounds = columns[-1]
            next_column_bounds = Bounds(
                x=next_x(screen_widgets, self.layout.spacing),
                y=0,
                **widget_dims,
            )
            if isinstance(c, SignalR) and isinstance(c.read_widget, ImageRead):
                if len(components) != 1:
                    # move widget to its own screen
                    c = Group(layout=SubScreen(), children=[c], name=c.name)
                else:
                    last_column_bounds.w = c.read_widget.width
                    last_column_bounds.h = c.read_widget.height
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
                        parent_bounds=screen_bounds,
                        column_bounds=last_column_bounds,
                        next_column_bounds=next_column_bounds,
                        # Indent top-level widgets to align with Group widgets
                        indent=True,
                    )
                )

            if next_column_bounds.y != 0:
                columns.append(next_column_bounds)

        sub_screens = self.create_sub_screen_formatters(screen_widgets)

        screen_bounds.w = max_x(screen_widgets)
        screen_bounds.h = max_y(screen_widgets)
        return (
            self.screen_formatter_cls(
                bounds=screen_bounds, title=title, children=screen_widgets
            ),
            sub_screens,
        )

    def create_sub_screen_formatters(
        self, screen_widgets: list[WidgetFormatter[T]]
    ) -> list[tuple[str, GroupFormatter[T]]]:
        """Create and return `ScreenFormatter`s for any `SubScreenWidgetFormatters`

        When the root screen formatter is created it will format a button that opens a
        screen when a `SubScreen` widget is found, with a `SubScreenWidgetFormatter`.
        Here we search through the components of the screen for these formatters and
        create `ScreenFormatters`s that will format the screens that those buttons will
        open.

        This will recursively call `create_screen_formatter` and
        `create_sub_screen_formatters` until no further `SubScreenWidgetFormatters` are
        found.

        Args:
            screen_widgets: List of `WidgetFormatters` containing 0-or-more
            `SubScreenFactory`s to be found

        Returns:
            List of (file name, `ScreenFormatter`) created from `SubScreenFactory`s

        """
        sub_screen_widget_formatters = [
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

        sub_screen_formatters: list[tuple[str, GroupFormatter[T]]] = []
        for sub_screen_widget_formatter in sub_screen_widget_formatters:
            if sub_screen_widget_formatter.components is None:
                # This is a reference to an existing screen - don't create it
                continue

            factory: ScreenFormatterFactory[T] = ScreenFormatterFactory(
                screen_formatter_cls=self.screen_formatter_cls,
                group_formatter_cls=self.group_formatter_cls,
                widget_formatter_factory=self.widget_formatter_factory,
                layout=self.layout,
                base_file_name=f"{sub_screen_widget_formatter.file_name}",
            )
            screen_formatter, _sub_screen_formatters = factory.create_screen_formatter(
                [sub_screen_widget_formatter.components],
                sub_screen_widget_formatter.components.name,
            )
            sub_screen_formatters.append(
                (sub_screen_widget_formatter.file_name, screen_formatter)
            )
            sub_screen_formatters.extend(_sub_screen_formatters)

        return sub_screen_formatters

    def create_group_formatters(
        self,
        c: Group,
        screen_bounds: Bounds,
        column_bounds: Bounds,
        next_column_bounds: Bounds,
    ) -> list[WidgetFormatter[T]]:
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
            c = Group(name=c.name, layout=SubScreen(), children=c.children)

        if isinstance(c.layout, SubScreen):
            return self.create_component_widget_formatters(
                Group(name=c.name, layout=SubScreen(), children=c.children),
                parent_bounds=screen_bounds,
                column_bounds=column_bounds,
                next_column_bounds=next_column_bounds,
                indent=True,
                add_label=False,
            )

        group_formatter = self.create_group_formatter(
            c, bounds=Bounds(x=column_bounds.x, y=column_bounds.y, h=screen_bounds.h)
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
                    x=next_column_bounds.x, y=next_column_bounds.y, h=screen_bounds.h
                ),
            )
            group_formatter.bounds.w += self.layout.group_width_offset

            next_column_bounds.y = (
                group_formatter.bounds.y
                + group_formatter.bounds.h
                + self.layout.spacing
            )

        return [group_formatter]

    def create_group_formatter(self, group: Group, bounds: Bounds) -> GroupFormatter[T]:
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
        widget_factories: list[WidgetFormatter[T]] = []

        assert isinstance(group.layout, Grid | SubScreen), (
            "Can only do Grid and SubScreen at the moment"
        )

        for c in group.children:
            component: Group | Component
            match c:
                case Group(layout=Grid()):
                    if is_table(c):
                        # Display table on a sub screen
                        component = Group(
                            name=c.name, layout=SubScreen(), children=c.children
                        )
                    else:
                        raise NotImplementedError(
                            "Cannot nest a Group(Grid()) in another Group on one screen"
                        )
                case _:
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
                    parent_bounds=bounds,
                    column_bounds=column_bounds,
                    next_column_bounds=next_column_bounds,
                    add_label=group.layout.labelled,
                )
            )
            if next_column_bounds.y != 0:
                # We have moved onto the next column
                column_bounds = next_column_bounds

        bounds.h = max_y(widget_factories)
        bounds.w = max_x(widget_factories)
        return self.group_formatter_cls(
            bounds=bounds, title=group.get_label(), children=widget_factories
        )

    def create_component_widget_formatters(
        self,
        c: ComponentUnion,
        parent_bounds: Bounds,
        column_bounds: Bounds,
        next_column_bounds: Bounds,
        indent: bool = False,
        add_label: bool = True,
    ) -> list[WidgetFormatter[T]]:
        """Generate widgets from component data and position them in a grid format

        Args:
            c: Component object extracted from a device.yaml
            column_bounds: Bounds of widget in current column
            parent_bounds: Size constraints from the object containing the widgets
            next_column_bounds: Bounds of widget in next column should widgets exceed
                height limits
            add_label: Whether the widget should have an associated label.
                Defaults to True.
            indent: Shift the resulting widgets to the group ident level
                Used for top-level widgets that are not inside a group.

        Returns:
            A collection of widgets representing the component

        Side Effect:
            One of {column_bounds,next_column_bounds}.y will be updated to fit the
            added widget

        """
        # Take copies so we don't modify the originals until we're done
        tmp_column_bounds = column_bounds.clone()
        tmp_next_column_bounds = next_column_bounds.clone()

        if indent:
            tmp_column_bounds.indent(self.layout.group_widget_indent)
            tmp_next_column_bounds.indent(self.layout.group_widget_indent)

        widgets = list(
            self.generate_component_formatters(c, tmp_column_bounds, add_label)
        )
        if max_y(widgets) <= parent_bounds.h:
            # Current column still fits on screen
            column_bounds.y = next_y(widgets, self.layout.spacing)
        else:
            # Widget makes current column too tall. Repeat in next column.
            widgets = list(
                self.generate_component_formatters(c, tmp_next_column_bounds, add_label)
            )
            next_column_bounds.y = next_y(widgets, self.layout.spacing)

        return widgets

    def generate_component_formatters(
        self,
        c: ComponentUnion,
        bounds: Bounds,
        add_label: bool = True,
    ) -> Iterator[WidgetFormatter[T]]:
        """Convert a component into its WidgetFormatter equivalents

        Args:
            c: Component object
            bounds: The size and position of the component widgets (x,y,w,h).
            add_label: Whether the component has an associated label. Defaults to True.

        Yields:
            A collection of widgets representing the component
        """

        # Widgets are allowed to expand bounds
        if not isinstance(c, SignalRef | Group):
            self.components[c.name] = c

        # Take a copy to modify in this scope
        component_bounds = bounds.clone()

        if isinstance(c, Group) and isinstance(c.layout, Row):
            # This Group should be formatted as a table
            if c.layout.header is not None:
                # Create table header
                assert len(c.layout.header) == len(c.children), (
                    "Header length does not match number of elements"
                )

                header_bounds = component_bounds.clone()
                if add_label:
                    # Scale the headers by the width with the label then
                    # indent them
                    original_width = len(c.layout.header) * (
                        header_bounds.w + self.layout.spacing
                    )
                    label_width = self.layout.label_width + self.layout.spacing

                    scaling_factor = (original_width - label_width) / original_width
                    header_bounds.w = int(header_bounds.w * scaling_factor)

                    header_bounds.indent(label_width)

                # Create column headers
                for column_header in c.layout.header:
                    yield self.widget_formatter_factory.header_formatter_cls(
                        bounds=header_bounds.clone(), text=column_header
                    )
                    header_bounds.x += header_bounds.w + self.layout.spacing

                # Shift down y
                component_bounds.y += self.layout.widget_height + self.layout.spacing

            row_components = c.children  # Create a widget for each row of Group
            # Allow given component width for each column, plus spacing
            component_bounds = component_bounds.tile(
                horizontal=len(c.children), spacing=self.layout.spacing
            )
        elif isinstance(c, SignalW) and isinstance(c.write_widget, ButtonPanel):
            # Convert SignalW into a SignalX with a fixed value for each action
            row_components = [
                SignalX(name=action, write_pv=c.write_pv, value=value)
                for action, value in c.write_widget.actions.items()
            ]
            # If this is a SignalRW, recreate the readback with a SignalR
            if isinstance(c, SignalRW) and c.read_widget is not None:
                row_components += [
                    SignalR(name=c.name, read_pv=c.read_pv, read_widget=c.read_widget)
                ]
        else:
            row_components = [c]  # Create one widget for row

            match c:
                case (
                    SignalR(read_widget=TableRead(widgets=widgets))
                    | SignalW(write_widget=TableWrite(widgets=widgets))
                ):
                    add_label = False  # Do not add row labels for Tables
                    component_bounds.w = 100 * len(widgets)
                    component_bounds.h *= 10  # TODO: How do we know the number of rows?
                case SignalR(read_widget=ImageRead()):
                    add_label = False
                case _:
                    pass

        if add_label:
            # Insert label and reduce width for widget
            left, row_bounds = component_bounds.split_left(
                self.layout.label_width, self.layout.spacing
            )
            yield self.widget_formatter_factory.label_formatter_cls(
                bounds=left,
                text=c.get_label(),
                tooltip=c.description or "No description provided",
            )
        else:
            # Allow full width for widget
            row_bounds = component_bounds

        if isinstance(c, SignalRef):
            yield from self.generate_component_formatters(
                self.components[c.name], row_bounds, add_label
            )
            return

        yield from self.generate_row_component_formatters(row_components, row_bounds)

    def generate_row_component_formatters(
        self,
        row_components: Sequence[Group | Component],
        row_bounds: Bounds,
    ) -> Iterator[WidgetFormatter[T]]:
        row_component_bounds = row_bounds.clone().split_into(
            len(row_components), self.layout.spacing
        )
        for rc_bounds, rc in zip(row_component_bounds, row_components, strict=True):
            # It is important to check for SignalX/SignalRW first, as they will also
            # match SignalR/SignalW

            if isinstance(rc, SignalX):
                yield self.widget_formatter_factory.action_formatter_cls(
                    bounds=rc_bounds,
                    label=rc.get_label(),
                    pv=rc.write_pv,
                    value=rc.value,
                )
            elif isinstance(rc, SignalRW):
                if rc.read_widget:
                    left, right = rc_bounds.split_into(2, self.layout.spacing)
                    yield from self.generate_write_widget(rc, left)
                    yield from self.generate_read_widget(rc, right)
                else:
                    yield from self.generate_write_widget(rc, rc_bounds)
            elif isinstance(rc, SignalW):
                yield from self.generate_write_widget(rc, rc_bounds)
            elif isinstance(rc, SignalR):
                yield from self.generate_read_widget(rc, rc_bounds)
            elif isinstance(rc, Group) and isinstance(rc.layout, SubScreen):
                yield self.widget_formatter_factory.sub_screen_formatter_cls(
                    bounds=rc_bounds,
                    label=rc.get_label(),
                    file_name=f"{self.base_file_name}_{rc.name.replace(' ', '_')}",
                    components=rc,
                )
            elif isinstance(rc, DeviceRef):
                yield self.widget_formatter_factory.sub_screen_formatter_cls(
                    bounds=rc_bounds,
                    label=" ".join(rc.macros.values()),
                    file_name=rc.ui,
                    macros=rc.macros,
                )
            else:
                print(f"Ignoring row component {rc}")

    def generate_read_widget(self, signal: SignalR, bounds: Bounds):
        if signal.read_widget is not None:
            yield self.widget_formatter_factory.pv_widget_formatter(
                signal.read_widget, bounds, signal.read_pv
            )

    def generate_write_widget(self, signal: SignalW, bounds: Bounds):
        yield self.widget_formatter_factory.pv_widget_formatter(
            signal.write_widget, bounds, signal.write_pv
        )


def is_table(component: Group) -> bool:
    return len(component.children) > 1 and all(
        isinstance(sub_component, Group) and isinstance(sub_component.layout, Row)
        for sub_component in component.children
    )
