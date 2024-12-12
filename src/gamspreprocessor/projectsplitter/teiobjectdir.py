"""Module to handle a directory for a TEI object."""

import logging
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET

from gamspreprocessor.utils import get_namespaces, register_namespaces

# from gamspreprocessor.projectsplitter.objectdir import find_file
from .objectdir import ObjectDirectory

logger = logging.getLogger(__name__)


class TEIObjectDirectory(ObjectDirectory):
    "Class to handle a directory for a TEI object."

    DEFAULT_NAMESPACE = {"tei": "http://www.tei-c.org/ns/1.0"}

    def split(self, sourcefile: Path, new_pid=None) -> None:
        "Copy the sourcefile and all referenced files to the object directory."
        # Keeps all files which must be copied to the object directory
        referenced_files: set[tuple[str, Path]] = set()

        shutil.copy(sourcefile, self.path)
        self.files.append(sourcefile)

        # from now on we operate on the copied file
        new_sourcefile = self.path / sourcefile.name

        namespaces = get_namespaces(sourcefile)
        # we want the keep the original prefixes in the namespaces
        register_namespaces(namespaces)

        tree = ET.parse(new_sourcefile)
        root = tree.getroot()
        # if we have a new pid (because we stripped it), we replace the old one
        if new_pid is not None:
            idno = root.find(
                "./tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:idno",
                namespaces=self.DEFAULT_NAMESPACE,
            )
            if idno is not None:
                idno.text = new_pid
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
    ) -> set[tuple[str, Path]]:
        "Replace the graphic elements in the tree."
        referenced_files = set()

        for graphic in root_node.findall(
            ".//tei:graphic", namespaces=self.DEFAULT_NAMESPACE
        ):
            referenced_uri = graphic.attrib["url"]
            graphic_id = graphic.attrib.get(
                "{http://www.w3.org/XML/1998/namespace}id", ""
            )
            referenced_file = self.find_file(referenced_uri, source_dir)

            if referenced_file is not None:
                # if an id is set, we use the id as file name, not the original name
                image_name = referenced_file.name
                if graphic_id:
                    image_name = f"{graphic_id}{referenced_file.suffix}"
                graphic.set("url", f"./{image_name}")
                referenced_files.add((image_name, referenced_file))
        return referenced_files

    def __str__(self):
        return f"TEIObjectDirectory('{self.path}')"
