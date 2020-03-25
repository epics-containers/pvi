from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Union, cast

from pydantic import Field

from pvi._types import Channel, DisplayForm, Widget

from ._types import (
    ChannelTree,
    Component,
    ComponentTree,
    Group,
    Producer,
    Record,
    RecordTree,
)
from ._util import camel_to_title, truncate_description, walk

VALUE_FIELD = Field(None, description="The initial value of the parameter")


@dataclass
class AsynParameterInfo:
    asyn_param_type: str  #: Asyn parameter type, e.g. asynParamFloat64
    read_record_type: str  #: RTYP of the read record, e.g. ai
    write_record_type: str  #: RTYP of the write record, e.g. ao
    read_record_fields: Dict[str, str]  #: Fields to add to the read record
    write_record_fields: Dict[str, str]  #: Fields to add to the write record


class ParameterRole(Enum):
    SETTING = "Setting"  #: Write record that syncs with readback values
    SETTING_PAIR = "Setting Pair"  #: Read and write records
    ACTION = "Action"  #: Write record only
    READBACK = "Readback"  #: Read record only
    ACTION_READBACK = "Action + Readback"  #: Write record current value readback

    def needs_read_record(self):
        return self not in [self.ACTION, self.SETTING]

    def needs_write_record(self):
        return self != self.READBACK


class ScanRate(Enum):
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
    read_widget: Widget = Field(
        Widget.TEXTUPDATE,
        description="Override the widget to use for read-only channels",
    )
    write_widget: Widget = Field(
        Widget.TEXTINPUT,
        description="Override the widget to use for writeable channels",
    )
    display_form: DisplayForm = Field(
        None, description="Display form for numeric fields"
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

    def _read_record_name(self, component: AsynParameter) -> str:
        if component.read_record_suffix:
            return self.prefix + component.read_record_suffix
        else:
            return self.prefix + component.name + "_RBV"

    def _make_read_record(self, component: AsynParameter) -> Record:
        info = component.asyn_parameter_info()
        fields = dict(
            SCAN=component.read_record_scan.value,
            **self._make_common_record_fields(component, "INP"),
            **info.read_record_fields,
        )
        return Record(
            record_name=self._read_record_name(component),
            record_type=info.read_record_type,
            fields=fields,
            infos={},
        )

    def _write_record_name(self, component: AsynParameter) -> str:
        if component.write_record_suffix:
            return self.prefix + component.write_record_suffix
        else:
            return self.prefix + component.name

    def _make_write_record(self, component: AsynParameter) -> Record:
        info = component.asyn_parameter_info()
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
            record_name=self._write_record_name(component),
            record_type=info.write_record_type,
            fields=fields,
            infos=infos,
        )

    def produce_records(self, components: ComponentTree) -> RecordTree:
        records: List[Union[Record, Group]] = []
        for component in components:
            if isinstance(component, Group):
                group: Group[Record] = Group(
                    name=component.name,
                    children=self.produce_records(component.children),
                )
                records.append(group)
            elif isinstance(component, AsynParameter):
                if component.role.needs_read_record():
                    records.append(self._make_read_record(component))
                if component.role.needs_write_record():
                    records.append(self._make_write_record(component))
        return records

    def produce_channels(self, components: ComponentTree) -> ChannelTree:
        channels: List[Union[Channel, Group]] = []
        for component in components:
            if isinstance(component, Group):
                group: Group[Channel] = Group(
                    name=component.name,
                    children=self.produce_channels(component.children),
                )
                channels.append(group)
            elif isinstance(component, AsynParameter):
                # Make the primary channel
                channel = Channel(
                    name=component.name,
                    label=camel_to_title(component.name),
                    description=component.description,
                    display_form=component.display_form,
                )
                # Add read pv
                if component.role == ParameterRole.ACTION_READBACK:
                    # readback is a separate channel
                    read_name = component.name + "Readback"
                    read_channel = Channel(
                        name=read_name,
                        label=camel_to_title(read_name),
                        description=component.description,
                        display_form=component.display_form,
                        read_pv=self._read_record_name(component),
                    )
                    channels.append(read_channel)
                elif component.role == ParameterRole.SETTING:
                    # write record is also a read record
                    channel.read_pv = channel.write_pv
                elif component.role.needs_read_record():
                    channel.read_pv = self._read_record_name(component)
                    channel.widget = component.read_widget
                # Add write pv
                if component.role.needs_write_record():
                    channel.write_pv = self._write_record_name(component)
                    # Write widget trumps read widget
                    channel.widget = component.write_widget
                channels.append(channel)

        return cast(ChannelTree, channels)

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
