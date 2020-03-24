from pydantic import Field

from ._types import WithType

VALUE_FIELD = Field(
    None, description="The default value of the parameter, None means required"
)


class Macro(WithType):
    name: str = Field(
        ..., description="The name of the Macro that will be passed when instantiated"
    )
    description: str = Field(
        ..., description="Description of what the Macro will be used for"
    )


class StringMacro(Macro):
    value: str = VALUE_FIELD


class FloatMacro(Macro):
    value: float = VALUE_FIELD
