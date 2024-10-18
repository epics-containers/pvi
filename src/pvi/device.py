from __future__ import annotations

import json
import re
from collections.abc import Iterator, Sequence
from enum import Enum
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    ClassVar,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_validator,
)
from typing_extensions import Self

from pvi._yaml_utils import YamlValidatorMixin, dump_yaml, type_first
from pvi.typed_model import TypedModel, as_tagged_union
from pvi.utils import find_pvi_yaml

PASCAL_CASE_REGEX = re.compile(r"(?<![A-Z])[A-Z]|[A-Z][a-z/d]|(?<=[a-z])\d")
NON_PASCAL_CHARS_RE = re.compile(r"[^A-Za-z0-9]")


def to_title_case(pascal_s: str) -> str:
    """Takes a PascalCaseFieldName and returns an Title Case Field Name

    :param pascal_s: e.g. PascalCaseFieldName

    :returns: Title Case converted name. E.g. Pascal Case Field Name

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

    String will be returned unchanged if it is already valid PascalCase.

    Args:
        s: String to convert

    Returns: PascalCase string

    """
    if PASCAL_CASE_REGEX.fullmatch(s) is not None:
        # Already valid
        return s

    # Do minimal conversion to PascalCase:
    # - Remove any invalid characters
    # - Make first character upper case
    s = NON_PASCAL_CHARS_RE.sub(lambda _: "", s)
    return s[0].upper() + s[1:]


PascalStr = Annotated[str, Field(pattern=r"^([A-Z][a-z0-9]*)*$")]
NumberStr = Annotated[str, Field(pattern=r"^\d*$")]


class TextFormat(Enum):
    """Format to use for display of Text{Read,Write} widgets on a UI"""

    decimal = "decimal"
    hexadecimal = "hexadecimal"
    engineer = "engineer"
    exponential = "exponential"
    string = "string"


class AccessModeMixin(BaseModel):
    _access_mode: ClassVar[str]

    @property
    def access_mode(self) -> str:
        return self._access_mode


class ReadWidget(TypedModel, AccessModeMixin):
    _access_mode = "r"


class LED(ReadWidget):
    """LED display of a boolean PV"""


class BitField(ReadWidget):
    """LED and label for each bit of an int PV"""

    labels: Sequence[str] | None = Field(default=None, description="Label for each bit")
    number_of_bits: int = Field(
        default=8, description="Number of bits to display", gt=0
    )


class ProgressBar(ReadWidget):
    """Progress bar from lower to upper limit of a float PV"""


class TextRead(ReadWidget):
    """Text view of any PV"""

    model_config = ConfigDict(use_enum_values=True)  # Use Enum value when dumping

    lines: int | None = Field(default=None, description="Number of lines to display")
    format: TextFormat | None = Field(default=None, description="Display format")

    def get_lines(self):
        return self.lines or 1


class ArrayTrace(ReadWidget):
    """Trace of the array in a plot view"""

    axis: str = Field(
        description=(
            "Traces with same axis name will appear on same axis, "
            "plotted against 'x' trace if it exists, or indexes if not. "
            "Only one traces with axis='x' allowed."
        ),
    )


class ImageRead(ReadWidget):
    """2D Image view of an NTNDArray"""


class WriteWidget(TypedModel, AccessModeMixin):
    """Widget that controls a PV"""

    _access_mode = "w"


class CheckBox(WriteWidget):
    """Checkable control of a boolean PV.

    This is compact replacement for a `ToggleButton` to be used in rows and tables.

    """


class ToggleButton(WriteWidget):
    """A pair of buttons to select between two mutually exclusive states."""


class ComboBox(WriteWidget):
    """Selection of an enum PV"""

    choices: Annotated[
        Sequence[str] | None, Field(default=None, description="Choices to select from")
    ] = None

    def get_choices(self) -> list[str]:
        return [] if self.choices is None else list(self.choices)


class ButtonPanel(WriteWidget):
    """One-or-more buttons that poke a PV with a value

    Args:
        actions: Dict of button label to value the button sends

    """

    actions: dict[PascalStr, str] = Field(
        default={"Go": "1"}, description="PV poker buttons"
    )


