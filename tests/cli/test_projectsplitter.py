"Tests for the projectsplitter command line interface."
import json
import os
from click.testing import CliRunner

# from gamspreprocessor.cli.projectsplitter import cli
from gamspreprocessor.cli.main import cli
from gamspreprocessor.projectsplitter.bookkeeper import BookKeeper


def test_projectsplitter():
    "The basic test is that '--help' does not lead to an error."
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_split_project(datadir, tmp_path):
    "Test the splitproject split command."
    runner = CliRunner()
    obj_file = os.path.join(datadir, "TEI_1.xml")
    result = runner.invoke(cli, ["splitproject", "split", "-o", tmp_path, obj_file])
    assert result.exit_code == 0
    assert "Created 1 object dirs, containing 3 files." in result.output


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
        "image01.jpeg": True,
        "image02.jpeg": True,
        "LIDO_1.xml": True,
        "TEI_1.xml": True,
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
        "image01.jpeg": True,
        "image02.jpeg": False,
        "LIDO_1.xml": True,
        "TEI_1.xml": True,
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
        "image01.jpeg": True,
        "image02.jpeg": False,
        "LIDO_1.xml": False,
        "TEI_1.xml": True,
    }
    bk_file = datadir / BookKeeper.FILENAME
    bk_file.write_text(json.dumps(data))
    runner = CliRunner()
    result = runner.invoke(cli, ["splitproject", "showunhandled", str(datadir)])

    assert result.exit_code == 0
    assert "Found 2 unhandled files" in result.output
    assert "image02.jpeg" in result.output
    assert "LIDO_1.xml" in result.output
