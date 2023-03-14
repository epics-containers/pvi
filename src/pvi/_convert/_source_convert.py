import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from pvi._convert.utils import (
    extract_create_param_strs,
    extract_define_strs,
    extract_device_and_parent_class,
    extract_index_declarations,
    insert_param_set_accessors,
    parse_create_param_str,
    parse_definition_str,
)
from pvi._produce.asyn import AsynParameter, find_components
from pvi.device import walk


@dataclass
class Source:
    cpp: str
    h: str


class SourceConverter:
    def __init__(
        self, cpp: Path, h: Path, yaml_paths: List[Path], drv_infos: List[str]
    ):
        self.source = Source(cpp.read_text(), h.read_text())
        self.yaml_paths = yaml_paths
        self.parameter_infos = drv_infos

        if cpp.name.startswith("asynNDArrayDriver"):
            # Special case to include NDArrayData to be removed from source files
            # There is also a special case to add it to the paramSet without it
            # appearing in the producer.yaml
            self.parameter_infos.append("ARRAY_DATA")

        self.device_class, self.parent_class = extract_device_and_parent_class(
            self.source.h
        )
        self.define_strings = extract_define_strs(self.source.h, self.parameter_infos)
        self.string_info_map = self._get_string_info_map(self.define_strings)
        self.create_param_strings = extract_create_param_strs(
            self.source.cpp, list(self.string_info_map)
        )
        self.string_index_map = self._get_string_index_map(self.create_param_strings)
        self.declaration_strings = extract_index_declarations(
            self.source.h, list(self.string_index_map.values())
        )

    def _get_string_info_map(self, define_strings: List[str]) -> Dict[str, str]:
        string_info_map = dict(
            parse_definition_str(definition) for definition in define_strings
        )
        return string_info_map

    def _get_string_index_map(self, create_param_strings: List[str]) -> Dict[str, str]:
        string_index_dict = dict(
            [
                parse_create_param_str(create_param_str)
                for create_param_str in create_param_strings
            ]
        )
        return string_index_dict

    def get_info_index_map(self) -> Dict[str, str]:
        index_string_map = dict(
            (index, string) for string, index in self.string_index_map.items()
        )
        info_index_map = dict(
            (self.string_info_map[string], index)
            for index, string in index_string_map.items()
        )
        return info_index_map

    def get_top_level_text(self) -> Source:
        extracted_cpp = self._convert_cpp(self.source.cpp)
        extracted_h = self._convert_h(self.source.h)

        return Source(extracted_cpp, extracted_h)

    def get_top_level_placeholder(self) -> Source:
        extracted_cpp = self._convert_cpp_placeholder(self.source.cpp)
        extracted_h = self._convert_h_placeholder(self.source.h)

        return Source(extracted_cpp, extracted_h)

    def _convert_cpp(self, original_cpp_text: str) -> str:
        unwanted_strings = self.create_param_strings

        # Re-create text with unwanted lines ommited
        lines = original_cpp_text.splitlines()
        lines = [
            line
            for line in lines
            if line.lstrip()
            not in [unwanted_string.lstrip() for unwanted_string in unwanted_strings]
        ]
        cpp_text = "\n".join(lines)

        # Insert accessors for parameters that have been moved to the param set
        parameters = list(self.string_index_map.values())
        parent_components = find_components(self.parent_class, self.yaml_paths)
        parameters += [
            parameter.get_index_name()
            for parameter in walk(parent_components)
            if isinstance(parameter, AsynParameter)
        ]

        parameters.append("NDArrayData")  # Special case to update NDArrayData
        cpp_text = insert_param_set_accessors(cpp_text, parameters)

        # Add the param set parameter to the constructor declaration
        cpp_text = cpp_text.replace(
            f"::{self.device_class}(",
            f"::{self.device_class}({self.device_class}ParamSet* paramSet, ",
        )

        # Add the param set parameter to the constructor call in the extern "C" function
        driver = self.device_class

        # Create paramSet and insert it into constructor arguments
        # Group 1 is leading whitespace - used to indent added line
        # Group 2 is the rest of the line up to driver constructor opening bracket
        cpp_text = re.sub(
            r"^(\s*)(.*new " + driver + r"\()",
            r"\1"
            + f"{driver}ParamSet* paramSet = new {driver}ParamSet;\n"
            + r"\1\2paramSet, ",
            cpp_text,
            flags=re.MULTILINE,  # Make ^ match start of line
        )

        # Add the initialiser list base class param set parameter
        parent_param_set = get_param_set(self.parent_class)
        cpp_text = cpp_text.replace(
            f"{self.parent_class}(",
            f"{self.parent_class}(static_cast<{parent_param_set}*>(paramSet), ",
        )

        # Add the param set to the initialiser list
        cpp_text = re.sub(
            # Driver constructor and initialiser list, all whitespace between ) and {
            r"(::" + self.device_class + r"\([^{]+\))(\s*){",
            # Insert param set after last entry in initialiser list, in between
            # match groups 1 and 2
            r"\1,\n    paramSet(paramSet)\2{",
            cpp_text,
        )

        return cpp_text

    def _convert_cpp_placeholder(self, original_cpp_text: str) -> str:
        cpp_text = original_cpp_text
        parent_param_set = get_param_set(self.parent_class)
        cpp_text = cpp_text.replace(
            f"{self.parent_class}(",
            f"{self.parent_class}(static_cast<{parent_param_set}*>(this), ",
        )
        return cpp_text

    def _convert_h(self, original_h: str) -> str:
        unwanted_strings = [
            string.strip() for string in self.define_strings + self.declaration_strings
        ]

        # Remove FIRST_*_PARAM define
        first_param_extractor = re.compile(r"")
        match = re.search(first_param_extractor, original_h)
        assert match, "Can't find first param"
        unwanted_strings += match.group()

        # Re-create text with unwanted lines ommited
        lines = original_h.splitlines()
        lines = [line for line in lines if line.strip() not in unwanted_strings]
        h_text = "\n".join(lines)

        # Add the constructor param set parameter
        h_text = h_text.replace(
            f" {self.device_class}(",
            f" {self.device_class}({self.device_class}ParamSet* paramSet, ",
        )

        # Add the include
        idx = h_text.index(f'#include "{self.parent_class}.h"')
        h_text = (
            h_text[:idx] + f'#include "{self.device_class}ParamSet.h"\n' + h_text[idx:]
        )
        # Add the param set pointer member definition
        protected_extractor = re.compile(r".*protected:")
        class_extractor = re.compile(r"class.* " + self.device_class + r" :[\s\S]* {")

        matches = re.findall(protected_extractor, h_text)
        class_str = re.findall(class_extractor, h_text)[0]
        param_set_definition = f"    {self.device_class}ParamSet* paramSet;"

        if matches:
            # Protected section exists - add param set here
            protected_str = matches[0]
            h_text = h_text.replace(
                protected_str,
                protected_str + "\n" + param_set_definition,
                1,
            )
        else:
            # Protected section does not exist - create it to add param set
            h_text = h_text.replace(
                class_str,
                class_str + "\n" + "protected:" + "\n" + param_set_definition,
            )

        # Replace FIRST_*_PARAM definition
        h_text = re.sub(
            r"(#define FIRST_\w+_PARAM) \w+",
            r"\1 paramSet->FIRST_" + self.device_class.upper() + "PARAMSET_PARAM",
            h_text,
        )

        return h_text

    def _convert_h_placeholder(self, original_h: str) -> str:
        h_text = original_h
        h_text = h_text.replace(
            f" {self.device_class} : public {self.parent_class}",
            (
                f" {self.device_class} : public {self.parent_class}ParamSet,"
                f" public {self.parent_class}"
            ),
        )
        return h_text


def filter_strings(strings: List[str], filters: List[str]) -> List[str]:
    return [
        string for string in strings if any(filter_ in string for filter_ in filters)
    ]


def get_param_set(driver: str):
    return "asynParamSet" if driver == "asynPortDriver" else driver + "ParamSet"
