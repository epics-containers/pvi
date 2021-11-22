from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Iterator, Optional, Union

from apischema.schemas import schema
from apischema.types import Number
from epicsdbbuilder import records
from epicsdbbuilder.recordbase import Record
from epicsdbbuilder.recordset import WriteRecords

from ._records import (
    AnalogueRecordPair,
    BinaryRecordPair,
    LongRecordPair,
    MultiBitBinaryRecordPair,
    RecordPair,
    StringRecordPair,
    WaveformRecordPair,
)
from ._utils import (
    Annotated,
    as_discriminated_union,
    desc,
    get_param_set,
    join_lines,
    truncate_description,
)
from .types import (
    LED,
    Access,
    CheckBox,
    ComboBox,
    Component,
    DisplayForm,
    Named,
    Producer,
    ReadWidget,
    SignalR,
    SignalRW,
    SignalW,
    TextRead,
    TextWrite,
    Tree,
    WriteWidget,
    on_each_node,
    walk,
)


@dataclass
class TypeStrings:
    """The type strings for record dtypes and parameter names"""

    asyn_read: Annotated[str, desc("e.g. asynInt32, asynOctetRead")]
    asyn_write: Annotated[str, desc("e.g. asynInt32, asynOctetWrite")]
    asyn_param: Annotated[str, desc("e.g. asynParamInt32, asynParamOctet")]


AReadWidget = Annotated[Optional[ReadWidget], desc("Widget to use for read record")]
AWriteWidget = Annotated[Optional[WriteWidget], desc("Widget to use for write record")]


@as_discriminated_union
@dataclass
class AsynParameter(Named):
    """Base class for all Asyn Parameters to inherit from"""

    description: Annotated[str, desc("Description of what this Parameter is for")]
    index_name: Annotated[
        Optional[str],
        desc("Override name of index variable in source code (defaults to name)"),
    ] = None
    drv_info: Annotated[
        Optional[str],
        desc(
            "Info string for drvUserCreate for dynamically created parameters",
            # Limit to 40 characters with no whitespace
            pattern=r"^\S{1,40}$",
        ),
    ] = None
    access: Annotated[Access, desc(Access.__doc__)] = Access.RW
    demand_auto_updates: Annotated[
        bool, desc("Should demand update when readback changes?")
    ] = False
    read_record_suffix: Annotated[
        Optional[str], desc("The read record suffix, if not given then use $(name)_RBV")
    ] = None
    write_record_suffix: Annotated[
        Optional[str], desc("The write record suffix, if not given then use $(name)")
    ] = None
    display_form: Annotated[
        Optional[DisplayForm], desc("Display form for numeric/array fields")
    ] = None
    type_strings: ClassVar[TypeStrings]
    initial: Any = None
    read_widget: Optional[AReadWidget] = None
    write_widget: Optional[AWriteWidget] = None
    record_fields: RecordPair = RecordPair()


def initial_value(pattern: str = None, min: Number = None, max: Number = None):
    if pattern:
        pattern = r"(\$\(\w+=(" + pattern + r")\))"
    return schema(
        description="The initial value of the parameter",
        min=min,
        max=max,
        pattern=pattern,
    )


@dataclass
class AsynBinary(AsynParameter):
    """Asyn Binary Parameter and records"""

    type_strings = TypeStrings(
        asyn_read="asynInt32", asyn_write="asynInt32", asyn_param="asynParamInt32",
    )
    initial: Annotated[
        Union[None, int, str], initial_value(r"[0-1]", min=0, max=1)
    ] = None
    read_widget: AReadWidget = LED()
    write_widget: AWriteWidget = CheckBox()
    record_fields: Annotated[  # type: ignore
        BinaryRecordPair, desc("Binary record fields")
    ] = BinaryRecordPair()


