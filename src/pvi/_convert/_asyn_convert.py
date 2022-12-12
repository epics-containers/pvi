import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Type, cast

from pvi._produce.asyn import Access, AsynParameter, AsynWaveform
from pvi._schema_utils import rec_subclasses

from ._parameters import Parameter, ReadParameterMixin, Record, WriteParameterMixin


class RecordError(Exception):
    pass


@dataclass
class AsynRecord(Record):
    def __post_init__(self):
        # We don't care about records without INP or OUT or with both (error)
        if all(k in self.fields.keys() for k in ("INP", "OUT")) or not any(
            k in self.fields.keys() for k in ("INP", "OUT")
        ):
            raise RecordError("Record has no input or output field or both")

        asyn_field = self.fields.get("INP", self.fields.get("OUT"))
        if "@asyn(" not in asyn_field:
            # Is it Asyn, because if it's not we don't care about it
            raise RecordError("Record has no @asyn field")

        # If there is no DESC field we must create one
        if "DESC" not in self.fields.keys():
            self.fields["DESC"] = self.name

    def get_parameter_name(self) -> Optional[str]:
        # e.g. from: field(INP,  "@asyn($(PORT),$(ADDR=0),$(TIMEOUT=1))FILE_PATH")
        # extract: FILE_PATH
        parameter_name_extractor = r"(?:@asyn\()(?:(?:\$\([^\)]*\)[,]*)*)(?:\))(\S+)"
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
            waveform_components = [AsynWaveform] + cast(
                List[Type[AsynWaveform]], rec_subclasses(AsynWaveform)
            )
            for waveform_cls in waveform_components:
                if self.fields["DTYP"] in (
                    waveform_cls.type_strings.asyn_read,
                    waveform_cls.type_strings.asyn_write,
                ):
                    return waveform_cls
            assert False, f"Waveform type for {self} not found in {waveform_components}"

        asyn_components = cast(List[Type[AsynParameter]], rec_subclasses(AsynParameter))
        if "INP" in self.fields.keys():
            type_fields = [
                (
                    cls.record_fields.in_record_type.__name__,
                    cls.type_strings.asyn_read,
                )
                for cls in asyn_components
            ]
        elif "OUT" in self.fields.keys():
            type_fields = [
                (
                    cls.record_fields.out_record_type.__name__,
                    cls.type_strings.asyn_write,
                )
                for cls in asyn_components
            ]
        try:
            idx = type_fields.index((self.type, self.fields["DTYP"]))
            asyn_class = asyn_components[idx]
            return asyn_class
        except ValueError as e:
            raise ValueError(
                f"{self.name} asyn type: ({self.type}, {self.fields['DTYP']}) "
                f"not found in {type_fields}"
            ) from e
        except KeyError as e:
            raise KeyError(f"{self.name} DTYP not found") from e


