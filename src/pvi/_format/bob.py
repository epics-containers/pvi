from __future__ import annotations

from copy import deepcopy
from typing import List, Optional, Sequence

from lxml.etree import ElementBase, SubElement, XMLParser, parse

from pvi._format.utils import Bounds
from pvi._format.widget import UITemplate, WidgetFormatter
from pvi.device import (
    LED,
    ComboBox,
    Group,
    Row,
    TableWidgetType,
    TableWidgetTypes,
    TableWrite,
    WidgetType,
    WriteWidget,
)


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
            if widget_type == "table" and item == "pv_name":
                new_text = f"pva://{value}"  # Must include pva prefix
            elif item == "file":
                new_text = f"{value}.bob"  # Must include file extension
            else:
                new_text = str(value)

            if new_text:
                replace_text(t_copy, item, new_text)

        if widget_type == "table" and isinstance(widget, TableWidgetTypes):
            add_table_columns(t_copy, widget)
        elif widget_type == "combo" and isinstance(widget, ComboBox):
            add_combo_box_items(t_copy, widget)

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


def is_table(component: Group) -> bool:
    return all(
        isinstance(sub_component, Group) and isinstance(sub_component.layout, Row)
        for sub_component in component.children
    )


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
        options = widget.choices

    column_element = SubElement(columns_element, "column")
    SubElement(column_element, "name").text = name
    add_editable(column_element, editable=isinstance(widget, WriteWidget))

    if options:
        options_element = SubElement(column_element, "options")
        for option in options:
            SubElement(options_element, "option").text = option


def add_combo_box_items(widget_element: ElementBase, combo_box: ComboBox):
    if not combo_box.choices:
        # Default empty -> get items from pv
        return

    items_element = SubElement(widget_element, "items")
    for item in combo_box.choices:
        SubElement(items_element, "item").text = item

    SubElement(widget_element, "items_from_pv").text = "false"


def add_editable(element: ElementBase, editable: bool):
    SubElement(element, "editable").text = "true" if editable else "false"


def replace_text(element: ElementBase, tag: str, text: str):
    try:
        # Iterate tree to find tag and replace text
        list(element.iter(tag=tag))[0].text = text
    except IndexError as idx:
        name = element.find("name").text
        raise ValueError(f"Failed to locate '{tag}' in {name}") from idx
