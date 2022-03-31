import json
import os
from pathlib import Path
from typing import Dict, List, NewType, Optional, Type, cast

import typer

from pvi import __version__
from pvi._convert._source_convert import SourceConverter
from pvi._convert._template_convert import TemplateConverter
from pvi._format import Formatter
from pvi._produce import Producer
from pvi._produce.asyn import AsynParameter, AsynProducer
from pvi._pv_group import pv_group
from pvi._schema_utils import make_json_schema
from pvi._yaml_utils import deserialize_yaml, serialize_yaml
from pvi.device import Device, Grid, Group, Tree, walk

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
):
    """Create template/csv/device/other product from producer YAML"""
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
    module_root: Path = typer.Argument(..., help="Root directory of support module"),
    cpp: Path = typer.Argument(..., help="Path to the .cpp file to convert"),
    h: Path = typer.Argument(..., help="Path to the .h file to convert"),
    templates: Optional[List[Path]] = typer.Argument(
        None,
        help="Paths to .template files to convert",
    ),
):
    """Convert cpp/h/template to producer YAML and stripped cpp/h/template"""
    output = module_root / "pvi"
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

    source_converter = SourceConverter(cpp, h, module_root, drv_infos)

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
    module_root: Path = typer.Argument(..., help="Root directory of support module"),
    cpp: Path = typer.Argument(..., help="Path to the .cpp file to convert"),
    h: Path = typer.Argument(..., help="Path to the .h file to convert"),
):
    """Alter cpp and h files of unconverted drivers"""

    output = module_root / "pvi" / "placeholders"
    if not output.exists():
        os.mkdir(output)

    drv_infos: List[str] = []
    source_converter = SourceConverter(cpp, h, module_root, drv_infos)
    extracted_source = source_converter.get_top_level_placeholder()

    (output / cpp.name).write_text(extracted_source.cpp)
    (output / h.name).write_text(extracted_source.h)


ScreenName = NewType("ScreenName", str)
GroupName = NewType("GroupName", str)
PVName = NewType("PVName", str)


def create_screen(
    screen_name: ScreenName,
    group_pv_map: Dict[GroupName, List[PVName]],
    records: Tree[AsynParameter],
) -> Group[Group[AsynParameter]]:
    return Group(
        screen_name,
        Grid(labelled=True),
        [
            create_group(group_name, pv_names, records)
            for group_name, pv_names in group_pv_map.items()
        ],
    )


def create_group(
    group_name: GroupName, pv_names: List[PVName], records: Tree[AsynParameter]
) -> Group[AsynParameter]:
    return Group(
        group_name,
        Grid(labelled=True),
        [record for record in records if record.name in set(pv_names)],
    )


@app.command()
def regroup(
    module_root: Path = typer.Argument(..., help="Root directory of support module"),
    producer_path: Path = typer.Argument(
        ..., help="Path to the producer.yaml file to regroup"
    ),
    screen_paths: List[Path] = typer.Argument(
        None, help="Path to the screen to regroup the pv's by"
    ),
):
    """
    Regroup a drivers producer.yaml file on pv groupings from one/many edl screens.
    """

    output = module_root.joinpath("pvi/grouped_producers")
    if not output.exists():
        os.mkdir(output)

    producer = deserialize_yaml(AsynProducer, producer_path)
    screen_pv_map: Dict[ScreenName, Dict[GroupName, List[PVName]]] = {
        ScreenName(screen.stem): pv_group(screen) for screen in screen_paths
    }

    component_group_one = producer.parameters[0]
    assert isinstance(component_group_one, Group)
    component_group_one_pvs = component_group_one.children

    grouped_pvs: List[Group[Group[AsynParameter]]] = [
        create_screen(screen_name, group_pv_map, component_group_one_pvs)
        for screen_name, group_pv_map in screen_pv_map.items()
    ]

    flat_grouped_pvs: List[AsynParameter] = [
        cast(AsynParameter, pv)
        for screen_pvs in grouped_pvs
        for group_pvs in screen_pvs.children
        for pv in group_pvs.children
    ]

    # delete them out of the unsorted group
    unthingmied_pvs = Group(
        component_group_one.name,
        component_group_one.layout,
        [pv for pv in component_group_one_pvs if pv not in flat_grouped_pvs],
    )

    new_pvs: Tree[Group[AsynParameter]] = [
        unthingmied_pvs,
        *grouped_pvs,
    ]

    producer.parameters = new_pvs  # type: ignore

    # create new producer file
    serialize_yaml(producer, output.joinpath(f"{producer_path.stem}.yaml"))


# test with: pipenv run python -m pvi
if __name__ == "__main__":
    app()
