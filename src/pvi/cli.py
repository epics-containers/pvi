from argparse import ArgumentParser
from pathlib import Path

from ._schema import Schema
from ._source_convert import SourceConverter
from ._template_convert import TemplateConverter, merge_in_index_names
from ._types import Formatter
from ._util import insert_entry

SUFFIXES = ["." + x[7:] for x in Formatter.__dict__ if x.startswith("format_")]


def convert(args):
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


def schema(args):
    with open(args.json, "w") as f:
        f.write(Schema.schema_json(indent=args.indent))


def generate(args):
    suffix = args.out.suffix
    assert suffix in SUFFIXES, f"File suffix '{suffix}' is not one of {SUFFIXES}"
    name = args.yaml.name
    assert name.endswith(".pvi.yaml"), "Expected '{name}' to end with '.pvi.yaml'"
    basename = name[:-9]
    schema = Schema.load(args.yaml.parent, basename)
    if suffix == ".template":
        tree = schema.producer.produce_records(schema.components)
    elif suffix in (".cpp", ".h"):
        tree = schema.producer.produce_asyn_parameters(schema.components)
    else:
        tree = schema.producer.produce_channels(schema.components)
    format = getattr(schema.formatter, f"format_{suffix[1:]}")
    text = format(tree, basename, schema)
    with open(args.out, "w") as f:
        f.write(text)


def main(args=None):
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    # Add a command for interatcting with the schema
    sub = subparsers.add_parser(
        "schema", help="Output JSON schema for pvi YAML format to file"
    )
    sub.add_argument("json", type=Path, help="path to the JSON output file")
    sub.set_defaults(func=schema)
    sub.add_argument(
        "-i", "--indent", type=int, default=2, help="indent level for JSON"
    )
    # Add a command for translating a database template and source code to YAML
    sub = subparsers.add_parser(
        "convert", help="Generate a yaml file from a template file"
    )
    sub.set_defaults(func=convert)
    sub.add_argument(
        "templates", type=Path, nargs="+", help="path to the template source file"
    )
    sub.add_argument(
        "--cpp", type=Path, help="Path .cpp file",
    )
    sub.add_argument(
        "--header", type=Path, help="Path .h file",
    )
    sub.add_argument(
        "output_dir", type=Path, help="Directory for output files",
    )
    sub.add_argument(
        "-r", "--root", type=Path, help="Full path to root of module", required=True
    )
    sub.add_argument(
        "-f", "--formatter", type=str, default="DLSFormatter", help="Formatter"
    )
    # Add a command for generating products
    sub = subparsers.add_parser("generate", help="Generate one of the products")
    sub.set_defaults(func=generate)
    sub.add_argument("yaml", type=Path, help="path to the YAML source file")
    sub.add_argument(
        "out",
        type=Path,
        help=f"path to the output file to produce with suffix in {SUFFIXES}",
    )
    # Parse args and return
    args = parser.parse_args(args)
    args.func(args)
