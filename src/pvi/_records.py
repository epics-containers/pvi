from __future__ import annotations

import ctypes
import dataclasses
from ctypes import POINTER, c_char_p, c_int, c_void_p, pointer
from dataclasses import Field, field, make_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Tuple, Type, get_type_hints

from apischema import serialize
from epicscorelibs.ioc import dbCore
from epicscorelibs.path import base_path
from typing_extensions import Annotated as A

from ._utils import desc


# https://code.activestate.com/recipes/576731-c-function-decorator/
class EPICSFunc:
    """This class wraps a Python function into its C equivalent in the given library"""

    def __init__(self, error_check=None):
        """Set the library to reference the function name against."""
        self.error_check = error_check

    def __getitem__(self, key):
        """Return a pointer to the type, used in get_type_hints below"""
        # https://github.com/python/mypy/issues/7540
        return POINTER(key)

    def __call__(self, f):
        """Performs the actual function wrapping."""
        # Get the type hints, redirecting pointer[something] to self
        hints = get_type_hints(f, localns=dict(pointer=self))

        # get the function itself
        function = dbCore[f.__name__]

        # Set its call args, return type, and error handler if there is one
        function.argtypes = [v for x, v in hints.items() if x != "return"]
        function.restype = hints.get("return")
        if self.error_check:
            function.errcheck = self.error_check

        return function


class auto_encode(c_char_p):
    @classmethod
    def from_param(cls, value):
        return None if value is None else value.encode()


def auto_decode(result, func, args):
    return None if result is None else result.decode()


def expect_success(result, function, args):
    assert result == 0, f"Expected success from {function}{args}"
    return result


@EPICSFunc(expect_success)
def dbReadDatabase(
    *,
    ppdbbase: c_void_p,
    filename: auto_encode,
    path: auto_encode,
    substitutions: auto_encode,
) -> c_int:
    ...


@EPICSFunc()
def dbAllocEntry(*, pdbbase: c_void_p) -> c_void_p:
    ...


@EPICSFunc(expect_success)
def dbFirstRecordType(*, pdbentry: c_void_p) -> c_int:
    ...


@EPICSFunc()
def dbNextRecordType(*, pdbentry: c_void_p) -> c_int:
    ...


@EPICSFunc(auto_decode)
def dbGetRecordTypeName(*, pdbentry: c_void_p) -> c_char_p:
    ...


@EPICSFunc(expect_success)
def dbFirstField(*, pdbentry: c_void_p, dctonly: c_int) -> c_int:
    ...


@EPICSFunc()
def dbNextField(*, pdbentry: c_void_p, dctonly: c_int) -> c_int:
    ...


@EPICSFunc(auto_decode)
def dbGetFieldName(*, pdbentry: c_void_p) -> c_char_p:
    ...


@EPICSFunc()
def dbGetFieldDbfType(*, pdbentry: c_void_p) -> c_int:
    ...


@EPICSFunc(auto_decode)
def dbGetFieldTypeString(*, dbfType: c_int) -> c_char_p:
    ...


@EPICSFunc(auto_decode)
def dbGetDefault(*, pdbentry: c_void_p) -> c_char_p:
    ...


@EPICSFunc(auto_decode)
def dbGetPrompt(*, pdbentry: c_void_p) -> c_char_p:
    ...


@EPICSFunc()
def dbGetNMenuChoices(*, pdbentry: c_void_p) -> c_int:
    ...


@EPICSFunc()
def dbGetMenuChoices(*, pdbentry: c_void_p) -> pointer[c_char_p]:
    ...


@EPICSFunc()
def dbFreeEntry(*, pdbentry: c_void_p):
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

FieldList = List[Tuple[str, Type, Field]]


def make_fields(entry) -> FieldList:
    status = dbFirstField(entry, 0)
    fields: FieldList = []
    while status == 0:
        field_name = dbGetFieldName(entry)
        default = dbGetDefault(entry)
        prompt = dbGetPrompt(entry)
        field_type = DBF_TYPE_MAP[dbGetFieldTypeString(dbGetFieldDbfType(entry))]
        if field_type is Enum:
            # Make a custom enum type from the menu choices
            choices = dbGetMenuChoices(entry)
            str_choices = [choices[i].decode() for i in range(dbGetNMenuChoices(entry))]
            field_type = Enum(field_name, [(c, c) for c in str_choices])  # type: ignore
        if field_type:
            fields.append(
                (field_name, A[field_type, desc(prompt)], field(default=default))
            )
        status = dbNextField(entry, 0)
    return fields


def make_fields_dict() -> Dict[str, FieldList]:
    fields_dict: Dict[str, FieldList] = {}
    pdbbase = ctypes.c_void_p()
    dbd_path = str(Path(base_path) / "dbd")
    dbReadDatabase(ctypes.byref(pdbbase), "base.dbd", dbd_path, None)
    entry = dbAllocEntry(pdbbase)
    status = dbFirstRecordType(entry)
    while status == 0:
        record_type = dbGetRecordTypeName(entry)
        fields_dict[record_type] = make_fields(entry)
        status = dbNextRecordType(entry)
    dbFreeEntry(entry)
    return fields_dict


fields_dict = make_fields_dict()


class RecordPair:
    in_record_type: ClassVar[Type]
    out_record_type: ClassVar[Type]

    @classmethod
    def for_record_types(cls, in_str: str, out_str: str) -> Type[RecordPair]:
        in_record_type = make_dataclass(in_str, fields_dict[in_str])
        out_record_type = make_dataclass(out_str, fields_dict[out_str])
        namespace = dict(in_record_type=in_record_type, out_record_type=out_record_type)
        subclass = type(
            f"{in_str}_{out_str}", (cls, in_record_type, out_record_type), namespace
        )
        return subclass

    def sort_records(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        record_fields: Dict[str, Any] = serialize(
            self, exclude_none=True, exclude_defaults=True
        )

        def make(cls: Type) -> Dict[str, Any]:
            fields = set(f.name for f in dataclasses.fields(cls))
            return {k: v for k, v in record_fields.items() if k in fields}

        return make(self.in_record_type), make(self.out_record_type)


AnalogueRecordPair = RecordPair.for_record_types("ai", "ao")
BinaryRecordPair = RecordPair.for_record_types("bi", "bo")
LongRecordPair = RecordPair.for_record_types("longin", "longout")
MultiBitBinaryRecordPair = RecordPair.for_record_types("mbbi", "mbbo")
StringRecordPair = RecordPair.for_record_types("stringin", "stringout")
WaveformRecordPair = RecordPair.for_record_types("waveform", "waveform")

# TODO: add busy record
