"""The types that should be inherited from or produced by Fields."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, ForwardRef, Iterator, List, Optional, Union

from pydantic import BaseModel, Field

# These must match the types defined in coniql schema


class DisplayForm(Enum):
    """Instructions for how a number should be formatted for display."""

    DEFAULT = "Use the default representation from value"
    STRING = "Force string representation, most useful for array of bytes"
    BINARY = "Binary, precision determines number of binary digits"
    DECIMAL = "Decimal, precision determines number of digits after decimal point"
    HEX = "Hexadecimal, precision determines number of hex digits"
    EXPONENTIAL = (
        "Exponential, precision determines number of digits after decimal point"
    )
    ENGINEERING = (
        "Exponential where exponent is multiple of 3, "
        "precision determines number of digits after decimal point"
    )


class Widget(Enum):
    """Default widget that should be used to display this channel"""

    TEXTINPUT = "Editable text input box"
    TEXTUPDATE = "Read only text update"
    MULTILINETEXTUPDATE = "Multi line read only text update"
    LED = "On/Off LED indicator"
    COMBO = "Select from a number of values"
    CHECKBOX = "A box that can be checked or not"
    TABLE = "Tabular view of array data"
    PLOT = "Graph view of array data"
    METER = "Progress meter"
    BUTTON = "Action button for no value puts"


# These classes allow us to generate Records, Devices and Channels in intermediate files


@dataclass
class Record:
    record_name: str  #: The name of the record e.g. $(P)$(M)Status
    record_type: str  #: The record type string e.g. ao, stringin
    fields: Dict[str, str]  #: The record fields
    infos: Dict[str, str]  #: Any infos to be added to the record


@dataclass
class Channel:
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


ChannelTree = Dict[str, Union[Channel, ForwardRef("ChannelTree")]]

# These classes are to be inherited from


class WithTypeMetaClass(type(BaseModel)):
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


class Group(Component):
    """Group that can contain multiple parameters or other Groups."""

    name: str = Field(..., description="Name of the Group that will form its label")
    components: List[Component] = Field(..., description="Child Parameters or Groups")


ComponentTree = List[Union[Group, Component]]


class Producer(WithType):
    def produce_records(self, component: Component) -> Iterator[Record]:
        """Called repeatedly to produce records for database template

        Args:
            component: A non-group component defined in this YAML file

        Returns:
            Records that should be passed to the Formatter
        """
        raise NotImplementedError(self)

    def produce_src(self, components: ComponentTree, basename: str) -> Dict[str, str]:
        """Produce any files that need to go in the src/ directory

        Args:
            components: Tree without base class Component instances

        Returns:
            {filename: contents} for source files that should be created
        """
        raise NotImplementedError(self)

    def produce_channels(self, components: ComponentTree) -> ChannelTree:
        """Produce a channel tree structure for making screens

        Args:
            components: Tree including base class Component instances

        Returns:
            A Channel Tree structure
        """
        raise NotImplementedError(self)
