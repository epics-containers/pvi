from __future__ import annotations

import re
from typing import List, Optional

from pvi._format.utils import Bounds, split_with_sep
from pvi._format.widget import UITemplate, WidgetFormatter
from pvi.device import TextFormat, TextRead, TextWrite, WidgetType

EDL_TEXT_FORMATS = {
    TextFormat.decimal: "decimal",
    TextFormat.hexadecimal: "hex",
    TextFormat.engineer: "engineer",
    TextFormat.exponential: "exp",
    TextFormat.string: "default",
}


class EdlTemplate(UITemplate[str]):
    def __init__(self, text: str):
        assert "endGroup" not in text, "Can't do groups"
        self.screen, text = split_with_sep(text, "\nendScreenProperties\n", 1)
        self.widgets = split_with_sep(text, "\nendObjectProperties\n")

    def set(
        self,
        template: str,
        bounds: Optional[Bounds] = None,
        widget: Optional[WidgetType] = None,
        **properties,
    ) -> str:
        if bounds:
            for k in "xywh":
                properties[k] = getattr(bounds, k)
        for item, value in properties.items():
            if item == "displayFileName":
                value = f"0 {value}"  # These are items in an array but we only use one

            multiline = re.compile(r"^%s {[^}]*}$" % item, re.MULTILINE | re.DOTALL)
            if multiline.search(template):
                pattern = multiline
                lines = str(value).splitlines()
                value = "\n".join(["{"] + [f'  "{x}"' for x in lines] + ["}"])
            else:
                # Single line
                pattern = re.compile(r"^%s .*$" % item, re.MULTILINE)
                if isinstance(value, str):
                    value = f'"{value}"'

            template, n = pattern.subn(f"{item} {value}", template)
            assert n == 1, f"No replacements made for {item}"

        # Add additional properties from widget
        match widget:
            case TextWrite(format=format) | TextRead(format=format) if (
                is_text_widget(template) and format is not None
            ):
                template = add_property(
                    template, "displayMode", EDL_TEXT_FORMATS[format]
                )

        return template

    def search(self, search: str) -> str:
        matches = [t for t in self.widgets if re.search(search, t)]
        assert len(matches) == 1, f"Got {len(matches)} matches for {search!r}"
        return matches[0]

    def create_group(
        self,
        group_object: List[str],
        children: List[WidgetFormatter[str]],
        padding: Bounds = Bounds(),
    ) -> List[str]:
        texts: List[str] = []

        for c in children:
            c.bounds.x += padding.x
            c.bounds.y += padding.y
            texts += c.format()

        return group_object + texts


def is_text_widget(text: str):
    return text.startswith("\n# (Text")


def add_property(text: str, property: str, value: str) -> str:
    end = "endObjectProperties\n"
    return text.replace(end, f'{property} "{value}"\n{end}')
