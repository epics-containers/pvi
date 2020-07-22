import json
from pathlib import Path
from unittest import mock

from pvi import ChannelConfig, Group, Schema, Widget, cli

PILATUS_YAML = Path(__file__).parent / "pilatus.pvi.yaml"
PILATUS_TEMPLATE = Path(__file__).parent / "pilatus.template"
PILATUS_SOURCE = Path(__file__).parent / "pilatusDetector.cpp"
EXPECTED = Path(__file__).parent / "expected"


def test_channels():
    pilatus_schema = Schema.load(PILATUS_YAML.parent, "pilatus")
    channel_tree = pilatus_schema.producer.produce_channels(pilatus_schema.components)
    assert len(channel_tree) == 2
    assert isinstance(channel_tree[0], Group)
    channels = channel_tree[0].children
    assert len(channels) == 1
    assert isinstance(channel_tree[1], Group)
    channels = channel_tree[1].children
    assert len(channels) == 6
    assert channels[0] == ChannelConfig(
        name="ThresholdEnergy",
        label=None,
        read_pv="$(P)$(R)ThresholdEnergy_RBV",
        write_pv="$(P)$(R)ThresholdEnergy",
        widget=Widget.TEXTINPUT,
        description="""Threshold energy in keV

camserver uses this value to set the discriminators in each pixel.
It is typically set to the incident x-ray energy ($(P)$(R)Energy),
but sometimes other values may be preferable.
""",
        display_form=None,
    )


def check_generation(tmp_path: Path, fname: str):
    cli.main(["generate", str(PILATUS_YAML), str(tmp_path / fname)])
    assert open(tmp_path / fname).read() == open(EXPECTED / fname).read(), str(
        EXPECTED / fname
    )


def test_yaml(tmp_path: Path):
    check_generation(tmp_path, "pilatus.coniql.yaml")


def test_h(tmp_path: Path):
    check_generation(tmp_path, "pilatusDetectorParamSet.h")


def test_template(tmp_path: Path):
    check_generation(tmp_path, "pilatusParameters.template")


def test_csv(tmp_path: Path):
    check_generation(tmp_path, "pilatus_parameters.csv")


def test_edl(tmp_path: Path):
    check_generation(tmp_path, "pilatus_parameters.edl")


def check_conversion(tmp_path: Path):
    cli.main(
        ["convert", str(PILATUS_TEMPLATE), str(tmp_path), "-s", str(PILATUS_SOURCE)]
    )
    assert (
        open(tmp_path / "pilatus.pvi.yaml").read()
        == open(EXPECTED / "pilatus.pvi.yaml").read()
    ), str(EXPECTED / "pilatus.pvi.yaml")
    assert (
        open(tmp_path / "pilatus_top.template").read()
        == open(EXPECTED / "pilatus_top.template").read()
    ), str(EXPECTED / "pilatus_top.template")
    assert (
        open(tmp_path / "pilatusDetector_top.cpp").read()
        == open(EXPECTED / "pilatusDetector_top.cpp").read()
    ), str(EXPECTED / "pilatusDetector_top.cpp")


def test_convert_template(tmp_path: Path):
    check_conversion(tmp_path)


def test_schema_matches_stored_one(tmp_path: Path):
    schema = str(tmp_path / "schema.json")
    cli.main(["schema", schema])
    expected = json.loads(
        open(Path(__file__).parent.parent / "pvi" / "schema.json").read()
    )
    # Don't care if version number didn't update to match if the rest is the same
    expected["title"] = mock.ANY
    actual = json.loads(open(schema).read())
    assert expected == actual
