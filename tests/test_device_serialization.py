import json
from pathlib import Path

import pytest
from apischema import serialize
from ruamel.yaml import YAML

from pvi._produce.asyn import AsynInt32
from pvi._produce.base import Access
from pvi._utils import serialize_yaml
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
                SignalRW("Width", "WIDTH", TextWrite()),
            ],
        ),
        SignalRW("Table", "TABLE", TableWrite([CheckBox(), ComboBox(), TextWrite()])),
        SignalR("OutA", "OUTA", LED()),
    ]
    return Device("label", components)


@pytest.fixture
def device_serialized():
    return YAML(typ="safe").load(
        Path(__file__).parent / "test_device_serialization.pvi.yaml"
    )


def test_serialize(device: Device, device_serialized):
    s = device.serialize()
    assert json.dumps(s, indent=2) == json.dumps(device_serialized, indent=2)


def test_deserialize(device: Device, device_serialized):
    d = Device.deserialize(device_serialized)
    assert d == device


def test_serialize_access(tmp_path: Path):
    p = AsynInt32("boo", "bad", access=Access.W)
    assert serialize(p, exclude_defaults=True, exclude_none=True) == {}
    d = {"access": Access.W}
    assert json.dumps(serialize(d)) == '{"access": "W"}'
    output = tmp_path / "out.yaml"
    serialize_yaml(d, output)
    assert output.read_text() == ""

