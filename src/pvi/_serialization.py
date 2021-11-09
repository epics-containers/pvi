from dataclasses import field, make_dataclass
from functools import lru_cache
from typing import List, TypeVar, Union

from apischema import deserializer, order, schema, serialized
from apischema.conversions import Conversion
from apischema.conversions.converters import serializer
from apischema.utils import identity
from typing_extensions import Literal


# Permanently cache so we don't include deserialization subclasses defined below
@lru_cache(maxsize=None)
def rec_subclasses(cls: type) -> List[type]:
    """Recursive implementation of type.__subclasses__"""
    subclasses = []
    for sub_cls in cls.__subclasses__():
        subclasses += [sub_cls] + rec_subclasses(sub_cls)
    return subclasses


Cls = TypeVar("Cls", bound=type)


def as_discriminated_union(cls: Cls) -> Cls:
    def deserialization() -> Conversion:
        def typed_subs():
            for sub in rec_subclasses(cls):
                # Make typed_sub derived from sub with additional type entry
                type_field = (
                    "type",
                    Literal[sub.__name__],
                    field(default=sub.__name__, metadata=order(-1)),
                )
                yield make_dataclass(
                    sub.__name__, [type_field], bases=(sub,)  # type: ignore
                )

        def convert(sub_inst):
            """Make instance of sub from instance of typed_sub"""
            d = {k: v for k, v in sub_inst.__dict__.items() if k != "type"}
            return type(sub_inst).__bases__[0](**d)

        return Conversion(
            convert,
            source=Union[tuple(typed_subs())],  # type: ignore
            target=cls,
        )

    def serialization() -> Conversion:
        @serialized("type", owner=cls, order=order(-1))
        def add_type(obj) -> str:
            """Add type entry to serialized dictionary"""
            return type(obj).__name__

        return Conversion(
            identity,
            source=cls,
            target=Union[tuple(rec_subclasses(cls))],  # type: ignore
            inherited=False,
        )

    serializer(lazy=serialization, source=cls)
    deserializer(lazy=deserialization, target=cls)
    return cls


def desc(description: str):
    return schema(description=description)
