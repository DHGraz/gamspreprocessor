from types import SimpleNamespace

import pytest

from gamspreprocessor.gams3.object import ExportError, ExportStatus, Gams3Object


REQUEST_TIMEOUT = 30
SUCCESS_STATUS = 200
EXPECTED_EXPORT_COUNT = 2


def _set_fake_metadata(obj):
    obj.audit_trail = SimpleNamespace(as_dict=lambda: [{"id": "AUDREC1"}])
    obj.object_properties = SimpleNamespace(
        as_dict=lambda: {
            "state": "A",
            "label": "Example object",
            "owner_id": "owner",
            "created_date": "2017-02-15T23:04:07Z",
            "last_modified_date": "2017-02-15T23:04:51Z",
        }
    )



def test_gams3_object_initialization():
    "Test the initialization of a Gams3Object."
    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora/")
    assert obj.pid == "o:foo.testobject1"
    assert (
        obj.base_url == "https://example.com/fedora"
    )  # trailing slash should be removed
    assert obj.object_url == "https://example.com/fedora/objects/o%3Afoo.testobject1"


def test_get_datastreams(lazy_shared_datadir, monkeypatch, make_fake_response):
    def fake_get(url, timeout):
        assert timeout == REQUEST_TIMEOUT

        if url.endswith("/datastreams?format=xml"):
            xml = (lazy_shared_datadir / "datastreams.xml").read_bytes()
            return make_fake_response(xml, SUCCESS_STATUS)

        assert url.endswith(
            "/export?format=info:fedora/fedora-system:FOXML-1.1"
        )
        xml = (lazy_shared_datadir / "foxml.xml").read_bytes()
        return make_fake_response(xml, SUCCESS_STATUS)

    base_url = "https://example.com/fedora/"
    monkeypatch.setattr("gamspreprocessor.gams3.object.requests.get", fake_get)

    gams3_object = Gams3Object(
        pid="o:foo.testobject1", base_url=base_url
    )

    datastreams = list(gams3_object.get_datastreams())
    assert len(datastreams) > 0
    for ds in datastreams:
        assert ds.url.startswith(base_url + "objects/o%3Afoo.testobject1/datastreams/")
        assert ds.dsid != ""
        assert ds.label != ""
        assert ds.mime_type != ""
    assert gams3_object.audit_trail is not None
    assert gams3_object.object_properties is not None
    assert len(gams3_object.audit_trail.as_dict()) > 0


def test_get_audit_trail(monkeypatch, make_fake_response):
    populated_xml = b"""
                <fedora:object xmlns:fedora="http://www.fedora.info/definitions/1/0/access/">
          <fedora:auditTrail>
            <fedora:event date="2024-01-01T00:00:00Z" type="ingest" outcome="success" detail="created" />
          </fedora:auditTrail>
        </fedora:object>
    """
    empty_xml = b"""
                <fedora:object xmlns:fedora="http://www.fedora.info/definitions/1/0/access/" />
    """
    responses = [
        make_fake_response(populated_xml, 200),
        make_fake_response(empty_xml, 200),
    ]

    def fake_get(url, timeout):
        assert timeout == REQUEST_TIMEOUT
        assert url.endswith("/objectXML")
        return responses.pop(0)

    monkeypatch.setattr("gamspreprocessor.gams3.object.requests.get", fake_get)

    populated = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")
    empty = Gams3Object(pid="o:foo.testobject2", base_url="https://example.com/fedora")

    assert getattr(populated, "_get_audit_trail")() == [
        {
            "date": "2024-01-01T00:00:00Z",
            "type": "ingest",
            "outcome": "success",
            "detail": "created",
        }
    ]
    assert getattr(empty, "_get_audit_trail")() == []
    


def test_export_creates_object_directory_and_exports_datastreams(tmp_path, monkeypatch):
    "Test that export creates an object-specific directory and exports datastreams into it."
    exported = []

    class FakeDatastream:
        def export(self, output_dir, special_dirname, strip_prefix=True):
            assert special_dirname == ".special_datastreams"
            assert strip_prefix is False
            exported.append(output_dir)

    def fake_get_datastreams(_self):
        return [FakeDatastream(), FakeDatastream()]

    monkeypatch.setattr(
        "gamspreprocessor.gams3.object.Gams3Object.get_datastreams",
        fake_get_datastreams,
    )

    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")
    _set_fake_metadata(obj)
    obj.export(tmp_path)

    object_dir = tmp_path / "o%3Afoo.testobject1"
    assert object_dir.exists()
    assert len(exported) == EXPECTED_EXPORT_COUNT
    assert exported == [object_dir, object_dir]
    assert (object_dir / ".special_datastreams" / "audit_trail.json").exists()
    assert (object_dir / ".special_datastreams" / "gams3_properties.json").exists()
    assert obj.status == ExportStatus.EXPORTED


