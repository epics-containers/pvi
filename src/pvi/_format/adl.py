from __future__ import annotations

import re
from typing import List, Optional

from pvi._format.utils import Bounds, split_with_sep
from pvi._format.widget import UITemplate, WidgetFormatter
from pvi.device import TextFormat, TextRead, TextWrite, WidgetType

ADL_TEXT_FORMATS = {
    TextFormat.decimal: "decimal",
    TextFormat.hexadecimal: "hexadecimal",
    TextFormat.engineer: "engr. notation",
    TextFormat.exponential: "exponential",
    TextFormat.string: "string",
}


class AdlTemplate(UITemplate[str]):
    def __init__(self, text: str):
        assert "children {" not in text, "Can't do groups"
        widgets = split_with_sep(text, "\n}\n")
        self.screen = "".join(widgets[:3])
        self.widgets = widgets[3:]

    def set(
        self,
        template: str,
        bounds: Optional[Bounds] = None,
        widget: Optional[WidgetType] = None,
        **properties,
    ) -> str:
        if bounds:
            properties["x"] = bounds.x
            properties["y"] = bounds.y
            properties["width"] = bounds.w
            properties["height"] = bounds.h

        for item, value in properties.items():
            if template.startswith('"related display"') and item == "name":
                if not value.endswith(".adl"):
                    value = f"{value}.adl"  # Must include file extension

            # Only need single line
            pattern = re.compile(r"^(\s*%s)=.*$" % item, re.MULTILINE)
            if isinstance(value, str):
                value = f'"{value}"'

            template, n = pattern.subn(r"\g<1>=" + str(value), template)
            assert n == 1, f"No replacements made for {item}"

        # Add additional properties from widget
        match widget:
            case TextWrite(format=format) | TextRead(format=format) if (
                is_text_widget(template) and format is not None
            ):
                template = add_property(template, "format", ADL_TEXT_FORMATS[format])

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
    return text.startswith('"text ')


def add_property(text: str, property: str, value: str) -> str:
    end = "\n}"
    return text.replace(end, f'\n\t{property}="{value}"{end}')
