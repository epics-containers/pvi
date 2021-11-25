import json
from pathlib import Path
from typing import Optional, Type

import jsonschema
import typer
from apischema import deserialize, serialize
from apischema.json_schema import JsonSchemaVersion, deserialization_schema
from ruamel.yaml import YAML

from pvi import __version__
from pvi._producers import Producer
from pvi.device import Device

cli = typer.Typer()


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@cli.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Print the version and exit",
    )
):
    """PVI builder interface"""


@cli.command()
def schema(output: Path = typer.Argument(..., help="filename to write the schema to"),):
    """Write the JSON schema for the pvi interface or producer interface"""
    cls: Type
    assert output.name.endswith(
        ".schema.json"
    ), f"Expected '{output.name}' to end with '.schema.json'"
    if output.name == "device.schema.json":
        cls = Device
    elif output.name == "producer.schema.json":
        cls = Producer
    else:
        raise ValueError(type)
    schema = deserialization_schema(
        cls, all_refs=True, version=JsonSchemaVersion.DRAFT_7
    )
    output.write_text(json.dumps(schema, indent=2))


UI_SUFFIXES = [".edl", ".adl", ".ui", ".opi", ".bob", ".csv"]


@cli.command()
def produce(
    yaml: Path = typer.Argument(..., help="path to the YAML source file"),
    output: Path = typer.Argument(..., help="filename to write the product to"),
):
    """Parse the producer from YAML and use it to make the requested product"""
    name = yaml.name
    assert name.endswith(".pvi.yaml"), f"Expected '{name}' to end with '.pvi.yaml'"
    # Need to use the safe loader otherwise we get:
    #    TypeError: Invalid JSON type <class 'ruamel.yaml.scalarfloat.ScalarFloat'>
    producer_dict = YAML(typ="safe").load(yaml)
    # first check the definition file with jsonschema since it has more
    # legible error messages than apischema
    jsonschema.validate(producer_dict, deserialization_schema(Producer))
    producer = deserialize(Producer, producer_dict)
    if output.suffix == ".template":
        producer.produce_records(output)
    elif output.suffix == ".csv":
        producer.produce_csv(output)
    elif output.suffixes == [".pvi", ".json"]:
        device = Device(producer.produce_components())
        serialized = serialize(device, exclude_none=True, exclude_defaults=True)
        output.write_text(json.dumps(serialized, indent=2))
    elif output.suffix in UI_SUFFIXES:
        producer.produce_components()
        # func = getattr(formatter, f"produce_{output.suffix[1:]}")
        # func(components, output)
    else:
        producer.produce_other(output)


if __name__ == "__main__":
    cli()
