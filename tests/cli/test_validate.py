"""Tests for the validate CLI subcommand."""

from pathlib import Path
from unittest.mock import Mock, patch

import click
import pytest
from click.testing import CliRunner
from gamslib.objectdir import ObjectDirectoryValidationError

from gamspreprocessor.cli.validate import validate


@pytest.fixture(name="cli_runner")
def cli_runner_fixture():
    """Provide a Click CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_context():
    """Provide a mock Click context."""
    ctx = Mock(spec=click.Context)
    ctx.params = {"quiet": False}
    return ctx


def test_validate_not_a_directory(cli_runner):
    """Test validate raises error when start_dir is not a directory."""
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(validate, ["/nonexistent/path"])
        assert result.exit_code != 0
    #   assert "is not a directory" in result.output


def test_validate_successful_single_dir(cli_runner, mock_context):
    """Test successful validation of a single object directory."""
    with cli_runner.isolated_filesystem():
        Path("test_obj").mkdir()
        with patch(
            "gamspreprocessor.cli.validate.click.get_current_context",
            return_value=mock_context,
        ):
            with patch(
                "gamspreprocessor.cli.validate.find_object_folders",
                return_value=[Path("test_obj")],
            ):
                with patch("gamspreprocessor.cli.validate.validate_object_dir"):
                    result = cli_runner.invoke(validate, ["."])
                    assert result.exit_code == 0
                    assert "Validation completed" in result.output


def test_validate_multiple_dirs_all_valid(cli_runner, mock_context):
    """Test validation of multiple valid object directories."""
    with cli_runner.isolated_filesystem():
        for i in range(3):
            Path(f"test_obj_{i}").mkdir()
        dirs = [Path(f"test_obj_{i}") for i in range(3)]
        with patch(
            "gamspreprocessor.cli.validate.click.get_current_context",
            return_value=mock_context,
        ):
            with patch(
                "gamspreprocessor.cli.validate.find_object_folders", return_value=dirs
            ):
                with patch("gamspreprocessor.cli.validate.validate_object_dir"):
                    result = cli_runner.invoke(validate, ["."])
                    assert result.exit_code == 0
                    assert "All 3 object directories are valid" in result.output


def test_validate_failure_without_continue(cli_runner, mock_context):
    """Test validation stops on first failure without --continue-on-error."""
    with cli_runner.isolated_filesystem():
        Path("test_obj").mkdir()
        with patch(
            "gamspreprocessor.cli.validate.click.get_current_context",
            return_value=mock_context,
        ):
            with patch(
                "gamspreprocessor.cli.validate.find_object_folders",
                return_value=[Path("test_obj")],
            ):
                with patch(
                    "gamspreprocessor.cli.validate.validate_object_dir",
                    side_effect=ObjectDirectoryValidationError("Invalid"),
                ):
                    result = cli_runner.invoke(validate, ["."])
                    assert result.exit_code != 0
                    assert "failed validation" in result.output


def test_validate_failure_with_continue(cli_runner, mock_context):
    """Test validation continues on error with --continue-on-error flag."""
    with cli_runner.isolated_filesystem():
        for i in range(2):
            Path(f"test_obj_{i}").mkdir()
        dirs = [Path(f"test_obj_{i}") for i in range(2)]
        with patch(
            "gamspreprocessor.cli.validate.click.get_current_context",
            return_value=mock_context,
        ):
            with patch(
                "gamspreprocessor.cli.validate.find_object_folders", return_value=dirs
            ):
                with patch(
                    "gamspreprocessor.cli.validate.validate_object_dir",
                    side_effect=[None, ObjectDirectoryValidationError("Invalid")],
                ):
                    result = cli_runner.invoke(validate, ["--continue-on-error", "."])
                    assert result.exit_code != 0
                    assert "1/2 object directories failed validation" in result.output


def test_validate_quiet_mode(cli_runner, mock_context):
    """Test validate in quiet mode produces no progress output."""
    mock_context.params = {"quiet": True}
    with cli_runner.isolated_filesystem():
        Path("test_obj").mkdir()
        with patch(
            "gamspreprocessor.cli.validate.click.get_current_context",
            return_value=mock_context,
        ):
            with patch(
                "gamspreprocessor.cli.validate.find_object_folders",
                return_value=[Path("test_obj")],
            ):
                with patch("gamspreprocessor.cli.validate.validate_object_dir"):
                    result = cli_runner.invoke(validate, ["."])
                    assert "." not in result.output
                    assert "Validation completed" not in result.output


def test_validate_error_log_creation(cli_runner, mock_context):
    """Test that validation_errors.log is created on failure."""
    with cli_runner.isolated_filesystem():
        Path("test_obj").mkdir()
        with patch(
            "gamspreprocessor.cli.validate.click.get_current_context",
            return_value=mock_context,
        ):
            with patch(
                "gamspreprocessor.cli.validate.find_object_folders",
                return_value=[Path("test_obj")],
            ):
                with patch(
                    "gamspreprocessor.cli.validate.validate_object_dir",
                    side_effect=ObjectDirectoryValidationError("Test error"),
                ):
                    cli_runner.invoke(validate, ["."])
                    assert Path("validation_errors.log").exists()
                    with open("validation_errors.log") as f:
                        assert "Test error" in f.read()
