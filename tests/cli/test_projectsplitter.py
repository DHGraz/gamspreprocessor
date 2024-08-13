import os
from pathlib import Path
import click
from click.testing import CliRunner
import pytest
#from gamspreprocessor.cli.projectsplitter import cli
from gamspreprocessor.cli.main import cli
from gamspreprocessor.projectsplitter.bookkeeper import BookKeeper


def test_projectsplitter():
    "The basic test is that '--help' does not lead to an error."
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0

def test_split_project(datadir, tmp_path):
    "Test the split-project command."
    runner = CliRunner()
    obj_file = os.path.join(datadir, "TEI_1.xml")
    result = runner.invoke(cli, ["split", "-o", tmp_path, obj_file])
    assert result.exit_code == 0
    assert "Created 1 object dirs, containing 3 files." in result.output


# FIXME: This test is not working. It should return all unhandled files.
def _test_find_unhandled(datadir):
    "Should return all unhandled files."
    runner = CliRunner()
#    obj_file = os.path.join(datadir, "TEI_1.xml")
    x = datadir / BookKeeper.FILENAME
    x.write_text("{'foo/bar.xml': false}")
    result = runner.invoke(cli, ["splitproject", "foo", datadir])
    assert result.output == "Found 1 unhandled files:\nfoo/bar.xml\n"
    #assert result.exit_code == 0
    #print("==>",result.output)
    #print("==>",result)
    #assert result.exit_code == 1
    #assert "No bookkeeper file found. Did you run split-project?" in result.output
    # with pytest.raises(click.ClickException):
    #     result = runner.invoke(cli, ["find-unhandled", datadir])
    #         #"No bookkeeper file found. Did you run split-project?"):
    # assert "foo." in result.output
    #assert False



    #assert "Found 0 unhandled files" in result.output
    #assert "No unhandled files found"