@dataclass
class SettingPair(Parameter, WriteParameterMixin, ReadParameterMixin):
    read_record: AsynRecord
    write_record: AsynRecord
    _dominant_read = True

    @property
    def dominant(self):
        return self.read_record if self._dominant_read else self.write_record

    @property
    def subordinate(self):
        return self.write_record if self._dominant_read else self.read_record

    def _get_read_record_suffix(self) -> Optional[str]:
        if self.read_record.name != self.write_record.name + "_RBV":
            return self.read_record.name
        else:
            return None

    def _get_field_clashes(self) -> List[str]:
        # Check to see if there any clashing values in pairs
        clashing_fields = []
        for (read_field_name, read_field_value) in self.read_record.fields.items():
            write_field_value = self.write_record.fields.get(
                read_field_name, read_field_value
            )
            if (
                write_field_value != read_field_value
                and read_field_name not in self.invalid
            ):
                clashing_fields.append(read_field_name)
        return clashing_fields

    def _handle_clashes(self, clashing_fields: List[str]):
        for field in clashing_fields:
            chosen_value = self.dominant.fields[field]
            discarded_value = self.subordinate.fields.get(field, chosen_value)
            print(
                f"Pair: {self.write_record.name}; "
                f"Field: {field}; "
                f"Values: {chosen_value}, "
                f"{discarded_value}; "
                f"Using {chosen_value} "
                f"for both",
                file=sys.stderr,
            )
            self.subordinate.fields[field] = self.dominant.fields.get(
                field, chosen_value
            )

    def get_naming_overrides(self) -> Tuple[str, List[str]]:
        record_name = self.subordinate.name
        override_fields = self._get_field_clashes()
        return record_name, override_fields

    def has_clashes(self) -> bool:
        empty = not self._get_field_clashes()
        return not empty

    def generate_component(self) -> AsynParameter:
        asyn_class = self.write_record.asyn_component_type()

        non_default_args: Dict[str, Any] = dict()
        non_default_args["demand_auto_updates"] = self._get_demand_auto_updates(
            self.write_record
        )
        autosave = self._get_autosave_fields(self.write_record)
        if autosave:
            pass
            # TODO: Consider handling autosave fields - see Action.generate_component
            # non_default_args["autosave"] = autosave

        drv_info = self.write_record.get_parameter_name()
        if drv_info != self.write_record.name:
            non_default_args["drv_info"] = drv_info

        initial = self._get_initial(self.write_record)
        if initial:
            non_default_args["initial"] = initial

        read_record_suffix = self._get_read_record_suffix()
        if read_record_suffix is not None:
            non_default_args["read_record_suffix"] = read_record_suffix

        field_clashes = self._get_field_clashes()
        self._handle_clashes(field_clashes)

        write_fields = self._remove_invalid(self.write_record.fields)
        read_fields = self._remove_invalid(self.read_record.fields)
        record_class = type(asyn_class.record_fields)
        kwargs = {**write_fields, **read_fields}
        record = record_class(**kwargs)  # type: ignore

        component = asyn_class(
            description=self.write_record.fields["DESC"],
            name=self.write_record.name,
            access=Access.RW,
            record_fields=record,
            **non_default_args,
        )
        return component


@dataclass
class Readback(Parameter, ReadParameterMixin):
    read_record: AsynRecord

    def _get_read_record_suffix(self) -> Optional[str]:
        if not self.read_record.name.endswith("_RBV"):
            return self.read_record.name
        else:
            return None

    def generate_component(self) -> AsynParameter:
        asyn_class = self.read_record.asyn_component_type()

        non_default_args: Dict[str, Any] = dict()
        read_record_suffix = self._get_read_record_suffix()
        if read_record_suffix:
            name = self.read_record.name
            non_default_args["read_record_suffix"] = read_record_suffix
        else:
            name = self.read_record.name[: -len("_RBV")]

        drv_info = self.read_record.get_parameter_name()
        if drv_info != self.read_record.name:
            non_default_args["drv_info"] = drv_info

        read_fields = self._remove_invalid(self.read_record.fields)
        record = type(asyn_class.record_fields)(**read_fields)  # type: ignore
        component = asyn_class(
            description=self.read_record.fields["DESC"],
            name=name,
            access=Access.R,
            record_fields=record,
            **non_default_args,
        )
        return component


@dataclass
class Action(Parameter, WriteParameterMixin):
    write_record: AsynRecord

    def generate_component(self) -> AsynParameter:
        asyn_class = self.write_record.asyn_component_type()

        non_default_args: Dict[str, Any] = dict()
        non_default_args["demand_auto_updates"] = self._get_demand_auto_updates(
            self.write_record
        )
        autosave_fields = self._get_autosave_fields(self.write_record)
        if autosave_fields:
            print(
                "Warning: Ignoring autosave fields. Consider how to handle this",
                file=sys.stderr,
            )
            # non_default_args["autosave"] = autosave_fields

        initial = self._get_initial(self.write_record)
        if initial:
            non_default_args["initial"] = initial

        drv_info = self.write_record.get_parameter_name()
        if drv_info != self.write_record.name:
            non_default_args["drv_info"] = drv_info

        write_fields = self._remove_invalid(self.write_record.fields)
        record = type(asyn_class.record_fields)(**write_fields)  # type: ignore
        component = asyn_class(
            description=self.write_record.fields["DESC"],
            name=self.write_record.name,
            access=Access.W,
            record_fields=record,
            **non_default_args,
        )
        return component
