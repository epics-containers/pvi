from __future__ import annotations

import json
import re
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

from pydantic import Field
from ruamel.yaml import YAML
from typing_extensions import Literal

from pvi.bases import BaseSettings
from pvi.utils import find_pvi_yaml

BaseSettingsDummy = object

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


class ReadWidget(BaseSettings):
    """Widget that displays a scalar PV"""


class LED(ReadWidget):
    """LED display of a boolean PV"""


class BitField(ReadWidget):
    """LED and label for each bit of an int PV"""

    labels: Sequence[str] = Field(description="Label for each bit")


class ProgressBar(ReadWidget):
    """Progress bar from lower to upper limit of a float PV"""


class TextRead(ReadWidget):
    """Text view of any PV"""

    lines: int = Field(1, description="Number of lines to display")
    format: Optional[TextFormat] = Field(None, description="Display format")


class ArrayTrace(ReadWidget):
    """Trace of the array in a plot view"""

    axis: str = Field(
        description=(
            "Traces with same axis name will appear on same axis, "
            "plotted against 'x' trace if it exists, or indexes if not. "
            "Only one traces with axis='x' allowed."
        ),
    )


class TableRead(ReadWidget):
    """Tabular view of an NTTable"""

    widgets: Sequence[ReadWidget] = Field(
        [], description="For each column, what widget should be repeated for every row"
    )


class ImageRead(ReadWidget):
    """2D Image view of an NTNDArray"""


class WriteWidget(BaseSettings):
    """Widget that controls a PV"""


class CheckBox(WriteWidget):
    """Checkable control of a boolean PV"""


class ComboBox(WriteWidget):
    """Selection of an enum PV"""

    choices: Sequence[str] = Field([], description="Choices to select from")


class ButtonPanel(WriteWidget):
    """One-or-more buttons that poke a PV with a value

    Args:
        actions: Dict of button label to value the button sends

    """

    actions: Dict[str, Any] = Field(dict(go=1), description="PV poker buttons")


class TextWrite(WriteWidget):
    """Text control of any PV"""

    lines: int = Field(1, description="Number of lines to display")
    format: Optional[TextFormat] = Field(None, description="Display format")


class ArrayWrite(WriteWidget):
    """Control of an array PV"""

    widget: WriteWidget = Field(description="What widget should be used for each item")


class TableWrite(WriteWidget):
    widgets: Sequence[WidgetType] = Field(
        [], description="For each column, what widget should be repeated for every row"
    )


WidgetType = Annotated[Union[ReadWidget, WriteWidget], Field(discriminator="type")]
TableWidgetType = Annotated[Union[TableRead, TableWrite], Field(discriminator="type")]
TableWidgetTypes = (TableRead, TableWrite)


class Layout(BaseSettings):
    """Widget displaying child Components"""


class Plot(Layout):
    """Children are traces of the plot"""


class Row(Layout):
    """Children are columns in the row"""

    header: Optional[Sequence[str]] = Field(
        None,
        description="Labels for the items in the row, None means use previous row header",
    )


class Grid(Layout):
    """Children are rows in the grid"""

    labelled: bool = Field(True, description="If True use names of children as labels")


class SubScreen(Layout):
    """Children are displayed on another screen opened with a button."""

    labelled: bool = Field(True, description="Display labels for components")


class Named(BaseSettings):
    name: str = Field(
        description="PascalCase name to uniquely identify",
        pattern=r"([A-Z][a-z0-9]*)*$",
    )


class Labelled(Named):
    label: str

    def __init_subclass__(cls, **kwargs):
        # Add an optional label to the end of the dataclass if not already there
        has_label_field = [f for f in cls.model_fields if f == "label"]
        # Hack so this doesn't fire for the Component class below, or anything
        # else that doesn't add annotations. We really want this to be on terminal
        # classes, but no way of knowing this in __init_subclass__
        adds_annotations = bool(cls.__annotations__)
        if not has_label_field and adds_annotations:
            cls.__annotations__["label"]: str = Field(
                description="Label for GUI. If empty, use name in Title Case"
            )

    def get_label(self):
        if getattr(self, "label", ""):
            return self.label
        else:
            return to_title_case(self.name)


