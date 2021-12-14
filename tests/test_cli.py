from pathlib import Path

import pytest
from typer.testing import CliRunner

from pvi import __version__
from pvi.__main__ import app

HERE = Path(__file__).parent


def test_version():
    result = CliRunner().invoke(app, ["--version"])
    assert result.exit_code == 0, result
    assert result.stdout == __version__ + "\n"


def assert_output_matches(
    expected_path: Path, cmd: str, output_path: Path, *paths: Path
):
    args = [cmd, str(output_path)] + [str(p) for p in paths]
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result
    assert output_path.read_text() == expected_path.read_text()


@pytest.mark.parametrize(
    "filename",
    [
        "pvi.device.schema.json",
        "pvi.producer.schema.json",
        "pvi.formatter.schema.json",
    ],
)
def test_schemas(tmp_path, filename):
    expected_path = HERE.parent / "schemas" / filename
    assert_output_matches(expected_path, "schema", tmp_path / filename)


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
    expected_path = HERE / "produce_format" / "output" / filename
    producer_path = HERE / "produce_format" / "input" / "pilatus.pvi.producer.yaml"
    assert_output_matches(expected_path, "produce", tmp_path / filename, producer_path)


@pytest.mark.parametrize(
    "filename,formatter",
    [
        ("pilatusParameters.edl", "dls.pvi.formatter.yaml"),
        ("pilatusParameters.adl", "aps.pvi.formatter.yaml"),
    ],
)
def test_format(tmp_path, filename, formatter):
    expected_path = HERE / "produce_format" / "output" / filename
    producer_path = HERE / "produce_format" / "input" / "pilatus.pvi.producer.yaml"
    formatter_path = HERE / "produce_format" / "input" / formatter
    assert_output_matches(
        expected_path, "format", tmp_path / filename, producer_path, formatter_path
    )
