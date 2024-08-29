"""Tests for the BookKeeper class."""

import json
import os
from pathlib import Path

from gamspreprocessor.projectsplitter.bookkeeper import BookKeeper

# pylint: disable=protected-access


def test_init_no_data(tmp_path):
    "Test creating a BookKeeper object without existing data."

    bk = BookKeeper(tmp_path)
    assert bk.project_dir == tmp_path
    assert bk.datafile == tmp_path / BookKeeper.FILENAME
    assert len(bk._data) == 0
    assert bk._data == {}


def test_init_with_existing_data(tmp_path):
    """Test creating a BookKeeper object with existing data.

    Here we assume:
        * 2 files (foo.xml and foo.csv) have been processed before
        * 1 file d1/bar.pdf existed before but has not been processed
        * 1 file foo.pdf is new and should be added to the list
    """

    data = {
        os.path.join(tmp_path, "foo.xml"): True,
        os.path.join(tmp_path, "foo.csv"): True,
        os.path.join(tmp_path, "d1/bar.pdf"): False,
    }
    with open(os.path.join(tmp_path, BookKeeper.FILENAME), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    bk = BookKeeper(tmp_path)

    assert bk._data == {
        os.path.join(tmp_path, "foo.xml"): True,
        os.path.join(tmp_path, "foo.csv"): True,
        os.path.join(tmp_path, "d1/bar.pdf"): False,
    }


def test_update(datadir):
    "After update() we should have a new file and one file removed."
    data = {
        os.path.join(datadir, "foo.xml"): ["123"],
        os.path.join(datadir, "foo.csv"): ["123", "xyz"],
        os.path.join(datadir, "d1/bar.pdf"): [],
        os.path.join(datadir, "removed.pdf"): [],
    }
    with open(os.path.join(datadir, BookKeeper.FILENAME), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    bk = BookKeeper(datadir)
    bk.update()
    assert os.path.join(datadir, "removed.pdf") not in bk._data
    assert os.path.join(datadir, "foo.pdf") in bk._data  # the new one
    assert not bk._data[os.path.join(datadir, "foo.pdf")]

    assert bk._data[os.path.join(datadir, "foo.xml")]
    assert bk._data[os.path.join(datadir, "foo.csv")]
    assert not bk._data[os.path.join(datadir, "d1/bar.pdf")]


def test_reset(tmp_path):
    "Test resetting a BookKeeper object."
    data = {
        os.path.join(tmp_path, "foo.xml"): True,
        os.path.join(tmp_path, "foo.csv"): True,
    }
    with open(os.path.join(tmp_path, BookKeeper.FILENAME), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    bk = BookKeeper(tmp_path)
    bk.reset()
    assert bk._data == {}
    with open(os.path.join(tmp_path, BookKeeper.FILENAME), encoding="utf-8") as f:
        data = json.load(f)
    assert data == {}


def test_add_pid(tmp_path):
    "Test marking a file as consumed."
    bk = BookKeeper(tmp_path)
    the_file = os.path.join(tmp_path, "foo.xml")
    bk._data[the_file] = []

    bk.add_pid(the_file, "foo")
    assert bk._data[the_file] == ["foo"]

    bk.add_pid(the_file, "bar")
    assert bk._data[the_file] == ["foo", "bar"]


def test_remove_pid(tmp_path):
    "Test removing a PID from a file."

    file1 = os.path.join(tmp_path, "foo.xml")
    file2 = os.path.join(tmp_path, "bar.xml")

    bk = BookKeeper(tmp_path)
    bk.add_pid(file1, "foo")
    bk.add_pid(file1, "bar")
    bk.add_pid(file2, "foo")

    assert bk._data[file1] == ["foo", "bar"]
    assert bk._data[file2] == ["foo"]

    bk.remove_pid("foo")
    assert bk._data[file1] == ["bar"]
    assert bk._data[file2] == []

    bk.remove_pid("bar")
    assert bk._data[file1] == []
    assert bk._data[file2] == []


def test_get_unhandled(tmp_path):
    "Test getting a list of unhandled files."
    bk = BookKeeper(tmp_path)

    file1 = os.path.join(tmp_path, "foo.xml")
    file2 = os.path.join(tmp_path, "foo.csv")
    file3 = os.path.join(tmp_path, "foo.pdf")
    bk._data[file1] = True
    bk._data[file2] = False
    bk._data[file3] = False

    unhandled = bk.get_unhandled()

    assert len(unhandled) == 2
    assert Path(file2) in unhandled
    assert Path(file3) in unhandled


def test_dump(tmp_path):
    "Test writing data to disk."
    bk = BookKeeper(tmp_path)
    bk.dump()
    with open(os.path.join(tmp_path, BookKeeper.FILENAME), encoding="utf-8") as f:
        data = json.load(f)
    assert data == bk._data


def test_file_to_be_ignored(datadir):
    "Test that the BookKeeper ignores its own data file."
    to_be_ignored = ["foo.log"]  # add more if needed
    for file in to_be_ignored:
        datadir.joinpath(file).touch()

    # the datafile must be parseable by json
    with open(os.path.join(datadir, BookKeeper.FILENAME), "w", encoding="utf-8") as f:
        f.write("{}")
    to_be_ignored.append(BookKeeper.FILENAME)
    bk = BookKeeper(datadir)

    for file in bk._data:
        assert (
            os.path.basename(file) not in to_be_ignored
        ), f"File {file} should have been ignored."
