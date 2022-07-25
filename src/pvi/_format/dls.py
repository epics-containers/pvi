from dataclasses import dataclass
from pathlib import Path
from typing import List

from lxml import etree
from typing_extensions import Annotated

from pvi._schema_utils import desc
from pvi.device import Device

from .base import Formatter
from .utils import (
    ActionFactory,
    BobTemplate,
    Bounds,
    EdlTemplate,
    GroupFactory,
    GroupType,
    LabelFactory,
    LayoutProperties,
    PVWidgetFactory,
    Screen,
    ScreenWidgets,
    WidgetFactory,
    with_title,
)


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
        layout_properties = LayoutProperties(
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
        screen_widgets = ScreenWidgets(
            label_cls=LabelFactory.from_template(
                template, search='"Label"', value="text"
            ),
            led_cls=PVWidgetFactory.from_template(
                template, search='"LED"', sized=Bounds.square, controlPv="pv"
            ),
            progress_bar_cls=PVWidgetFactory.from_template(
                template, search='"ProgressBar"', indicatorPv="pv"
            ),
            text_read_cls=PVWidgetFactory.from_template(
                template, search='"TextRead"', controlPv="pv"
            ),
            check_box_cls=PVWidgetFactory.from_template(
                template, search='"CheckBox"', controlPv="pv"
            ),
            combo_box_cls=PVWidgetFactory.from_template(
                template, search='"ComboBox"', controlPv="pv"
            ),
            text_write_cls=PVWidgetFactory.from_template(
                template, search='"TextWrite"', controlPv="pv"
            ),
            action_button_cls=ActionFactory.from_template(
                template,
                search='"SignalX"',
                onLabel="label",
                offLabel="label",
                controlPv="pv",
            ),
        )
        screen_title_cls = LabelFactory.from_template(
            template, search='"Title"', value="text"
        )
        group_title_cls = LabelFactory.from_template(
            template, search='"  Group  "', value="text"
        )
        group_box_cls = WidgetFactory.from_template(
            template, search="fillColor index 5"
        )

        def make_group_box(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            x, y, w, h = bounds.x, bounds.y, bounds.w, bounds.h
            return [
                group_box_cls(
                    Bounds(
                        x,
                        y + layout_properties.spacing,
                        w,
                        h - layout_properties.spacing,
                    )
                ),
                group_title_cls(
                    Bounds(x, y, w, layout_properties.group_label_height),
                    f"  {title}  ",
                ),
            ]

        def make_screen_title(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            return [
                screen_title_cls(
                    Bounds(0, 0, bounds.w, layout_properties.title_height), title
                )
            ]

        screen = Screen(
            screen_cls=GroupFactory.from_template(
                template,
                search=GroupType.SCREEN,
                sized=with_title(
                    layout_properties.spacing, layout_properties.title_height
                ),
                make_widgets=make_screen_title,
            ),
            group_cls=GroupFactory.from_template(
                template,
                search=GroupType.GROUP,
                sized=with_title(
                    layout_properties.spacing, layout_properties.group_label_height
                ),
                make_widgets=make_group_box,
            ),
            screen_widgets=screen_widgets,
            prefix=prefix,
            layout=layout_properties,
        )
        title = f"{device.label} - {prefix}"
        texts = screen.screen(device.children, title).format()
        path.write_text("".join(texts))

    def format_bob(self, device: Device, prefix: str, path: Path):
        template = BobTemplate(str(Path(__file__).parent / "dls.bob"))
        # LP DOCS REF: Define the layout properties
        layout_properties = LayoutProperties(
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
        screen_widgets = ScreenWidgets(
            label_cls=LabelFactory.from_template(template, search="Label", text="text"),
            led_cls=PVWidgetFactory.from_template(
                template, search="LED", sized=Bounds.square, pv_name="pv"
            ),
            progress_bar_cls=PVWidgetFactory.from_template(
                template, search="ProgressBar", pv_name="pv"
            ),
            text_read_cls=PVWidgetFactory.from_template(
                template, search="TextUpdate", pv_name="pv"
            ),
            check_box_cls=PVWidgetFactory.from_template(
                template, search="ChoiceButton", pv_name="pv"
            ),
            combo_box_cls=PVWidgetFactory.from_template(
                template, search="ComboBox", pv_name="pv"
            ),
            text_write_cls=PVWidgetFactory.from_template(
                template, search="TextEntry", pv_name="pv"
            ),
            action_button_cls=ActionFactory.from_template(
                template, search="ActionButton", text="label", pv_name="pv"
            ),
        )
        # MAKE_WIDGETS DOCS REF: Define screen and group widgets
        screen_title_cls = LabelFactory.from_template(
            template, search="Title", text="text"
        )
        group_object_cls = LabelFactory.from_template(
            template, search="Group", name="text"
        )

        def make_group_object(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            return [
                group_object_cls(
                    Bounds(bounds.x, bounds.y, bounds.w, bounds.h), f"{title}"
                )
            ]

        def make_screen_title(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            return [
                screen_title_cls(
                    Bounds(0, 0, bounds.w, layout_properties.title_height), title
                )
            ]

        # SCREEN_INI DOCS REF: Construct a screen object
        screen = Screen(
            screen_cls=GroupFactory.from_template(
                template,
                search=GroupType.SCREEN,
                sized=with_title(
                    layout_properties.spacing, layout_properties.title_height
                ),
                make_widgets=make_screen_title,
            ),
            group_cls=GroupFactory.from_template(
                template,
                search=GroupType.GROUP,
                sized=with_title(
                    layout_properties.spacing, layout_properties.group_label_height
                ),
                make_widgets=make_group_object,
            ),
            screen_widgets=screen_widgets,
            prefix=prefix,
            layout=layout_properties,
        )
        # SCREEN_FORMAT DOCS REF: Format the screen
        title = f"{device.label} - {prefix}"
        texts = screen.screen(device.children, title).format()
        # SCREEN_WRITE DOCS REF: Generate the screen file
        # The root:'Display' is always the first element in texts
        ET = etree.fromstring(etree.tostring(texts[0]))
        for element in texts[:0:-1]:
            ET.insert(ET.index(ET.find("height")) + 1, element)
        ET = ET.getroottree()
        ET.write(str(path), pretty_print=True)
