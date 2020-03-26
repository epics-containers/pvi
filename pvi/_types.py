"""The types that should be inherited from or produced by Fields."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Generic, Optional, Sequence, TypeVar, Union

from pydantic import BaseModel, Field


class WithTypeMetaClass(type(BaseModel)):  # type: ignore
    def __new__(mcs, name, bases, namespace, **kwargs):
        # Override type in namespace to be the literal value of the class name
        namespace["type"] = Field(name, const=True)
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class WithType(BaseModel, metaclass=WithTypeMetaClass):
    """BaseModel that adds a type parameter from class name."""

    type: str


class Component(WithType):
    """Something that can appear in the tree of components to make up the
    device."""

    name: str


T = TypeVar("T")


class Group(Component, Generic[T]):
    """Group that can contain multiple parameters or other Groups."""

    name: str = Field(..., description="Name of the Group that will form its label")
    children: Sequence[Union["Group", T]]


Tree = Sequence[Union[T, Group[T]]]
ComponentTree = Sequence[Union[Component, Group[Component]]]


# These must match the types defined in coniql schema
class DisplayForm(str, Enum):
    """Instructions for how a number should be formatted for display."""

    DEFAULT = "Default"
    STRING = "String"
    BINARY = "Binary"
    DECIMAL = "Decimal"
    HEX = "Hexadecimal"
    EXPONENTIAL = "Exponential"
    ENGINEERING = "Engineering"


class Widget(str, Enum):
    """Default widget that should be used to display this channel"""

    TEXTINPUT = "Text Input"
    TEXTUPDATE = "Text Update"
    MULTILINETEXTUPDATE = "Multiline Text Update"
    LED = "LED"
    COMBO = "Combo"
    CHECKBOX = "Checkbox"
    TABLE = "Table"
    PLOT = "Plot"
    METER = "Meter"
    BUTTON = "Button"


# These classes allow us to generate Records, Devices and Channels in intermediate files
@dataclass
class Record:
    record_name: str  #: The name of the record e.g. $(P)$(M)Status
    record_type: str  #: The record type string e.g. ao, stringin
    fields: Dict[str, str]  #: The record fields
    infos: Dict[str, str]  #: Any infos to be added to the record


RecordTree = Sequence[Union[Record, Group[Record]]]


@dataclass
class Channel:
    name: str  #: The name of the Channel within the Device
    label: str  #: The GUI label for the Channel
    read_pv: Optional[
        str
    ] = None  #: The pv to get from, None means not readable (an action)
    write_pv: Optional[
        str
    ] = None  #: The pv to put to, None means not writeable (a readback)
    # The following are None to allow multiple references to channels
    widget: Optional[Widget] = None  #: Which widget to use for the Channel
    description: Optional[str] = None  #: Description of what the Channel does
    display_form: Optional[
        DisplayForm
    ] = None  #: How should numeric values be displayed


ChannelTree = Sequence[Union[Channel, Group[Channel]]]


@dataclass
class AsynParameter:
    name: str  #: Asyn parameter name
    type: str  #: Asyn parameter type
    description: str  #: Comment about this parameter


AsynParameterTree = Sequence[Union[AsynParameter, Group[AsynParameter]]]


class Producer(WithType):
    def produce_records(self, components: ComponentTree) -> RecordTree:
        """Produce a Record tree structure for database template

        Args:
            components: Tree without base class Component instances

        Returns:
            Record tree structure that should be passed to the Formatter
        """
        raise NotImplementedError(self)

    def produce_asyn_parameters(self, components: ComponentTree) -> AsynParameterTree:
        """Produce any files that need to go in the src/ directory

        Args:
            components: Tree without base class Component instances

        Returns:
            AsynParameter tree structure that should be passed to the Formatter
        """
        raise NotImplementedError(self)

    def produce_channels(self, components: ComponentTree) -> ChannelTree:
        """Produce a channel tree structure for making screens

        Args:
            components: Tree including base class Component instances

        Returns:
            Channel tree structure that should be passed to the Formatter
        """
        raise NotImplementedError(self)


class Formatter(WithType):
    # template_path: str
    # device_path: str
    # opi_path: str
    # bob_path: str
    # adl_path: str
    # edl_path: str
    def format_h_file(self, parameters: AsynParameterTree, basename: str) -> str:
        raise NotImplementedError(self)

    def format_cpp_file(self, parameters: AsynParameterTree, basename: str) -> str:
        raise NotImplementedError(self)
