import re
from pathlib import Path
from typing import Type, TypeVar, overload

from ruamel.yaml import YAML

T = TypeVar("T")


@overload
def type_first(tree: dict) -> dict: ...


@overload
def type_first(tree: list) -> list: ...


def type_first(tree: dict | list) -> dict | list:
    """Walk through tree and move `type` key of dictionaries to first item.

    Args:
        node: Tree to modify

    Returns:
        The modified tree

    """
    match tree:
        case {"type": type, **rest}:
            # Move 'type' to first in dictionary
            tree = {"type": type} | rest

    # Walk down tree
    if isinstance(tree, dict):
        for key, branch in tree.items():
            if isinstance(branch, (list, dict)):
                tree[key] = type_first(branch)
    elif isinstance(tree, list):
        for idx, branch in enumerate(tree):
            if isinstance(branch, (list, dict)):
                tree[idx] = type_first(branch)

    return tree


def add_line_before_type(s: str) -> str:
    return re.sub(r"(\s*- type:)", "\n\\g<1>", s)


def dump_yaml(serialized: dict, path: Path):
    """Write serialized representation of a class instance to YAML with formatting.

    Ensure that the `type` field of every entry appears first because this
    defines what class the entry corresponds to.

    Add a space in between each entry for readability.

    """
    YAML().dump(serialized, path, transform=add_line_before_type)


class YamlValidatorMixin:
    """Class to serialize and deserialize instances of a class to/from YAML.

    Inheriting this mixin registers that the child class can be serialized to a custom
    pvi.{cls}.yaml - where cls is the class name in lower case - and provides a utility
    to validate that a given YAML file matches the class or its child classes.

    """

    @classmethod
    def validate_yaml(cls: Type, yaml: Path) -> dict:
        """Validate the YAML file and load into a serialized dictionary of an instance.

        This method checks that the given YAML file exists and has an appropriate file
        extension. If these checks pass the YAML file is loaded into a dictionary `d`
        and returned, such that an instance of the class could be instantiated with
        `cls(**d)`.

        Args:
            yaml: YAML representation of class to validate

        Returns: Serialized form of class instance as a dictionary

        """
        if not yaml.is_file():
            raise FileNotFoundError(yaml)

        # Walk up to find the direct child class
        while cls not in YamlValidatorMixin.__subclasses__() and len(cls.__mro__) > 1:
            cls = cls.__mro__[1]

        # Check the file extension matches the given cls
        suffix = f".pvi.{cls.__name__.lower()}.yaml"
        if not yaml.name.endswith(suffix):
            raise ValueError(f"Expected '{yaml.name}' to end with '{suffix}'")

        serialized: dict = YAML(typ="safe").load(yaml)

        cls_type = serialized.get("type", cls.__name__)
        if cls_type != cls.__name__:
            try:
                cls = [c for c in cls.__subclasses__() if c.__name__ == cls_type][0]
            except IndexError:
                raise ValueError(
                    f"Could not deserialize '{cls}' as subtype '{cls_type}', "
                    "not found in subclasses."
                )

        return serialized
