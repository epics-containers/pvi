import json
import os
from pathlib import Path
from typing import List, Optional, Type

import typer

from pvi import __version__
from pvi._convert._template_convert import TemplateConverter
from pvi._convert.utils import extract_device_and_parent_class
from pvi._format import Formatter
from pvi._pv_group import group_parameters
from pvi._schema_utils import make_json_schema
from pvi._yaml_utils import deserialize_yaml, serialize_yaml
from pvi.device import Device

app = typer.Typer()
convert_app = typer.Typer()
app.add_typer(convert_app, name="convert", help="Convert a module to use PVI")


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
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


@app.command()
def schema(output: Path = typer.Argument(..., help="filename to write the schema to")):
    """Write the JSON schema for the pvi interface"""
    cls: Type
    assert output.name.endswith(
        ".schema.json"
    ), f"Expected '{output.name}' to end with '.schema.json'"
    if output.name == "pvi.device.schema.json":
        cls = Device
    elif output.name == "pvi.formatter.schema.json":
        cls = Formatter
    else:
        typer.echo(f"Don't know how to create {output.name}")
        raise typer.Exit(code=1)
    schema = make_json_schema(cls)
    output.write_text(json.dumps(schema, indent=2))


@app.command()
def format(
    output_path: Path = typer.Argument(
        ..., help="Directory to write output file(s) to"
    ),
    device_path: Path = typer.Argument(..., help="Path to the .pvi.device.yaml file"),
    formatter_path: Path = typer.Argument(
        ..., help="Path to the .pvi.formatter.yaml file"
    ),
    yaml_paths: List[Path] = typer.Option(
        [], "--yaml-path", help="Paths to directories with .pvi.device.yaml files"
    ),
):
    """Create screen product from device and formatter YAML"""
    device = Device.deserialize(device_path)
    device.deserialize_parents(yaml_paths)

    formatter_inst: Formatter = deserialize_yaml(Formatter, formatter_path)
    formatter_inst.format(device, "$(P)$(R)", output_path)


@convert_app.command()
def device(
    output: Path = typer.Argument(..., help="Directory to write output file to"),
    h: Path = typer.Argument(..., help="Path to the .h file to convert"),
    templates: List[Path] = typer.Option(
        [], "--template", help="Paths to .template files to convert"
    ),
):
    """Convert template to device YAML"""
    if not output.exists():
        os.mkdir(output)

    name, parent = extract_device_and_parent_class(h.read_text())
    component_group = TemplateConverter(templates).convert()
    device = Device(name, parent, component_group)

    serialize_yaml(device, output / f"{name}.pvi.device.yaml")


@app.command()
def regroup(
    device_path: Path = typer.Argument(
        ..., help="Path to the device.yaml file to regroup"
    ),
    ui_paths: List[Path] = typer.Argument(
        ..., help="Paths to the ui files to regroup the PVs by"
    ),
):
    """Regroup a device.yaml file based on ui files that the PVs appear in"""
    device = Device.deserialize(device_path)
    device.children = group_parameters(device, ui_paths)

    serialize_yaml(device, device_path)


# test with: pipenv run python -m pvi
if __name__ == "__main__":
    app()
