"Tests for the main CLI entry point."

import logging
import click
from click.testing import CliRunner
import pytest
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


def test_main_quiet_and_verbose():
    "Test --quiet and --verbose options."
    runner = CliRunner()

    # using both --quiet and --verbose should raise an error
    result = runner.invoke(cli, ["--quiet", "--verbose", "project", "init"])
    assert result.exit_code == 2
    assert "Cannot use --quiet and --verbose together." in result.output

    runner.invoke(cli, ["--quiet", "project", "init"])
    assert logging.getLogger().getEffectiveLevel() == logging.ERROR

    runner.invoke(cli, ["--verbose", "project", "init"])
    assert logging.getLogger().getEffectiveLevel() == logging.DEBUG
