import re
from dataclasses import dataclass, field, replace
from typing import Callable, Dict, Iterator, List, Tuple, Type, TypeVar, Union

from pvi.device import (
    LED,
    CheckBox,
    ComboBox,
    Component,
    Generic,
    Grid,
    Group,
    ReadWidget,
    SignalR,
    SignalRef,
    SignalRW,
    SignalW,
    SignalX,
    TextRead,
    TextWrite,
    Tree,
    WriteWidget,
)

T = TypeVar("T")


@dataclass
class Bounds:
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0

    def split(self, w: int, spacing: int) -> "Bounds":
        assert w + spacing < self.w, f"Can't split off {w + spacing} from {self.w}"
        dims = Bounds(self.x, self.y, w, self.h)
        self.x += w + spacing
        self.w -= w + spacing
        return dims


@dataclass
class WidgetFactory(Generic[T]):
    bounds: Bounds

    def format(self) -> List[T]:
        raise NotImplementedError(self)


@dataclass
class LabelFactory(WidgetFactory[T]):
    text: str


@dataclass
class PVWidgetFactory(WidgetFactory[T]):
    pv: str


@dataclass
class ActionFactory(WidgetFactory[T]):
    label: str
    pv: str
    value: str


@dataclass
class GroupFactory(WidgetFactory[T]):
    title: str
    children: List[WidgetFactory[T]]


def max_x(widgets: List[WidgetFactory[T]], spacing: int = 0) -> int:
    if widgets:
        return max(w.bounds.x + w.bounds.w + spacing for w in widgets)
    else:
        return 0


def max_y(widgets: List[WidgetFactory[T]], spacing: int = 0) -> int:
    if widgets:
        return max(w.bounds.y + w.bounds.h + spacing for w in widgets)
    else:
        return 0


@dataclass
class Screen(Generic[T]):
    screen_cls: Type[GroupFactory[T]]
    group_cls: Type[GroupFactory[T]]
    label_cls: Type[LabelFactory[T]]
    led_cls: Type[PVWidgetFactory[T]]
    # TODO: add bitfield, progress_bar, plot, table, image
    text_read_cls: Type[PVWidgetFactory[T]]
    check_box_cls: Type[PVWidgetFactory[T]]
    combo_box_cls: Type[PVWidgetFactory[T]]
    text_write_cls: Type[PVWidgetFactory[T]]
    action_button_cls: Type[ActionFactory[T]]
    prefix: str
    spacing: int
    label_width: int
    widget_width: int
    widget_height: int
    max_height: int
    components: Dict[str, Component] = field(init=False, default_factory=dict)

    def screen(self, components: Tree[Component], title: str) -> WidgetFactory[T]:
        # Make the contents of the screen
        widgets: List[WidgetFactory[T]] = []
        x, y = 0, 0
        for c in components:
            if isinstance(c, Group):
                group = self.group(c, bounds=Bounds(x, y))
                if group.bounds.h + group.bounds.x > self.max_height:
                    if group.bounds.h > self.max_height:
                        # Group will be wider to fit
                        h = self.max_height
                    else:
                        # Group will cap to height
                        h = 0
                    # Retry in a new column
                    x = max_x(widgets)
                    y = 0
                    group = self.group(c, bounds=Bounds(x, y, h=h))
                widgets.append(group)
            else:
                raise NotImplementedError(c)
        bounds = Bounds(w=max_x(widgets), h=max_y(widgets))
        # Then the screen itself
        return self.screen_cls(bounds, title, widgets)

    def component(
        self, c: Component, bounds: Bounds, add_label=True
    ) -> Iterator[WidgetFactory[T]]:
        # Widgets are allowed to expand bounds
        if not isinstance(c, SignalRef):
            self.components[c.name] = c
        if add_label:
            yield self.label_cls(bounds.split(self.label_width, self.spacing), c.label)
        if isinstance(c, SignalX):
            yield self.action_button_cls(bounds, c.label, c.pv, c.value)
        elif isinstance(c, SignalR) and c.widget:
            yield self.pv_widget(c.widget, bounds, c.pv)
        elif isinstance(c, SignalRW) and c.read_pv and c.read_widget and c.widget:
            left_bounds = bounds.split(int((bounds.w - self.spacing) / 2), self.spacing)
            yield self.pv_widget(c.widget, left_bounds, c.pv)
            yield self.pv_widget(c.read_widget, bounds, c.read_pv)
        elif isinstance(c, (SignalW, SignalRW)) and c.widget:
            yield self.pv_widget(c.widget, bounds, c.pv)
        elif isinstance(c, SignalRef):
            yield from self.component(self.components[c.name], bounds, add_label)
        # TODO: Need to handle DeviceRef

    def pv_widget(
        self, widget: Union[ReadWidget, WriteWidget], bounds: Bounds, pv: str
    ) -> PVWidgetFactory[T]:
        widget_factory: Dict[type, Type[PVWidgetFactory[T]]] = {
            LED: self.led_cls,
            TextRead: self.text_read_cls,
            CheckBox: self.check_box_cls,
            ComboBox: self.combo_box_cls,
            TextWrite: self.text_write_cls,
        }
        if isinstance(widget, (TextRead, TextWrite)):
            bounds.h *= widget.lines
        return widget_factory[type(widget)](bounds, self.prefix + pv)

    def group(self, group: Group[Component], bounds: Bounds) -> WidgetFactory[T]:
        x = 0
        full_w = self.label_width + 2 * (self.spacing + self.widget_width)
        widget_lists: List[List[WidgetFactory[T]]] = [[]]
        assert isinstance(group.layout, Grid), "Can only do grid at the moment"
        for c in group.children:
            if isinstance(c, Group):
                # TODO: make a new screen
                raise NotImplementedError(c)
            else:

                def make(y):
                    return self.component(
                        c,
                        bounds=Bounds(x, y, full_w, self.widget_height),
                        add_label=group.layout.labelled,
                    )

                widgets = list(make(y=max_y(widget_lists[-1], self.spacing)))
                max_h = max(w.bounds.y + w.bounds.h for w in widgets)
                if bounds.h > 0 and max_h > bounds.h:
                    # Retry in the next row
                    x = max_x(widget_lists[-1], self.spacing)
                    widget_lists.append(list(make(y=0)))
                else:
                    # Add in this row
                    for w in widgets:
                        widget_lists[-1].append(w)

        widgets = concat(widget_lists)
        bounds.h = max_y(widgets)
        bounds.w = max_x(widgets)
        return self.group_cls(bounds, group.label, widgets)


