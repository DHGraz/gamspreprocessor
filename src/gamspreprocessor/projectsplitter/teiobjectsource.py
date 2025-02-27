"""The TEI Source of an object."""

from frozendict import frozendict

from .abstractfilereferences import AbstractXMLFileReference
from .abstractobjectsources import XMLObjectSource


class TEIGraphicReference(AbstractXMLFileReference):
    "A wrapper around a graphic element in a TEI file."

    def get_reference(self) -> str:
        """Return the uri of the graphic elementfrom a TEI file."""
        url = self._element.attrib.get("url", "")
        if not url:
            raise ValueError("No url attribute found in graphic element.")
        return url

    def set_reference(self, new_reference: str) -> None:
        """Set the reference to the graphic element."""
        self._element.set("url", new_reference)

    def get_id(self) -> str:
        """Return the id of the element.

        If no explicit id is set, return "".
        """
        return self._element.attrib.get("{http://www.w3.org/XML/1998/namespace}id", "")


class TEIObjectSource(XMLObjectSource):
    """Represents a TEI source file for a single GAMS object."""

    DEFAULT_NAMESPACES = frozendict({"tei": "http://www.tei-c.org/ns/1.0"})

    def rewrite_references(self):
        "Set the pid to a clean value and replace all referenced file references."
        root = self.tree.getroot()

        # replace the references in the graphic elements
        for graphic_element in root.findall(
            ".//tei:graphic", namespaces=self.DEFAULT_NAMESPACES
        ):
            ref = TEIGraphicReference(graphic_element)
            ref.replace_ref(self.source_file.parent, self.strip_extension)
            self.referenced_files.append(ref)

    def _extract_pid_from_content(self) -> str:
        """Return the pid (object id) of the object.

        pid is extracted from the TEIs idno element.
        If no pid is found, a ValueError is raised.
        """
        root = self.tree.getroot()
        idno_element = root.find(
            "./tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:idno",
            namespaces=self.DEFAULT_NAMESPACES,
        )
        return idno_element.text if idno_element is not None else ""

    def _set_pid(self, pid: str) -> None:
        """Set the pid of the object.

        This methods set a new value for the tei:idno element.
        """
        root = self.tree.getroot()
        idno_element = root.find(
            "./tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:idno",
            namespaces=self.DEFAULT_NAMESPACES,
        )
        idno_element.text = pid
