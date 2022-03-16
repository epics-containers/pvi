import os
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

    if output_path.is_file():
        output_path = output_path.parent
        expected_path = expected_path.parent

    if os.environ.get("PVI_REGENERATE_OUTPUT", None):
        # We were asked to regenerate output, so copy output files to expected
        for output_file in output_path.iterdir():
            shutil.copy(output_file, expected_path / output_file.name)

    for output_file in output_path.iterdir():
        expected_child = expected_path / output_file.relative_to(output_path)
        assert expected_child.read_text() == output_file.read_text()


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
        "pilatusDetectorParameters.template",
        "pilatusDetectorParamSet.h",
        "pilatusDetector.pvi.device.yaml",
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
        ("pilatusParameters.bob", "dls.pvi.formatter.yaml"),
    ],
)
def test_format(tmp_path, filename, formatter):
    expected_path = HERE / "produce_format" / "output" / filename
    input_path = HERE / "produce_format" / "input"
    formatter_path = input_path / formatter
    assert_output_matches(
        expected_path,
        "format --yaml-paths " + str(input_path),
        tmp_path / filename,
        PILATUS_PRODUCER,
        formatter_path,
    )


def test_convert(tmp_path):
    expected_path = HERE / "convert" / "output"
    input_path = HERE / "convert" / "input"
    assert_output_matches(
        expected_path,
        "convert asyn --yaml-paths " + str(input_path),
        tmp_path,
        input_path / "pilatusDetector.cpp",
        input_path / "pilatusDetector.h",
        input_path / "pilatus.template",
    )
