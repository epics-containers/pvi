import re
from pathlib import Path
from typing import List, Tuple

from pvi.device import ComponentUnion, Grid, Group, Tree, enforce_pascal_case

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

    def convert(self) -> Tree:
        return [
            Group(
                name=enforce_pascal_case(template.stem),
                layout=Grid(labelled=True),
                children=template_components,
            )
            for template, template_components in zip(
                self.templates, self._extract_components()
            )
        ]

    def _extract_components(self) -> List[List[ComponentUnion]]:
        components = []
        for text in self._text:
            record_extractor = RecordExtractor(text)
            asyn_records = record_extractor.get_asyn_records()
            template_components = []
            for parameter in RecordRoleSorter.sort_records(asyn_records):
                component = parameter.generate_component()
                template_components.append(component)
            components.append(template_components)
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

        if record_type == "motor":
            newline = "\n"
            raise RecordError(
                f"Record `{record_str.split(newline)[0]}` is type motor - ignoring"
            )

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
            except RecordError as error:
                print(error)
        return record_list


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
