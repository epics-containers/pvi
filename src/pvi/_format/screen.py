from __future__ import annotations

from typing import (
    Dict,
    Generic,
    Iterator,
    List,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel, Field

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
    ReadSignalType,
    Row,
    SignalR,
    SignalRef,
    SignalRW,
    SignalW,
    SignalX,
    SubScreen,
    TableWidgetTypes,
    Tree,
    WriteSignalType,
)

T = TypeVar("T")


class ScreenLayout(BaseModel):
    spacing: int = Field(description="Spacing between widgets")
    title_height: int = Field(description="Height of screen title bar")
    max_height: int = Field(description="Max height of the screen")
    group_label_height: int = Field(description="Height of the group title label")
    label_width: int = Field(description="Width of the labels describing widgets")
    widget_width: int = Field(description="Width of the widgets")
    widget_height: int = Field(
        description="Height of the widgets (Labels use this too)"
    )
    group_widget_indent: int = Field(
        0, description="Indentation of widgets within groups. Defaults to 0"
    )
    group_width_offset: int = Field(
        0, description="Additional border width when using group objects. Defaults to 0"
    )


class ScreenFormatterFactory(BaseModel, Generic[T]):
    screen_formatter_cls: Type[GroupFormatter]
    group_formatter_cls: Type[GroupFormatter]
    widget_formatter_factory: WidgetFormatterFactory
    layout: ScreenLayout
    prefix: str
    components: Dict[str, ComponentUnion] = Field(default={}, init_var=False)
    base_file_name: str = ""

    def create_screen_formatter(
        self, components: Tree, title: str
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
        widget_dims = {"w": full_w, "h": self.layout.widget_height}
        screen_widgets: List[WidgetFormatter[T]] = []
        columns: List[Bounds] = [Bounds(**widget_dims)]

        match components:
            case [Group(layout=SubScreen()) as component]:
                # Expand single group sub screen as only component on screen
                # This is where the actual content of sub screens are created after
                # being replaced by a sub screen button in the original location
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
            if sub_screen_factory.components is None:
                # This is a reference to an existing screen - don't create it
                continue

            factory: ScreenFormatterFactory = ScreenFormatterFactory(
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
        c: Group,
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
        widget_factories: List[WidgetFormatter[T]] = []

        assert isinstance(
            group.layout, (Grid, SubScreen)
        ), "Can only do Grid and SubScreen at the moment"

        for c in group.children:
            component: Union[Group, Component]
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
        indent=False,
        add_label=True,
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
        add_label=True,
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
        if not isinstance(c, (SignalRef, Group)):
            self.components[c.name] = c

        # Take a copy to modify in this scope
        component_bounds = bounds.clone()

        if isinstance(c, Group) and isinstance(c.layout, Row):
            # This Group should be formatted as a table
            if c.layout.header is not None:
                # Create table header
                assert len(c.layout.header) == len(
                    c.children
                ), "Header length does not match number of elements"

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
        elif (
            isinstance(c, (SignalW, SignalRW))
            and hasattr(c, "widget")
            and isinstance(c.widget, ButtonPanel)
        ):
            # Convert W of Signal(R)W into SignalX for each button
            row_components = [
                SignalX(name=action, pv=c.pv, value=value)
                for action, value in c.widget.actions.items()
            ]
            if isinstance(c, SignalRW):
                row_components += [
                    # TODO: Improve optional read_pv with property?
                    SignalR(name=c.name, pv=c.read_pv or c.pv, widget=c.read_widget)
                ]
        else:
            row_components = [c]  # Create one widget for row

            if hasattr(c, "widget") and isinstance(c.widget, TableWidgetTypes):
                add_label = False  # Do not add row labels for Tables
                component_bounds.w = 100 * len(c.widget.widgets)
                component_bounds.h *= 10  # TODO: How do we know the number of rows?

        if add_label:
            # Insert label and reduce width for widget
            left, row_bounds = component_bounds.split_left(
                self.layout.label_width, self.layout.spacing
            )
            yield self.widget_formatter_factory.label_formatter_cls(
                bounds=left, text=c.get_label()
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
        row_components: Sequence[Union[Group, Component]],
        row_bounds: Bounds,
    ) -> Iterator[WidgetFormatter[T]]:
        row_component_bounds = row_bounds.clone().split_into(
            len(row_components), self.layout.spacing
        )
        for rc_bounds, rc in zip(row_component_bounds, row_components):
            if isinstance(rc, SignalRW):
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
            elif isinstance(rc, SignalX):
                yield self.widget_formatter_factory.action_formatter_cls(
                    bounds=rc_bounds,
                    label=rc.get_label(),
                    pv=self.prefix + rc.pv,
                    value=rc.value,
                )
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
                    label=rc.get_label(),
                    file_name=rc.ui,
                    macros=rc.macros,
                )
            else:
                print(f"Ignoring row component {rc}")

    def generate_read_widget(self, signal: ReadSignalType, bounds: Bounds):
        if isinstance(signal, SignalRW):
            widget = signal.read_widget
            pv = signal.read_pv or signal.pv
        else:
            widget = signal.widget
            pv = signal.pv

        if widget is not None:
            yield self.widget_formatter_factory.pv_widget_formatter(
                widget, bounds, pv, self.prefix
            )

    def generate_write_widget(self, signal: WriteSignalType, bounds: Bounds):
        if signal.widget is not None:
            yield self.widget_formatter_factory.pv_widget_formatter(
                signal.widget, bounds, signal.pv, self.prefix
            )


def is_table(component: Group) -> bool:
    return len(component.children) > 1 and all(
        isinstance(sub_component, Group) and isinstance(sub_component.layout, Row)
        for sub_component in component.children
    )
