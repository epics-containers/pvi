from typing import Dict, List, Optional

from pydantic import BaseModel

from ._types import Component, Record


class Parameter(BaseModel):
    invalid = ["DESC", "DTYP", "INP", "OUT", "PINI", "VAL"]

    def _remove_invalid(self, fields: Dict[str, str]) -> Dict[str, str]:
        valid_fields = {
            key: value for (key, value) in fields.items() if key not in self.invalid
        }
        return valid_fields

    def generate_component(self) -> Component:
        raise NotImplementedError(self)


class ReadParameterMixin:
    def _get_read_record_suffix(self) -> Optional[str]:
        raise NotImplementedError(self)


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
