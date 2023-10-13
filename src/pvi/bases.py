from __future__ import annotations

from functools import lru_cache
from typing import List, Literal, Type

from pydantic import BaseModel, ConfigDict

# def rec_subclasses(cls: Cls) -> List[Cls]:
#     """Recursive implementation of type.__subclasses__"""
#     subclasses = []
#     for sub_cls in cls.__subclasses__():
#         subclasses += [sub_cls] + rec_subclasses(sub_cls)
#     return subclasses


class BaseSettings(BaseModel):
    """A Base class for consistent model settings"""

    model_config = ConfigDict(
        extra="forbid",
    )


# Permanently cache so we don't include deserialization subclasses defined below
@lru_cache(maxsize=None)
def get_all_subclasses(cls: Type) -> List[Type]:
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def add_type(cls: Type) -> Type:
    def __init_subclass__(cls: Type):
        value = Literal[cls.__name__]  # type: ignore
        cls.__annotations__["type"] = value
        cls.type = cls.__name__
        cls.super().__init_subclass__()

    setattr(cls, "__init_subclass__", __init_subclass__)
    return cls
