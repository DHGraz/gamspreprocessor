"""This module provides the main API forexporting GAMS 3 objects."""

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator

from gamslib.formatdetect.xmltypes import FormatDetectionWarning

from gamspreprocessor.gams3.apiquery import Gams3Query
from gamspreprocessor.gams3.datastream import DataStream
from gamspreprocessor.gams3.object import ExportError, Gams3Object


def export_objects(  # noqa: PLR0913 # pylint: disable=too-many-positional-arguments, too-many-arguments
    pid_pattern: str,
    output_dir: Path,
    overwrite: bool = False,
    base_url: str = "https://gams.uni-graz.at/archive",
    strip_prefix: bool = False,
    colon_replacement: str = "%3A",
) -> Generator[Gams3Object, None, None]:
    """Export all objects matching the given PID pattern from a GAMS 3 repository.

    Yield each exported Gams3Object.
    Export exceptions are converted to warnings, so you want to check the status attribute of each object.
    All warnings and errors are also collected in the warnings and errors attributes of each object, respectively.

    Args:
        pid_pattern: A pattern to match PIDs, e.g. "o:foo*"
        output_dir: Path to the directory to save the exported objects to.
        overwrite: Whether to overwrite existing object directories and files.
            If set to False, objects which already exist in the output directory
            are skipped.
        base_url: Base URL of the GAMS 3 repository,
            default is "https://gams.uni-graz.at/archive"
        strip_prefix: Whether to strip the type prefix (e.g. o:) from the PID
            when naming the subdirectories.
        colon_replacement: String to replace ":" in PIDs when naming subdirectories,
            default is "%3A". Ignored if strip_prefix is True.
    Yields:
        Each exported Gams3Object.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    query = Gams3Query(base_url)
        
    # ignore warnings from format detection of datastreams, which are not relevant for export
    warnings.filterwarnings("ignore", category=FormatDetectionWarning)  
    for obj in query.find_objects(pid_pattern):
        try:
            obj.export(
                output_dir,
                overwrite=overwrite,
                strip_prefix=strip_prefix,
                colon_replacement=colon_replacement,
            )
        except ExportError as e:
            warnings.warn(f"Failed to export object {obj.pid}: {e}")
        finally:
            yield obj


__all__ = [
    "DataStream",
    "ExportError",
    "Gams3Object",
    "Gams3Query",
    "export_objects",
]
