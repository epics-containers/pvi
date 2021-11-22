from pathlib import Path

import pytest
from typer.testing import CliRunner

from pvi.__main__ import cli


@pytest.mark.parametrize(
    "filename",
    ["pilatusParamSet.template", "pilatusDetectorParamSet.h", "pilatus.pvi.json"],
)
def test_produce(tmp_path, filename):
    tmp_file = tmp_path / filename
    yaml = Path(__file__).parent / "pilatusDetector.pvi.yaml"
    result = CliRunner().invoke(cli, ["produce", str(yaml), str(tmp_file)])
    assert result.exit_code == 0, result
    expected = open(Path(__file__).parent / filename).read()
    assert open(tmp_file).read() == expected
