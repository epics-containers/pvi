from annotypes import Anno, add_call_types, Array

from pvi.intermediate import Intermediate, ASuffix
from pvi.asynparam import Float64AsynParam
from pvi.record import AIRecord, AORecord

with Anno("The description of an asyn parameter"):
    ADescription = str


with Anno("The display precision"):
    APrecision = int


with Anno("The engineering units"):
    AEgu = str


with Anno("A collection of fields to autosave"):
    AAutosaveFields = str


with Anno("The widget associated with the parameter"):
    AWidget = str


with Anno("The group in the GUI containing the widget"):
    AGroup = str


with Anno("The initial value (if any) of an asyn parameter"):
    AInitialValue = int


with Anno("Is a demand record and widget required"):
    ADemand = str


with Anno("Is a readback record and widget required"):
    AReadback = str


with Anno("An array of Intermediate objects"):
    AIntermediatesArray = Array[Intermediate]


@add_call_types
def float64(name,  # type: ASuffix
            description,  # type: ADescription
            prec,  # type: APrecision
            egu,  # type: AEgu
            autosave_fields,  # type: AAutosaveFields
            widget,  # type: AWidget
            group,  # type: AGroup
            initial_value=None,  # type: AInitialValue
            demand="AutoUpdate",  # type: ADemand
            readback="No"  # type: AReadback
            ):
    # type: (...) -> AIntermediatesArray

    # TODO: demand and readback parameters should have type Enum
    assert demand in ["Yes", "No", "AutoUpdate"]
    assert readback in ["Yes", "No"]

    inout_parameter = "@asyn($(PORT),$(ADDR),$(TIMEOUT))"
    truncated_desc = truncate_desc(description)

    intermediate_objects = [Float64AsynParam(name)]

    if demand != "No":

        if initial_value is None:
            aorecord_fields = {
                "DTYP": "asynFloat64",
                "OUT": name,
                "DESC": truncated_desc,
                "EGU": egu,
                "PREC": prec,
            }
        else:
            aorecord_fields = {
                "PINI": "YES",
                "DTYP": "asynFloat64",
                "OUT": name,
                "DESC": truncated_desc,
                "EGU": egu,
                "PREC": prec,
                "VAL": initial_value
            }

        aorecord_infos = {
            "autosaveFields": autosave_fields
        }

        aorecord = AORecord(name, inout_parameter, aorecord_fields,
                            aorecord_infos)
        intermediate_objects.append(aorecord)

    if readback != "No":
        airecord_fields = {
            "DTYP": "asynFloat64",
            "INP": name,
            "DESC": truncated_desc,
            "EGU": egu,
            "PREC": prec,
            "SCAN": "I/O Intr"
        }

        airecord_infos = {}

        airecord = AIRecord(name + "_RBV", inout_parameter, airecord_fields,
                            airecord_infos)
        intermediate_objects.append(airecord)

    return AIntermediatesArray(intermediate_objects)


def truncate_desc(desc):
    # type: (str) -> str
    desc_split = desc.strip("\n").strip().split("\n")
    one_line_desc = desc_split[0]
    return one_line_desc[:40]
