from __future__ import annotations

import json
import re
from enum import IntEnum
from pathlib import Path
from typing import (
    Annotated,
    Any,
    ClassVar,
    Dict,
    Iterator,
    Optional,
    Sequence,
)

from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag
from typing_extensions import Literal

from pvi._yaml_utils import YamlValidatorMixin, dump_yaml, type_first
from pvi.bases import BaseSettings, TypedModel
from pvi.utils import find_pvi_yaml

PASCAL_CASE_REGEX = re.compile(r"(?<![A-Z])[A-Z]|[A-Z][a-z/d]|(?<=[a-z])\d")
NON_PASCAL_CHARS_RE = re.compile(r"[^A-Za-z0-9]")


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


def enforce_pascal_case(s: str) -> str:
    """Enforce a pascal case string, removing any invalid characters.

    Args:
        s: String to convert

    Returns: PascalCase string

    """
    s = NON_PASCAL_CHARS_RE.sub(lambda _: "", s)
    return s[0].upper() + s[1:]


class TextFormat(IntEnum):
    """Format to use for display of Text{Read,Write} widgets on a UI"""

    decimal = 0
    hexadecimal = 1
    engineer = 2
    exponential = 3
    string = 4


class ReadWidget(BaseSettings):
    """Widget that displays a scalar PV"""

    type: str


class LED(ReadWidget):
    """LED display of a boolean PV"""

    type: Literal["LED"] = "LED"


class BitField(ReadWidget):
    """LED and label for each bit of an int PV"""

    type: Literal["BitField"] = "BitField"

    labels: Sequence[str] = Field(description="Label for each bit")


class ProgressBar(ReadWidget):
    """Progress bar from lower to upper limit of a float PV"""

    type: Literal["ProgressBar"] = "ProgressBar"


class TextRead(ReadWidget):
    """Text view of any PV"""

    type: Literal["TextRead"] = "TextRead"
    model_config = ConfigDict(use_enum_values=True)  # Use Enum value when dumping

    lines: Optional[int] = Field(default=None, description="Number of lines to display")
    format: Optional[TextFormat] = Field(default=None, description="Display format")

    def get_lines(self):
        return self.lines or 1


class ArrayTrace(ReadWidget):
    """Trace of the array in a plot view"""

    type: Literal["ArrayTrace"] = "ArrayTrace"

    axis: str = Field(
        description=(
            "Traces with same axis name will appear on same axis, "
            "plotted against 'x' trace if it exists, or indexes if not. "
            "Only one traces with axis='x' allowed."
        ),
    )


class TableRead(ReadWidget):
    """Tabular view of an NTTable"""

    type: Literal["TableRead"] = "TableRead"

    widgets: Sequence[ReadWidget] = Field(
        [], description="For each column, what widget should be repeated for every row"
    )


class ImageRead(ReadWidget):
    """2D Image view of an NTNDArray"""

    type: Literal["ImageRead"] = "ImageRead"


class WriteWidget(BaseSettings):
    """Widget that controls a PV"""

    type: str


class CheckBox(WriteWidget):
    """Checkable control of a boolean PV"""

    type: Literal["CheckBox"] = "CheckBox"


class ComboBox(WriteWidget):
    """Selection of an enum PV"""

    type: Literal["ComboBox"] = "ComboBox"

    choices: Sequence[str] = Field(default=None, description="Choices to select from")

    def get_choices(self) -> list:
        return [] if self.choices is None else list(self.choices)


class ButtonPanel(WriteWidget):
    """One-or-more buttons that poke a PV with a value

    Args:
        actions: Dict of button label to value the button sends

    """

    type: Literal["ButtonPanel"] = "ButtonPanel"

    actions: Dict[str, str] = Field(default={"go": "1"}, description="PV poker buttons")


class TextWrite(WriteWidget):
    """Text control of any PV"""

    type: Literal["TextWrite"] = "TextWrite"
    model_config = ConfigDict(use_enum_values=True)  # Use Enum value when dumping

    lines: Optional[int] = Field(default=None, description="Number of lines to display")
    format: Optional[TextFormat] = Field(default=None, description="Display format")

    def get_lines(self):
        return self.lines or 1


class ArrayWrite(WriteWidget):
    """Control of an array PV"""

    type: Literal["ArrayWrite"] = "ArrayWrite"

    widget: WriteWidget = Field(description="What widget should be used for each item")


class TableWrite(WriteWidget):
    type: Literal["TableWrite"] = "TableWrite"

    widgets: Sequence[ReadWidgetUnion | WriteWidgetUnion] = Field(
        [], description="For each column, what widget should be repeated for every row"
    )


WidgetType = Annotated[Union[ReadWidget, WriteWidget], Field(discriminator="type")]
TableWidgetType = Annotated[Union[TableRead, TableWrite], Field(discriminator="type")]
TableWidgetTypes = (TableRead, TableWrite)


ReadWidgetUnion = Annotated[
    ArrayTrace | BitField | ImageRead | LED | ProgressBar | TableRead | TextRead,
    Field(discriminator="type"),
]
WriteWidgetUnion = Annotated[
    ArrayWrite | ButtonPanel | CheckBox | ComboBox | TableWrite | TextWrite,
    Field(discriminator="type"),
]


class Layout(BaseModel):
    """Widget displaying child Components"""


