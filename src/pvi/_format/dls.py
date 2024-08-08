from pathlib import Path
from typing import Annotated

from lxml.etree import (
    _Element,  # pyright: ignore [reportPrivateUsage]
    fromstring,
    tostring,
)
from pydantic import Field

from pvi._format.bob import BobTemplate, find_element
from pvi._format.edl import EdlTemplate
from pvi._format.screen import (
    ScreenFormatterFactory,
    ScreenLayout,
    WidgetFormatterFactory,
)
from pvi._format.widget import (
    ActionWidgetFormatter,
    GroupFormatter,
    GroupType,
    LabelWidgetFormatter,
    PVWidgetFormatter,
    SubScreenWidgetFormatter,
    WidgetFormatter,
)
from pvi.device import Device

from .base import Formatter
from .utils import Bounds, with_title


class DLSFormatter(Formatter):
    spacing: Annotated[int, Field(description="Spacing between widgets")] = 5
    title_height: Annotated[int, Field(description="Height of screen title bar")] = 25
    max_height: Annotated[int, Field(description="Max height of the screen")] = 900
    label_width: Annotated[
        int, Field(description="Width of the widget description labels")
    ] = 150
    widget_width: Annotated[int, Field(description="Width of the widgets")] = 200
    widget_height: Annotated[int, Field(description="Height of the widgets")] = 20

    def format(self, device: Device, path: Path) -> None:
        if path.suffix == ".edl":
            f = self.format_edl
        elif path.suffix == ".bob":
            f = self.format_bob
        else:
            raise ValueError("Can only write .edl or .bob files")
        f(device, path)

    def format_edl(self, device: Device, path: Path):
        template = EdlTemplate((Path(__file__).parent / "dls.edl").read_text())
        screen_layout = ScreenLayout(
            spacing=self.spacing,
            title_height=self.title_height,
            max_height=self.max_height,
            group_label_height=10,
            label_width=self.label_width,
            widget_width=self.widget_width,
            widget_height=self.widget_height,
            group_widget_indent=5,
            group_width_offset=0,
        )
        widget_formatter_factory = WidgetFormatterFactory[str](
            header_formatter_cls=LabelWidgetFormatter[str].from_template(
                template,
                search='"Heading"',
                property_map={"value": "text"},
            ),
            label_formatter_cls=LabelWidgetFormatter[str].from_template(
                template,
                search='"Label"',
                property_map={"value": "text"},
            ),
            led_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"LED"',
                sized=Bounds.square,
                property_map={"controlPv": "pv"},
            ),
            progress_bar_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"ProgressBar"',
                property_map={"indicatorPv": "pv"},
            ),
            text_read_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"TextRead"',
                property_map={"controlPv": "pv"},
            ),
            check_box_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"ComboBox"',
                property_map={"controlPv": "pv"},
            ),
            toggle_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"ToggleButton"',
                property_map={"controlPv": "pv"},
            ),
            combo_box_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"ComboBox"',
                property_map={"controlPv": "pv"},
            ),
            text_write_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"TextWrite"',
                property_map={"controlPv": "pv"},
            ),
            # Cannot handle dynamic tables so insert a label with the PV name
            table_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"Label"',
                property_map={"value": "pv"},
            ),
            action_formatter_cls=ActionWidgetFormatter[str].from_template(
                template,
                search='"SignalX"',
                property_map={
                    "onLabel": "label",
                    "offLabel": "label",
                    "controlPv": "pv",
                },
            ),
            sub_screen_formatter_cls=SubScreenWidgetFormatter[str].from_template(
                template,
                search='"SubScreenFile"',
                property_map={"displayFileName": "file_name"},
            ),
            bitfield_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"LED"',
                property_map={"controlPv": "pv"},
            ),
            button_panel_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"Label"',
                property_map={"value": "pv"},
            ),
            array_trace_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"Label"',
                property_map={"value": "pv"},
            ),
            image_read_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"Label"',
                property_map={"value": "pv"},
            ),
        )
        screen_title_cls = LabelWidgetFormatter[str].from_template(
            template,
            search='"Title"',
            property_map={"value": "text"},
        )
        group_title_cls = LabelWidgetFormatter[str].from_template(
            template,
            search='"  Group  "',
            property_map={"value": "text"},
        )
        group_box_cls = WidgetFormatter[str].from_template(
            template, search="fillColor index 5"
        )

        def create_group_box_formatter(
            bounds: Bounds, title: str
        ) -> list[WidgetFormatter[str]]:
            x, y, w, h = bounds.x, bounds.y, bounds.w, bounds.h
            return [
                group_box_cls(
                    bounds=Bounds(
                        x=x,
                        y=y + screen_layout.spacing,
                        w=w,
                        h=h - screen_layout.spacing,
                    )
                ),
                group_title_cls(
                    bounds=Bounds(x=x, y=y, w=w, h=screen_layout.group_label_height),
                    text=f"  {title}  ",
                ),
            ]

        def create_screen_title_formatter(
            bounds: Bounds, title: str
        ) -> list[WidgetFormatter[str]]:
            return [
                screen_title_cls(
                    bounds=Bounds(x=0, y=0, w=bounds.w, h=screen_layout.title_height),
                    text=title,
                )
            ]

        formatter_factory: ScreenFormatterFactory[str] = ScreenFormatterFactory(
            screen_formatter_cls=GroupFormatter[str].from_template(
                template,
                search=GroupType.SCREEN,
                sized=with_title(screen_layout.spacing, screen_layout.title_height),
                widget_formatter_hook=create_screen_title_formatter,
            ),
            group_formatter_cls=GroupFormatter[str].from_template(
                template,
                search=GroupType.GROUP,
                sized=with_title(
                    screen_layout.spacing, screen_layout.group_label_height
                ),
                widget_formatter_hook=create_group_box_formatter,
            ),
            widget_formatter_factory=widget_formatter_factory,
            layout=screen_layout,
            base_file_name=path.stem,
        )
        title = f"{device.label}"

        screen_formatter, sub_screens = formatter_factory.create_screen_formatter(
            device.children, title
        )

        path.write_text("".join(screen_formatter.format()))
        for sub_screen_name, sub_screen_formatter in sub_screens:
            sub_screen_path = Path(path.parent / f"{sub_screen_name}{path.suffix}")
            sub_screen_path.write_text("".join(sub_screen_formatter.format()))

    def format_bob(self, device: Device, path: Path):
        template = BobTemplate(str(Path(__file__).parent / "dls.bob"))
        # LP DOCS REF: Define the layout properties
        screen_layout = ScreenLayout(
            spacing=self.spacing,
            title_height=self.title_height,
            max_height=self.max_height,
            group_label_height=26,
            label_width=self.label_width,
            widget_width=self.widget_width,
            widget_height=self.widget_height,
            group_widget_indent=18,
            group_width_offset=26,
        )
        # SW DOCS REF: Extract widget types from template file
        widget_formatter_factory: WidgetFormatterFactory[_Element] = (
            WidgetFormatterFactory(
                header_formatter_cls=LabelWidgetFormatter[_Element].from_template(
                    template,
                    search="Heading",
                    property_map={"text": "text"},
                ),
                label_formatter_cls=LabelWidgetFormatter[_Element].from_template(
                    template,
                    search="Label",
                    property_map={"text": "text", "tooltip": "description"},
                ),
                led_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="LED",
                    sized=Bounds.square,
                    property_map={"pv_name": "pv"},
                ),
                progress_bar_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="ProgressBar",
                    property_map={"pv_name": "pv"},
                ),
                bitfield_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="BitField",
                    property_map={"pv_name": "pv"},
                ),
                button_panel_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="ButtonPanel",
                    property_map={"pv_name": "pv"},
                ),
                array_trace_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="ArrayTrace",
                    property_map={"y_pv": "pv"},
                ),
                image_read_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="ImageRead",
                    property_map={"pv_name": "pv"},
                ),
                text_read_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="TextUpdate",
                    property_map={"pv_name": "pv"},
                ),
                check_box_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="ChoiceButton",
                    property_map={"pv_name": "pv"},
                ),
                toggle_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="ToggleButton",
                    property_map={"pv_name": "pv"},
                ),
                combo_box_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="ComboBox",
                    property_map={"pv_name": "pv"},
                ),
                text_write_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="TextEntry",
                    property_map={"pv_name": "pv"},
                ),
                table_formatter_cls=PVWidgetFormatter[_Element].from_template(
                    template,
                    search="Table",
                    property_map={"pv_name": "pv"},
                ),
                action_formatter_cls=ActionWidgetFormatter[_Element].from_template(
                    template,
                    search="WritePV",
                    property_map={
                        "text": "label",
                        "pv_name": "pv",
                        "value": "value",
                        "tooltip": "tooltip",
                    },
                ),
                sub_screen_formatter_cls=SubScreenWidgetFormatter[
                    _Element
                ].from_template(
                    template,
                    search="OpenDisplay",
                    property_map={
                        "file": "file_name",
                        "text": "label",
                        "macros": "macros",
                    },
                ),
            )
        )
        # MAKE_WIDGETS DOCS REF: Define screen and group widgets
        screen_title_cls = LabelWidgetFormatter[_Element].from_template(
            template,
            search="Title",
            property_map={"text": "text"},
        )
        group_title_cls = LabelWidgetFormatter[_Element].from_template(
            template,
            search="Group",
            property_map={"name": "text"},
        )

        def create_group_object_formatter(
            bounds: Bounds, title: str
        ) -> list[WidgetFormatter[_Element]]:
            return [
                group_title_cls(
                    bounds=Bounds(x=bounds.x, y=bounds.y, w=bounds.w, h=bounds.h),
                    text=f"{title}",
                )
            ]

        def create_screen_title_formatter(
            bounds: Bounds, title: str
        ) -> list[WidgetFormatter[_Element]]:
            return [
                screen_title_cls(
                    bounds=Bounds(x=0, y=0, w=bounds.w, h=screen_layout.title_height),
                    text=title,
                )
            ]

        # SCREEN_INI DOCS REF: Construct a screen object
        formatter_factory: ScreenFormatterFactory[_Element] = ScreenFormatterFactory(
            screen_formatter_cls=GroupFormatter[_Element].from_template(
                template,
                search=GroupType.SCREEN,
                sized=with_title(screen_layout.spacing, screen_layout.title_height),
                widget_formatter_hook=create_screen_title_formatter,
            ),
            group_formatter_cls=GroupFormatter[_Element].from_template(
                template,
                search=GroupType.GROUP,
                sized=with_title(
                    screen_layout.spacing, screen_layout.group_label_height
                ),
                widget_formatter_hook=create_group_object_formatter,
            ),
            widget_formatter_factory=widget_formatter_factory,
            layout=screen_layout,
            base_file_name=path.stem,
        )
        # SCREEN_FORMAT DOCS REF: Format the screen
        title = f"{device.label}"

        screen_formatter, sub_screens = formatter_factory.create_screen_formatter(
            device.children, title
        )

        write_bob(screen_formatter, path)
        for sub_screen_name, sub_screen_formatter in sub_screens:
            sub_screen_path = Path(path.parent / f"{sub_screen_name}{path.suffix}")
            write_bob(sub_screen_formatter, sub_screen_path)


def write_bob(screen_formatter: GroupFormatter[_Element], path: Path):
    # SCREEN_WRITE DOCS REF: Generate the screen file
    # The root:'Display' is always the first element in texts
    texts = screen_formatter.format()
    element_tree = fromstring(tostring(texts[0]), None)
    for element in texts[:0:-1]:
        grid_step_y = element_tree.find("grid_step_y")
        if grid_step_y is None:
            raise ValueError(f"Could not find grid_step_y in element {element}")

        element_tree.insert(element_tree.index(grid_step_y) + 1, element)

    element_tree = element_tree.getroottree()
    find_element(element_tree, "name").text = screen_formatter.title  # type: ignore
    element_tree.write(str(path), pretty_print=True)
