"Unittests for the object directory class."

from pathlib import Path

import pytest

from gamspreprocessor.projectsplitter.objectdir import ObjectDirectory


def test_init(tmp_path):
    "Test the initialization of the object directory."
    obj = ObjectDirectory(tmp_path / "foo")
    assert obj.path == tmp_path / "foo"
    assert obj.path.is_dir()


def test_init_with_colon(tmp_path):
    "Test the initialization of the object directory with a colon in the name."
    obj = ObjectDirectory(tmp_path / "foo:bar")
    assert obj.path == tmp_path / "foo%3Abar"


def test_init_dir_exists(tmp_path):
    "Test the initialization of the object directory if the directory exists."

    # at the moment we ignore the case if the directory exists
    obj_dir = tmp_path / "foo"
    obj_dir.mkdir()

    with pytest.raises(FileExistsError) as excinfo:
        ObjectDirectory(obj_dir)
    assert "already exists" in str(excinfo.value)


def test_split(tmp_path):
    "Test the split method of the object directory."
    objectdir = tmp_path / "foo"
    obj = ObjectDirectory(objectdir)

    # create file to be copied
    sourcedir = tmp_path / "src"
    sourcedir.mkdir()
    sourcefile = sourcedir / "bar.txt"
    sourcefile.write_text("Hello World")

    obj.split(sourcefile)

    assert obj.files == [sourcefile]
    assert sourcefile.exists()
    assert sourcefile.read_bytes() == (objectdir / "bar.txt").read_bytes()


@pytest.mark.parametrize(
    "long, short, expected",
    [
        ("foo", "foox", ""),
        ("foo", "foo", "foo"),
        ("foxo", "foo", "o"),
        ("bar/foo", "foo", "foo"),
        ("data/find_file/foo.png", "foo.png", "foo.png"),
        ("data/find_file/foo.png", "foo/foo.png", "/foo.png"),
        ("data/find_file/bar/foo.png", "foo/foo.png", "/foo.png"),
        ("data/find_file/foo/foo.png", "foo/foo.png", "foo/foo.png"),
        ("data/find_file/foo/bar/foo.png", "foo/foo.png", "/foo.png"),
    ],
)
def test_rank_path(long, short, expected):
    rank_size = ObjectDirectory.rank_path(Path(short), Path(long))
    assert rank_size == len(expected), (
        f"Got {rank_size} instead of: {expected} (short: {short}, long: {long})"
    )


@pytest.mark.parametrize(
    "uri, expected",
    [  # the second value is the file to be found relative to 'shared_datadir / find_file' (root_dir)
        ("foo.jpeg", None),  # file does not exist
        ("foo.png", "foo.png"),  # we have a foo.ping in root_dir
        ("foo/foo.png", "foo/foo.png"), # we have a foo/foo.png in root_dir 
        ("/bar/foo.png", "bar/foo.png"), # bar/foo.png should win over foo/bar/foo.png
        ("bar/foo.png", "bar/foo.png"),  # reference is relative
        # test uri notation
        ("file:///bar/foo.png", "bar/foo.png"),
        ("http://example.com/bar/foo.png", "bar/foo.png"),
    ],
)
def test_find_file(shared_datadir, uri, expected):
    """The the find_file method of the object directory.

    We have an uri (which might also be a string representing a path), which comes from a xml ref.
    We try to find a matching file in shared_datadir. The third parameter is the file we expect to be found."
    """
    # the directory, where we start searching
    root_dir = shared_datadir / "find_file"

    result = ObjectDirectory.find_file(uri, root_dir) 
    expected_path = root_dir / expected if expected else None
    assert result == expected_path, f"Expected: {expected_path}, got: {result}"

def test_str(tmp_path):
    "Test the string representation of the object directory."

    obj_path = tmp_path / "foo"
    obj = ObjectDirectory(obj_path)
    assert str(obj) == f"ObjectDirectory('{str(obj_path)}')"
