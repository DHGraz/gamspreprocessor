"Unit tests for the TEIObjectDirectory class."

from xml.etree import ElementTree as ET

import pytest

from gamspreprocessor.projectsplitter.teiobjectdir import TEIObjectDirectory


def test_teiobjectdirectory_init(tmp_path):
    "Test if TEIObjectDirectory is initialized correctly."
    obj_path = tmp_path / "object1"
    obj = TEIObjectDirectory(obj_path)
    assert obj.path == obj_path
    assert obj_path.is_dir()


def test_teiobjectdirectory_init_dir_exists(tmp_path):
    "Test creating a TEIObjectDirectory with an existing directory."
    obj_path = tmp_path / "object1"
    obj_path.mkdir()
    with pytest.raises(FileExistsError):
        TEIObjectDirectory(obj_path)


def test_teiobjectdirectory_split(shared_datadir, tmp_path):
    "Test the split method of TEIObjectDirectory."
    project_file = shared_datadir / "projects" / "TEI_1.xml"
    obj_path = tmp_path / "object1"
    objdir = TEIObjectDirectory(obj_path)

    objdir.split(project_file)

    assert (obj_path / "TEI_1.xml").exists()
    assert (obj_path / "IMG.1.jpeg").exists()
    assert (obj_path / "image02.jpeg").exists()

    tree = ET.parse(obj_path / "TEI_1.xml")
    root = tree.getroot()
    for graphic in root.findall(".//{http://www.tei-c.org/ns/1.0}graphic"):
        assert graphic.attrib["url"] in {"./image02.jpeg", "./IMG.1.jpeg"}


def test_teiobjectdirectory_split_with_new_pid(shared_datadir, tmp_path):
    "Test the split method of TEIObjectDirectory with a new pid."
    project_file = shared_datadir / "projects" / "TEI_1.xml"
    obj_path = tmp_path / "object1"
    objdir = TEIObjectDirectory(obj_path)

    objdir.split(project_file, new_pid="new_pid")

    tree = ET.parse(obj_path / "TEI_1.xml")
    root = tree.getroot()
    assert root.find(".//{http://www.tei-c.org/ns/1.0}idno").text == "new_pid"


def test_teiobjectdirectory_whitespace_handling(shared_datadir, tmp_path):
    "Make sure that the XML is written correctly."
    project_file = shared_datadir / "projects" / "bar.xml"
    obj_path = tmp_path / "bar"
    objdir = TEIObjectDirectory(obj_path)

    objdir.split(project_file)
    text = (obj_path / "bar.xml").read_text(encoding="utf-8")
    assert (
        '<p cid="1">Mit den besten <foo>Weihnachtsgrüßen</foo> übersende ich</p>'
        in text
    )
    assert '<p cid="2"> foobar <foo> bar </foo> foo </p>' in text
    assert (
        """<p cid="2"> foobar <foo> bar </foo> foo </p> 
            <p cid="3">ein erster
            Absatz

            und ein zweiter
            </p>"""
        in text
    )


def test_str(tmp_path):
    "Test the __str__ method."
    obj_path = tmp_path / "object1"
    obj = TEIObjectDirectory(obj_path)
    assert str(obj) == f"TEIObjectDirectory('{str(obj_path)}')"
