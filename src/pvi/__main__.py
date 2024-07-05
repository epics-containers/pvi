import json
import os
from pathlib import Path
from typing import Annotated, Optional

import typer

from pvi import __version__
from pvi._convert._template_convert import TemplateConverter
from pvi._convert.utils import extract_device_and_parent_class
from pvi._format import Formatter
from pvi._format.template import format_template
from pvi._pv_group import group_by_ui
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
    # TODO: typer does not support `<type> | None` yet
    # https://github.com/tiangolo/typer/issues/533
    version: Optional[bool] = typer.Option(  # noqa
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Print the version and exit",
    ),
):
    """PVI builder interface"""


@app.command()
def schema(
    output: Annotated[
        Path, typer.Argument(..., help="filename to write the schema to")
    ],
):
    """Write the JSON schema for the pvi interface"""
    assert output.name.endswith(
        ".schema.json"
    ), f"Expected '{output.name}' to end with '.schema.json'"

    if output.name == "pvi.device.schema.json":
        schema = Device.model_json_schema()
    elif output.name == "pvi.formatter.schema.json":
        schema = Formatter.create_schema()
    else:
        typer.echo(f"Don't know how to create {output.name}")
        raise typer.Exit(code=1)

    output.write_text(json.dumps(schema, indent=2))


@app.command()
def format(
    output_path: Annotated[
        Path, typer.Argument(..., help="Directory to write output file(s) to")
    ],
    device_path: Annotated[
        Path, typer.Argument(..., help="Path to the .pvi.device.yaml file")
    ],
    formatter_path: Annotated[
        Path, typer.Argument(..., help="Path to the .pvi.formatter.yaml file")
    ],
    yaml_paths: Annotated[
        Optional[list[Path]],  # noqa
        typer.Option(
            ..., "--yaml-path", help="Paths to directories with .pvi.device.yaml files"
        ),
    ] = None,
):
    """Create screen product from device and formatter YAML"""
    yaml_paths = yaml_paths or []

    device = Device.deserialize(device_path)
    device.deserialize_parents(yaml_paths)

    formatter = Formatter.deserialize(formatter_path)
    formatter.format(device, output_path)


@app.command()
def generate_template(
    device_path: Annotated[
        Path, typer.Argument(..., help="Path to the .pvi.device.yaml file")
    ],
    pv_prefix: Annotated[str, typer.Argument(..., help="Prefix of PVI PV")],
    output_path: Annotated[Path, typer.Argument(..., help="Output file to generate")],
):
    """Create template with info tags for device signals"""
    device = Device.deserialize(device_path)
    format_template(device, pv_prefix, output_path)


@convert_app.command()
def device(
    output: Annotated[
        Path, typer.Argument(..., help="Directory to write output file to")
    ],
    h: Annotated[Path, typer.Argument(..., help="Path to the .h file to convert")],
    templates: Annotated[
        Optional[list[Path]],  # noqa
        typer.Option(..., "--template", help="Paths to .template files to convert"),
    ] = None,
):
    """Convert template to device YAML"""
    templates = templates or []

    if not output.exists():
        os.mkdir(output)

    name, parent = extract_device_and_parent_class(h.read_text())
    component_group = TemplateConverter(templates).convert()
    device = Device(label=name, parent=parent, children=component_group)

    device.serialize(output / f"{name}.pvi.device.yaml")


@app.command()
def regroup(
    device_path: Annotated[
        Path, typer.Argument(..., help="Path to the device.yaml file to regroup")
    ],
    ui_paths: Annotated[
        list[Path],
        typer.Argument(..., help="Paths to the ui files to regroup the PVs by"),
    ],
):
    """Regroup a device.yaml file based on ui files that the PVs appear in"""
    device = Device.deserialize(device_path)
    device.children = group_by_ui(device, ui_paths)

    device.serialize(device_path)


# test with: pipenv run python -m pvi
if __name__ == "__main__":
    app()
