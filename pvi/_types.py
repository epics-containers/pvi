"""The types that should be inherited from or produced by Fields."""

from enum import Enum
from typing import Callable, Dict, Generic, List, Sequence, Type, TypeVar, Union

from pydantic import BaseModel, Field


class WithTypeMetaClass(type(BaseModel)):  # type: ignore
    def __new__(mcs, name, bases, namespace, **kwargs):
        # Override type in namespace to be the literal value of the class name
        namespace["type"] = Field(name, const=True)
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class WithType(BaseModel, metaclass=WithTypeMetaClass):
    """BaseModel that adds a type parameter from class name."""

    type: str


T = TypeVar("T")
C = TypeVar("C", bound="Component")
S = TypeVar("S")
Tree = Sequence[Union[T, "Group[T]"]]


class Component(WithType):
    """Something that can appear in the tree of components to make up the
    device."""

    name: str = Field(
        ...,
        description="CamelCase name to uniquely identify this component",
        regex=r"([A-Z][a-z0-9]*)*$",
    )

    @classmethod
    def on_each_node(
        cls: Type[C], tree: Tree["Component"], func: Callable[[C], List[S]]
    ) -> Tree[S]:
        """Visit each node of the tree of type typ, calling func on each leaf"""
        out: List[Union[S, Group[S]]] = []
        for t in tree:
            if isinstance(t, Group):
                group: Group[S] = Group(
                    name=t.name, children=cls.on_each_node(t.children, func)
                )
                out.append(group)
            elif isinstance(t, cls):
                out += func(t)
        return out


class Group(Component, Generic[T]):
    """Group that can contain multiple parameters or other Groups."""

    children: Tree[T]


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
class Record(BaseModel):
    name: str = Field(..., description="The name of the record e.g. $(P)$(M)Status")
    type: str = Field(..., description="The record type string e.g. ao, stringin")
    fields_: Dict[str, str] = Field(
        ..., description="The record fields", alias="fields"
    )
    infos: Dict[str, str] = Field({}, description="Any infos to be added to the record")


class Channel(BaseModel):
    name: str = Field(..., description="The name of the Channel within the Device")
    label: str = Field(..., description="The GUI label for the Channel")
    read_pv: str = Field(
        None, description="The pv to get from, None means not readable (an action)"
    )
    write_pv: str = Field(
        None, description="The pv to put to, None means not writeable (a readback)"
    )
    # The following are None to allow multiple references to channels
    widget: Widget = Field(None, description="Which widget to use for the Channel")
    description: str = Field(None, description="Description of what the Channel does")
    display_form: DisplayForm = Field(
        None, description="How should numeric values be displayed"
    )


class AsynParameter(BaseModel):
    name: str = Field(..., description="Asyn parameter name")
    type: str = Field(..., description="Asyn parameter type")
    description: str = Field(..., description="Comment about this parameter")


class Producer(WithType):
    def produce_records(self, components: Tree[Component]) -> Tree[Record]:
        """Produce a Record tree structure for database template

        Args:
            components: Tree without base class Component instances

        Returns:
            Record tree structure that should be passed to the Formatter
        """
        raise NotImplementedError(self)

    def produce_asyn_parameters(
        self, components: Tree[Component]
    ) -> Tree[AsynParameter]:
        """Produce any files that need to go in the src/ directory

        Args:
            components: Tree without base class Component instances

        Returns:
            AsynParameter tree structure that should be passed to the Formatter
        """
        raise NotImplementedError(self)

    def produce_channels(self, components: Tree[Component]) -> Tree[Channel]:
        """Produce a channel tree structure for making screens

        Args:
            components: Tree including base class Component instances

        Returns:
            Channel tree structure that should be passed to the Formatter
        """
        raise NotImplementedError(self)


class Formatter(WithType):
    def format_adl(self, channels: Tree[Channel], basename: str) -> str:
        raise NotImplementedError(self)

    def format_edl(self, channels: Tree[Channel], basename: str) -> str:
        raise NotImplementedError(self)

    def format_opi(self, channels: Tree[Channel], basename: str) -> str:
        raise NotImplementedError(self)

    def format_bob(self, channels: Tree[Channel], basename: str) -> str:
        raise NotImplementedError(self)

    def format_ui(self, channels: Tree[Channel], basename: str) -> str:
        raise NotImplementedError(self)

    def format_csv(self, channels: Tree[Channel], basename: str) -> str:
        raise NotImplementedError(self)

    def format_template(self, records: Tree[Record], basename: str) -> str:
        raise NotImplementedError(self)

    def format_h(self, parameters: Tree[AsynParameter], basename: str) -> str:
        raise NotImplementedError(self)

    def format_cpp(self, parameters: Tree[AsynParameter], basename: str) -> str:
        raise NotImplementedError(self)
