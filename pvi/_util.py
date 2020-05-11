import re
from enum import Enum

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
