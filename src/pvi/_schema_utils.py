from dataclasses import field, make_dataclass
from functools import lru_cache
from typing import Any, Callable, List, Mapping, Optional, Pattern, Set, TypeVar, Union

from apischema import deserializer, order, schema, serialized, type_name
from apischema.conversions import Conversion
from apischema.conversions.converters import serializer
from apischema.json_schema import JsonSchemaVersion, deserialization_schema
from apischema.utils import identity
from typing_extensions import Literal

Cls = TypeVar("Cls", bound=type)


# Permanently cache so we don't include deserialization subclasses defined below
@lru_cache(maxsize=None)
def rec_subclasses(cls: Cls) -> List[Cls]:
    """Recursive implementation of type.__subclasses__"""
    subclasses = []
    for sub_cls in cls.__subclasses__():
        subclasses += [sub_cls] + rec_subclasses(sub_cls)
    return subclasses


has_type: Set[type] = set()


def _make_converters(cls: Cls, classes: Callable[[Cls], List[Cls]]) -> Cls:
    params = tuple(getattr(cls, "__parameters__", ()))

    def with_params(sub: Cls) -> Any:
        return sub[params] if params else sub  # type: ignore

    def deserialization() -> Conversion:
        def typed_subs():
            for sub in classes(cls):
                # Make typed_sub derived from sub with additional type entry
                type_field = (
                    "type",
                    Literal[sub.__name__],  # type: ignore
                    field(default=sub.__name__, metadata=order(-1)),
                )
                yield make_dataclass(
                    sub.__name__, [type_field], bases=(with_params(sub),)
                )

        def convert(sub_inst):
            """Make instance of sub from instance of typed_sub"""
            d = {k: v for k, v in sub_inst.__dict__.items() if k != "type"}
            return type(sub_inst).__bases__[0](**d)

        return Conversion(
            convert,
            source=Union[tuple(with_params(s) for s in typed_subs())],  # type: ignore
            target=with_params(cls),
        )

    def serialization() -> Conversion:
        @serialized("type", owner=cls, order=order(-1))
        def add_type(obj) -> str:
            """Add type entry to serialized dictionary"""
            return type(obj).__name__

        return Conversion(
            identity,
            source=cls,
            target=Union[tuple(classes(cls))],  # type: ignore
            inherited=False,
        )

    serializer(lazy=serialization, source=cls)
    deserializer(lazy=deserialization, target=cls)
    type_name(lambda tp, arg: f"{arg.__name__}{tp.__name__}")(cls)
    has_type.add(cls)
    return cls


def add_type_field(cls: Cls) -> Cls:
    return _make_converters(cls, lambda cls: [cls])


def as_discriminated_union(cls: Cls) -> Cls:
    return _make_converters(cls, rec_subclasses)


def desc(description: str, *, pattern: Optional[Union[str, Pattern]] = None):
    return schema(description=description, pattern=pattern)


def make_json_schema(cls: Cls) -> Mapping[str, Any]:
    return deserialization_schema(cls, all_refs=True, version=JsonSchemaVersion.DRAFT_7)
