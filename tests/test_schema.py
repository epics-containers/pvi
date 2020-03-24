from pathlib import Path

import pytest
from ruamel.yaml import YAML

from pvi import Group, Record, Schema
from pvi._asyn import AsynFloat64


@pytest.fixture
def pilatus_schema():
    here = Path(__file__).parent
    data = YAML().load(here / "pilatus.pvi.yaml")
    schema = Schema(**data)
    return schema


def test_records(pilatus_schema: Schema):
    # Create records from the contents
    group: Group = pilatus_schema.components[0]
    energy: AsynFloat64 = group.components[0]
    records = list(pilatus_schema.producer.produce_records(energy))
    assert len(records) == 2
    assert records[0] == Record(
        record_type="ai",
        record_name="$(P)$(M)ThresholdEnergy_RBV",
        fields=dict(
            DESC="Threshold energy in keV",
            DTYP="asynFloat64",
            EGU="keV",
            INP="@asyn($(PORT),$(ADDR),$(TIMEOUT))THRESHOLDENERGY",
            PREC="3",
            SCAN="I/O Intr",
        ),
        infos={},
    )
    assert records[1] == Record(
        record_type="ao",
        record_name="$(P)$(M)ThresholdEnergy",
        fields=dict(
            DESC="Threshold energy in keV",
            DTYP="asynFloat64",
            EGU="keV",
            OUT="@asyn($(PORT),$(ADDR),$(TIMEOUT))THRESHOLDENERGY",
            PREC="3",
            VAL="10.0",
            PINI="YES",
        ),
        infos=dict(autosaveFields="VAL"),
    )
