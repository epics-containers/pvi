from copy import deepcopy
from typing import Dict, List, Optional, Sequence

from lxml.etree import ElementBase, SubElement, XMLParser, parse

from pvi._format.utils import Bounds
from pvi._format.widget import UITemplate, WidgetFormatter
from pvi.device import (
    LED,
    ComboBox,
    TableRead,
    TableWidgetType,
    TableWrite,
    TextFormat,
    TextRead,
    TextWrite,
    WidgetType,
    WriteWidget,
)

BOB_TEXT_FORMATS = {
    TextFormat.decimal: "1",
    TextFormat.hexadecimal: "4",
    TextFormat.engineer: "3",
    TextFormat.exponential: "2",
    TextFormat.string: "6",
}


class BobTemplate(UITemplate[ElementBase]):
    """Extract and modify elements from a template .bob file."""

    def __init__(self, text: str):
        """Parse an XML string to an element tree object."""

        # Passing `remove_blank_text` means we can pretty print our additions
        self.tree = parse(text, parser=XMLParser(remove_blank_text=True))
        self.screen = self.search("Display")

    def set(
        self,
        template: ElementBase,
        bounds: Optional[Bounds] = None,
        widget: Optional[WidgetType] = None,
        **properties,
    ) -> ElementBase:
        if bounds:
            properties["x"] = bounds.x
            properties["y"] = bounds.y
            properties["width"] = bounds.w
            properties["height"] = bounds.h

        widget_type = template.attrib.get("type", "")

        t_copy = deepcopy(template)
        for item, value in properties.items():
            new_text = ""

            match widget_type, item, value:
                case "table", "pv_name", pv:
                    new_text = f"pva://{pv}"  # Must include pva prefix
                case "action_button", "file", file_name:
                    new_text = file_name
                    if not new_text.endswith(".bob"):
                        new_text += ".bob"  # Must include file extension
                case "action_button", "macros", dict() as macros:
                    if macros:
                        add_button_macros(t_copy, value)
                case _:
                    new_text = str(value)

            if new_text:
                find_element(t_copy, item).text = new_text

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
                add_format(t_copy, BOB_TEXT_FORMATS[format])

        return t_copy

    def search(self, search: str) -> ElementBase:
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
            element.getparent()
            for element in tree_copy.iter("name")
            if element.text == search
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
        group_object: List[ElementBase],
        children: List[WidgetFormatter[ElementBase]],
        padding: Bounds = Bounds(),
    ) -> List[ElementBase]:
        """Create an xml group object from a list of child widgets

        Args:
            group_object: Templated group xml element
            children: List of child widgets within the group
            padding: Additional placement data to fit the children to the group object.
                Defaults to Bounds().

        Returns:
            An xml group with children attached as subelements
        """
        assert (
            len(group_object) == 1
        ), f"Size of group_object is {len(group_object)}, should be 1"
        for c in children:
            group_object[0].append(c.format()[0])
        return group_object


def add_table_columns(widget_element: ElementBase, table: TableWidgetType):
    if not table.widgets:
        # Default empty -> get options from pv
        return

    columns_element = SubElement(widget_element, "columns")
    for column, widget in enumerate(table.widgets):
        add_table_column(columns_element, f"Column {column + 1}", widget)

    add_editable(widget_element, editable=isinstance(table, TableWrite))


def add_table_column(
    columns_element: ElementBase,
    name: str,
    widget: WidgetType,
):
    options: Sequence[str] = []
    if isinstance(widget, LED):
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


def add_button_macros(widget_element: ElementBase, macros: Dict[str, str]):
    """Add action macros to the given element.

    Args:
        widget_element: Element to add action macros to
        macros: Macros to add to element

    """
    action_element = find_element(widget_element, "action")
    macros_element = SubElement(action_element, "macros")
    for macro, value in macros.items():
        SubElement(macros_element, macro).text = value


def add_combo_box_items(widget_element: ElementBase, combo_box: ComboBox):
    if not combo_box.get_choices():
        # Default empty -> get items from pv
        return

    items_element = SubElement(widget_element, "items")
    for item in combo_box.get_choices():
        SubElement(items_element, "item").text = item

    SubElement(widget_element, "items_from_pv").text = "false"


def add_editable(element: ElementBase, editable: bool):
    SubElement(element, "editable").text = "true" if editable else "false"


def add_format(element: ElementBase, format: str):
    if format:
        SubElement(element, "format").text = format


def find_element(root_element: ElementBase, tag: str, index: int = 0) -> ElementBase:
    """Iterate tree to find tag and replace text.

    Args:
        root_element: Root of tree to search
        tag: Tag to search for in tree
        index: Match to return if multiple matches are found

    """
    match list(root_element.iter(tag=tag)):
        case []:
            raise ValueError(
                f"No matches for '{tag}' in {root_element.find('name').text}"
            )
        case matches:
            return matches[index]
