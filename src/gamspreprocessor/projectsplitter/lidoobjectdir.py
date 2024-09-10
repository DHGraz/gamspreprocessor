"""Module to handle a directory for a LIDO object."""

import logging
import mimetypes
import shutil
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from uritools import urisplit

from gamspreprocessor.utils import get_namespaces, register_namespaces

from .objectdir import ObjectDirectory

logger = logging.getLogger(__name__)


@dataclass
class ResourceSet:
    "Represents important data from a LIDO resourceSet element."

    resource_id: str
    resource_type: str
    link_format: str
    link_url: str

    def get_new_url(self) -> str:
        "Return the new URL for the resource."
        extension = mimetypes.guess_extension(self.link_format)
        if extension is None:
            if "://" in self.link_url:
                uri = urisplit(self.link_url)
                suffix = Path(uri.path).suffix
            else:
                suffix = Path(self.link_url).suffix
            if suffix:
                extension = Path(uri.path).suffix
            else:
                extension = ""
        logger.debug("Extension for %s is %s", self.link_url, extension)
        return f"./{self.resource_id}{extension}"

    @classmethod
    def from_element(
        cls, element: ET.Element, namespaces: dict[str, str]
    ) -> "ResourceSet":
        "Create a ResourceSet object from a XML resourceSet element."
        resourceset_element = element
        resourceid_element = resourceset_element.find(
            "lido:resourceID", namespaces=namespaces
        )
        resourcelink_element = resourceset_element.find(
            "lido:resourceRepresentation/lido:linkResource", namespaces=namespaces
        )

        resource_id = resourceid_element.text
        resource_type = resourceid_element.attrib[f"{{{namespaces['lido']}}}type"]
        link_format = resourcelink_element.attrib[
            f"{{{namespaces['lido']}}}formatResource"
        ]
        link_url = resourcelink_element.text
        return cls(resource_id, resource_type, link_format, link_url)


class LIDOObjectDirectory(ObjectDirectory):
    """Class to handle a directory for a LIDO object.


    Provides as split method to create a object folder for the file given as argument.
    """

    DEFAULT_NAMESPACE = {"lido": "http://www.lido-schema.org"}

    def split(self, sourcefile: Path, new_pid=None) -> None:
        """Copy the sourcefile and all referenced files to the object directory.

        If new_pid is given, the old pid will be replaced with the new one in the xml document.
        """
        # Keeps all files which must be copied to the object directory
        referenced_files: set[tuple[str, Path]] = set()

        shutil.copy(sourcefile, self.path)
        self.files.append(sourcefile)

        # from now on we operate on the copied file
        new_sourcefile = self.path / sourcefile.name

        # we want the keep the original prefixes in the namespaces
        register_namespaces(get_namespaces(new_sourcefile))

        tree = ET.parse(new_sourcefile)
        root = tree.getroot()
        # if we have a new pid (because we stripped it), we replace the old one
        if new_pid is not None:
            root.find('./lido:lidoRecID', namespaces=self.DEFAULT_NAMESPACE).text = new_pid
        referenced_files.update(self._replace_resource_set(root, sourcefile.parent))

        tree.write(self.path / sourcefile.name, encoding="utf-8", xml_declaration=True)
        # we copy the images after writing the TEI file (just in case something goes wrong)
        for filename, sourcepath in referenced_files:
            target = self.path / filename
            logger.debug("Moving %s to %s", target, sourcepath)
            shutil.copy(sourcepath, target)
            self.files.append(sourcepath)

    def _replace_resource_set(
        self, root_node: ET.Element, source_dir: Path
    ) -> set[tuple[str, Path]]:
        "Replace the URIs in the resourceSet elements in the tree."
        referenced_files = set()

        for resourceset_element in root_node.findall(
            ".//lido:resourceSet", namespaces=self.DEFAULT_NAMESPACE
        ):
            resourceset = ResourceSet.from_element(
                resourceset_element, self.DEFAULT_NAMESPACE
            )
            referenced_file = self.find_file(resourceset.link_url, source_dir)
            if referenced_file is not None:
                new_url = resourceset.get_new_url()
                referenced_files.add((new_url, referenced_file))
                resourceset_element.find(
                    ".//lido:linkResource", namespaces=self.DEFAULT_NAMESPACE
                ).text = new_url
        return referenced_files

    def __str__(self):
        return f"LIDOObjectDirectory({self.path})"
