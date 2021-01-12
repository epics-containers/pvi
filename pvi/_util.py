import re
from enum import Enum
from glob import glob
from pathlib import Path
from typing import Any, List

from ruamel.yaml.scalarstring import preserve_literal


def truncate_description(desc: str) -> str:
    """Take the first line of a multiline description, truncated to 40 chars"""
    first_line = desc.strip().split("\n")[0]
    return first_line[:40]


def camel_to_title(name):
    """Takes a CamelCaseFieldName and returns an Title Case Field Name
    Args:
        name (str): E.g. CamelCaseFieldName
    Returns:
        str: Title Case converted name. E.g. Camel Case Field Name
    """
    split = re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z0-9]|$)", name)
    ret = " ".join(split)
    ret = ret[0].upper() + ret[1:]
    return ret


def prepare_for_yaml(child):
    if isinstance(child, dict):
        return {k: prepare_for_yaml(v) for k, v in child.items()}
    elif isinstance(child, list):
        return [prepare_for_yaml(v) for v in child]
    elif isinstance(child, Enum):
        return child.value
    elif isinstance(child, str) and "\n" in child:
        return preserve_literal(child)
    else:
        return child


def insert_entry(yaml: dict, insert_key: str, insert_value: Any, position_key: str):
    # Recreate given yaml with new key inserted just before position_key
    updated_yaml = {}
    for key, value in yaml.items():
        if key == position_key:
            updated_yaml[insert_key] = insert_value
        updated_yaml[key] = value

    return updated_yaml


def get_param_set(driver: str):
    return "asynParamSet" if driver == "asynPortDriver" else driver + "ParamSet"


def find_parent_modules(module_root: Path) -> List[Path]:

    configure = module_root / "configure"
    release_paths = glob(str(configure / "RELEASE*"))

    macros = {}
    # e.g. extract (ADCORE, /path/to/ADCore) from ADCORE = /path/to/ADCore
    module_definition_extractor = re.compile(r"^(\w+)\s*=\s*(\S+)", re.MULTILINE)
    for release_path in release_paths:
        with open(release_path) as release_file:
            match = re.findall(module_definition_extractor, release_file.read())
            macros.update(dict(match))

    macro_re = re.compile(r"\$\(([^\)]+)\)")
    for macro in macros:
        for nested_macro in macro_re.findall(macros[macro]):
            if nested_macro in macros.keys():
                macros[macro] = macros[macro].replace(
                    "$({})".format(nested_macro), macros[nested_macro]
                )

    modules = [Path(module) for module in macros.values()]

    return modules
