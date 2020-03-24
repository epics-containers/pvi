from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterator, List

from pydantic import Field

from ._types import ChannelTree, Component, ComponentTree, Group, Producer, Record
from ._util import truncate_description, walk

VALUE_FIELD = Field(None, description="The initial value of the parameter")


@dataclass
class AsynParameterInfo:
    asyn_param_type: str  #: Asyn parameter type, e.g. asynParamFloat64
    read_record_type: str  #: RTYP of the read record, e.g. ai
    write_record_type: str  #: RTYP of the write record, e.g. ao
    read_record_fields: Dict[str, str]  #: Fields to add to the read record
    write_record_fields: Dict[str, str]  #: Fields to add to the write record


class ParameterRole(str, Enum):
    SETTING = "Setting"  #: Write record that syncs with readback values
    SETTING_PAIR = "Setting Pair"  #: Read and write records
    ACTION = "Action"  #: Write record only
    READBACK = "Readback"  #: Read record only
    ACTION_READBACK = "Action + Readback"  #: Write record current value readback

    def needs_read_record(self):
        return self not in [self.ACTION, self.SETTING]

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


class AsynParameter(Component):
    """Base class for all Asyn Parameters to inherit from"""

    name: str = Field(
        ..., description="Name of the Asyn Parameter in the C++ code",
    )
    description: str = Field(
        ..., description="Description of what this Parameter is for"
    )
    role: ParameterRole = Field(
        ParameterRole.SETTING_PAIR, description=ParameterRole.__doc__,
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

    def _make_common_record_fields(
        self, component: AsynParameter, io_field: str
    ) -> Dict[str, str]:
        fields = dict(DESC=truncate_description(component.description))
        fields[io_field] = (
            f"@asyn({self.asyn_port},{self.address},{self.timeout})"
            + component.name.upper()
        )
        return fields

    def _make_read_record(self, component: AsynParameter) -> Record:
        info = component.asyn_parameter_info()
        if component.read_record_suffix:
            record_name = self.prefix + component.read_record_suffix
        else:
            record_name = self.prefix + component.name + "_RBV"
        fields = dict(
            SCAN=component.read_record_scan.value,
            **self._make_common_record_fields(component, "INP"),
            **info.read_record_fields,
        )
        return Record(
            record_name=record_name,
            record_type=info.read_record_type,
            fields=fields,
            infos={},
        )

    def _make_write_record(self, component: AsynParameter) -> Record:
        info = component.asyn_parameter_info()
        if component.write_record_suffix:
            record_name = self.prefix + component.write_record_suffix
        else:
            record_name = self.prefix + component.name
        if info.write_record_type == "waveform":
            io_field = "INP"
        else:
            io_field = "OUT"
        fields = dict(
            **self._make_common_record_fields(component, io_field),
            **info.write_record_fields,
        )
        if component.initial is not None:
            fields["PINI"] = "YES"
            fields["VAL"] = str(component.initial)
        infos = {}
        if component.autosave:
            infos["autosaveFields"] = " ".join(component.autosave)
        if component.role == ParameterRole.SETTING:
            infos["asyn:READBACK"] = "1"
        return Record(
            record_name=record_name,
            record_type=info.write_record_type,
            fields=fields,
            infos=infos,
        )

    def produce_records(self, component: Component) -> Iterator[Record]:
        if isinstance(component, AsynParameter):
            if component.role.needs_read_record():
                yield self._make_read_record(component)
            if component.role.needs_write_record():
                yield self._make_write_record(component)

    def produce_channels(self, components: ComponentTree) -> ChannelTree:
        channels: ChannelTree = []
        return channels

    def produce_src(self, components: ComponentTree, basename: str):
        parameter_strings = ""
        parameter_members = ""
        create_params = ""
        for component in walk(components):
            if isinstance(component, Group):
                title = f"/* Group: {component.name} */\n"
                parameter_strings += title
                parameter_members += title
                create_params += title
            elif isinstance(component, AsynParameter):
                parameter_strings += (
                    f'#define {component.name}String "{component.name.upper()}"'
                    f" /* {component.type} {component.role.value} */\n"
                )
                parameter_members += f"    int {component.name};\n"
                param_type = component.asyn_parameter_info().asyn_param_type
                create_params += (
                    f"    parent->createParam({component.name}String, "
                    f"{param_type}, &{component.name});"
                )
        h_txt = f"""\
#ifndef {basename.upper()}_PARAMETERS_H
#define {basename.upper()}_PARAMETERS_H

/* Strings defining the parameter interface with the Database */
{parameter_strings.rstrip()}

/* Class definition */
class {basename.title()}Parameters {{
public:
    {basename.title()}Parameters(asynPortDriver *parent);
    /* Parameters */
    {parameter_members.rstrip()}
}}

#endif //{basename.upper()}_PARAMETERS_H
"""
        cpp_txt = f"""\
{basename.title()}Parameters::{basename.title()}Parameters(asynPortDriver *parent) {{
    {create_params.rstrip()}
}}
"""
        outputs = {
            basename + "_parameters.h": h_txt,
            basename + "_parameters.cpp": cpp_txt,
        }
        return outputs
