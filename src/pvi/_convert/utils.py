import re
from typing import List, Tuple


def extract_device_and_parent_class(header_text: str) -> Tuple[str, str]:
    # e.g. extract 'NDPluginDriver' and 'asynNDArrayDriver' from
    # class epicsShareClass NDPluginDriver : public asynNDArrayDriver, public epicsThreadRunable {  # noqa
    class_extractor = re.compile(r"class.*\s+(\w+)\s+:\s+\w+\s+(\w+).*")
    match = re.search(class_extractor, header_text)
    assert match, "Can't find device class and parent class in header file"
    classname, parent = match.groups()
    return classname, parent


def extract_define_strs(header_text, info_strings: List[str]) -> List[str]:
    # e.g. extract: #define SimGainXString                "SIM_GAIN_X";
    define_extractor = re.compile(r'\#define[_A-Za-z0-9 ]*"[^"]*".*')
    definitions = re.findall(define_extractor, header_text)
    # We only want to extract the defines for the given parameter infos
    definitions = filter_strings(definitions, info_strings)
    return definitions


def extract_create_param_strs(source_text, param_strings: List[str]) -> List[str]:
    # e.g. extract: createParam(SimGainXString, asynParamFloat64, &SimGainX);
    create_param_extractor = re.compile(r"((?:this->)?createParam\([^\)]*\);.*)")
    create_param_strs = re.findall(create_param_extractor, source_text)
    # We only want to extract the createParam calls for the given parameter strings
    create_param_strs = filter_strings(create_param_strs, param_strings)
    return create_param_strs


def extract_index_declarations(header_text, index_names: List[str]) -> List[str]:
    # e.g. extract:     int SimGainX;
    declaration_extractor = re.compile(r"\s*int [^;]*;")
    declarations = re.findall(declaration_extractor, header_text)
    # We only want to extract the declarations for the given index names - this also
    # filters any generic int parameter definitions in the class and some comments
    declarations = filter_strings(declarations, index_names)
    return declarations


def parse_definition_str(definition_str: str) -> Tuple[str, str]:
    # e.g. from: #define SimGainXString                "SIM_GAIN_X";
    # extract:
    # Group1: SimGainXString
    # Group2: SIM_GAIN_X
    define_extractor = re.compile(r'(?:\#define) (\w+) *"([^"]*)')
    string_info_pair = re.findall(define_extractor, definition_str)[0]
    return string_info_pair


def parse_create_param_str(create_param_str: str) -> Tuple[str, str]:
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


def insert_param_set_accessors(source_text: str, parameters: List[str]) -> str:
    for parameter in parameters:
        # Only match parameter name exactly, not others with same prefix
        source_text = re.sub(
            r"(\W)" + parameter + r"(\W)",
            r"\1paramSet->" + parameter + r"\2",
            source_text,
        )
    return source_text


def filter_strings(strings: List[str], filters: List[str]) -> List[str]:
    return [
        string for string in strings if any(filter_ in string for filter_ in filters)
    ]


def get_param_set(driver: str):
    return "asynParamSet" if driver == "asynPortDriver" else driver + "ParamSet"
