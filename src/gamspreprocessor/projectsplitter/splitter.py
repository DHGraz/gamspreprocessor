"""Module to split a project into single objects, each in it's own folder.

The main class is ProjectSplitter, which provides a split method to create
a object folder for the file given as argument.
The module tries to find all referenced files (based on the object type)
and copies them to the object folder.
"""

import logging
import mimetypes
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union

from uritools import urisplit

from .. import NAME
from .bookkeeper import BookKeeper

# Match Namespaces to formats
XML_FORMATS = {
    "http://www.tei-c.org/ns/1.0": "tei",
    "http://www.lido-schema.org": "lido",
}

logger = logging.getLogger(NAME)


def guess_format(filename: str) -> str:
    """Guess the format of the file from the extension.

    It does more than the mimetype guesser, as it also checks the namespaces for xml files.
    All string returned are lowercase.
    """
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


def validate_filename(path: Path) -> None:
    "Raise a ValueError if filename does not match our conventions."
    allowed_pattern = "^([a-z]:)?[.-_a-z0-9]+$"
    filename = path.name
    m = re.match(allowed_pattern, filename)
    if m is None:
        raise ValueError(
            f"Filename {filename} does not match the allowed pattern {allowed_pattern}"
        )


def extract_pid(path: Path) -> str:
    "Extract pid from a path."
    return ".".join(path.name.split(".")[0:-1])


def get_namespaces(filename: Path) -> Dict[str, str]:
    "Return all namespaces from the XML file a dictionary."
    return {k: v for (_, (k, v)) in ET.iterparse(filename, events=["start-ns"])}


def register_namespaces(namespaces: dict) -> None:
    "Register all namespaces in the ElementTree module."
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])


def rank_path(short_path: Path, long_path: Path):
    "Return how many chars are the same at the end of both paths."
    score = 0

    for short, long in zip(str(short_path)[::-1], str(long_path)[::-1]):
        if short == long:
            score += 1
        else:
            break
    return score


def find_file(referenced_uri: str, source_dir: Path) -> Union[Path, None]:
    """Try to find a file below source_dir with might match the file referenced in uri.

    The file will be identified by the best matching path (dir + filename)
    If 2 or more paths are ranked equally, the shortest matching path will be returned.

    Return path to the first file which matches or None if no file was found
    """
    uri = urisplit(referenced_uri)
    path = uri.path
    if path.endswith("/"):
        path = path[:-1]

    ranked_paths = []
    for file in source_dir.rglob(path.split("/")[-1]):
        ranked_paths.append((rank_path(path, file), file))

    if ranked_paths:
        # we sort by 1) rank (desc) and 2) length of the path (asc: *-1)
        ranked_paths.sort(key=lambda x: (x[0], len(str(x[1]) * -1)), reverse=True)
        return ranked_paths[0][1]
    return None


class ObjectDirectory:
    "Class to handle a directory for a generic single object."

    def __init__(self, path: Path):
        """Initialize the object directory.

        File will be created, if necessary.
        """
        self.path = path
        if self.path.is_dir():
            # TODO: How to react if the directory exists and is not empty?
            pass
        else:
            self.path.mkdir()
        self.files = []

    def split(self, sourcefile: Path):
        "Copy the sourcefile to the object directory."
        shutil.copy(sourcefile, self.path)
        self.files.append(sourcefile)

    def __str__(self):
        return f"ObjectDirectory({self.path})"


class TEIObjectDirectory(ObjectDirectory):
    "Class to handle a directory for a TEI object."

    NAMESPACES = {"tei": "http://www.tei-c.org/ns/1.0"}

    def split(self, sourcefile: Path) -> None:
        "Copy the sourcefile and all referenced files to the object directory."

        # Keeps all files which must be copied to the object directory
        referenced_files: Set[Tuple[str, Path]] = set()

        shutil.copy(sourcefile, self.path)
        self.files.append(sourcefile)

        # from now on we operate on the copied file
        new_sourcefile = self.path / sourcefile.name

        # we want the keep the original prefixes in the namespaces
        register_namespaces(get_namespaces(new_sourcefile))

        tree = ET.parse(new_sourcefile)
        root = tree.getroot()
        referenced_files.update(self._replace_graphics(root, sourcefile.parent))

        tree.write(self.path / sourcefile.name, encoding="utf-8", xml_declaration=True)
        # we copy the images after writing the TEI file (just in case something goes wrong)
        for filename, sourcepath in referenced_files:
            target = self.path / filename
            logger.debug("Moving %s to %s", target, sourcepath)
            shutil.copy(sourcepath, target)
            self.files.append(sourcepath)

    def _replace_graphics(
        self, root_node: ET.Element, source_dir: Path
    ) -> Set[Tuple[str, Path]]:
        "Replace the graphic elements in the tree."
        referenced_files = set()

        for graphic in root_node.findall(".//tei:graphic", namespaces=self.NAMESPACES):
            referenced_uri = graphic.attrib["url"]
            graphic_id = graphic.attrib.get(
                "{http://www.w3.org/XML/1998/namespace}id", ""
            )
            referenced_file = find_file(referenced_uri, source_dir)

            if referenced_file is not None:
                # if an id is set. we use the id as file name, not the original name
                image_name = referenced_file.name
                if graphic_id:
                    image_name = f"{graphic_id}{referenced_file.suffix}"
                graphic.set("url", f"./{image_name}")
                referenced_files.add((image_name, referenced_file))
        return referenced_files

    def __str__(self):
        return f"TEIObjectDirectory({self.path})"


class LIDOObjectDirectory(ObjectDirectory):
    """Class to handle a directory for a LIDO object.


    Provides as split method to create a object folder for the file given as argument.
    """


    def __str__(self):
        return f"LIDOObjectDirectory({self.path})"


class ProjectSplitter:
    """Class to split a project into single objects.

    Provides as split method to create a object folder for the file given as argument.
    """

    def __init__(self, outputdir: Path, project_dir: Path) -> List[Path]:
        self.outputdir = outputdir
        if not self.outputdir.exists():
            self.outputdir.mkdir()
        self.project_dir = project_dir 
        #self.bookkeeper_file = project_dir / BookKeeper.FILENAME
        #self._bookkeeper = BookKeeper(self.outputdir / BookKeeper.FILENAME)

    def split(self, sourcefile: Path, objecttype: str) -> None:
        """Split a file into an object directory.
        
        Return a list files (Path objects) which have been copied to the object directory.
        """
        #bk_file = sourcefile.parent / BookKeeper.FILENAME
        with BookKeeper(self.project_dir) as bk:
            validate_filename(sourcefile)
            pid = extract_pid(sourcefile)
            if objecttype == "auto":
                objecttype = guess_format(sourcefile)

            if objecttype == "tei":
                objdir = TEIObjectDirectory(self.outputdir / pid)
            elif objecttype == "lido":
                objdir = LIDOObjectDirectory(self.outputdir / pid)
            else:
                objdir = ObjectDirectory(self.outputdir / pid)
            objdir.split(sourcefile)
            for path in objdir.files:
                #self._bookkeeper.consumed(path)
                bk.consumed(str(path))
        return objdir.files
    
    def update_bookkeeper(self) -> None:
        "Update the bookkeeper with all files in the project directory."
        with BookKeeper(self.project_dir) as bk:
            bk.update()
        #self._bookkeeper.update()

    def reset(self) -> None:
        "Reset the bookkeeper."
        
        with BookKeeper(self.project_dir) as bk:
            bk.reset()
        #self._bookkeeper.reset()
