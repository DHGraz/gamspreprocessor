from pathlib import Path
import warnings

from frozendict import frozendict
from lxml import etree as ET

from .filereference import FileReference

from .objectsource import ObjectSource


class LIDOResourceSet(FileReference):
    "A wrapper around a ResourceSet element in a LIDO file."

    #   <lido:resourceSet lido:sortorder="1">
    #     <lido:resourceID lido:type="IMAGE">IMAGE.1</lido:resourceID>
    #     <lido:resourceRepresentation>
    #       <lido:linkResource lido:formatResource="image/jpeg">http://gams.uni-graz.at/o:ges.a-88/image01.jpeg</lido:linkResource>
    #     </lido:resourceRepresentation>
    #   </lido:resourceSet>

    def get_reference(self) -> str:
        """Return the uri of the linkResource element of the resourceSet."""
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
        """Set the reference to the graphic element."""
        linkresource_node = self._element.find(
            "lido:resourceRepresentation/lido:linkResource",
            namespaces=LIDOObjectSource.DEFAULT_NAMESPACES,
        )
        linkresource_node.text = new_reference

    def get_id(self) -> str:
        """Return the id of the element.

        If no explicit id is set, return "".
        """
        resource_id_node = self._element.find(
            "lido:resourceID", namespaces=LIDOObjectSource.DEFAULT_NAMESPACES
        )
        return "" if resource_id_node is None else resource_id_node.text or ""


class LIDOObjectSource(ObjectSource):
    """Represents a LIDO file for a single GAMS object.

    The TEIObjectSource is a subclass of ObjectSource and is used for TEI XML files.
    """

    DEFAULT_NAMESPACES = frozendict({"lido": "http://www.lido-schema.org"})

    def __init__(
        self, source_file: Path, strip_prefix: bool, strip_extension: bool
    ) -> None:
        """Initialize the LIDOObjectSource."""
        super().__init__(source_file, strip_prefix, strip_extension)

        self.tree = ET.parse(source_file)

    @property
    def pid(self) -> str:
        """Return the pid (object id) of the object.

        pid is extracted from content or filename if not found in content.
        If no pid is found, a ValueError is raised.
        """
        pid = self._extract_pid_from_content()
        if not pid:
            pid = self._extract_pid_from_filename()
            warnings.warn(
                f"No pid found in TEI file {self.source_file}. Using filename as pid."
            )

        pid = self._normalize_pid(pid)
        self._validate_pid(pid)
        return pid

    def rewrite_references(self):
        "Set the pid to a clean value and replace all referenced file references."
        root = self.tree.getroot()
        # replace the pid in the idno element
        rec_id_node = root.find("./lido:lidoRecID", namespaces=self.DEFAULT_NAMESPACES)
        # if there is a colon in pid, it should only be replaced in file names!
        rec_id_node.text = self.pid.replace("%3A", ":", 1)

        # replace the references in the graphic elements
        for resourceset in root.findall(
            "../lido:resourceSet", namespaces=self.DEFAULT_NAMESPACES
        ):
            ref = LIDOResourceSet(resourceset)
            ref.replace_ref(self.source_file.parent, self.strip_extension)
            self.referenced_files.append(ref)

    def save(self, object_dir: Path) -> list[Path]:
        """Save the object to the target directory.

        Arguments:
        object_dir: The directory where the object contents should be saved.
                This directory must have the object PID as name.
                It will be created if it does not exist.

        Return a list of all files copied in the object directory.
        """
        copied_files = []
        self.rewrite_references()
        object_dir.mkdir(exist_ok=True)
        # Save the main resource file
        target_file = object_dir / self.source_file.name
        # save the modified TEI file
        x = target_file.absolute()
        self.tree.write(target_file, encoding="utf-8", xml_declaration=True)
        
        copied_files.append(target_file)
        # copy the referenced files
        for ref in self.referenced_files:
            if ref.source_file is not None:
                copied_files.append(ref.copy_file(object_dir))
        return list(set(copied_files))


    def _extract_pid_from_content(self) -> str:
        """Return the pid (object id) of the object.

        pid is extracted from the TEIs idno element and changed if strip_prefix is True.
        If no pid is found, a ValueError is raised.
        """
        root = self.tree.getroot()
        rec_id = root.find("./lido:lidoRecID", namespaces=self.DEFAULT_NAMESPACES)
        return rec_id.text if rec_id is not None else ""
