from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from pvi._utils import as_discriminated_union
from pvi.device import Component, Tree


class Access(str, Enum):
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


class DisplayForm(str, Enum):
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


@as_discriminated_union
@dataclass
class Producer:
    def produce_components(self) -> Tree[Component]:
        """Make signals from components"""
        raise NotImplementedError(self)

    def produce_csv(self, path: Path):
        """Make docs csv table"""
        raise NotImplementedError(self)

    def produce_records(self, path: Path):
        """Make epicsdbbuilder records"""
        raise NotImplementedError(self)

    def produce_other(self, path: Path):
        """Make things like cpp, h files"""
        raise NotImplementedError(self)
