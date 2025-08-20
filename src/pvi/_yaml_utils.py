import re
from pathlib import Path
from typing import Any, TypeVar, overload

from ruamel.yaml import YAML

T = TypeVar("T")
Leaf = dict[str, Any] | list[Any]
Branch = dict[str, "Branch | Any"] | list["Branch | Any"]
Tree = Branch | Leaf


@overload
def type_first(tree: dict[str, T]) -> dict[str, T]: ...


@overload
def type_first(tree: list[T]) -> list[T]: ...


def type_first(tree: Tree) -> Tree:
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
        case _:
            pass

    # Walk down tree
    if isinstance(tree, dict):
        for key, branch in tree.items():
            if isinstance(branch, list | dict):
                tree[key] = type_first(branch)
    else:
        for idx, branch in enumerate(tree):
            if isinstance(branch, list | dict):
                tree[idx] = type_first(branch)

    return tree


def add_line_before_type(s: str) -> str:
    return re.sub(r"([^:])(\n\s*- type:)", "\\g<1>\n\\g<2>", s)


def dump_yaml(serialized: dict[str, Any], path: Path) -> None:
    """Write serialized representation of a class instance to YAML with formatting.

    Ensure that the `type` field of every entry appears first because this
    defines what class the entry corresponds to.

    Add a space in between each entry for readability.

    """
    yaml = YAML()
    # RedHat YAML plugin settings
    yaml.indent(mapping=2, sequence=4, offset=2)  # type: ignore
    yaml.dump(serialized, path, transform=add_line_before_type)  # type: ignore


def load_yaml(path: Path) -> dict[str, Any]:
    """Load yaml from file."""
    return YAML(typ="safe").load(path)  # type: ignore


class YamlValidatorMixin:
    """Class to serialize and deserialize instances of a class to/from YAML.

    Inheriting this mixin registers that the child class can be serialized to a custom
    pvi.{cls}.yaml - where cls is the class name in lower case - and provides a utility
    to validate that a given YAML file matches the class or its child classes.

    """

    @classmethod
    def validate_yaml(cls: type, yaml: Path) -> dict[str, Any]:
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

        serialized: dict[str, Any] = load_yaml(yaml)

        cls_type: str = serialized.get("type", cls.__name__)
        if cls_type != cls.__name__:
            try:
                cls = [c for c in cls.__subclasses__() if c.__name__ == cls_type][0]
            except IndexError:
                raise ValueError(
                    f"Could not deserialize '{cls}' as subtype '{cls_type}', "
                    "not found in subclasses."
                ) from None

        return serialized
