from enum import Enum
from typing import Any, ClassVar, Dict, List, Union

from pydantic import BaseModel, Field

from pvi._types import Channel, DisplayForm, Widget

from ._records import (
    AnalogueCommon,
    AnalogueIn,
    AnalogueOut,
    BinaryCommon,
    BinaryIn,
    BinaryOut,
    LongCommon,
    LongIn,
    LongOut,
    MultiBitBinaryCommon,
    MultiBitBinaryIn,
    MultiBitBinaryOut,
    StringCommon,
    StringIn,
    StringOut,
    WaveformCommon,
    WaveformIn,
    WaveformOut,
)
from ._types import AsynParameter, Component, Producer, Record, Tree
from ._util import camel_to_title, truncate_description

VALUE_FIELD = Field(None, description="The initial value of the parameter")
RecordCommonUnion = Union[
    AnalogueCommon,
    BinaryCommon,
    LongCommon,
    MultiBitBinaryCommon,
    StringCommon,
    WaveformCommon,
]
RecordInUnion = Union[
    AnalogueIn, BinaryIn, LongIn, MultiBitBinaryIn, StringIn, WaveformIn,
]
RecordOutUnion = Union[
    AnalogueOut, BinaryOut, LongOut, MultiBitBinaryOut, StringOut, WaveformOut,
]


class AsynComponentType(BaseModel):
    inp: str = Field(..., description="e.g. ai, bi, longin")
    out: str = Field(..., description="e.g. ao, bo, longout")
    asyn_read_type: str = Field(..., description="e.g. asynInt32, asynOctetRead")
    asyn_write_type: str = Field(..., description="e.g. asynInt32, asynOctetWrite")
    asyn_param_type: str = Field(..., description="e.g. asynParamInt32, asynParamOctet")


class AsynInfo(BaseModel):
    asyn_param_type: str = Field(
        ..., description="Asyn parameter type, e.g. asynParamFloat64"
    )
    read_record_type: str = Field(..., description="RTYP of the read record, e.g. ai")
    write_record_type: str = Field(..., description="RTYP of the write record, e.g. ao")
    read_record_fields: Dict[str, str] = Field(
        ..., description="Fields to add to the read record"
    )
    write_record_fields: Dict[str, str] = Field(
        ..., description="Fields to add to the write record"
    )


class ParameterRole(str, Enum):
    """What role does this parameter play within the device. One of:

    - Readback: a parameter of the device that can be read from.
      E.g. chipTemperature on a detector, or isHomed for a motor
    - Action: a parameter of the device that can be written to, but there
      is no current value.
      E.g. reboot on a detector, or overwriteCurrentPosition for a motor
    - Setting: a parameter of the device that can be written to, the
      current value can be read from, and should be saved/loaded when
      switching between configurations of the device.
      E.g. acquireTime on a detector, or velocity of a motor
    - Transient: a parameter of the device that can be written to and
      read from, but should not be saved/loaded when switching between
      configurations of the device.
      E.g. arrayCounter on a detector, or position of a motor
    """

    READBACK = "Readback"  #: Read record only
    ACTION = "Action"  #: Write record only
    SETTING = "Setting"  #: Read and write record, for saving
    TRANSIENT = "Transient"  #: Read and write record, not for saving

    def needs_read_record(self):
        return self != self.ACTION

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


class AsynComponent(Component):
    """Base class for all Asyn Parameters to inherit from"""

    description: str = Field(
        ..., description="Description of what this Parameter is for"
    )
    role: ParameterRole = Field(
        ParameterRole.SETTING, description=ParameterRole.__doc__,
    )
    demand_auto_updates: bool = Field(
        False, description="Should demand update when readback changes?"
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
        None, description="Display form for numeric/array fields"
    )
    asyn_component_type: ClassVar[AsynComponentType]
    initial: Any
    common_fields: Any = None
    read_fields: Any = None
    write_fields: Any = None

    def asyn_parameter_info(self) -> AsynInfo:
        read_fields = {
            **dict(DTYP=self.asyn_component_type.asyn_read_type),
            **self.common_fields.dict(exclude_none=True),
            **self.read_fields.dict(exclude_none=True),
        }
        write_fields = {
            **dict(DTYP=self.asyn_component_type.asyn_write_type),
            **self.common_fields.dict(exclude_none=True),
            **self.write_fields.dict(exclude_none=True),
        }
        info = AsynInfo(
            read_record_type=self.asyn_component_type.inp,
            read_record_fields=read_fields,
            write_record_type=self.asyn_component_type.out,
            write_record_fields=write_fields,
            asyn_param_type=self.asyn_component_type.asyn_param_type,
        )
        return info


