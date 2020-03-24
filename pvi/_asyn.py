from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterator, List

from pydantic import Field

from ._types import Producer, Record, WithType
from ._util import truncate_description

VALUE_FIELD = Field(None, description="The initial value of the parameter")


@dataclass
class AsynParameterInfo:
    asyn_param_type: str  #: Asyn parameter type, e.g. asynParamFloat64
    read_record_type: str  #: RTYP of the read record, e.g. ai
    write_record_type: str  #: RTYP of the write record, e.g. ao
    read_record_fields: Dict[str, str]  #: Fields to add to the read record
    write_record_fields: Dict[str, str]  #: Fields to add to the write record


class ParameterRole(str, Enum):
    READBACK = "READBACK"  #: Read record only
    ACTION = "ACTION"  #: Write record only
    SETTING1 = "SETTING1"  #: Write record that syncs with readback values
    SETTING2 = "SETTING2"  #: Read and write records
    ACTION_READBACK = "ACTION_READBACK"  #: Write record with readback for current value

    def needs_read_record(self):
        return self not in [self.ACTION, self.SETTING1]

    def needs_write_record(self):
        return self != self.READBACK


class ScanRate(str, Enum):
    PASSIVE = "Passive"
    EVENT = "Event"
    IOINTR = "I/O Intr"
    TEN = "10 second"
    FIVE = "5 second"
    TWO = "2 second"
    ONE = "1 second"
    POINTFIVE = ".5 second"
    POINTTWO = ".2 second"
    POINTONE = ".1 second"


class AsynParameter(WithType):
    """Base class for all Asyn Parameters to inherit from"""

    name: str = Field(
        ..., description="Name of the Asyn Parameter in the C++ code",
    )
    description: str = Field(
        ..., description="Description of what this Parameter is for"
    )
    role: ParameterRole = Field(
        ParameterRole.SETTING2, description=ParameterRole.__doc__,
    )
    autosave: List[str] = Field(
        [], description="Record fields that should be autosaved"
    )
    read_record_suffix: str = Field(
        None, description="The read record suffix, if not given then use $(name)_RBV"
    )
    read_record_scan: ScanRate = Field(
        ScanRate.IOINTR, description="SCAN rate of the read record"
    )
    write_record_suffix: str = Field(
        None, description="The write record suffix, if not given then use $(name)"
    )
    initial: Any = None

    def asyn_parameter_info(self) -> AsynParameterInfo:
        """Return (InRecordInfo, OutRecordInfo)"""
        raise NotImplementedError(self)


class AsynString(AsynParameter):
    """Asyn String Parameter and records"""

    initial: str = VALUE_FIELD

    def asyn_parameter_info(self) -> AsynParameterInfo:
        info = AsynParameterInfo(
            read_record_type="stringin",
            read_record_fields=dict(DTYP="asynOctetRead"),
            write_record_type="stringout",
            write_record_fields=dict(DTYP="asynOctetWrite"),
            asyn_param_type="asynParamOctet",
        )
        return info


class AsynFloat64(AsynParameter):
    """Asyn Float64 Parameter and records"""

    initial: float = VALUE_FIELD
    precision: int = Field(3, description="Record precision")
    units: str = Field("", description="Record engineering units")

    def asyn_parameter_info(self) -> AsynParameterInfo:
        fields = dict(DTYP="asynFloat64", EGU=self.units, PREC=str(self.precision))
        info = AsynParameterInfo(
            read_record_type="ai",
            read_record_fields=fields,
            write_record_type="ao",
            write_record_fields=fields,
            asyn_param_type="asynParamFloat64",
        )
        return info


class AsynProducer(Producer):
    prefix: str = Field(
        ..., description="The prefix for record names created by the template file"
    )
    asyn_port: str = Field(..., description="The asyn port name")
    address: str = Field(..., description="The asyn address")
    timeout: str = Field(..., description="The timeout for the asyn port")

    def _make_common_fields(
        self, component: AsynParameter, io_field: str
    ) -> Dict[str, str]:
        fields = dict(DESC=truncate_description(component.description))
        fields[io_field] = (
            f"@asyn({self.asyn_port},{self.address},{self.timeout})"
            + component.name.upper()
        )
        return fields

    def produce_records(self, component: AsynParameter) -> Iterator[Record]:
        if isinstance(component, AsynParameter):
            info = component.asyn_parameter_info()
            if component.role.needs_read_record():
                if component.read_record_suffix:
                    record_name = self.prefix + component.read_record_suffix
                else:
                    record_name = self.prefix + component.name + "_RBV"
                fields = dict(
                    SCAN=component.read_record_scan.value,
                    **self._make_common_fields(component, "INP"),
                    **info.read_record_fields,
                )
                yield Record(
                    record_name=record_name,
                    record_type=info.read_record_type,
                    fields=fields,
                    infos={},
                )
            if component.role.needs_write_record():
                if component.write_record_suffix:
                    record_name = self.prefix + component.write_record_suffix
                else:
                    record_name = self.prefix + component.name
                if info.write_record_type == "waveform":
                    io_field = "INP"
                else:
                    io_field = "OUT"
                fields = dict(
                    **self._make_common_fields(component, io_field),
                    **info.write_record_fields,
                )
                if component.initial is not None:
                    fields["PINI"] = "YES"
                    fields["VAL"] = str(component.initial)
                infos = {}
                if component.autosave:
                    infos["autosaveFields"] = " ".join(component.autosave)
                if component.role == ParameterRole.SETTING1:
                    infos["asyn:READBACK"] = "1"
                yield Record(
                    record_name=record_name,
                    record_type=info.write_record_type,
                    fields=fields,
                    infos=infos,
                )

    def produce_src(self, components: List[AsynParameter]):
        return super().produce_src(components)