class TextWrite(WriteWidget):
    """Text control of any PV"""

    model_config = ConfigDict(use_enum_values=True)  # Use Enum value when dumping

    lines: int | None = Field(default=None, description="Number of lines to display")
    format: TextFormat | None = Field(default=None, description="Display format")

    def get_lines(self):
        return self.lines or 1


# Subset of widgets that can displayed together in one row
_RowWriteUnion = ButtonPanel | CheckBox | ComboBox | TextWrite
_RowReadUnion = BitField | LED | ProgressBar | TextRead

if not TYPE_CHECKING:
    _RowWriteUnion = as_tagged_union(_RowWriteUnion)
    _RowReadUnion = as_tagged_union(_RowReadUnion)


class ArrayWrite(WriteWidget):
    """Control of an array PV"""

    widget: _RowWriteUnion = Field(
        description="What widget should be used for each item"
    )


class TableRead(ReadWidget):
    """A read-only tabular view of an NTTable."""

    widgets: Sequence[_RowReadUnion] = Field(
        [], description="For each column, what widget should be repeated for every row"
    )


class TableWrite(WriteWidget):
    """A writeable tabular view of an NTTable."""

    widgets: Sequence[_RowWriteUnion] = Field(
        [], description="For each column, what widget should be repeated for every row"
    )


class Layout(TypedModel):
    """Widget displaying child Components"""


class Plot(Layout):
    """Children are traces of the plot"""


class Row(Layout):
    """Children are columns in the row"""

    header: Sequence[str] | None = Field(
        None,
        description="Labels for the items in the row",
    )


class Grid(Layout):
    """Children are rows in the grid"""

    labelled: Annotated[
        bool, Field(description="If True use names of children as labels")
    ] = True


class SubScreen(Layout):
    """Children are displayed on another screen opened with a button."""

    labelled: bool = Field(default=True, description="Display labels for components")


LayoutUnion = Plot | Row | Grid | SubScreen

ReadWidgetUnion = (
    ArrayTrace | BitField | ImageRead | LED | ProgressBar | TableRead | TextRead
)

WriteWidgetUnion = (
    ArrayWrite
    | ButtonPanel
    | CheckBox
    | ComboBox
    | TableWrite
    | TextWrite
    | ToggleButton
)

if not TYPE_CHECKING:
    LayoutUnion = as_tagged_union(LayoutUnion)
    ReadWidgetUnion = as_tagged_union(ReadWidgetUnion)
    WriteWidgetUnion = as_tagged_union(WriteWidgetUnion)


WidgetUnion = ReadWidgetUnion | WriteWidgetUnion


class Named(TypedModel):
    name: Annotated[
        PascalStr | NumberStr,
        Field(description="PascalCase name or number to uniquely identify"),
    ]


class Component(Named):
    """These make up a Device"""

    label: Annotated[str | None, Field(description="Label for component")] = None
    description: Annotated[
        str | None, Field(description="Description for label tooltip")
    ] = None

    def get_label(self):
        return self.label or to_title_case(self.name)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Component) and self.name == other.name


class Signal(Component, AccessModeMixin):
    """Base signal type representing one or two PVs of a `Device`."""


class SignalR(Signal):
    """Read-only `Signal` backed by a single PV."""

    _access_mode = "r"

    read_pv: str = Field(description="PV to use for readback")
    read_widget: Annotated[
        ReadWidgetUnion | None,
        Field(
            description="Widget to use for display. `TextRead` will be used if unset.",
            validate_default=True,
        ),
    ] = TextRead()


class SignalW(Signal):
    """Write-only `Signal` backed by a single PV."""

    _access_mode = "w"

    write_pv: str = Field(description="PV to use for demand")
    write_widget: Annotated[
        WriteWidgetUnion,
        Field(description="Widget to use for control"),
    ] = TextWrite()


