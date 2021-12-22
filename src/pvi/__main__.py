import json
from pathlib import Path
from typing import Optional, Type

import typer
from apischema.json_schema import JsonSchemaVersion, deserialization_schema

from pvi import __version__
from pvi._convert._source_convert import SourceConverter
from pvi._convert._template_convert import TemplateConverter
from pvi._format import Formatter
from pvi._produce import Producer
from pvi._produce.asyn import AsynParameter
from pvi._yaml_utils import deserialize_yaml, serialize_yaml
from pvi.device import Device, walk

from . import __version__

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


@app.command()
def produce(
    output: Path = typer.Argument(..., help="filename to write the product to"),
    producer: Path = typer.Argument(..., help="path to the producer .pvi.yaml file"),
):
    """Create template/csv/device product from producer YAML"""
    producer_inst = deserialize_yaml(Producer, producer)
    if output.suffix == ".template":
        producer_inst.produce_records(output)
    elif output.suffix == ".csv":
        producer_inst.produce_csv(output)
    elif output.suffixes == [".pvi", ".device", ".yaml"]:
        device = producer_inst.produce_device()
        serialize_yaml(device, output)
    else:
        producer_inst.produce_other(output)


@app.command()
def format(
    output: Path = typer.Argument(..., help="filename to write the product to"),
    producer: Path = typer.Argument(..., help="path to the .pvi.producer.yaml file"),
    formatter: Path = typer.Argument(..., help="path to the .pvi.formatter.yaml file"),
):
    """Create screen product from producer and formatter YAML"""
    producer_inst = deserialize_yaml(Producer, producer)
    formatter_inst = deserialize_yaml(Formatter, formatter)
    device = producer_inst.produce_device()
    formatter_inst.format(device, producer_inst.prefix, output)


@convert_app.command()
def asyn(
    output: Path = typer.Argument(..., help="directory to put the output files in"),
    template: Path = typer.Argument(..., help="path to the .template file to convert"),
    cpp: Path = typer.Argument(..., help="path to the .cpp file to convert"),
    h: Path = typer.Argument(..., help="path to the .h file to convert"),
):
    """Convert template/cpp/h to producer YAML and stripped template/cpp/h"""

    template_converter = TemplateConverter(template)

    # Generate initial yaml to provide parameter info strings to source converter
    producer = template_converter.convert()

    drv_infos = [
        parameter.get_drv_info()
        for parameter in walk(producer.parameters)
        if isinstance(parameter, AsynParameter)
    ]
    source_converter = SourceConverter(cpp, h, output, drv_infos)

    # Process and recreate template files - pass source device for param set include
    extracted_templates = template_converter.top_level_text(
        source_converter.device_class
    )
    for template_text, template_path in zip(extracted_templates, [template]):
        (output / template_path.name).write_text(template_text)

    # Process and recreate source files
    extracted_source = source_converter.get_top_level_text()
    (output / cpp.name).write_text(extracted_source.cpp)
    (output / h.name).write_text(extracted_source.h)

    # Update yaml based on source file definitions and write
    producer.parent = source_converter.parent_class
    index_map = source_converter.get_info_index_map()
    for parameter in walk(producer.parameters):
        if isinstance(parameter, AsynParameter):
            parameter.index_name = index_map[parameter.get_drv_info()]
    serialize_yaml(
        producer, output / f"{source_converter.device_class}.pvi.producer.yaml"
    )


# test with: pipenv run python -m pvi
if __name__ == "__main__":
    app()