def test_export_collects_exported_files_and_sets_exported_status(tmp_path, monkeypatch):
    "Test that export stores returned datastream paths and marks the object as exported." 
    exported_paths = []

    class FakeDatastream:
        def __init__(self, name):
            self.name = name

        def export(self, output_dir, special_dirname, strip_prefix=True):
            assert special_dirname == ".special_datastreams"
            exported_path = output_dir / self.name
            exported_path.write_text("content", encoding="utf-8")
            exported_paths.append((output_dir, strip_prefix, exported_path))
            return exported_path

    monkeypatch.setattr(
        "gamspreprocessor.gams3.object.Gams3Object.get_datastreams",
        lambda self: [FakeDatastream("DC.xml"), FakeDatastream("TEI_SOURCE.xml")],
    )

    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")
    _set_fake_metadata(obj)

    obj.export(tmp_path, strip_prefix=True)

    object_dir = tmp_path / "foo.testobject1"
    assert object_dir.exists()
    assert [item[0] for item in exported_paths] == [object_dir, object_dir]
    assert [item[1] for item in exported_paths] == [True, True]
    assert obj.exported_files == [object_dir / "DC.xml", object_dir / "TEI_SOURCE.xml"]
    assert obj.status == ExportStatus.EXPORTED


def test_export_ignores_if_object_dir_exists_and_overwrite_false(tmp_path):
    "Test that export marks the object as ignored if the target directory already exists."
    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")
    object_dir = tmp_path / "o%3Afoo.testobject1"
    object_dir.mkdir(parents=True)

    obj.export(tmp_path, overwrite=False)

    assert obj.status == ExportStatus.IGNORED


def test_export_overwrite_cleans_existing_directory(tmp_path, monkeypatch):
    "Test that export with overwrite=True cleans the existing object directory before exporting."
    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")
    object_dir = tmp_path / "o%3Afoo.testobject1"
    nested = object_dir / "nested"
    nested.mkdir(parents=True)
    stale_file = nested / "old.txt"
    stale_file.write_text("stale")

    monkeypatch.setattr(
        "gamspreprocessor.gams3.object.Gams3Object.get_datastreams",
        lambda self: [],
    )

    _set_fake_metadata(obj)
    obj.export(tmp_path, overwrite=True)

    assert object_dir.exists()
    assert not stale_file.exists()
    assert (object_dir / ".special_datastreams").exists()
    assert obj.status == ExportStatus.REPLACED


def test_export_raises_export_error_for_datastream_failure(tmp_path, monkeypatch):
    "Test that datastream export errors are wrapped, warnings and errors are collected, and partial exports are removed." 

    class FakeDatastream:
        def __init__(self, dsid, should_fail=False):
            self.dsid = dsid
            self.should_fail = should_fail

        def export(self, output_dir, special_dirname, strip_prefix=True):
            assert special_dirname == ".special_datastreams"
            assert strip_prefix is False
            if self.should_fail:
                raise RuntimeError("boom")
            exported_path = output_dir / f"{self.dsid}.xml"
            exported_path.write_text("content", encoding="utf-8")
            return exported_path

    monkeypatch.setattr(
        "gamspreprocessor.gams3.object.Gams3Object.get_datastreams",
        lambda self: [FakeDatastream("DC"), FakeDatastream("TEI_SOURCE", should_fail=True)],
    )

    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")
    _set_fake_metadata(obj)

    with pytest.raises(ExportError):
        obj.export(tmp_path)

    object_dir = tmp_path / "o%3Afoo.testobject1"
    assert not object_dir.exists()
    assert obj.status == ExportStatus.ERROR
    assert obj.warnings == ["Error occurred while exporting datastream: boom"]
    assert len(obj.errors) == 1
    assert "Failed to export object o:foo.testobject1:" in obj.errors[0]


def test_export_sets_error_status_when_get_datastreams_fails(tmp_path, monkeypatch):
    "Test that unexpected iteration errors are stored on the object and converted to ExportError." 
    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")

    def fake_get_datastreams(_self):
        raise RuntimeError("listing failed")

    monkeypatch.setattr(
        "gamspreprocessor.gams3.object.Gams3Object.get_datastreams",
        fake_get_datastreams,
    )

    with pytest.raises(ExportError):
        obj.export(tmp_path)

    assert obj.status == ExportStatus.ERROR
    assert obj.warnings == []
    assert len(obj.errors) == 1
    assert obj.errors[0] == "Failed to export object o:foo.testobject1: listing failed"


def test_export_uses_custom_colon_replacement(tmp_path, monkeypatch):
    "Test that export uses the configured colon replacement in the object directory name." 
    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")

    monkeypatch.setattr(
        "gamspreprocessor.gams3.object.Gams3Object.get_datastreams",
        lambda self: [],
    )

    _set_fake_metadata(obj)
    obj.export(tmp_path, colon_replacement="_")

    assert (tmp_path / "o_foo.testobject1").exists()


def test_export_strip_prefix(tmp_path, monkeypatch):
    "Test that export with strip_prefix=True creates an object directory without the type prefix."
    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")

    monkeypatch.setattr(
        "gamspreprocessor.gams3.object.Gams3Object.get_datastreams",
        lambda self: [],
    )

    _set_fake_metadata(obj)
    obj.export(tmp_path, strip_prefix=True)

    object_dir = tmp_path / "foo.testobject1"
    assert object_dir.exists()