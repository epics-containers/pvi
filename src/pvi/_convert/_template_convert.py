import re
from pathlib import Path
from typing import Dict, List, Tuple

from pvi._produce.asyn import AsynParameter, AsynProducer
from pvi.device import Grid, Group

from ._asyn_convert import (
    Action,
    AsynRecord,
    Parameter,
    Readback,
    RecordError,
    SettingPair,
)

OVERRIDE_DESC = "# Overriding value in auto-generated template"


class TemplateConverter:
    def __init__(self, templates: List[Path]):
        self.templates = templates
        self._text = [t.read_text() for t in self.templates]

    def top_level_text(self, driver_name: str):
        extracted_templates = []
        for text in self._text:
            record_extractor = RecordExtractor(text)
            extracted_templates.append(record_extractor.get_top_level_text(driver_name))
        return extracted_templates

    def convert(self) -> AsynProducer:
        def get_prefix(texts: List[str]) -> str:
            # e.g. from: record(waveform, "$(P)$(R)FilePath")
            # extract: $(P)$(R)
            prefix_extractor = re.compile(
                r'(?:record\()(?:[^,]*)(?:[^"]*)(?:")((?:\$\([^)]\))*)(?:[^"]*)'
            )
            for text in texts:
                prefixes = re.findall(prefix_extractor, text)
            prefixes = list(set(prefixes))
            if len(prefixes) > 1:
                raise ValueError("Not all asyn records have the same macro prefix")
            return prefixes.pop()

        def get_asyn_parameters(texts: List[str]) -> Dict[int, str]:
            # e.g. from: field(INP,  "@asyn($(PORT),$(ADDR=0),$(TIMEOUT=1))FILE_PATH")
            # extract: $(PORT),$(ADDR=0),$(TIMEOUT=1))FILE_PATH
            asyn_parameter_extractor = r'(?:@asyn\()([^"]*)'
            for text in texts:
                asyn_parameters = re.findall(asyn_parameter_extractor, text)
            # then: remove final close bracket and driver param name
            # $(PORT),$(ADDR=0),$(TIMEOUT=1)
            asyn_parameters = [match[: match.rfind(")")] for match in asyn_parameters]
            assert asyn_parameters, "No Asyn parameters found"
            if len(set(asyn_parameters)) > 1:
                print(
                    "More than one set of asyn params found. Taking the first instance"
                )
            return {i: p.strip() for i, p in enumerate(asyn_parameters[0].split(","))}

        asyn_vars = get_asyn_parameters(self._text)

        return AsynProducer(
            prefix=get_prefix(self._text),
            label=self.templates[0].stem,
            asyn_port=asyn_vars.get(0, "$(PORT)"),
            address=asyn_vars.get(1, "$(ADDR=0)"),
            timeout=asyn_vars.get(2, "$(TIMEOUT=1)"),
            parent="asynPortDriver",
            parameters=[
                Group(
                    name="ComponentGroupOne",
                    layout=Grid(),
                    children=self._extract_components(),
                )
            ],
        )

    def _extract_components(self) -> List[AsynParameter]:
        components = []
        for text in self._text:
            record_extractor = RecordExtractor(text)
            asyn_records = record_extractor.get_asyn_records()
            for parameter in RecordRoleSorter.sort_records(asyn_records):
                component = parameter.generate_component()
                components.append(component)
        return components


