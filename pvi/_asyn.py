from typing import Dict, List, Tuple
from dataclasses import dataclass

from pydantic import Field, BaseModel

from ._types import ChannelRole, WithType, Record
from ._util import truncate_description


VALUE_FIELD = Field(None, description="The initial value of the parameter")


@dataclass
class RecordInfo:
    record_type: str  #: What is the RTYP of the Record
    fields: Dict[str, str]  #: Fields passed straight through


class AsynParameter(WithType):
    """Base class for all Asyn Parameters to inherit from"""
    name: str = Field(
        ..., description="Name of the created Channel within the Device",
    )
    description: str = Field(..., description="Description of what this Channel is for")
    role: ChannelRole = Field(
        ChannelRole.SETTING, description=ChannelRole.__doc__,
    )
    autosave: List[str] = Field(
        [], description="Record fields that should be autosaved"
    )
    auto_update: bool = Field(
        False,
        description="If set then create a single record for both demand and readback",
    )

    def record_info(self) -> Tuple[RecordInfo, Record]:
        """Return (InRecordInfo, OutRecordInfo)"""
        raise NotImplementedError(self)


class AsynString(AsynParameter):
    """Asyn String Parameter and records"""

    value: str = VALUE_FIELD

    def record_info(self) -> RecordInfo:
        in_info = RecordInfo("stringin", dict(DTYP="asynOctetRead"))
        out_info = RecordInfo("stringout", dict(DTYP="asynOctetWrite"))
        return (in_info, out_info)


class AsynFloat64(AsynParameter):
    """Asyn Float64 Parameter and records"""

    value: float = VALUE_FIELD
    precision: int = Field(3, description="Record precision")
    units: str = Field("", description="Record engineering units")

    def record_info(self) -> RecordInfo:
        fields = dict(DTYP="asynFloat64", EGU=self.units, PREC=self.precision)
        in_info = RecordInfo("ai", fields)
        out_info = RecordInfo("ao", fields)
        return (in_info, out_info)


class AsynProducer(WithType):
    pass
