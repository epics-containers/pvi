import json
from pathlib import Path
from unittest import mock

from pvi import ChannelConfig, Group, Schema, Widget, cli

ROOT = Path(__file__).parent
PILATUS_YAML = ROOT / "pvi/pilatusDetector.pvi.yaml"
PILATUS_TEMPLATE = ROOT / "pilatus.template"
PILATUS_CPP = ROOT / "pilatusDetector.cpp"
PILATUS_H = ROOT / "pilatusDetector.h"
EXPECTED = ROOT / "expected"


def test_channels():
    pilatus_schema = Schema.load(PILATUS_YAML.parent, "pilatusDetector")
    channel_tree = pilatus_schema.producer.produce_channels(pilatus_schema.components)
    assert len(channel_tree) == 1
    assert isinstance(channel_tree[0], Group)
    channels = channel_tree[0].children
    assert len(channels) == 48
    assert channels[43] == ChannelConfig(
        name="ThresholdEnergy",
        label=None,
        read_pv="$(P)$(R)ThresholdEnergy_RBV",
        write_pv="$(P)$(R)ThresholdEnergy",
        widget=Widget.TEXTINPUT,
        description="Energy threshold",
        display_form=None,
    )


def check_generation(tmp_path: Path, fname: str):
    cli.main(["generate", str(PILATUS_YAML), str(tmp_path / fname)])
    assert open(tmp_path / fname).read() == open(EXPECTED / fname).read(), str(
        EXPECTED / fname
    )


def test_coniql_yaml(tmp_path: Path):
    check_generation(tmp_path, "pilatusParamSet.coniql.yaml")


def test_h(tmp_path: Path):
    check_generation(tmp_path, "pilatusDetectorParamSet.h")


def test_template(tmp_path: Path):
    check_generation(tmp_path, "pilatusParamSet.template")


def test_csv(tmp_path: Path):
    check_generation(tmp_path, "pilatusParamSet.csv")


def test_edl(tmp_path: Path):
    check_generation(tmp_path, "pilatusParamSet.edl")


def test_adl(tmp_path: Path):
    check_generation(tmp_path, "pilatusParamSet.adl")


def check_conversion(tmp_path: Path):
    cli.main(
        [
            "convert",
            str(PILATUS_TEMPLATE),
            str(tmp_path),
            "--cpp",
            str(PILATUS_CPP),
            "--header",
            str(PILATUS_H),
            "--root",
            str(ROOT),
        ]
    )
    assert (
        open(tmp_path / "pilatusDetector.pvi.yaml").read() == open(PILATUS_YAML).read()
    ), str(PILATUS_YAML)
    assert (
        open(tmp_path / "pilatus.template").read()
        == open(EXPECTED / "pilatus.template").read()
    ), str(EXPECTED / "pilatus.template")
    assert (
        open(tmp_path / "pilatusDetector.cpp").read()
        == open(EXPECTED / "pilatusDetector.cpp").read()
    ), str(EXPECTED / "pilatusDetector.cpp")
    assert (
        open(tmp_path / "pilatusDetector.h").read()
        == open(EXPECTED / "pilatusDetector.h").read()
    ), str(EXPECTED / "pilatusDetector.h")


def test_convert_template(tmp_path: Path):
    check_conversion(tmp_path)


def test_schema_matches_stored_one(tmp_path: Path):
    schema = str(tmp_path / "schema.json")
    cli.main(["schema", schema])
    expected = json.loads(
        open(Path(__file__).parent.parent / "src" / "pvi" / "schema.json").read()
    )
    # Don't care if version number didn't update to match if the rest is the same
    expected["title"] = mock.ANY
    actual = json.loads(open(schema).read())
    assert expected == actual
