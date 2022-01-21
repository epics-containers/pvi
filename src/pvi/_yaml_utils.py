import re
from pathlib import Path
from typing import Type, TypeVar

from apischema import deserialize, serialize
from ruamel.yaml import YAML

from ._schema_utils import has_type

T = TypeVar("T")


def add_line_before_type(s: str) -> str:
    return re.sub(r"(\s*- type:)", "\n\\g<1>", s)


def serialize_yaml(obj, path: Path):
    serialized = serialize(obj, exclude_none=True, exclude_defaults=True)
    # TODO: add modeline
    YAML().dump(serialized, path, transform=add_line_before_type)


def deserialize_yaml(cls: Type[T], path: Path) -> T:
    # Walk up to find the deserialization root
    while cls not in has_type and len(cls.__mro__) > 1:
        cls = cls.__mro__[1]
    suffix = f".pvi.{cls.__name__.lower()}.yaml"
    assert path.name.endswith(suffix), f"Expected '{path.name}' to end with '{suffix}'"
    # Need to use the safe loader otherwise we get:
    #    TypeError: Invalid JSON type <class 'ruamel.yaml.scalarfloat.ScalarFloat'>
    d = YAML(typ="safe").load(path)
    return deserialize(cls, d)
