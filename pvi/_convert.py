import re
from itertools import chain
from typing import Any, Callable, Dict, List, Tuple, TypeVar

from pydantic import BaseModel, Field, FilePath

from ._asyn_convert import (
    Action,
    AsynRecord,
    Parameter,
    Readback,
    RecordError,
    SettingPair,
)
from ._schema import FormatterUnion
from ._types import Component, Record

R = TypeVar("R", bound=Record)
P = TypeVar("P", bound=Parameter)


class TemplateConverter(BaseModel):
    template_file: FilePath = Field(..., description="template file to convert to yaml")
    formatter: FormatterUnion = Field(
        ..., description="The Formatter class to format the output"
    )

    def top_level_text(self):
        record_extractor = RecordExtractor(self.get_text())
        top_level_text = record_extractor.get_top_level_text()
        return top_level_text

    def convert(self):
        extractor_dict = dict(
            description=lambda: "<Driver Description>",
            macros=self._extract_macros,
            template=self._extract_template,
            includes=self._extract_includes,
            producer=self._extract_asyn_producer,
            formatter=lambda: self.formatter.dict(),
            components=lambda: [
                dict(
                    type="ComponentGroup",
                    name="ComponentGroupOne",
                    children=self._extract_components(),
                )
            ],
        )
        yaml_dict = self._extract_to_dict(extractor_dict)
        return yaml_dict

    def get_text(self):
        with open(self.template_file, "r") as f:
            text = f.read()
        return text

    def _extract_to_dict(self, extractor_dict: Dict[str, Callable[[], Any]]):
        filled_dict = dict()
        for key, extractor_func in extractor_dict.items():
            value = extractor_func()
            if value:
                filled_dict[key] = value
        return filled_dict

    def _extract_template(self) -> str:
        template = "<path-to-template>/" + str(self.template_file.name)
        return template

    def _extract_includes(self) -> List[Dict[str, str]]:
        def get_include_names(text: str) -> List[str]:
            include_extractor = re.compile(
                r'(?:include)(?:[^"]*)(?:")([A-Za-z0-9][^.]*)(?:\.template)'
            )
            include_names = re.findall(include_extractor, text)
            include_names = list(set(include_names))
            return include_names

        include_names = get_include_names(self.get_text())
        include_list = [
            dict(path=f"<path-to-yaml>/{name}.pvi.yaml") for name in include_names
        ]
        return include_list

    def _extract_asyn_producer(self) -> Dict[str, str]:
        def get_prefix(text: str) -> Dict[str, str]:
            prefix_extractor = re.compile(
                r'(?:record\()(?:[^,]*)(?:[^"]*)(?:")((?:\$\([^)]\))*)(?:[^"]*)'
            )
            prefixes = re.findall(prefix_extractor, text)
            prefixes = list(set(prefixes))
            if len(prefixes) > 1:
                print(f"More than one prefix found. Taking the first instance")
            prefix_dict = dict(prefix=prefixes[0])
            return prefix_dict

        def get_asyn_macros(text: str) -> Dict[str, str]:
            default_asyn_macros = dict(
                asyn_port="$(PORT)", address="$(ADDR)", timeout="$(TIMEOUT)"
            )
            asyn_macro_extractor = r"(?:@asyn\()((?:\$\([^\)]*\)(?:[^\$\)])*)*)"
            asyn_macros = re.findall(asyn_macro_extractor, text)
            asyn_macros = list(set(asyn_macros))
            if len(asyn_macros) > 1:
                print(
                    f"More than one set of asyn macros found. Taking the first instance"
                )
            asyn_macros = asyn_macros[0].split(",")
            if len(asyn_macros) > len(default_asyn_macros):
                raise ValueError("Found too many asyn macros")
            elif len(asyn_macros) < len(default_asyn_macros):
                print(
                    f"Didn't find enough asyn_macros,"
                    "taking a guess at the missing ones"
                )
                extra_macros = iter(
                    set(default_asyn_macros.values()).difference(asyn_macros)
                )
                while len(asyn_macros) < len(default_asyn_macros):
                    asyn_macros.append(next(extra_macros))
            asyn_macro_dict = dict(zip(default_asyn_macros.keys(), asyn_macros))
            return asyn_macro_dict

        producer = dict(type="AsynProducer")
        macro_dict = {**get_prefix(self.get_text()), **get_asyn_macros(self.get_text())}
        producer = {**producer, **macro_dict}
        return producer

    def _extract_components(self) -> List[Component]:
        record_extractor = RecordExtractor(self.get_text())
        asyn_records = record_extractor.get_asyn_records()
        actions, readbacks, setting_pairs = RecordRoleSorter.sort_records(asyn_records)
        components = []
        for parameter in chain(actions, readbacks, setting_pairs):
            component = parameter.generate_component()
            component_dict = component.dict(
                exclude_unset=True,
                exclude_none=True,
                exclude_defaults=True,
                by_alias=True,
            )
            components.append(component_dict)
        return components

    def _extract_macros(self) -> List[Dict[str, str]]:
        def get_all_macros(text: str) -> List[str]:
            macro_extractor = r"(?:\$\()([^\)]*)(?:\))"
            macros = re.findall(macro_extractor, text)
            macros = list(set(macros))
            return macros

        all_macros = get_all_macros(self.get_text())
        macro_list = [
            dict(type="StringMacro", name=macro, description="Macro desc")
            for macro in all_macros
        ]
        return macro_list


