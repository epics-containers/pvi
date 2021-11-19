import re
import sys
from dataclasses import field, make_dataclass
from functools import lru_cache
from typing import Any, Callable, List, Optional, Pattern, TypeVar, Union

from apischema import deserializer, order, schema, serialized, type_name
from apischema.conversions import Conversion
from apischema.conversions.converters import serializer
from apischema.utils import CAMEL_CASE_REGEX, identity
from typing_extensions import Literal

if sys.version_info >= (3, 8):
    from typing import Annotated, Literal
else:
    from typing_extensions import Annotated, Literal

__all__ = ["Annotated", "Literal"]

Cls = TypeVar("Cls", bound=type)


# Permanently cache so we don't include deserialization subclasses defined below
@lru_cache(maxsize=None)
def rec_subclasses(cls: Cls) -> List[Cls]:
    """Recursive implementation of type.__subclasses__"""
    subclasses = []
    for sub_cls in cls.__subclasses__():
        subclasses += [sub_cls] + rec_subclasses(sub_cls)
    return subclasses


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
                    Literal[sub.__name__],
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
    return cls


def add_type_field(cls: Cls) -> Cls:
    return _make_converters(cls, lambda cls: [cls])


def as_discriminated_union(cls: Cls) -> Cls:
    return _make_converters(cls, rec_subclasses)


def desc(description: str, *, pattern: Optional[Union[str, Pattern]] = None):
    return schema(description=description, pattern=pattern)


CAMEL_CASE_REGEX = re.compile(r"(?<![A-Z])[A-Z]|[A-Z][a-z/d]|(?<=[a-z])\d")


def to_title_case(pascal_s: str) -> str:
    """Takes a PascalCaseFieldName and returns an Title Case Field Name

    Args:
        pascal_s: E.g. PascalCaseFieldName
    Returns:
        Title Case converted name. E.g. Pascal Case Field Name
    """
    return CAMEL_CASE_REGEX.sub(lambda m: " " + m.group(), pascal_s)


def truncate_description(desc: str) -> str:
    """Take the first line of a multiline description, truncated to 40 chars"""
    first_line = desc.strip().split("\n")[0]
    return first_line[:40]


def join(texts, indent=0):
    return (" " * indent + "\n").join(texts)
