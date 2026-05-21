from pathlib import Path
from typing import Generator

from gamspreprocessor.gams3.apiquery import Gams3Query
from gamspreprocessor.gams3.object import Gams3Object


def export_objects(
    pid_pattern: str,
    output_dir: Path,
    overwrite: bool = False,
    base_url: str = "https://gams.uni-graz.at/archive",
) -> Generator[Gams3Object, None, None]:
    """Export all objects matching the given PID pattern from a GAMS 3 repository.

    pid_pattern: A pattern to match PIDs, e.g. "o:foo*"
    output_dir: Directory to save the exported objects to. For each object, add a 
        subdirectory named after the pid
    overwrite: Whether to overwrite existing object directories and files. 
        If False, skip objects that already exist in the output directory.
    base_url: Base URL of the GAMS 3 repository, e.g. "https://gams.uni-graz.at/archive"
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    query = Gams3Query(base_url)
    for obj in query.find_objects(pid_pattern):
        obj.export(output_dir, overwrite=overwrite)
        yield obj
    