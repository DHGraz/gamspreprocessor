"""Tests for the BookKeeper class.
"""
import json
import os


from gamspreprocessor.projectsplitter.bookkeeper import BookKeeper
 

def test_init(datadir):
    "Test creating a BookKeeper object without existing data."

    bk = BookKeeper(datadir)
    assert bk.root_dir == str(datadir)

    assert bk._data == {
        os.path.join(datadir, "foo.xml"): False,
        os.path.join(datadir, "foo.pdf"): False,
        os.path.join(datadir, "foo.csv"): False,
        os.path.join(datadir, "d1/bar.pdf"): False,
    }


def test_init_with_existing_data(datadir):
    """Test creating a BookKeeper object with existing data.

    Here we assume:
        * 2 files (foo.xml and foo.csv) have been processed before
        * 1 file d1/bar.pdf existed before but has not been processed
        * 1 file foo.pdf is new and should be added to the list
    """

    data = {
        os.path.join(datadir, "foo.xml"): True,
        os.path.join(datadir, "foo.csv"): True,
        os.path.join(datadir, "d1/bar.pdf"): False,
    }
    with open(os.path.join(datadir, BookKeeper.FILENAME), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    bk = BookKeeper(datadir)
    assert bk._data == {
        os.path.join(datadir, "foo.xml"): True,
        os.path.join(datadir, "foo.csv"): True,
        os.path.join(datadir, "foo.pdf"): False,
        os.path.join(datadir, "d1/bar.pdf"): False,
    }


def test_reset(datadir):
    "Test resetting a BookKeeper object."
    data = {
        os.path.join(datadir, "foo.xml"): True,
        os.path.join(datadir, "foo.csv"): True,
    }
    with open(os.path.join(datadir, BookKeeper.FILENAME), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    bk = BookKeeper(datadir)
    bk.reset()
    assert bk._data == {}
    with open(os.path.join(datadir, BookKeeper.FILENAME), encoding="utf-8") as f:
        data = json.load(f)
    assert data == {}


def test_consumed(datadir):
    "Test marking a file as consumed."
    bk = BookKeeper(datadir)
    # check initial state
    testfile = os.path.join(datadir, "foo.xml")
    assert not bk._data[testfile]

    bk.consumed(os.path.join(datadir, "foo.xml"))
    assert bk._data[os.path.join(testfile)]


def test_get_unhandled(datadir):
    "Test getting a list of unhandled files."
    bk = BookKeeper(datadir)
    assert len(bk.get_unhandled()) == 4
    bk.consumed(os.path.join(datadir, "foo.xml"))
    assert len(bk.get_unhandled()) == 3


def test_dump(datadir):
    "Test writing data to disk."
    bk = BookKeeper(datadir)
    bk.dump()
    with open(os.path.join(datadir, BookKeeper.FILENAME), encoding="utf-8") as f:
        data = json.load(f)
    assert data == bk._data


def test_file_to_be_ignored(datadir):
    "Test that the BookKeeper ignores its own data file."
    to_be_ignored = ["foo.log"]  # add more if needed
    for file in to_be_ignored:
        with open(os.path.join(datadir, file), "w", encoding="utf-8") as f:
            f.write("dummy content")
            f.flush()

    # the datafile must be parseable by json
    with open(os.path.join(datadir, BookKeeper.FILENAME), "w", encoding="utf-8") as f:
        f.write("{}")
    to_be_ignored.append(BookKeeper.FILENAME)
    bk = BookKeeper(datadir)

    for file in bk._data:
        assert (
            os.path.basename(file) not in to_be_ignored
        ), f"File {file} should have been ignored."
