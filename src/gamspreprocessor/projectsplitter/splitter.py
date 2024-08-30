"""Module to split a project into single objects, each in it's own folder.

The main class is ProjectSplitter, which provides a split method to create
an object folder for the file given as argument.
The module tries to find all referenced files (based on the object type)
and copies them to the object folder.
"""

import logging
import shutil
from pathlib import Path

from gamspreprocessor.projectsplitter.lidoobjectdir import LIDOObjectDirectory
from gamspreprocessor.projectsplitter.objectdir import ObjectDirectory
from gamspreprocessor.projectsplitter.teiobjectdir import TEIObjectDirectory
from gamspreprocessor.utils import validate_filename

from .bookkeeper import BookKeeper
from .formatguesser import guess_format

logger = logging.getLogger(__name__)


class ProjectSplitter:
    """Class to split a project into single objects.

    Provides as split method to create a object folder for the file given as argument.
    """

    def __init__(
        self,
        outputdir: Path,
        project_dir: Path,
        replace_existing_object_dirs: bool = False,
    ):
        self.outputdir = outputdir
        self.replace_existing_object_dirs = replace_existing_object_dirs
        if not self.outputdir.exists():
            self.outputdir.mkdir()
        self.project_dir = project_dir
        self.update_bookkeeper()
        replace_msg = ""
        if self.replace_existing_object_dirs:
            replace_msg = "Existing object directories will be replaced."
        logger.debug(
            "ProjectSplitter initialized with outputdir %s and project_dir %s. %s",
            outputdir,
            project_dir,
            replace_msg,
        )

    def make_object_dir(
        self, pid: str, mimetype: str, objecttype: str
    ) -> ObjectDirectory:
        """ObjectType factory.

        Return an ObjectDirectory or a derived class for a given pid depending
        in objecttype.

        Will raise a FileExistsError if the directory already exists (ie. the object
        has already been split).
        """
        if mimetype == "application/xml":
            if objecttype == "tei":
                objdir = TEIObjectDirectory(self.outputdir / pid)
                logger.debug("Created TeiObjectDirectory for {pid}")
            elif objecttype == "lido":
                objdir = LIDOObjectDirectory(self.outputdir / pid)
                logger.debug("Created LidoObjectDirectory for {pid}")
            else:
                objdir = ObjectDirectory(self.outputdir / pid)
                logger.debug(
                    "Created ObjectDirectory for %s with unspecified XML objecttype %s",
                    pid,
                    objecttype,
                )
        else:
            objdir = ObjectDirectory(self.outputdir / pid)
            logger.debug(
                "Created ObjectDirectory for %s. Detected mime type was: %s", pid, mimetype
            )
        return objdir

    def split(self, sourcefile: Path, objecttype: str = "auto") -> list[Path]:
        """Split a file into an object directory.

        Return a list files (Path objects) which have been copied to the object directory.
        """
        with BookKeeper(self.project_dir) as bk:
            validate_filename(sourcefile)
            pid = self.extract_pid(sourcefile)
            mimetype, objecttype = guess_format(sourcefile, objecttype)
            try:
                objdir = self.make_object_dir(pid, mimetype, objecttype)
            except FileExistsError as exp:
                if self.replace_existing_object_dirs:
                    logger.warning("Replacing object directory for '%s'", pid)
                    bk.remove_pid(pid)
                    shutil.rmtree(self.outputdir / pid)
                    objdir = self.make_object_dir(pid, mimetype, objecttype)
                else:
                    logger.error("Object '%s' already exists. Skipping.", pid)
                    raise exp
            objdir.split(sourcefile)
            for path in objdir.files:
                bk.add_pid(str(path), pid)
        return objdir.files

    def update_bookkeeper(self) -> None:
        "Update the bookkeeper with all files in the project directory."
        with BookKeeper(self.project_dir) as bk:
            bk.update()

    def reset(self) -> None:
        "Reset the bookkeeper."

        with BookKeeper(self.project_dir) as bk:
            bk.reset()

    @classmethod
    def extract_pid(cls, path: Path) -> str:
        """Extract the pid from a path.

        This is only useful if path is the main file of an object and contains
        the pid as filename.
        """
        # TODO: Maybe this must be more sophisticated eg. if the object name has
        # to be extracted from content (TEI)
        return ".".join(path.name.split(".")[0:-1])
