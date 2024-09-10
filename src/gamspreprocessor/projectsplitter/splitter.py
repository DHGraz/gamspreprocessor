"""Module to split a project into single objects, each in it's own folder.

The main class is ProjectSplitter, which provides a split method to create
an object folder for the file given as argument.
The module tries to find all referenced files (based on the object type)
and copies them to the object folder.
"""

import logging
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET

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
        output_dir: Path,
        project_dir: Path,
        replace_existing_object_dirs: bool = False,
    ):
        self.output_dir = output_dir
        self.project_dir = project_dir
        self.replace_existing_object_dirs = replace_existing_object_dirs

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

    def instantiate_object_directory(
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
                objdir = TEIObjectDirectory(self.output_dir / pid)
                logger.debug("Created TeiObjectDirectory for {pid}")
            elif objecttype == "lido":
                objdir = LIDOObjectDirectory(self.output_dir / pid)
                logger.debug("Created LidoObjectDirectory for {pid}")
            else:
                objdir = ObjectDirectory(self.output_dir / pid)
                logger.debug(
                    "Created ObjectDirectory for %s with unspecified XML objecttype %s",
                    pid,
                    objecttype,
                )
        else:
            objdir = ObjectDirectory(self.output_dir / pid)
            logger.debug(
                "Created ObjectDirectory for %s. Detected mime type was: %s",
                pid,
                mimetype,
            )
        return objdir

    def split(
        self, sourcefile: Path, objecttype: str = "auto", strip_prefix=False
    ) -> list[Path]:
        """Split a file into an object directory.

        strip_prefix: If True, the prefix of the pid ('o:') will be removed.
        Return a list files (Path objects) which have been copied to the object directory.
        """
        # TODO: Unsure if this is the right place to validate the filename?
        validate_filename(sourcefile)

        mimetype, objecttype = guess_format(sourcefile, objecttype)
        pid, from_content = self.extract_pid(sourcefile, objecttype, strip_prefix)
        try:
            objdir = self.instantiate_object_directory(pid, mimetype, objecttype)
        except FileExistsError as exp:
            if self.replace_existing_object_dirs:
                logger.warning("Replacing object directory for '%s'", pid)
                self._bookkeeper.remove_pid(pid)
                shutil.rmtree(self.output_dir / pid)
                objdir = self.instantiate_object_directory(pid, mimetype, objecttype)
            else:
                logger.error("Object '%s' already exists. Skipping.", pid)
                raise exp
        if strip_prefix and from_content:
            objdir.split(sourcefile, pid)
        else:
            objdir.split(sourcefile)
        for path in objdir.files:
            self._bookkeeper.add_pid(str(path), pid)
        self._bookkeeper.save()
        return objdir.files

    def update_bookkeeper(self) -> None:
        "Update the bookkeeper with all files in the project directory."
        self._bookkeeper.update(self.project_dir)
        self._bookkeeper.save()

    def reset(self) -> None:
        "Reset the bookkeeper."
        self._bookkeeper.reset()
        self._bookkeeper.save()

    @classmethod
    def extract_pid(
        cls, file_path: Path, object_type: str, strip_prefix: bool
    ) -> tuple[str, bool]:
        """Extract the pid from a path.

        If the PID was extracted from the content (eg. TEI or LIDO file), the second return value is True.
        This is important, because this means that we might have to update the value in the file.

        If object_type is 'tei' or 'lido', we try to extract the PID from the file.
        If strip_prefix is True, we remove the prefix (eg.: 'o:') from the pid.
        If this fails or object_type is not known, we use the filename without extension.
        """
        from_content = False
        if object_type == "tei":
            root = ET.parse(file_path).getroot()
            element = root.find(
                "./tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:idno",
                namespaces={"tei": "http://www.tei-c.org/ns/1.0"},
            )
            if element is not None and element.text:
                pid = element.text
                from_content = True
        elif object_type == "lido":
            root = ET.parse(file_path).getroot()
            element = root.find(
                "./lido:lidoRecID", namespaces={"lido": "http://www.lido-schema.org"}
            )
            if element is not None and element.text:
                pid = element.text
                from_content = True
        else:
            pid = None

        if pid is None:
            pid = ".".join(file_path.name.split(".")[0:-1])
            from_content = False
        else:
            if strip_prefix:
                pid = pid.split(":")[-1]
        return pid, from_content