class AsynBinary(AsynComponent):
    """Asyn Float32 Parameter and records"""

    asyn_component_type: ClassVar[AsynComponentType] = AsynComponentType(
        inp="bi",
        out="bo",
        asyn_read_type="asynInt32",
        asyn_write_type="asynInt32",
        asyn_param_type="asynParamInt32",
    )
    initial: int = Field(
        None, ge=0, le=1, description="The initial value of the parameter"
    )
    common_fields: BinaryCommon = Field(BinaryCommon(), description="Optional common")
    read_fields: BinaryIn = Field(BinaryIn(), description="Optional read fields")
    write_fields: BinaryOut = Field(BinaryOut(), description="Optional write fields")


class AsynBusy(AsynComponent):
    """Asyn busy Parameter and records"""

    asyn_component_type: ClassVar[AsynComponentType] = AsynComponentType(
        inp="bi",
        out="busy",
        asyn_read_type="asynInt32",
        asyn_write_type="asynInt32",
        asyn_param_type="asynParamInt32",
    )
    initial: int = Field(
        None, ge=0, le=1, description="The initial value of the parameter"
    )
    common_fields: BinaryCommon = Field(BinaryCommon(), description="Optional common")
    read_fields: BinaryIn = Field(BinaryIn(), description="Optional read fields")
    write_fields: BinaryOut = Field(BinaryOut(), description="Optional write fields")


class AsynFloat64(AsynComponent):
    """Asyn Float64 Parameter and records"""

    asyn_component_type: ClassVar[AsynComponentType] = AsynComponentType(
        inp="ai",
        out="ao",
        asyn_read_type="asynFloat64",
        asyn_write_type="asynFloat64",
        asyn_param_type="asynParamFloat64",
    )
    initial: float = VALUE_FIELD
    common_fields: AnalogueCommon = Field(
        AnalogueCommon(), description="Optional common"
    )
    read_fields: AnalogueIn = Field(AnalogueIn(), description="Optional read fields")
    write_fields: AnalogueOut = Field(
        AnalogueOut(), description="Optional write fields"
    )


class AsynInt32(AsynComponent):
    """Asyn Int32 Parameter and records"""

    asyn_component_type: ClassVar[AsynComponentType] = AsynComponentType(
        inp="ai",
        out="ao",
        asyn_read_type="asynInt32",
        asyn_write_type="asynInt32",
        asyn_param_type="asynParamInt32",
    )
    initial: int = VALUE_FIELD
    common_fields: AnalogueCommon = Field(
        AnalogueCommon(), description="Optional common"
    )
    read_fields: AnalogueIn = Field(AnalogueIn(), description="Optional read fields")
    write_fields: AnalogueOut = Field(
        AnalogueOut(), description="Optional write fields"
    )


class AsynLong(AsynComponent):
    """Asyn Long Parameter and records"""

    asyn_component_type: ClassVar[AsynComponentType] = AsynComponentType(
        inp="longin",
        out="longout",
        asyn_read_type="asynInt32",
        asyn_write_type="asynInt32",
        asyn_param_type="asynParamInt32",
    )
    initial: int = VALUE_FIELD
    common_fields: LongCommon = Field(LongCommon(), description="Optional common")
    read_fields: LongIn = Field(LongIn(), description="Optional read fields")
    write_fields: LongOut = Field(LongOut(), description="Optional write fields")


class AsynMultiBitBinary(AsynComponent):
    """Asyn MultiBitBinary Parameter and records"""

    asyn_component_type: ClassVar[AsynComponentType] = AsynComponentType(
        inp="mbbi",
        out="mbbo",
        asyn_read_type="asynInt32",
        asyn_write_type="asynInt32",
        asyn_param_type="asynParamInt32",
    )
    initial: int = Field(
        None, ge=0, le=15, description="The initial value of the parameter"
    )
    common_fields: MultiBitBinaryCommon = Field(
        MultiBitBinaryCommon(), description="Optional common"
    )
    read_fields: MultiBitBinaryIn = Field(
        MultiBitBinaryIn(), description="Optional read fields"
    )
    write_fields: MultiBitBinaryOut = Field(
        MultiBitBinaryOut(), description="Optional write fields"
    )


