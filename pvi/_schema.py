from typing import List, Union

from pydantic import BaseModel, Field

from ._asyn import AsynFloat64, AsynProducer, AsynString
from ._macros import FloatMacro, StringMacro
from ._types import Group as _Group

# from ._stream import StreamFloat64, StreamString, StreamProducer
# from ._formatters import APSFormatter, DLSFormatter

MacroUnion = Union[FloatMacro, StringMacro]
ProducerUnion = Union[AsynProducer]  # , StreamProducer]
# FormatterUnion = Union[APSFormatter, DLSFormatter]
ComponentUnion = Union["Group", AsynFloat64, AsynString]


class Group(_Group):
    """Group that can contain multiple parameters or other Groups."""

    components: List[ComponentUnion] = Field(
        ..., description="Child Parameters or Groups"
    )


Group.update_forward_refs()


class Schema(BaseModel):
    base: str = Field(None, description="YAML file to use as base class for this")
    local: str = Field(
        None, description="YAML file that overrides this for local changes"
    )
    macros: List[MacroUnion] = Field(
        [], description="Macros needed to make an instance of this"
    )
    producer: ProducerUnion = Field(
        ..., description="The Producer class to make Records and the Device"
    )
    components: List[ComponentUnion] = Field(
        ..., description="The Components to pass to the Producer"
    )
    startup_lines: List[str] = Field(
        [], description="Lines to insert into the startup script"
    )
    extra_db_files: List[str] = Field(
        [], description="List of paths to extra db files to include"
    )


Schema.update_forward_refs()
