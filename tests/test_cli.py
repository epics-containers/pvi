import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pvi import __version__
from pvi.__main__ import app

HERE = Path(__file__).parent
PILATUS_PRODUCER = (
    HERE / "produce_format" / "input" / "pilatusDetector.pvi.producer.yaml"
)


def test_cli_version():
    cmd = [sys.executable, "-m", "pvi", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__


def assert_output_matches(
    expected_path: Path, cmd: str, output_path: Path, *paths: Path
):
    args = cmd.split() + [str(output_path)] + [str(p) for p in paths]
    result = CliRunner().invoke(app, args)
    if result.exception:
        raise result.exception
    if expected_path.is_dir():
        for child in expected_path.iterdir():
            output_child = output_path / child.relative_to(expected_path)
            assert output_child.read_text() == child.read_text()
    else:
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
    assert_output_matches(
        expected_path, "produce", tmp_path / filename, PILATUS_PRODUCER
    )


@pytest.mark.parametrize(
    "filename,formatter",
    [
        ("pilatusParameters.edl", "dls.pvi.formatter.yaml"),
        ("pilatusParameters.adl", "aps.pvi.formatter.yaml"),
    ],
)
def test_format(tmp_path, filename, formatter):
    expected_path = HERE / "produce_format" / "output" / filename
    formatter_path = HERE / "produce_format" / "input" / formatter
    assert_output_matches(
        expected_path, "format", tmp_path / filename, PILATUS_PRODUCER, formatter_path
    )


def test_convert(tmp_path):
    expected_path = HERE / "convert" / "output"
    input_path = HERE / "convert" / "input"
    for parent in ["ADDriver", "asynNDArrayDriver"]:
        shutil.copy(input_path / f"{parent}.pvi.producer.yaml", tmp_path)
    assert_output_matches(
        expected_path,
        "convert asyn",
        tmp_path,
        input_path / "pilatus.template",
        input_path / "pilatusDetector.cpp",
        input_path / "pilatusDetector.h",
    )
