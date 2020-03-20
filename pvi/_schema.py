from typing import List, Union

from pydantic import BaseModel, Field

from ._types import WithType, Group
from ._asyn import AsynFloat64, AsynString, AsynProducer, DLSAsynProducer
from ._stream import StreamFloat64, StreamString
from ._arguments import FloatArgument, StringArgument


ArgumentUnion = Union[FloatArgument, StringArgument]
ProducerUnion = Union[AsynProducer, DLSAsynProducer]
ComponentUnion = Union[
    "SchemaGroup", AsynFloat64, AsynString, StreamFloat64, StreamString
]


# Can't do this in types as we don't know what Component types we can have
class SchemaGroup(Group):
    children: List[ComponentUnion] = Field(
        ..., description="Child Parameters or Groups"
    )


SchemaGroup.update_forward_refs()


class Schema(BaseModel):
    base: str = Field(None, description="YAML file to use as base class for this")
    local: str = Field(
        None, description="YAML file that overrides this for local changes"
    )
    arguments: List[Union[StringArgument, FloatArgument]] = Field(
        [], description="Arguments needed to make an isntance of this"
    )
    producer: ProducerUnion = Field(
        ..., description="The Producer class to make templates, screens, etc."
    )
    components: List[GroupOrParameter]

    pv_prefix: str = Field(
        ..., description="The PV Prefix for records created by the template file"
    )
    template_file: str = Field(
        ..., description="Path to the template file that will be created"
    )
    includes: List[Union[DBInclude, YAMLInclude]]
    startup_script: str
