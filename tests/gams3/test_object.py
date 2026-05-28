import pytest
from gamspreprocessor.gams3.object import Gams3Object



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
        assert timeout == 30

        assert url.endswith("/datastreams?format=xml")
        xml = (lazy_shared_datadir / "datastreams.xml").read_bytes()
        return make_fake_response(xml, 200)

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


def test_export_creates_object_directory_and_exports_datastreams(tmp_path, monkeypatch):
    "Test that export creates an object-specific directory and exports datastreams into it."
    exported = []

    class FakeDatastream:
        def export(self, output_dir, strip_prefix=True):
            exported.append(output_dir)

    def fake_get_datastreams(_self):
        return [FakeDatastream(), FakeDatastream()]

    monkeypatch.setattr(
        "gamspreprocessor.gams3.object.Gams3Object.get_datastreams",
        fake_get_datastreams,
    )

    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")
    obj.export(tmp_path)

    object_dir = tmp_path / "o%3Afoo.testobject1"
    assert object_dir.exists()
    assert len(exported) == 2
    assert exported == [object_dir, object_dir]


def test_export_raises_if_object_dir_exists_and_overwrite_false(tmp_path):
    "Test that export raises FileExistsError if the target object directory already exists and overwrite is False."
    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")
    object_dir = tmp_path / "o%3Afoo.testobject1"
    object_dir.mkdir(parents=True)

    with pytest.raises(FileExistsError):
        obj.export(tmp_path, overwrite=False)


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

    with pytest.warns(UserWarning):
        obj.export(tmp_path, overwrite=True)

    assert object_dir.exists()
    assert not stale_file.exists()
    assert list(object_dir.iterdir()) == []


def test_export_strip_prefix(tmp_path, monkeypatch):
    "Test that export with strip_prefix=True creates an object directory without the type prefix."
    obj = Gams3Object(pid="o:foo.testobject1", base_url="https://example.com/fedora")

    monkeypatch.setattr(
        "gamspreprocessor.gams3.object.Gams3Object.get_datastreams",
        lambda self: [],
    )

    obj.export(tmp_path, strip_prefix=True)

    object_dir = tmp_path / "foo.testobject1"
    assert object_dir.exists()