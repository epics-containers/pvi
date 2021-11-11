from dataclasses import dataclass
from typing import Any, Optional, Sequence

from typing_extensions import Annotated as A

from ._utils import as_discriminated_union, desc, to_title_case


@as_discriminated_union
@dataclass
class ReadWidget:
    """Widget that displays a scalar PV"""


class LED(ReadWidget):
    """LED display of a boolean PV"""


@dataclass
class BitField(ReadWidget):
    """LED and label for each bit of an int PV"""

    labels: A[Sequence[str], desc("Label for each bit")]


class ProgressBar(ReadWidget):
    """Progress bar from lower to upper limit of a float PV"""


@dataclass
class TextRead(ReadWidget):
    """Text view of any PV"""

    lines: A[int, desc("Number of lines to display")] = 1


@dataclass
class ArrayTrace(ReadWidget):
    """Trace of the array in a plot view"""

    axis: A[
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

    widgets: A[
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

    lines: A[int, desc("Number of lines to display")] = 1


@dataclass
class ArrayWrite(WriteWidget):
    """Control of an array PV"""

    widget: A[
        WriteWidget, desc("What widget should be used for each item"),
    ]


@dataclass
class TableWrite(WriteWidget):
    widgets: A[
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

    header: A[
        Optional[Sequence[str]],
        desc("Labels for the items in the row, None means use previous row header"),
    ] = None


@dataclass
class Grid(Layout):
    """Children are rows in the grid"""

    labelled: A[bool, desc("If True use names of children as labels")] = True


@dataclass
@as_discriminated_union
class Component:
    """These make up a Device"""

    name: A[
        str, desc("PascalCase name to uniquely identify", pattern=r"([A-Z][a-z0-9]*)*$")
    ]

    # TODO: add optional label in subclasses to override this
    @property
    def label(self):
        return to_title_case(self.name)


@dataclass
class SignalR(Component):
    """Scalar value backed by a single PV"""

    pv: A[str, desc("PV to be used for get and monitor")]
    widget: A[
        Optional[ReadWidget],
        desc("Widget to use for display, None means don't display"),
    ] = None


@dataclass
class SignalRW(Component):
    """Read/Write value backed by one or two PVs"""

    pv: A[str, desc("PV to be used for put")]
    widget: A[
        Optional[WriteWidget],
        desc("Widget to use for control, None means don't display"),
    ] = None
    # This was Optional[str] but produced JSON schema that YAML editor didn't understand
    read_pv: A[str, desc("PV to be used for read, empty means use pv")] = ""
    read_widget: A[
        Optional[ReadWidget], desc("Widget to use for display, None means use widget"),
    ] = None


@dataclass
class SignalX(Component):
    """Executable that puts a fixed value to a PV."""

    pv: A[str, desc("PV to be used for call")]
    value: A[Any, desc("Value to write. None means zero")] = None


@dataclass
class DeviceRef(Component):
    """Reference to another Device."""

    pv: A[str, desc("Child device PVI PV")]


class SignalRef(Component):
    """Reference to another Signal with the same name in this Device."""


@dataclass
class Group(Component):
    """Group of child components in a Layout"""

    layout: A[Layout, desc("How to layout children on screen")]
    children: A[Sequence[Component], desc("Child Components")]


@as_discriminated_union
@dataclass
class Formatter:
    # Screens
    def format_adl(self, components: Sequence[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_edl(self, components: Sequence[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_opi(self, components: Sequence[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_bob(self, components: Sequence[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_ui(self, components: Sequence[Component], basename: str) -> str:
        raise NotImplementedError(self)

    # TODO: add pvi json and csv to cli


@as_discriminated_union
@dataclass
class Producer:
    def produce_records(self):
        """Make epicsdbbuilder records"""
        raise NotImplementedError(self)

    def produce_components(self) -> Sequence[Component]:
        """Make signals from components"""
        raise NotImplementedError(self)

    def produce_text(self, extension: str) -> str:
        """Make things like cpp, h files"""
        raise NotImplementedError(self)
