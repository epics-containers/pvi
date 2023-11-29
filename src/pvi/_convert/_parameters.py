from enum import Enum
from typing import ClassVar, Dict, List, Optional, Type, cast

from pydantic import BaseModel, Field

from pvi._schema_utils import rec_subclasses
from pvi.device import (
    LED,
    CheckBox,
    ComboBox,
    ComponentUnion,
    Named,
    ReadWidgetUnion,
    TextFormat,
    TextRead,
    TextWrite,
    WriteWidgetUnion,
)


class TypeStrings(BaseModel):
    """The type strings for record dtypes and parameter names"""

    asyn_read: str = Field(description="e.g. asynInt32, asynOctetRead")
    asyn_write: str = Field(description="e.g. asynInt32, asynOctetWrite")
    asyn_param: str = Field(description="e.g. asynParamInt32, asynParamOctet")


class Access(Enum):
    """What access does the user have. One of:

    - R: Read only value that cannot be set. E.g. chipTemperature on a detector,
      or isHomed for a motor
    - W: Write only value that can be written to, but there is no current value.
      E.g. reboot on a detector, or overwriteCurrentPosition for a motor
    - RW: Read and Write value that can be written to and read back.
      E.g. acquireTime on a detector, or velocity of a motor
    """

    R = "R"  #: Read record only
    W = "W"  #: Write record only
    RW = "RW"  #: Read and write record

    def needs_read_record(self):
        return self != self.W

    def needs_write_record(self):
        return self != self.R


class DisplayForm(Enum):
    """Instructions for how a number should be formatted for display"""

    #: Use the default representation from value
    DEFAULT = "Default"
    #: Force string representation, most useful for array of bytes
    STRING = "String"
    #: Binary, precision determines number of binary digits
    BINARY = "Binary"
    #: Decimal, precision determines number of digits after decimal point
    DECIMAL = "Decimal"
    #: Hexadecimal, precision determines number of hex digits
    HEX = "Hex"
    #: Exponential, precision determines number of digits after decimal point
    EXPONENTIAL = "Exponential"
    #: Exponential where exponent is multiple of 3, precision determines number of
    #: digits after decimal point
    ENGINEERING = "Engineering"


class AsynParameter(Named):
    """Base class for all Asyn Parameters to inherit from"""

    type_strings: ClassVar[TypeStrings]
    read_record: Optional[str] = Field(
        default=None,
        description="The full read record, if not given then use $(name)_RBV",
    )
    write_record: Optional[str] = Field(
        default=None, description="The full write record, if not given then use $(name)"
    )
    display_form: Optional[DisplayForm] = Field(
        default=None, description="Display form for numeric/array fields"
    )
    read_widget: Optional[ReadWidgetUnion] = None
    write_widget: Optional[WriteWidgetUnion] = None

    def get_read_record(self) -> str:
        if self.read_record:
            return self.read_record
        else:
            return self.name + "_RBV"

    def get_write_record(self) -> str:
        if self.write_record:
            return self.write_record
        else:
            return self.name


class AsynBinary(AsynParameter):
    """Asyn Binary Parameter and records"""

    type_strings = TypeStrings(
        asyn_read="asynInt32",
        asyn_write="asynInt32",
        asyn_param="asynParamInt32",
    )
    read_widget: ReadWidgetUnion = Field(LED())
    write_widget: WriteWidgetUnion = Field(CheckBox())


class AsynBusy(AsynBinary):
    """Asyn Busy Parameter and records"""


class AsynFloat64(AsynParameter):
    """Asyn Float64 Parameter and records"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynFloat64",
        asyn_write="asynFloat64",
        asyn_param="asynParamFloat64",
    )
    read_widget: ReadWidgetUnion = Field(default=TextRead())
    write_widget: WriteWidgetUnion = Field(default=TextWrite())


class AsynInt32(AsynParameter):
    """Asyn Int32 Parameter and records"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynInt32",
        asyn_write="asynInt32",
        asyn_param="asynParamInt32",
    )
    read_widget: ReadWidgetUnion = Field(default=TextRead())
    write_widget: WriteWidgetUnion = Field(default=TextWrite())


