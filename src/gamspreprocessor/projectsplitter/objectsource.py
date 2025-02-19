from pathlib import Path
import re
import shutil
from typing import Protocol
import warnings

from .filereference import FileReference


class ObjectSource:
    """Represents a file which is used as base for a single GAMS object.

    Should be subclassed for specific formats like TEI or LIDO.
    """

    def __init__(
        self, source_file: Path, strip_prefix: bool, strip_extension: bool
    ) -> None:
        self.source_file: Path = source_file
        self.strip_prefix: bool = strip_prefix
        self.strip_extension: bool = strip_extension

        self.referenced_files: list[FileReference] = []

    def save(self, object_dir: Path) -> None:
        """Save the object to the target directory.

        Arguments:
        object_dir: The directory where the object contents should be saved.
                This directory must have the object PID as name.
                It will be created if it does not exist.
        """
        # do not forget to rewrite internal references if appropriate if you overwrite this method
        object_dir.mkdir(exist_ok=True)
        target_path = object_dir / self.pid
        shutil.copy(self.source_file, target_path)
        return [target_path]

    @property
    def pid(self) -> str:
        """Return the pid (object id) of the object.

        pid is extracted from the filename and changed if strip_prefix is True.
        If no pid is found, a ValueError is raised.
        """
        # For other formats, the pid might be extracted from the content.
        # pid = self._extract_pid_from_content()
        pid = self._extract_pid_from_filename()
        self._validate_pid(pid)
        return self._normalize_pid(pid)

    def _extract_pid_from_filename(self) -> str:
        """Extract the pid from the filename."""
        return self.source_file.stem if self.strip_extension else self.source_file.name

    def _extract_pid_from_content(self) -> str:
        """Extract the pid from the content.

        Return "" if PID cannot not be extracted.
        """
        # Implement this method in the subclass if the pid is in the content.
        raise NotImplementedError

    def _normalize_pid(self, pid: str) -> str:
        """Normalize the pid."""
        pid = pid.replace(":", "%3A", 1)
        if self.strip_prefix and "%3A" in pid:
            pid = pid.split("%3A")[1]
        return pid

    @classmethod
    def _validate_pid(cls, pid: str) -> None:
        "Make sure, the pid only contains valid charcters."
        allowed_pattern = r"^([a-zA-Z]+(:|%3A|%3a))?[a-zA-Z0-9-._]+$"

        m = re.match(allowed_pattern, pid)
        if m is not None:
            if ":" in pid or "%3A" in pid.upper():
                warnings.warn(
                    f"PID {pid} contains a colon, which is discouraged in the new GAMS.",
                    UserWarning,
                )
            return True
        else:
            raise ValueError(
                f"PID {pid} does not match the allowed pattern {allowed_pattern}"
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.source_file}, self.strip_prefix, self.strip_extension)"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.source_file})"
