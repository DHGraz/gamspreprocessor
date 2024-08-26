"""Provide functionality to guess the format of a file based on its content.

Detecting and validating formats seems to be a big mess as a application 
needs to be portable and distributable.

There is an old (but nice) rant about this: https://github.com/KBNLresearch/omSipCreator/issues/23.

"""

import logging
import xml.etree.ElementTree as ET
import mimetypes


# Match Namespaces to formats
XML_FORMATS = {
    "http://www.tei-c.org/ns/1.0": "tei",
    "http://www.lido-schema.org": "lido",
}


def guess_format(filename: str) -> str:
    """Guess the format of the file from the extension.

    It does more than the mimetype guesser, as it also checks the namespaces for xml files.
    All strings returned are lowercase.
    """
    # TODO: Add more formats
    # TODO: Using an external lib like fido or fits might be a good idea.
    mtype = mimetypes.guess_type(filename)[0]
    file_format = None
    if mtype == "application/xml":
        file_format = "xml"  # for xml without namespace
        # search for the document namespace
        for node in ET.iterparse(filename, events=["start-ns"]):
            file_format = XML_FORMATS.get(node[1][1], "xml")
            break
    elif mtype.startswith("application/"):
        file_format = mtype.split("/")[1]
    elif mtype.startswith("text/"):
        file_format = mtype.split("/")[1]
    else:
        file_format = mtype.split("/")[0]
    return file_format.lower()


