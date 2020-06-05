from typing import Dict, List

from pydantic import BaseModel

from ._asyn import ScanRate
from ._types import Component, Record


class Parameter(BaseModel):
    invalid = ["DESC", "DTYP", "INP", "OUT", "PINI", "SCAN", "VAL"]

    def _remove_invalid(self, fields: Dict[str, str]) -> Dict[str, str]:
        valid_fields = {
            key: value for (key, value) in fields.items() if key not in self.invalid
        }
        return valid_fields

    def generate_component(self) -> Component:
        raise NotImplementedError(self)


class ReadParameterMixin:
    def _get_scan_rate(self, read_record: Record) -> ScanRate:
        try:
            scan_rate = read_record.fields_["SCAN"]
        except KeyError:
            print(f"Key error for {read_record.name}")
            scan_rate = ScanRate.IOINTR
        try:
            return ScanRate(scan_rate)
        except ValueError as e:
            print(f"Validation error for {read_record.name}")
            print(e)
            return ScanRate.IOINTR

    def _get_suffix(self, read_record: Record) -> str:
        try:
            suffix = "_" + read_record.name.split("_", 1)[1]
        except IndexError:
            suffix = "_RBV"
        return suffix


class WriteParameterMixin:
    def _get_initial(self, write_record: Record) -> str:
        try:
            pini = write_record.fields_["PINI"].lower()
        except KeyError:
            pini = "no"
        if pini == "yes":
            try:
                initial = write_record.fields_["VAL"]
            except KeyError:
                initial = "0"
        else:
            initial = ""
        return initial

    def _get_demand_auto_updates(self, write_record: Record) -> bool:
        return write_record.infos.get("asyn:READBACK") == "1"

    def _get_autosave_fields(self, write_record: Record) -> List[str]:
        autosave_fields = write_record.infos.get("autosaveFields")
        if autosave_fields:
            autosave_list = autosave_fields.split(" ")
        else:
            autosave_list = []
        return autosave_list
