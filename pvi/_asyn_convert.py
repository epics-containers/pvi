import re
import sys
from typing import Any, Dict, Type

from pydantic import root_validator

from ._asyn import AsynComponent, ParameterRole
from ._parameters import Parameter, ReadParameterMixin, WriteParameterMixin
from ._types import Record


class RecordError(Exception):
    pass


class AsynRecord(Record):
    def __init__(self, **fields_: Dict[str, str]):
        super().__init__(**fields_)
        # If there is no DESC field we must create one
        if "DESC" not in self.fields_.keys():
            self.fields_["DESC"] = self.name

    @root_validator
    def validate_template_file(cls, values):
        v = values.get("fields_")
        # We don't care about records without INP or OUT or with both (error)
        if all(k in v.keys() for k in ("INP", "OUT")) or not any(
            k in v.keys() for k in ("INP", "OUT")
        ):
            raise RecordError(f"Record has no input or output field or both")

        asyn_field = v.get("INP", v.get("OUT"))
        if "@asyn(" not in asyn_field:
            # Is it Asyn, because if it's not we don't care about it
            raise RecordError(f"Record has no @asyn field")
        return values

    def get_parameter_name(self):
        # e.g. from: field(INP,  "@asyn($(PORT),$(ADDR=0),$(TIMEOUT=1))FILE_PATH")
        # extract: FILE_PATH
        parameter_name_extractor = r"(?:@asyn\()(?:(?:\$\([^\)]*\)[,]*)*)(?:\))(\S+)"
        for k, v in self.fields_.items():
            if k == "INP" or k == "OUT":
                if "@asyn(" in v:
                    parameter_name = re.search(parameter_name_extractor, v).group(1)
        return parameter_name

    def asyn_component_type(self) -> Type[AsynComponent]:
        asyn_components = [cls for cls in AsynComponent.__subclasses__()]
        asyn_component_types = [
            cls.type_strings for cls in AsynComponent.__subclasses__()
        ]
        if "INP" in self.fields_.keys():
            type_fields = [
                (type_string.read_record, type_string.asyn_read)
                for type_string in asyn_component_types
            ]
        elif "OUT" in self.fields_.keys():
            type_fields = [
                (type_string.write_record, type_string.asyn_write)
                for type_string in asyn_component_types
            ]

        # waveform is a special case. It can only ever be an INP
        if self.type == "waveform" and self.fields_["DTYP"] == "asynOctetWrite":
            type_fields = [
                (type_string.write_record, type_string.asyn_write)
                for type_string in asyn_component_types
            ]
        try:
            idx = type_fields.index((self.type, self.fields_["DTYP"]))
            asyn_class = asyn_components[idx]
            return asyn_class
        except ValueError as e:
            raise ValueError(
                f"{self.name} asyn type: ({self.type}, {self.fields_['DTYP']}) "
                f"not found"
            ) from e
        except KeyError as e:
            raise KeyError(f"{self.name} DTYP not found") from e


class SettingPair(Parameter, WriteParameterMixin, ReadParameterMixin):
    read_record: AsynRecord
    write_record: AsynRecord

    def _get_pair_suffix(self) -> str:
        if self.read_record.name.startswith(self.write_record.name):
            suffix = self.read_record.name[len(self.write_record.name) :]
        else:
            suffix = self._get_suffix(self.read_record)
        return suffix

    def _handle_clashes(self) -> None:
        # Check to see if there any clashing values in pairs
        for (read_field_name, read_field_value) in self.read_record.fields_.items():
            write_field_value = self.write_record.fields_.get(
                read_field_name, read_field_value
            )
            if (
                write_field_value != read_field_value
                and read_field_name not in self.invalid
            ):
                print(
                    f"Pair: {self.write_record.name}; "
                    f"Field: {read_field_name}; "
                    f"Values: {read_field_value}, "
                    f"{write_field_value}; "
                    f"Using {write_field_value} "
                    f"for both",
                    file=sys.stderr,
                )
                self.read_record.fields_[
                    read_field_name
                ] = self.write_record.fields_.get(read_field_name, read_field_value)

    def generate_component(self) -> AsynComponent:
        asyn_class = self.write_record.asyn_component_type()

        non_default_args: Dict[str, Any] = dict()
        non_default_args["demand_auto_updates"] = self._get_demand_auto_updates(
            self.write_record
        )
        non_default_args["autosave"] = self._get_autosave_fields(self.write_record)

        initial = self._get_initial(self.write_record)
        if initial:
            non_default_args["initial"] = initial

        read_record_scan = self._get_scan_rate(self.read_record)
        if read_record_scan:
            non_default_args["read_record_scan"] = read_record_scan

        suffix = self._get_pair_suffix()
        if suffix:
            non_default_args["read_record_suffix"] = suffix

        self._handle_clashes()

        component = asyn_class(
            description=self.write_record.fields_["DESC"],
            name=self.write_record.name,
            role=ParameterRole.SETTING,
            record_fields={**self.write_record.fields_, **self.read_record.fields_},
            **non_default_args,
        )
        return component


class Readback(Parameter, ReadParameterMixin):
    read_record: AsynRecord

    def generate_component(self) -> AsynComponent:
        asyn_class = self.read_record.asyn_component_type()
        name = self.read_record.name.split("_", 1)[0]

        non_default_args: Dict[str, Any] = dict()
        read_record_scan = self._get_scan_rate(self.read_record)
        if read_record_scan:
            non_default_args["read_record_scan"] = read_record_scan

        suffix = self._get_suffix(self.read_record)
        if suffix:
            non_default_args["read_record_suffix"] = suffix

        fields = {}
        read_fields = self._remove_invalid(self.read_record.fields_)
        if read_fields:
            fields["read_fields"] = read_fields

        component = asyn_class(
            description=self.read_record.fields_["DESC"],
            name=name,
            role=ParameterRole.READBACK,
            record_fields=self.read_record.fields_,
            **non_default_args,
        )
        return component


class Action(Parameter, WriteParameterMixin):
    write_record: AsynRecord

    def generate_component(self) -> AsynComponent:
        asyn_class = self.write_record.asyn_component_type()

        non_default_args: Dict[str, Any] = dict()
        non_default_args["demand_auto_updates"] = self._get_demand_auto_updates(
            self.write_record
        )
        non_default_args["autosave"] = self._get_autosave_fields(self.write_record)

        initial = self._get_initial(self.write_record)
        if initial:
            non_default_args["initial"] = initial

        fields = {}
        write_fields = self._remove_invalid(self.write_record.fields_)
        if write_fields:
            fields["write_fields"] = write_fields

        component = asyn_class(
            description=self.write_record.fields_["DESC"],
            name=self.write_record.name,
            role=ParameterRole.ACTION,
            record_fields=self.write_record.fields_,
            **non_default_args,
        )
        return component
