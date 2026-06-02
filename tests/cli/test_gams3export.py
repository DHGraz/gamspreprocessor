"Tests for the gams3export CLI command."

import logging
from pathlib import Path
from types import SimpleNamespace

from click.testing import CliRunner

from gamspreprocessor.cli.gams3export import gams3export
from gamspreprocessor.cli.main import cli
from gamspreprocessor.gams3.object import ExportStatus


def _reset_gams3export_file_logger() -> None:
    logger_name = "gamspreprocessor.cli.gams3export.file"

    file_logger = logging.getLogger(logger_name)
    for handler in file_logger.handlers[:]:
        handler.close()
        file_logger.removeHandler(handler)


def test_gams3export_help_uses_command_usage() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["gams3export", "--help"])

    assert result.exit_code == 0
    assert "Usage: cli gams3export [OPTIONS] PATTERN" in result.output
    assert "COMMAND [ARGS]" not in result.output
    assert "--colon-replacement" in result.output


def test_gams3export_fails_for_missing_output_dir() -> None:
    runner = CliRunner()
    _reset_gams3export_file_logger()

    with runner.isolated_filesystem():
        result = runner.invoke(gams3export, ["--output-dir", "missing", "o:test*"])

        assert result.exit_code != 0
        assert "Output directory 'missing' does not exist or is not a directory." in result.output

        log_file = Path("gams3export.log")
        assert log_file.exists()
        assert "Output directory does not exist or is not a directory: missing" in log_file.read_text(encoding="utf-8")


def test_gams3export_exports_objects_and_logs_to_file(monkeypatch) -> None:
    runner = CliRunner()
    _reset_gams3export_file_logger()

    exported_one = SimpleNamespace(
        pid="o:test.1",
        status=ExportStatus.EXPORTED,
        exported_files=[Path("TEI_SOURCE.xml"), Path("DC.xml")],
        warnings=[],
        errors=[],
    )
    replaced_two = SimpleNamespace(
        pid="o:test.2",
        status=ExportStatus.REPLACED,
        exported_files=[Path("METS.xml")],
        warnings=["minor warning"],
        errors=[],
    )

    def fake_export_objects(
        pid_pattern: str,
        output_dir: Path,
        **kwargs,
    ):
        assert pid_pattern == "o:test*"
        assert output_dir == Path("objects")
        assert kwargs == {
            "overwrite": True,
            "base_url": "https://example.com/archive",
            "strip_prefix": True,
            "colon_replacement": "_",
        }
        yield exported_one
        yield replaced_two

    monkeypatch.setattr(
        "gamspreprocessor.cli.gams3export.export_objects",
        fake_export_objects,
    )

    with runner.isolated_filesystem():
        Path("objects").mkdir()
        result = runner.invoke(
            gams3export,
            [
                "--output-dir",
                "objects",
                "--replace",
                "--strip-prefix",
                "--base-url",
                "https://example.com/archive",
                "--colon-replacement",
                "_",
                "o:test*",
            ],
        )

        assert result.exit_code == 0
        assert "Exported object 'o:test.1' with status EXPORTED: 2 datastreams exported, 0 warnings, 0 errors." in result.output
        assert "Exported object 'o:test.2' with status REPLACED: 1 datastreams exported, 1 warnings, 0 errors." in result.output
        assert "Exported 1 objects with 3 datastreams, replaced 1 objects, ignored 0 objects, with 1 warnings and 0 errors." in result.output

        log_output = Path("gams3export.log").read_text(encoding="utf-8")
        assert "Starting gams3export: pattern=o:test* output_dir=objects replace=True strip_prefix=True base_url=https://example.com/archive" in log_output
        assert "Exported object 'o:test.1' with status EXPORTED: 2 datastreams exported, 0 warnings, 0 errors" in log_output
        assert "Exported object 'o:test.2' with status REPLACED: 1 datastreams exported, 1 warnings, 0 errors" in log_output
        assert "Warnings for object 'o:test.2': minor warning" in log_output


def test_gams3export_logs_errors_for_error_status(monkeypatch) -> None:
    runner = CliRunner()
    _reset_gams3export_file_logger()
    failed_object = SimpleNamespace(
        pid="o:test.error",
        status=ExportStatus.ERROR,
        exported_files=[],
        warnings=[],
        errors=["failed to export datastream", "cleanup failed"],
    )

    def fake_export_objects(
        pid_pattern: str,
        output_dir: Path,
        **kwargs,
    ):
        assert pid_pattern == "o:error*"
        assert output_dir == Path("objects")
        assert kwargs == {
            "overwrite": False,
            "base_url": "https://gams.uni-graz.at/archive",
            "strip_prefix": False,
            "colon_replacement": "%3A",
        }
        yield failed_object

    monkeypatch.setattr(
        "gamspreprocessor.cli.gams3export.export_objects",
        fake_export_objects,
    )

    with runner.isolated_filesystem():
        Path("objects").mkdir()
        result = runner.invoke(
            gams3export,
            ["--output-dir", "objects", "o:error*"],
        )

        assert result.exit_code == 0
        assert "Error while exporting object o:test.error. See log file for details" in result.output
        log_output = Path("gams3export.log").read_text(encoding="utf-8")
        assert "Error while exporting object 'o:test.error': failed to export datastream" in log_output
        assert "Error while exporting object 'o:test.error': cleanup failed" in log_output
