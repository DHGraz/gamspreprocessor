import pytest
from pathlib import Path
from gamspreprocessor import projectsplitter 
from gamspreprocessor.projectsplitter.teiobjectsource import TEIObjectSource
from gamspreprocessor.projectsplitter.lidoobjectsource import LIDOObjectSource
from gamspreprocessor.projectsplitter.genericobjectsource import GenericObjectSource

from gamslib.formatdetect.formatinfo import SubType
from gamslib.formatdetect import FormatInfo

# @pytest.fixture
# def mock_detect_format(mocker):
#     return mocker.patch('gamslib.formatdetect.detect_format')

def test_make_object_source_missing_file():
    source_file = Path("/path/to/nonexistent.file") 
    with pytest.raises(FileNotFoundError):
        projectsplitter.make_object_source(source_file)


def test_make_object_source_auto_tei(monkeypatch, shared_datadir):
    "Test make_object_source with auto format detection for TEI files"
    source_file = shared_datadir / "projects" / "TEI_1.xml"
    # we fake the format detector used by make_object_source
    monkeypatch.setattr(projectsplitter, 'detect_format', lambda x: FormatInfo('foodector', "application/tei+xml", SubType.TEI ))

    obj_src = projectsplitter.make_object_source(source_file, use_format="auto")
    assert isinstance(obj_src, TEIObjectSource)

def test_make_object_source_auto_lido(monkeypatch, shared_datadir):
    "Test make_object_source with auto format detection for LIDO files"
    source_file = shared_datadir / "projects" / "LIDO_1.xml"
    # we fake the format detector used by make_object_source
    monkeypatch.setattr(projectsplitter, 'detect_format', lambda x: FormatInfo('foodector', "application/xml", SubType.LIDO ))

    obj_src = projectsplitter.make_object_source(source_file, use_format="auto")
    assert isinstance(obj_src, LIDOObjectSource)

def test_make_object_source_auto_generic(monkeypatch, shared_datadir):
    "Test make_object_source with auto format detection for non-TEI and non-LIDO files"
    source_file = shared_datadir / "projects" / "foo.pdf"
    # we fake the format detector used by make_object_source
    monkeypatch.setattr(projectsplitter, 'detect_format', lambda x: FormatInfo('foodector', "application/pdf", None ))

    obj_src = projectsplitter.make_object_source(source_file, use_format="auto")
    assert isinstance(obj_src, GenericObjectSource)


def test_make_object_source_tei(shared_datadir):
    "Test make_object_source with exlicit TEI format"
    source_file = shared_datadir / "projects" / "TEI_1.xml"
    obj_src = projectsplitter.make_object_source(source_file, use_format="tei")
    assert isinstance(obj_src, TEIObjectSource)

def test_make_object_source_lido(shared_datadir):
    "Test make_object_source with exlicit LIDO format"
    source_file = shared_datadir / "projects" / "LIDO_1.xml"
    obj_src = projectsplitter.make_object_source(source_file, use_format="lido")
    assert isinstance(obj_src, LIDOObjectSource)
    

def test_make_object_source_invalid_format(tmp_path):
    source_file = tmp_path / "foo.xml"
    source_file.write_text("<foo></foo>")   
    with pytest.raises(ValueError):
        projectsplitter.make_object_source(source_file, use_format="invalid")
