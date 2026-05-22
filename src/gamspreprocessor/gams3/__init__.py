"""This module provides the main API forexporting GAMS 3 objects."""

from dataclasses import dataclass
from pathlib import Path
from typing import Generator
import warnings

from gamspreprocessor.gams3.apiquery import Gams3Query
from gamspreprocessor.gams3.object import Gams3Object
from gamspreprocessor.gams3.datastream import DataStream


@dataclass
class ExportResult:
    "Result of exporting a GAMS 3 object."

    obj: Gams3Object
    exported_files: list[Path]
    warnings: list[Warning]


def export_objects(
    pid_pattern: str,
    output_dir: Path,
    overwrite: bool = False,
    base_url: str = "https://gams.uni-graz.at/archive",
    strip_prefix: bool = False,
) -> Generator[ExportResult, None, None]:
    """Export all objects matching the given PID pattern from a GAMS 3 repository.

    Args:
        pid_pattern: A pattern to match PIDs, e.g. "o:foo*"
        output_dir: Path to the directory to save the exported objects to. 
        overwrite: Whether to overwrite existing object directories and files.
            If False, skip objects that already exist in the output directory.
        base_url: Base URL of the GAMS 3 repository, 
            default is "https://gams.uni-graz.at/archive"
        strip_prefix: Whether to strip the type prefix (e.g. o:) from the PID 
            when naming the subdirectories.
    Yields:
        An ExportResult for each exported object, containing the object, the 
            list of exported files, and any warnings.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    query = Gams3Query(base_url)
    for obj in query.find_objects(pid_pattern):
        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter("ignore", category=UserWarning)
            exported_files = obj.export(
                output_dir, overwrite=overwrite, strip_prefix=strip_prefix
            )
        yield ExportResult(obj, exported_files, list(warns))


__all__ = [
    "DataStream",
    "Gams3Object",
    "Gams3Query",
    "export_objects",
]
