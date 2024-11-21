from pathlib import Path
from typing import Annotated, Any, Union

from pydantic import Field, TypeAdapter

from pvi._yaml_utils import YamlValidatorMixin
from pvi.device import Device, DeviceRef, enforce_pascal_case
from pvi.typed_model import TypedModel, as_tagged_union


class IndexEntry(TypedModel):
    """A structure defining an index button to launch a UI with some macros."""

    label: Annotated[
        str,
        Field(description="Button label (this will be converted to PascalCase)"),
    ]
    ui: Annotated[str, Field(description="File name of UI to open with button")]
    macros: Annotated[dict[str, str], Field(description="Macros to launch UI with")]


class Formatter(TypedModel, YamlValidatorMixin):
    """Base UI formatter."""

    @classmethod
    def type_adapter(cls) -> TypeAdapter["Formatter"]:
        """Create TypeAdapter of all child classes"""
        return TypeAdapter(
            as_tagged_union(Union[tuple(cls.__subclasses__())])  # type: ignore # noqa: UP007
        )

    @classmethod
    def from_dict(cls, serialized: dict[str, Any]) -> "Formatter":
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
        cls.rebuild_child_models()
        return cls.type_adapter().json_schema()

    def format(self, device: Device, path: Path) -> None:
        """To be implemented by child classes to define how to format specific UIs.

        Args:
            device: Device to populate UI from
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
                        label=index.label,
                        pv=index.label.upper(),
                        ui=index.ui,
                        macros=index.macros,
                    )
                    for index in index_entries
                ],
            ),
            path=path,
        )