class RecordExtractor:
    def __init__(self, text):
        self._text = text

    def _extract_record_strs(self):
        # extract a whole record definition inc. fields and leading empty lines e.g.
        # record(waveform, "$(P)$(R)FilePath")
        # {
        #    field(PINI, "YES")
        #    field(DTYP, "asynOctetWrite")
        #    field(INP,  "@asyn($(PORT),$(ADDR=0),$(TIMEOUT=1))FILE_PATH")
        #    field(FTVL, "CHAR")
        #    field(NELM, "256")
        #    info(autosaveFields, "VAL")
        # }
        record_extractor = re.compile(r"\s*^[^#\n]*record\([^{]*{[^}]*}", re.MULTILINE)
        return re.findall(record_extractor, self._text)

    def _parse_record(self, record_str: str) -> Tuple:
        # extract three groups from a record definition e.g.
        # from:
        # record(waveform, "$(P)$(R)FilePath")
        # {
        #    #field(PINI, "YES")
        #    field(DTYP, "asynOctetWrite")
        #    field(INP,  "@asyn($(PORT),$(ADDR=0),$(TIMEOUT=1))FILE_PATH")
        #    field(FTVL, "CHAR")
        #    field(NELM, "256")
        #    info(autosaveFields, "VAL")
        # }
        # extract:
        # Group 1 - record type: waveform
        # Group 2 - record name exc. prefix: FilePath
        # Group 3 - all fields:
        #    #field(PINI, "YES")
        #    field(DTYP, "asynOctetWrite")
        #    field(INP,  "@asyn($(PORT),$(ADDR=0),$(TIMEOUT=1))FILE_PATH")
        #    field(FTVL, "CHAR")
        #    field(NELM, "256")
        #    info(autosaveFields, "VAL")
        #
        record_parser = re.compile(
            r'(?:record\()([^,]*)(?:[^"]*)(?:")'
            r'(?:(?:\$\([a-zA-Z0-9]\))*)([^"]*)'
            r'(?:")(?:[^{]*)(?:{)([^}]*)(?:})'
        )
        return re.findall(record_parser, record_str)[0]

    def _extract_fields(self, fields_str: str) -> List[Tuple[str, str]]:
        # extract two groups from a field e.g.
        # from: field(PINI, "YES")
        # extract:
        # Group 1 - Field: PINI
        # Group 2 - Value: YES
        field_extractor = re.compile(
            r'^[^#\n]*(?:field\()([^,]*)(?:,)(?:[^"]*)(?:")([^"]*)(?:")', re.MULTILINE
        )
        return re.findall(field_extractor, fields_str)

    def _extract_infos(self, fields_str: str) -> List[Tuple[str, str]]:
        # extract two groups from an info tag e.g.
        # from: info(autosaveFields, "VAL")
        # extract:
        # Group 1 - Field: autosaveFields
        # Group 2 - Value: VAL
        info_extractor = re.compile(
            r'^[^#\n]*(?:info\()([^,]*)(?:,)(?:[^"]*)(?:")([^"]*)(?:")', re.MULTILINE
        )
        return re.findall(info_extractor, fields_str)

    def _create_asyn_record(self, record_str: str) -> AsynRecord:
        record_type, record_name, record_fields = self._parse_record(record_str)
        fields = dict(self._extract_fields(record_fields))
        info = dict(self._extract_infos(record_fields))
        record = AsynRecord(
            name=record_name, type=record_type, fields=fields, infos=info
        )
        return record

    def get_asyn_records(self) -> List[AsynRecord]:
        record_strs = self._extract_record_strs()
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

    def get_top_level_text(self, driver_name: str) -> str:
        record_strs = self._extract_record_strs()
        top_level_str = self._text
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

        # Get override strings for setting pair clashes
        asyn_records = self.get_asyn_records()

        setting_pairs = [
            p
            for p in RecordRoleSorter.sort_records(asyn_records)
            if isinstance(p, SettingPair)
        ]
        overrides = [
            setting_pair.get_naming_overrides()
            for setting_pair in setting_pairs
            if setting_pair.has_clashes()
        ]
        record_lines = {
            self._parse_record(record_str)[1]: record_str.splitlines()
            for record_str in record_strs
        }

        def keep_line(line: str, clashing_fields: List[str]) -> bool:
            extracted_field = self._extract_fields(line) or self._extract_infos(line)
            return not extracted_field or (extracted_field[0][0] in clashing_fields)

        override = [
            "\n".join(
                [OVERRIDE_DESC]
                + [
                    line
                    for line in record_lines[record_name]
                    if line and keep_line(line, clashing_fields)
                ]
            )
            for record_name, clashing_fields in overrides
        ]

        top_level_str = self._add_param_template_include(top_level_str, driver_name)
        top_level_str += "\n\n".join(override)
        return top_level_str

    def _add_param_template_include(self, top_level_str: str, driver_name: str) -> str:
        top_level_str = f'include "{driver_name}Parameters.template"\n' + top_level_str
        return top_level_str


class RecordRoleSorter:
    @staticmethod
    def sort_records(records: List[AsynRecord]) -> List[Parameter]:
        def _sort_inputs_outputs(
            records: List[AsynRecord],
        ) -> Tuple[List[AsynRecord], List[AsynRecord]]:
            inp_records = [r for r in records if "INP" in r.fields]
            write_records = [r for r in records if "OUT" in r.fields]

            # Move waveform records with asynOctetWrite from read to write
            read_records = []
            for r in inp_records:
                if r.type == "waveform" and (
                    r.fields["DTYP"] == "asynOctetWrite"
                    or r.fields["DTYP"].endswith("ArrayOut")
                ):
                    write_records.append(r)
                else:
                    read_records.append(r)
            return read_records, write_records

        read_records, write_records = _sort_inputs_outputs(records)
        parameters: List[Parameter] = []
        parameters += ParameterRoleMatcher.get_actions(read_records, write_records)
        parameters += ParameterRoleMatcher.get_readbacks(read_records, write_records)
        parameters += ParameterRoleMatcher.get_setting_pairs(
            read_records, write_records
        )
        return parameters


class ParameterRoleMatcher:
    @staticmethod
    def get_actions(
        read_records: List[AsynRecord], write_records: List[AsynRecord]
    ) -> List[Action]:
        actions = [
            Action(write_record=w)
            for w in write_records
            if w.get_parameter_name()
            not in [r.get_parameter_name() for r in read_records]
        ]
        return actions

    @staticmethod
    def get_readbacks(
        read_records: List[AsynRecord], write_records: List[AsynRecord]
    ) -> List[Readback]:
        readbacks = [
            Readback(read_record=r)
            for r in read_records
            if r.get_parameter_name()
            not in [w.get_parameter_name() for w in write_records]
        ]
        return readbacks

    @staticmethod
    def get_setting_pairs(
        read_records: List[AsynRecord], write_records: List[AsynRecord]
    ) -> List[SettingPair]:
        setting_pairs = [
            SettingPair(read_record=r, write_record=w)
            for r in read_records
            for w in write_records
            if r.get_parameter_name() == w.get_parameter_name()
        ]
        return setting_pairs
