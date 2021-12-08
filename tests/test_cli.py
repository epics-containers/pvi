from pathlib import Path

import pytest
from typer.testing import CliRunner

from pvi import __version__
from pvi.__main__ import cli

HERE = Path(__file__).parent


def test_version():
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0, result
    assert result.stdout == __version__ + "\n"


def assert_output_matches(expected_path: Path, cmd: str, *paths: Path):
    args = [cmd] + [str(p) for p in paths]
    output_path = paths[-1]
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0, result
    assert output_path.read_text() == expected_path.read_text()


@pytest.mark.parametrize("schema", ["device", "producer", "formatter"])
def test_schemas(tmp_path, schema):
    expected_path = HERE.parent / "schemas" / f"pvi.{schema}.schema.json"
    output_path = tmp_path / f"pvi.{schema}.schema.json"
    assert_output_matches(expected_path, "schema", output_path)


@pytest.mark.parametrize(
    "filename",
    [
        "pilatusParameters.csv",
        "pilatusParameters.template",
        "pilatusDetectorParamSet.h",
        "pilatus.pvi.device.yaml",
    ],
)
def test_produce(tmp_path, filename):
    expected_path = HERE / "produce" / filename
    producer_path = HERE / "pilatus.pvi.producer.yaml"
    assert_output_matches(expected_path, "produce", producer_path, tmp_path / filename)


@pytest.mark.parametrize(
    "filename,formatter", [("pilatusParamSet.edl", "dls.pvi.formatter.yaml")],
)
def test_format(tmp_path, filename, formatter):
    expected_path = HERE / "format" / filename
    producer_path = HERE / "pilatus.pvi.producer.yaml"
    formatter_path = HERE / formatter
    assert_output_matches(
        expected_path, "format", producer_path, formatter_path, tmp_path / filename
    )