class RecordExtractor:
    def __init__(self, text):
        self.text = text

    def _extract_record_strs(self):
        record_extractor = re.compile(r"record\([^{]*{[^}]*}")
        return re.findall(record_extractor, self.text)

    def _parse_record(self, record_str: str) -> Tuple:
        record_parser = re.compile(
            r'(?:record\()([^,]*)(?:[^"]*)(?:")'
            r'(?:(?:\$\([a-zA-Z0-9]\))*)([^"]*)'
            r'(?:")(?:[^{]*)(?:{)([^}]*)(?:})'
        )
        return re.findall(record_parser, record_str)[0]

    def _create_asyn_record(self, record_str: str) -> AsynRecord:
        record_type, record_name, record_fields = self._parse_record(record_str)
        field_extractor = r'(?:field\()([^,]*)(?:,)(?:[^"]*)(?:")([^"]*)(?:")'
        fields = dict(re.findall(field_extractor, record_fields))
        info_extractor = r'(?:info\()([^,]*)(?:,)(?:[^"]*)(?:")([^"]*)(?:")'
        info = dict(re.findall(info_extractor, record_fields))
        record = AsynRecord(
            name=record_name, type=record_type, fields=fields, infos=info,
        )
        return record

    def get_asyn_records(self) -> List[AsynRecord]:
        record_strs = [record for record in self._extract_record_strs()]
        record_list = []
        for record_str in record_strs:
            try:
                record_list.append(self._create_asyn_record(record_str))
            except RecordError:
                pass
        return record_list

    def _create_stream_record(self, record_str):
        raise RecordError

    def get_stream_records(self):
        return []

    def get_top_level_text(self):
        record_strs = [record for record in self._extract_record_strs()]
        top_level_str = self.text
        for record_str in record_strs:
            try:
                self._create_asyn_record(record_str)
            except RecordError:
                try:
                    self._create_stream_record(record_str)
                except RecordError:
                    pass
            else:
                top_level_str = top_level_str.replace(record_str, "")
        return top_level_str


class RecordRoleSorter:
    @staticmethod
    def sort_records(
        records: List[R],
    ) -> Tuple[List[Action], List[Readback], List[SettingPair]]:
        def _sort_inputs_outputs(records: List[R]) -> Tuple[List[R], List[R]]:
            inp_records = [r for r in records if "INP" in r.fields_.keys()]
            write_records = [r for r in records if "OUT" in r.fields_.keys()]

            # Move waveform records with asynOctetWrite from read to write
            read_records = []
            for r in inp_records:
                if r.type == "waveform" and r.fields_["DTYP"] == "asynOctetWrite":
                    write_records.append(r)
                else:
                    read_records.append(r)
            return read_records, write_records

        read_records, write_records = _sort_inputs_outputs(records)
        actions = ParameterRoleMatcher.get_actions(read_records, write_records)
        readbacks = ParameterRoleMatcher.get_readbacks(read_records, write_records)
        setting_pairs = ParameterRoleMatcher.get_setting_pairs(
            read_records, write_records
        )
        return actions, readbacks, setting_pairs


class ParameterRoleMatcher:
    @staticmethod
    def get_actions(read_records, write_records) -> List[Action]:
        actions = [
            Action(write_record=w)
            for w in write_records
            if w.get_parameter_name()
            not in [r.get_parameter_name() for r in read_records]
        ]
        return actions

    @staticmethod
    def get_readbacks(read_records, write_records) -> List[Readback]:
        readbacks = [
            Readback(read_record=r)
            for r in read_records
            if r.get_parameter_name()
            not in [w.get_parameter_name() for w in write_records]
        ]
        return readbacks

    @staticmethod
    def get_setting_pairs(read_records, write_records) -> List[SettingPair]:
        setting_pairs = [
            SettingPair(read_record=r, write_record=w)
            for r in read_records
            for w in write_records
            if r.get_parameter_name() == w.get_parameter_name()
        ]
        return setting_pairs
