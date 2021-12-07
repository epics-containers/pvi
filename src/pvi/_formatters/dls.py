from dataclasses import dataclass
from pathlib import Path
from typing import List

from pvi._utils import Annotated, desc
from pvi.device import Device

from .base import Formatter
from .utils import (
    ActionFactory,
    Bounds,
    EdlFile,
    EdlWidget,
    LabelFactory,
    PVWidgetFactory,
    Screen,
    WidgetFactory,
)


@dataclass
class DLSFormatter(Formatter):
    spacing: Annotated[int, desc("Spacing between widgets")] = 5
    title_height: Annotated[int, desc("Height of screen title bar")] = 25
    max_height: Annotated[int, desc("Max height of the screen")] = 900

    def format(self, device: Device, prefix: str, path: Path):
        assert path.suffix == ".edl", "Can only write EDL files"
        ef = EdlFile(open(Path(__file__).parent / "dls.edl").read())
        screen_title_cls = ef.widget_factory(LabelFactory, '"Title"', value="text")
        group_title_cls = ef.widget_factory(LabelFactory, '"  Group  "', value="text")
        group_box_cls = ef.widget_factory(WidgetFactory, "fillColor index 5")
        group_label_height = 10

        def make_group_widgets(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            x, y, w, h = bounds.x, bounds.y, bounds.w, bounds.h
            return [
                group_box_cls(Bounds(x, y + self.spacing, w, h - self.spacing)),
                group_title_cls(Bounds(x, y, w, group_label_height), f"  {title}  "),
            ]

        def make_screen_widgets(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            return [screen_title_cls(Bounds(0, 0, bounds.w, self.title_height), title)]

        def make_square(text: str, bounds: Bounds):
            # Modify bounds so it's square and centred
            x = bounds.x + int((bounds.w - bounds.h) / 2)
            bounds = Bounds(x, bounds.y, bounds.h, bounds.h)
            return EdlWidget.bounded(text, bounds)

        def padding(title_height: int) -> Bounds:
            return Bounds(
                self.spacing,
                self.spacing + title_height,
                2 * self.spacing,
                2 * self.spacing + title_height,
            )

        screen = Screen(
            screen_cls=ef.group_factory(
                padding(self.title_height), make_screen_widgets, is_screen=True
            ),
            group_cls=ef.group_factory(padding(group_label_height), make_group_widgets),
            label_cls=ef.widget_factory(LabelFactory, '"Label"', value="text"),
            led_cls=ef.widget_factory(
                PVWidgetFactory, '"LED"', make_square, controlPv="pv"
            ),
            text_read_cls=ef.widget_factory(
                PVWidgetFactory, '"TextRead"', controlPv="pv"
            ),
            check_box_cls=ef.widget_factory(
                PVWidgetFactory, '"CheckBox"', controlPv="pv"
            ),
            combo_box_cls=ef.widget_factory(
                PVWidgetFactory, '"ComboBox"', controlPv="pv"
            ),
            text_write_cls=ef.widget_factory(
                PVWidgetFactory, '"TextWrite"', controlPv="pv"
            ),
            action_button_cls=ef.widget_factory(
                ActionFactory,
                '"SignalX"',
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
