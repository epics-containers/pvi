from pvi.asynparam import Float64AsynParam
from pvi.record import AIRecord, AORecord


def float64(name, desc, prec, egu, autosave_fields, widget, group,
            initial_value=None, demand="AutoUpdate", readback="AutoUpdate"):

    desc_split = desc.strip("\n").split("\n")
    one_line_desc = desc_split[0]
    truncated_desc = one_line_desc[:40]

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
    try:
        return "{val:.{prec}f}".format(val=val, prec=prec)
    except ValueError:
        return val
