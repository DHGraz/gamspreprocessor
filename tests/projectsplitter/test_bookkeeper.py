"""Tests for the BookKeeper class."""

import json
import os
from pathlib import Path

from gamspreprocessor.projectsplitter.bookkeeper import BookKeeper

# pylint: disable=protected-access


def test_init_no_data(tmp_path):
    "Test creating a BookKeeper object without existing data."

    bk_file = tmp_path / BookKeeper.FILENAME
    bk = BookKeeper(bk_file)

    assert bk.storage_path == bk_file
    assert len(bk._data) == 0
    assert bk._data == {}


def test_init_with_existing_data(tmp_path):
    """Test creating a BookKeeper object with existing data.

    Here we assume:
        * 2 files (foo.xml and foo.csv) have been processed before
        * 1 file d1/bar.pdf existed before but has not been processed
        * 1 file foo.pdf is new and should be added to the list
    """
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    bkfile = tmp_path / "objects" / BookKeeper.FILENAME
    bkfile.parent.mkdir()

    # let's create 3 files and assume that 2 of them have been consumed
    data = {
        os.path.abspath(os.path.join(project_dir, "foo.xml")): ["foo"],
        os.path.abspath(os.path.join(project_dir, "foo.csv")): ["bar"],
        os.path.abspath(os.path.join(project_dir, "d1/bar.pdf")): [],
    }
    with open(bkfile, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    # Now create the BookKeeper object. It should read the data from the file.
    bk = BookKeeper(bkfile)

    assert bk._data == {
        os.path.abspath(os.path.join(project_dir, "foo.xml")): ["foo"],
        os.path.abspath(os.path.join(project_dir, "foo.csv")): ["bar"],
        os.path.abspath(os.path.join(project_dir, "d1/bar.pdf")): [],
    }


def test_update(datadir):
    "After update() we should have a new file and one file removed."
    project_path = datadir / "project"
    bk_file = datadir / BookKeeper.FILENAME

    # create a BookKeeper object, run update and check if all files registered with the BookKeeper
    bk = BookKeeper(bk_file)
    bk.update(project_path)
    assert len(bk._data) == len(['foo.csv', 'foo.xml', 'foo.pdf', 'd1/bar.pdf'])

    # add a new file and remove an existing file
    new_file = project_path / "foo.pdf"
    deleted_file = project_path / "foo.csv"
    new_file.touch()
    deleted_file.unlink()

    bk.update(project_path)

    # check if the bookkeeper has been updated correctly
    posix_deleted_file = deleted_file.absolute().as_posix()
    posix_new_file = new_file.absolute().as_posix()

    # bookkeeper should have updated data
    assert posix_deleted_file not in bk._data
    assert posix_new_file in bk._data  # the new one
    assert bk._data[posix_new_file] == []  # the new one has not been processed yet


def test_reset(tmp_path):
    "Test resetting a BookKeeper object."
    bk_file = tmp_path / BookKeeper.FILENAME
    bk = BookKeeper(bk_file)
    bk._data = {"/foo.xml": ["foo"], "/bar.xml": ["bar"]}
    bk.save()

    # make sure we have data
    bk = BookKeeper(bk_file)
    assert len(bk._data) > 0

    # run reset and check again
    bk.reset()
    assert len(bk._data) == 0

    # create bookkeeper file again and make sure it's empty
    bk = BookKeeper(bk_file)
    assert len(bk._data) == 0


def test_add_pid(tmp_path):
    "Test marking a file as consumed."
    bk_file = tmp_path / BookKeeper.FILENAME

    testfile = tmp_path / "foo.xml"

    bk = BookKeeper(bk_file)

    bk.add_pid(testfile, "id1")
    expected_key = testfile.absolute().as_posix()
    assert bk._data[expected_key] == ["id1"]

    bk.add_pid(testfile, "id2")
    assert bk._data[expected_key] == ["id1", "id2"]

def test_add_pid_str(tmp_path):
    "Test marking a file as consumed by providing a string instead of a Path."
    bk_file = tmp_path / BookKeeper.FILENAME

    testpath = tmp_path / "foo.xml"
    testfile = str(testpath)

    bk = BookKeeper(bk_file)

    bk.add_pid(testfile, "id1")
    expected_key = testpath.absolute().as_posix()
    assert bk._data[expected_key] == ["id1"]

    bk.add_pid(testfile, "id2")
    assert bk._data[expected_key] == ["id1", "id2"]


def test_remove_pid(tmp_path):
    "Test removing a PID from a file."

    bk_file = tmp_path / BookKeeper.FILENAME

    #file1 = os.path.abspath("/bar/foo.xml").as_posix()
    file1 = tmp_path / "foo.xml"
    #file2 = os.path.abspath("/foo/bar.xml").as_posix()
    file2 = tmp_path / "bar.xml"

    bk = BookKeeper(bk_file)
    bk.add_pid(file1, "foo")
    bk.add_pid(file1, "bar")
    bk.add_pid(file2, "foo")

    assert bk.get_pids_for_file(file1) == ["foo", "bar"]
    assert bk.get_pids_for_file(file2) == ["foo"]

    bk.remove_pid("foo")
    assert bk.get_pids_for_file(file1) == ["bar"]
    assert bk.get_pids_for_file(file2) == []

    bk.remove_pid("bar")
    assert bk.get_pids_for_file(file1) == []
    assert bk.get_pids_for_file(file2) == []


def test_get_unhandled(tmp_path):
    "Test getting a list of unhandled files."
    bk_file = tmp_path / BookKeeper.FILENAME

    bk = BookKeeper(bk_file)

    file1 = "foo.xml"
    file2 = "foo.csv"
    file3 = "foo.pdf"

    bk._data[file1] = ["bar"]
    bk._data[file2] = []
    bk._data[file3] = []

    unhandled = bk.get_unhandled()

    assert len(unhandled) == 2
    assert Path(file2) in unhandled
    assert Path(file3) in unhandled


def test_save(tmp_path):
    "Test writing data to disk."
    bk_file = tmp_path / BookKeeper.FILENAME

    bk = BookKeeper(bk_file)

    # first without any data
    bk.save()
    with open(bk_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data == bk._data

    # and now with some data
    file1 = "foo.xml"
    file2 = "foo.csv"
    bk._data[file1] = []
    bk._data[file2] = ["foo"]
    bk.save()
    with open(os.path.join(tmp_path, BookKeeper.FILENAME), encoding="utf-8") as f:
        data = json.load(f)
    assert data == bk._data


def test_update_with_ignores(datadir, tmp_path):
    "Test that the BookKeeper update method ignores unwanted files."
    project_path = datadir / "project"
    obj_csv = project_path / "object.csv"
    ds_csv = project_path / "datastreams.csv"
    logfile = project_path / "foo.log"
    obj_csv.touch()
    ds_csv.touch()
    logfile.touch()

    bk_file = datadir / BookKeeper.FILENAME

    # create a BookKeeper object, run update and check if all files registered with the BookKeeper
    bk = BookKeeper(bk_file)
    bk.update(project_path)
    assert len(bk._data) == 4

    filenames = [os.path.basename(file) for file in bk._data]

    assert "object.csv" not in filenames
    assert "datastreams.csv" not in filenames
    assert "foo.log" not in filenames
    assert "foo.xml" in filenames
    assert "foo.csv" in filenames
    assert "bar.pdf" in filenames
    assert "foo.pdf" in filenames
