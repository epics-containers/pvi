from pathlib import Path

from pydantic import Field

from pvi._format.adl import AdlTemplate
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


class APSFormatter(Formatter):
    spacing: int = Field(5, description="Spacing between widgets")
    title_height: int = Field(25, description="Height of screen title bar")
    max_height: int = Field(900, description="Max height of the screen")
    label_width: int = Field(205, description="Width of the widget description labels")
    widget_width: int = Field(100, description="Width of the widgets")
    widget_height: int = Field(20, description="Height of the widgets")

    def format(self, device: Device, path: Path) -> None:
        assert path.suffix == ".adl", "Can only write adl files"
        template = AdlTemplate((Path(__file__).parent / "aps.adl").read_text())
        layout = ScreenLayout(
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
        widget_formatter_factory = WidgetFormatterFactory(
            header_formatter_cls=LabelWidgetFormatter[str].from_template(
                template,
                search='"Heading"',
                property_map={"textix": "text"},
            ),
            label_formatter_cls=LabelWidgetFormatter[str].from_template(
                template,
                search='"Label"',
                property_map={"textix": "text"},
            ),
            led_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"LED"',
                sized=Bounds.square,
                property_map={"chan": "pv"},
            ),
            progress_bar_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"ProgressBar"',
                property_map={"chan": "pv"},
            ),
            text_read_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"TextRead"',
                property_map={"chan": "pv"},
            ),
            check_box_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"CheckBox"',
                property_map={"chan": "pv"},
            ),
            toggle_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"ToggleButton"',
                property_map={"chan": "pv"},
            ),
            combo_box_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"ComboBox"',
                property_map={"chan": "pv"},
            ),
            text_write_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"TextWrite"',
                property_map={"chan": "pv"},
            ),
            # Cannot handle dynamic tables so insert a label with the PV name
            table_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"Label"',
                property_map={"textix": "pv"},
            ),
            action_formatter_cls=ActionWidgetFormatter[str].from_template(
                template,
                search='"SignalX"',
                property_map={"label": "label", "chan": "pv"},
            ),
            sub_screen_formatter_cls=SubScreenWidgetFormatter[str].from_template(
                template,
                search='"SubScreenFile"',
                property_map={"name": "file_name"},
            ),
            bitfield_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"Label"',
                property_map={"textix": "pv"},
            ),
            array_trace_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"Label"',
                property_map={"textix": "pv"},
            ),
            image_read_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"Label"',
                property_map={"textix": "pv"},
            ),
            button_panel_formatter_cls=PVWidgetFormatter[str].from_template(
                template,
                search='"Label"',
                property_map={"textix": "pv"},
            ),
        )

        label_background_formatter = WidgetFormatter[str].from_template(
            template, search="clr=2"
        )
        screen_title_formatter = LabelWidgetFormatter[str].from_template(
            template,
            search='"Title"',
            property_map={"textix": "text"},
        )
        group_title_formatter = LabelWidgetFormatter[str].from_template(
            template,
            search='"Group"',
            property_map={"textix": "text"},
        )
        group_box_formatter = WidgetFormatter[str].from_template(
            template, search='fill="outline"'
        )

        def create_group_widget_formatters(
            bounds: Bounds, title: str
        ) -> list[WidgetFormatter[str]]:
            title_bounds = Bounds(
                x=bounds.x + layout.spacing,
                y=bounds.y + layout.spacing,
                w=bounds.w - 2 * layout.spacing,
                h=layout.group_label_height - layout.spacing,
            )
            return [
                group_box_formatter(bounds=bounds),
                label_background_formatter(bounds=title_bounds),
                group_title_formatter(bounds=title_bounds, text=title),
            ]

        def create_screen_widget_formatters(
            bounds: Bounds, title: str
        ) -> list[WidgetFormatter[str]]:
            title_bounds = Bounds(x=0, y=0, w=bounds.w, h=layout.title_height)
            return [
                label_background_formatter(bounds=title_bounds),
                screen_title_formatter(bounds=title_bounds, text=title),
            ]

        formatter_factory: ScreenFormatterFactory[str] = ScreenFormatterFactory(
            screen_formatter_cls=GroupFormatter[str].from_template(
                template,
                search=GroupType.SCREEN,
                sized=with_title(layout.spacing, layout.title_height),
                widget_formatter_hook=create_screen_widget_formatters,
            ),
            group_formatter_cls=GroupFormatter[str].from_template(
                template,
                search=GroupType.GROUP,
                sized=with_title(layout.spacing, layout.group_label_height),
                widget_formatter_hook=create_group_widget_formatters,
            ),
            widget_formatter_factory=widget_formatter_factory,
            layout=layout,
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
