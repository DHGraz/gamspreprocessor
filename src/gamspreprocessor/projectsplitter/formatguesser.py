"""Provide functionality to guess the format of a file based on its content.

This is a very naive implementation that only uses file extensions and XML namespaces.
It is not very reliable, but it is a start.

Detecting and validating formats seems to be a big mess if an application
needs to be portable and distributable. There is an old (but nice) rant
about this: https://github.com/KBNLresearch/omSipCreator/issues/23.

"""

import logging
import xml.etree.ElementTree as ET
import mimetypes


# Match Namespaces to formats
XML_FORMATS = {
    "http://www.tei-c.org/ns/1.0": "tei",
    "http://www.lido-schema.org": "lido",
}

logger = logging.getLogger(__name__)


def _guess_xml_format(filename: str) -> str:
    """Try to guess the XML format of the file."""
    file_format = ""
    for node in ET.iterparse(filename, events=["start-ns"]):
        file_format = XML_FORMATS.get(node[1][1], "")
        break
    return file_format


def guess_format(filename: str, explicit_type: str = "auto") -> tuple[str, str]:
    """Guess the format of the file from the extension.

    It does more than the mimetype guesser, as it also checks the namespaces for xml files.

    Retuns a tuple with the mimetype and sub-format (like 'tei' for xml.). The sub-format
    always is lowercase and can be an empty string if no subformat was dedected.
    """
    # TODO: Add more formats
    # TODO: Using an external lib like fido or fits might be a good idea.
    content_type = mimetypes.guess_type(filename)[0]
    # guess_type returns text/xml or application/xml on different platforms?!?
    # At least the github runner returns text/xml while my local system returns application/xml ...
    print(content_type)
    if content_type == "text/xml": 
        content_type = "application/xml"
    if explicit_type == "auto":
        if content_type == "application/xml":
            file_format = _guess_xml_format(filename)
        else:
            file_format = ""
    else:
        file_format = explicit_type
    return content_type, file_format.lower()
