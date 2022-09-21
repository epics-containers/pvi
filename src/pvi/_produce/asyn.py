import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Iterator, List, Optional, Union

from apischema.schemas import schema
from apischema.types import Number
from epicsdbbuilder import WriteRecords, records
from epicsdbbuilder.recordbase import Record
from typing_extensions import Annotated

from pvi._schema_utils import as_discriminated_union, desc
from pvi._yaml_utils import deserialize_yaml
from pvi.device import (
    LED,
    CheckBox,
    ComboBox,
    Component,
    Device,
    Group,
    Named,
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

from .base import Access, DisplayForm, Producer
from .records import (
    PVI_NELM,
    AnalogueRecordPair,
    BinaryRecordPair,
    BusyRecordPair,
    LongRecordPair,
    MultiBitBinaryRecordPair,
    PVIRecord,
    RecordPair,
    StringRecordPair,
    WaveformRecordPair,
)
from .utils import get_param_set, join_lines, truncate_description


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

    def get_index_name(self):
        return self.index_name or self.name

    def get_drv_info(self):
        return self.drv_info or self.name


def initial_value(pattern: str = None, min: Number = None, max: Number = None):
    if pattern:
        pattern = r"[\'\"]?(?:\$\(\w+=)?" + pattern + r"\)?[\'\"]?"
    return schema(
        description="The initial value of the parameter",
        min=min,
        max=max,
        pattern=pattern,
    )


# The child classes of AsynParameter redefine record_fields with a dynamic type to
# generate a schema with fields specific to the parameter type. However, the dymanic
# types make mypy unhappy when it tries to do static type checking, so we use
# `type: ignore`.
# https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases


@dataclass
class AsynBinary(AsynParameter):
    """Asyn Binary Parameter and records"""

    type_strings = TypeStrings(
        asyn_read="asynInt32",
        asyn_write="asynInt32",
        asyn_param="asynParamInt32",
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
class AsynBusy(AsynBinary):
    """Asyn Busy Parameter and records"""

    record_fields: Annotated[  # type: ignore
        BusyRecordPair, desc("Busy record fields")
    ] = BusyRecordPair()


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
        asyn_read="asynInt32",
        asyn_write="asynInt32",
        asyn_param="asynParamInt32",
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
        asyn_read="asynInt32",
        asyn_write="asynInt32",
        asyn_param="asynParamInt32",
    )
    initial: Annotated[
        # Regex: [0-9] OR 1[0-5] -> [0-15]  (Single character matching)
        Union[None, int, str],
        initial_value(r"([0-9]|1[0-5])", min=0, max=15),
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
    read_widget: AReadWidget = TextRead()
    write_widget: AWriteWidget = TextWrite()
    record_fields: Annotated[  # type: ignore
        WaveformRecordPair, desc("Waveform record fields")
    ] = WaveformRecordPair()


@dataclass
class AsynInt32Waveform(AsynWaveform):
    """Asyn Waveform Parameter and records with int32 array elements"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynInt32ArrayIn",
        asyn_write="asynInt32ArrayOut",
        asyn_param="asynParamInt32",
    )
    # We have to redefine this to retain the `type: ignore` for mypy
    record_fields: Annotated[  # type: ignore
        WaveformRecordPair, desc("Waveform record fields")
    ] = WaveformRecordPair()


@dataclass
class AsynFloat64Waveform(AsynWaveform):
    """Asyn Waveform Parameter and records with int32 array elements"""

    type_strings: ClassVar[TypeStrings] = TypeStrings(
        asyn_read="asynFloat64ArrayIn",
        asyn_write="asynFloat64ArrayOut",
        asyn_param="asynParamFloat64",
    )
    # We have to redefine this to retain the `type: ignore` for mypy
    record_fields: Annotated[  # type: ignore
        WaveformRecordPair, desc("Waveform record fields")
    ] = WaveformRecordPair()


def find_components(yaml_name: str, yaml_paths: List[Path]) -> Tree[AsynParameter]:
    if yaml_name == "asynPortDriver":
        return []  # asynPortDriver is the most base class and has no parameters

    # Look in this module first
    producer_name = f"{yaml_name}.pvi.producer.yaml"
    producer_yaml = find_pvi_yaml(producer_name, yaml_paths)

    if producer_yaml is None:
        raise IOError(f"Cannot find {producer_name} in {yaml_paths}")

    producer = deserialize_yaml(AsynProducer, producer_yaml)

    return list(producer.parameters) + list(
        find_components(producer.parent, yaml_paths)
    )


def find_pvi_yaml(yaml_name: str, yaml_paths: List[Path]) -> Union[Path, None]:
    """Find a yaml file in given directory"""
    for yaml_path in yaml_paths:
        if yaml_path.is_dir():
            if yaml_name in [f.name for f in yaml_path.iterdir()]:
                return yaml_path / yaml_name
    return None


@dataclass
class AsynProducer(Producer):
    label: Annotated[str, desc("Screen title")]
    asyn_port: Annotated[str, desc("The asyn port name")]
    address: Annotated[str, desc("The asyn address")]
    timeout: Annotated[str, desc("The timeout for the asyn port")]
    parent: Annotated[
        str,
        desc(
            "The parent producer (basename of yaml file), "
            "asynPortDriver is the top of the tree"
        ),
    ]
    parameters: Annotated[
        Tree[AsynParameter], desc("The parameters to make into an IOC")
    ]

    def deserialize_parents(self, yaml_paths: List[Path]):
        """Deserialize yaml of parents and extract parameters"""
        if self.parent == "asynPortDriver":
            pass

        parent_parameters = find_components(self.parent, yaml_paths)
        for node in parent_parameters:
            if isinstance(node, Group):
                for param_group in self.parameters:
                    if not isinstance(param_group, Group):
                        continue
                    elif param_group.name == node.name:
                        param_group.children = list(node.children) + list(
                            param_group.children
                        )
                        break  # Groups merged - skip to next parent group

                else:  # No break - Did not find the Group
                    # Inherit as a new Group
                    self.parameters = list(self.parameters) + [node]
                    continue  # Skip to next parent group

            else:
                # Node is an individual AsynParameter - just append it
                self.parameters = list(self.parameters) + [node]

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

    def produce_device(self) -> Device:
        """Make signals from components"""
        components = on_each_node(self.parameters, self._produce_component)
        return Device(self.label, components)

    def _produce_component(self, parameter: AsynParameter) -> Iterator[Component]:
        # TODO: what about SignalX?
        read_pv = self._read_record_suffix(parameter)
        write_pv = self._write_record_suffix(parameter)
        if parameter.access == Access.R:
            yield SignalR(parameter.name, read_pv, parameter.read_widget)
        elif parameter.access == Access.W:
            yield SignalW(parameter.name, write_pv, parameter.write_widget)
        elif parameter.access == Access.RW:
            need_both = not parameter.demand_auto_updates
            yield SignalRW(
                parameter.name,
                write_pv,
                parameter.write_widget,
                read_pv=read_pv if need_both else "",
                read_widget=parameter.read_widget if need_both else None,
            )

    def produce_csv(self, path: Path):
        with open(path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",", quotechar='"')
            writer.writerow(
                [
                    "Parameter Index Variable",
                    "Asyn Interface",
                    "Access",
                    "drvInfo String",
                    "Record Names",
                    "Record Types",
                    "Description",
                ]
            )
            for node in walk(self.parameters):
                if isinstance(node, Group):
                    writer.writerow([f"*{node.name}*"] + [""] * 6)
                else:
                    names = []
                    types = []
                    interfaces = []
                    if node.access.needs_write_record():
                        names.append(self.prefix + self._write_record_suffix(node))
                        types.append(node.record_fields.out_record_type.__name__)
                        interfaces.append(node.type_strings.asyn_write)
                    if node.access.needs_read_record():
                        names.append(self.prefix + self._read_record_suffix(node))
                        types.append(node.record_fields.in_record_type.__name__)
                        if node.type_strings.asyn_read not in interfaces:
                            interfaces.append(node.type_strings.asyn_read)

                    writer.writerow(
                        [
                            node.index_name,
                            ",\n".join(interfaces),
                            node.access.name,
                            node.drv_info,
                            ",\n".join(names),
                            ",\n".join(types),
                            node.description,
                        ]
                    )

    def produce_records(self, path: Path):
        """Make epicsdbbuilder records"""
        comment = None
        for node in walk(self.parameters):
            if isinstance(node, Group):
                comment = f"Group: {node.name}"
            else:
                for record in self._produce_record(node):
                    if node.display_form:
                        record.add_info("Q:form", node.display_form)
                    if comment:
                        record.add_comment(comment)
                    comment = None

        if self.parent == "asynPortDriver":
            PVIRecord(self.prefix + "PVI")

        header = """\
This file was automatically generated
*** Please do not edit this file: edit the source file instead. ***
"""
        WriteRecords(str(path), header=header, alphabetical=False)

    def _produce_record(self, parameter: AsynParameter) -> Iterator[Record]:
        inp_fields, out_fields = parameter.record_fields.sort_records()
        drv_info = parameter.get_drv_info()
        io = f"@asyn({self.asyn_port},{self.address},{self.timeout}){drv_info}"
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

    def produce_other(self, path: Path, yaml_paths: List[Path]):
        """Make things like cpp, h files"""
        is_valid = path.suffix == ".h" and "." not in path.stem
        parent_param_set = get_param_set(self.parent)
        assert is_valid, f"Can only make header files not {path}"
        guard_define = path.stem[0].upper() + path.stem[1:] + "_H"
        defines = []
        adds = []
        indexes = []

        # Special case to add NDArrayData as first asynNDArrayDriver parameter
        # There is also a special case to remove it from the source files
        if path.name.startswith("asynNDArrayDriver"):
            defines.append('#define NDArrayDataString "ARRAY_DATA"')
            adds.append(
                "this->add(NDArrayDataString, asynParamGenericPointer, &NDArrayData);"
            )
            indexes.append("int NDArrayData;")
            indexes.append(f"#define FIRST_{path.stem.upper()}_PARAM NDArrayData")

        for node in walk(self.parameters):
            if isinstance(node, AsynParameter):
                param_type = node.type_strings.asyn_param
                index_name = node.get_index_name()

                defines.append(f'#define {index_name}String "{node.get_drv_info()}"')
                adds.append(
                    f"this->add({index_name}String, {param_type}, &{index_name});"
                )
                indexes.append(f"int {index_name};")

                if len(indexes) == 1:
                    indexes.append(
                        f"#define FIRST_{path.stem.upper()}_PARAM {index_name}"
                    )

        self.deserialize_parents(yaml_paths)
        param_tree = self.produce_device().generate_param_tree()
        assert len(param_tree) <= PVI_NELM, "Param tree limited to 100000 characters"

        path.write_text(
            f"""\
#ifndef {guard_define}
#define {guard_define}

#include "{parent_param_set}.h"

{join_lines(defines)}

const std::string {self.label}ParamTree = \\
{param_tree};

class {path.stem} : public virtual {parent_param_set} {{
public:
    {path.stem}() {{
        {join_lines(adds, indent=8)}

        this->paramTree = {self.label}ParamTree;
    }}

    {join_lines(indexes, indent=4)}
}};

#endif // {guard_define}
"""
        )
