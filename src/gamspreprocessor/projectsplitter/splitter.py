"""Module to split a project into single objects, each in it's own folder.

The main class is ProjectSplitter, which provides a split method to create
an object folder for the file given as argument.
The module tries to find all referenced files (based on the object type)
and copies them to the object folder.
"""

import logging
from pathlib import Path


from gamspreprocessor.projectsplitter.lidoobjectdir import LIDOObjectDirectory
from gamspreprocessor.projectsplitter.objectdir import ObjectDirectory
from gamspreprocessor.projectsplitter.teiobjectdir import TEIObjectDirectory
from gamspreprocessor.utils import extract_pid, validate_filename

from .. import NAME
from .bookkeeper import BookKeeper
from .formatguesser import guess_format

logger = logging.getLogger(NAME)


class ProjectSplitter:
    """Class to split a project into single objects.

    Provides as split method to create a object folder for the file given as argument.
    """

    def __init__(self, outputdir: Path, project_dir: Path) -> list[Path]:
        self.outputdir = outputdir
        if not self.outputdir.exists():
            self.outputdir.mkdir()
        self.project_dir = project_dir
        # self.bookkeeper_file = project_dir / BookKeeper.FILENAME
        # self._bookkeeper = BookKeeper(self.outputdir / BookKeeper.FILENAME)

    def split(self, sourcefile: Path, objecttype: str) -> None:
        """Split a file into an object directory.

        Return a list files (Path objects) which have been copied to the object directory.
        """
        # bk_file = sourcefile.parent / BookKeeper.FILENAME
        with BookKeeper(self.project_dir) as bk:
            validate_filename(sourcefile)
            pid = extract_pid(sourcefile)
            if objecttype == "auto":
                objecttype = guess_format(sourcefile)

            if objecttype == "tei":
                objdir = TEIObjectDirectory(self.outputdir / pid)
            elif objecttype == "lido":
                objdir = LIDOObjectDirectory(self.outputdir / pid)
            else:
                objdir = ObjectDirectory(self.outputdir / pid)
            objdir.split(sourcefile)
            for path in objdir.files:
                # self._bookkeeper.consumed(path)
                bk.consumed(str(path))
        return objdir.files

    def update_bookkeeper(self) -> None:
        "Update the bookkeeper with all files in the project directory."
        with BookKeeper(self.project_dir) as bk:
            bk.update()


    def reset(self) -> None:
        "Reset the bookkeeper."

        with BookKeeper(self.project_dir) as bk:
            bk.reset()
