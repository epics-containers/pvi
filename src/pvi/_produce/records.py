from __future__ import annotations

import dataclasses
from ctypes import POINTER, c_char_p, c_int, c_void_p, pointer
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Tuple, Type, Union, get_type_hints

from apischema import serialize
from epicsdbbuilder import dbd, mydbstatic, records
from epicsdbbuilder.recordbase import Record
from typing_extensions import Annotated

from pvi._schema_utils import desc

# Add DBDs
dbd.InitialiseDbd()
for submodule_dbd in [
    # "asyn/asyn/devEpics/asynCalc.dbd",
    "asyn/asyn/devEpics/devAsynFloat32Array.dbd",
    "asyn/asyn/devEpics/devAsynFloat64.dbd",
    "asyn/asyn/devEpics/devAsynFloat64Array.dbd",
    "asyn/asyn/devEpics/devAsynFloat64TimeSeries.dbd",
    "asyn/asyn/devEpics/devAsynInt16Array.dbd",
    "asyn/asyn/devEpics/devAsynInt32.dbd",
    "asyn/asyn/devEpics/devAsynInt32Array.dbd",
    "asyn/asyn/devEpics/devAsynInt32TimeSeries.dbd",
    "asyn/asyn/devEpics/devAsynInt64.dbd",
    "asyn/asyn/devEpics/devAsynInt64Array.dbd",
    "asyn/asyn/devEpics/devAsynInt64Misc.dbd",
    "asyn/asyn/devEpics/devAsynInt64TimeSeries.dbd",
    "asyn/asyn/devEpics/devAsynInt8Array.dbd",
    "asyn/asyn/devEpics/devAsynOctet.dbd",
    "asyn/asyn/devEpics/devAsynOctetLs.dbd",
    "asyn/asyn/devEpics/devAsynUInt32Digital.dbd",
    "copyInfo/copyInfoApp/src/devCopyInfo.dbd",
    "busy/busyApp/src/busyRecord.dbd",
    # "busy/busyApp/src/busySupport_LOCAL.dbd",
    "busy/busyApp/src/busySupport_withASYN.dbd",
    # "busy/busyApp/src/testBusyAsynInclude.dbd",
]:
    dbd.LoadDbdFile(Path(__file__).parent.parent / "submodules" / submodule_dbd)


# https://code.activestate.com/recipes/576731-c-function-decorator/
class DbFunction:
    """This class wraps a Python function into its C equivalent in the given library"""

    def __init__(self, error_check=None):
        """Set the library to reference the function name against."""
        self.error_check = error_check

    def __call__(self, f):
        """Performs the actual function wrapping."""

        class PointerFactory:
            def __getitem__(self, key):
                """Return a pointer to the type, used in get_type_hints below"""
                # https://github.com/python/mypy/issues/7540
                return POINTER(key)

        # Get the type hints, redirecting pointer[something] to PointerFactory
        hints = get_type_hints(f, localns=dict(pointer=PointerFactory()))

        # Return the function with argtypes etc. described by the type hints
        return mydbstatic.GetDbFunction(
            f.__name__,
            argtypes=[v for x, v in hints.items() if x != "return"],
            restype=hints.get("return"),
            errcheck=self.error_check,
        )


@DbFunction()
def dbGetFieldDbfType(pdbentry: c_void_p) -> c_int:
    ...


@DbFunction(mydbstatic.auto_decode)
def dbGetFieldTypeString(dbfType: c_int) -> c_char_p:
    ...


@DbFunction(mydbstatic.auto_decode)
def dbGetDefault(pdbentry: c_void_p) -> c_char_p:
    ...


@DbFunction(mydbstatic.auto_decode)
def dbGetPrompt(pdbentry: c_void_p) -> c_char_p:
    ...


@DbFunction()
def dbGetNMenuChoices(pdbentry: c_void_p) -> c_int:
    ...


@DbFunction()
def dbGetMenuChoices(pdbentry: c_void_p) -> pointer[c_char_p]:
    ...


