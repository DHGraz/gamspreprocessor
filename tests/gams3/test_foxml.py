from gamspreprocessor.gams3.foxml import FoxmlObject


def test_foxml_init(lazy_shared_datadir):
    "Test that FoxmlObject can be initialized with a simple FOXML XML tree."
    xml_content = (lazy_shared_datadir / "foxml.xml").read_bytes()
    obj = FoxmlObject(xml_content)
    assert obj.pid == "o:km.8586"


    # test the ObjectProperties subclass initialization
    assert obj.properties.state == "Active"
    assert obj.properties.label == "LIDO Object"
    assert obj.properties.owner_id == "km"
    assert obj.properties.created_date == "2017-02-15T23:04:07.397Z"
    assert obj.properties.last_modified_date == "2023-03-02T19:30:54.981Z"

    # Test the AuditTrail Subclass initialization
    at_records = obj.audit_trail.records
    assert len(at_records) == 19

    # Test the AuditRecord initialization for the first record
    assert at_records[0].id == "AUDREC1"
    #assert at_records[0].process == "Fedora API-M"
    assert at_records[0].action == "ingest"
    assert at_records[0].component_id == ""
    assert at_records[0].responsibility == "yoda"
    assert at_records[0].date == "2017-02-15T23:04:07.397Z"
    assert at_records[0].justification == "Cloned from template 'cirilo:LIDO.km' by user 'yoda'"    


def test_objectproperties_as_dict(lazy_shared_datadir):
    "Test that ObjectProperties can be converted to a dictionary with the expected keys and values."
    xml_content = (lazy_shared_datadir / "foxml.xml").read_bytes()
    obj = FoxmlObject(xml_content)
    properties_dict = obj.properties.as_dict()

    assert properties_dict == {
        "state": "Active",
        "label": "LIDO Object",
        "owner_id": "km",
        "created_date": "2017-02-15T23:04:07Z",
        "last_modified_date": "2023-03-02T19:30:54Z",
    }


def test_auditrecord_as_dict(lazy_shared_datadir):
    "Test that an AuditRecord can be converted to a dictionary with the expected keys and values."
    xml_content = (lazy_shared_datadir / "foxml.xml").read_bytes()
    obj = FoxmlObject(xml_content)
    audit_record = obj.audit_trail.records[0]
    record_dict = audit_record.as_dict()

    expected_dict = {
        "id": "AUDREC1",
        "record_id": "o:km.8586", 
        "action": "create",
        "user_id": "yoda",
        "timestamp": "2017-02-15T23:04:07Z",
        "changes": {
             "title": "Cloned from template 'cirilo:LIDO.km' by user 'yoda'", 
             "description": ""
             }
    }
    assert record_dict == expected_dict


def test_audittrail_as_dict(lazy_shared_datadir):
    "Test that an AuditTrail can be converted to a list of dictionaries with the expected keys and values."
    xml_content = (lazy_shared_datadir / "foxml.xml").read_bytes()
    obj = FoxmlObject(xml_content)
    audit_trail_dict = obj.audit_trail.as_dict()
    assert audit_trail_dict["pid"] == "o:km.8586"
    audit_trail_dicts = audit_trail_dict["records"]
    assert len(audit_trail_dicts) == 19

    expected_record_0 = {
        "id": "AUDREC1",
        "record_id": "o:km.8586", 
        "action": "create",
        "user_id": "yoda",
        "timestamp": "2017-02-15T23:04:07Z",
        "changes": {
             "title": "Cloned from template 'cirilo:LIDO.km' by user 'yoda'", 
             "description": ""
             }
        }

    assert audit_trail_dicts[0] == expected_record_0