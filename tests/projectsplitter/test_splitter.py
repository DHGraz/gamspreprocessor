"Unit tests for gamspreprocessor.projectsplitter.splitter module."

import json
import logging
from pathlib import Path

import pytest

# pylint: disable=protected-access
from gamspreprocessor.projectsplitter import bookkeeper
from gamspreprocessor.projectsplitter.lidoobjectsource import LIDOObjectSource
from gamspreprocessor.projectsplitter.objectsource import ObjectSource
from gamspreprocessor.projectsplitter.splitter import ProjectSplitter, guess_format
from gamspreprocessor.projectsplitter.teiobjectsource import TEIObjectSource


def test_guess_format(shared_datadir):
    """Make sure the usage of the formatdetector lib is correct."""
    mimetype, subtype = guess_format(shared_datadir / "projects" / "TEI_1.xml")
    assert mimetype == "application/tei+xml"
    assert subtype == "TEI"


def test_init(shared_datadir, tmp_path):
    "Test the initialization of the ProjectSplitter object."
    outputdir = tmp_path / "objects"
    project_dir = shared_datadir / "projects"

    splitter = ProjectSplitter(outputdir, project_dir)
    assert splitter.output_dir == outputdir
    assert splitter.project_dir == project_dir
    assert splitter.output_dir.is_dir()
    assert splitter.replace_existing_object_dirs is False


def test_init_with_existing_dir(shared_datadir, tmp_path, caplog):
    outputdir = tmp_path / "objects"
    project_dir = shared_datadir / "projects"

    # If we replace existing object directories, we should a debug message
    with caplog.at_level(logging.DEBUG):
        ProjectSplitter(outputdir, project_dir, replace_existing_object_dirs=True)
    assert "Existing object directories will be replaced" in caplog.text


@pytest.mark.parametrize(
    "filename, explicit_format, expected_type",
    [
        ("TEI_1.xml", "tei", TEIObjectSource),
        ("LIDO_1.xml", "lido", LIDOObjectSource),
        ("foo.txt", "auto", ObjectSource),
    ],
)
def test_make_object_source(
    filename, explicit_format, expected_type, shared_datadir, tmp_path
):
    "Test the creation of an ObjectSource object."
    outputdir = tmp_path / "objects"
    project_dir = shared_datadir / "projects"

    splitter = ProjectSplitter(outputdir, project_dir)
    # the file to run the test against
    source_file = project_dir / filename

    # default format is auto
    assert isinstance(splitter.make_object_source(source_file), expected_type)

    # use explicit auto
    assert isinstance(splitter.make_object_source(source_file, "auto"), expected_type)

    # use explicit format
    assert isinstance(
        splitter.make_object_source(source_file, explicit_format), expected_type
    )


def test_split(shared_datadir, tmp_path):
    "Test splitting a file into an object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    splitter = ProjectSplitter(target_dir, source_dir)

    # self, sourcefile: Path, objecttype: str = "auto", strip_prefix=False
    testfile = source_dir / "foo.pdf"
    result = splitter.split(testfile)
    assert len(result) == 1
    assert all(f.is_file() for f in result)


def test_split_tei(shared_datadir, tmp_path):
    "Test splitting a file into an object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"

    splitter = ProjectSplitter(target_dir, source_dir)
    testfile = source_dir / "TEI_1.xml"

    # with pytest.warns(UserWarning, match=r"colon"):
    result = splitter.split(testfile, "tei")
    assert len(result) == 3  # noqa: PLR2004
    assert all(f.is_file() for f in result)

    # strip path
    filenames = [f.name for f in result]

    assert "TEI_1.xml" in filenames
    assert "IMG.1" in filenames
    assert "image02.jpeg" in filenames

    # check if the object id has changed in the TEI file
    tei_file = target_dir / "hsa.letter.12137" / "TEI_1.xml"
    with (tei_file).open(encoding="utf-8", newline="") as f:
        content = f.read()
    assert ">hsa.letter.12137</idno>" in content


# def test_split_lido(shared_datadir, tmp_path):
#     "Test splitting a file into an object directory."
#     source_dir = shared_datadir / "projects"
#     target_dir = tmp_path / "objects"
#     testfile = source_dir / "LIDO_1.xml"

#     splitter = ProjectSplitter(target_dir, source_dir)
#     with pytest.warns(UserWarning, match=r"colon"):
#         result = splitter.split(testfile, "lido")
#     assert len(result) == 3
#     assert all(f.is_file() for f in result)

#     filenames = [f.name for f in result]

#     assert "LIDO_1.xml" in filenames
#     assert "image01.jpeg" in filenames
#     assert "image01.jpeg" in filenames


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


def test_strip_with_no_strip_prefix_and_from_content(
    shared_datadir, tmp_path, monkeypatch
):
    "When strip_prefix is False the prefix should not be removed and we expect a warning."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"

    splitter = ProjectSplitter(target_dir, source_dir)

    testfile = source_dir / "TEI_1.xml"
    # monkeypatch.setattr(splitter, "extract_pid", lambda x, y, z: ("obj1", True))
    result = splitter.split(testfile, strip_prefix=False)
    assert len(result) == 3
    assert all(f.is_file() for f in result)

    tei_file = target_dir / "o%3Ahsa.letter.12137" / "TEI_1.xml"
    with tei_file.open(encoding="utf-8", newline="") as f:
        content = f.read()
    assert ">o:hsa.letter.12137</idno>" in content


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
