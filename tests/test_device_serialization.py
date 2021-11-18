import json
from pathlib import Path

import pytest
from apischema import deserialize, serialize
from apischema.json_schema import deserialization_schema
from ruamel.yaml import YAML

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
    Tree,
)


@pytest.fixture
def device():
    return [
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


@pytest.fixture
def device_serialized():
    return YAML(typ="safe").load(
        Path(__file__).parent / "test_device_serialization.pvi.yaml"
    )


def test_serialize(device, device_serialized):
    s = serialize(device, exclude_none=True, exclude_defaults=True)
    assert json.dumps(s, indent=2) == json.dumps(device_serialized, indent=2)


def test_deserialize(device, device_serialized):
    d = deserialize(Tree[Component], device_serialized)
    assert d == device


def test_schema_matches_stored():
    expected = json.dumps(
        deserialization_schema(Tree[Component], all_refs=True), indent=2
    )
    # open(Path(__file__).parent.parent / "pvi.schema.json", "w").write(expected)
    actual = open(Path(__file__).parent.parent / "pvi.schema.json").read()
    assert actual == expected