DBF_TYPE_MAP = dict(
    DBF_STRING=str,
    DBF_CHAR=int,
    DBF_UCHAR=int,
    DBF_SHORT=int,
    DBF_USHORT=int,
    DBF_LONG=int,
    DBF_ULONG=int,
    DBF_INT64=int,
    DBF_UINT64=int,
    DBF_FLOAT=float,
    DBF_DOUBLE=float,
    DBF_ENUM=str,
    DBF_MENU=Enum,
    DBF_DEVICE=str,
    DBF_INLINK=str,
    DBF_OUTLINK=str,
    DBF_FWDLINK=str,
    DBF_NOACCESS=None,
)

FieldList = List[Tuple[str, Type, dataclasses.Field]]


def make_fields(entry: dbd.DBEntry, record_type: str) -> FieldList:
    fields: FieldList = []
    for field_name in entry.iterate_fields():
        default = dbGetDefault(entry)
        prompt = dbGetPrompt(entry)
        field_type = DBF_TYPE_MAP[dbGetFieldTypeString(dbGetFieldDbfType(entry))]
        if field_type is Enum:
            # Make a custom enum type from the menu choices
            choices = dbGetMenuChoices(entry)
            str_choices = [choices[i].decode() for i in range(dbGetNMenuChoices(entry))]
            enum_name = record_type + field_name
            field_type = Enum(enum_name, [(c, c) for c in str_choices])  # type: ignore
        if field_type:
            fields.append(
                (
                    field_name,
                    Annotated[Union[field_type, str], desc(prompt)],
                    dataclasses.field(default=default),
                )
            )
    return fields


def make_fields_dict() -> Dict[str, FieldList]:
    fields_dict: Dict[str, FieldList] = {}
    entry = dbd.DBEntry()
    for record_type in entry.iterate_records():
        fields_dict[record_type] = make_fields(entry, record_type)
    return fields_dict


fields_dict = make_fields_dict()


class RecordPair:
    in_record_type: ClassVar[Type]
    out_record_type: ClassVar[Type]

    @classmethod
    def for_record_types(cls, in_str: str, out_str: str) -> Type[RecordPair]:
        in_record_type = dataclasses.make_dataclass(in_str, fields_dict[in_str])
        out_record_type = dataclasses.make_dataclass(out_str, fields_dict[out_str])
        namespace = dict(in_record_type=in_record_type, out_record_type=out_record_type)

        # Create combined record type for the record pair subclass
        in_fields = dict((a, (b, c)) for a, b, c, in fields_dict[in_str])
        in_fields.update(dict((a, (b, c)) for a, b, c, in fields_dict[out_str]))
        all_fields = [(a, b, c) for [a, (b, c)] in in_fields.items()]

        record_type = dataclasses.make_dataclass(
            f"{in_str}_{out_str}",
            all_fields,
        )
        subclass = type(f"{in_str}_{out_str}", (cls, record_type), namespace)

        return subclass

    def sort_records(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        record_fields: Dict[str, Any] = serialize(
            self, exclude_none=True, exclude_defaults=True
        )

        def make(cls: Type) -> Dict[str, Any]:
            fields = set(f.name for f in dataclasses.fields(cls))
            return {k: v for k, v in record_fields.items() if k in fields}

        return make(self.in_record_type), make(self.out_record_type)


# Populate records
AnalogueRecordPair = RecordPair.for_record_types("ai", "ao")
BinaryRecordPair = RecordPair.for_record_types("bi", "bo")
BusyRecordPair = RecordPair.for_record_types("bi", "busy")
LongRecordPair = RecordPair.for_record_types("longin", "longout")
MultiBitBinaryRecordPair = RecordPair.for_record_types("mbbi", "mbbo")
StringRecordPair = RecordPair.for_record_types("stringin", "stringout")
WaveformRecordPair = RecordPair.for_record_types("waveform", "waveform")

PVI_NELM = 100000


class PVIRecord(records.waveform, Record):
    def __init__(self, record: str):
        super().__init__(
            record,
            DESC="Driver PV Interface",
            DTYP="asynOctetRead",
            FTVL="CHAR",
            INP="@asyn($(PORT),$(ADDR=0),$(TIMEOUT=1))PVI_PARAM_TREE",
            NELM=PVI_NELM,
            SCAN="I/O Intr",
        )
