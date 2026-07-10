"""Split project files into objects directories.

This package contains modules for splitting up project folders into object directories.
"""

from collections.abc import Sequence
from pathlib import Path

from gamslib.formatdetect import detect_format
from gamslib.formatdetect.formatinfo import SubType

from gamspreprocessor.objectsource import (
    AbstractObjectSource,
    GenericObjectSource,
    LIDOObjectSource,
    TEIObjectSource,
)
from gamspreprocessor.projectsplitter.bookkeeper import BookKeeper
from gamspreprocessor.projectsplitter.splitter import ProjectSplitter

def make_object_source(
    source_file: Path, use_format="auto", strip_prefix=True, strip_extension=False
) -> AbstractObjectSource:
    """ObjectSource factory function.

    Arguments:
    source_file: Path to the source file.
    use_format: The format to use for the source file. Can be 'auto', 'tei' or 'lido'.
    strip_prefix: If True, the prefix of the pid ('o:') will be removed.

    Returns an ObjectSource object for the given source_file.
    """
    if not source_file.is_file():
        raise FileNotFoundError(f"File {source_file} not found or not a file.")

    use_format_lower = use_format.lower()
    if use_format_lower == "auto":
        format_info = detect_format(source_file)
        subtype = format_info.subtype
    elif use_format_lower == "tei":
        subtype = SubType.TEIP5
    elif use_format_lower == "lido":
        subtype = SubType.LIDO
    else:
        raise ValueError(
            f"Invalid format type: '{use_format}'. Must be 'auto', 'tei' or 'lido'."
        )

    if subtype in (SubType.TEIP4, SubType.TEIP5):
        obj_src = TEIObjectSource(source_file, strip_prefix, strip_extension)
    elif subtype == SubType.LIDO:
        obj_src = LIDOObjectSource(source_file, strip_prefix, strip_extension)
    else:
        obj_src = GenericObjectSource(source_file, strip_prefix, strip_extension)
    return obj_src


def split_project_files(  # noqa: PLR0913
    output_dir: Path | str,
    sourcefiles: Sequence[Path | str],
    object_format: str = "auto",
    reset: bool = False,
    replace: bool = False,
    strip_prefix: bool = False,
) -> tuple[int, int]:
    """Split one or more source files into object directories.

    Returns a tuple with the number of object directories created and the number of files
    copied into those directories.
    """
    if len(sourcefiles) == 0:
        raise ValueError("No processable source files found.")

    source_paths = [Path(sourcefile) for sourcefile in sourcefiles]
    splitter = ProjectSplitter(Path(output_dir), source_paths[0].parent, replace)
    if reset:
        splitter.reset()
    splitter.update_bookkeeper()

    object_counter = 0
    file_counter = 0
    for sourcefile in source_paths:
        copied_files = splitter.split(sourcefile, object_format, strip_prefix)
        object_counter += 1
        file_counter += len(copied_files)
    return object_counter, file_counter


def create_project_splitter(
    output_dir: Path | str,
    project_dir: Path | str,
    replace: bool = False,
    reset: bool = False,
) -> ProjectSplitter:
    """Create and initialize a ProjectSplitter instance for public use."""
    splitter = ProjectSplitter(Path(output_dir), Path(project_dir), replace)
    if reset:
        splitter.reset()
    splitter.update_bookkeeper()
    return splitter


def split_project_file(
    splitter: ProjectSplitter,
    sourcefile: Path | str,
    object_format: str = "auto",
    strip_prefix: bool = False,
) -> list[Path]:
    """Split a single source file into an object directory using an existing splitter."""
    return splitter.split(Path(sourcefile), object_format, strip_prefix)


def list_unhandled_files(output_dir: Path | str) -> list[Path]:
    """Return files that are still unhandled in the given object directory tree."""
    objects_dir = Path(output_dir)
    bookkeeper_file = objects_dir / BookKeeper.FILENAME
    if not bookkeeper_file.exists():
        raise FileNotFoundError("No bookkeeper file found. Did you run split?")
    bookkeeper = BookKeeper(bookkeeper_file)
    return bookkeeper.get_unhandled()


__all__ = [
    "BookKeeper",
    "ProjectSplitter",
    "create_project_splitter",
    "list_unhandled_files",
    "make_object_source",
    "split_project_file",
    "split_project_files",
]
