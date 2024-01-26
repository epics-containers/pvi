import json
import os
from pathlib import Path

import pytest

from pvi.device import (
    LED,
    CheckBox,
    ComboBox,
    Device,
    Grid,
    Group,
    SignalR,
    SignalRW,
    SignalW,
    TableWrite,
    TextRead,
    TextWrite,
)


@pytest.fixture
def device():
    components = [
        Group(
            name="Parameters",
            layout=Grid(),
            children=[
                SignalW(
                    name="WidthUnits",
                    write_pv="WIDTH:UNITS",
                    write_widget=ComboBox(),
                ),
                SignalRW(
                    name="Width",
                    write_pv="WIDTH",
                    write_widget=TextWrite(),
                    read_pv="WIDTH_RBV",
                    read_widget=TextRead(),
                ),
            ],
        ),
        SignalW(
            name="Table",
            write_pv="TABLE",
            write_widget=TableWrite(widgets=[CheckBox(), ComboBox(), TextWrite()]),
        ),
        SignalR(name="OutA", read_pv="OUTA", read_widget=LED()),
    ]
    return Device(label="label", parent="parent", children=components)


DEVICE_YAML = Path(__file__).parent / "test.pvi.device.yaml"


def test_serialize(device: Device):
    if os.environ.get("PVI_REGENERATE_OUTPUT", None):
        device.serialize(DEVICE_YAML)

    s = device._to_dict()
    d = Device.validate_yaml(DEVICE_YAML)

    assert json.dumps(s, indent=2) == json.dumps(d, indent=2)


def test_deserialize(device: Device):
    d = Device.deserialize(DEVICE_YAML)
    assert d == device
