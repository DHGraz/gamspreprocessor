import pytest
from gamspreprocessor.projectsplitter.teiobjectsource import TEIObjectSource
from xml.etree import ElementTree as ET



def test_pid_keep_prefix(shared_datadir):
    """Test the split method of TEIObjectDirectory without removing the prefix.
    
    The pid is comming from the content of the file.
    """
    tei_file = shared_datadir / "projects" / "TEI_1.xml"
    src = TEIObjectSource(tei_file, strip_prefix=False, strip_extension=False)
    with pytest.warns(UserWarning):
        assert src.pid == "o%3Ahsa.letter.12137"


def test_pid_remove_prefix(shared_datadir):
    """Test the split method of TEIObjectDirectory with removing the prefix.
    
    The pid is comming from the content of the file.
    """
    tei_file = shared_datadir / "projects" / "TEI_1.xml"
    src = TEIObjectSource(tei_file, strip_prefix=True, strip_extension=False)
    assert src.pid == "hsa.letter.12137"

def test_pid_from_filename(tmp_path, shared_datadir):
    """If no pid is found in the content, the pid is extracted from the filename.
    """
    # first we create a tei with an empty idno element
    tree = ET.parse(shared_datadir / "projects" / "TEI_1.xml")
    root = tree.getroot()
    root.find(".//{http://www.tei-c.org/ns/1.0}idno").text = ""
    tei_file = tmp_path / "TEI_1.xml"
    tree.write(tei_file)

    
    src = TEIObjectSource(tei_file, strip_prefix=True, strip_extension=False)
    with pytest.warns(UserWarning):
        assert src.pid == "TEI_1.xml"

def test_save(tmp_path, shared_datadir):
    """Test the save method."""
    tei_file = shared_datadir / "projects" / "TEI_1.xml"
    src = TEIObjectSource(tei_file, strip_prefix=True, strip_extension=False)
    
    obj_dir = tmp_path / "object1"
    obj_dir.mkdir()
    src.save(obj_dir)
    assert (obj_dir / "TEI_1.xml").exists()

def test_save(shared_datadir, tmp_path):
    """Test the save method."""
    src_file = shared_datadir / "projects" / "TEI_1.xml"
    src = TEIObjectSource(src_file, strip_prefix=True, strip_extension=False)

    obj_dir = tmp_path / "object1"
    obj_dir.mkdir()

    result = src.save(obj_dir)    
    assert (obj_dir / "TEI_1.xml").is_file()
    assert (obj_dir / "IMG.1").is_file()
    assert (obj_dir / "image02.jpeg").is_file()

def test_save_strip_extension(shared_datadir, tmp_path):
    """Test the save method with strip_extension=True."""
    src_file = shared_datadir / "projects" / "TEI_1.xml"
    src = TEIObjectSource(src_file, strip_prefix=True, strip_extension=True)

    obj_dir = tmp_path / "object1"
    obj_dir.mkdir()

    result = src.save(obj_dir)    
    assert (obj_dir / "TEI_1").is_file()
    assert (obj_dir / "IMG.1").is_file()
    assert (obj_dir / "image02").is_file()    