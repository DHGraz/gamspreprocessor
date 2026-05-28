"""Provides objects representing specific datastream subtypes.

Use these objects to handle datastreams of specific subtypes in a special way, e.g.
by rewriting references to other datastreams before exporting them to files.
"""

from pathlib import Path

from gamslib.formatdetect import detect_format
from gamslib.formatdetect.formatinfo import SubType

from gamspreprocessor.objectsource.genericobjectsource import GenericObjectSource
from gamspreprocessor.objectsource.lidoobjectsource import LIDOObjectSource, LIDOResourceSet
from gamspreprocessor.objectsource.teiobjectsource import TEIObjectSource
from gamspreprocessor.objectsource.abstractobjectsources import AbstractObjectSource
from gamspreprocessor.objectsource.abstractfilereferences import AbstractFileReference

__all__ = [
    "AbstractFileReference",
    "AbstractObjectSource",
    "GenericObjectSource",
    "LIDOObjectSource",
    "LIDOResourceSet",
    "TEIObjectSource",
    "make_object_source",
]

# def guess_format(filename: str | Path, explicit_type: str = "auto") -> tuple[str, str]:
#     """Guess the format of the file from the extension.

#     Uses the formatdetector from gamslib to find out the format of the file. This means,
#     that the type of format guesser can be configured via project.toml or
#     environment variables.

#     Returns a tuple with the content type and the (sub)format.
#     """
#     filepath = Path(filename) if isinstance(filename, str) else filename
#     format_info = detect_format(filepath)
#     subtype = format_info.subtype if explicit_type == "auto" else explicit_type
#     return format_info.mimetype, subtype


def make_object_source(
    source_file: Path,
    use_format: str = "auto",
    strip_prefix: bool = True,
    strip_extension: bool = False,
) -> GenericObjectSource:
    """ObjectSource factory.

    Return an ObjectSource or a subclass of ObjectSource representing the source file.
    The type of the returned class depends on mimetype and objecttype.
    """
    # just in case we get a string instead of a Path object, we convert it to a Path object
    filepath = Path(source_file) if isinstance(source_file, str) else source_file
    use_format = use_format.lower()
    if use_format == "auto":
        objecttype = detect_format(filepath).subtype
    elif use_format == "tei":
        objecttype = SubType.TEIP5
    elif use_format == "lido":
        objecttype = SubType.LIDO
    else:
        raise ValueError(
            f"Invalid format type: '{use_format}'. Must be 'auto', 'tei' or 'lido'."
        )

    # TODO: unsure if P4 needs its own ObjectSource class
    if objecttype in (SubType.TEIP4, SubType.TEIP5):
        return TEIObjectSource(source_file, strip_prefix, strip_extension)
    if objecttype == SubType.LIDO:
        return LIDOObjectSource(source_file, strip_prefix, strip_extension)
    return GenericObjectSource(source_file, strip_prefix, strip_extension)
