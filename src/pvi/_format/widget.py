from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, List, Type, TypeVar, Union

from pvi._format.utils import Bounds, GroupType
from pvi.device import Generic, Group, ReadWidget, WriteWidget

T = TypeVar("T")


class WidgetTemplate(Generic[T]):
    screen: T

    def search(self, search) -> T:
        """Search for a widget"""
        raise NotImplementedError(self)

    def set(self, t: T, bounds: Bounds = None, **properties) -> T:
        """Return a copy of the internal representation with the bounds and
        properties set"""
        raise NotImplementedError(self)

    def create_group(
        self,
        group_object: List[T],
        children: List[WidgetFactory[T]],
        padding: Bounds = Bounds(),
    ) -> List[T]:
        """Return a group widget with its children attached and appropritately padded"""
        raise NotImplementedError(self)


WF = TypeVar("WF", bound="WidgetFactory")


@dataclass
class WidgetFactory(Generic[T]):
    bounds: Bounds

    def format(self) -> List[T]:
        """Will be filled in by from_template"""
        raise NotImplementedError(self)

    @classmethod
    def from_template(
        cls: Type[WF],
        template: WidgetTemplate[T],
        search,
        sized: Callable[[Bounds], Bounds] = Bounds.copy,
        **attrs,
    ) -> Type[WF]:
        t = template.search(search)

        class FormattableWidgetFactory(cls):  # type: ignore
            def format(self) -> List[T]:
                properties = {k: getattr(self, v) for k, v in attrs.items()}
                return [template.set(t, sized(self.bounds), **properties)]

        # Make debugging the sorcery a bit easier
        FormattableWidgetFactory.__name__ = (
            f"{FormattableWidgetFactory.__name__}<{cls.__name__}<{search}>>"
        )
        FormattableWidgetFactory.__qualname__ = FormattableWidgetFactory.__name__

        return FormattableWidgetFactory


@dataclass
class LabelFactory(WidgetFactory[T]):
    text: str


@dataclass
class PVWidgetFactory(WidgetFactory[T]):
    pv: str
    widget_spec: Union[ReadWidget, WriteWidget]


@dataclass
class ActionFactory(WidgetFactory[T]):
    label: str
    pv: str
    value: str


@dataclass
class SubScreenFactory(WidgetFactory[T]):
    file_name: str
    components: Group


@dataclass
class GroupFactory(WidgetFactory[T]):
    title: str
    children: List[WidgetFactory[T]]

    @classmethod
    def from_template(
        cls,
        template: WidgetTemplate[T],
        search: GroupType,
        sized: Callable[[Bounds], Bounds] = Bounds.copy,
        make_widgets: Callable[[Bounds, str], List[WidgetFactory[T]]] = None,
        **attrs,
    ) -> Type[GroupFactory[T]]:
        @dataclass
        class FormattableGroupFactory(GroupFactory[T]):
            def format(self) -> List[T]:
                padding = sized(self.bounds)
                texts: List[T] = []
                made_widgets: List[T] = []

                if search == GroupType.SCREEN:
                    properties = {k: getattr(self, v) for k, v in attrs.items()}
                    texts.append(
                        template.set(template.screen, self.bounds, **properties)
                    )
                    # Make screen title
                    if make_widgets:
                        for widget in make_widgets(self.bounds, self.title):
                            texts += widget.format()
                    for c in self.children:
                        c.bounds.x += padding.x
                        c.bounds.y += padding.y
                        texts += c.format()

                if search == GroupType.GROUP:
                    # Make group object
                    if make_widgets:
                        for widget in make_widgets(self.bounds, self.title):
                            made_widgets += widget.format()
                    texts += template.create_group(made_widgets, self.children, padding)
                return texts

            def __post_init__(self):
                padding = sized(self.bounds)
                self.bounds = replace(self.bounds, w=padding.w, h=padding.h)

        return FormattableGroupFactory


def max_x(widgets: List[WidgetFactory[T]]) -> int:
    """Given multiple widgets, calulate the maximum x position that they occupy"""
    if widgets:
        return max(w.bounds.x + w.bounds.w for w in widgets)
    else:
        return 0


def max_y(widgets: List[WidgetFactory[T]]) -> int:
    """Given multiple widgets, calulate the maximum y position that they occupy"""
    if widgets:
        return max(w.bounds.y + w.bounds.h for w in widgets)
    else:
        return 0


def next_x(widgets: List[WidgetFactory[T]], spacing: int = 0) -> int:
    """Given multiple widgets, calulate the next feasible location for an
    additional widget in the x axis"""
    if widgets:
        return max_x(widgets) + spacing
    else:
        return 0


def next_y(widgets: List[WidgetFactory[T]], spacing: int = 0) -> int:
    """Given multiple widgets, calulate the next feasible location for an
    additional widget in the y axis"""
    if widgets:
        return max_y(widgets) + spacing
    else:
        return 0
