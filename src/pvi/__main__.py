import json
import os
from pathlib import Path
from typing import List, Optional, Type

import typer

from pvi import __version__
from pvi._convert._source_convert import SourceConverter
from pvi._convert._template_convert import TemplateConverter
from pvi._format import Formatter
from pvi._produce import Producer
from pvi._produce.asyn import AsynParameter, AsynProducer
from pvi._pv_group import group_parameters
from pvi._schema_utils import make_json_schema
from pvi._yaml_utils import deserialize_yaml, serialize_yaml
from pvi.device import Device, walk

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
    schema = make_json_schema(cls)
    output.write_text(json.dumps(schema, indent=2))


@app.command()
def produce(
    output: Path = typer.Argument(..., help="filename to write the product to"),
    producer: Path = typer.Argument(..., help="path to the producer .pvi.yaml file"),
    yaml_paths: Optional[List[Path]] = typer.Option(
        None, help="Paths to directories with .pvi.producer.yaml files"
    ),
):
    """Create template/csv/device/other product from producer YAML"""
    if yaml_paths is None:
        yaml_paths = []

    producer_inst = deserialize_yaml(Producer, producer)
    if output.suffix == ".template":
        producer_inst.produce_records(output)
    elif output.suffix == ".csv":
        producer_inst.produce_csv(output)
    elif output.suffixes == [".pvi", ".device", ".yaml"]:
        device = producer_inst.produce_device()
        serialize_yaml(device, output)
    else:
        producer_inst.produce_other(output, yaml_paths)


@app.command()
def format(
    output: Path = typer.Argument(..., help="Directory to write output file(s) to"),
    producer: Path = typer.Argument(..., help="path to the .pvi.producer.yaml file"),
    formatter: Path = typer.Argument(..., help="path to the .pvi.formatter.yaml file"),
    yaml_paths: Optional[List[Path]] = typer.Option(
        None, help="Paths to directories with .pvi.producer.yaml files"
    ),
):
    """Create screen product from producer and formatter YAML"""
    if yaml_paths is None:
        yaml_paths = []

    producer_inst: Producer = deserialize_yaml(Producer, producer)
    producer_inst.deserialize_parents(yaml_paths)
    device = producer_inst.produce_device()

    formatter_inst: Formatter = deserialize_yaml(Formatter, formatter)
    formatter_inst.format(device, producer_inst.prefix, output)


@convert_app.command()
def asyn(
    output: Path = typer.Argument(..., help="Directory to write output file(s) to"),
    cpp: Path = typer.Argument(..., help="Path to the .cpp file to convert"),
    h: Path = typer.Argument(..., help="Path to the .h file to convert"),
    templates: Optional[List[Path]] = typer.Argument(
        None, help="Paths to .template files to convert"
    ),
    yaml_paths: Optional[List[Path]] = typer.Option(
        None, help="Paths to directories with .pvi.producer.yaml files"
    ),
):
    """Convert cpp/h/template to producer YAML and stripped cpp/h/template"""
    if yaml_paths is None:
        yaml_paths = []

    if not output.exists():
        os.mkdir(output)

    drv_infos = []
    producer = AsynProducer(
        prefix="$(P)$(R)",
        label=h.stem,
        asyn_port="$(PORT)",
        address="$(ADDR=0)",
        timeout="$(TIMEOUT=1)",
        parent="asynPortDriver",
        parameters=[],
    )

    # if a template is given, convert it and populate drv_infos
    if templates:
        template_converter = TemplateConverter(templates)

        # Generate initial yaml to provide parameter info strings to source converter
        producer = template_converter.convert()
        drv_infos = [
            parameter.get_drv_info()
            for parameter in walk(producer.parameters)
            if isinstance(parameter, AsynParameter)
        ]

    source_converter = SourceConverter(cpp, h, yaml_paths, drv_infos)

    if templates:
        # Process and recreate template files - pass source device for param set include
        extracted_templates = template_converter.top_level_text(
            source_converter.device_class
        )
        for template_text, template_path in zip(extracted_templates, templates):
            (output / template_path.name).write_text(template_text)

    # Process and recreate source files
    extracted_source = source_converter.get_top_level_text()
    (output / cpp.name).write_text(extracted_source.cpp)
    (output / h.name).write_text(extracted_source.h)

    # Update yaml based on source file definitions and write
    producer.parent = source_converter.parent_class
    if source_converter.define_strings:
        index_map = source_converter.get_info_index_map()
        for parameter in walk(producer.parameters):
            if isinstance(parameter, AsynParameter):
                parameter.index_name = index_map.get(
                    parameter.get_drv_info(), "INPUT MANUALLY"
                )

    serialize_yaml(
        producer, output / f"{source_converter.device_class}.pvi.producer.yaml"
    )


@app.command()
def convertplaceholder(
    output: Path = typer.Argument(..., help="Directory to write output file(s) to"),
    cpp: Path = typer.Argument(..., help="Path to the .cpp file to convert"),
    h: Path = typer.Argument(..., help="Path to the .h file to convert"),
    yaml_paths: Optional[List[Path]] = typer.Option(
        None, help="Paths to directories with .pvi.producer.yaml files"
    ),
):
    """Alter cpp and h files of unconverted drivers"""
    if yaml_paths is None:
        yaml_paths = []

    if not output.exists():
        os.mkdir(output)

    drv_infos: List[str] = []
    source_converter = SourceConverter(cpp, h, yaml_paths, drv_infos)
    extracted_source = source_converter.get_top_level_placeholder()

    (output / cpp.name).write_text(extracted_source.cpp)
    (output / h.name).write_text(extracted_source.h)


@app.command()
def regroup(
    output: Path = typer.Argument(..., help="Directory to write output file(s) to"),
    producer_path: Path = typer.Argument(
        ..., help="Path to the producer.yaml file to regroup"
    ),
    ui_paths: List[Path] = typer.Argument(
        ..., help="Paths to the ui files to regroup the PVs by"
    ),
):
    """Regroup a producer.yaml file based on ui files that the PVs appear in"""
    producer = deserialize_yaml(AsynProducer, producer_path)
    producer.parameters = group_parameters(producer, ui_paths)

    # Create new yaml
    if not output.exists():
        os.mkdir(output)
    serialize_yaml(producer, output.joinpath(f"{producer_path.stem}.yaml"))


# test with: pipenv run python -m pvi
if __name__ == "__main__":
    app()
