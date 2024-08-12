"Unit tests for gamspreprocessor.projectsplitter.splitter module."
from pathlib import Path
from xml.etree import ElementTree as ET

from gamspreprocessor.projectsplitter.splitter import (
    TEIObjectDirectory,
    extract_pid,
    find_file,
    get_namespaces,
    guess_format,
    rank_path,
    validate_filename,
)


def test_extract_pid():
    "Test extracting a PID from a path."
    assert extract_pid(Path("foo.xml")) == "foo"
    assert extract_pid(Path("foo.bar.xml")) == "foo.bar"
    assert extract_pid(Path("foo.bar.baz.xml")) == "foo.bar.baz"


def test_validate_filename():
    "Only a few characters are allowed in filenames."
    assert validate_filename(Path("foo.xml")) is None
    # assert validate_filename(Path("foo1.xml"))


def test_get_namespaces(datadir):
    "Test extracting namespaces from an XML file."
    namespaces = get_namespaces(datadir / "projects" / "TEI_1.xml")
    assert namespaces == {
        "": "http://www.tei-c.org/ns/1.0",
        "foo": "https://example.com/foo",
    }


def test_rank_path():
    """Test the rank path function.

    In short the rank ist the number of identical chars counted from the end
    """
    assert rank_path(Path("foo"), Path("foox")) == 0
    assert rank_path(Path("foo"), Path("foo")) == 3
    assert rank_path(Path("foxo"), Path("foo")) == 1
    assert rank_path(Path("bar/foo"), Path("foo")) == 3


def test_find_file(datadir):
    "Test finding a file in a directory."
    root_dir = datadir / "find_file"

    assert find_file("foo.png", root_dir) == root_dir / "foo.png"
    assert find_file("foo/foo.png", root_dir) == root_dir / "foo" / "foo.png"
    assert find_file("/bar/foo.png", datadir) == root_dir / "bar" / "foo.png"

    # bar/foo.png should win over foo/bar/foo.png
    assert find_file("bar/foo.png", datadir) == root_dir / "bar" / "foo.png"

    assert find_file("file:///bar/foo.png", datadir) == root_dir / "bar" / "foo.png"
    assert (
        find_file("http://example.com/bar/foo.png", datadir)
        == root_dir / "bar" / "foo.png"
    )
    assert find_file("foo.jpeg", datadir) is None


def test_teiobjectdirectory_init(tmp_path):
    "Test if TEIObjectDirectory is initialized correctly."
    tei_dir = tmp_path / "object1"
    obj = TEIObjectDirectory(tei_dir)
    assert obj.path == tei_dir
    assert tei_dir.is_dir()

    # Check what happens if directory ist not empty
    # At the moment: nothing
    tei_dir = tmp_path / "object2"
    tei_dir.mkdir()
    (tei_dir / "foo.xml").touch()
    obj = TEIObjectDirectory(tei_dir)
    assert obj.path == tei_dir


def test_teiobjectdirectory_split(datadir, tmp_path):
    "Test the split method of TEIObjectDirectory."
    project_file = datadir / "projects" / "TEI_1.xml"
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


def test_teiobjectdirectory_whitespace_handling(datadir, tmp_path):
    "Make sure that the XML is written correctly."
    project_file = datadir / "projects" / "bar.xml"
    tei_dir = tmp_path / "bar"
    objdir = TEIObjectDirectory(tei_dir)

    objdir.split(project_file)
    with open(tei_dir / "bar.xml", encoding="utf-8") as f:
        text = f.read()
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


def test_guess_format(datadir):
    "Guess the format of the file from the extension."

    foo_xml = datadir / "projects" / "foo.xml"
    with open(foo_xml, "w", encoding="utf-8") as f:
        f.write("<foo></foo>")

    assert guess_format(datadir / "projects" / "TEI_1.xml") == "tei"
    assert guess_format(datadir / "projects" / "LIDO_1.xml") == "lido"
    assert guess_format(str(foo_xml)) == "xml"
    assert guess_format(datadir / "projects" / "foo.csv") == "csv"
    assert guess_format(datadir / "projects" / "foo.pdf") == "pdf"
    assert guess_format(datadir / "projects" / "d1/bar.pdf") == "pdf"
    assert guess_format("img.jpeg") == "image"
    assert guess_format("img.png") == "image"
