"""Module to split a project into single objects, each in it's own folder.

The main class is ProjectSplitter, which provides a split method to create
an object folder for the file given as argument.
The module tries to find all referenced files (based on the object type)
and copies them to the object folder.
"""

import logging
import shutil
import warnings
from pathlib import Path

from gamspreprocessor.objectsource import make_object_source, GenericObjectSource

from .bookkeeper import BookKeeper

logger = logging.getLogger(__name__)


class ProjectSplitter:
    """Class to split a project into single objects.

    Provides as split method to create a object folder for the file given as argument.
    """

    def __init__(
        self,
        output_dir: Path,
        project_dir: Path,
        replace_existing_object_dirs: bool = False,
    ):
        """Initialize the ProjectSplitter.

        Arguments:
        output_dir: The directory where the object directories will be created.
        project_dir: The directory containing the original data.
        replace_existing_object_dirs: If True, existing object directories will
            be replaced. Default is False.
        """
        self.output_dir: Path = (
            output_dir  # this is where the object directories will be created
        )
        self.project_dir: Path = (
            project_dir  # this is the directory containing the original data
        )
        self.replace_existing_object_dirs: bool = replace_existing_object_dirs

        if not self.output_dir.exists():
            self.output_dir.mkdir()

        self._bookkeeper = BookKeeper(self.output_dir / BookKeeper.FILENAME)
        self.update_bookkeeper()
        replace_msg = ""
        if self.replace_existing_object_dirs:
            replace_msg = "Existing object directories will be replaced."
        logger.debug(
            "ProjectSplitter initialized with outputdir '%s' and project_dir '%s'. %s",
            output_dir,
            project_dir,
            replace_msg,
        )

    def make_object_source(
        self,
        source_file: Path,
        use_format: str = "auto",
        strip_prefix: bool = True,
        strip_extension: bool = False,
    ) -> GenericObjectSource:
        """ObjectSource factory.

        Return an ObjectSource or a subclass of ObjectSource representing the source file.
        The type of the returned class depends on mimetype and objecttype.

        Raises a FileExistsError if the directory already exists (ie. the object
        has already been split).
        """
        return make_object_source(
            source_file, use_format, strip_prefix, strip_extension
        )

    def split(
        self,
        sourcefile: Path,
        objecttype: str = "auto",
        strip_prefix=True,
        strip_extension=False,
    ) -> list[Path]:
        """Convert sourcefile into an object directory.

        Arguments:
        sourcefile: Path to the source file to be processed.
        objecttype: The format to use for the source file. Can be 'auto', 'tei' or 'lido'.
        strip_prefix: If True, the prefix of the pid ('o:') will be removed.

        Return a list files (Path objects) which have been copied to the object directory.
        """
        rv = []
        obj_src = self.make_object_source(
            sourcefile, objecttype, strip_prefix, strip_extension
        )
        obj_src.rewrite_pid()
        obj_src.rewrite_references()
        obj_output_dir = self.output_dir / obj_src.safe_pid
        if obj_output_dir.exists():
            if self.replace_existing_object_dirs:
                warnings.warn(f"Replacing object directory for '{obj_src.pid}'")
                self._bookkeeper.remove_pid(obj_src.pid)
                shutil.rmtree(obj_output_dir)
            else:
                raise FileExistsError(
                    f"Object directory '{obj_output_dir}' already exists."
                )
        for copied_file in obj_src.save(obj_output_dir):
            self._bookkeeper.add_pid(copied_file, obj_src.pid)
            rv.append(copied_file)
        return rv

    def update_bookkeeper(self) -> None:
        "Update the bookkeeper with all files in the project directory."
        self._bookkeeper.update(self.project_dir)
        self._bookkeeper.save()

    def reset(self) -> None:
        "Reset the bookkeeper."
        self._bookkeeper.reset()
        self._bookkeeper.save()
