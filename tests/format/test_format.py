from pathlib import Path

import pytest
from typer.testing import CliRunner

from pvi.__main__ import cli


@pytest.mark.parametrize(
    "filename,formatter", [("pilatusParamSet.edl", "DLSFormatter")],
)
def test_format(tmp_path, filename, formatter):
    tmp_file = tmp_path / filename
    producer = Path(__file__).parent.parent / "pilatusDetector.pvi.producer.yaml"
    formatter = Path(__file__).parent.parent / "dls.pvi.formatter.yaml"
    result = CliRunner().invoke(
        cli, ["format", str(producer), str(formatter), str(tmp_file)]
    )
    assert result.exit_code == 0, result
    expected = open(Path(__file__).parent / filename).read()
    assert open(tmp_file).read() == expected
