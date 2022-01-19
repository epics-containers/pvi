from dataclasses import dataclass
from typing import Dict, List, Optional

from pvi._produce.asyn import AsynParameter


@dataclass
class Record:
    name: str  # The name of the record e.g. $(P)$(M)Status
    type: str  # The record type string e.g. ao, stringin
    fields: Dict[str, str]  # The record fields
    infos: Dict[str, str]  # Any infos to be added to the record


class Parameter:
    invalid = ["DESC", "DTYP", "INP", "OUT", "PINI", "VAL"]

    def _remove_invalid(self, fields: Dict[str, str]) -> Dict[str, str]:
        valid_fields = {
            key: value for (key, value) in fields.items() if key not in self.invalid
        }
        return valid_fields

    def generate_component(self) -> AsynParameter:
        raise NotImplementedError(self)


class ReadParameterMixin:
    def _get_read_record_suffix(self) -> Optional[str]:
        raise NotImplementedError(self)


class WriteParameterMixin:
    def _get_initial(self, write_record: Record) -> str:
        return write_record.fields.get("VAL", "")

    def _get_demand_auto_updates(self, write_record: Record) -> bool:
        return write_record.infos.get("asyn:READBACK") == "1"

    def _get_autosave_fields(self, write_record: Record) -> List[str]:
        autosave_fields = write_record.infos.get("autosaveFields")
        if autosave_fields:
            autosave_list = autosave_fields.split(" ")
        else:
            autosave_list = []
        return autosave_list
