from argparse import ArgumentParser
from pathlib import Path

from ._schema import Schema
from ._source_convert import SourceConverter
from ._template_convert import TemplateConverter, merge_in_index_names
from ._types import Formatter

SUFFIXES = ["." + x[7:] for x in Formatter.__dict__ if x.startswith("format_")]


def convert(args):
    source_converter = SourceConverter(source_files=args.source_files)
    index_info_mapping = source_converter.get_index_info_mapping()

    for source_file in args.source_files:
        top_level_text = source_converter.get_top_level_text(source_file)
        with open(
            args.output_dir / f"{source_file.stem}_top{source_file.suffix}", "w"
        ) as f:
            f.write(top_level_text)

    template_converter = TemplateConverter(
        template_file=args.template, formatter=dict(type=args.formatter)
    )
    converted_yaml = template_converter.convert()

    # merge in index names
    converted_yaml = merge_in_index_names(converted_yaml, index_info_mapping)
    Schema.write(converted_yaml, args.output_dir, args.template.stem)
    top_level_text = template_converter.top_level_text()
    with open(args.output_dir / f"{args.template.stem}_top.template", "w") as f:
        f.write(top_level_text)


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
    text = format(tree, basename, schema.macros)
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
    # Add a command for translating a database templates and source code to YAML
    sub = subparsers.add_parser(
        "convert", help="Generate a yaml file from a template file"
    )
    sub.set_defaults(func=convert)
    sub.add_argument("template", type=Path, help="path to the template source file")
    sub.add_argument(
        "-s",
        "--source_files",
        type=Path,
        help="paths to the .cpp and .h source files",
        nargs="*",
    )
    sub.add_argument(
        "output_dir", type=Path, help=f"directory for output files",
    )
    sub.add_argument(
        "-f", "--formatter", type=str, default="DLSFormatter", help="Formatter"
    )
    # Add a command for generating produces
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
