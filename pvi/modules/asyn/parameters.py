from annotypes import Optional, TYPE_CHECKING

from pvi.asynparam import Float64AsynParam
from pvi.record import AIRecord, AORecord

if TYPE_CHECKING:
    from typing import List


def float64(name,  # type: str
            desc,  # type: str
            prec,  # type: int
            egu,  # type: str
            autosave_fields,  # type: str
            widget,  # type: str
            group,  # type: str
            initial_value=None,  # type: Optional[int]
            demand="AutoUpdate",  # type: str
            readback="AutoUpdate"  # type: str
            ):
    # type: (...) -> List[Float64AsynParam, AIRecord, AORecord]

    truncated_desc = truncate_desc(desc)

    intermediate_objects = list()
    intermediate_objects.append(Float64AsynParam(name, initial_value))

    if demand != "No":
        prefix = "$(P)$(R)"
        out_string = "@asyn($(PORT),$(ADDR),$(TIMEOUT))" + name

        aorecord_fields = {
            "PINI": "YES",
            "DTYP": "asynFloat64",
            "OUT": out_string,
            "DESC": truncated_desc,
            "EGU": egu,
            "PREC": str(prec),
            "VAL": format_init_val(initial_value, prec)
        }

        aorecord_infos = {
            "autosaveFields": autosave_fields
        }

        aorecord = AORecord(prefix, name, aorecord_fields, aorecord_infos)
        intermediate_objects.append(aorecord)

    if readback != "No":
        prefix = "$(P)$(R)"
        in_string = "@asyn($(PORT),$(ADDR),$(TIMEOUT))" + name

        airecord_fields = {
            "DTYP": "asynFloat64",
            "INP": in_string,
            "DESC": truncated_desc,
            "EGU": egu,
            "PREC": str(prec),
            "SCAN": "I/O Intr"
        }

        airecord_infos = {}

        airecord = AIRecord(prefix, name + "_RBV", airecord_fields,
                            airecord_infos)
        intermediate_objects.append(airecord)

    return intermediate_objects


def format_init_val(val, prec):
    # type: (Optional[int], int) -> Optional[str]
    try:
        return "{val:.{prec}f}".format(val=val, prec=prec)
    except ValueError:
        return val


def truncate_desc(desc):
    # type: (str) -> str
    desc_split = desc.strip("\n").split("\n")
    one_line_desc = desc_split[0]
    return one_line_desc[:40]
