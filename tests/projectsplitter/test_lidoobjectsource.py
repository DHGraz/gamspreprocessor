import pytest
from gamspreprocessor.projectsplitter.lidoobjectsource import LIDOObjectSource, LIDOResourceSet
from xml.etree import ElementTree as ET


def test_pid_keep_prefix(shared_datadir):
    """Test the split method without removing the prefix.

    The pid is comming from the content of the file.
    """
    lido_file = shared_datadir / "projects" / "LIDO_1.xml"
    src = LIDOObjectSource(lido_file, strip_prefix=False, strip_extension=False)
    with pytest.warns(UserWarning):
        src.rewrite_pid()
        assert src.pid == "o:ges.a-88"
        assert src.safe_pid == "o%3Ages.a-88"


def test_pid_remove_prefix(shared_datadir):
    """Test the split method of LIDOObjectDirectory with removing the prefix.

    The pid is comming from the content of the file.
    """
    LIDO_file = shared_datadir / "projects" / "LIDO_1.xml"
    src = LIDOObjectSource(LIDO_file, strip_prefix=True, strip_extension=False)
    src.rewrite_pid()
    assert src.pid == "ges.a-88"
    assert src.safe_pid == "ges.a-88"


def test_pid_from_filename(tmp_path, shared_datadir):
    """If no pid is found in the content, the pid is extracted from the filename."""
    # first we create a LIDO with an empty idno element
    tree = ET.parse(shared_datadir / "projects" / "LIDO_1.xml")
    root = tree.getroot()
    root.find(
        "./lido:lidoRecID", namespaces={"lido": "http://www.lido-schema.org"}
    ).text = ""

    LIDO_file = tmp_path / "LIDO_1.xml"
    tree.write(LIDO_file)

    src = LIDOObjectSource(LIDO_file, strip_prefix=True, strip_extension=False)
    with pytest.warns(UserWarning):
        assert src.pid == "LIDO_1.xml"


def test_save(shared_datadir, tmp_path):
    """Test the save method."""
    src_file = shared_datadir / "projects" / "LIDO_1.xml"
    src = LIDOObjectSource(src_file, strip_prefix=True, strip_extension=False)
    src.rewrite_pid()
    src.rewrite_references()
    objects_root = tmp_path / "object1"
    objects_root.mkdir()

    result = src.save(objects_root)

    assert (objects_root / "LIDO_1.xml").is_file()
    assert (objects_root / "IMAGE.1").is_file()
    assert (objects_root / "image02.jpeg").is_file()


def test_save_strip_extension(shared_datadir, tmp_path):
    """Test the save method with strip_extension=True."""
    src_file = shared_datadir / "projects" / "LIDO_1.xml"
    src = LIDOObjectSource(src_file, strip_prefix=True, strip_extension=True)
    src.rewrite_pid()
    src.rewrite_references()
    objects_root = tmp_path / "object1"
    objects_root.mkdir()

    result = src.save(objects_root)
    assert (objects_root / "LIDO_1").is_file()
    assert (objects_root / "IMAGE.1").is_file()
    assert (objects_root / "image02").is_file()
    

def test_get_reference_valid(shared_datadir):
    """Test get_reference method with a valid linkResource element."""
    lido_file = shared_datadir / "projects" / "LIDO_1.xml"
    src = LIDOObjectSource(lido_file, strip_prefix=False, strip_extension=False)
    resource_set = src.tree.find(".//lido:resourceSet", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES)
    lido_resource_set = LIDOResourceSet(resource_set)
    assert lido_resource_set.get_reference() == "http://gams.uni-graz.at/o:ges.a-88/image01.jpeg"


def test_get_reference_missing(shared_datadir):
    """Test get_reference method when linkResource element is missing."""
    lido_file = shared_datadir / "projects" / "LIDO_1.xml"

    # Remove the linkResource  element from the first resourceSet
    tree=ET.parse(lido_file)    
    root=tree.getroot()
    parent =  root.find(".//lido:resourceRepresentation", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES)
    parent.remove(parent.find(".//lido:linkResource", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES))
    tree.write(lido_file)

    src = LIDOObjectSource(lido_file, strip_prefix=False, strip_extension=False)
    resource_set = src.tree.find(".//lido:resourceSet", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES)
    lido_resource_set = LIDOResourceSet(resource_set)
    with pytest.raises(ValueError, match="No linkResource element found in resourceSet element"):
        lido_resource_set.get_reference()




