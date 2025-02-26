import pytest
from gamspreprocessor.projectsplitter.teiobjectsource import TEIObjectSource
from xml.etree import ElementTree as ET



def test_pid_keep_prefix(shared_datadir):
    """Test the split method of TEIObjectDirectory without removing the prefix.
    
    The pid is comming from the content of the file.
    """
    tei_file = shared_datadir / "projects" / "TEI_1.xml"
    src = TEIObjectSource(tei_file, strip_prefix=False, strip_extension=False)
    
    assert src.pid == "o:hsa.letter.12137"
    with pytest.warns(UserWarning, match=r"contains a colon"):        
        assert src.safe_pid == "o%3Ahsa.letter.12137" 

    with pytest.warns(UserWarning, match=r"contains a colon"):
        new_pid = src.rewrite_pid() # this replaces the pid in the content
        assert new_pid == "o:hsa.letter.12137"
        assert src.safe_pid == "o%3Ahsa.letter.12137" 


def test_pid_remove_prefix(shared_datadir):
    """Test the split method of TEIObjectDirectory with removing the prefix.
    
    The pid is comming from the content of the file.
    """
    tei_file = shared_datadir / "projects" / "TEI_1.xml"
    src = TEIObjectSource(tei_file, strip_prefix=True, strip_extension=False)

    # As pid is extracted from content, the prefix is not removed yet.
    assert src.pid == "o:hsa.letter.12137"

    new_pid = src.rewrite_pid() # this replaces the pid in the content
    assert new_pid == "hsa.letter.12137"  

    # the pid property should now reflect the changed pid
    assert src.pid == "hsa.letter.12137"
    assert src.safe_pid == "hsa.letter.12137"

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

def test_save(shared_datadir, tmp_path):
    """Test the save method."""
    src_file = shared_datadir / "projects" / "TEI_1.xml"
    src = TEIObjectSource(src_file, strip_prefix=True, strip_extension=False)
    src.rewrite_pid()
    src.rewrite_references()
    objects_root = tmp_path / "object1"
    objects_root.mkdir()

    result = src.save(objects_root)    
    assert (objects_root / "TEI_1.xml").is_file()
    assert (objects_root / "IMG.1").is_file()
    assert (objects_root / "image02.jpeg").is_file()

def test_save_strip_extension(shared_datadir, tmp_path):
    """Test the save method with strip_extension=True."""
    src_file = shared_datadir / "projects" / "TEI_1.xml"
    src = TEIObjectSource(src_file, strip_prefix=True, strip_extension=True)
    src.rewrite_pid()
    src.rewrite_references()
    objects_root = tmp_path / "object1"
    objects_root.mkdir()

    result = src.save(objects_root)    
    assert (objects_root / "TEI_1").is_file()
    assert (objects_root / "IMG.1").is_file()
    assert (objects_root / "image02").is_file()    