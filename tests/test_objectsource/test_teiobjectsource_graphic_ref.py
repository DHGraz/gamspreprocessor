"Tests for the TEIGraphicReference object."

import pytest
from lxml import etree as ET

from gamspreprocessor.objectsource.teiobjectsource import TEIGraphicReference

# pylint: disable=c-extension-no-member

@pytest.fixture(name="tei_graphic_element")
def make_tei_graphic_element():
    "Return an example TEI graphic element."
    graphic = ET.Element("graphic")
    graphic.set("url", "foo.png")
    graphic.set("{http://www.w3.org/XML/1998/namespace}id", "bar")
    return graphic


def test_init(tei_graphic_element):
    "Test the initialization of the TEIGraphicReference object."
    ref = TEIGraphicReference(tei_graphic_element)
    assert ref._element == tei_graphic_element
    assert ref.source_file is None


def test_get_reference(tei_graphic_element, tmp_path):
    "Test the get_uri method of the TEIGraphicReference object."
    ref = TEIGraphicReference(tei_graphic_element)
    assert ref.get_reference() == "foo.png"

    # An empty url attribute should raise a ValueError
    tei_graphic_element.set("url", "")
    ref = TEIGraphicReference(tei_graphic_element)
    with pytest.raises(ValueError) as excinfo:
        ref.get_reference()


def test_set_reference(tei_graphic_element):
    "Test the set_reference method of the TEIGraphicReference object."
    ref = TEIGraphicReference(tei_graphic_element)
    ref.set_reference("bar.png")
    assert ref._element.attrib["url"] == "bar.png"


def test_get_id(tei_graphic_element):
    "Test the get_id method of the TEIGraphicReference object."
    ref = TEIGraphicReference(tei_graphic_element)
    assert ref.get_id() == "bar"


def test_get_id_missing(tei_graphic_element):
    "Test the get_id method of the TEIGraphicReference object if no id is set."
    tei_graphic_element.attrib.pop("{http://www.w3.org/XML/1998/namespace}id")
    ref = TEIGraphicReference(tei_graphic_element)
    assert ref.get_id() == ""


def test_replace_ref_using_id(tei_graphic_element, tmp_path):
    """Test the replace method of the TEIGraphicReference object.

    As the id is set, we use the id as file name, not the original name
    """
    referenced_file = tmp_path / "bar" / "foo.png"
    referenced_file.parent.mkdir()
    referenced_file.touch()
    ref = TEIGraphicReference(tei_graphic_element)
    ref.replace_ref(tmp_path, strip_extension=False)
    assert ref.source_file == referenced_file
    assert ref.get_reference() == "./bar"


def test_replace_ref_no_id_keep_extension(tei_graphic_element, tmp_path):
    """Test the replace method of the TEIGraphicReference object.

    As no id is set, the filename is used as reference and extension is kept.
    """
    referenced_file = tmp_path / "bar" / "foo.png"
    referenced_file.parent.mkdir()
    referenced_file.touch()
    tei_graphic_element.attrib.pop("{http://www.w3.org/XML/1998/namespace}id")
    ref = TEIGraphicReference(tei_graphic_element)
    ref.replace_ref(tmp_path, strip_extension=False)
    assert ref.source_file == referenced_file
    assert ref.get_reference() == "./foo.png"


def test_replace_ref_no_id_no_extension(tei_graphic_element, tmp_path):
    """Test the replace method of the TEIGraphicReference object.

    As no id is set, the filename is used as reference and extension is removed.
    """
    referenced_file = tmp_path / "bar" / "foo.png"
    referenced_file.parent.mkdir()
    referenced_file.touch()
    tei_graphic_element.attrib.pop("{http://www.w3.org/XML/1998/namespace}id")
    ref = TEIGraphicReference(tei_graphic_element)
    ref.replace_ref(tmp_path, strip_extension=True)
    assert ref.source_file == referenced_file
    assert ref.get_reference() == "./foo"


def test_replace_ref_no_file(tei_graphic_element, tmp_path):
    """Test the replace method of the TEIGraphicReference object if no file can be found.

    In this case, the source_file attribute should be None and no replacement should happen.
    """
    tei_graphic_element.set("url", "https://example.com/foo/bar.png")
    ref = TEIGraphicReference(tei_graphic_element)
    ref.replace_ref(tmp_path, strip_extension=False)
    assert ref.source_file is None
    assert ref.get_reference() == "https://example.com/foo/bar.png"

def test_copy_file(tei_graphic_element, tmp_path):
    "Test the copy_file method of the TEIGraphicReference object."
    ref = TEIGraphicReference(tei_graphic_element)
    ref.source_file = tmp_path / "foo.png"
    ref.source_file.touch()

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target_file = ref.copy_file(target_dir)
    assert target_file == tmp_path / "target" / "foo.png"
    assert target_file.exists()

def test_copy_file_with_url(tei_graphic_element, tmp_path):
    "Test the copy_file method of the TEIGraphicReference object if source file is an URL."
    tei_graphic_element.set("url", "http://example.com/foofoo.png")
    ref = TEIGraphicReference(tei_graphic_element)

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    
    target_file = ref.copy_file(target_dir)
    assert target_file is None#== tmp_path / "target" / "foo.png"

def test_repr(tei_graphic_element):
    "Test the repr method of the TEIGraphicReference object."
    ref = TEIGraphicReference(tei_graphic_element)
    assert repr(ref) == f"TEIGraphicReference({tei_graphic_element})"

def test_str(tei_graphic_element,  tmp_path):
    "Test the str method of the TEIGraphicReference object."
    ref = TEIGraphicReference(tei_graphic_element)
    ref.source_file = tmp_path / "foo.png"
    assert str(ref) == f"TEIGraphicReference for '{tmp_path / 'foo.png'}'"

def test_hash(tei_graphic_element, tmp_path):
    "Test the hash method of the TEIGraphicReference object."
    ref = TEIGraphicReference(tei_graphic_element)
    ref.source_file = tmp_path / "foo.png"
    assert hash(ref) == hash(f"TEIGraphicReference {(tmp_path / 'foo.png').absolute()}")