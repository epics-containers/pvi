"""The types that should be inherited from or produced by Fields"""

from enum import Enum
from typing import Iterator, List, Dict

from pydantic import BaseModel, Field
from dataclasses import dataclass


class ChannelRole(str, Enum):
    """Does Channel describe a readback, setpoint or both"""

    READ = "READ"  #: Read-only
    WRITE = "WRITE"  #: Write-only
    SETTING = "SETTING"  #: Readable and writeable
    POSITIONER = "POSITIONER"  #: Like the position of a motor


@dataclass
class Record:
    record_type: str  #: The record type string e.g. ao, stringin
    suffix: str  #: Record name is Producer prefix plus this suffix
    fields: Dict[str, str]  #: The record fields
    infos: Dict[str, str]  #: Any infos to be added to the record


class WithTypeMetaClass(type(BaseModel)):
    def __new__(mcs, name, bases, namespace, **kwargs):
        # Override type in namespace to be the literal value of the class name
        namespace["type"] = Field(name, const=True)
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class WithType(BaseModel, metaclass=WithTypeMetaClass):
    """BaseModel that adds a type parameter from class name"""

    type: str

