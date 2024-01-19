from pathlib import Path
from typing import Any, Literal, Union

from pydantic import Field, TypeAdapter

from pvi._yaml_utils import YamlValidatorMixin
from pvi.bases import BaseTyped
from pvi.device import Device, DeviceRef, enforce_pascal_case


class IndexEntry(BaseTyped):
    """A structure defining an index button to launch a UI with some macros."""

    type: Literal["IndexEntry"] = "IndexEntry"

    label: str = Field(
        "Button label. This will be converted to PascalCase if it is not already."
    )
    ui: str = Field("File name of UI to open with button")
    macros: dict[str, str] = Field("Macros to launch UI with")


class Formatter(BaseTyped, YamlValidatorMixin):
    """Base UI formatter."""

    @classmethod
    def type_adapter(cls) -> TypeAdapter:
        """Create TypeAdapter of all child classes"""
        return TypeAdapter(Union[tuple(cls.__subclasses__())])  # type: ignore

    @classmethod
    def from_dict(cls, serialized: dict) -> "Formatter":
        """Instantiate a Formatter child class from a dictionary.

        Args:
            serialized: Dictionary of class instance

        """
        return cls.type_adapter().validate_python(serialized)

    @classmethod
    def deserialize(cls, yaml: Path) -> "Formatter":
        """Instantiate a Formatter child class from YAML.

        Args:
            yaml: Path of YAML file

        """
        serialized = cls.validate_yaml(yaml)
        return cls.from_dict(serialized)

    @classmethod
    def create_schema(cls) -> dict[str, Any]:
        """Create a schema of Formatter child classes.

        Formatter itself is not included, as it should not be instanstiated directly.

        """
        return cls.type_adapter().json_schema()

    def format(self, device: Device, prefix: str, path: Path):
        """To be implemented by child classes to define how to format specific UIs.

        Args:
            device: Device to populate UI from
            prefix: PV prefix for widgets
            path: Output file path to write UI to

        """
        raise NotImplementedError(self)

    def format_index(self, label: str, index_entries: list[IndexEntry], path: Path):
        """Format an index of buttons to open the given UIs.

        Args:
            label: Title of generated index UI
            index_entries: Buttons to format on the index UI
            path: Output path of generated UI

        """
        self.format(
            Device(
                label=label,
                children=[
                    DeviceRef(
                        name=enforce_pascal_case(index.label),
                        pv=index.label.upper(),
                        ui=index.ui,
                        macros=index.macros,
                    )
                    for index in index_entries
                ],
            ),
            prefix="Index",
            path=path,
        )
