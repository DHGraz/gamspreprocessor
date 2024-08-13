"""Keep track of files that have been processed between runs."""

import json
import os
from pathlib import Path
from typing import Dict


class BookKeeper:
    """A class to keep track of files that have been processed.

    As the project dir also contains referenced data streams (images, etc.),
    we need to keep track of which files have been processed and which have not.
    It important for the incremental processing of the project that the user
    can find out which files have not been processed yet.
    """

    # the default filename.
    FILENAME = ".bookkeeping.json"

    # We use pathlib.Path for public interfaces, but strings for paths internally
    # because json does not support Path objects and is does not really make sense
    # to cast values from an to Path objects.
    def __init__(self, project_dir: Path):
        "Initialize the BookKeeper object."

        self.project_dir = project_dir
        self.datafile = project_dir / self.FILENAME
        self._data: Dict[str, str] = {}

        ## read stored data from disk (if it exists)
        self._load_data()

        ## update data with new files
        #self._update_files()

    def dump(self) -> None:
        "Write data to disk"
        with open('/tmp/x.log', 'w') as f:
            for file in self._data:
                f.write(f"{file}, {type(file)}\n")
        #with open(self.datafile, "w", encoding="utf-8") as f:
        #    json.dump(self._data, f, ensure_ascii=False)

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
        if self.datafile.exists():
            with open(self.datafile, encoding="utf-8") as f:
                self._data = json.load(f)


    #def _update_files(self):
    def update(self):
        """Merge already registered files with newly colleced files.

        Also remove files which have been deleted since last run.
        """
        all_files = set()
        for root, _, files in os.walk(str(self.project_dir)):
            for file in files:
                # skip the bookkeeping file and log files
                if file == self.datafile.name or file.endswith(".log"):
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


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        "Make sure the updated data is written to disk."
        self.dump()
