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
    PVWidgetFactory,
    Screen,
    WidgetFactory,
    with_title,
)


@dataclass
class DLSFormatter(Formatter):
    spacing: Annotated[int, desc("Spacing between widgets")] = 5
    title_height: Annotated[int, desc("Height of screen title bar")] = 25
    max_height: Annotated[int, desc("Max height of the screen")] = 900

    def format(self, device: Device, prefix: str, path: Path):
        if path.suffix == ".edl":
            f = self.format_edl
        elif path.suffix == ".bob":
            f = self.format_bob
        f(device, prefix, path)

    def format_edl(self, device: Device, prefix: str, path: Path):
        assert path.suffix == ".edl", "Can only write EDL files"
        template = EdlTemplate((Path(__file__).parent / "dls.edl").read_text())
        screen_title_cls = LabelFactory.from_template(
            template, search='"Title"', value="text"
        )
        group_title_cls = LabelFactory.from_template(
            template, search='"  Group  "', value="text"
        )
        group_box_cls = WidgetFactory.from_template(
            template, search="fillColor index 5"
        )
        group_label_height = 10

        def make_group_widgets(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            x, y, w, h = bounds.x, bounds.y, bounds.w, bounds.h
            return [
                group_box_cls(Bounds(x, y + self.spacing, w, h - self.spacing)),
                group_title_cls(Bounds(x, y, w, group_label_height), f"  {title}  "),
            ]

        def make_screen_widgets(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            return [screen_title_cls(Bounds(0, 0, bounds.w, self.title_height), title)]

        screen = Screen(
            screen_cls=GroupFactory.from_template(
                template,
                search=GroupType.SCREEN,
                sized=with_title(self.spacing, self.title_height),
                make_widgets=make_screen_widgets,
            ),
            group_cls=GroupFactory.from_template(
                template,
                search=GroupType.GROUP,
                sized=with_title(self.spacing, group_label_height),
                make_widgets=make_group_widgets,
            ),
            label_cls=LabelFactory.from_template(
                template, search='"Label"', value="text"
            ),
            led_cls=PVWidgetFactory.from_template(
                template, search='"LED"', sized=Bounds.square, controlPv="pv"
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
            prefix=prefix,
            spacing=self.spacing,
            label_width=115,
            widget_width=60,
            widget_height=20,
            max_height=self.max_height - self.title_height - self.spacing,
        )
        title = f"{device.label} - {prefix}"
        texts = screen.screen(device.children, title).format()
        path.write_text("".join(texts))

    def format_bob(self, device: Device, prefix: str, path: Path):
        assert path.suffix == ".bob", "Can only write bob files"
        template = BobTemplate(str(Path(__file__).parent / "dls.bob"))
        screen_title_cls = LabelFactory.from_template(
            template, search="Title", text="text"
        )
        group_object_cls = LabelFactory.from_template(
            template, search="Group", name="text"
        )
        group_label_height = 20

        def make_group_object(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            group_spacing = 20

            x, y, w, h = bounds.x, bounds.y, bounds.w, bounds.h
            return [
                group_object_cls(
                    Bounds(
                        x - group_spacing,
                        y + self.spacing,
                        w + group_spacing,
                        h - self.spacing + group_spacing,
                    ),
                    f"  {title}  ",
                ),
            ]

        def make_screen_widgets(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            return [screen_title_cls(Bounds(0, 0, bounds.w, self.title_height), title)]

        screen = Screen(
            screen_cls=GroupFactory.from_template(
                template,
                search=GroupType.SCREEN,
                sized=with_title(self.spacing, self.title_height),
                make_widgets=make_screen_widgets,
            ),
            group_cls=GroupFactory.from_template(
                template,
                search=GroupType.GROUP,
                sized=with_title(self.spacing, group_label_height),
                make_widgets=make_group_object,
            ),
            label_cls=LabelFactory.from_template(template, search="Label", text="text"),
            led_cls=PVWidgetFactory.from_template(
                template, search="LED", sized=Bounds.square, pv_name="pv"
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
                template,
                search="ActionButton",
                text="label",
                pv_name="pv",
            ),
            prefix=prefix,
            spacing=self.spacing,
            label_width=115,
            widget_width=60,
            widget_height=20,
            max_height=self.max_height - self.title_height - self.spacing,
        )
        title = f"{device.label} - {prefix}"
        texts = screen.screen(device.children, title).format()

        # 'Display' is always the first element in texts
        ET = etree.fromstring(etree.tostring(texts[0]))
        for element in texts[:1:-1]:
            ET.insert(ET.index(ET.find("height")) + 1, element)
        ET = ET.getroottree()
        ET.write(str(path), pretty_print=True)
