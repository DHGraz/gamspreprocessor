import shutil
from pathlib import Path

from gamspreprocessor.projectsplitter.abstractobjectsources import AbstractObjectSource

from .abstractfilereferences import AbstractFileReference


class GenericObjectSource(AbstractObjectSource):
    """A file which is used as base for a single generic GAMS object.

    Use this class for any file types, where no reference rewriting
    is necessary or possible.
    """

    def __init__(
        self, source_file: Path, strip_prefix: bool, strip_extension: bool
    ) -> None:
        super().__init__(source_file, strip_prefix, strip_extension)
        self._new_pid: str|None = None

    @property
    def pid(self) -> str:
        """Return the pid (object id) of the object.
        """
        # As the new pid cannot be stored in content, we have to store it in the object.
        # this is done in the set_pid method.
        if self._new_pid is None:
            pid = self._extract_pid_from_filename()
        else:
            pid = self._new_pid
        return pid
            
    def save(self, object_dir: Path) -> None:
        """Save the object to the target directory.

        :param object_dir: The directory where the object contents should be saved.
                This directory must have the object PID as name.
                It will be created if it does not exist.
        """
        # do not forget to rewrite internal references if appropriate if you overwrite this method
        object_dir.mkdir(exist_ok=True)
        target_path = object_dir / self.safe_pid
        shutil.copy(self.source_file, target_path)
        return [target_path]


    def _set_pid(self, new_pid: str) -> None:
        self._new_pid = new_pid

    def rewrite_references(self) -> None:
        """Rewrite internal references if appropriate."""
        # As we ignore content of files, there is no need to rewrite references.
        pass
