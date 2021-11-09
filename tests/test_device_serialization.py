import json
from typing import List

import pytest
from apischema import deserialize, serialize
from apischema.json_schema import deserialization_schema

from pvi.types import (
    LED,
    CheckBox,
    ComboBox,
    Component,
    Grid,
    Group,
    SignalR,
    SignalRW,
    TableWrite,
    TextWrite,
)


@pytest.fixture
def device():
    return [
        Group(
            "parameters",
            Grid(),
            [
                SignalRW("widthUnits", "WIDTH:UNITS", ComboBox()),
                SignalRW("width", "WIDTH", TextWrite()),
            ],
        ),
        SignalRW("table", "TABLE", TableWrite([CheckBox(), ComboBox(), TextWrite()])),
        SignalR("outA", "OUTA", LED()),
    ]


@pytest.fixture
def device_serialized():
    return [
        {
            "type": "Group",
            "name": "parameters",
            "layout": {"type": "Grid"},
            "children": [
                {
                    "type": "SignalRW",
                    "name": "widthUnits",
                    "pv": "WIDTH:UNITS",
                    "widget": {"type": "ComboBox"},
                },
                {
                    "type": "SignalRW",
                    "name": "width",
                    "pv": "WIDTH",
                    "widget": {"type": "TextWrite"},
                },
            ],
        },
        {
            "type": "SignalRW",
            "name": "table",
            "pv": "TABLE",
            "widget": {
                "type": "TableWrite",
                "widgets": [
                    {"type": "CheckBox"},
                    {"type": "ComboBox"},
                    {"type": "TextWrite"},
                ],
            },
        },
        {"type": "SignalR", "name": "outA", "pv": "OUTA", "widget": {"type": "LED"}},
    ]


def test_serialize(device, device_serialized):
    s = serialize(device, exclude_none=True, exclude_defaults=True)
    assert json.dumps(s, indent=2) == json.dumps(device_serialized, indent=2)


def test_deserialize(device, device_serialized):
    d = deserialize(List[Component], device_serialized)
    assert d == device


def test_schema():
    expected = json.dumps(deserialization_schema(List[Component]), indent=2)
    open("pvi.schema.json", "w").write(expected)
