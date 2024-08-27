"Unit tests for gamspreprocessor.projectsplitter.splitter module."
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from gamspreprocessor.projectsplitter import bookkeeper
from gamspreprocessor.projectsplitter.splitter import ProjectSplitter

def test_init(shared_datadir, tmp_path):
    "Test the initialization of the ProjectSplitter object."
    from gamspreprocessor.projectsplitter.splitter import ProjectSplitter

    outputdir = tmp_path / "objects"
    project_dir = shared_datadir / "projects"
    
    splitter = ProjectSplitter(outputdir, project_dir)
    assert splitter.outputdir == outputdir
    assert splitter.project_dir == project_dir
    assert splitter.outputdir.is_dir()

def test_split(shared_datadir, tmp_path):
    "Test splitting a file into an object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    testfile = source_dir / "foo.pdf"

    splitter = ProjectSplitter(target_dir, source_dir)    
    result = splitter.split(testfile)
    assert len(result) == 1
    assert all([f.is_file() for f in result])

def test_split_tei(shared_datadir, tmp_path):
    "Test splitting a file into an object directory."   
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    testfile = source_dir / "TEI_1.xml"

    splitter = ProjectSplitter(target_dir, source_dir)    
    result = splitter.split(testfile, "tei")
    assert len(result) == 3
    assert all([f.is_file() for f in result])


def test_split_invalid_filename(shared_datadir, tmp_path):
    "Test splitting a file into an object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    testfile = source_dir / "füß.pdf"

    splitter = ProjectSplitter(target_dir, source_dir)    
    with pytest.raises(ValueError) as excinfo:
        splitter.split(testfile)
    assert "does not match the allowed pattern" in str(excinfo.value)


def test_update_bookkeeper(shared_datadir, tmp_path):
    "Test updating the bookkeeper with all files in the project directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"

    # We create a splitter first and then add a new file to the project directory
    splitter = ProjectSplitter(target_dir, source_dir)    
    newfile = source_dir / "newfoo.txt"
    newfile.write_text("foo")
    splitter.update_bookkeeper()

    # make sure the Bookkeeper knows about the new file
    bkfile = source_dir / bookkeeper.BookKeeper.FILENAME
    assert bkfile.is_file()
    bk = bookkeeper.BookKeeper(source_dir)
    assert bk._data[str(newfile)] is False


def test_reset(shared_datadir, tmp_path):
    "Test resetting the bookkeeper."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"

    splitter = ProjectSplitter(target_dir, source_dir)    

    # after creating the splitter, bookkeeping data should exist
    bk = bookkeeper.BookKeeper(source_dir)
    assert len(bk._data) > 0

    splitter.reset()
    
    # resetting the bookkeeper should be empty
    bkfile = source_dir / bookkeeper.BookKeeper.FILENAME
    assert bkfile.is_file()
    
    bk = bookkeeper.BookKeeper(source_dir)
    assert len(bk._data) == 0


def test_extract_pid():
    "Test extracting the pid from a path via _extract_pid."
    assert ProjectSplitter.extract_pid(Path("foo/bar/TEI_1.xml")) == "TEI_1"
    assert ProjectSplitter.extract_pid(Path("foo/bar/o:foo.bar.1.jpg")) == "o:foo.bar.1"