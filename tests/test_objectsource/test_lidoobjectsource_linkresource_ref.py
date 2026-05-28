"""Tests for the LIDOResourceSet class."""

from pathlib import Path
import pytest

from lxml import etree as ET

from gamspreprocessor.objectsource import LIDOObjectSource, LIDOResourceSet


@pytest.fixture(name="lidoresourceset_element")
def make_lidoresourceset_element() -> ET.Element:
    "Return an example Lido resourceSet element."
    xml = """<lido:resourceSet xmlns:lido="http://www.lido-schema.org" lido:type='xsd:string' lido:sortorder="1">
        <lido:resourceID lido:type="IMAGE">IMAGE.1</lido:resourceID>
        <lido:resourceRepresentation>
          <lido:linkResource lido:formatResource="image/jpeg">http://gams.uni-graz.at/o:ges.a-88/image01.jpeg</lido:linkResource>
        </lido:resourceRepresentation>
      </lido:resourceSet>"""
    return ET.fromstring(xml)

def test_init(lidoresourceset_element):
    "Test the initialization of the LIDOResourceSet object."
    ref = LIDOResourceSet(lidoresourceset_element)
    assert ref._element == lidoresourceset_element
    assert ref.source_file is None

def test_get_reference(lidoresourceset_element, tmp_path):
    "Test the get_uri method of the  object."
    ref = LIDOResourceSet(lidoresourceset_element)
    x = ref.get_reference()
    assert ref.get_reference() == "http://gams.uni-graz.at/o:ges.a-88/image01.jpeg"

    # # An empty url attribute should raise a ValueError
    # lidoresourceset_element.find("lido:resourceRepresentation/lido:linkResource", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES).text = ""
    # ref = LIDOResourceSet(lidoresourceset_element)
    # with pytest.raises(ValueError) as excinfo:
    #     ref.get_reference()

def test_set_reference(lidoresourceset_element):
    "Test the set_reference method of the TEIGraphicReference object."
    ref = LIDOResourceSet(lidoresourceset_element)
    ref.set_reference("bar.png")
    assert ref.get_reference() == "bar.png"


def test_get_id(lidoresourceset_element):
    "Test the get_id method of the TEIGraphicReference object."
    ref = LIDOResourceSet(lidoresourceset_element)
    assert ref.get_id() == "IMAGE.1"


def test_get_id_missing(lidoresourceset_element):
    "Test the get_id method of the TEIGraphicReference object if no id is set."
    #del lidoresourceset_element.find("lido:resourceID", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES)
    lidoresourceset_element.remove(lidoresourceset_element.find("lido:resourceID", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES))
    ref = LIDOResourceSet(lidoresourceset_element)
    assert ref.get_id() == ""


def test_replace_ref_using_id(lidoresourceset_element, tmp_path):
    """Test the replace method of the LIDOResourceSet object.

    As the id is set, we use the id as file name, not the original name
    """
    referenced_file = tmp_path / "bar" / "image01.jpeg"
    referenced_file.parent.mkdir()
    referenced_file.touch()
    ref = LIDOResourceSet(lidoresourceset_element)
    # hint: the value of strip_extension is not used in this case, because the id is used
    ref.replace_ref(tmp_path, strip_extension=False)
    assert ref.source_file == referenced_file
    assert ref.get_reference() == "./IMAGE.1"


def test_replace_ref_no_id_keep_extension(lidoresourceset_element, tmp_path):
    """Test the replace method of the LIDOResourceSet object.

    As no id is set, the filename is used as reference and extension is kept.
    """
    lidoresourceset_element.remove(lidoresourceset_element.find("lido:resourceID", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES))
    
    referenced_file = tmp_path / "bar" / "image01.jpeg"
    referenced_file.parent.mkdir()
    referenced_file.touch()

    ref = LIDOResourceSet(lidoresourceset_element)
    ref.replace_ref(tmp_path, strip_extension=False)
    assert ref.source_file == referenced_file
    assert ref.get_reference() == "./image01.jpeg"


def test_replace_ref_no_id_no_extension(lidoresourceset_element, tmp_path):
    """Test the replace method of the LIDOResourceSet object.

    As no id is set, the filename is used as reference and extension is removed.
    """
    lidoresourceset_element.remove(lidoresourceset_element.find("lido:resourceID", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES))
    
    referenced_file = tmp_path / "bar" / "image01.jpeg"
    referenced_file.parent.mkdir()
    referenced_file.touch()

    
    ref = LIDOResourceSet(lidoresourceset_element)
    ref.replace_ref(tmp_path, strip_extension=True)
    assert ref.source_file == referenced_file
    assert ref.get_reference() == "./image01"


def test_replace_ref_no_file(lidoresourceset_element, tmp_path):
    """Test the replace method of the LIDOResourceSet object if no file can be found.

    In this case, the source_file attribute should be None and no replacement should happen.
    """
    # tei_graphic_element.set("url", "https://example.com/foo/bar.png")
    ref = LIDOResourceSet(lidoresourceset_element)
    ref.replace_ref(tmp_path, strip_extension=False)

    assert ref.source_file is None
    assert ref.get_reference() == "http://gams.uni-graz.at/o:ges.a-88/image01.jpeg"

def test_copy_file(lidoresourceset_element, tmp_path):
    "Test the copy_file method of the LIDOResourceSet object."
    ref = LIDOResourceSet(lidoresourceset_element)

    # we have a url refering image01.jpeg in the element: create it as file
    src_path = tmp_path / "src"
    src_path.mkdir()
    source_file = src_path / "image01.jpeg" # the filename is used as reference and extension is removed.IMAGE.1"
    source_file.touch()

    ref.replace_ref(src_path, strip_extension=False)

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target_file = ref.copy_file(target_dir)
    assert target_file == target_dir / "IMAGE.1"
    assert target_file.exists()

def test_copy_file_no_id(lidoresourceset_element, tmp_path):
    "If the LIDOResourceSet object has no id, the filename is used as reference."
    lidoresourceset_element.remove(lidoresourceset_element.find("lido:resourceID", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES))
    ref = LIDOResourceSet(lidoresourceset_element)

    # we have a url refering image01.jpeg in the element: create it as file
    src_path = tmp_path / "src"
    src_path.mkdir()
    source_file = src_path / "image01.jpeg" # the filename is used as reference and extension is removed.IMAGE.1"
    source_file.touch()

    ref.replace_ref(src_path, strip_extension=False)

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target_file = ref.copy_file(target_dir)
    assert target_file == target_dir / "image01.jpeg" 
    assert target_file.exists()


def test_repr(lidoresourceset_element):
    "Test the repr method of the TEIGraphicReference object."
    ref = LIDOResourceSet(lidoresourceset_element)
    assert repr(ref) == f"LIDOResourceSet({lidoresourceset_element})"

def test_str(lidoresourceset_element,  tmp_path):
    "Test the str method of the TEIGraphicReference object."
    ref = LIDOResourceSet(lidoresourceset_element) 
    ref.source_file = tmp_path / "foo.png"
    assert str(ref) == f"LIDOResourceSet for '{tmp_path / 'foo.png'}'"

def test_hash(lidoresourceset_element, tmp_path):
    "Test the hash method of the TEIGraphicReference object."
    ref = LIDOResourceSet(lidoresourceset_element)
    ref.source_file = tmp_path / "foo.png"
    assert hash(ref) == hash(f"LIDOResourceSet {(tmp_path / 'foo.png').absolute()}")        