import os
import re
from typing import Any, Dict, List, Tuple
from pathlib import Path

from pydantic import BaseModel, Field, FilePath

from ._schema import Schema, ComponentUnion
from ._util import get_param_set


class SourceConverter(BaseModel):
    source_files: List[FilePath] = Field(
        ..., description="source files to convert to yaml"
    )
    module_root: Path = Field(..., description="Path to root of module")
    _text: str
    _create_param_strs: List[str]

    class Config:
        extra = "forbid"

    def __init__(self, **data: Any):
        super().__init__(**data)
        text = ""
        for source_file in self.source_files:
            with open(source_file, "r") as f:
                text += f.read()
        object.__setattr__(self, "_text", text)
        self._extract_create_param_strs()

    def _extract_parent_class(self) -> str:
        # e.g. extract 'asynNDArrayDriver' from
        # class epicsShareClass ADDriver : public asynNDArrayDriver {
        parent_class_extractor = re.compile(r"class.* (\w+) {")
        parent_class = re.search(parent_class_extractor, self._text).groups()[0]

        return parent_class

    def _extract_create_param_strs(self) -> List[str]:
        # e.g. extract: createParam(SimGainXString, asynParamFloat64, &SimGainX);
        create_param_extractor = re.compile(r"createParam\([^\)]*\);.*")
        create_param_strs = re.findall(create_param_extractor, self._text)
        object.__setattr__(self, "_create_param_strs", create_param_strs)

    def _filter_create_param_strs(self, parameters: List[str]) -> List[str]:
        return [s for s in self._create_param_strs if any(p in s for p in parameters)]

    def _extract_define_strs(self, str_names: List[str]) -> List[str]:
        # e.g. extract: #define SimGainXString                "SIM_GAIN_X";
        define_extractor = re.compile(r'\#define[_A-Za-z0-9 ]*"[^"]*".*')
        definitions = re.findall(define_extractor, self._text)
        # We only want to strip the definitions with corresponding createParam calls
        definitions = [
            definition
            for definition in definitions
            if any(str_name in definition for str_name in str_names)
        ]
        return definitions

    def _extract_index_declarations(self, index_names: List[str]) -> List[str]:
        # e.g. extract:     int SimGainX;
        declaration_extractor = re.compile(r" *int[^\n]*")
        declarations = re.findall(declaration_extractor, self._text)
        # We only want to strip the declarations with corresponding createParam calls
        declarations = [
            declaration
            for declaration in declarations
            if any(index_name in declaration for index_name in index_names)
        ]
        return declarations

    def _parse_create_param_str(self, create_param_str: str) -> Tuple[str, str]:
        # e.g. from: createParam(SimGainXString, asynParamFloat64, &SimGainX);
        # extract: SimGainXString,               asynParamFloat64, &SimGainX
        create_param_extractor = re.compile(r"(?:createParam\()([^\)]*)(?:\))")
        # There are two signatures for createParam. 3 argument and 4 argument
        # I think we are only ever interested in the final three arguments
        create_param_args = (
            re.findall(create_param_extractor, create_param_str)[0]
            .replace(" ", "")
            .split(",")[-3:]
        )
        string_index_pair = (create_param_args[0], create_param_args[2].strip("&"))
        return string_index_pair

    def _parse_definition_str(self, definition_str: str) -> Tuple[str, str]:
        # e.g. from: #define SimGainXString                "SIM_GAIN_X";
        # extract:
        # Group1: SimGainXString
        # Group2: SIM_GAIN_X
        define_extractor = re.compile(r'(?:\#define) ([A-Za-z0-9]*) *"([^"]*)')
        string_info_pair = re.findall(define_extractor, definition_str)[0]
        return string_info_pair

    def _get_string_index_mapping(self) -> Dict[str, str]:
        string_index_dict = dict(
            [
                self._parse_create_param_str(create_param_str)
                for create_param_str in self._create_param_strs
            ]
        )
        return string_index_dict

    def _get_string_info_mapping(self, strs: List[str]) -> Dict[str, str]:
        definitions = self._extract_define_strs(strs)
        string_info_dict = dict(
            [self._parse_definition_str(definition) for definition in definitions]
        )
        return string_info_dict

    def _map_index_to_info(
        self, string_info_dict: Dict[str, str], string_index_dict: Dict[str, str]
    ) -> Dict[str, str]:
        index_info_dict = dict()
        for string, index in string_index_dict.items():
            try:
                index_info_dict[index] = string_info_dict[string]
            except KeyError:
                raise KeyError(
                    f"String drvInfoString mapping not found for string: ",
                    f"index pair {string}:{index}",
                )
        return index_info_dict

    def get_index_info_mapping(self) -> Dict[str, str]:
        string_index_dict = self._get_string_index_mapping()
        string_info_dict = self._get_string_info_mapping(list(string_index_dict.keys()))
        index_info_dict = self._map_index_to_info(string_info_dict, string_index_dict)
        return index_info_dict

    def get_top_level_text(
        self, source_file: FilePath, device_name: str, parameters: List[str]
    ) -> str:
        with open(source_file, "r") as f:
            text = f.read()

        top_level_text = self._extract_top_level_text(text, parameters)

        parent = self._extract_parent_class()
        if source_file.suffix == ".cpp":
            top_level_text = self._add_param_set_cpp(
                top_level_text, device_name, parent
            )
        elif source_file.suffix == ".h":
            top_level_text = self._add_param_set_h(top_level_text, device_name, parent)

        return top_level_text

    def _add_param_set_cpp(
        self, top_level_text: str, device_class: str, parent_class: str
    ) -> str:
        # Add the constructor param set parameter
        top_level_text = top_level_text.replace(
            f"::{device_class}(", f"::{device_class}({device_class}ParamSet* paramSet, "
        )

        # Add the initialiser list base class param set parameter
        parent_param_set = get_param_set(parent_class)
        top_level_text = top_level_text.replace(
            f"{parent_class}(",
            f"{parent_class}(static_cast<{parent_param_set}*>(paramSet), ",
        )

        # Add the param set to the initialiser list
        top_level_text = re.sub(
            # Driver constructor and initialiser list, all whitespace between ) and {
            r"(::" + device_class + r"\([^{]+\))(\s*){",
            # Insert param set after last entry in initialiser list, in between match groups 1 and 2
            r"\1,\n    paramSet(paramSet)\2{",
            top_level_text,
        )

        return top_level_text

    def _add_param_set_h(
        self, top_level_text: str, device_class: str, parent_class: str
    ) -> str:
        # Add the constructor param set parameter
        top_level_text = top_level_text.replace(
            f" {device_class}(", f" {device_class}({device_class}ParamSet* paramSet, "
        )

        # Add the include
        idx = top_level_text.index(f'#include "{parent_class}.h"')
        top_level_text = (
            top_level_text[:idx]
            + f'#include "{device_class}ParamSet.h"\n'
            + top_level_text[idx:]
        )
        # Add the param set pointer member definition
        protected_extractor = re.compile(r".*protected:")
        protected_str = re.findall(protected_extractor, top_level_text)[0]
        param_set_definition = f"    {device_class}ParamSet* paramSet;"
        top_level_text = top_level_text.replace(
            protected_str, protected_str + "\n" + param_set_definition
        )

        return top_level_text

    def _extract_top_level_text(self, text: str, parameter_infos: List[str]) -> str:
        definition_strs = self._extract_define_strs(parameter_infos)
        string_index_dict = self._get_string_index_mapping()

        string_info_dict = self._get_string_info_mapping(list(string_index_dict.keys()))
        info_string_dict = dict(
            (string, info) for info, string in string_info_dict.items()
        )
        parameter_strings = [
            info_string_dict[parameter_info] for parameter_info in parameter_infos
        ]
        create_param_strs = self._filter_create_param_strs(parameter_strings)

        parameter_indexes = [string_index_dict[s] for s in parameter_strings]

        declaration_strs = self._extract_index_declarations(parameter_indexes)

        unwanted_strs = create_param_strs + definition_strs + declaration_strs

        top_level_lines = text.splitlines()
        top_level_lines = [
            line
            for line in top_level_lines
            if line.lstrip()
            not in [unwanted_str.lstrip() for unwanted_str in unwanted_strs]
        ]
        top_level_text = "\n".join(top_level_lines)

        info_index_map = dict(
            (info, string_index_dict[s]) for info, s in info_string_dict.items()
        )
        parameters = [info_index_map[info] for info in parameter_infos]
        parent_components = find_parent_components(
            self._extract_parent_class(), self.module_root,
        )
        parameters += [
            parameter.index_name
            for component in parent_components
            for parameter in component.children
        ]

        top_level_text = self._insert_param_set_accessors(top_level_text, parameters)

        return top_level_text

    def _insert_param_set_accessors(self, text: str, parameters: List[str]) -> str:
        for parameter in parameters:
            # Only match parameter name exactly, not others with same prefix
            text = re.sub(
                r"(\W)" + parameter + r"(\W)", r"\1paramSet->" + parameter + r"\2", text
            )
        return text


def find_parent_components(yaml_name: str, module_root: str) -> List[ComponentUnion]:
    if yaml_name == "asynPortDriver":
        return []  # asynPortDriver is the most base class and has no parameters

    # Look in this module first
    if f"{yaml_name}.pvi.yaml" in os.listdir(os.path.join(module_root, "pvi")):
        directory = os.path.join(module_root, "pvi")
    else:
        # TODO: Search configure/RELEASE paths
        raise IOError(f"Cannot find {yaml_name}.pvi.yaml")

    schema = Schema.load(Path(directory), Path(yaml_name))

    return schema.components + find_parent_components(schema.parent, module_root)