class AsynLong(AsynInt32):
    """Asyn Long Parameter and records"""


class AsynMultiBitBinary(AsynParameter):
    """Asyn MultiBitBinary Parameter and records"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynInt32",
        asyn_write="asynInt32",
        asyn_param="asynParamInt32",
    )
    read_widget: ReadWidgetUnion = Field(TextRead())
    write_widget: WriteWidgetUnion = Field(ComboBox())


class AsynString(AsynParameter):
    """Asyn String Parameter and records"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynOctetRead",
        asyn_write="asynOctetWrite",
        asyn_param="asynParamOctet",
    )
    read_widget: ReadWidgetUnion = Field(TextRead())
    write_widget: WriteWidgetUnion = Field(TextWrite())


InRecordTypes = {
    "ai": AsynFloat64,
    "bi": AsynBinary,
    "longin": AsynLong,
    "mbbi": AsynMultiBitBinary,
    "stringin": AsynString,
}


OutRecordTypes = {
    "ao": AsynFloat64,
    "bo": AsynBinary,
    "busy": AsynBusy,
    "longout": AsynLong,
    "mbbo": AsynMultiBitBinary,
    "stringout": AsynString,
}


class AsynWaveform(AsynParameter):
    """Asyn Waveform Parameter and records"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynOctetRead",
        asyn_write="asynOctetWrite",
        asyn_param="asynParamOctet",
    )
    read_widget: ReadWidgetUnion = Field(TextRead(format=TextFormat.string))
    write_widget: WriteWidgetUnion = Field(TextWrite(format=TextFormat.string))


class AsynInt32Waveform(AsynWaveform):
    """Asyn Waveform Parameter and records with int32 array elements"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynInt32ArrayIn",
        asyn_write="asynInt32ArrayOut",
        asyn_param="asynParamInt32",
    )
    read_widget: ReadWidgetUnion = Field(TextRead())
    write_widget: WriteWidgetUnion = Field(TextWrite())


class AsynFloat64Waveform(AsynWaveform):
    """Asyn Waveform Parameter and records with float64 array elements"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynFloat64ArrayIn",
        asyn_write="asynFloat64ArrayOut",
        asyn_param="asynParamFloat64",
    )
    read_widget: ReadWidgetUnion = Field(TextRead())
    write_widget: WriteWidgetUnion = Field(TextWrite())


WaveformRecordTypes = [AsynWaveform] + cast(
    List[Type[AsynWaveform]], rec_subclasses(AsynWaveform)
)


def get_waveform_parameter(dtyp: str):
    for waveform_cls in WaveformRecordTypes:
        if dtyp in (
            waveform_cls.type_strings.asyn_read,
            waveform_cls.type_strings.asyn_write,
        ):
            return waveform_cls

    assert False, f"Waveform type for DTYP {dtyp} not found in {WaveformRecordTypes}"


class Record(BaseModel):
    name: str  # The name of the record e.g. $(P)$(M)Status
    type: str  # The record type string e.g. ao, stringin
    fields: Dict[str, str]  # The record fields
    infos: Dict[str, str]  # Any infos to be added to the record


class Parameter(BaseModel):
    """Base class representing an Asyn parameter"""

    invalid: list[str] = ["DESC", "DTYP", "INP", "OUT", "PINI", "VAL"]

    def _remove_invalid(self, fields: Dict[str, str]) -> Dict[str, str]:
        valid_fields = {
            key: value for (key, value) in fields.items() if key not in self.invalid
        }
        return valid_fields

    def generate_component(self) -> ComponentUnion:
        raise NotImplementedError(self)


class ReadParameterMixin:
    def _get_read_record(self) -> Optional[str]:
        raise NotImplementedError(self)
