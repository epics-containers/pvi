from argparse import ArgumentParser

from ._schema import Schema


def schema(args):
    print(Schema.schema_json(indent=args.indent))


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    # Add the schema options
    parser_schema = subparsers.add_parser(
        "schema", help="Show JSON schema for pvi YAML format"
    )
    parser_schema.set_defaults(func=schema)
    parser_schema.add_argument(
        "-i", "--indent", type=int, default=2, help="indent level for JSON"
    )
    # Parse args and return
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