class Plot(Layout):
    """Children are traces of the plot"""

    type: Literal["Plot"] = "Plot"


class Row(Layout):
    """Children are columns in the row"""

    type: Literal["Row"] = "Row"

    header: Optional[Sequence[str]] = Field(
        None,
        description="Labels for the items in the row",
    )


class Grid(Layout):
    """Children are rows in the grid"""

    type: Literal["Grid"] = "Grid"

    labelled: bool = Field(True, description="If True use names of children as labels")


class SubScreen(Layout):
    """Children are displayed on another screen opened with a button."""

    type: Literal["SubScreen"] = "SubScreen"

    labelled: bool = Field(default=True, description="Display labels for components")


LayoutUnion = Annotated[
    Plot | Row | Grid | SubScreen,
    Field(discriminator="type"),
]


class Named(TypedModel):
    name: str = Field(
        description="PascalCase name to uniquely identify",
        pattern=r"^([A-Z][a-z0-9]*)*$",
    )


class Component(Named):
    """These make up a Device"""

    label: Optional[str] = None

    def get_label(self):
        return self.label or to_title_case(self.name)


class Signal(Component):
    """Base signal type representing one or two PVs of a `Device`."""

    _access_mode: ClassVar[str]

    @property
    def access_mode(cls) -> str:
        return cls._access_mode


class SignalR(Signal):
    """Read-only `Signal` backed by a single PV."""

    _access_mode = "r"

    read_pv: str = Field(description="PV to be used for reading")
    read_widget: ReadWidgetUnion = Field(
        default_factory=TextRead, description="Widget to use for display"
    )


class SignalW(Signal):
    """Write-only `Signal` backed by a single PV."""

    _access_mode = "w"

    write_pv: str = Field(description="PV to be used for writing")
    write_widget: WriteWidgetUnion = Field(
        default_factory=TextWrite, description="Widget to use for control"
    )


class SignalRW(SignalR, SignalW):
    """Read/write `Signal` backed by a write PV and a readback PV."""

    _access_mode = "rw"


class SignalX(SignalW):
    """`SignalW` that can be triggered to write a fixed value to a PV."""

    value: str = Field(None, description="Value to write. None means zero")
    write_widget: ButtonPanel = Field(
        default_factory=ButtonPanel, description="Widget to use for actions"
    )


class DeviceRef(Component):
    """Reference to another Device."""

    pv: str = Field(description="Child device PVI PV")
    ui: str = Field(description="UI file to open for referenced Device")
    macros: Dict[str, str] = Field(
        default={}, description="Macro-value pairs for UI file"
    )


class SignalRef(Component):
    """Reference to another Signal with the same name in this Device."""


class Group(Component):
    """Group of child components in a Layout"""

    layout: LayoutUnion = Field(description="How to layout children on screen")
    children: Tree = Field(description="Child Components")


ComponentUnion = Annotated[
    Annotated[Group, Tag("Group")]
    | Annotated[SignalR, Tag("SignalR")]
    | Annotated[SignalW, Tag("SignalW")]
    | Annotated[SignalRW, Tag("SignalRW")]
    | Annotated[SignalX, Tag("SignalX")]
    | Annotated[SignalRef, Tag("SignalRef")]
    | Annotated[DeviceRef, Tag("DeviceRef")],
    Field(discriminator=Discriminator(TypedModel.get_type_name)),
]
Tree = Sequence[ComponentUnion]


def walk(tree: Tree) -> Iterator[ComponentUnion]:
    """Depth first traversal of tree"""
    for t in tree:
        yield t
        if isinstance(t, Group):
            yield from walk(t.children)


class Device(TypedModel, YamlValidatorMixin):
    """Collection of Components"""

    label: str = Field(description="Label for screen")
    parent: Optional[
        Annotated[
            str,
            "The parent device (basename of yaml file)",
        ]
    ] = None
    children: Tree = Field([], description="Child Components")

    def _to_dict(self) -> dict[str, Any]:
        """Serialize a `Device` instance to a `dict`.

        The returned dictionary does not include a type field for the `Device` itself
        because the discriminator is specified by the file suffix, `pvi.device.yaml`.

        In real use only `Device.serialize` will be called, which calls this method.
        This method exists as an intermediary to enable testing of the serialization
        logic separately from writing/reading a file.

        """
        d = type_first(self.model_dump(exclude_none=True))
        d.pop("type")
        return d

    def serialize(self, yaml: Path):
        """Serialize a `Device` instance to YAML.

        Args:
            yaml: Path of YAML file

        """
        d = self._to_dict()
        dump_yaml(d, yaml)

    @classmethod
    def deserialize(cls, yaml: Path) -> Device:
        """Instantiate a Device instance from YAML.

        Args:
            serialized: Dictionary of class instance

        """
        serialized = cls.validate_yaml(yaml)
        return cls(**serialized)

    def deserialize_parents(self, yaml_paths: list[Path]):
        """Populate Device with Components from Device yaml of parent classes.

        Args:
            yaml_paths: Paths of parent class Device YAMLs

        """
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
        param_tree = ", ".join(
            json.dumps((group.model_dump_json())) for group in self.children
        )
        # Encode again to quote the string as a value and escape double quotes within
        return json.dumps('{"parameters":[' + param_tree + "]}")


def find_components(yaml_name: str, yaml_paths: list[Path]) -> Tree:
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
