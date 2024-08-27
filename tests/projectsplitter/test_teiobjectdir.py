import pytest
from gamspreprocessor.projectsplitter.teiobjectdir import TEIObjectDirectory
from xml.etree import ElementTree as ET


def test_teiobjectdirectory_init(tmp_path):
    "Test if TEIObjectDirectory is initialized correctly."
    tei_dir = tmp_path / "object1"
    obj = TEIObjectDirectory(tei_dir)
    assert obj.path == tei_dir
    assert tei_dir.is_dir()

    # Check what happens if directory ist not empty
    with pytest.raises(FileExistsError):
        obj = TEIObjectDirectory(tei_dir)
    
def test_teiobjectdirectory_init_dir_with_replace(tmp_path):
    "Test creating a TEIObjectDirectory with an existing directory and replace=True."
    tei_dir = tmp_path / "object2"
    tei_dir.mkdir()
    (tei_dir / "foo.xml").touch()
    obj = TEIObjectDirectory(tei_dir, True)
    assert obj.path == tei_dir


def test_teiobjectdirectory_split(shared_datadir, tmp_path):
    "Test the split method of TEIObjectDirectory."
    project_file = shared_datadir / "projects" / "TEI_1.xml"
    tei_dir = tmp_path / "object1"
    objdir = TEIObjectDirectory(tei_dir)

    objdir.split(project_file)

    assert (tei_dir / "TEI_1.xml").exists()
    assert (tei_dir / "IMG.1.jpeg").exists()
    assert (tei_dir / "image02.jpeg").exists()

    tree = ET.parse(tei_dir / "TEI_1.xml")
    root = tree.getroot()
    for graphic in root.findall(".//{http://www.tei-c.org/ns/1.0}graphic"):
        assert graphic.attrib["url"] in {"./image02.jpeg", "./IMG.1.jpeg"}


def test_teiobjectdirectory_whitespace_handling(shared_datadir, tmp_path):
    "Make sure that the XML is written correctly."
    project_file = shared_datadir / "projects" / "bar.xml"
    tei_dir = tmp_path / "bar"
    objdir = TEIObjectDirectory(tei_dir)

    objdir.split(project_file)
    with open(tei_dir / "bar.xml", encoding="utf-8") as f:
        text = f.read()
    print(text)
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
