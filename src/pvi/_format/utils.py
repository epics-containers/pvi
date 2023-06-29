from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Tuple, TypeVar


@dataclass
class Bounds:
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0

    def copy(self) -> Bounds:
        return Bounds(self.x, self.y, self.w, self.h)

    def split(self, width: int, spacing: int) -> Tuple[Bounds, Bounds]:
        """Split horizontally"""
        to_split = width + spacing
        assert to_split < self.w, f"Can't split off {to_split} from {self.w}"
        left = Bounds(self.x, self.y, width, self.h)
        right = Bounds(self.x + to_split, self.y, self.w - to_split, self.h)
        return left, right

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
