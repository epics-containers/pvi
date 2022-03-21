from dataclasses import dataclass
from pathlib import Path
from typing import List

from typing_extensions import Annotated

from pvi._schema_utils import desc
from pvi.device import Device

from .base import Formatter
from .utils import (
    ActionFactory,
    AdlTemplate,
    Bounds,
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
class APSFormatter(Formatter):
    spacing: Annotated[int, desc("Spacing between widgets")] = 5
    title_height: Annotated[int, desc("Height of screen title bar")] = 25
    max_height: Annotated[int, desc("Max height of the screen")] = 900
    label_width: Annotated[int, desc("Width of the widget description labels")] = 205
    widget_width: Annotated[int, desc("Width of the widgets")] = 100
    widget_height: Annotated[int, desc("Height of the widgets")] = 20

    def format(self, device: Device, prefix: str, path: Path):
        assert path.suffix == ".adl", "Can only write adl files"
        template = AdlTemplate((Path(__file__).parent / "aps.adl").read_text())
        layout = LayoutProperties(
            spacing=self.spacing,
            title_height=self.title_height,
            max_height=self.max_height,
            group_label_height=25,
            label_width=self.label_width,
            widget_width=self.widget_width,
            widget_height=self.widget_height,
            group_widget_indent=0,
            group_width_offset=0,
        )
        screen_widgets = ScreenWidgets(
            label_cls=LabelFactory.from_template(
                template, search='"Label"', textix="text"
            ),
            led_cls=PVWidgetFactory.from_template(
                template, search='"LED"', sized=Bounds.square, chan="pv"
            ),
            progress_bar_cls=PVWidgetFactory.from_template(
                template, search='"ProgressBar"', chan="pv"
            ),
            text_read_cls=PVWidgetFactory.from_template(
                template, search='"TextRead"', chan="pv"
            ),
            check_box_cls=PVWidgetFactory.from_template(
                template, search='"CheckBox"', chan="pv"
            ),
            combo_box_cls=PVWidgetFactory.from_template(
                template, search='"ComboBox"', chan="pv"
            ),
            text_write_cls=PVWidgetFactory.from_template(
                template, search='"TextWrite"', chan="pv"
            ),
            action_button_cls=ActionFactory.from_template(
                template, search='"SignalX"', label="label", chan="pv"
            ),
        )

        label_background_cls = group_box_cls = WidgetFactory.from_template(
            template, search="clr=2"
        )
        screen_title_cls = LabelFactory.from_template(
            template, search='"Title"', textix="text"
        )
        group_title_cls = LabelFactory.from_template(
            template, search='"Group"', textix="text"
        )
        group_box_cls = WidgetFactory.from_template(template, search='fill="outline"')

        def make_group_widgets(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            title_bounds = Bounds(
                bounds.x + layout.spacing,
                bounds.y + layout.spacing,
                bounds.w - 2 * layout.spacing,
                layout.group_label_height - layout.spacing,
            )
            return [
                group_box_cls(bounds),
                label_background_cls(title_bounds),
                group_title_cls(title_bounds, title),
            ]

        def make_screen_widgets(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            title_bounds = Bounds(0, 0, bounds.w, layout.title_height)
            return [
                label_background_cls(title_bounds),
                screen_title_cls(title_bounds, title),
            ]

        screen = Screen(
            screen_cls=GroupFactory.from_template(
                template,
                search=GroupType.SCREEN,
                sized=with_title(layout.spacing, layout.title_height),
                make_widgets=make_screen_widgets,
            ),
            group_cls=GroupFactory.from_template(
                template,
                search=GroupType.GROUP,
                sized=with_title(layout.spacing, layout.group_label_height),
                make_widgets=make_group_widgets,
            ),
            screen_widgets=screen_widgets,
            prefix=prefix,
            layout=layout,
        )
        title = f"{device.label} - {prefix}"
        texts = screen.screen(device.children, title).format()
        path.write_text("".join(texts))
