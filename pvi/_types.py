"""The types that should be inherited from or produced by Fields."""

from enum import Enum
from typing import Dict, Iterator, List, Union

from pydantic import BaseModel, Field
from dataclasses import dataclass


# These must match the types defined in coniql schema


class ValueAccess(Enum):
    """Does Channel value describe a readback, action or setting."""

    NONE = "Action with no value"
    RO = "Read-only readback value"
    WO = "Write-only action with a value"
    RW = "Readable and writeable setting"


class DisplayForm(Enum):
    """Instructions for how a number should be formatted for display."""

    DEFAULT = "Use the default representation from value"
    STRING = "Force string representation, most useful for array of bytes"
    BINARY = "Binary, precision determines number of binary digits"
    DECIMAL = "Decimal, precision determines number of digits after " "decimal point"
    HEX = "Hexadecimal, precision determines number of hex digits"
    EXPONENTIAL = (
        "Exponential, precision determines number of digits after " "decimal point"
    )
    ENGINEERING = (
        "Exponential where exponent is multiple of 3, "
        "precision determines number of digits after decimal point"
    )


# These classes allow us to generate Records, Devices and Channels in intermediate files


@dataclass
class Record:
    record_type: str  #: The record type string e.g. ao, stringin
    suffix: str  #: Record name is Producer prefix plus this suffix
    fields: Dict[str, str]  #: The record fields
    infos: Dict[str, str]  #: Any infos to be added to the record


@dataclass
class Channel:
    pv: str  #: The pv (with unexpanded macros in it)
    label: str  #: The GUI label for the Channel
    # The following are None to allow multiple references to channels
    # TODO: need Reference component
    description: str = None  #: Description of what the Channel does
    value_access: ValueAccess = None  #: What can you do with the value of the Channel
    display_form: DisplayForm = None  #: How should numeric values be displayed


ChannelUnion = Union[Channel, "ChannelGroup"]


@dataclass
class ChannelGroup:
    label: str  #: The GUI label for the Group
    channels = Dict[str, ChannelUnion]  #: Child channels


@dataclass
class Device:
    description: str  #: Description of what the Device does
    channels = Dict[str, ChannelUnion]  #: Child channels


class WithTypeMetaClass(type(BaseModel)):
    def __new__(mcs, name, bases, namespace, **kwargs):
        # Override type in namespace to be the literal value of the class name
        namespace["type"] = Field(name, const=True)
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class WithType(BaseModel, metaclass=WithTypeMetaClass):
    """BaseModel that adds a type parameter from class name."""

    type: str


class Macro(WithType):
    """Define a Macro that will be passed when making an instance."""

    name: str


class Component(WithType):
    """Something that can appear in the tree of components to make up the
    device."""

    name: str


class Group(Component):
    """Group that can contain multiple parameters or other Groups."""

    name: str = Field(..., description="Name of the Group that will form its label")
    components: List[Component] = Field(..., description="Child Parameters or Groups")


class Producer(WithType):
    def produce_template(
        self, components: List[Component], macros: List[Macro]
    ) -> List[Record]:
        """Produce a database template, components does not include base class
        instances."""
        raise NotImplementedError(self)

    def produce_device(
        self, components: List[Component], macros: List[Macro]
    ) -> Device:
        """Produce a device structure, components includes base class
        instances."""