class Component(Labelled):
    """These make up a Device"""


class SignalR(Component):
    """Scalar value backed by a single PV"""

    pv: str = Field(description="PV to be used for get and monitor")
    widget: Optional[ReadWidget] = Field(
        None, description="Widget to use for display, None means don't display"
    )


class SignalW(Component):
    """Write only value backed by a single PV"""

    type: Literal["SignalW"] = "SignalW"

    pv: str = Field(description="PV to be used for put")
    widget: Optional[WriteWidget] = Field(
        None, description="Widget to use for control, None means don't display"
    )


class SignalRW(Component):
    """Read/write value backed by one or two PVs"""

    pv: str = Field(description="PV to be used for put")
    widget: Optional[WriteWidget] = Field(
        None, description="Widget to use for control, None means don't display"
    )
    # TODO This was Optional[str] but produced JSON schema that YAML editor didn't understand
    # UPDATE trying optional again in pydantic
    read_pv: Optional[str] = Field(
        None, description="PV to be used for read, empty means use pv"
    )
    read_widget: Optional[ReadWidget] = Field(
        None, description="Widget to use for display, None means use widget"
    )


SignalTypes = (SignalR, SignalW, SignalRW)
ReadSignalType = Annotated[Union[SignalR, SignalRW], Field(discriminator="type")]
WriteSignalType = Annotated[Union[SignalW, SignalRW], Field(discriminator="type")]


class SignalX(Component):
    """Executable that puts a fixed value to a PV."""

    pv: str = Field(description="PV to be used for call")
    value: Any = Field(None, description="Value to write. None means zero")


class DeviceRef(Component):
    """Reference to another Device."""

    pv: str = Field(description="Child device PVI PV")


class SignalRef(Component):
    """Reference to another Signal with the same name in this Device."""


T = TypeVar("T", bound=BaseSettings)
S = TypeVar("S", bound=BaseSettings)


# TODO in all other generics cases I have the BaseModel derived class first
# but here we get the following if we swap the types in Group
# TypeError: <class 'pvi.device.Group'> cannot be parametrized because it
# does not inherit from typing.Generic
class Group(Generic[T], Labelled):
    """Group of child components in a Layout"""

    layout: Layout = Field(description="How to layout children on screen")
    children: SignalR = Field(description="Child Components")


GroupUnion = Annotated[Union[Group[T], T], Field(discriminator="type")]
# TODO TODO we are getting infinite recursion on schem on the command
# pvi schema pvi.device.schema.json
Tree = Sequence[GroupUnion]


def on_each_node(tree: Tree[T], func: Callable[[T], Iterator[S]]) -> Tree[S]:
    """Visit each node of the tree of type typ, calling func on each leaf"""
    out: List[Union[S, Group[S]]] = []
    for t in tree:
        if isinstance(t, Group):
            group: Group[S] = Group(
                name=t.name,
                layout=t.layout,
                children=on_each_node(t.children, func),
                label=t.label,
            )
            out.append(group)
        else:
            out += list(func(t))
    return out


def walk(tree: Tree[T]) -> Iterator[Union[T:BaseModel, Group[T]]]:
    """Depth first traversal of tree"""
    for t in tree:
        yield t
        if isinstance(t, Group):
            yield from walk(t.children)


class Device(BaseSettings):
    """Collection of Components"""

    label: str = Field(description="Label for screen")

    parent: Optional[
        Annotated[
            str,
            "The parent device (basename of yaml file)",
        ]
    ] = None
    children: Tree = Field([], description="Child Components")

    def serialize(self) -> Mapping[str, Any]:
        """Serialize the Device to a dictionary."""
        return self.model_dump(exclude_unset=True, exclude_defaults=True)

    @classmethod
    def deserialize(cls, serialized: Path) -> Device:
        """Deserialize the Device from a YAML file"""
        yaml = YAML(typ="safe").load(serialized)
        return cls(**yaml)

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
        param_tree = ", ".join(
            json.dumps((group.model_dump_json())) for group in self.children
        )
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
