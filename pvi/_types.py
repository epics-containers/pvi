"""The types that should be inherited from or produced by Fields."""
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel, Field

from ._util import camel_to_title
from .coniql_schema import DisplayForm, Layout, Widget


# These classes allow us to generate Records, Devices and Channels in intermediate files
class Record(BaseModel):
    name: str = Field(..., description="The name of the record e.g. $(P)$(M)Status")
    type: str = Field(..., description="The record type string e.g. ao, stringin")
    fields_: Dict[str, str] = Field(
        ..., description="The record fields", alias="fields"
    )
    infos: Dict[str, str] = Field({}, description="Any infos to be added to the record")


class AsynParameter(BaseModel):
    name: str = Field(..., description="Channel name (base name of PV)")
    type: str = Field(..., description="Asyn parameter type")
    index_name: str = Field(..., description="Name of index variable in source code")
    description: str = Field(..., description="Comment about this parameter")


# These are used in the definition of the Schema
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
    label: str = Field(
        None,
        description="The GUI Label for this, default is name converted to Title Case",
    )

    def get_label(self) -> str:
        """If the component has a label, use that, otherwise
        return the Title Case version of its camelCase name"""
        label = self.label
        if label is None:
            label = camel_to_title(self.name)
        return label

    # override dict method
    # want to always return 'type' even when using exclude_unset=True
    # want to return all enums as values
    def dict(self, **kwargs):
        default_export = super().dict(**kwargs)
        modified_export = {**dict(type=self.type), **default_export}
        for key, value in modified_export.items():
            if isinstance(value, Enum):
                modified_export[key] = value.value
        return modified_export

    @classmethod
    def on_each_node(
        cls: Type[C], tree: Tree["Component"], func: Callable[[C], List[S]]
    ) -> Tree[S]:
        """Visit each node of the tree of type typ, calling func on each leaf"""
        out: List[Union[S, Group[S]]] = []
        for t in tree:
            if isinstance(t, Group):
                group: Group[S] = Group(
                    name=t.name,
                    label=t.label,
                    children=cls.on_each_node(t.children, func),
                )
                out.append(group)
            elif isinstance(t, cls):
                out += func(t)
        return out


class Group(Component, Generic[T]):
    """Group that can contain multiple parameters or other Groups."""

    layout: Layout = Field(
        Layout.BOX, description="The layout to arrange the children within"
    )
    children: Tree[T]


def walk(tree: Tree[T]) -> Iterator[Union[T, Group[T]]]:
    """Depth first traversal of tree"""
    for t in tree:
        yield t
        if isinstance(t, Group):
            yield from walk(t.children)


class ChannelConfig(Component):
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


class File(BaseModel):
    path: str = Field(..., description="Path to the file, can include macros")
    macros: Dict[str, Any] = Field(
        {}, description="Extra macros to pass along with the macros from this file"
    )


class Macro(WithType):
    name: str = Field(
        ..., description="The name of the Macro that will be passed when instantiated"
    )
    description: str = Field(
        ..., description="Description of what the Macro will be used for"
    )
    value: Any


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

    def produce_channels(self, components: Tree[Component]) -> Tree[ChannelConfig]:
        """Produce a channel tree structure for making screens

        Args:
            components: Tree including base class Component instances

        Returns:
            Channel tree structure that should be passed to the Formatter
        """
        raise NotImplementedError(self)


class Formatter(WithType):
    def format_adl(
        self, channels: Tree[ChannelConfig], basename: str, macros: List[Macro]
    ) -> str:
        raise NotImplementedError(self)

    def format_edl(
        self, channels: Tree[ChannelConfig], basename: str, macros: List[Macro]
    ) -> str:
        raise NotImplementedError(self)

    def format_opi(
        self, channels: Tree[ChannelConfig], basename: str, macros: List[Macro]
    ) -> str:
        raise NotImplementedError(self)

    def format_bob(
        self, channels: Tree[ChannelConfig], basename: str, macros: List[Macro]
    ) -> str:
        raise NotImplementedError(self)

    def format_ui(
        self, channels: Tree[ChannelConfig], basename: str, macros: List[Macro]
    ) -> str:
        raise NotImplementedError(self)

    def format_yaml(
        self, channels: Tree[ChannelConfig], basename: str, macros: List[Macro]
    ) -> str:
        raise NotImplementedError(self)

    def format_csv(
        self, channels: Tree[ChannelConfig], basename: str, macros: List[Macro]
    ) -> str:
        raise NotImplementedError(self)

    def format_template(
        self, records: Tree[Record], basename: str, macros: List[Macro]
    ) -> str:
        raise NotImplementedError(self)

    def format_h(
        self, parameters: Tree[AsynParameter], basename: str, macros: List[Macro]
    ) -> str:
        raise NotImplementedError(self)
