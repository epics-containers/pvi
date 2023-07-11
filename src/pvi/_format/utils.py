from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Tuple, TypeVar, Union


@dataclass
class Bounds:
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0

    def copy(self) -> Bounds:
        return Bounds(self.x, self.y, self.w, self.h)

    def split_left(self, width: int, spacing: int) -> Tuple[Bounds, Bounds]:
        """Split horizontally by width of first element"""
        to_split = width + spacing
        assert to_split < self.w, f"Can't split off {to_split} from {self.w}"
        left = Bounds(self.x, self.y, width, self.h)
        right = Bounds(self.x + to_split, self.y, self.w - to_split, self.h)
        return left, right

    def split_by_ratio(
        self, ratio: Tuple[float, ...], spacing: int
    ) -> Tuple[Bounds, ...]:
        """Split horizontally by ratio of widths for each element"""
        splits = len(ratio) - 1
        widget_space = self.w - splits * spacing
        widget_widths = tuple(int(widget_space * r) for r in ratio)
        widget_xs = tuple(
            self.x + sum(widget_widths[:i]) + spacing * i for i in range(splits + 1)
        )

        return tuple(
            Bounds(x, self.y, w, self.h) for x, w in zip(widget_xs, widget_widths)
        )

    def split_into(self, count: int, spacing: int) -> Tuple[Bounds, ...]:
        """Split horizontally by into count equal widths"""
        return self.split_by_ratio((1 / count,) * count, spacing)

    def square(self) -> Bounds:
        """Return the largest square that will fit in self"""
        size = min(self.w, self.h)
        return Bounds(
            x=self.x + int((self.w - size) / 2),
            y=self.y + int((self.h - size) / 2),
            w=size,
            h=size,
        )

    def added_to(self, bounds: Bounds) -> Bounds:
        return Bounds(
            x=self.x + bounds.x,
            y=self.y + bounds.y,
            w=self.w + bounds.w,
            h=self.h + bounds.h,
        )

    def tile(
        self, *, horizontal: int = 1, vertical: int = 1, spacing: int = 0
    ) -> Bounds:
        """Tile bounds for one element to N elements with spacing"""
        return Bounds(
            x=self.x,
            y=self.y,
            w=self.w * horizontal + spacing * (horizontal - 1),
            h=self.h * vertical + spacing * (vertical - 1),
        )


class GroupType(Enum):
    GROUP = "GROUP"
    SCREEN = "SCREEN"


T = TypeVar("T")


def concat(items: List[List[T]]) -> List[T]:
    return [x for seq in items for x in seq]


def split_with_sep(text: str, sep: str, maxsplit: int = -1) -> List[str]:
    return [t + sep for t in text.split(sep, maxsplit=maxsplit)]


def with_title(spacing, title_height: int) -> Callable[[Bounds], Bounds]:
    return Bounds(
        spacing, spacing + title_height, 2 * spacing, 2 * spacing + title_height
    ).added_to


def indent_widget(bounds: Bounds, indentation: int) -> Bounds:
    """Shifts the x position of a widget. Used on top level widgets to align
    them with group indentation"""
    return Bounds(bounds.x + indentation, bounds.y, bounds.w, bounds.h)
