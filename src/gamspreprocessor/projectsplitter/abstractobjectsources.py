"""Define "interfaces" for ObjectSource classes.


This module provides 2 abstract Classes:

  * AbstractObjectSource: Interface for all ObjectSource classes.
  * AbstractXMLObjectSource: Interface for XML ObjectSource classes.
"""

import re
import warnings
from abc import ABC, abstractmethod
from pathlib import Path

from frozendict import frozendict
from lxml import etree as ET

from .abstractfilereferences import AbstractFileReference


class AbstractObjectSource(ABC):
    """Define Interface for alls ObjectSource classes."""

    def __init__(
        self, source_file: Path, strip_prefix: bool, strip_extension: bool
    ) -> None:
        """Initialize the ObjectSource.

        :param source_file: Path to the source file, which should be
            transformed into an object directory.
        :param strip_prefix: If True, the prefix of the pid ('o:') will
            be removed.
        :param strip_extension: If True, the file extension will be
            removed from the pid.
        """
        self.source_file: Path = source_file
        self.strip_prefix: bool = strip_prefix
        self.strip_extension: bool = strip_extension

        self.referenced_files: list[AbstractFileReference] = []

    def rewrite_pid(self) -> str:
        """Replace the existing pid with the new one (eg. without prefix).

        Returns the new pid.
        """
        pid = self.pid
        if self.strip_prefix and ":" in pid:
            pid = pid.split(":")[1]
        self.validate_pid(pid)
        self._set_pid(pid)  # pylint: disable=E1101 # pylint does not recognize the abstract method
        return pid

    @abstractmethod
    def rewrite_references(self) -> None:
        """Rewrite internal references if appropriate.

        This method should be implemented in the subclass if the object
        content contains internal references, eg. TEI files containing
        references to images or other files which are part of the object.
        """

    @abstractmethod
    def save(self, object_dir: Path) -> None:
        """Save the object to the target directory.

        Arguments:
        :param object_dir: The directory where the object contents should be saved.
                This directory must have the object PID as name.
                It will be created if it does not exist.
        """

    @property
    @abstractmethod
    def pid(self) -> str:
        """Return the pid (object id) of the object.

        pid might be extracted from the filename and content, depending on the format.
        So this method must be implemented in the subclass.

        If no pid is found, a ValueError must be raised.
        """

    @property
    def safe_pid(self) -> str:
        """Return a safe version of the pid, which can be used in file names."""
        self.validate_pid(self.pid)
        pid = self.pid.replace(":", "%3A", 1)
        if self.strip_prefix and "%3A" in pid:
            pid = pid.split("%3A")[1]
        return pid

    @classmethod
    def validate_pid(cls, pid: str) -> bool:
        """Make sure, the pid only contains valid characters."""
        allowed_pattern = r"^([a-zA-Z]+(:|%3A|%3a))?[a-zA-Z0-9-._]+$"

        m = re.match(allowed_pattern, pid)
        if m is None:
            # if the pid does not match the allowed pattern, raise an error
            raise ValueError(
                f"Invalid PID {pid} does not match the allowed pattern {allowed_pattern}"
            )
        if ":" in pid or "%3A" in pid.upper():
            # we discourage the use of colons in PIDs, so we issue a warning
            # but do not raise an error, because we still want to allow them
            # for compatibility reasons.
            warnings.warn(
                f"PID {pid} contains a colon, which is discouraged in the new GAMS.",
                UserWarning,
            )

    def _extract_pid_from_filename(self) -> str:
        """Extract the pid from the filename."""
        return self.source_file.stem if self.strip_extension else self.source_file.name

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.source_file}, "
            f"strip_prefix={self.strip_prefix!s}, "
            f"strip_extension={self.strip_extension!s})"
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.source_file})"


class XMLObjectSource(AbstractObjectSource):
    """Subtype of AbstractObjectSource for XML files.

    All ObjectSource classes for XML should implement this interface.
    """

    # Set this for all subclasses!
    # This should be an abstract class property but this is no longer possible in Python :(
    DEFAULT_NAMESPACES: frozendict = frozendict({})

    def __init__(
        self, source_file: Path, strip_prefix: bool, strip_extension: bool
    ) -> None:
        """Initialize the TEIObjectSource.

        :param source_file: Path to the source file, which should be
            transformed into an object directory.
        :param strip_prefix: If True, the prefix of the pid ('o:')
            will be removed.
        :param strip_extension: If True, the file extension will
            be removed from the pid.
        """
        super().__init__(source_file, strip_prefix, strip_extension)

        self.tree = ET.parse(source_file)  # pylint: disable=I1101

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
        return pid

    def rewrite_references(self):
        "Set the pid to a clean value and replace all referenced file references."
        root = self.tree.getroot()

        # iterate over all XPath expressions in the reference registry and create a new
        # Reference Object for each element found in the XML file.
        for xpath, ref_class in self.REFERENCE_REGISTRY.items():  # pylint: disable=E1101  # not in ABC class
            for element in root.findall(xpath, namespaces=self.DEFAULT_NAMESPACES):
                ref = ref_class(element)
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

        # self.rewrite_references()
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

    @abstractmethod
    def _extract_pid_from_content(self) -> str:
        """Return the pid (object id) of the object.

        pid is extracted from files content and changed if strip_prefix is True.

        If no pid is found, a ValueError is raised.
        """

    @abstractmethod
    def _set_pid(self, pid: str) -> None:
        """Set the pid of the object.

        This method should be implemented in the subclass.
        """
