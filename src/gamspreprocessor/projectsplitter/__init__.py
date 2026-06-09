"""Split project files into objects directories.

This package contains modules for splitting up project folders into object directories.
"""

from pathlib import Path

from gamslib.formatdetect import detect_format
from gamslib.formatdetect.formatinfo import SubType

from gamspreprocessor.objectsource import (
    AbstractObjectSource,
    GenericObjectSource,
    LIDOObjectSource,
    TEIObjectSource,
)

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
