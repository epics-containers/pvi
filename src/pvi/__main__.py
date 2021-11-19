import json
from enum import Enum
from pathlib import Path
from typing import Optional, Type

import jsonschema
import typer
from apischema import deserialize
from apischema.json_schema import deserialization_schema
from ruamel.yaml import YAML

from pvi import __version__
from pvi.types import Component, Producer, Tree

from . import _asyn  # noqa

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


class SchemaType(str, Enum):
    pvi = "pvi"
    producer = "producer"


@cli.command()
def schema(
    type: SchemaType = typer.Argument(..., help="sort of schema to write"),
    output: Path = typer.Argument(..., help="filename to write the schema to"),
):
    """Write the JSON schema for the pvi interface or producer interface"""
    cls: Type
    if type is SchemaType.pvi:
        cls = Tree[Component]
    elif type is SchemaType.producer:
        cls = Producer
    else:
        raise ValueError(type)
    schema = json.dumps(deserialization_schema(cls, all_refs=True), indent=2)
    output.write_text(schema)


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
    # schema = deserialization_schema(Producer, all_refs=True)
    schema = json.loads(open("producer.schema.json").read())
    jsonschema.validate(producer_dict, schema)
    # basename = name[:-9]
    producer = deserialize(Producer, producer_dict)
    if output.suffix == ".template":
        producer.produce_records(output)
    else:
        producer.produce_other(output)


if __name__ == "__main__":
    cli()
