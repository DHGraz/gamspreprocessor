"Unit tests for gamspreprocessor.projectsplitter.splitter module."

import json
import logging
from pathlib import Path
import shutil

import pytest

# pylint: disable=protected-access
from gamspreprocessor.projectsplitter import bookkeeper
from gamspreprocessor.projectsplitter.lidoobjectsource import LIDOObjectSource
from gamspreprocessor.projectsplitter.genericobjectsource import GenericObjectSource
from gamspreprocessor.projectsplitter.splitter import ProjectSplitter, guess_format
from gamspreprocessor.projectsplitter.teiobjectsource import TEIObjectSource
from gamslib.formatdetect.formatinfo import SubType

from xml.etree import ElementTree as ET

def test_guess_format(shared_datadir):
    """Make sure the usage of the formatdetector lib is correct."""
    mimetype, subtype = guess_format(shared_datadir / "projects" / "TEI_1.xml")
    assert mimetype == "application/tei+xml"
    assert subtype == SubType.TEI


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
        ("foo.txt", "auto", GenericObjectSource),
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


def test_split_lido(shared_datadir, tmp_path):
    "Test splitting a file into an object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    testfile = source_dir / "LIDO_1.xml"

    splitter = ProjectSplitter(target_dir, source_dir)
    #with pytest.warns(UserWarning, match=r"colon"):
    result = splitter.split(testfile, "lido")
    assert len(result) == 3
    assert all(f.is_file() for f in result)

    filenames = [f.name for f in result]

    assert "LIDO_1.xml" in filenames
    assert "IMAGE.1" in filenames  
    assert "image02.jpeg" in filenames


def test_split_invalid_filename(shared_datadir, tmp_path):
    "Test splitting a file into an object directory."
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    testfile = source_dir / "füß.pdf"
    shutil.copy(source_dir / "foo.pdf", testfile)

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
    with pytest.warns(UserWarning, match=r"colon"):
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
            bk_path = path.resolve().as_posix()
            assert bk_path in splitter._bookkeeper._data
            assert splitter._bookkeeper._data[bk_path] == []
            

    # add one more file and assert update adds it to the bookkeeper
    newfile = project_dir / "newfoo.txt"
    newfile.write_text("foo")
    splitter.update_bookkeeper()
    assert str(newfile.resolve().as_posix()) in splitter._bookkeeper._data
    assert splitter._bookkeeper._data[newfile.resolve().as_posix()] == []


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

def test_make_object_source_invalid_format(shared_datadir, tmp_path):
    """Test that make_object_source raises ValueError for invalid format types."""
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    
    splitter = ProjectSplitter(target_dir, source_dir)
    source_file = source_dir / "foo.pdf"
    
    with pytest.raises(ValueError, match=r"Invalid format type"):
        splitter.make_object_source(source_file, "invalid_format")
    
    with pytest.raises(ValueError, match=r"Invalid format type"):
        splitter.make_object_source(source_file, "xml")


def test_make_object_source_strip_parameters(shared_datadir, tmp_path, monkeypatch):
    """Test that strip_prefix and strip_extension parameters are correctly passed."""
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    
    splitter = ProjectSplitter(target_dir, source_dir)
    tei_file = source_dir / "TEI_1.xml"
    lido_file = source_dir / "LIDO_1.xml"
    generic_file = source_dir / "foo.pdf"
    
    # Test with different strip combinations
    tei_source = splitter.make_object_source(tei_file, "tei", strip_prefix=False, strip_extension=True)
    assert isinstance(tei_source, TEIObjectSource)
    assert tei_source.strip_prefix is False
    assert tei_source.strip_extension is True
    
    lido_source = splitter.make_object_source(lido_file, "lido", strip_prefix=True, strip_extension=False)
    assert isinstance(lido_source, LIDOObjectSource)
    assert lido_source.strip_prefix is True
    assert lido_source.strip_extension is False
    
    generic_source = splitter.make_object_source(generic_file, "auto", strip_prefix=False, strip_extension=False)
    assert isinstance(generic_source, GenericObjectSource)
    assert generic_source.strip_prefix is False
    assert generic_source.strip_extension is False


def test_make_object_source_case_insensitive(shared_datadir, tmp_path):
    """Test that the format parameter is case-insensitive."""
    source_dir = shared_datadir / "projects"
    target_dir = tmp_path / "objects"
    
    splitter = ProjectSplitter(target_dir, source_dir)
    tei_file = source_dir / "TEI_1.xml"
    lido_file = source_dir / "LIDO_1.xml"
    
    # Test with uppercase formats
    tei_source = splitter.make_object_source(tei_file, "TEI")
    assert isinstance(tei_source, TEIObjectSource)
    
    lido_source = splitter.make_object_source(lido_file, "LIDO")
    assert isinstance(lido_source, LIDOObjectSource)
    
    # Test with mixed case formats
    tei_source = splitter.make_object_source(tei_file, "TeI")
    assert isinstance(tei_source, TEIObjectSource)
    
    lido_source = splitter.make_object_source(lido_file, "LiDo")
    assert isinstance(lido_source, LIDOObjectSource)


# def test_extract_pid_lido(shared_datadir):
#     "Test extracting PID from a LIDO file."
#     testfile = shared_datadir / "projects" / "LIDO_1.xml"
#     pid, from_content = ProjectSplitter.extract_pid(testfile, "lido", strip_prefix=True)
#     assert pid == "ges.a-88"
#     assert from_content is True

#     pid, from_content = ProjectSplitter.extract_pid(testfile, "lido", strip_prefix=False)
#     assert pid == "o:ges.a-88"
#     assert from_content is True


# def test_extract_pid_unknown_format(shared_datadir):
#     "Test extracting PID from a file with unknown format."
#     testfile = shared_datadir / "projects" / "foo.txt"
#     pid, from_content = ProjectSplitter.extract_pid(testfile, "unknown", strip_prefix=True)
#     assert pid == "foo"
#     assert from_content is False

#     pid, from_content = ProjectSplitter.extract_pid(testfile, "unknown", strip_prefix=False)
#     assert pid == "foo"
#     assert from_content is False


# def test_extract_pid_no_pid_in_content(shared_datadir):
#     "Test extracting PID from a file with no PID in content."
#     testfile = shared_datadir / "projects" / "TEI_1.xml"

#     # we remove the pid from the content
#     root = ET.parse(testfile).getroot()
#     for elem in root.iter():
#         if elem.tag.endswith("idno"):
#             elem.text = ""
#     testfile.write_text(ET.tostring(root, encoding="unicode"))

#     pid, from_content = ProjectSplitter.extract_pid(testfile, "tei", strip_prefix=True)
#     assert pid == "TEI_1"
#     assert from_content is False

#     pid, from_content = ProjectSplitter.extract_pid(testfile, "tei", strip_prefix=False)
#     assert pid == "TEI_1"
#     assert from_content is False

