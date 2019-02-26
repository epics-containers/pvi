import importlib
from collections import namedtuple
from annotypes import Any, TYPE_CHECKING, Array
from ruamel import yaml

from pvi.intermediate import Intermediate

if TYPE_CHECKING:
    from typing import List, Callable, Dict, NamedTuple

ComponentData = namedtuple('ComponentData',
                           'component_type yaml_path lineno component_params')


# Taken from malcolm
# file: yamlutil.py
# class.method: Section.instantiate
def lookup_component(component_type, filename, lineno):
    # type: (str, str, int) -> Callable[..., List[Any]]

    pkg, ident = component_type.rsplit(".", 1)
    # TODO: the hardcoded "pvi.modules." string below will eventually be a
    #  variable and supplied by a Producer instance
    pkg = "pvi.modules.%s" % pkg

    try:
        ob = importlib.import_module(pkg)
    except ImportError as e:
        print("\n%s: %d: \n%s" % (filename, lineno, e))

    try:
        ob = getattr(ob, ident)
    except AttributeError:
        print("\n%s:%d:\nPackage %s has no ident %s" %
              (filename, lineno, pkg, ident))

    return ob


def get_component_yaml_info(yaml_path):
    # type: (str) -> List[NamedTuple[str, str, int, Dict]]
    with open(yaml_path) as f:
        text = f.read()

    code = yaml.load(text, Loader=yaml.RoundTripLoader)
    components_section = code["components"]
    all_components_data = []

    for component_params in components_section:
        pos_info = component_params.lc.key("type")
        lineno = pos_info[0]
        component_type = component_params.pop("type")
        all_components_data.append(ComponentData(component_type, yaml_path,
                                                 lineno, component_params))

    return all_components_data


def get_intermediate_objects(data):
    # type: (List[NamedTuple[str, str, int, Dict]]) -> Array[Intermediate]
    intermediate_objects = []

    for component_type, yaml_path, lineno, component_params in data:
        component = lookup_component(component_type, yaml_path, lineno)
        intermediate_objects += component(**component_params).seq

    return Array[Intermediate](intermediate_objects)
