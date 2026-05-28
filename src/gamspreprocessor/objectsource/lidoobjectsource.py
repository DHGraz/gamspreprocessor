"""LIDOObjectSource module for splitting up legacy project LIDO objects.
"""

from frozendict import frozendict

from gamspreprocessor.objectsource.abstractobjectsources import XMLObjectSource

from .abstractfilereferences import AbstractXMLFileReference


class LIDOResourceSet(AbstractXMLFileReference):
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
                "No linkResource element found in resourceSet element "
                f"(line {self._element.sourceline})."
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

    # Registry of XPaths to all references in LIDO files which might have to be rewritten.
    # If you find more elements that need to be rewritten, add the XPath to this dictionary
    # and create a new class inheriting from AbstractXMLFileReference, which handles the
    # replacement of the reference.
    REFERENCE_REGISTRY = frozendict({
        ".//lido:resourceSet": LIDOResourceSet,
    })

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
