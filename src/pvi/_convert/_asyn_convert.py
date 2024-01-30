import re
from typing import Any, Optional, Type

from pvi.device import SignalR, SignalRW, SignalW, enforce_pascal_case

from ._parameters import (
    AsynParameter,
    InRecordTypes,
    OutRecordTypes,
    Parameter,
    Record,
    get_waveform_parameter,
)


class RecordError(Exception):
    pass


class AsynRecord(Record):
    def model_post_init(self, __context: Any):
        # We don't care about records without INP or OUT or with both (error)
        if all(k in self.fields.keys() for k in ("INP", "OUT")) or not any(
            k in self.fields.keys() for k in ("INP", "OUT")
        ):
            raise RecordError("Record has no input or output field or both")

        asyn_field = self.fields.get("INP", self.fields.get("OUT"))
        if asyn_field is None or "@asyn(" not in asyn_field:
            # Is it Asyn, because if it's not we don't care about it
            raise RecordError("Record has no @asyn field")

        # If there is no DESC field we must create one
        if "DESC" not in self.fields.keys():
            self.fields["DESC"] = self.name

    def get_parameter_name(self) -> Optional[str]:
        # e.g. from: field(INP,  "@asyn($(PORT),$(ADDR=0),$(TIMEOUT=1))FILE_PATH")
        # extract: FILE_PATH
        parameter_name_extractor = r"@asyn\(.*\)(\S+)"
        parameter_name = None
        for k, v in self.fields.items():
            if k == "INP" or k == "OUT":
                if "@asyn(" in v:
                    match = re.search(parameter_name_extractor, v)
                    if match:
                        parameter_name = match.group(1)
        return parameter_name

    def asyn_component_type(self) -> Type[AsynParameter]:
        # For waveform records the data type is defined by DTYP
        if self.type == "waveform":
            return get_waveform_parameter(self.fields["DTYP"])

        try:
            if "INP" in self.fields.keys():
                record_types = InRecordTypes
                return record_types[self.type]
            elif "OUT" in self.fields.keys():
                record_types = OutRecordTypes
                return record_types[self.type]
        except KeyError as e:
            raise KeyError(
                f"{self.name} asyn type {self.type}({self.fields}) not found in"
                f"{list(record_types)}"
            ) from e

        raise ValueError(
            f"Could not determine asyn type for {self.name} fields {self.fields}"
        )


class SettingPair(Parameter):
    read_record: AsynRecord
    write_record: AsynRecord

    def generate_component(self) -> SignalRW:
        asyn_cls = self.write_record.asyn_component_type()
        component = asyn_cls(
            name=enforce_pascal_case(self.write_record.name),
            write_record=self.write_record.name,
        )

        return SignalRW(
            name=component.name,
            pv=component.get_write_record(),
            widget=component.write_widget,
            read_pv=component.get_read_record(),
            read_widget=component.read_widget,
        )


class Readback(Parameter):
    read_record: AsynRecord

    def generate_component(self) -> SignalR:
        asyn_cls = self.read_record.asyn_component_type()

        if self.read_record.name.endswith("_RBV"):
            name = self.read_record.name[: -len("_RBV")]
        else:
            name = self.read_record.name

        component = asyn_cls(
            name=enforce_pascal_case(name), read_record=self.read_record.name
        )

        return SignalR(
            name=component.name,
            pv=component.get_read_record(),
            widget=component.read_widget,
        )


class Action(Parameter):
    write_record: AsynRecord

    def generate_component(self) -> SignalW:
        asyn_cls = self.write_record.asyn_component_type()

        component = asyn_cls(
            name=enforce_pascal_case(self.write_record.name),
            write_record=self.write_record.name,
        )

        return SignalW(
            name=component.name,
            pv=component.get_write_record(),
            widget=component.write_widget,
        )
