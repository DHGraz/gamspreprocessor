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

    def __init__(self, path: Path):
        """Initialize the object directory.

        If the directory exists and replace is False, a FileExistsError will be raised.
        So set replace to True if you want to replace the directory.
        """
        self.files = []
        self.path = path
        if self.path.is_dir():
            raise FileExistsError(f"Directory {self.path} already exists")
        self.path.mkdir()

    def split(self, sourcefile: Path):
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
        uri = urisplit(referenced_uri)
        path = uri.path
        if path.endswith("/"):
            path = path[:-1]

        ranked_paths = []
        for file in source_dir.rglob(path.split("/")[-1]):
            ranked_paths.append((cls.rank_path(path, file), file))

        if ranked_paths:
            # we sort by 1) rank (desc) and 2) length of the path (asc: *-1)
            ranked_paths.sort(key=lambda x: (x[0], len(str(x[1]) * -1)), reverse=True)
            return ranked_paths[0][1]
        return None

    @staticmethod
    def rank_path(short_path: Path, long_path: Path) -> int:
        "Return how many chars are the same at the end of both paths."
        score = 0

        for short, long in zip(str(short_path)[::-1], str(long_path)[::-1]):
            if short == long:
                score += 1
            else:
                break
        return score

    def __str__(self):
        return f"ObjectDirectory({self.path})"
