from pathlib import Path

import pytest

from gamspreprocessor.projectsplitter.objectdir import ObjectDirectory, find_file, rank_path


def test_init(tmp_path):
    "Test the initialization of the object directory."
    obj = ObjectDirectory(tmp_path / "foo")
    assert obj.path == tmp_path / "foo"
    assert obj.path.is_dir()

def test_init_dir_exists_no_replace(tmp_path):    
    "Test the initialization of the object directory if the directory exists."

    # at the moment we ignore the case if the directory exists
    obj_dir = tmp_path / "foo"
    obj_dir.mkdir()

    with pytest.raises(FileExistsError) as excinfo:
        ObjectDirectory(obj_dir)
    assert "already exists" in str(excinfo.value)

def test_init_dir_exists_with_replace(tmp_path):    
    "Test the initialization of the object directory if the directory exists an replace is set to True."

    # at the moment we ignore the case if the directory exists
    obj_dir = tmp_path / "foo"
    obj_dir.mkdir()

    # Add a file to make sure that the object is replaced
    (obj_dir / "foo.txt").write_text("Hello World")

    obj = ObjectDirectory(obj_dir, True)
    assert obj.path == tmp_path / "foo"
    assert obj.path.is_dir()

    # directory should be empty
    assert obj.files == []
    
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
    
    
def test_rank_path():
    """Test the rank path function.

    In short the rank ist the number of identical chars counted from the end
    """
    assert rank_path(Path("foo"), Path("foox")) == 0
    assert rank_path(Path("foo"), Path("foo")) == 3
    assert rank_path(Path("foxo"), Path("foo")) == 1
    assert rank_path(Path("bar/foo"), Path("foo")) == 3


def test_find_file(shared_datadir):
    "Test finding a file in a directory."
    root_dir = shared_datadir / "find_file"

    assert find_file("foo.png", root_dir) == root_dir / "foo.png"
    assert find_file("foo/foo.png", root_dir) == root_dir / "foo" / "foo.png"
    assert find_file("/bar/foo.png", shared_datadir) == root_dir / "bar" / "foo.png"

    # bar/foo.png should win over foo/bar/foo.png
    assert find_file("bar/foo.png", shared_datadir) == root_dir / "bar" / "foo.png"

    assert find_file("file:///bar/foo.png", shared_datadir) == root_dir / "bar" / "foo.png"
    assert (
        find_file("http://example.com/bar/foo.png", shared_datadir)
        == root_dir / "bar" / "foo.png"
    )
    assert find_file("foo.jpeg", shared_datadir) is None