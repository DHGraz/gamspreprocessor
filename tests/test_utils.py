"Tests for the utility functions."
from pathlib import Path

import pytest
from gamspreprocessor.utils import get_namespaces, validate_filename


def test_validate_filename():
    "Only a few characters are allowed in filenames."
    assert validate_filename(Path("foo/bar/foo.xml")) is None
    assert validate_filename(Path("foo/bar/foo-1.xml")) is None
    assert validate_filename(Path("foo/bar/o:foo.1.xml")) is None
    assert validate_filename(Path("foo/bar/o:foo.bar.1.xml")) is None
    assert validate_filename(Path("foo/bar/o:foo.bar.1.2.3xml")) is None
    with pytest.raises(ValueError):
        validate_filename(Path("foo/bar/foß.xml"))

def test_get_namespaces(datadir):
    "Test extracting namespaces from an XML file."
    namespaces = get_namespaces(datadir / "projects" / "TEI_1.xml")
    assert namespaces == {
        "": "http://www.tei-c.org/ns/1.0",
        "foo": "https://example.com/foo",
    }
