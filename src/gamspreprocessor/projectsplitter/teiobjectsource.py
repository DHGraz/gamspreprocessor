"""The TEI Source of an object."""


from pathlib import Path
import shutil
from warnings import warn
import warnings
from frozendict import frozendict
from lxml import etree as ET
from uritools import urisplit
from gamspreprocessor.projectsplitter.objectsource import ObjectSource


from .filereference import FileReference

class TEIGraphicReference(FileReference):
    "A wrapper around a graphic element in a TEI file."

    def get_reference(self) -> str:
        """Return the uri of the graphic elementfrom a TEI file.
        """
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
        return self._element.attrib.get(
            "{http://www.w3.org/XML/1998/namespace}id", ""
        )
    

class TEIObjectSource(ObjectSource):
    """Represents a TEI source file for a single GAMS object.

    The TEIObjectSource is a subclass of ObjectSource and is used for TEI XML files.
    """

    DEFAULT_NAMESPACES = frozendict({
        "tei": "http://www.tei-c.org/ns/1.0"
        })
    

    def __init__(self, source_file: Path,  strip_prefix: bool, strip_extension: bool) -> None:
        """Initialize the TEIObjectSource.
        """
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
            warnings.warn(f"No pid found in TEI file {self.source_file}. Using filename as pid.")
        
        pid = self._normalize_pid(pid)
        self._validate_pid(pid)
        return pid

    def rewrite_references(self):
        "Set the pid to a clean value and replace all referenced file references."
        root = self.tree.getroot()
        # replace the pid in the idno element
        idno = root.find(
            ".//tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:idno",
            namespaces=self.DEFAULT_NAMESPACES,
        )
        # if there is a colon in pid, it should only be replaced in file names!
        idno.text = self.pid.replace("%3A", ":", 1)

        # replace the references in the graphic elements
        for graphic_element in root.findall(
            ".//tei:graphic", namespaces=self.DEFAULT_NAMESPACES
        ):
            
            ref = TEIGraphicReference(graphic_element)
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
        if self.strip_extension:
            target_file = object_dir / self.source_file.stem
        else:
            target_file = object_dir / self.source_file.name
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
        idno_element = root.find(
                "./tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:idno",
                namespaces=self.DEFAULT_NAMESPACES
            )
        return idno_element.text if idno_element is not None else ""
      
