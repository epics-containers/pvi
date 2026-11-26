import json
import os
from pathlib import Path
from typing import Annotated, TypeAlias
from unittest.mock import patch

import pytest
from pydantic import BaseModel, Discriminator, Field, Tag, ValidationError

from pvi._format import Formatter
from pvi.device import (
    LED,
    CheckBox,
    ComboBox,
    Device,
    Grid,
    Group,
    Include,
    SignalR,
    SignalRW,
    SignalW,
    TableWrite,
    TextRead,
    TextWrite,
)
from pvi.typed_model import TypedModel


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
        Include(file_name="parent"),
    ]
    return Device(label="label", children=components)


DEVICE_YAML = Path(__file__).parent / "test.pvi.device.yaml"
BAD_DEVICE_YAML = Path(__file__).parent / "bad.pvi.device.yaml"
DEPRECATED_DEVICE_YAML = Path(__file__).parent / "deprecated.pvi.device.yaml"


def test_serialize(device: Device):
    if os.environ.get("PVI_REGENERATE_OUTPUT", None):
        device.serialize(DEVICE_YAML)

    s = device._to_dict()
    d = Device.validate_yaml(DEVICE_YAML)

    assert json.dumps(s, indent=2) == json.dumps(d, indent=2)


def test_deserialize(device: Device):
    d = Device.deserialize(DEVICE_YAML)
    assert d == device


def test_deserialize_raises_validation_error():
    with pytest.raises(ValidationError):
        Device.deserialize(BAD_DEVICE_YAML)


@pytest.mark.filterwarnings("error::DeprecationWarning")
def test_deserialize_parents_raises_deprecation_warning():
    with patch("pvi.device.Device.expand_includes", return_value=[]):
        with pytest.deprecated_call(
            match="parent is deprecated, use `Include` statement instead"
        ):
            Device.deserialize(DEPRECATED_DEVICE_YAML).deserialize_parents([])


def test_validate_fails():
    class NotTypedModel(BaseModel):
        pass

    BadUnion: TypeAlias = Annotated[  # type: ignore
        Annotated[SignalR, Tag("SignalR")]
        | Annotated[NotTypedModel, Tag("NotTypedModel")],
        Field(discriminator=Discriminator(TypedModel._get_type_name)),
    ]

    class Container(BaseModel):
        m: BadUnion

    # Test that trying to validate a Union using TypedModel.get_type_name fails if not
    # all members are TypedModel

    assert TypedModel._get_type_name(NotTypedModel()) is None  # type: ignore

    with pytest.raises(ValidationError):
        Container(m=NotTypedModel()).model_dump_json()


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    keys = [k for k, _ in pairs]
    assert len(keys) == len(set(keys)), f"Duplicate keys in JSON object: {keys}"
    return dict(pairs)


def test_serialize_default_widgets_after_schema_generation():
    """Default widget instances must serialize cleanly after schemas are generated.

    Widgets such as the default `TextWrite()` of `SignalRW` are instantiated when
    their class is defined. Schema generation must not change the models in a way
    that makes those pre-existing instances mismatch their serializer
    """
    Device.model_json_schema()
    Formatter.create_schema()

    device = Device(
        label="label",
        children=[
            SignalRW(name="Width", write_pv="WIDTH", read_pv="WIDTH_RBV"),
            SignalW(name="Height", write_pv="HEIGHT"),
            SignalR(name="Out", read_pv="OUT"),
        ],
    )

    device_json = device.model_dump_json()

    serialized = json.loads(device_json, object_pairs_hook=_reject_duplicate_keys)
    assert serialized["type"] == "Device"
    assert serialized["children"][0]["write_widget"]["type"] == "TextWrite"
    assert Device.model_validate_json(device_json) == device


def test_type_in_schema_of_subclass_defined_later():
    class LateWidget(TextRead):
        pass

    schema = LateWidget.model_json_schema()
    assert schema["properties"]["type"]["const"] == "LateWidget"
    assert LateWidget().model_dump()["type"] == "LateWidget"


def test_validate_rejects_mismatched_type():
    with pytest.raises(ValidationError):
        TextWrite.model_validate({"type": "TextRead"})
    assert TextWrite.model_validate({"type": "TextWrite"}) == TextWrite()
