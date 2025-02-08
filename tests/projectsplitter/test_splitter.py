"Unit tests for gamspreprocessor.projectsplitter.splitter module."

import json
import logging
from pathlib import Path

import pytest

# pylint: disable=protected-access
from gamspreprocessor.projectsplitter import bookkeeper
from gamspreprocessor.projectsplitter.lidoobjectdir import LIDOObjectDirectory
from gamspreprocessor.projectsplitter.objectdir import ObjectDirectory
from gamspreprocessor.projectsplitter.splitter import ProjectSplitter
from gamspreprocessor.projectsplitter.teiobjectdir import TEIObjectDirectory


def test_init(shared_datadir, tmp_path):
    "Test the initialization of the ProjectSplitter object."
    outputdir = tmp_path / "objects"
    project_dir = shared_datadir / "projects"

    splitter = ProjectSplitter(outputdir, project_dir)
    assert splitter.output_dir == outputdir
    assert splitter.project_dir == project_dir
    assert splitter.output_dir.is_dir()


def test_init_with_existing_dir(shared_datadir, tmp_path, caplog):
    outputdir = tmp_path / "objects"
    # dummy_object = outputdir / "obj1"
    # dummy_object.mkdir(parents=True)
    project_dir = shared_datadir / "projects"
    with caplog.at_level(logging.DEBUG):
        ProjectSplitter(outputdir, project_dir, replace_existing_object_dirs=True)
    assert "Existing object directories will be replaced" in caplog.text


def test_split(shared_datadir, tmp_path):
    "Test splitting a file into an object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    testfile = source_dir / "foo.pdf"

    splitter = ProjectSplitter(target_dir, source_dir)
    result = splitter.split(testfile)
    assert len(result) == 1
    assert all(f.is_file() for f in result)


def test_split_tei(shared_datadir, tmp_path):
    "Test splitting a file into an object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    testfile = source_dir / "TEI_1.xml"

    splitter = ProjectSplitter(target_dir, source_dir)
    with pytest.warns(UserWarning, match=r"colon"):
        result = splitter.split(testfile, "tei")
    assert len(result) == 3  # noqa: PLR2004
    assert all(f.is_file() for f in result)

    filenames = [f.name for f in result]

    assert "TEI_1.xml" in filenames
    assert "image01.jpeg" in filenames
    assert "image01.jpeg" in filenames


def test_split_lido(shared_datadir, tmp_path):
    "Test splitting a file into an object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    testfile = source_dir / "LIDO_1.xml"

    splitter = ProjectSplitter(target_dir, source_dir)
    with pytest.warns(UserWarning, match=r"colon"):
        result = splitter.split(testfile, "lido")
    assert len(result) == 3
    assert all(f.is_file() for f in result)

    filenames = [f.name for f in result]

    assert "LIDO_1.xml" in filenames
    assert "image01.jpeg" in filenames
    assert "image01.jpeg" in filenames


def test_split_invalid_filename(shared_datadir, tmp_path):
    "Test splitting a file into an object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    testfile = source_dir / "füß.pdf"

    splitter = ProjectSplitter(target_dir, source_dir)
    with pytest.raises(ValueError) as excinfo:
        splitter.split(testfile)
    assert "does not match the allowed pattern" in str(excinfo.value)


def test_split_existing_object_dir(shared_datadir, tmp_path):
    "Test splitting a file into an existing object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    testfile = source_dir / "foo.pdf"

    splitter = ProjectSplitter(target_dir, source_dir)
    result = splitter.split(testfile)
    assert len(result) == 1
    assert all(f.is_file() for f in result)

    # Splitting the same file again should raise an error
    with pytest.raises(FileExistsError, match=r"already exists"):
        splitter.split(testfile)

    # Splitting the same file with replace_existing_object_dirs=True
    # should not raise an error, but still give a warning
    splitter.replace_existing_object_dirs = True
    with pytest.warns(UserWarning, match=r"Replacing object directory"):
        result = splitter.split(testfile)
    assert len(result) == 1
    assert all(f.is_file() for f in result)


