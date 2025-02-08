"""Base class for ObjectDirectory.

Each ObjectDirerectory represents a directory that contains all files that
belong to a single GAMS object.
"""

import logging
import shutil
from pathlib import Path

from uritools import urisplit

logger = logging.getLogger(__name__)


class ObjectDirectory:
    "Class to handle a directory for a generic single object."

    def __init__(self, object_directory_path: Path):
        """Initialize the object directory.

        If the directory exists a FileExistsError will be raised.
        """
        self.files = []
        objects_dir = object_directory_path.parent
        object_id = object_directory_path.name.replace(":", "%3A")

        self.path = objects_dir / object_id
        if self.path.is_dir():
            raise FileExistsError(f"Directory {self.path} already exists")
        
        self.path.mkdir()

    def split(self, sourcefile: Path, new_pid=None) -> None:
        "Copy the sourcefile to the object directory."
        shutil.copy(sourcefile, self.path)
        self.files.append(sourcefile)

    @classmethod
    def find_file(cls, referenced_uri: str, source_dir: Path) -> Path | None:
        """Try to find a file below source_dir with might match the file referenced in uri.

        The file will be identified by the best matching path (dir + filename)
        If 2 or more paths are ranked equally, the shortest matching path will be returned.

        Return path to the first file which matches or None if no file was found
        """
        uri_path:str = urisplit(referenced_uri).path
        glob_pattern = uri_path.split("/")[-1]
        ranked_paths = []
        for file in source_dir.rglob(glob_pattern):
            ranked_paths.append((cls.rank_path(uri_path, file), file, uri_path))
        if ranked_paths:
            # we sort by 1) rank (desc) and 2) length of the path (asc: *-1)
            ranked_paths.sort(key=lambda x: (x[0], len(str(x[1]) * -1)), reverse=True)
            return ranked_paths[0][1]
        return None

    @staticmethod
    def rank_path(long_path: Path, short_path: Path) -> int:
        "Return how many chars are the same at the end of both paths."
        score = 0
        long_str = str(long_path).replace('\\', '/')
        short_str = str(short_path).replace('\\', '/')
        for short, long in zip(short_str[::-1], long_str[::-1]):
            if short == long:
                score += 1
            else:
                break
        return score

    def __str__(self):
        return f"ObjectDirectory('{self.path}')"
