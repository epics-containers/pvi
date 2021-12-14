import json
from pathlib import Path
from typing import Optional, Type, TypeVar

import jsonschema
import typer
from apischema import deserialize, serialize
from apischema.json_schema import JsonSchemaVersion, deserialization_schema
from ruamel.yaml import YAML

from pvi import __version__
from pvi._format import Formatter
from pvi._produce import Producer
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
        serialized = serialize(device, exclude_none=True, exclude_defaults=True)
        # TODO: add modeline
        YAML().dump(serialized, output)
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

    template_converter = TemplateConverter(
        template_files=args.templates, formatter=dict(type=args.formatter)
    )

    # Generate initial yaml to provide parameter info strings to source converter
    converted_yaml = template_converter.convert()

    parameter_infos = [
        parameter["drv_info"]
        for component in converted_yaml["components"]
        for parameter in component["children"]
    ]
    source_converter = SourceConverter(
        cpp=args.cpp,
        h=args.header,
        module_root=args.root,
        parameter_infos=parameter_infos,
    )

    # Process and recreate template files - pass source device for param set include
    extracted_templates = template_converter.top_level_text(
        source_converter.device_class
    )
    for template_text, template_path in zip(extracted_templates, args.templates):
        with open(args.output_dir / f"{template_path.stem}.template", "w") as f:
            f.write(template_text)

    # Process and recreate source files
    extracted_source = source_converter.get_top_level_text()
    with open(args.output_dir / f"{args.cpp.stem}{args.cpp.suffix}", "w") as f:
        f.write(extracted_source.cpp)
    with open(args.output_dir / f"{args.header.stem}{args.header.suffix}", "w") as f:
        f.write(extracted_source.h)

    # Update yaml based on source file definitions and write
    converted_yaml = insert_entry(
        converted_yaml, "parent", source_converter.parent_class, "components"
    )
    converted_yaml = merge_in_index_names(
        converted_yaml, source_converter._get_index_info_map()
    )

    Schema.write(converted_yaml, args.output_dir, source_converter.device_class)


if __name__ == "__main__":
    app()
