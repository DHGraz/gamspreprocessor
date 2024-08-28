"Tests for the main CLI entry point."
from click.testing import CliRunner
from gamspreprocessor.cli.main import cli
from gamspreprocessor import APP_NAME, VERSION


def test_main():
    "The basic test is that '--help' does not lead to an error."
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_main_version():
    "Compare the version number with the one in the package."
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"{APP_NAME}, version {VERSION}\n"
