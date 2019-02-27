import importlib
import inspect
from collections import namedtuple
from annotypes import Any, TYPE_CHECKING, Array, NO_DEFAULT
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
        try:
            validated_params = validate(component, component_params)
            intermediates = component(**validated_params)
        except Exception as e:
            sourcefile = inspect.getsourcefile(component)
            sourcefile_lineno = inspect.getsourcelines(component)[1]
            print("\n%s:%d:\n%s:%d:\n%s" % (
                yaml_path, lineno, sourcefile, sourcefile_lineno, e))
        else:
            intermediate_objects += intermediates.seq

    return Array[Intermediate](intermediate_objects)


def validate(component, params):
    # type: (Callable[..., Array[Intermediate]], Dict) -> Dict
    validated_params = dict()
    required_params = [param for param in component.call_types
                       if component.call_types[param].default == NO_DEFAULT]

    for name, anno_obj in component.call_types.items():
        if name in params:
            param_val = params[name]
            if anno_obj.typ == str:
                param_val = str(param_val)  # TODO change for python 3
            elif anno_obj.typ in (int, float):
                param_val = anno_obj.typ(param_val)
            validated_params[name] = param_val

    missing_params = set(required_params) - set(validated_params)
    assert not missing_params, \
        "Requires parameters %s but only given %s" % (
            list(required_params), list(validated_params))

    return validated_params
