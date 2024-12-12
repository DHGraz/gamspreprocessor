"Unit tests for the LIDOObjectDirectory and ResourceSet classes."

import re
from xml.etree import ElementTree as ET

import pytest

from gamspreprocessor.projectsplitter.lidoobjectdir import (
    LIDOObjectDirectory,
    ResourceSet,
)


def test_resourceset_from_element():
    "Test the ResourceSet classmethod from_element."
    xml = """
        <lido:resourceSet xmlns:lido="http://www.lido-schema.org">
            <lido:resourceID lido:type="IMAGE">123</lido:resourceID>
            <lido:resourceRepresentation>
                <lido:linkResource lido:formatResource="image/jpeg">http://example.com/image.jpg</lido:linkResource>
            </lido:resourceRepresentation>
        </lido:resourceSet>
    """
    root = ET.fromstring(xml)
    ns = {"lido": "http://www.lido-schema.org"}
    resourceset = ResourceSet.from_element(root, ns)
    assert resourceset.resource_id == "123"
    assert resourceset.resource_type == "IMAGE"
    assert resourceset.link_format == "image/jpeg"
    assert resourceset.link_url == "http://example.com/image.jpg"


def test_resourceset_from_incomplete_element():
    "Test the ResourceSet classmethod from_element with missing data."

    xml = """
        <lido:resourceSet xmlns:lido="http://www.lido-schema.org">
            
            <lido:resourceRepresentation>
                <lido:linkResource lido:formatResource="image/jpeg">http://example.com/image.jpg</lido:linkResource>
            </lido:resourceRepresentation>
        </lido:resourceSet>
    """
    root = ET.fromstring(xml)
    ns = {"lido": "http://www.lido-schema.org"}
    resourceset = ResourceSet.from_element(root, ns)
    assert resourceset.resource_id == ""
    assert resourceset.resource_type == ""
    assert resourceset.link_format == "image/jpeg"
    assert resourceset.link_url == "http://example.com/image.jpg"

    xml = """
        <lido:resourceSet xmlns:lido="http://www.lido-schema.org">
            <lido:resourceID lido:type="IMAGE">123</lido:resourceID>
        </lido:resourceSet>
    """
    root = ET.fromstring(xml)
    ns = {"lido": "http://www.lido-schema.org"}
    resourceset = ResourceSet.from_element(root, ns)
    assert resourceset.resource_id == "123"
    assert resourceset.resource_type == "IMAGE"
    assert resourceset.link_format == ""
    assert resourceset.link_url == ""


def test_resourceset_get_new_url():
    """The get_new_url tries to come up with a relativ uri for the resource.

    The returned value depends on the data provided in the LIDO ResourceSet.
    """
    resourceset = ResourceSet("IMAGE123", "IMAGE", "image/jpeg", "file:///image.jpg")
    assert resourceset.get_new_url() == "./IMAGE123.jpg"

    # if we cannot resolve the extension via mimetype,
    # we use the extension of the referenced file
    resourceset = ResourceSet(
        "IMAGE123", "IMAGE", "application/qwirks", "file:///image.xxx"
    )
    assert resourceset.get_new_url() == "./IMAGE123.xxx"

    # if we cannot dedect the extension, we use the pid without extension
    resourceset = ResourceSet(
        "IMAGE123", "IMAGE", "application/qwirks", "file:///image"
    )
    assert resourceset.get_new_url() == "./IMAGE123"

    resourceset = ResourceSet("IMAGE123", "IMAGE", "application/qwirks", "image")
    assert resourceset.get_new_url() == "./IMAGE123"


def test_lidoobjectdirectory_init(tmp_path):
    "Test if LIDOObjectDirectory is initialized correctly."
    obj_path = tmp_path / "object1"
    obj = LIDOObjectDirectory(obj_path)
    assert obj.path == obj_path
    assert obj_path.is_dir()


def test_lidoobjectdirectory_init_dir_exists(tmp_path):
    "Test creating a LIDOObjectDirectory with an existing object directory."
    obj_path = tmp_path / "object2"
    obj_path.mkdir()

    # Check what happens if directory ist not empty
    with pytest.raises(FileExistsError):
        LIDOObjectDirectory(obj_path)


def test_lidoobjectdirectory_split(shared_datadir, tmp_path):
    "Test the split method of LIDOObjectDirectory."
    project_file = shared_datadir / "projects" / "LIDO_1.xml"
    obj_path = tmp_path / "object1"
    objdir = LIDOObjectDirectory(obj_path)

    objdir.split(project_file)

    assert (obj_path / "LIDO_1.xml").exists()
    assert (obj_path / "LIDO_1.xml").exists()
    assert (obj_path / "IMAGE.1.jpg").exists()
    assert (obj_path / "IMAGE.2.jpg").exists()
    assert not (
        obj_path / "IMAGE.3"
    ).exists()  # the third image is a URL, without a matching local file

    # check the resulting LIO xml if the references have been replaced correctly
    tree = ET.parse(obj_path / "LIDO_1.xml")
    root = tree.getroot()
    resourcesets = list(root.findall(".//{http://www.lido-schema.org}resourceSet"))
    assert len(resourcesets) == 3
    assert (
        resourcesets[0].find(".//{http://www.lido-schema.org}linkResource").text
        == "./IMAGE.1.jpg"
    )
    assert (
        resourcesets[1].find(".//{http://www.lido-schema.org}linkResource").text
        == "./IMAGE.2.jpg"
    )
    # the next one should not be replaced, because it is an external URL
    assert (
        resourcesets[2].find(".//{http://www.lido-schema.org}linkResource").text
        == "http://gams.uni-graz.at/o:ges.a-88/IMAGE.3"
    )


def test_lidoobjectdirectory_split_with_new_pid(shared_datadir, tmp_path):
    "Test the split method of LIDOObjectDirectory with a new pid."
    project_file = shared_datadir / "projects" / "LIDO_1.xml"
    obj_path = tmp_path / "object1"
    objdir = LIDOObjectDirectory(obj_path)

    objdir.split(project_file, new_pid="new_pid")

    tree = ET.parse(obj_path / "LIDO_1.xml")
    root = tree.getroot()
    assert root.find(".//{http://www.lido-schema.org}lidoRecID").text == "new_pid"


def test_teiobjectdirectory_whitespace_handling(shared_datadir, tmp_path):
    "Make sure that the XML is written correctly."

    project_file = shared_datadir / "projects" / "LIDO_1.xml"
    obj_path = tmp_path / "object1"
    objdir = LIDOObjectDirectory(obj_path)

    objdir.split(project_file)
    lido_file = obj_path / "LIDO_1.xml"
    assert (lido_file).exists()

    text = lido_file.read_text(encoding="utf-8")
    assert re.search(
        r'<lido:term lido:label="info:fedora/context:ges">Meringer Sammlung:\s*$',
        text,
        re.MULTILINE,
    )
    assert re.search(r"\s+Geräte</lido:term>", text, re.MULTILINE)


def test_str(tmp_path):
    "Test the string representation of the object directory."

    obj_path = tmp_path / "foo"
    obj = LIDOObjectDirectory(obj_path)
    assert str(obj) == f"LIDOObjectDirectory('{str(obj_path)}')"
