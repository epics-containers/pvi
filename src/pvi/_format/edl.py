from __future__ import annotations

import re
from typing import List

from pvi._format.utils import Bounds, split_with_sep
from pvi._format.widget import WidgetFactory, WidgetTemplate


class EdlTemplate(WidgetTemplate[str]):
    def __init__(self, text: str):
        assert "endGroup" not in text, "Can't do groups"
        self.screen, text = split_with_sep(text, "\nendScreenProperties\n", 1)
        self.widgets = split_with_sep(text, "\nendObjectProperties\n")

    def set(self, t: str, bounds: Bounds = None, **properties) -> str:
        if bounds:
            for k in "xywh":
                properties[k] = getattr(bounds, k)
        for item, value in properties.items():
            if item == "displayFileName":
                value = f"0 {value}"  # These are items in an array but we only use one
            multiline = re.compile(r"^%s {[^}]*}$" % item, re.MULTILINE | re.DOTALL)
            if multiline.search(t):
                pattern = multiline
                lines = str(value).splitlines()
                value = "\n".join(["{"] + [f'  "{x}"' for x in lines] + ["}"])
            else:
                # Single line
                pattern = re.compile(r"^%s .*$" % item, re.MULTILINE)
                if isinstance(value, str):
                    value = f'"{value}"'
            t, n = pattern.subn(f"{item} {value}", t)
            assert n == 1, f"No replacements made for {item}"
        return t

    def search(self, search: str) -> str:
        matches = [t for t in self.widgets if re.search(search, t)]
        assert len(matches) == 1, f"Got {len(matches)} matches for {search!r}"
        return matches[0]

    def create_group(
        self,
        group_object: List[str],
        children: List[WidgetFactory[str]],
        padding: Bounds = Bounds(),
    ) -> List[str]:

        texts: List[str] = []

        for c in children:
            c.bounds.x += padding.x
            c.bounds.y += padding.y
            texts += c.format()

        return group_object + texts
