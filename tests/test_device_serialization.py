import json
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from pvi.device import (
    LED,
    CheckBox,
    ComboBox,
    Device,
    Grid,
    Group,
    SignalR,
    SignalRW,
    TableWrite,
    TextRead,
    TextWrite,
)


@pytest.fixture
def device():
    components = [
        Group(
            "Parameters",
            Grid(),
            [
                SignalRW("WidthUnits", "WIDTH:UNITS", ComboBox()),
                SignalRW("Width", "WIDTH", TextWrite(), "WIDTH_RBV", TextRead()),
            ],
        ),
        SignalRW("Table", "TABLE", TableWrite([CheckBox(), ComboBox(), TextWrite()])),
        SignalR("OutA", "OUTA", LED()),
    ]
    return Device("label", "parent", components)


DEVICE_YAML = Path(__file__).parent / "test_device_serialization.pvi.yaml"


def test_serialize(device: Device):
    s = device.serialize()
    assert json.dumps(s, indent=2) == json.dumps(
        YAML(typ="safe").load(DEVICE_YAML), indent=2
    )


def test_deserialize(device: Device):
    d = Device.deserialize(DEVICE_YAML)
    assert d == device
