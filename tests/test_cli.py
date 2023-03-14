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
    "filename,formatter",
    [
        ("mixedWidgets.adl", "aps.adl.pvi.formatter.yaml"),
        ("mixedWidgets.edl", "dls.edl.pvi.formatter.yaml"),
        ("mixedWidgets.bob", "dls.bob.pvi.formatter.yaml"),
    ],
)
def test_format(tmp_path, filename, formatter):
    expected_path = HERE / "format" / "output" / filename
    input_path = HERE / "format" / "input"
    formatter_path = input_path / formatter
    assert_output_matches(
        expected_path,
        "format --yaml-path " + str(input_path),
        tmp_path / filename,
        HERE / "format" / "input" / "mixedWidgets.pvi.device.yaml",
        formatter_path,
    )


def test_convert(tmp_path):
    expected_path = HERE / "convert" / "output"
    input_path = HERE / "convert" / "input"
    assert_output_matches(
        expected_path,
        "convert device",
        tmp_path,
        input_path / "simDetector.h",
        "--template",
        input_path / "simDetector.template",
    )
