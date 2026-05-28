"""A module for handling references in (XML) documents."""

import abc
import shutil
from pathlib import Path

from lxml import etree as ET
from uritools import urisplit


class AbstractFileReference(metaclass=abc.ABCMeta):
    """An abstract class for handling references in documents.
    """

    def __init__(self) -> None:
        """Initialize the FileReference.
        """
        self.source_file: Path | None = None

    @abc.abstractmethod
    def get_reference(self) -> str:
        """Return the reference as it is set in the element.

        As this depends on the specific element, this method MUST be implemented by the subclass.
        """

    @abc.abstractmethod
    def set_reference(self, new_reference: str) -> None:
        """Set a new reference to the reference element.

        As this depends on the specific element, this method MUST be
        implemented by the subclass.

        'new_reference' should be a string containing a path relative to
        the object directory. Typically this will be something
        like './foo.png'.
        """

    @abc.abstractmethod
    def get_id(self) -> str:
        """Return the id of the element.

        As this depends on the specific element, this method MUST be
        implemented by the subclass.

        If no explicit id is set or not even possible in the schema of the
        subclassed element, return "".
        """

    def replace_ref(self, file_root: Path, strip_extension: bool) -> None:
        """Replace the reference in the graphic element with a new value.

        If strip_extension is set to True, the extension of the source file
        will be stripped from the reference.

        Normally there is no need to implement this method in the subclass,
        as it will work for any subclass.
        """
        ref_uri = self.get_reference()
        self.source_file = self._find_source_file(ref_uri, file_root)
        if self.source_file is not None:
            ref_id = self.get_id()
            if ref_id:
                new_ref = f"./{ref_id}"
            else:  # noqa: PLR5501
                if not strip_extension:
                    new_ref = f"./{self.source_file.name}"
                else:
                    new_ref = f"./{self.source_file.stem}"
            self.set_reference(new_ref)

    def copy_file(self, object_dir: Path) -> Path | None:
        """Copy the referenced file to the object directory.

        Normally there is no need to implement this method in the
        subclass, as it should work for any subclass.

        Return the path to the copied file in object_dir.
        """
        target_file = None
        # it makes no sense to copy a file which does not exist
        if self.source_file is not None:
            target_name = self.get_reference()
            target_file = object_dir / target_name
            if not target_file.exists():
                shutil.copy(self.source_file, target_file)
        return target_file

    @classmethod
    def _find_source_file(cls, referenced_uri: str, file_root: Path) -> Path | None:
        """Try to find a file below source_dir which might match the file referenced in uri.

        The file will be identified by the best matching path (dir + filename)
        If 2 or more paths are ranked equally, the shortest matching path will be returned.

        Return path to the first file which matches or None if no file was found
        """
        uri_path: str = urisplit(referenced_uri).path
        glob_pattern = uri_path.rsplit("/", maxsplit=1)[-1]
        ranked_paths = []
        for file in file_root.rglob(glob_pattern):
            ranked_paths.append((cls._rank_path(Path(uri_path), file), file, uri_path))
        if ranked_paths:
            # we sort by 1) rank (desc) and 2) length of the path (asc: *-1)
            ranked_paths.sort(key=lambda x: (x[0], len(str(x[1]) * -1)), reverse=True)
            return ranked_paths[0][1]
        return None

    @classmethod
    def _rank_path(cls, long_path: Path, short_path: Path) -> int:
        "Return how many chars are the same at the end of both paths."
        score = 0

        long_str = long_path.as_posix()
        short_str = short_path.as_posix()

        # An empty paths as_posix() will return ".". We need to handle this case
        long_str = "" if long_str == "." else long_str
        short_str = "" if short_str == "." else short_str
        for short_char, long_char in zip(short_str[::-1], long_str[::-1]):
            if short_char == long_char:
                score += 1
            else:
                break
        return score

    def __hash__(self):
        # the source file is the one we want to distinguish the object
        if self.source_file is None:
            return hash(f"{self.__class__.__name__!s} {id(self)}")
        return hash(f"{self.__class__.__name__!s} {self.source_file.absolute()}")
        return hash(f"{self.__class__.__name__!s} {self.source_file.absolute()}")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.source_file!s})"

    def __str__(self):
        return f"{self.__class__.__name__!s} for '{self.source_file!s}'"


class AbstractXMLFileReference(AbstractFileReference):
    """An abstract class for handling references in XML documents.

    Subclass this class for any XML element which contains a reference, which might be
    resolvable to a file.

    For almost all cases implement the `get_reference()`, `set_reference()` and `get_id()`
    methods should be enough.
    """

    def __init__(self, element: ET.Element) -> None:  # pylint: disable=I1101
        """Initialize the FileReference.

        Arguments:
        element: The XML element which contains the reference.
        """
        super().__init__()
        self._element: ET.Element = element  # pylint: disable=I1101

    @abc.abstractmethod
    def get_reference(self) -> str:
        """Return the reference as it is set in the element.

        As this depends on the specific element, this method MUST be implemented by the subclass.
        """

    @abc.abstractmethod
    def set_reference(self, new_reference: str) -> None:
        """Set a new reference to the reference element.

        As this depends on the specific element, this method MUST be
        implemented by the subclass.

        'new_reference' should be a string containing a path relative to
        the object directory. Typically this will be something
        like './foo.png'.
        """

    @abc.abstractmethod
    def get_id(self) -> str:
        """Return the id of the element.

        As this depends on the specific element, this method MUST be
        implemented by the subclass.

        If no explicit id is set or not even possible in the schema of the
        subclassed element, return "".
        """

    def __repr__(self):
        return f"{self.__class__.__name__}({self._element!r})"
