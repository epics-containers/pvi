import re
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field, FilePath


class SourceConverter(BaseModel):
    source_files: List[FilePath] = Field(
        ..., description="source files to convert to yaml"
    )
    _text: str

    class Config:
        extra = "forbid"

    def __init__(self, **data: Any):
        super().__init__(**data)
        text = ""
        for source_file in self.source_files:
            with open(source_file, "r") as f:
                text += f.read()
        object.__setattr__(self, "_text", text)

    def _extract_create_param_strs(self) -> List[str]:
        # e.g. extract: createParam(SimGainXString, asynParamFloat64, &SimGainX);
        create_param_extractor = re.compile(r"createParam\([^\)]*\);")
        create_param_strs = re.findall(create_param_extractor, self._text)
        return create_param_strs

    def _extract_define_strs(self, str_names: List[str]) -> List[str]:
        # e.g. extract: #define SimGainXString                "SIM_GAIN_X";
        define_extractor = re.compile(r'\#define[_A-Za-z0-9 ]*"[^"]*"[^\n ]*')
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
        create_param_strs = self._extract_create_param_strs()
        string_index_dict = dict(
            [
                self._parse_create_param_str(create_param_str)
                for create_param_str in create_param_strs
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

    def get_top_level_text(self, source_file: FilePath, paramset_name: str) -> str:
        with open(source_file, "r") as f:
            text = f.read()
        top_level_text = self._extract_top_level_text(text)
        top_level_text = self._add_param_set_to_class(top_level_text, paramset_name)
        top_level_text = self._add_ADDriver_paramSet(top_level_text)
        return top_level_text

    def _add_param_set_to_class(self, top_level_text: str, paramset_name: str) -> str:
        # e.g. extract: class epicsShareClass simDetector : public ADDriver {
        class_def_extractor = re.compile(r"class[^:]*:[ ]*public[ ]*ADDriver[ ]*{")
        try:
            class_def_str = re.findall(class_def_extractor, top_level_text)[0]
            class_def_replacement = class_def_str.replace(
                "public", f"public {paramset_name}ParamSet, public"
            )
            top_level_text = top_level_text.replace(
                class_def_str, class_def_replacement
            )
            # Add the include
            idx = top_level_text.index('#include "ADDriver.h"')
            top_level_text = (
                top_level_text[:idx]
                + f'#include "{paramset_name}ParamSet.h"\n'
                + top_level_text[idx:]
            )
        except IndexError:
            pass
        return top_level_text

    def _add_ADDriver_paramSet(self, top_level_text: str) -> str:
        # e.g. extract: "   :  ADDriver(portName"
        constructor_extractor = re.compile(r"[ ]*:[ ]*ADDriver\(portName")
        try:
            constructor_str = re.findall(constructor_extractor, top_level_text)[0]
            idx = constructor_str.find("(") + 1
            constructor_replacement = constructor_str.replace(
                "portName",
                f"static_cast<ADDriverParamSet*>(this),  "
                f"/* Upcast to provide ADDriver with its param set */"
                f"\n{' '*idx}portName",
            )
            top_level_text = top_level_text.replace(
                constructor_str, constructor_replacement
            )
        except IndexError:
            pass
        return top_level_text

    def _extract_top_level_text(self, text: str) -> str:
        string_index_dict = self._get_string_index_mapping()
        create_param_strs = self._extract_create_param_strs()
        definition_strs = self._extract_define_strs(list(string_index_dict.keys()))
        declaration_strs = self._extract_index_declarations(
            list(string_index_dict.values())
        )
        unwanted_strs = create_param_strs + definition_strs + declaration_strs
        top_level_lines = text.splitlines()
        top_level_lines = [
            line
            for line in top_level_lines
            if line.lstrip()
            not in [unwanted_str.lstrip() for unwanted_str in unwanted_strs]
        ]
        top_level_text = "\n".join(top_level_lines)
        return top_level_text