def test_split_with_strip_prefix_and_from_content(
    shared_datadir, tmp_path, monkeypatch
):
    "When split_prefix is true an from_content is true, the prefix should be removed."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    testfile = source_dir / "TEI_1.xml"

    splitter = ProjectSplitter(target_dir, source_dir)
    monkeypatch.setattr(splitter, "extract_pid", lambda x, y, z: ("obj1", True))
    splitter.split(testfile, "tei", strip_prefix=True)
    obj_path, created_tei = target_dir / "obj1", "TEI_1.xml"
    tei_file = obj_path / created_tei
    assert tei_file.is_file()
    with tei_file.open(encoding="utf-8", newline="") as f:
        content = f.read()
    assert ">obj1</idno>" in content


def test_update_bookkeeper(shared_datadir, tmp_path):
    "Test updating the bookkeeper with all files in the project directory."
    project_dir = shared_datadir / "projects"
    object_dir = tmp_path / "objects"

    # We create a splitter first and then add a new file to the project directory
    splitter = ProjectSplitter(object_dir, project_dir)

    # Check if an update put all files into the bookkeeper
    splitter.update_bookkeeper()
    for path in project_dir.glob("**/*"):
        if path.is_file():
            assert str(path) in splitter._bookkeeper._data
            assert splitter._bookkeeper._data[str(path)] == []

    # add one more file and assert update adds it to the bookkeeper
    newfile = project_dir / "newfoo.txt"
    newfile.write_text("foo")
    splitter.update_bookkeeper()
    assert str(newfile) in splitter._bookkeeper._data
    assert splitter._bookkeeper._data[str(newfile)] == []


def test_reset(shared_datadir, tmp_path):
    "Test resetting the bookkeeper."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"

    splitter = ProjectSplitter(target_dir, source_dir)

    # after creating the splitter, bookkeeping data should exist
    bkfile = target_dir / bookkeeper.BookKeeper.FILENAME
    bk = bookkeeper.BookKeeper(bkfile)
    assert len(bk._data) > 0

    splitter.reset()

    data = json.loads(bkfile.read_text())
    assert len(data) == 0


def test_extract_pid(shared_datadir):
    "Test extracting the pid from a path via _extract_pid."
    tei_file = shared_datadir / "projects" / "TEI_1.xml"
    assert ProjectSplitter.extract_pid(tei_file, "tei", True) == (
        "hsa.letter.12137",
        True,
    )
    assert ProjectSplitter.extract_pid(tei_file, "tei", False) == (
        "o:hsa.letter.12137",
        True,
    )

    lido_file = shared_datadir / "projects" / "LIDO_1.xml"
    assert ProjectSplitter.extract_pid(lido_file, "lido", True) == ("ges.a-88", True)
    assert ProjectSplitter.extract_pid(lido_file, "lido", False) == ("o:ges.a-88", True)

    # Not tei nor lido
    assert ProjectSplitter.extract_pid(Path("foo/bar/foo.txt"), "csv", True) == (
        "foo",
        False,
    )
    assert ProjectSplitter.extract_pid(Path("foo/bar/foo.txt"), "csv", False) == (
        "foo",
        False,
    )


def test_instantiate_object_directory(shared_datadir, tmp_path, caplog):
    "Test the instantiation of an object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    splitter = ProjectSplitter(target_dir, source_dir)

    obj_dir = splitter.instantiate_object_directory("obj1", "application/xml", "tei")
    assert isinstance(obj_dir, TEIObjectDirectory)

    obj_dir = splitter.instantiate_object_directory("obj2", "application/xml", "lido")
    assert isinstance(obj_dir, LIDOObjectDirectory)

    with caplog.at_level(logging.DEBUG):
        obj_dir = splitter.instantiate_object_directory(
            "obj3", "application/xml", "foo"
        )
        assert type(obj_dir) is ObjectDirectory
    assert "with unspecified XML objecttype foo" in caplog.text

    # again a ObjectDirectory, but a different log message
    with caplog.at_level(logging.DEBUG):
        obj_dir = splitter.instantiate_object_directory("obj4", "text/plain", "bar")
        assert type(obj_dir) is ObjectDirectory
    assert "Detected mime type was: text/plain" in caplog.text
