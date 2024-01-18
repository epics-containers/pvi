from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BaseSettings(BaseModel):
    """A Base class for consistent model settings."""

    model_config = ConfigDict(extra="forbid")


class BaseTyped(BaseSettings):
    """A Base class for tagged unions discriminated by a `type` field."""

    type: str
