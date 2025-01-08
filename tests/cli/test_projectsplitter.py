"Tests for the projectsplitter command line interface."

import json
import os
from pathlib import Path
from click.testing import CliRunner

# from gamspreprocessor.cli.projectsplitter import cli
from gamspreprocessor.cli.main import cli
from gamspreprocessor.projectsplitter.bookkeeper import BookKeeper
import pytest


def test_projectsplitter():
    "The basic test is that '--help' does not lead to an error."
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_split_project(datadir, tmp_path):
    "Test the splitproject split command."
    runner = CliRunner()
    obj_file = os.path.join(datadir, "TEI_1.xml")
    with pytest.warns(UserWarning, match="colon"):
        result = runner.invoke(cli, ["splitproject", "split", "-o", tmp_path, obj_file])
    assert result.exit_code == 0
    assert "Created 1 object dirs, containing 3 files." in result.output


def test_split_project_exclusive_options(datadir, tmp_path):
    "file-list and sourcefiles are exclusive options."

    file_list_file = tmp_path / "file_list.txt"
    outputdir = tmp_path / "objects"
    outputdir.mkdir()
    file_list_file.touch()

    runner = CliRunner()

    # using both --file-list and sourcefiles should raise an error
    result = runner.invoke(
        cli,
        [
            "splitproject",
            "split",
            "-o",
            outputdir,
            "--file-list",
            str(file_list_file),
            ("sourcefiles1", "sourcefile2"),
        ],
    )
    assert result.exit_code == 1
    assert "You cannot use both" in result.output


def test_find_unhandled_missing_bookkeeping_file(datadir):
    "The bookkeeper file does not exist until the splitter has been run at least once."
    runner = CliRunner()
    result = runner.invoke(cli, ["splitproject", "showunhandled", str(datadir)])
    assert result.exit_code == 1
    assert "No bookkeeper file found" in result.output


def test_find_unhandled_no_found(datadir):
    "Test the find-unhandled command with existing bookkeeping file and no unhandled files."
    # create the bookkeeper file
    data = {
        "image01.jpeg": ["foo"],
        "image02.jpeg": ["foo"],
        "LIDO_1.xml": ["foo"],
        "TEI_1.xml": ["bar"],
    }
    bk_file = datadir / BookKeeper.FILENAME
    bk_file.write_text(json.dumps(data))
    runner = CliRunner()
    result = runner.invoke(cli, ["splitproject", "showunhandled", str(datadir)])

    assert result.exit_code == 0
    assert "No unhandled files found" in result.output


def test_find_unhandled_one_found(datadir):
    "Test the find-unhandled command with existing bookkeeping file."
    # create the bookkeeper file
    data = {
        "image01.jpeg": ["foo"],
        "image02.jpeg": [],
        "LIDO_1.xml": ["foo"],
        "TEI_1.xml": ["foo"],
    }
    bk_file = datadir / BookKeeper.FILENAME
    bk_file.write_text(json.dumps(data))
    runner = CliRunner()
    result = runner.invoke(cli, ["splitproject", "showunhandled", str(datadir)])

    assert result.exit_code == 0
    assert "Found 1 unhandled file" in result.output
    assert "image02.jpeg" in result.output


def test_find_unhandled_multiple_found(datadir):
    "Test the find-unhandled command with existing bookkeeping file and 2 unhandled files."
    # create the bookkeeper file
    data = {
        "image01.jpeg": ["foo"],
        "image02.jpeg": [],
        "LIDO_1.xml": [],
        "TEI_1.xml": ["bar"],
    }
    bk_file = datadir / BookKeeper.FILENAME
    bk_file.write_text(json.dumps(data))
    runner = CliRunner()
    result = runner.invoke(cli, ["splitproject", "showunhandled", str(datadir)])

    assert result.exit_code == 0
    assert "Found 2 unhandled files" in result.output
    assert "image02.jpeg" in result.output
    assert "LIDO_1.xml" in result.output


def test_read_from_filelist(datadir, tmp_path):
    "Test the splitproject split command with --file-list option."
    runner = CliRunner()
    file_list_file = tmp_path / "file_list.txt"
    outputdir = tmp_path / "objects"
    outputdir.mkdir()
    file_list_file.write_text(f"{datadir}/TEI_1.xml\n{datadir}/LIDO_1.xml\n")
    result = runner.invoke(
        cli,
        [
            "splitproject",
            "split",
            "-o",
            outputdir,
            "--strip-prefix",
            "--file-list",
            str(file_list_file),
        ],
    )
    assert result.exit_code == 0
    assert "Created 2 object dirs, containing 4 files." in result.output


def test_split_project_no_source_files(datadir, tmp_path):
    "Test the splitproject split command with no source files."
    runner = CliRunner()
    outputdir = tmp_path / "objects"
    outputdir.mkdir()
    result = runner.invoke(cli, ["splitproject", "split", "-o", outputdir])
    assert result.exit_code == 1
    assert "No processable source files found." in result.output


def test_object_file_already_exists(datadir, tmp_path):
    "Test the splitproject split command with an object directory that already exists."
    runner = CliRunner()
    obj_file = os.path.join(datadir, "TEI_1.xml")
    outputdir = tmp_path / "objects"
    outputdir.mkdir()
    with pytest.warns(UserWarning, match="colon"):
        result = runner.invoke(
            cli, ["splitproject", "split", "-o", outputdir, obj_file]
        )
    assert result.exit_code == 0
    with pytest.warns(UserWarning, match="colon"):
        result = runner.invoke(
            cli, ["splitproject", "split", "-o", outputdir, obj_file]
        )
    assert result.exit_code == 1
    assert "Object directory for" in result.output
    assert "already exists" in result.output
    assert "Use '--replace' to overwrite the object directory" in result.output
    assert "or delete the directory by hand" in result.output


def test_reset(datadir, tmp_path):
    "Test the splitproject split command with the --reset option."

    def extract_from_bookkeeper(bookkeeper_file: Path, filename: str):
        bk_data = json.loads(bookkeeper_file.read_text())
        for key, value in bk_data.items():
            if key.endswith(filename):
                return value

    runner = CliRunner()
    obj_file = os.path.join(datadir, "TEI_1.xml")
    outputdir = tmp_path / "objects"
    bookkepper_file = outputdir / BookKeeper.FILENAME
    outputdir.mkdir()

    # we create some objects to fill the bookkeeper
    with pytest.warns(UserWarning, match="colon"):
        result = runner.invoke(
            cli, ["splitproject", "split", "-o", outputdir, obj_file]
        )
    assert result.exit_code == 0
    assert bookkepper_file.exists()
    # make sure TEI_1.xml has entries in the bookkeeper
    assert extract_from_bookkeeper(bookkepper_file, "TEI_1.xml")

    obj_file = os.path.join(datadir, "LIDO_1.xml")
    with pytest.warns(UserWarning, match="colon"):
        runner.invoke(
            cli, ["splitproject", "split", "-o", outputdir, obj_file, "--reset"]
        )
    assert result.exit_code == 0
    assert bookkepper_file.exists()
    # make sure TEI_1.xml has no entries in the bookkeeper
    assert not extract_from_bookkeeper(bookkepper_file, "TEI_1.xml")
