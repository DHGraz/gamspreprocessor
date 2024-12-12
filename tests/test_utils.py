"Tests for the utility functions."

import logging
import pytest
from gamspreprocessor.utils import get_namespaces, validate_pid
from gamspreprocessor.utils import configure_logging


def test_validate_pid():
    "Only a few characters are allowed in PIDs."
    assert validate_pid("foo") is None
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


def test_configure_logging(tmp_path):
    "Test configuring the logging."

    logger = configure_logging()
    assert logger.level == logging.INFO

    logger = configure_logging(logging.DEBUG)
    assert logger.level == logging.DEBUG

    logger = configure_logging(logfile=str(tmp_path / "test.log"))
    logger.info("This is a test message")
    assert (tmp_path / "test.log").exists()
    assert "test message" in (tmp_path / "test.log").read_text()

    logger = configure_logging(
        logfile=str(tmp_path / "test_error.log"), logfile_level=logging.ERROR
    )
    logger.info("This is an info message")
    logger.error("This is an error message")

    assert "info message" not in (tmp_path / "test_error.log").read_text()
