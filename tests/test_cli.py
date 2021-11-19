from pathlib import Path

import pytest
from typer.testing import CliRunner

from pvi import __version__
from pvi.__main__ import cli


def test_version():
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0, result
    assert result.stdout == __version__ + "\n"


@pytest.mark.parametrize("schema", ["pvi", "producer"])
def test_schemas(tmp_path, schema):
    tmp_file = tmp_path / f"{schema}.schema.json"
    result = CliRunner().invoke(cli, ["schema", schema, str(tmp_file)])
    assert result.exit_code == 0, result
    expected = open(Path(__file__).parent.parent / f"{schema}.schema.json").read()
    assert open(tmp_file).read() == expected
