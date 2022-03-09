from dataclasses import dataclass
from pathlib import Path
from typing import List

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
    def format(self, device: Device, prefix: str, path: Path):
        assert path.suffix == ".adl", "Can only write adl files"
        template = AdlTemplate((Path(__file__).parent / "aps.adl").read_text())

        layout_properties = LayoutProperties(
            spacing=5,
            title_height=25,
            max_height=900,
            group_label_height=25,
            label_width=205,
            widget_width=100,
            widget_height=20,
            group_widget_indent=0,
        )

        screen_widgets = ScreenWidgets(
            label_cls=LabelFactory.from_template(
                template, search='"Label"', textix="text"
            ),
            led_cls=PVWidgetFactory.from_template(
                template, search='"LED"', sized=Bounds.square, chan="pv"
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
                bounds.x + layout_properties.spacing,
                bounds.y + layout_properties.spacing,
                bounds.w - 2 * layout_properties.spacing,
                layout_properties.group_label_height - layout_properties.spacing,
            )
            return [
                group_box_cls(bounds),
                label_background_cls(title_bounds),
                group_title_cls(title_bounds, title),
            ]

        def make_screen_widgets(bounds: Bounds, title: str) -> List[WidgetFactory[str]]:
            title_bounds = Bounds(0, 0, bounds.w, layout_properties.title_height)
            return [
                label_background_cls(title_bounds),
                screen_title_cls(title_bounds, title),
            ]

        screen = Screen(
            screen_cls=GroupFactory.from_template(
                template,
                search=GroupType.SCREEN,
                sized=with_title(
                    layout_properties.spacing, layout_properties.title_height
                ),
                make_widgets=make_screen_widgets,
            ),
            group_cls=GroupFactory.from_template(
                template,
                search=GroupType.GROUP,
                sized=with_title(
                    layout_properties.spacing, layout_properties.group_label_height
                ),
                make_widgets=make_group_widgets,
            ),
            screen_widgets=screen_widgets,
            prefix=prefix,
            layout=layout_properties,
        )
        title = f"{device.label} - {prefix}"
        texts = screen.screen(device.children, title).format()
        path.write_text("".join(texts))
