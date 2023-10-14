from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# upating a pydantiv model seems problematic
# https://github.com/pydantic/pydantic/discussions/3139
class BaseSettings(BaseModel):
    """A Base class for consistent model settings"""

    type: Literal["BaseSettings"] = "BaseSettings"

    model_config = ConfigDict(
        extra="forbid",
    )

    @classmethod
    def __init_subclass__(subclass, **kwargs):
        value = Literal[subclass.__name__]  # type: ignore
        subclass.__annotations__["type"] = value
        subclass.type = Field(
            value, description="The dscrimintating type of this entity", required=True
        )
        super().__init_subclass__(**kwargs)


class BaseSettingsSansType(BaseModel):
    """A Base class for consistent model settings"""

    model_config = ConfigDict(
        extra="forbid",
    )
