from dataclasses import dataclass
from pathlib import Path
from typing import List

from pvi._schema_utils import Annotated, desc
from pvi.device import Device

from .base import Formatter
from .utils import (
    ActionFactory,
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
        assert path.suffix == ".edl", "Can only write EDL files"
        template = EdlTemplate(open(Path(__file__).parent / "dls.edl").read())
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