def concat(items: List[List[T]]) -> List[T]:
    return [x for seq in items for x in seq]


def split_with_sep(text: str, sep: str, maxsplit: int = -1) -> List[str]:
    return [t + sep for t in text.split(sep, maxsplit=maxsplit)]


@dataclass
class EdlWidget:
    text: str

    def __setitem__(self, item: str, value):
        multiline = re.compile(r"^%s {[^}]*}$" % item, re.MULTILINE | re.DOTALL)
        if multiline.search(self.text):
            pattern = multiline
            lines = str(value).splitlines()
            value = "\n".join(["{"] + [f'  "{x}"' for x in lines] + ["}"])
        else:
            # Single line
            pattern = re.compile(r"^%s .*$" % item, re.MULTILINE)
            if isinstance(value, str):
                value = f'"{value}"'
        self.text, n = pattern.subn(f"{item} {value}", self.text)
        assert n == 1, f"No replacements made for {item}"

    @classmethod
    def bounded(cls, text: str, bounds: Bounds) -> "EdlWidget":
        w = cls(text)
        for prop in "xywh":
            w[prop] = getattr(bounds, prop)
        return w


ExtraText = Callable[[str, Bounds], Tuple[List[str], int]]


class EdlFile:
    def __init__(self, text: str):
        assert "endGroup" not in text, "Can't do groups"
        self.screen, text = split_with_sep(text, "\nendScreenProperties\n", 1)
        self.widgets = split_with_sep(text, "\nendObjectProperties\n")

    def widget_factory(
        self,
        cls: Type[T],
        search: str,
        make_widget: Callable[[str, Bounds], EdlWidget] = EdlWidget.bounded,
        **properties: str,
    ) -> Type[T]:
        matches = [t for t in self.widgets if re.search(search, t)]
        assert len(matches) == 1, f"Got {len(matches)} matches for {search!r}"

        class EdlWidgetFactory(cls):  # type: ignore
            def format(self) -> List[str]:
                widget = make_widget(matches[0], self.bounds)
                for prop, attr in properties.items():
                    widget[prop] = getattr(self, attr)
                return [widget.text]

        return EdlWidgetFactory

    def group_factory(
        self,
        padding: Bounds,
        make_widgets: Callable[[Bounds, str], List[WidgetFactory[str]]],
        is_screen: bool = False,
    ) -> Type[GroupFactory[str]]:
        @dataclass
        class EdlGroupFactory(GroupFactory[str]):
            def format(self, screen=self.screen, padding=padding) -> List[str]:
                texts: List[str] = []
                if is_screen:
                    texts.append(EdlWidget.bounded(screen, self.bounds).text)
                else:
                    padding = replace(
                        padding,
                        x=padding.x + self.bounds.x,
                        y=padding.y + self.bounds.y,
                    )
                for widget in make_widgets(self.bounds, self.title):
                    texts += widget.format()
                for c in self.children:
                    c.bounds.x += padding.x
                    c.bounds.y += padding.y
                    texts += c.format()
                return texts

            def __post_init__(self):
                self.bounds.h += padding.h
                self.bounds.w += padding.w

        return EdlGroupFactory
