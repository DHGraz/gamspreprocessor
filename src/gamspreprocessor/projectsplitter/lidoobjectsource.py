from pathlib import Path
import warnings

from frozendict import frozendict
from lxml import etree as ET

from gamspreprocessor.projectsplitter.abstractobjectsources import XMLObjectSource

from .filereference import FileReference

from .genericobjectsource import GenericObjectSource


class LIDOResourceSet(FileReference):
    "A wrapper around a ResourceSet element in a LIDO file."

    def get_reference(self) -> str:
        """Return the uri of the linkResource element of the resourceSet.

        This is the value of the text node of the
        `resourceRepresentation/lido:linkResource` element in the xml snippet.
        """
        linkresource_node = self._element.find(
            "lido:resourceRepresentation/lido:linkResource",
            namespaces=LIDOObjectSource.DEFAULT_NAMESPACES,
        )

        if linkresource_node is None or linkresource_node.text == "":
            raise ValueError(
                f"No linkResource element found in resourceSet element (line {self._element.sourceline})."
            )
        return linkresource_node.text

    def set_reference(self, new_reference: str) -> None:
        """Set the new linResource value."""
        linkresource_node = self._element.find(
            "lido:resourceRepresentation/lido:linkResource",
            namespaces=LIDOObjectSource.DEFAULT_NAMESPACES,
        )
        linkresource_node.text = new_reference

    def get_id(self) -> str:
        """Return the id of the element.

        If no explicit id is set, returns "".
        """
        resource_id_node = self._element.find(
            "lido:resourceID", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES
        )
        return "" if resource_id_node is None else resource_id_node.text or ""


class LIDOObjectSource(XMLObjectSource):
    """Represents a LIDO file for a single GAMS object.

    The TEIObjectSource is a subclass of ObjectSource and is used for TEI XML files.
    """

    DEFAULT_NAMESPACES: frozendict = frozendict({"lido": "http://www.lido-schema.org"})

    def rewrite_references(self):
        "Set the pid to a clean value and replace all referenced file references."
        root = self.tree.getroot()
        # replace the pid in the recId element (might have change due to strip_prefix)
        rec_id_node = root.find("./lido:lidoRecID", namespaces=self.DEFAULT_NAMESPACES)
        # if there is a colon in pid, it should only be replaced in file names!
        rec_id_node.text = self.pid.replace("%3A", ":", 1)

        # replace the references in the graphic elements
        for resourceset in root.findall(
            ".//lido:resourceSet", namespaces=self.DEFAULT_NAMESPACES
        ):
            ref = LIDOResourceSet(resourceset)
            ref.replace_ref(self.source_file.parent, self.strip_extension)
            self.referenced_files.append(ref)

    def _extract_pid_from_content(self) -> str:
        """Return the pid (object id) of the object.

        pid is extracted from the TEIs idno element.
        If no pid is found, a ValueError is raised.
        """
        root = self.tree.getroot()
        rec_id = root.find("./lido:lidoRecID", namespaces=self.DEFAULT_NAMESPACES)
        return rec_id.text if rec_id is not None else ""

    def _set_pid(self, pid: str) -> None:
        """Set the pid of the object.

        This methods set a new value for the tei:idno element.
        """
        root = self.tree.getroot()
        rec_id = root.find("./lido:lidoRecID", namespaces=self.DEFAULT_NAMESPACES)
        rec_id.text = pid
