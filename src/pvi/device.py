from __future__ import annotations

import json
import re
from dataclasses import dataclass, fields
from typing import (
    Any,
    Callable,
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
from typing_extensions import Annotated

from ._schema_utils import add_type_field, as_discriminated_union, desc

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
    ]


class ImageRead(ReadWidget):
    """2D Image view of an NTNDArray"""


@as_discriminated_union
@dataclass
class WriteWidget:
    """Widget that controls a PV"""


class CheckBox(WriteWidget):
    """Checkable control of a boolean PV"""


class ComboBox(WriteWidget):
    """Selection of an enum PV"""


@dataclass
class TextWrite(WriteWidget):
    """Text control of any PV"""

    lines: Annotated[int, desc("Number of lines to display")] = 1


@dataclass
class ArrayWrite(WriteWidget):
    """Control of an array PV"""

    widget: Annotated[WriteWidget, desc("What widget should be used for each item")]


@dataclass
class TableWrite(WriteWidget):
    widgets: Annotated[
        Sequence[WriteWidget],
        desc("For each column, what widget should be repeated for every row"),
    ]


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
class SignalRW(SignalW):
    """Read/write value backed by one or two PVs"""

    # This was Optional[str] but produced JSON schema that YAML editor didn't understand
    read_pv: Annotated[str, desc("PV to be used for read, empty means use pv")] = ""
    read_widget: Annotated[
        Optional[ReadWidget], desc("Widget to use for display, None means use widget")
    ] = None


@dataclass
class SignalX(Component):
    """Executable that puts a fixed value to a PV."""

    pv: Annotated[str, desc("PV to be used for call")]
    value: Annotated[Any, desc("Value to write. None means zero")] = None


@dataclass
class DeviceRef(Component):
    """Reference to another Device."""

    pv: Annotated[str, desc("Child device PVI PV")]


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
    children: Annotated[Tree[Component], desc("Child Components")]

    def serialize(self) -> Mapping[str, Any]:
        """Serialize the Device to a dictionary."""
        return serialize(self, exclude_none=True, exclude_defaults=True)

    @classmethod
    def deserialize(cls, serialized: Mapping[str, Any]) -> Device:
        """Deserialize the Device from a dictionary."""
        return deserialize(cls, serialized)

    def generate_param_tree(self) -> str:
        param_tree = ", ".join(json.dumps(serialize(group)) for group in self.children)
        # Encode again to quote the string as a value and escape double quotes within
        return json.dumps('{"parameters":[' + param_tree + "]}")
