"Tests for the utility functions."
from pathlib import Path

import pytest
from gamspreprocessor.utils import get_namespaces, validate_pid


def test_validate_pid():
    "Only a few characters are allowed in PIDs."
    assert validate_pid('foo') is None
    assert validate_pid("foo.123") is None
    assert validate_pid("foo.1.2.3") is None
    assert validate_pid("foo-bar_1") is None
    assert validate_pid("o:foo.123") is None
    with pytest.raises(ValueError):
        validate_pid("foo/bar")

def test_get_namespaces(datadir):
    "Test extracting namespaces from an XML file."
    namespaces = get_namespaces(datadir / "projects" / "TEI_1.xml")
    assert namespaces == {
        "": "http://www.tei-c.org/ns/1.0",
        "foo": "https://example.com/foo",
    }
