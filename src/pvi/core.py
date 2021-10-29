from dataclasses import dataclass, field, make_dataclass
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, TypeVar, Union

from apischema import deserializer, order, schema, serialized
from apischema.conversions import Conversion
from typing_extensions import Annotated as A
from typing_extensions import Literal


def rec_subclasses(cls: type) -> Iterator[type]:
    """Recursive implementation of type.__subclasses__"""
    for sub_cls in cls.__subclasses__():
        yield sub_cls
        yield from rec_subclasses(sub_cls)


Cls = TypeVar("Cls", bound=type)


def as_discriminated_union(cls: Cls) -> Cls:
    @serialized("type", owner=cls)
    def add_type(obj) -> str:
        """Add type entry to serialized dictionary"""
        return type(obj).__name__

    def deserialization() -> Conversion:
        union = None
        for sub in list(rec_subclasses(cls)):
            # Make typed_sub derived from sub with additional type entry
            type_field = (
                "type",
                Literal[sub.__name__],
                field(default=sub.__name__, metadata=order(-1)),
            )
            typed_sub = make_dataclass(
                sub.__name__, [type_field], bases=(sub,)  # type: ignore
            )
            if union is None:
                union = typed_sub
            else:
                union = Union[union, typed_sub]
        assert union, f"No subclasses of {cls}"

        def convert(sub_inst):
            """Make instance of sub from instance of typed_sub"""
            d = {k: v for k, v in sub_inst.__dict__.items() if k != "type"}
            return type(sub_inst).__bases__[0](**d)

        return Conversion(convert, source=union, target=cls)

    deserializer(lazy=deserialization, target=cls)
    return cls


@as_discriminated_union
class ReadWidget:
    """Widget that displays a PV."""


class LED(ReadWidget):
    """LED display of a boolean PV."""


@dataclass
class BitField(ReadWidget):
    """LED and label for each bit of an int PV."""

    labels: A[List[str], schema(description="Label for each bit")]


class ProgressBar(ReadWidget):
    """Progress bar from lower to upper limit of a float PV."""


@dataclass
class TextRead(ReadWidget):
    """Text view of any PV."""

    lines: A[int, schema(description="Number of lines to display")] = 1


@dataclass
class ArrayRead(ReadWidget):
    """View of an array PV with a TextRead"""


@dataclass
class Image(ReadWidget):
    """Image view of an NTNDArray"""


@as_discriminated_union
class WriteWidget:
    """Widget that controls a PV"""


class CheckBox(WriteWidget):
    """Checkable control of a boolean PV"""


class ComboBox(WriteWidget):
    """Selection of an enum PV"""


@dataclass
class TextWrite(WriteWidget):
    """Text control of any PV"""

    lines: A[int, schema(description="Number of lines to display")] = 1


@dataclass
class ArrayWrite(WriteWidget):
    """Control of an array PV with a TextControl or ComboBox"""

    choices: A[
        Optional[List[str]],
        schema(description="If given, use a ComboBox with the given choices"),
    ]


@as_discriminated_union
class Signal:
    """A single value backed by one or more PVs."""


@dataclass
class SignalR(Signal):
    """Read only value backed by a read-only PV"""

    read_pv: A[str, schema(description="PV to be used for get and monitor")]
    read_widget: A[
        Optional[ReadWidget], schema(description="Widget to use for display")
    ] = None


@dataclass
class SignalW(Signal):
    """Write only value backed by a write-only PV whose value shouldn't be saved"""

    write_pv: A[str, schema(description="PV to be used for put")]
    write_widget: A[
        Optional[WriteWidget], schema(description="Widget to use for control")
    ] = None


@dataclass
class SignalRW(SignalW):
    """Read/Write value backed by a pair of PVs"""

    read_pv: A[
        Optional[str],
        schema(description="PV to be used for read, None means use write_pv"),
    ] = None
    read_widget: A[
        Optional[ReadWidget],
        schema(description="Widget to use for display, None means use write_widget"),
    ] = None
    is_config: A[
        bool, schema(description="Is this a configuration value that should be saved?")
    ] = False
    set_after: A[
        Optional[str],
        schema(
            description="Name of another signal. "
            "If given, the other signal should be set before this one."
        ),
    ] = None


@dataclass
class SignalX(Signal):
    """Executable that puts a fixed value to a PV."""

    write_pv: A[str, schema(description="PV to be used for put")]
    write_value: A[Any, schema(description="Value to write. None means zero.")] = None


@as_discriminated_union
class Composite:
    """A composite value backed by multiple Signals."""


@dataclass
class Table(Composite):
    pv: A[Optional[str], schema(description="NTTable pv to read/write to")] = None
    columns: A[
        List[str],
        schema(
            description="Name of signals with ArrayRead/ArrayWrite widgets for columns"
        ),
    ] = field(default_factory=list)


@dataclass
class Trace:
    y: A[
        str,
        schema(description="Name of signal with ArrayRead widget for y axis of trace"),
    ]
    x: A[
        Optional[str],
        schema(description="Name of signal with ArrayRead widget for x axis of trace"),
    ] = None
    y_axis: A[Optional[str], schema(description="Y axis name to plot on")] = None


@dataclass
class Plot(Composite):
    traces: A[List[Trace], schema(description="Traces to plot")]


@dataclass
class Row(Composite):
    columns: A[List[str], schema(description="Name of signals to lay out horizontally")]


class GridStyle(str, Enum):
    GROUPBOX = "GROUPBOX"
    TITLEBAR = "TITLEBAR"
    OUTLINE = "OUTLINE"
    NONE = "NONE"


@dataclass
class Grid(Composite):
    rows: A[List[str], schema(description="Name of signals to lay out vertically")]
    style: A[
        GridStyle, schema(description="How to present the contents")
    ] = GridStyle.NONE


@dataclass
class Screen(Composite):
    contents: A[
        List[str], schema(description="Name of grids/tables/plots to put in screen")
    ]


@dataclass
class Device:
    """Describes the Signals that make up a particular Device"""

    signals: A[Dict[str, Signal], schema(description="Single values")]
    composites: A[Dict[str, Composite], schema(description="Composite values")]
    devices: A[Dict[str, str], schema(description="Child device PVs")]
