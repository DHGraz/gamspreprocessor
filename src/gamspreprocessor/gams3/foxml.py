"""
Classes which represent some aspects of an FOXML document.


We use extract relevant information from the FOXML representation of
a Fedora 3 object, which is obtained by requesting the datastream
with id "OBJECT_XML" from the object.
"""

from dataclasses import InitVar, dataclass, field
from datetime import datetime
import re

from lxml import etree as ET

# pylint: disable=c-extension-no-member

NAMESPACES: dict[str, str] = {
    "foxml": "info:fedora/fedora-system:def/foxml#",
    "xlink": "http://www.w3.org/1999/xlink",
    "audit": "info:fedora/fedora-system:def/audit#",
}


class FOXMLParseWarning(UserWarning):
    "A warning for issues during parsing of FOXML content."

def reformat_timestamp(iso_string):
    """Create a standard ISO format without sub seconds.
    """
    dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    iso_out = dt.isoformat(timespec='seconds', sep='T')
    if iso_out.endswith('+00:00'):
        iso_out = iso_out[:-6] + 'Z'
    return iso_out

@dataclass
class ObjectProperties:
    "The object properties of a Fedora 3 object, as extracted from the FOXML."

    object_properties_element: InitVar[ET.Element] = None

    state: str = ""
    label: str = ""
    owner_id: str = ""
    created_date: str = ""
    last_modified_date: str = ""

    def __post_init__(self, obj_properties_element: ET.Element):
        "Initialize the object properties from the given XML element."

        self.name = obj_properties_element.get("NAME", "")

        for prop in obj_properties_element.findall(
            "./foxml:property", namespaces=NAMESPACES
        ):
            name = prop.get("NAME")
            value = prop.get("VALUE")

            if name == "info:fedora/fedora-system:def/model#state":
                self.state = value
            elif name == "info:fedora/fedora-system:def/model#label":
                self.label = value
            elif name == "info:fedora/fedora-system:def/model#ownerId":
                self.owner_id = value
            elif name == "info:fedora/fedora-system:def/model#createdDate":
                self.created_date = value
            elif name == "info:fedora/fedora-system:def/view#lastModifiedDate":
                self.last_modified_date = value

    def as_dict(self) -> dict[str, str]:
        "Return the object properties as a dictionary."

        return {
            "state": self.state,
            "label": self.label,
            "owner_id": self.owner_id,
            "created_date": reformat_timestamp(self.created_date),
            "last_modified_date": reformat_timestamp(self.last_modified_date),
        }

@dataclass
class AuditRecord:
    "A single record in the audit trail of a Fedora 3 object."

    object_pid: str
    # this is the audit:record element passed to init.
    audit_record_element: InitVar[ET.Element] = None

    id: str = ""
    process: str = ""
    action: str = ""
    component_id: str = ""
    responsibility: str = ""
    date: str = ""
    justification: str = ""

    def __post_init__(self, audit_record_element: ET.Element):
        "Initialize the audit record from the given XML element."
        self.id = (
            audit_record_element.get("ID") if audit_record_element is not None else ""
        )
        for child in audit_record_element:
            if child.tag == f"{{{NAMESPACES['audit']}}}process":
                self.process = child.get("type") or ""
            elif child.tag == f"{{{NAMESPACES['audit']}}}action":
                self.action = child.text or ""
            elif child.tag == f"{{{NAMESPACES['audit']}}}componentID":
                self.component_id = child.text or ""
            elif child.tag == f"{{{NAMESPACES['audit']}}}responsibility":
                self.responsibility = child.text or ""
            elif child.tag == f"{{{NAMESPACES['audit']}}}date":
                self.date = child.text or ""
            elif child.tag == f"{{{NAMESPACES['audit']}}}justification":
                justification = child.text or ""
                self.justification = re.sub(r"\s+", " ", justification)

    def as_dict(self) -> dict[str, str]:
        """Return the audit record as a dictionary.

        The format is based on the invenio rdm record format for audit records.
        """
        actions = {
            "addObject": "create",
            "modifyObject": "update",
            "purgeObject": "delete",
            "addDatastream": "create",
            "modifyDatastreamByValue": "update",
            "modifyDatastreamByReference": "update",
            "purgeDatastream": "delete",
            "addRelationship": "update",
            "purgeRelationship": "delete",
            "ingest": "create",
        }
        return  {
            "id": self.id,
            "record_id": self.object_pid,
            "user_id": self.responsibility,
            "timestamp": reformat_timestamp(self.date),
            "action": actions.get(self.action, f"???{self.action}???"),
            "changes": {
                "title": self.justification or "unknown change",
                "description": ""
            }
        }
       

@dataclass
class AuditTrail:
    "The audit trail of a Fedora 3 object, as extracted from the FOXML."

    pid: str 
    # this is the audit:auditTrail element passed to init.
    audit_trail_element: InitVar[ET.Element] = None

    records: list[AuditRecord] = field(init=False, default_factory=list)

    def __post_init__(self, audit_trail_element: ET.Element):
        "Initialize the audit trail from the given XML element."

        for record in audit_trail_element.findall(
            "./audit:record", namespaces=NAMESPACES
        ):
            self.records.append(AuditRecord(self.pid, record))

    def as_dict(self) -> dict[str, list[dict[str, str]]]:
        """Return the audit trail as a dictionary.

        The format is that of invenio rdm records.
        """
        return {
            "pid": self.pid,
            "records": [record.as_dict() for record in self.records]
        }

@dataclass
class FoxmlObject:
    """A Fedora 3 object represented as FOXML XML tree.

    This class contains only metadata extracted from the FOXML,
    which is relevant for the export process.
    """

    xml_content: InitVar[bytes]

    pid: str = ""
    properties: ObjectProperties = None
    audit_trail: AuditTrail = None

    def __post_init__(self, xml_content: bytes):
        "Initialize the object from the given FOXML content."
        tree = ET.fromstring(xml_content)
        self.pid = tree.get("PID")
        self.object_properties = None
        self.audit_trail = None

        obj_properties_element = tree.find(
            "./foxml:objectProperties", namespaces=NAMESPACES
        )
        if obj_properties_element is not None:
            self.properties = ObjectProperties(obj_properties_element)
        else:
            raise FOXMLParseWarning("No object properties found in FOXML content")
        audit_trail_element = tree.find(
            './foxml:datastream[@ID="AUDIT"]/foxml:datastreamVersion/foxml:xmlContent/audit:auditTrail',
            namespaces=NAMESPACES,
        )
        if audit_trail_element is not None:
            self.audit_trail = AuditTrail(self.pid, audit_trail_element)
        else:
            raise FOXMLParseWarning("No audit trail found in FOXML content")
