from dataclasses import dataclass
from pathlib import Path
from typing import List

from lxml import etree
from typing_extensions import Annotated

from pvi._format.bob import BobTemplate
from pvi._format.edl import EdlTemplate
from pvi._format.screen import (
    ScreenFormatterFactory,
    ScreenLayout,
    WidgetFormatterFactory,
)
from pvi._format.widget import (
    ActionWidgetFormatter,
    GroupFormatter,
    LabelWidgetFormatter,
    PVWidgetFormatter,
    SubScreenWidgetFormatter,
    WidgetFormatter,
)
from pvi._schema_utils import desc
from pvi.device import Device

from .base import Formatter
from .utils import Bounds, GroupType, with_title


@dataclass
class DLSFormatter(Formatter):
    spacing: Annotated[int, desc("Spacing between widgets")] = 5
    title_height: Annotated[int, desc("Height of screen title bar")] = 25
    max_height: Annotated[int, desc("Max height of the screen")] = 900
    label_width: Annotated[int, desc("Width of the widget description labels")] = 115
    widget_width: Annotated[int, desc("Width of the widgets")] = 120
    widget_height: Annotated[int, desc("Height of the widgets")] = 20

    def format(self, device: Device, prefix: str, path: Path):
        if path.suffix == ".edl":
            f = self.format_edl
        elif path.suffix == ".bob":
            f = self.format_bob
        else:
            raise ValueError("Can only write .edl or .bob files")
        f(device, prefix, path)

    def format_edl(self, device: Device, prefix: str, path: Path):
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
        widget_formatter_factory = WidgetFormatterFactory(
            heading_formatter_cls=LabelWidgetFormatter.from_template(
                template,
                search='"Heading"',
                property_map=dict(value="text"),
            ),
            label_formatter_cls=LabelWidgetFormatter.from_template(
                template,
                search='"Label"',
                property_map=dict(value="text"),
            ),
            led_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search='"LED"',
                sized=Bounds.square,
                property_map=dict(controlPv="pv"),
            ),
            progress_bar_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search='"ProgressBar"',
                property_map=dict(indicatorPv="pv"),
            ),
            text_read_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search='"TextRead"',
                property_map=dict(controlPv="pv"),
            ),
            check_box_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search='"ComboBox"',
                property_map=dict(controlPv="pv"),
            ),
            combo_box_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search='"ComboBox"',
                property_map=dict(controlPv="pv"),
            ),
            text_write_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search='"TextWrite"',
                property_map=dict(controlPv="pv"),
            ),
            # Cannot handle dynamic tables so insert a label with the PV name
            table_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search='"Label"',
                property_map=dict(value="pv"),
            ),
            action_formatter_cls=ActionWidgetFormatter.from_template(
                template,
                search='"SignalX"',
                property_map=dict(onLabel="label", offLabel="label", controlPv="pv"),
            ),
            sub_screen_formatter_cls=SubScreenWidgetFormatter.from_template(
                template,
                search='"SubScreenFile"',
                property_map=dict(displayFileName="file_name"),
            ),
        )
        screen_title_cls = LabelWidgetFormatter.from_template(
            template,
            search='"Title"',
            property_map=dict(value="text"),
        )
        group_title_cls = LabelWidgetFormatter.from_template(
            template,
            search='"  Group  "',
            property_map=dict(value="text"),
        )
        group_box_cls = WidgetFormatter.from_template(
            template, search="fillColor index 5"
        )

        def create_group_box_formatter(
            bounds: Bounds, title: str
        ) -> List[WidgetFormatter[str]]:
            x, y, w, h = bounds.x, bounds.y, bounds.w, bounds.h
            return [
                group_box_cls(
                    Bounds(
                        x,
                        y + screen_layout.spacing,
                        w,
                        h - screen_layout.spacing,
                    )
                ),
                group_title_cls(
                    Bounds(x, y, w, screen_layout.group_label_height),
                    f"  {title}  ",
                ),
            ]

        def create_screen_title_formatter(
            bounds: Bounds, title: str
        ) -> List[WidgetFormatter[str]]:
            return [
                screen_title_cls(
                    Bounds(0, 0, bounds.w, screen_layout.title_height), title
                )
            ]

        formatter_factory = ScreenFormatterFactory(
            screen_formatter_cls=GroupFormatter.from_template(
                template,
                search=GroupType.SCREEN,
                sized=with_title(screen_layout.spacing, screen_layout.title_height),
                widget_formatter_hook=create_screen_title_formatter,
            ),
            group_formatter_cls=GroupFormatter.from_template(
                template,
                search=GroupType.GROUP,
                sized=with_title(
                    screen_layout.spacing, screen_layout.group_label_height
                ),
                widget_formatter_hook=create_group_box_formatter,
            ),
            widget_formatter_factory=widget_formatter_factory,
            prefix=prefix,
            layout=screen_layout,
            base_file_name=path.stem,
        )
        title = f"{device.label} - {prefix}"

        screen_formatter, sub_screens = formatter_factory.create_screen_formatter(
            device.children, title
        )

        path.write_text("".join(screen_formatter.format()))
        for sub_screen_name, sub_screen_formatter in sub_screens:
            sub_screen_path = Path(path.parent / f"{sub_screen_name}{path.suffix}")
            sub_screen_path.write_text("".join(sub_screen_formatter.format()))

    def format_bob(self, device: Device, prefix: str, path: Path):
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
        widget_formatter_factory = WidgetFormatterFactory(
            heading_formatter_cls=LabelWidgetFormatter.from_template(
                template,
                search="Heading",
                property_map=dict(text="text"),
            ),
            label_formatter_cls=LabelWidgetFormatter.from_template(
                template,
                search="Label",
                property_map=dict(text="text"),
            ),
            led_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search="LED",
                sized=Bounds.square,
                property_map=dict(pv_name="pv"),
            ),
            progress_bar_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search="ProgressBar",
                property_map=dict(pv_name="pv"),
            ),
            text_read_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search="TextUpdate",
                property_map=dict(pv_name="pv"),
            ),
            check_box_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search="ChoiceButton",
                property_map=dict(pv_name="pv"),
            ),
            combo_box_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search="ComboBox",
                property_map=dict(pv_name="pv"),
            ),
            text_write_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search="TextEntry",
                property_map=dict(pv_name="pv"),
            ),
            table_formatter_cls=PVWidgetFormatter.from_template(
                template,
                search="Table",
                property_map=dict(pv_name="pv"),
            ),
            action_formatter_cls=ActionWidgetFormatter.from_template(
                template,
                search="ActionButton",
                property_map=dict(text="label", pv_name="pv", value="value"),
            ),
            sub_screen_formatter_cls=SubScreenWidgetFormatter.from_template(
                template,
                search="SubScreen",
                property_map=dict(file="file_name"),
            ),
        )
        # MAKE_WIDGETS DOCS REF: Define screen and group widgets
        screen_title_cls = LabelWidgetFormatter.from_template(
            template,
            search="Title",
            property_map=dict(text="text"),
        )
        group_title_cls = LabelWidgetFormatter.from_template(
            template,
            search="Group",
            property_map=dict(name="text"),
        )

        def create_group_object_formatter(
            bounds: Bounds, title: str
        ) -> List[WidgetFormatter[str]]:
            return [
                group_title_cls(
                    Bounds(bounds.x, bounds.y, bounds.w, bounds.h), f"{title}"
                )
            ]

        def create_screen_title_formatter(
            bounds: Bounds, title: str
        ) -> List[WidgetFormatter[str]]:
            return [
                screen_title_cls(
                    Bounds(0, 0, bounds.w, screen_layout.title_height), title
                )
            ]

        # SCREEN_INI DOCS REF: Construct a screen object
        formatter_factory = ScreenFormatterFactory(
            screen_formatter_cls=GroupFormatter.from_template(
                template,
                search=GroupType.SCREEN,
                sized=with_title(screen_layout.spacing, screen_layout.title_height),
                widget_formatter_hook=create_screen_title_formatter,
            ),
            group_formatter_cls=GroupFormatter.from_template(
                template,
                search=GroupType.GROUP,
                sized=with_title(
                    screen_layout.spacing, screen_layout.group_label_height
                ),
                widget_formatter_hook=create_group_object_formatter,
            ),
            widget_formatter_factory=widget_formatter_factory,
            prefix=prefix,
            layout=screen_layout,
            base_file_name=path.stem,
        )
        # SCREEN_FORMAT DOCS REF: Format the screen
        title = f"{device.label} - {prefix}"

        screen_formatter, sub_screens = formatter_factory.create_screen_formatter(
            device.children, title
        )

        write_bob(screen_formatter, path)
        for sub_screen_name, sub_screen_formatter in sub_screens:
            sub_screen_path = Path(path.parent / f"{sub_screen_name}{path.suffix}")
            write_bob(sub_screen_formatter, sub_screen_path)


def write_bob(screen_formatter: GroupFormatter, path: Path):
    # SCREEN_WRITE DOCS REF: Generate the screen file
    # The root:'Display' is always the first element in texts
    texts = screen_formatter.format()
    ET = etree.fromstring(etree.tostring(texts[0]))
    for element in texts[:0:-1]:
        ET.insert(ET.index(ET.find("grid_step_y")) + 1, element)
    ET = ET.getroottree()
    ET.write(str(path), pretty_print=True)
