from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from typing_extensions import Self

from pvi._format.utils import Bounds
from pvi.device import (
    LED,
    ArrayTrace,
    BitField,
    ButtonPanel,
    CheckBox,
    ComboBox,
    Group,
    ImageRead,
    ProgressBar,
    TableRead,
    TableWrite,
    TextRead,
    TextWrite,
    ToggleButton,
    WidgetUnion,
)

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum


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
        bounds: Bounds | None = None,
        widget: WidgetUnion | None = None,
        properties: dict[str, Any] | None = None,
    ) -> T:
        """Modify template elements with component data

        Args:
            template: A template element
            bounds: The size and position of the widget
            widget: A Widget to define some additional properties for the element
            properties: The element properties in the form: {placeholder: value}
                placeholder is value to find in the template and value is the component
                value to replace it with

        Returns:
            The modified element

        """
        raise NotImplementedError(self)

    def create_group(
        self,
        group_object: list[T],
        children: list[WidgetFormatter[T]],
        padding: Bounds,
    ) -> list[T]:
        """Create a group widget with its children embedded and appropriately padded"""
        raise NotImplementedError(self)


@dataclass
class WidgetFormatter(Generic[T]):
    bounds: Bounds

    def format(self) -> list[T]:
        """Instances should be created using `from_template`, which defines `format`"""
        raise NotImplementedError(self)

    @classmethod
    def from_template(
        cls: type[Self],
        template: UITemplate[T],
        search: str,
        sized: Callable[[Bounds], Bounds] = Bounds.clone,
        widget_formatter_hook: Callable[[Bounds, str], list[WidgetFormatter[T]]]
        | None = None,
        property_map: dict[str, str] | None = None,
    ) -> type[Self]:
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

        def format(self: WidgetFormatter[T]) -> list[T]:
            properties: dict[str, str] = {}
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
                    properties,
                )
            ]

        return type(  # type: ignore
            f"""{cls.__name__}<{search.strip('"')}>""",
            (cls,),
            {"format": format},
        )


@dataclass
class LabelWidgetFormatter(WidgetFormatter[T]):
    text: str
    description: str = ""


@dataclass
class PVWidgetFormatter(WidgetFormatter[T]):
    pv: str
    widget: WidgetUnion


@dataclass
class ActionWidgetFormatter(WidgetFormatter[T]):
    label: str
    pv: str
    value: str

    @property
    def tooltip(self) -> str:
        return f"{self.pv} = {self.value}"


@dataclass
class SubScreenWidgetFormatter(WidgetFormatter[T]):
    label: str
    file_name: str
    components: Group | None = None
    macros: dict[str, str] = field(default_factory=dict)


if sys.version_info >= (3, 11):

    class GroupType(StrEnum):
        GROUP = "GROUP"
        SCREEN = "SCREEN"
else:

    class GroupType(str, Enum):
        GROUP = "GROUP"
        SCREEN = "SCREEN"


@dataclass
class GroupFormatter(WidgetFormatter[T]):
    bounds: Bounds
    title: str
    children: list[WidgetFormatter[T]]

    def format(self) -> list[T]:
        """Instances should be created using `from_template`, which defines `format`"""
        raise NotImplementedError(self)

    def __post_init__(self) -> None:
        self.resize()

    def resize(self):
        pass

    @classmethod
    def from_template(
        cls: type[Self],
        template: UITemplate[T],
        search: str,
        sized: Callable[[Bounds], Bounds] = Bounds.clone,
        widget_formatter_hook: Callable[[Bounds, str], list[WidgetFormatter[T]]]
        | None = None,
        property_map: dict[str, str] | None = None,
    ) -> type[Self]:
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

        def format(self: GroupFormatter[T]) -> list[T]:
            padding = sized(self.bounds)
            texts: list[T] = []
            made_widgets: list[T] = []

            if search == GroupType.SCREEN:
                properties: dict[str, str] = {}
                if property_map is not None:
                    for placeholder, widget_property in property_map.items():
                        assert hasattr(
                            self, widget_property
                        ), f"{self} has no property {widget_property}"
                        properties[placeholder] = getattr(self, widget_property)

                texts.append(
                    template.set(template.screen, self.bounds, properties=properties)
                )
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

        def resize(self: GroupFormatter[T]):
            """Resize based on widget template.

            Called in __init__ by parent class.

            """
            padding = sized(self.bounds)
            self.bounds = Bounds(
                x=self.bounds.x, y=self.bounds.y, w=padding.w, h=padding.h
            )
            pass

        return type(  # type: ignore
            f"{cls.__name__}<{search}>",
            (cls,),
            {"format": format, "resize": resize},
        )


