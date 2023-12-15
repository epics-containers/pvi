from __future__ import annotations

from enum import Enum
from typing import Callable, List, Tuple, TypeVar

from pydantic import BaseModel


class Bounds(BaseModel):
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0

    def clone(self) -> Bounds:
        return Bounds(x=self.x, y=self.y, w=self.w, h=self.h)

    def split_left(self, width: int, spacing: int) -> Tuple[Bounds, Bounds]:
        """Split horizontally by width of first element"""
        to_split = width + spacing
        assert to_split < self.w, f"Can't split off {to_split} from {self.w}"
        left = Bounds(x=self.x, y=self.y, w=width, h=self.h)
        right = Bounds(x=self.x + to_split, y=self.y, w=self.w - to_split, h=self.h)
        return left, right

    def split_by_ratio(
        self, ratio: Tuple[float, ...], spacing: int
    ) -> Tuple[Bounds, ...]:
        """Split horizontally by ratio of widths, separated by spacing"""
        splits = len(ratio) - 1
        widget_space = self.w - splits * spacing
        widget_widths = tuple(int(widget_space * r) for r in ratio)
        widget_xs = tuple(
            self.x + sum(widget_widths[:i]) + spacing * i for i in range(splits + 1)
        )

        return tuple(
            Bounds(x=x, y=self.y, w=w, h=self.h)
            for x, w in zip(widget_xs, widget_widths)
        )

    def split_into(self, count: int, spacing: int) -> Tuple[Bounds, ...]:
        """Split horizontally into count equal widths, separated by spacing"""
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
        """Expand by tiling self `horizontal`/`vertical` times, plus spacing"""
        return Bounds(
            x=self.x,
            y=self.y,
            w=self.w * horizontal + spacing * (horizontal - 1),
            h=self.h * vertical + spacing * (vertical - 1),
        )

    def indent(self, indentation: int) -> None:
        self.x += indentation


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
        x=spacing, y=spacing + title_height, w=2 * spacing, h=2 * spacing + title_height
    ).added_to
