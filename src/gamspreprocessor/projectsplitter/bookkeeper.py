"""Keep track of processed files, also between runs.

The bookkeeper keeps track of which files have been processed for which object.
As the bookkeeper data is stored in the project directory automatically, the
state of previous runs is preserved. The bookkeeper is used to find out which
files have not been processed yet. This is important for the incremental processing.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class BookKeeper:
    """A class to keep track of files that have been processed.

    As the project dir also contains referenced data streams (images, etc.),
    we need to keep track of which files have been processed and which have not.
    It important for the incremental processing of the project that the user
    can find out which files have not been processed yet.
    """

    # the default filename where data is stored between runs.
    FILENAME = ".bookkeeping.json"

    # We use pathlib.Path for public interfaces, but strings for paths internally
    # because json does not support Path objects and is does not really make sense
    # to cast values from an to Path objects.
    def __init__(self, storage_path: Path) -> None:
        """Initialize the BookKeeper object.

        'data_path' is the path to the file where the bookkeeping data is stored.
        

        If you plan to run the splitter multiple times for a single project, make sure
        that the 'data_path' is the same for all runs.
        """
        self.storage_path: Path = storage_path
        self._data: dict[str, list[str]] = {}

        ## read stored data from disk (if it exists)
        self._load_data()


    def save(self) -> None:
        "Write data to disk."
        with self.storage_path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False)
        logger.debug("Bookkeeper data written to '%a'", self.storage_path)

    def add_pid(self, filepath: Path|str, pid: str) -> None:
        """Mark a file as used for an object with ID pid.

        As a file can be used by more than one object, we keep the
        objects it is referenced in as list of object pids.
        """
        if isinstance(filepath, str):
            filepath = Path(filepath)

        posix_path = filepath.resolve().as_posix()

        pids_for_file = self._data.get(posix_path, [])
        
        if pid not in pids_for_file:
            pids_for_file.append(pid)
            logger.debug("Added object pid '%s' for '%s' to bookkeeper", pid, posix_path)
        self._data[posix_path] = pids_for_file

    def remove_pid(self, pid: str) -> None:
        """Remove object ID pid from all entries.

        The is useful if an existing object is replaced by a new one.
        """
        for filepath, pids in self._data.items():
            if pid in pids:
                self._data[filepath].remove(pid)
                logger.debug(
                    "Removed object '%s' from '%s' in bookkeeper", pid, filepath
                )

    def get_unhandled(self) -> list[Path]:
        "Return a list of paths for all files that have not been consumed yet."
        return [Path(file) for file, pids in self._data.items() if not pids]

    def reset(self) -> None:
        "Reset the bookkeeper."
        self._data = {}
        self.save()

    def get_pids_for_file(self, filepath: Path) -> list[str]:
        "Return a list of object pids for a file."
        posix_path = filepath.resolve().as_posix()
        return self._data.get(posix_path, [])

    def _load_data(self) -> dict[str, Any] | None:
        "Load data from the json file in self.storage_path."
        if self.storage_path.exists():
            with open(self.storage_path, encoding="utf-8") as f:
                self._data = json.load(f)
            logger.debug("Bookkeeper data loaded from '%s'", self.storage_path)
        else:
            logger.debug(
                "Bookkeeper data file '%s' not found, starting with empty data.",
                self.storage_path,
            )
            self._data = {}

    def update(self, project_path: Path) -> None:
        """Merge already registered files with newly collected files.

        Also remove files which have been deleted since last run.
        'project_path' is the root directory of the project files.
        """
        files_to_ignore = ["object.csv", "datastreams.csv"]
        all_files = set()

        for filepath in project_path.rglob("*"):
            if filepath.is_file():
                if filepath.name in files_to_ignore or filepath.suffix == ".log":
                    logger.debug("skipping '%s' while updating bookkeeper", filepath)
                    continue
                posix_path = filepath.resolve().as_posix()
                #relative_path = filepath.relative_to(project_path).as_posix() 
                if posix_path not in self._data:
                    self._data[posix_path] = []
                all_files.add(posix_path)

        removed_files = set(self._data.keys()) - all_files
        for file in removed_files:
            self._data.pop(file)
            logger.debug("Removed deleted file '%s' from bookkeeper", file)
        self.save()

