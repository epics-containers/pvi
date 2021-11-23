from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
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

from ._utils import (
    Annotated,
    add_type_field,
    as_discriminated_union,
    desc,
    to_title_case,
)


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

    widget: Annotated[
        WriteWidget, desc("What widget should be used for each item"),
    ]


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

    # TODO: add optional label in subclasses to override this
    @property
    def label(self):
        return to_title_case(self.name)


@as_discriminated_union
class Component(Named):
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
        Optional[ReadWidget], desc("Widget to use for display, None means use widget"),
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
class Group(Generic[T], Named):
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
                name=t.name, layout=t.layout, children=on_each_node(t.children, func),
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

    children: Annotated[Tree[Component], desc("Child Components")]

    def serialize(self) -> Mapping[str, Any]:
        """Serialize the Device to a dictionary."""
        return serialize(self, exclude_none=True, exclude_defaults=True)

    @classmethod
    def deserialize(cls, serialized: Mapping[str, Any]) -> Device:
        """Deserialize the Device from a dictionary."""
        return deserialize(cls, serialized)


@as_discriminated_union
@dataclass
class Formatter:
    # Screens
    def format_adl(self, components: Tree[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_edl(self, components: Tree[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_opi(self, components: Tree[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_bob(self, components: Tree[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_ui(self, components: Tree[Component], basename: str) -> str:
        raise NotImplementedError(self)

    # TODO: add pvi json and csv to cli


@as_discriminated_union
@dataclass
class Producer:
    def produce_components(self) -> Tree[Component]:
        """Make signals from components"""
        raise NotImplementedError(self)

    def produce_csv(self, path: Path):
        """Make docs csv table"""
        raise NotImplementedError(self)

    def produce_records(self, path: Path):
        """Make epicsdbbuilder records"""
        raise NotImplementedError(self)

    def produce_other(self, path: Path):
        """Make things like cpp, h files"""
        raise NotImplementedError(self)


class Access(str, Enum):
    """What access does the user have. One of:

    - R: Read only value that cannot be set. E.g. chipTemperature on a detector,
      or isHomed for a motor
    - W: Write only value that can be written to, but there is no current value.
      E.g. reboot on a detector, or overwriteCurrentPosition for a motor
    - RW: Read and Write value that can be written to and read back.
      E.g. acquireTime on a detector, or velocity of a motor
    """

    R = "R"  #: Read record only
    W = "W"  #: Write record only
    RW = "RW"  #: Read and write record

    def needs_read_record(self):
        return self != self.W

    def needs_write_record(self):
        return self != self.R


class DisplayForm(str, Enum):
    """Instructions for how a number should be formatted for display"""

    #: Use the default representation from value
    DEFAULT = "Default"
    #: Force string representation, most useful for array of bytes
    STRING = "String"
    #: Binary, precision determines number of binary digits
    BINARY = "Binary"
    #: Decimal, precision determines number of digits after decimal point
    DECIMAL = "Decimal"
    #: Hexadecimal, precision determines number of hex digits
    HEX = "Hex"
    #: Exponential, precision determines number of digits after decimal point
    EXPONENTIAL = "Exponential"
    #: Exponential where exponent is multiple of 3, precision determines number of
    #: digits after decimal point
    ENGINEERING = "Engineering"
