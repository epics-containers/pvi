import subprocess
import sys
from pathlib import Path

import pytest

from pvi import __version__
from pvi.__main__ import app

HERE = Path(__file__).parent


def test_cli_version():
    cmd = [sys.executable, "-m", "pvi", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__


@pytest.mark.parametrize(
    "filename",
    [
        "pvi.device.schema.json",
        "pvi.formatter.schema.json",
    ],
)
def test_schemas(tmp_path, helper, filename):
    expected_path = HERE.parent / "schemas" / filename
    helper.assert_cli_output_matches(app, expected_path, "schema", tmp_path / filename)


@pytest.mark.parametrize(
    "filename,formatter",
    [
        ("mixedWidgets.adl", "aps.adl.pvi.formatter.yaml"),
        ("mixedWidgets.edl", "dls.edl.pvi.formatter.yaml"),
        ("mixedWidgets.bob", "dls.bob.pvi.formatter.yaml"),
    ],
)
def test_format(tmp_path, helper, filename, formatter):
    expected_path = HERE / "format" / "output" / filename
    input_path = HERE / "format" / "input"
    formatter_path = input_path / formatter
    helper.assert_cli_output_matches(
        app,
        expected_path,
        "format --yaml-path " + str(input_path),
        tmp_path / filename,
        HERE / "format" / "input" / "mixedWidgets.pvi.device.yaml",
        formatter_path,
    )


def test_convert(tmp_path, helper):
    expected_path = HERE / "convert" / "output"
    input_path = HERE / "convert" / "input"
    helper.assert_cli_output_matches(
        app,
        expected_path,
        "convert device",
        tmp_path,
        input_path / "simDetector.h",
        "--template",
        input_path / "simDetector.template",
    )


@pytest.mark.parametrize(
    "input_yaml,formatter,output",
    [
        (
            "static_table.pvi.device.yaml",
            "dls.edl.pvi.formatter.yaml",
            "static_table.edl",
        ),
        (
            "static_table.pvi.device.yaml",
            "dls.bob.pvi.formatter.yaml",
            "static_table.bob",
        ),
        (
            "static_table.pvi.device.yaml",
            "aps.pvi.formatter.yaml",
            "static_table.adl",
        ),
    ],
)
def test_static_table(tmp_path, helper, input_yaml, formatter, output):
    expected_path = HERE / "format" / "output" / output
    input_path = HERE / "format" / "input"
    formatter_path = HERE / "../formatters/" / formatter
    helper.assert_cli_output_matches(
        app,
        expected_path,
        "format --yaml-path " + str(input_path),
        tmp_path / output,
        input_path / input_yaml,
        formatter_path,
    )
