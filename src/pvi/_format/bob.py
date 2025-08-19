from collections.abc import Sequence
from copy import deepcopy
from typing import Any

from lxml.etree import (
    SubElement,
    XMLParser,
    _Element,  # pyright: ignore [reportPrivateUsage]
    parse,
)

from pvi._format.utils import Bounds
from pvi._format.widget import UITemplate, WidgetFormatter
from pvi.device import (
    LED,
    BitField,
    CheckBox,
    ComboBox,
    ImageRead,
    TableRead,
    TableWrite,
    TextFormat,
    TextRead,
    TextWrite,
    WidgetUnion,
    WriteWidget,
)

BOB_TEXT_FORMATS = {
    TextFormat.decimal: "1",
    TextFormat.hexadecimal: "4",
    TextFormat.engineer: "3",
    TextFormat.exponential: "2",
    TextFormat.string: "6",
}


class BobTemplate(UITemplate[_Element]):
    """Extract and modify elements from a template .bob file."""

    def __init__(self, text: str):
        """Parse an XML string to an element tree object."""

        # Passing `remove_blank_text` means we can pretty print our additions
        self.tree = parse(text, parser=XMLParser(remove_blank_text=True))
        self.screen = self.search("Display")

    def set(
        self,
        template: _Element,
        bounds: Bounds | None = None,
        widget: WidgetUnion | None = None,
        properties: dict[str, Any] | None = None,
    ) -> _Element:
        properties = properties or {}

        if bounds:
            properties["x"] = bounds.x
            properties["y"] = bounds.y
            properties["width"] = bounds.w
            properties["height"] = bounds.h

            if isinstance(widget, BitField):
                properties["width"] = widget.number_of_bits * 20
                properties.pop("height")

        widget_type = template.attrib.get("type", "")

        t_copy = deepcopy(template)
        for item, value in properties.items():
            new_text = ""

            match widget_type, item, value:
                case "table", "pv_name", pv:
                    pva_prefix = "pva://"
                    if not pv.startswith(pva_prefix):
                        new_text = f"{pva_prefix}{pv}"  # Must include pva prefix
                    else:
                        new_text = str(pv)
                case "action_button", "file", file_name:
                    new_text = file_name
                    if not new_text.endswith(".bob"):
                        new_text += ".bob"  # Must include file extension
                case "action_button", "macros", dict():
                    macros: dict[str, str] = value  # type: ignore
                    if macros:
                        add_button_macros(t_copy, macros)
                case _:
                    new_text = str(value)

            if new_text:
                find_element(t_copy, item).text = new_text  # type: ignore

        # Add additional properties from widget
        match widget_type, widget:
            case ("combo", ComboBox() as combo_box):
                add_combo_box_items(t_copy, combo_box)
            case ("table", TableRead() | TableWrite() as table):
                add_table_columns(t_copy, table)
            case ("textentry", TextWrite(format=format)) | (
                "textupdate",
                TextRead(format=format),
            ) if format is not None:
                add_format(t_copy, BOB_TEXT_FORMATS[TextFormat(format)])
            case ("byte_monitor", BitField() as bit_field):
                add_byte_number_of_bits(t_copy, bit_field.number_of_bits)
            case ("image", ImageRead(grayscale=grayscale)):
                if grayscale:
                    set_color_map(t_copy, "GRAY")
            case _:
                pass

        return t_copy

    def search(self, search: str) -> _Element:
        """Locate and extract elements from the Element tree.

        Args:
            search: The unique name of the element to extract.
                Can be found in its name subelement.

        Returns:
            The extracted element.
        """

        tree_copy = deepcopy(self.tree)
        # 'name' is the unique ID for each element
        matches = [
            e
            for e in [
                element.getparent()
                for element in tree_copy.iter("name")
                if element.text == search
            ]
            if isinstance(e, _Element)
        ]
        assert len(matches) == 1, f"Got {len(matches)} matches for {search!r}"

        # Isolate the screen properties
        if matches[0].tag == "display":
            for child in matches[0]:
                if child.tag == "widget":
                    matches[0].remove(child)

        return matches[0]

    def create_group(
        self,
        group_object: list[_Element],
        children: list[WidgetFormatter[_Element]],
        padding: Bounds | None = None,
    ) -> list[_Element]:
        """Create an xml group object from a list of child widgets

        Args:
            group_object: Templated group xml element
            children: List of child widgets within the group
            padding: Additional placement data to fit the children to the group object.
                Defaults to Bounds().

        Returns:
            An xml group with children attached as subelements
        """
        padding = padding or Bounds()

        assert len(group_object) == 1, (
            f"Size of group_object is {len(group_object)}, should be 1"
        )
        for c in children:
            group_object[0].append(c.format()[0])
        return group_object


def add_table_columns(widget_element: _Element, table: TableRead | TableWrite):
    if not table.widgets:
        # Default empty -> get options from pv
        return

    columns_element = SubElement(widget_element, "columns")
    for column, widget in enumerate(table.widgets):
        add_table_column(columns_element, f"Column {column + 1}", widget)

    add_editable(widget_element, editable=table.access_mode == "w")


def add_table_column(
    columns_element: _Element,
    name: str,
    widget: WidgetUnion,
):
    options: Sequence[str] = []
    if isinstance(widget, LED | CheckBox):
        options = ["false", "true"]
    elif isinstance(widget, ComboBox):
        options = widget.get_choices()

    column_element = SubElement(columns_element, "column")
    SubElement(column_element, "name").text = name
    add_editable(column_element, editable=isinstance(widget, WriteWidget))

    if options:
        options_element = SubElement(column_element, "options")
        for option in options:
            SubElement(options_element, "option").text = option


def add_button_macros(widget_element: _Element, macros: dict[str, str]):
    """Add action macros to the given element.

    Args:
        widget_element: Element to add action macros to
        macros: Macros to add to element

    """
    action_element = find_element(widget_element, "action")
    macros_element = SubElement(action_element, "macros")
    for macro, value in macros.items():
        SubElement(macros_element, macro).text = value


def add_combo_box_items(widget_element: _Element, combo_box: ComboBox):
    if not combo_box.get_choices():
        # Default empty -> get items from pv
        return

    items_element = SubElement(widget_element, "items")
    for item in combo_box.get_choices():
        SubElement(items_element, "item").text = item

    SubElement(widget_element, "items_from_pv").text = "false"


def add_editable(element: _Element, editable: bool):
    SubElement(element, "editable").text = "true" if editable else "false"


def add_format(element: _Element, format: str):
    if format:
        SubElement(element, "format").text = format

def set_color_map(element: _Element, color_map: str):
    color_map_element = SubElement(element, "color_map")
    SubElement(color_map_element, "name").text = color_map

def add_byte_number_of_bits(element: _Element, number_of_bits: int):
    SubElement(element, "numBits").text = str(number_of_bits)


def find_element(root_element: _Element, tag: str, index: int = 0) -> _Element:
    """Iterate tree to find tag and replace text.

    Args:
        root_element: Root of tree to search
        tag: Tag to search for in tree
        index: Match to return if multiple matches are found
    """
    match list(root_element.iter(tag=tag)):
        case []:
            raise ValueError(f"No matches for '{tag}' in {root_element}")
        case matches:
            return matches[index]
