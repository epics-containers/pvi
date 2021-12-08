import json
from pathlib import Path
from typing import Optional, Type, TypeVar

import jsonschema
import typer
from apischema import deserialize, serialize
from apischema.json_schema import JsonSchemaVersion, deserialization_schema
from ruamel.yaml import YAML

from pvi import __version__
from pvi._formatters import Formatter
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
    if output.name == "pvi.device.schema.json":
        cls = Device
    elif output.name == "pvi.producer.schema.json":
        cls = Producer
    elif output.name == "pvi.formatter.schema.json":
        cls = Formatter
    else:
        typer.echo(f"Don't know how to create {output.name}")
        raise typer.Exit(code=1)
    schema = deserialization_schema(
        cls, all_refs=True, version=JsonSchemaVersion.DRAFT_7
    )
    output.write_text(json.dumps(schema, indent=2))


T = TypeVar("T")


def deserialize_yaml(cls: Type[T], path: Path) -> T:
    suffix = f".pvi.{cls.__name__.lower()}.yaml"
    assert path.name.endswith(suffix), f"Expected '{path.name}' to end with '{suffix}'"
    # Need to use the safe loader otherwise we get:
    #    TypeError: Invalid JSON type <class 'ruamel.yaml.scalarfloat.ScalarFloat'>
    d = YAML(typ="safe").load(path)
    # first check the definition file with jsonschema since it has more
    # legible error messages than apischema
    jsonschema.validate(d, deserialization_schema(cls))
    return deserialize(cls, d)


@cli.command()
def produce(
    producer: Path = typer.Argument(..., help="path to the producer .pvi.yaml file"),
    output: Path = typer.Argument(..., help="filename to write the product to"),
):
    """Parse the producer from YAML and use it to make the requested product"""
    producer_inst = deserialize_yaml(Producer, producer)
    if output.suffix == ".template":
        producer_inst.produce_records(output)
    elif output.suffix == ".csv":
        producer_inst.produce_csv(output)
    elif output.suffixes == [".pvi", ".device", ".yaml"]:
        device = producer_inst.produce_device()
        serialized = serialize(device, exclude_none=True, exclude_defaults=True)
        # TODO: add modeline
        YAML().dump(serialized, output)
    else:
        producer_inst.produce_other(output)


@cli.command()
def format(
    producer: Path = typer.Argument(..., help="path to the .pvi.producer.yaml file"),
    formatter: Path = typer.Argument(..., help="path to the .pvi.formatter.yaml file"),
    output: Path = typer.Argument(..., help="filename to write the product to"),
):
    """Parse producer and formatter from YAML and use it to make the requested screen"""
    producer_inst = deserialize_yaml(Producer, producer)
    formatter_inst = deserialize_yaml(Formatter, formatter)
    device = producer_inst.produce_device()
    formatter_inst.format(device, producer_inst.prefix, output)


if __name__ == "__main__":
    cli()
