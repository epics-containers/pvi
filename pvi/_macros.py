from typing import Union

from pydantic import Field

from ._types import Macro

VALUE_FIELD = Field(
    None, description="The default value of the parameter, None means required"
)


class StringMacro(Macro):
    value: str = VALUE_FIELD


class FloatMacro(Macro):
    value: float = VALUE_FIELD


class IntMacro(Macro):
    value: int = VALUE_FIELD


MacroUnion = Union[FloatMacro, StringMacro, IntMacro]
