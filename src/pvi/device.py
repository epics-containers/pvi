from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, fields
from enum import Enum
from pathlib import Path
from typing import (
    Annotated,
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from apischema import deserialize, serialize
from ruamel.yaml import YAML

from pvi._schema_utils import add_type_field, as_discriminated_union, desc
from pvi.utils import find_pvi_yaml

PASCAL_CASE_REGEX = re.compile(r"(?<![A-Z])[A-Z]|[A-Z][a-z/d]|(?<=[a-z])\d")


def to_title_case(pascal_s: str) -> str:
    """Takes a PascalCaseFieldName and returns an Title Case Field Name

    Args:
        pascal_s: E.g. PascalCaseFieldName
    Returns:
        Title Case converted name. E.g. Pascal Case Field Name
    """
    return PASCAL_CASE_REGEX.sub(lambda m: " " + m.group(), pascal_s)[1:]


def to_snake_case(pascal_s: str) -> str:
    """Takes a PascalCaseFieldName and returns a snake_case_field_name
    Args:
        pascal_s: E.g. PascalCaseFieldName
    Returns:
        snake_case converted name. E.g. pascal_case_field_name
    """
    return PASCAL_CASE_REGEX.sub(lambda m: "_" + m.group().lower(), pascal_s)[1:]


class TextFormat(Enum):
    """Format to use for display of Text{Read,Write} widgets on a UI"""

    decimal = 0
    hexadecimal = 1
    engineer = 2
    exponential = 3
    string = 4


@as_discriminated_union
@dataclass
class ReadWidget:
    """Widget that displays a scalar PV"""


class LED(ReadWidget):
    """LED display of a boolean PV"""


@dataclass
class BitField(ReadWidget):
    """LED and label for each bit of an int PV"""

    labels: Annotated[Sequence[str], desc("Label for each bit")]


class ProgressBar(ReadWidget):
    """Progress bar from lower to upper limit of a float PV"""


@dataclass
class TextRead(ReadWidget):
    """Text view of any PV"""

    lines: Annotated[int, desc("Number of lines to display")] = 1
    format: Annotated[Optional[TextFormat], desc("Display format")] = None


@dataclass
class ArrayTrace(ReadWidget):
    """Trace of the array in a plot view"""

    axis: Annotated[
        str,
        desc(
            "Traces with same axis name will appear on same axis, "
            "plotted against 'x' trace if it exists, or indexes if not. "
            "Only one traces with axis='x' allowed."
        ),
    ]


@dataclass
class TableRead(ReadWidget):
    """Tabular view of an NTTable"""

    widgets: Annotated[
        Sequence[ReadWidget],
        desc("For each column, what widget should be repeated for every row"),
    ] = field(default_factory=list)


class ImageRead(ReadWidget):
    """2D Image view of an NTNDArray"""


@as_discriminated_union
@dataclass
class WriteWidget:
    """Widget that controls a PV"""


class CheckBox(WriteWidget):
    """Checkable control of a boolean PV"""


@dataclass
class ComboBox(WriteWidget):
    """Selection of an enum PV"""

    choices: Annotated[Sequence[str], desc("Choices to select from")] = field(
        default_factory=list
    )


@dataclass
class ButtonPanel(WriteWidget):
    """One-or-more buttons that poke a PV with a value

    Args:
        actions: Dict of button label to value the button sends

    """

    actions: Dict[str, Any] = field(default_factory=lambda: dict(go=1))


@dataclass
class TextWrite(WriteWidget):
    """Text control of any PV"""

    lines: Annotated[int, desc("Number of lines to display")] = 1
    format: Annotated[Optional[TextFormat], desc("Display format")] = None


@dataclass
class ArrayWrite(WriteWidget):
    """Control of an array PV"""

    widget: Annotated[WriteWidget, desc("What widget should be used for each item")]


@dataclass
class TableWrite(WriteWidget):
    widgets: Annotated[
        Sequence[WidgetType],
        desc("For each column, what widget should be repeated for every row"),
    ] = field(default_factory=list)


WidgetType = Union[ReadWidget, WriteWidget]
TableWidgetType = Union[TableRead, TableWrite]
TableWidgetTypes = (TableRead, TableWrite)


@as_discriminated_union
@dataclass
class Layout:
    """Widget displaying child Components"""


class Plot(Layout):
    """Children are traces of the plot"""


@dataclass
class Row(Layout):
    """Children are columns in the row"""

    header: Annotated[
        Optional[Sequence[str]],
        desc("Labels for the items in the row, None means use previous row header"),
    ] = None


@dataclass
class Grid(Layout):
    """Children are rows in the grid"""

    labelled: Annotated[bool, desc("If True use names of children as labels")] = True


@dataclass
class SubScreen(Layout):
    """Children are displayed on another screen opened with a button."""

    labelled: Annotated[bool, desc("Display labels for components")] = True


@dataclass
class Named:
    name: Annotated[
        str, desc("PascalCase name to uniquely identify", pattern=r"([A-Z][a-z0-9]*)*$")
    ]


class Labelled(Named):
    label: str

    def __init_subclass__(cls, **kwargs):
        # Add an optional label to the end of the dataclass if not already there
        has_label_field = [f for f in fields(cls) if f.name == "label"]
        # Hack so this doesn't fire for the Component class below, or anything
        # else that doesn't add annotations. We really want this to be on terminal
        # classes, but no way of knowing this in __init_subclass__
        adds_annotations = bool(cls.__annotations__)
        if not has_label_field and adds_annotations:
            cls.__annotations__["label"] = Annotated[
                str, desc("Label for GUI. If empty, use name in Title Case")
            ]
            cls.label = ""
            dataclass(cls)

    def get_label(self):
        if getattr(self, "label", ""):
            return self.label
        else:
            return to_title_case(self.name)


@as_discriminated_union
class Component(Labelled):
    """These make up a Device"""


@dataclass
class SignalR(Component):
    """Scalar value backed by a single PV"""

    pv: Annotated[str, desc("PV to be used for get and monitor")]
    widget: Annotated[
        Optional[ReadWidget],
        desc("Widget to use for display, None means don't display"),
    ] = None


@dataclass
class SignalW(Component):
    """Write only value backed by a single PV"""

    pv: Annotated[str, desc("PV to be used for put")]
    widget: Annotated[
        Optional[WriteWidget],
        desc("Widget to use for control, None means don't display"),
    ] = None


@dataclass
class SignalRW(Component):
    """Read/write value backed by one or two PVs"""

    pv: Annotated[str, desc("PV to be used for put")]
    widget: Annotated[
        Optional[WriteWidget],
        desc("Widget to use for control, None means don't display"),
    ] = None
    # This was Optional[str] but produced JSON schema that YAML editor didn't understand
    read_pv: Annotated[str, desc("PV to be used for read, empty means use pv")] = ""
    read_widget: Annotated[
        Optional[ReadWidget], desc(
            "Widget to use for display, default TextRead"
        )
    ] = TextRead()

    def __post_init__(self):
        if self.read_pv == "":
            self.read_pv = f"{self.pv}.RBV"


SignalTypes = (SignalR, SignalW, SignalRW)
ReadSignalType = Union[SignalR, SignalRW]
WriteSignalType = Union[SignalW, SignalRW]


@dataclass
class SignalX(Component):
    """Executable that puts a fixed value to a PV."""

    pv: Annotated[str, desc("PV to be used for call")]
    value: Annotated[Any, desc("Value to write. None means zero")] = None


@dataclass
class DeviceRef(Component):
    """Reference to another Device."""

    pv: Annotated[str, desc("Child device PVI PV")]
    macros: Annotated[
        Dict[str, str],
        desc("Macro-value pairs"),
    ] = field(default_factory=dict)


class SignalRef(Component):
    """Reference to another Signal with the same name in this Device."""


T = TypeVar("T")
S = TypeVar("S")


@add_type_field
@dataclass
class Group(Generic[T], Labelled):
    """Group of child components in a Layout"""

    layout: Annotated[Layout, desc("How to layout children on screen")]
    children: Annotated[Tree[T], desc("Child Components")]


Tree = Sequence[Union[T, Group[T]]]


def on_each_node(tree: Tree[T], func: Callable[[T], Iterator[S]]) -> Tree[S]:
    """Visit each node of the tree of type typ, calling func on each leaf"""
    out: List[Union[S, Group[S]]] = []
    for t in tree:
        if isinstance(t, Group):
            group: Group[S] = Group(
                name=t.name, layout=t.layout, children=on_each_node(t.children, func)
            )
            out.append(group)
        else:
            out += list(func(t))
    return out


def walk(tree: Tree[T]) -> Iterator[Union[T, Group[T]]]:
    """Depth first traversal of tree"""
    for t in tree:
        yield t
        if isinstance(t, Group):
            yield from walk(t.children)


@dataclass
class Device:
    """Collection of Components"""

    label: Annotated[str, desc("Label for screen")]
    parent: Optional[
        Annotated[
            str,
            desc("The parent device (basename of yaml file)"),
        ]
    ] = None
    children: Annotated[Tree[Component], desc("Child Components")] = field(
        default_factory=list
    )

    def serialize(self) -> Mapping[str, Any]:
        """Serialize the Device to a dictionary."""
        return serialize(self, exclude_none=True, exclude_defaults=True)

    @classmethod
    def deserialize(cls, serialized: Path) -> Device:
        """Deserialize the Device from a YAML file"""
        return deserialize(cls, YAML(typ="safe").load(serialized))

    def deserialize_parents(self, yaml_paths: List[Path]):
        """Deserialize yaml of parents and extract parameters"""
        if self.parent is None or self.parent == "asynPortDriver":
            return

        parent_parameters = find_components(self.parent, yaml_paths)
        for node in parent_parameters:
            if isinstance(node, Group):
                for param_group in self.children:
                    if not isinstance(param_group, Group):
                        continue
                    elif param_group.name == node.name:
                        param_group.children = list(node.children) + list(
                            param_group.children
                        )
                        break  # Groups merged - skip to next parent group

                else:  # No break - Did not find the Group
                    # Inherit as a new Group
                    self.children = list(self.children) + [node]
                    continue  # Skip to next parent group

            else:
                # Node is an individual AsynParameter - just append it
                self.children = list(self.children) + [node]

    def generate_param_tree(self) -> str:
        param_tree = ", ".join(json.dumps(serialize(group)) for group in self.children)
        # Encode again to quote the string as a value and escape double quotes within
        return json.dumps('{"parameters":[' + param_tree + "]}")


def find_components(yaml_name: str, yaml_paths: List[Path]) -> Tree[Component]:
    if yaml_name == "asynPortDriver":
        return []  # asynPortDriver is the most base class and has no parameters

    # Look in this module first
    device_name = f"{yaml_name}.pvi.device.yaml"
    device_yaml = find_pvi_yaml(device_name, yaml_paths)

    if device_yaml is None:
        raise IOError(f"Cannot find {device_name} in {yaml_paths}")

    device = Device.deserialize(device_yaml)

    parent_components = (
        list(find_components(device.parent, yaml_paths))
        if device.parent is not None
        else []
    )

    return list(device.children) + parent_components