@dataclass
class WidgetFormatterFactory(Generic[T]):
    header_formatter_cls: type[LabelWidgetFormatter[T]]
    label_formatter_cls: type[LabelWidgetFormatter[T]]
    led_formatter_cls: type[PVWidgetFormatter[T]]
    progress_bar_formatter_cls: type[PVWidgetFormatter[T]]
    text_read_formatter_cls: type[PVWidgetFormatter[T]]
    check_box_formatter_cls: type[PVWidgetFormatter[T]]
    toggle_formatter_cls: type[PVWidgetFormatter[T]]
    combo_box_formatter_cls: type[PVWidgetFormatter[T]]
    text_write_formatter_cls: type[PVWidgetFormatter[T]]
    table_formatter_cls: type[PVWidgetFormatter[T]]
    action_formatter_cls: type[ActionWidgetFormatter[T]]
    sub_screen_formatter_cls: type[SubScreenWidgetFormatter[T]]
    bitfield_formatter_cls: type[PVWidgetFormatter[T]]
    array_trace_formatter_cls: type[PVWidgetFormatter[T]]
    button_panel_formatter_cls: type[PVWidgetFormatter[T]]
    image_read_formatter_cls: type[PVWidgetFormatter[T]]

    def pv_widget_formatter(
        self,
        widget: WidgetUnion,
        bounds: Bounds,
        pv: str,
    ) -> PVWidgetFormatter[T]:
        """Convert a component into its WidgetFormatter equivalent

        Args:
            widget: The read/write widget property of a component
            bounds: The size and position of the widget (x,y,w,h).
            pv: The process variable assigned to a component

        Returns:
            A WidgetFormatter representing the component
        """

        widget_formatter_classes: dict[type, type[PVWidgetFormatter[T]]] = {
            # Currently supported formatters of ReadWidget/WriteWidget Components
            LED: self.led_formatter_cls,
            ProgressBar: self.progress_bar_formatter_cls,
            TextRead: self.text_read_formatter_cls,
            TableRead: self.table_formatter_cls,
            CheckBox: self.check_box_formatter_cls,
            ToggleButton: self.toggle_formatter_cls,
            ComboBox: self.combo_box_formatter_cls,
            TextWrite: self.text_write_formatter_cls,
            TableWrite: self.table_formatter_cls,
            BitField: self.bitfield_formatter_cls,
            ArrayTrace: self.array_trace_formatter_cls,
            ButtonPanel: self.button_panel_formatter_cls,
            ImageRead: self.image_read_formatter_cls,
        }
        if isinstance(widget, TextRead | TextWrite):
            bounds.h *= widget.get_lines()

        widget_formatter_cls = widget_formatter_classes[type(widget)]
        return widget_formatter_cls(bounds=bounds, pv=pv, widget=widget)


def max_x(widgets: list[WidgetFormatter[T]]) -> int:
    """Given multiple widgets, calulate the maximum x position that they occupy"""
    if widgets:
        return max(w.bounds.x + w.bounds.w for w in widgets)
    else:
        return 0


def max_y(widgets: list[WidgetFormatter[T]]) -> int:
    """Given multiple widgets, calulate the maximum y position that they occupy"""
    if widgets:
        return max(w.bounds.y + w.bounds.h for w in widgets)
    else:
        return 0


def next_x(widgets: list[WidgetFormatter[T]], spacing: int = 0) -> int:
    """Given multiple widgets, calulate the next feasible location for an
    additional widget in the x axis"""
    if widgets:
        return max_x(widgets) + spacing
    else:
        return 0


def next_y(widgets: list[WidgetFormatter[T]], spacing: int = 0) -> int:
    """Given multiple widgets, calulate the next feasible location for an
    additional widget in the y axis"""
    if widgets:
        return max_y(widgets) + spacing
    else:
        return 0
