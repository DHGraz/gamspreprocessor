"""Provide functionality to guess the format of a file based on its content.

This is a very naive implementation that only uses file extensions and XML namespaces.
It is not very reliable, but it is a start.

Detecting and validating formats seems to be a big mess if an application
needs to be portable and distributable. There is an old (but nice) rant
about this: https://github.com/KBNLresearch/omSipCreator/issues/23.

"""

from pathlib import Path

from gamslib.formatdetect import detect_format


def guess_format(filename: str | Path, explicit_type: str = "auto") -> tuple[str, str]:
    """Guess the format of the file from the extension.

    It does more than the mimetype guesser, as it also checks the namespaces for xml files.

    Uses the formatdetector from gamslib to find out the format of the file.

    Returns a tuple with the content type and the (sub)format.
    """
    filepath = Path(filename) if isinstance(filename, str) else filename

    format_info = detect_format(filepath)

    subtype = format_info.subtype if explicit_type == "auto" else explicit_type
    return format_info.mimetype, subtype
