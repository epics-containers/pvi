import os
import shutil
from pathlib import Path

import pytest
from typer import Typer
from typer.testing import CliRunner

# See: https://github.com/pytest-dev/pytest/issues/7409
if os.getenv("PYTEST_RAISE", "0") != "0":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call):
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo):
        raise excinfo.value


class Helper:
    @staticmethod
    def assert_output_matches(expected_path: Path, output_path: Path):
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

    @staticmethod
    def assert_cli_output_matches(
        app: Typer, expected_path: Path, cmd: str, output_path: Path, *paths: Path
    ):
        args = cmd.split() + [str(output_path)] + [str(p) for p in paths]
        result = CliRunner().invoke(app, args)
        if result.exception:
            raise result.exception

        Helper.assert_output_matches(expected_path, output_path)


@pytest.fixture
def helper():
    return Helper
