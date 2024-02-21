import re
from typing import Any, ClassVar, List, Optional, Type, cast

from pydantic import Field

from pvi._schema_utils import rec_subclasses
from pvi.device import (
    LED,
    ComboBox,
    Named,
    ReadWidgetUnion,
    TextFormat,
    TextRead,
    TextWrite,
    ToggleButton,
    WriteWidgetUnion,
)

from ._parameters import Record, TypeStrings


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

    def asyn_component_type(self) -> Type["AsynParameter"]:
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
                f"{self.pv} asyn type {self.type}({self.fields}) not found in"
                f"{list(record_types)}"
            ) from e

        raise ValueError(
            f"Could not determine asyn type for {self.pv} fields {self.fields}"
        )


class AsynParameter(Named):
    """Base class for all Asyn Parameters to inherit from"""

    type_strings: ClassVar[TypeStrings]
    read_record: AsynRecord | None = Field(
        default=None,
        description="A read AsynRecord, if not given then use $(name)_RBV as read PV",
    )
    write_record: AsynRecord | None = Field(
        default=None,
        description="A write AsynRecord, if not given then use $(name) as write PV",
    )
    read_widget: ReadWidgetUnion = Field(default=TextRead())
    write_widget: WriteWidgetUnion = Field(default=TextWrite())

    def get_read_pv(self) -> str:
        if self.read_record:
            return self.read_record.pv
        else:
            return self.name + "_RBV"

    def get_write_pv(self) -> str:
        if self.write_record:
            return self.write_record.pv
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
    write_widget: WriteWidgetUnion = Field(ToggleButton())

    def model_post_init(self, __context: Any) -> None:
        if self.write_record is not None:
            if not all(f in self.write_record.fields for f in ("ZNAM", "ONAM")):
                print(
                    f"WARNING: ZNAM/ONAM not set for {self.write_record.pv}. "
                    "Button labels will be blank."
                )


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
