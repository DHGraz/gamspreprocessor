"""Keep track of files that have been processed between runs.
"""

import json
import os
from pathlib import Path


class BookKeeper:
    """A class to keep track of files that have been processed.

    As the project dir also contains referenced data streams (images, etc.), 
    we need to keep track of which files have been processed and which have not.
    It important for the incremental processing of the project that the user
    can find out which files have not been processed yet.
    """

    FILENAME = ".bookkeeping.json"

    # We use pathlib.Path for public interfaces, but strings for paths internally
    # because json does not support Path objects.
    def __init__(self, root_dir: Path):
        self.root_dir = str(root_dir)
        # the file where we keep track of the processed files
        self._datafile = os.path.join(self.root_dir, self.FILENAME)

        self._data = {}

        # read data from disk
        self._load_data()
        # update data with new files
        self._update_files()

    def dump(self) -> None:
        "Write data to disk"
        with open(self._datafile, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False)

    def consumed(self, file: str) -> None:
        "Mark a file as consumed."
        self._data[file] = True

    def get_unhandled(self) -> list[Path]:
        "Return a list of paths for all files that have not been consumed yet."
        return [Path(file) for file, consumed in self._data.items() if not consumed]

    def reset(self) -> None:
        "Reset the bookkeeper."
        self._data = {}
        self.dump()

    def _load_data(self) -> dict:
        "Load data from the json file, if it exists."
        if os.path.exists(self._datafile):
            with open(self._datafile, encoding="utf-8") as f:
                self._data = json.load(f)

    # def _collect_files(self, root_dir: str) -> None:
    #     "Search for (new) files in and below root_dir."
    #     new_files = []
    #     for root, _, files in os.walk(root_dir):
    #         for file in files:
    #             # skip the bookkeeping file and log files
    #             if file == self.FILENAME or file.endswith(".log"):
    #                 continue
    #             filepath = os.path.join(root, file)
    #             new_files.append(filepath)
    #     return new_files

    def _update_files(self):
        "Merge stored files with newly colleced files."
        all_files = set()
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                # skip the bookkeeping file and log files
                if file == self.FILENAME or file.endswith(".log"):
                    continue
                filepath = os.path.join(root, file)
                # add new files as unhandled
                if filepath not in self._data:
                    self._data[filepath] = False
                all_files.add(filepath)
        # remove files which have been deleted since last run
        removed_files = set(self._data.keys()) - all_files
        for file in removed_files:
            del self._data[file]    

        # # We have to do this in two steps:
        # # 1) We remove alle Files to avoid modifying the dictionary while iterating over it
        # # step 1: remove files which have been deleted since last run
        # new_data = self._collect_files(self.root_dir)
        # for file in self._data:
        #     if file not in new_data:
        #         del self._data[file]
        # # step 2: add new files
        # for file in new_data:
        #     if file not in self._data:
        #         self._data[file] = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        "Make sure the updated data is written to disk."
        self.dump()


