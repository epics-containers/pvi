from pathlib import Path

import pytest
from ruamel.yaml import YAML

from pvi import Record, Schema
from pvi._types import Channel, Group, Widget


@pytest.fixture
def pilatus_schema():
    here = Path(__file__).parent
    data = YAML().load(here / "pilatus.pvi.yaml")
    schema = Schema(**data)
    return schema


def test_records(pilatus_schema: Schema):
    record_tree = pilatus_schema.producer.produce_records(pilatus_schema.components)
    assert len(record_tree) == 1
    assert isinstance(record_tree[0], Group)
    records = record_tree[0].children
    assert len(records) == 2
    assert records[0] == Record(
        type="ai",
        name="$(P)$(M)ThresholdEnergy_RBV",
        fields=dict(
            DESC="Threshold energy in keV",
            DTYP="asynFloat64",
            EGU="keV",
            INP="@asyn($(PORT),$(ADDR),$(TIMEOUT))ThresholdEnergy",
            PREC="3",
            SCAN="I/O Intr",
        ),
        infos={},
    )
    assert records[1] == Record(
        type="ao",
        name="$(P)$(M)ThresholdEnergy",
        fields=dict(
            DESC="Threshold energy in keV",
            DTYP="asynFloat64",
            EGU="keV",
            OUT="@asyn($(PORT),$(ADDR),$(TIMEOUT))ThresholdEnergy",
            PREC="3",
            VAL="10.0",
            PINI="YES",
        ),
        infos=dict(autosaveFields="VAL"),
    )


def test_channels(pilatus_schema: Schema):
    channel_tree = pilatus_schema.producer.produce_channels(pilatus_schema.components)
    assert len(channel_tree) == 1
    assert isinstance(channel_tree[0], Group)
    channels = channel_tree[0].children
    assert len(channels) == 1
    assert channels[0] == Channel(
        name="ThresholdEnergy",
        label="Threshold Energy",
        read_pv="$(P)$(M)ThresholdEnergy_RBV",
        write_pv="$(P)$(M)ThresholdEnergy",
        widget=Widget.TEXTINPUT,
        description="""Threshold energy in keV

camserver uses this value to set the discriminators in each pixel.
It is typically set to the incident x-ray energy ($(P)$(R)Energy),
but sometimes other values may be preferable.
""",
        display_form=None,
    )


H_TXT = """\
#ifndef PILATUS_PARAMETERS_H
#define PILATUS_PARAMETERS_H

class PilatusParameters {
public:
    PilatusParameters(asynPortDriver *parent);
    /* Group: AncilliaryInformation */
    int ThresholdEnergy;  /* asynParamFloat64 Setting Pair */
}

#endif //PILATUS_PARAMETERS_H
"""


def test_h(pilatus_schema: Schema):
    parameters = pilatus_schema.producer.produce_asyn_parameters(
        pilatus_schema.components
    )
    h = pilatus_schema.formatter.format_h(parameters, "pilatus")
    assert h == H_TXT


CPP_TXT = """\
PilatusParameters::PilatusParameters(asynPortDriver *parent) {
    parent->createParam("ThresholdEnergy", asynParamFloat64, &ThresholdEnergy);
}
"""


def test_cpp(pilatus_schema: Schema):
    parameters = pilatus_schema.producer.produce_asyn_parameters(
        pilatus_schema.components
    )
    cpp = pilatus_schema.formatter.format_cpp(parameters, "pilatus")
    assert cpp == CPP_TXT


TEMPLATE_TXT = """\
# Group: AncilliaryInformation

record(ai, "$(P)$(M)ThresholdEnergy_RBV") {
    field(SCAN, "I/O Intr")
    field(DESC, "Threshold energy in keV")
    field(INP,  "@asyn($(PORT),$(ADDR),$(TIMEOUT))ThresholdEnergy")
    field(DTYP, "asynFloat64")
    field(EGU,  "keV")
    field(PREC, "3")
}

record(ao, "$(P)$(M)ThresholdEnergy") {
    field(DESC, "Threshold energy in keV")
    field(DTYP, "asynFloat64")
    field(EGU,  "keV")
    field(PREC, "3")
    field(OUT,  "@asyn($(PORT),$(ADDR),$(TIMEOUT))ThresholdEnergy")
    field(PINI, "YES")
    field(VAL,  "10.0")
    info(autosaveFields, "VAL)
}

"""


def test_template(pilatus_schema: Schema):
    records = pilatus_schema.producer.produce_records(pilatus_schema.components)
    template = pilatus_schema.formatter.format_template(records, "pilatus")
    assert template == TEMPLATE_TXT


DEVICE_TXT = r"""{
  "description": "",
  "channels": [
    {
      "type": "Group",
      "name": "AncilliaryInformation",
      "children": [
        {
          "name": "ThresholdEnergy",
          "label": "Threshold Energy",
          "read_pv": "$(P)$(M)ThresholdEnergy_RBV",
          "write_pv": "$(P)$(M)ThresholdEnergy",
          "widget": "Text Input",
          "description": "Threshold energy in keV\n\ncamserver uses this value to set the discriminators in each pixel.\nIt is typically set to the incident x-ray energy ($(P)$(R)Energy),\nbut sometimes other values may be preferable.\n",
          "display_form": null
        }
      ]
    }
  ]
}"""  # noqa


def test_device(pilatus_schema: Schema):
    channels = pilatus_schema.producer.produce_channels(pilatus_schema.components)
    device = pilatus_schema.formatter.format_device(channels, "pilatus")
    assert device == DEVICE_TXT
