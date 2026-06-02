"Classes used to export a GAMS 3 Object."

import shutil
from enum import Enum
from pathlib import Path
from typing import ClassVar, Final

import requests
from lxml import etree as ET

import json

from gamspreprocessor.gams3.datastream import DataStream
from gamspreprocessor.gams3.foxml import AuditTrail, FoxmlObject, ObjectProperties

# pylint: disable=c-extension-no-member

# name of the subdirectory where datastreams with an id contained in SPECIAL_DS_IDS are stored
SPECIAL_DIR_NAME: Final[str] = ".special_datastreams"


class ExportError(Exception):
    "Custom exception for errors during export of a GAMS 3 object."


class ExportStatus(Enum):
    "Status of the export process for a GAMS 3 object."

    PENDING = 0
    EXPORTED = 1
    REPLACED = 2
    IGNORED = 3
    ERROR = 4


class Gams3Object:
    "A Fedora 3 object."

    NAMESPACES: ClassVar[dict[str, str]] = {
        "fedora": "http://www.fedora.info/definitions/1/0/access/"
    }

    def __init__(self, pid: str, base_url: str):
        "Initialize the object with its PID and base URL."
        self.pid: str = pid
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        self.base_url:str = base_url
        self.object_url:str = f"{self.base_url}/objects/{requests.utils.quote(self.pid)}"
        self.object_properties: ObjectProperties | None = None
        self.audit_trail: AuditTrail | None  = None

        self.status = ExportStatus.PENDING
        self.exported_files = []
        self.warnings = []
        self.errors = []

    def get_datastreams(self):
        "Yield all datastreams of the object as DataStream objects."
        url = f"{self.object_url}/datastreams?format=xml"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        tree = ET.fromstring(response.content)
        for datastream in tree.findall(
            "./fedora:datastream", namespaces=self.NAMESPACES
        ):
            ds_url = f"{self.object_url}/datastreams/{datastream.get('dsid')}"
            dsid = datastream.get("dsid")
            label = datastream.get("label")
            mime_type = datastream.get("mimeType")
            yield DataStream(
                url=ds_url, dsid=dsid, pid=self.pid, label=label, mime_type=mime_type
            )
        self._fetch_audit_trail_and_properties()

    def export(
        self,
        output_root: Path,
        overwrite: bool = False,
        strip_prefix: bool = False,
        colon_replacement: str = "%3A",
    ) -> list[Path]:
        """Export this object and its datastreams into an object-specific directory.

        This method raises an Export Error if an error occurs during export.
        The object is aware of its status which can be checked after export:
        the status attribute has the following possible values implement as ExportStatus Enum:

           - ExportStatus.PENDING (initial state),
           - ExportStatus.EXPORTED (export successful),
           - ExportStatus.REPLACED (existing export was replaced),
           - ExportStatus.IGNORED (export skipped due to existing export and overwrite=False),
           - ExportStatus.ERROR (an error occurred during export).

        You might also want to check the warnings and errors attributes of the object after export,
        which contain any warnings or errors that occurred during export.

        Args:
            output_root: Root directory where the object directory will be created.
            overwrite: Whether to overwrite an existing object directory.
                 If an object directory already exists at the target location and `overwrite`
                 is True, it will be deleted and re-exported. If `overwrite` is False,
                 the existing directory is skipped.
            strip_prefix: Whether to strip the "o:" prefix from the PID when naming the subdirectories.
            colon_replacement: String to replace ":" in PIDs when naming subdirectories.

        Returns: None

        Raises:
            ExportError: If an error occurs during export of the object or any of its datastream
        """
        was_cleared = False
        object_dir = output_root / self._get_object_dir_name(
            strip_prefix, colon_replacement
        )
        if object_dir.exists():
            if overwrite is False:
                self.status = ExportStatus.IGNORED
                return
            self._clear_directory(object_dir)
            was_cleared = True

        object_dir.mkdir(parents=True, exist_ok=True)
        try:
            for ds in self.get_datastreams():
                try:
                    exported_file = ds.export(object_dir, special_dirname=SPECIAL_DIR_NAME, strip_prefix=strip_prefix)
                    if exported_file:
                        self.exported_files.append(exported_file)
                except Exception as e:
                    self.warnings.append(
                        f"Error occurred while exporting datastream: {e}"
                    )
                    # reset to initals state to avoid partial exports
                    self._clear_directory(object_dir)
                    raise ExportError(
                        f"Failed to export datastream {ds.dsid} of object {self.pid}: {e}"
                    ) from e
            self._export_audit_trail(object_dir)
            self._export_gams3_properties(object_dir)
            self.status = (
                ExportStatus.REPLACED if was_cleared else ExportStatus.EXPORTED
            )
        except Exception as e:
            self.errors.append(f"Failed to export object {self.pid}: {e}")
            self.status = ExportStatus.ERROR
            raise ExportError(f"Failed to export object {self.pid}: {e}") from e

    def _clear_directory(self, directory: Path):
        "Recursively delete all files and subdirectories in the given directory."
        shutil.rmtree(directory)

    def _get_object_dir_name(self, strip_prefix: bool, colon_replacement: str) -> str:
        """Return a clean object dir name.

        Escapes colons in the PID and optionally strips the prefix (o:, context:, etc).
        """
        if strip_prefix and ":" in self.pid:
            dirname = self.pid.split(":", 1)[1]
        else:
            dirname = self.pid
        return dirname.replace(":", colon_replacement)

    def _get_audit_trail(self):
        """Get the audit trail of the object

        Problem: this method requires API-M and therefore authentication.
        """
        url = f"{self.object_url}/objectXML"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        tree = ET.fromstring(response.content)
        events = []
        for event in tree.findall(
            "./fedora:auditTrail/fedora:event", namespaces=self.NAMESPACES
        ):
            events.append(
                {
                    "date": event.get("date"),
                    "type": event.get("type"),
                    "outcome": event.get("outcome"),
                    "detail": event.get("detail"),
                }
            )
        return events

    def _fetch_audit_trail_and_properties(self):
        """Fetch the audit trail and properties datastreams to make them available for export.

        This is necessary because these datastreams are not included in the list of datastreams
        returned by the API-A endpoint, but they are still needed for export. We fetch them here
        to avoid making additional requests later during export.
        """
        url = f"{self.object_url}/export?format=info:fedora/fedora-system:FOXML-1.1" 
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        foxml_obj = FoxmlObject(response.content)
        self.audit_trail = foxml_obj.audit_trail
        self.object_properties = foxml_obj.properties

    def _export_audit_trail(self, object_dir: Path):
        """Export the audit trail of the object to a file in the given object directory.

        This datastream is put in the special directory.
        """
        target_file = object_dir / SPECIAL_DIR_NAME / "audit_trail.json"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with target_file.open("w", encoding="utf-8") as f:
            json.dump(self.audit_trail.as_dict(), f, indent=2, ensure_ascii=False)

    
    
    def _export_gams3_properties(self, object_dir: Path):
        """Export the GAMS 3 properties of the object to a file in the given object directory.
        
        This datastream is put in the special directory.
        """
        target_file = object_dir / SPECIAL_DIR_NAME / "gams3_properties.json"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with target_file.open("w", encoding="utf-8") as f:
            json.dump(self.object_properties.as_dict(), f, indent=2, ensure_ascii=False)