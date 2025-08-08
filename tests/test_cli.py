import shutil
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


@pytest.fixture(scope="module")
def formats_to_skip():
    return {
        ".adl": ["bit_field", "array_trace", "image_read", "table_read", "table_write"],
        ".edl": ["array_trace", "image_read", "table_read", "table_write"],
        ".bob": [],
    }


@pytest.mark.parametrize(
    "widget_name",
    [
        "array_trace",
        "bit_field",
        "button_panel",
        "check_box",
        "combo_box",
        "image_read",
        "led",
        "progress_bar",
        "table_read",
        "table_write",
        "text_read",
        "text_write",
        "toggle_button",
    ],
)
@pytest.mark.parametrize(
    "formatter,format",
    [
        ("aps.adl.pvi.formatter.yaml", ".adl"),
        ("dls.edl.pvi.formatter.yaml", ".edl"),
        ("dls.bob.pvi.formatter.yaml", ".bob"),
    ],
)
def test_format(tmp_path, helper, formatter, format, widget_name, formats_to_skip):
    if widget_name in formats_to_skip[format]:
        pytest.skip(f"{widget_name} not supported in {format} format")
    filename = widget_name + format
    expected_path = HERE / "format" / "output" / "all_widgets" / filename
    input_path = HERE / "format" / "input"
    formatter_path = input_path / formatter
    helper.assert_cli_output_matches(
        app,
        expected_path,
        "format --yaml-path " + str(input_path),
        tmp_path / filename,
        input_path / "all_widgets" / (widget_name + ".pvi.device.yaml"),
        formatter_path,
    )


def test_format_parent_child(tmp_path, helper):
    expected_path = HERE / "format" / "output" / "parent_child.bob"
    input_path = HERE / "format" / "input"
    formatter_path = input_path / "dls.bob.pvi.formatter.yaml"
    helper.assert_cli_output_matches(
        app,
        expected_path,
        "format --yaml-path " + str(input_path),
        tmp_path / "parent_child.bob",
        HERE / "format" / "input" / "child.pvi.device.yaml",
        formatter_path,
    )


def test_signal_default_widgets(tmp_path, helper):
    expected_path = HERE / "format" / "output" / "signal_default_widgets.bob"
    input_path = HERE / "format" / "input"
    formatter_path = input_path / "dls.bob.pvi.formatter.yaml"
    helper.assert_cli_output_matches(
        app,
        expected_path,
        "format --yaml-path " + str(input_path),
        tmp_path / "signal_default_widgets.bob",
        HERE / "format" / "input" / "signal_default_widgets.pvi.device.yaml",
        formatter_path,
    )


def test_convert_header(tmp_path, helper):
    expected_path = HERE / "convert" / "output"
    input_path = HERE / "convert" / "input"
    helper.assert_cli_output_matches(
        app,
        expected_path,
        "convert device",
        tmp_path,
        "--header",
        input_path / "simDetector.h",
        "--template",
        input_path / "simDetector.template",
    )


def test_convert_device_name(tmp_path, helper):
    expected_path = HERE / "convert" / "output"
    input_path = HERE / "convert" / "input"
    helper.assert_cli_output_matches(
        app,
        expected_path,
        "convert device",
        tmp_path,
        "--name",
        "Mako125B",
        "--label",
        "GenICam Mako125B",
        "--parent",
        "GenICamDriver",
        "--template",
        input_path / "Mako125B.template",
    )


def test_reconvert(tmp_path, helper):
    expected_path = HERE / "reconvert" / "output"
    input_path = HERE / "reconvert" / "input"
    # Make a copy to modify in place
    shutil.copy(
        input_path / "simDetector.pvi.device.yaml",
        tmp_path / "simDetector.pvi.device.yaml",
    )
    helper.assert_cli_output_matches(
        app,
        expected_path / "simDetector.pvi.device.yaml",
        "reconvert",
        tmp_path / "simDetector.pvi.device.yaml",
        "--template",
        input_path / "simDetectorExtra.template",
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