class SignalRW(SignalR, SignalW):
    """Read/write `Signal` backed by a demand PV and a readback PV.

    One PV can be used as both a demand and a readback by leaving `read_pv` unset. In
    this case no readback widget will be displayed unless `read_widget` is set.

    If `read_pv` is set and `read_widget` is not, a `TextRead` widget will be used.
    """

    _access_mode = "rw"
    # Flag to show this is a single PV SignalRW and the `read_pv` has been dynamically
    # set to `write_pv`. This ensures that `_validate_model` is idempotent.
    _single_pv_rw = False

    # Make optional and replace with `write_pv` during validation if not given
    read_pv: Annotated[
        str,
        Field(description="PV to use for readback. If empty, `write_pv` will be used."),
    ] = ""
    # Override description
    read_widget: Annotated[
        ReadWidgetUnion | None,
        Field(
            description=(
                "Widget to use for readback display. "
                "A `TextRead` will be used if unset and `read_pv` is given, "
                "else no readback widget will be displayed."
            ),
            validate_default=True,
        ),
    ] = None

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        if self.read_pv and not self._single_pv_rw and self.read_widget is None:
            # Update default read widget if given a read PV
            self.read_widget = TextRead()
        elif not self.read_pv:
            # No read widget, but update to use write PV for read in PVI definition
            self.read_pv = self.write_pv
            self._single_pv_rw = True

        return self


class SignalX(SignalW):
    """`SignalW` that can be triggered to write a fixed value to a PV."""

    value: Annotated[
        str,
        Field(None, description="Value to write. Uses '1' if unset."),
    ] = "1"
    write_widget: Annotated[
        WriteWidgetUnion,
        Field(description="Widget to use for actions"),
    ] = ButtonPanel()

    @model_validator(mode="after")
    def check_write_widget(self) -> Self:
        if not isinstance(self.write_widget, ButtonPanel):
            raise TypeError("SignalX write_widget must be ButtonPanel")

        return self


class DeviceRef(Component):
    """Reference to another Device."""

    pv: str = Field(description="Child device PVI PV")
    ui: str = Field(description="UI file to open for referenced Device")
    macros: dict[str, str] = Field(
        default={}, description="Macro-value pairs for UI file"
    )


class SignalRef(Component):
    """Reference to another Signal with the same name in this Device."""


class Group(Component):
    """Group of child components in a Layout"""

    layout: LayoutUnion = Field(description="How to layout children on screen")
    children: Tree = Field(description="Child Components")


ComponentUnion = Group | SignalR | SignalW | SignalRW | SignalX | SignalRef | DeviceRef

if not TYPE_CHECKING:
    ComponentUnion = as_tagged_union(ComponentUnion)

Tree = Sequence[ComponentUnion]


def walk(tree: Tree) -> Iterator[ComponentUnion]:
    """Depth first traversal of tree"""
    for t in tree:
        if isinstance(t, Group):
            yield from walk(t.children)
        else:
            yield t


class Device(TypedModel, YamlValidatorMixin):
    """Collection of Components"""

    label: str = Field(description="Label for screen")
    parent: Annotated[str, "The parent device (basename of yaml file)"] | None = None
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
        d.pop("type", None)
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
        try:
            return cls(**serialized)
        except ValidationError:
            print(f"\nFailed to validate `{yaml}` as Device:\n")
            raise

    def deserialize_parents(self, yaml_paths: list[Path]):
        """Populate Device with Components from Device yaml of parent classes.

        Args:
            yaml_paths: Paths of parent class Device YAMLs

        """
        if self.parent is None or self.parent == "asynPortDriver":
            return

        parent_components = find_components(self.parent, yaml_paths)
        self.merge_components(parent_components)

    def merge_components(self, components: Tree) -> None:
        existing_components = list(walk(self.children))
        for node in components:
            if isinstance(node, Group):
                for group in self.children:
                    if not isinstance(group, Group):
                        continue
                    elif group.name == node.name:
                        group.children = list(group.children) + [
                            c for c in node.children if c not in group.children
                        ]
                        break  # Groups merged - skip to next group

                else:  # No break - Did not find the Group
                    # Remove any signals already in device from node
                    node.children = [
                        c for c in node.children if c not in existing_components
                    ]

                    # Add node as a new group
                    self.children = list(self.children) + [node]

                    continue  # Skip to next group
            else:
                # Node is an individual AsynParameter - just append it
                self.children = list(self.children) + [node]

    def generate_param_tree(self) -> str:
        param_tree = ", ".join(
            json.dumps(group.model_dump_json()) for group in self.children
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
        raise OSError(f"Cannot find {device_name} in {yaml_paths}")

    device = Device.deserialize(device_yaml)

    parent_components = (
        list(find_components(device.parent, yaml_paths))
        if device.parent is not None
        else []
    )

    return list(device.children) + parent_components