@dataclass
class AsynFloat64(AsynParameter):
    """Asyn Float64 Parameter and records"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynFloat64",
        asyn_write="asynFloat64",
        asyn_param="asynParamFloat64",
    )
    initial: Annotated[
        Union[None, float, str], initial_value(r"-?[0-9]+(\.[0-9]+)?")
    ] = None
    read_widget: AReadWidget = TextRead()
    write_widget: AWriteWidget = TextWrite()
    record_fields: Annotated[  # type: ignore
        AnalogueRecordPair, desc("Analogue record fields")
    ] = AnalogueRecordPair()


@dataclass
class AsynInt32(AsynParameter):
    """Asyn Int32 Parameter and records"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynInt32", asyn_write="asynInt32", asyn_param="asynParamInt32",
    )
    initial: Annotated[Union[None, int, str], initial_value(r"-?\d+")] = None
    read_widget: AReadWidget = TextRead()
    write_widget: AWriteWidget = TextWrite()
    record_fields: Annotated[  # type: ignore
        AnalogueRecordPair, desc("Analogue record fields")
    ] = AnalogueRecordPair()


@dataclass
class AsynLong(AsynInt32):
    """Asyn Long Parameter and records"""

    record_fields: Annotated[  # type: ignore
        LongRecordPair, desc("Long record fields")
    ] = LongRecordPair()


@dataclass
class AsynMultiBitBinary(AsynParameter):
    """Asyn MultiBitBinary Parameter and records"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynInt32", asyn_write="asynInt32", asyn_param="asynParamInt32",
    )
    initial: Annotated[
        Union[None, int, str], initial_value(r"[0-15]", min=0, max=15)
    ] = None
    read_widget: AReadWidget = TextRead()
    write_widget: AWriteWidget = ComboBox()
    record_fields: Annotated[  # type: ignore
        MultiBitBinaryRecordPair, desc("Multi-bit binary record fields")
    ] = MultiBitBinaryRecordPair()


@dataclass
class AsynString(AsynParameter):
    """Asyn String Parameter and records"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynOctetRead",
        asyn_write="asynOctetWrite",
        asyn_param="asynParamOctet",
    )
    initial: Annotated[Union[None, str], initial_value()] = None
    read_widget: AReadWidget = TextRead()
    write_widget: AWriteWidget = TextWrite()
    record_fields: Annotated[  # type: ignore
        StringRecordPair, desc("String record fields")
    ] = StringRecordPair()


@dataclass
class AsynWaveform(AsynParameter):
    """Asyn Waveform Parameter and records"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynOctetRead",
        asyn_write="asynOctetWrite",
        asyn_param="asynParamOctet",
    )
    record_fields: Annotated[  # type: ignore
        WaveformRecordPair, desc("Waveform record fields")
    ] = WaveformRecordPair()


@dataclass
class AsynProducer(Producer):
    prefix: Annotated[
        str, desc("The prefix for record names created by the template file")
    ]
    asyn_port: Annotated[str, desc("The asyn port name")]
    address: Annotated[str, desc("The asyn address")]
    timeout: Annotated[str, desc("The timeout for the asyn port")]
    parent_class: Annotated[
        str, desc("The parent class for the ParamSet.h")
    ] = "ADDriver"
    parameters: Annotated[
        Tree[AsynParameter], desc("The parameters to make into an IOC")
    ] = field(default_factory=list)

    def _read_record_suffix(self, parameter: AsynParameter) -> str:
        if parameter.read_record_suffix:
            return parameter.read_record_suffix
        else:
            return parameter.name + "_RBV"

    def _write_record_suffix(self, parameter: AsynParameter) -> str:
        if parameter.write_record_suffix:
            return parameter.write_record_suffix
        else:
            return parameter.name

    def produce_components(self) -> Tree[Component]:
        """Make signals from components"""
        return on_each_node(self.parameters, self._produce_component)

    def _produce_component(self, parameter: AsynParameter) -> Iterator[Component]:
        # TODO: what about SignalX?
        read_pv = self._read_record_suffix(parameter)
        write_pv = self._write_record_suffix(parameter)
        if parameter.access == Access.R:
            yield SignalR(parameter.name, read_pv, parameter.read_widget)
        elif parameter.access == Access.W:
            yield SignalW(
                parameter.name, write_pv, parameter.write_widget,
            )
        elif parameter.access == Access.RW:
            need_both = not parameter.demand_auto_updates
            yield SignalRW(
                parameter.name,
                write_pv,
                parameter.write_widget,
                read_pv=read_pv if need_both else "",
                read_widget=parameter.read_widget if need_both else None,
            )

    def produce_records(self, path: Path):
        """Make epicsdbbuilder records"""
        comment = None
        for node in walk(self.parameters):
            if isinstance(node, AsynParameter):
                for record in self._produce_record(node):
                    if node.display_form:
                        record.add_info("Q:form", node.display_form)
                    if comment:
                        record.add_comment(comment)
                    comment = None
            else:
                comment = f"Group: {node.name}"
                header = """\
