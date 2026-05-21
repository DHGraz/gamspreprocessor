from pathlib import Path
from typing import ClassVar
import warnings

import requests

from lxml import etree as ET

from gamspreprocessor.gams3.datastream import DataStream


# pylint: disable=c-extension-no-member

class Gams3Object:
    "A Fedora 3 object."

    NAMESPACES: ClassVar[dict[str, str]] = {
        "fedora": "http://www.fedora.info/definitions/1/0/access/"
    }

    def __init__(self, pid: str, base_url: str):
        "Initialize the object with its PID and base URL."
        self.pid = pid
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        self.base_url = base_url
        self.object_url = f"{self.base_url}/objects/{requests.utils.quote(self.pid)}"

    def get_datastreams(self):
        "Yield all datastreams of the object as DataStream objects."
        url = f"{self.object_url}/datastreams?format=xml"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        tree = ET.fromstring(response.content)
        for datastream in tree.findall("./fedora:datastream", namespaces=self.NAMESPACES):
            ds_url = f"{self.object_url}/datastreams/{datastream.get('dsid')}"
            dsid = datastream.get("dsid")
            label = datastream.get("label")
            mime_type = datastream.get("mimeType")
            yield DataStream(url=ds_url, dsid=dsid, pid=self.pid, label=label, mime_type=mime_type)

    def export(self, output_root: Path, overwrite: bool = False) -> list[Path]:
        """Export this object and its datastreams into an object-specific directory.

        Args:
            output_root: Root directory where the object directory will be created.
            overwrite: Whether to overwrite an existing object directory.

        Returns:
            Paths of all exported datastream files.

        Raises:
            FileExistsError: If the target object directory exists and `overwrite` is False.
        """
        exported_ds_files = []
        object_dir = output_root / self.pid.replace(":", "%3A")
        if object_dir.exists():
            if not overwrite:
                raise FileExistsError(f"Output directory for PID {self.pid} already exists: {object_dir}")
            else:
                warnings.warn(f"Overwriting existing directory for PID {self.pid}: {object_dir}")
                self._clean_directory(object_dir)
        object_dir.mkdir(parents=True, exist_ok=True)
        for ds in self.get_datastreams():
            exported_file = ds.export(object_dir)
            if exported_file:
                exported_ds_files.append(exported_file)
        return exported_ds_files

    def _clean_directory(self, directory: Path):
        "Recursively delete all files and subdirectories in the given directory."
        for item in directory.iterdir():
            if item.is_file():
                item.unlink()
            else:
                self._clean_directory(item)
                item.rmdir()