import re
from enum import Enum
from functools import cached_property
from typing import Annotated

from pydantic import BaseModel, Field

from pvi.device import ComponentUnion


class TypeStrings(BaseModel):
    """The type strings for record dtypes and parameter names"""

    asyn_read: Annotated[str, Field(description="e.g. asynInt32, asynOctetRead")]
    asyn_write: Annotated[str, Field(description="e.g. asynInt32, asynOctetWrite")]
    asyn_param: Annotated[str, Field(description="e.g. asynParamInt32, asynParamOctet")]


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


MACRO_RE = re.compile(r"\$\(.*\)")


class Record(BaseModel):
    pv: str  # The pv of the record e.g. $(P)$(M)Status
    type: str  # The record type string e.g. ao, stringin
    fields: dict[str, str]  # The record fields
    infos: dict[str, str]  # Any infos to be added to the record

    @cached_property
    def name(self) -> str:
        """Return pv with macros removed to use as label on UIs."""
        return re.sub(MACRO_RE, "", self.pv)


class Parameter(BaseModel):
    """Base class representing an Asyn parameter"""

    invalid: list[str] = ["DESC", "DTYP", "INP", "OUT", "PINI", "VAL"]

    def _remove_invalid(self, fields: dict[str, str]) -> dict[str, str]:
        valid_fields = {
            key: value for (key, value) in fields.items() if key not in self.invalid
        }
        return valid_fields

    def generate_component(self) -> ComponentUnion:
        raise NotImplementedError(self)


class ReadParameterMixin:
    def _get_read_record(self) -> str | None:
        raise NotImplementedError(self)