This file was automatically generated

*** Please do not edit this file: edit the source file instead. ***
"""
        WriteRecords(str(path), header=header, alphabetical=None)

    def _produce_record(self, parameter: AsynParameter) -> Iterator[Record]:
        inp_fields, out_fields = parameter.record_fields.sort_records()
        asyn_param_name = parameter.drv_info or parameter.name
        io = f"@asyn({self.asyn_port},{self.address},{self.timeout}){asyn_param_name}"
        if parameter.access.needs_read_record():
            name = self.prefix + self._read_record_suffix(parameter)
            rtype = parameter.record_fields.in_record_type.__name__
            inp_fields.update(
                DESC=truncate_description(parameter.description),
                DTYP=parameter.type_strings.asyn_read,
                INP=io,
            )
            yield getattr(records, rtype)(name, **inp_fields)
        if parameter.access.needs_write_record():
            name = self.prefix + self._write_record_suffix(parameter)
            rtype = parameter.record_fields.out_record_type.__name__
            out_fields.update(
                DESC=truncate_description(parameter.description),
                DTYP=parameter.type_strings.asyn_write,
            )
            if rtype == "waveform":
                out_fields["INP"] = io
            else:
                out_fields["OUT"] = io
            if parameter.initial is not None:
                out_fields.update(PINI="YES", VAL=parameter.initial)
            out_fields.pop("SCAN", None)
            record = getattr(records, rtype)(name, **out_fields)
            if parameter.demand_auto_updates:
                record.add_info("asyn:READBACK", 1)
            yield record

    def produce_other(self, path: Path):
        """Make things like cpp, h files"""
        is_valid = path.suffix == ".h" and "." not in path.stem
        parent_param_set = get_param_set(self.parent_class)
        assert is_valid, f"Can only make header files not {path}"
        guard_define = path.stem[0].upper() + path.stem[1:] + "_H"
        defines = []
        adds = []
        indexes = []
        for node in walk(self.parameters):
            if isinstance(node, AsynParameter):
                param_type = node.type_strings.asyn_param
                index_name = node.index_name or node.name
                drv_info = node.drv_info or node.name
                defines.append(f'#define {index_name}String "{drv_info}"')
                adds.append(
                    f"this->add({index_name}String, {param_type}, &{index_name});"
                )
                indexes.append(f"int {index_name};")
                if len(indexes) == 1:
                    indexes.append(
                        f"#define FIRST_{path.stem.upper()}_PARAM {index_name}"
                    )

        path.write_text(
            f"""\
#ifndef {guard_define}
#define {guard_define}

#include "{parent_param_set}.h"

{join_lines(defines)}

class {path.stem} : public virtual {parent_param_set} {{
public:
    {path.stem}() {{
        {join_lines(adds, indent=8)}
    }}

    {join_lines(indexes, indent=4)}
}};

#endif // {guard_define}
"""
        )