class AsynString(AsynComponent):
    """Asyn String Parameter and records"""

    asyn_component_type: ClassVar[AsynComponentType] = AsynComponentType(
        inp="stringin",
        out="stringout",
        asyn_read_type="asynOctetRead",
        asyn_write_type="asynOctetWrite",
        asyn_param_type="asynParamOctet",
    )
    initial: str = VALUE_FIELD
    common_fields: StringCommon = Field(StringCommon(), description="Optional common")
    read_fields: StringIn = Field(StringIn(), description="Optional read fields")
    write_fields: StringOut = Field(StringOut(), description="Optional write fields")


class AsynWaveform(AsynComponent):
    """Asyn Waveform Parameter and records"""

    asyn_component_type: ClassVar[AsynComponentType] = AsynComponentType(
        inp="waveform",
        out="waveform",
        asyn_read_type="asynOctetRead",
        asyn_write_type="asynOctetWrite",
        asyn_param_type="asynParamOctet",
    )
    common_fields: WaveformCommon = Field(
        WaveformCommon(), description="Optional common"
    )
    read_fields: WaveformIn = Field(WaveformIn(), description="Optional read fields")
    write_fields: WaveformOut = Field(
        WaveformOut(), description="Optional write fields"
    )


class AsynProducer(Producer):
    prefix: str = Field(
        ..., description="The prefix for record names created by the template file"
    )
    asyn_port: str = Field(..., description="The asyn port name")
    address: str = Field(..., description="The asyn address")
    timeout: str = Field(..., description="The timeout for the asyn port")

    def _read_record_name(self, component: AsynComponent) -> str:
        if component.read_record_suffix:
            return self.prefix + component.read_record_suffix
        else:
            return self.prefix + component.name + "_RBV"

    def _write_record_name(self, component: AsynComponent) -> str:
        if component.write_record_suffix:
            return self.prefix + component.write_record_suffix
        else:
            return self.prefix + component.name

    def _make_records(self, component: AsynComponent) -> List[Record]:
        records = []
        info = component.asyn_parameter_info()
        io = f"@asyn({self.asyn_port},{self.address},{self.timeout}){component.name}"
        if component.role.needs_read_record():
            fields = dict(
                SCAN=component.read_record_scan.value,
                DESC=truncate_description(component.description),
                INP=io,
                **info.read_record_fields,
            )
            records.append(
                Record(
                    name=self._read_record_name(component),
                    type=info.read_record_type,
                    fields=fields,
                    infos={},
                )
            )
        if component.role.needs_write_record():
            fields = dict(
                DESC=truncate_description(component.description),
                **info.write_record_fields,
            )
            if info.write_record_type == "waveform":
                fields["INP"] = io
            else:
                fields["OUT"] = io
            if component.initial is not None:
                fields["PINI"] = "YES"
                fields["VAL"] = str(component.initial)
            infos = {}
            if component.autosave:
                infos["autosaveFields"] = " ".join(component.autosave)
            if component.demand_auto_updates:
                infos["asyn:READBACK"] = "1"
            records.append(
                Record(
                    name=self._write_record_name(component),
                    type=info.write_record_type,
                    fields=fields,
                    infos=infos,
                )
            )
        return records

    def produce_records(self, components: Tree[Component]) -> Tree[Record]:
        return AsynComponent.on_each_node(components, self._make_records)

    def _make_channels(self, component: AsynComponent) -> List[Channel]:
        channels = []
        # Make the primary channel
        channel = Channel(
            name=component.name,
            label=camel_to_title(component.name),
            description=component.description,
            display_form=component.display_form,
        )
        # Add read pv
        if component.role == ParameterRole.TRANSIENT:
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
        elif component.role.needs_read_record():
            channel.read_pv = self._read_record_name(component)
            channel.widget = component.read_widget
        # Add write pv
        if component.role.needs_write_record():
            channel.write_pv = self._write_record_name(component)
            # Write widget trumps read widget
            channel.widget = component.write_widget
        channels.append(channel)
        return channels

    def produce_channels(self, components: Tree[Component]) -> Tree[Channel]:
        return AsynComponent.on_each_node(components, self._make_channels)

    def _make_asyn_parameters(self, component: AsynComponent) -> List[AsynParameter]:
        parameter = AsynParameter(
            name=component.name,
            type=component.asyn_parameter_info().asyn_param_type,
            description=component.role.value,
        )
        return [parameter]

    def produce_asyn_parameters(
        self, components: Tree[Component]
    ) -> Tree[AsynParameter]:
        return AsynComponent.on_each_node(components, self._make_asyn_parameters)
