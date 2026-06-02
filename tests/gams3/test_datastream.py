"Tests the for datastreams module of the gams3 package."

from pathlib import Path
from types import SimpleNamespace

from gamslib.formatdetect.formatinfo import SubType

from gamspreprocessor.gams3.datastream import DataStream
from gamspreprocessor.gams3.object import SPECIAL_DIR_NAME
REQUEST_TIMEOUT = 30


def _mock_datastream_response(monkeypatch, make_fake_response, payload: bytes):
    def fake_get(_url, timeout):
        assert timeout == REQUEST_TIMEOUT
        return make_fake_response(payload, 200)

    monkeypatch.setattr("gamspreprocessor.gams3.datastream.requests.get", fake_get)


def test_datastream_init():
    "Test the initialization of a DataStream."
    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/METADATA",
        dsid="METADATA",
        pid="o:foo.testobject1",
        label="Metadata for test object 1",
        mime_type="text/xml",
    )
    assert (
        ds.url
        == "https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/METADATA"
    )
    assert ds.dsid == "METADATA"
    assert ds.pid == "o:foo.testobject1"
    assert ds.label == "Metadata for test object 1"
    assert ds.mime_type == "text/xml"


def test_datastream_content(monkeypatch, lazy_shared_datadir, make_fake_response):
    "Test the content property of a DataStream."

    def fake_get(url, timeout):
        assert timeout == REQUEST_TIMEOUT
        assert (
            url
            == "https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/TEI_SOURCE/content"
        )
        xml = (lazy_shared_datadir / "tei_source.xml").read_bytes()
        return make_fake_response(xml, 200)

    monkeypatch.setattr("gamspreprocessor.gams3.datastream.requests.get", fake_get)

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/TEI_SOURCE",
        dsid="TEI_SOURCE",
        pid="o:foo.testobject1",
        label="TEI Source for test object 1",
        mime_type="text/xml",
    )

    content = ds.content
    assert content == (lazy_shared_datadir / "tei_source.xml").read_bytes()


def test_datastream_content_is_cached(monkeypatch, make_fake_response):
    calls = []

    def fake_get(url, timeout):
        calls.append((url, timeout))
        return make_fake_response(b"cached-content", 200)

    monkeypatch.setattr("gamspreprocessor.gams3.datastream.requests.get", fake_get)

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/TEI_SOURCE",
        dsid="TEI_SOURCE",
        pid="o:foo.testobject1",
        label="TEI Source",
        mime_type="text/xml",
    )

    assert ds.content == b"cached-content"
    assert ds.content == b"cached-content"
    assert len(calls) == 1


def test_datastream_content_returns_empty_bytes_when_cache_is_none():
    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/TEI_SOURCE",
        dsid="TEI_SOURCE",
        pid="o:foo.testobject1",
        label="TEI Source",
        mime_type="text/xml",
    )
    object.__setattr__(ds, "_content", None)

    assert ds.content == b""


def test_datastream_content_returns_empty_bytes_on_http_error(monkeypatch):
    calls = []

    class FakeResponse:
        status_code = 500
        content = b"server error"

    def fake_get(url, timeout):
        calls.append((url, timeout))
        assert timeout == REQUEST_TIMEOUT
        return FakeResponse()

    monkeypatch.setattr("gamspreprocessor.gams3.datastream.requests.get", fake_get)

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/TEI_SOURCE",
        dsid="TEI_SOURCE",
        pid="o:foo.testobject1",
        label="TEI Source",
        mime_type="text/xml",
    )

    assert ds.content is None
    assert ds.content == b""
    assert len(calls) == 1


def test_export_rewrites_references_for_teip5(monkeypatch, tmp_path, make_fake_response):
    captured = {}

    def fake_detect_format(_path):
        return SimpleNamespace(subtype=SubType.TEIP5)

    class FakeObjectSource:
        def __init__(self, ds_file, mode, strip_prefix, strip_extension):
            captured["init"] = (ds_file, mode, strip_prefix, strip_extension)

        def rewrite_references(self):
            captured["rewrite"] = True

        def save(self, directory):
            captured["save"] = directory

    monkeypatch.setattr("gamspreprocessor.gams3.datastream.detect_format", fake_detect_format)
    monkeypatch.setattr("gamspreprocessor.gams3.datastream.make_object_source", FakeObjectSource)
    monkeypatch.setattr(
        "gamspreprocessor.gams3.datastream.requests.get",
        lambda _url, timeout: make_fake_response(b"<TEI/>", 200),
    )

    ds_file = tmp_path / "TEI_SOURCE.xml"
    ds_file.write_text("<TEI/>", encoding="utf-8")

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/TEI_SOURCE",
        dsid="TEI_SOURCE",
        pid="o:foo.testobject1",
        label="TEI Source",
        mime_type="text/xml",
    )

    result = ds.export(tmp_path, SPECIAL_DIR_NAME, strip_prefix=True)

    assert captured["init"] == (ds_file, "auto", True, False)
    assert captured["rewrite"] is True
    assert captured["save"] == ds_file.parent
    assert result == ds_file


def test_export_ignores_non_rewriteable_formats(monkeypatch, tmp_path, make_fake_response):
    called = []

    def fake_detect_format(_path):
        return None

    monkeypatch.setattr("gamspreprocessor.gams3.datastream.detect_format", fake_detect_format)
    monkeypatch.setattr(
        "gamspreprocessor.gams3.datastream.requests.get",
        lambda _url, timeout: make_fake_response(b"<root/>", 200),
    )
    monkeypatch.setattr(
        "gamspreprocessor.gams3.datastream.make_object_source",
        lambda *args, **kwargs: called.append((args, kwargs)),
    )

    ds_file = tmp_path / "TEXT.xml"
    ds_file.write_text("<root/>", encoding="utf-8")

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/TEXT",
        dsid="TEXT",
        pid="o:foo.testobject1",
        label="Text",
        mime_type="text/xml",
    )

    result = ds.export(tmp_path, SPECIAL_DIR_NAME)

    assert called == []
    assert result == ds_file


def test_datastream_str():
    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/TEXT",
        dsid="TEXT",
        pid="o:foo.testobject1",
        label="Text",
        mime_type="text/xml",
    )

    assert str(ds) == "DataStream(dsid=TEXT)"


def test_is_empty_detects_empty_payload(monkeypatch, make_fake_response):
    _mock_datastream_response(monkeypatch, make_fake_response, b"")

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/EMPTY",
        dsid="EMPTY",
        pid="o:foo.testobject1",
        label="Empty",
        mime_type="application/octet-stream",
    )

    assert ds.is_empty() is True


def test_is_empty_detects_default_access_marker(monkeypatch, make_fake_response):
    _mock_datastream_response(
        monkeypatch, make_fake_response, b"prefix [DefaulAccess] suffix"
    )

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/METADATA",
        dsid="METADATA",
        pid="o:foo.testobject1",
        label="Metadata",
        mime_type="text/xml",
    )

    assert ds.is_empty() is True


def test_is_empty_detects_generated_text_marker(monkeypatch, make_fake_response):
    _mock_datastream_response(
        monkeypatch,
        make_fake_response,
        b"This was automatically generated by GAMS for testing",
    )

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/INFO",
        dsid="INFO",
        pid="o:foo.testobject1",
        label="Info",
        mime_type="text/plain",
    )

    assert ds.is_empty() is True


def test_is_empty_returns_false_for_real_content(monkeypatch, make_fake_response):
    _mock_datastream_response(
        monkeypatch,
        make_fake_response,
        b"<TEI><text>actual content</text></TEI>",
    )

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/TEI_SOURCE",
        dsid="TEI_SOURCE",
        pid="o:foo.testobject1",
        label="TEI",
        mime_type="text/xml",
    )

    assert ds.is_empty() is False


def test_export_dc_uses_xml_filename(tmp_path: Path, monkeypatch, make_fake_response):
    _mock_datastream_response(monkeypatch, make_fake_response, b"<dc />")

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/DC",
        dsid="DC",
        pid="o:foo.testobject1",
        label="Dublin Core",
        mime_type="text/xml",
    )

    result = ds.export(tmp_path, SPECIAL_DIR_NAME)

    assert result is not None
    assert result.name == "DC.xml"


def test_export_warns_on_unknown_mime_type(
    recwarn, tmp_path: Path, monkeypatch, make_fake_response
):
    _mock_datastream_response(monkeypatch, make_fake_response, b"custom")

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/CUSTOM",
        dsid="CUSTOM",
        pid="o:foo.testobject1",
        label="Custom",
        mime_type="application/x-unknown-type",
    )

    result = ds.export(tmp_path, SPECIAL_DIR_NAME)

    assert result is not None
    assert result.name == "CUSTOM"
    assert len(recwarn) == 1


def test_export_returns_none_for_ignored_datastream(
    tmp_path: Path, monkeypatch, make_fake_response
):
    _mock_datastream_response(monkeypatch, make_fake_response, b"ignored")

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/PID",
        dsid="PID",
        pid="o:foo.testobject1",
        label="Persistent Identifier",
        mime_type="text/plain",
    )

    result = ds.export(tmp_path, SPECIAL_DIR_NAME)

    assert result is None


def test_export_writes_special_datastream_to_subdirectory(
    tmp_path: Path, monkeypatch, make_fake_response
):
    _mock_datastream_response(monkeypatch, make_fake_response, b"<xml>metadata</xml>")

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/METADATA",
        dsid="METADATA",
        pid="o:foo.testobject1",
        label="Metadata",
        mime_type="text/xml",
    )

    result = ds.export(tmp_path, SPECIAL_DIR_NAME)

    assert result is not None
    assert result.parent.name == SPECIAL_DIR_NAME
    assert result.name == "METADATA.xml"
    assert result.read_bytes() == b"<xml>metadata</xml>"


def test_export_writes_regular_datastream_to_object_directory(
    tmp_path: Path, monkeypatch, make_fake_response
):
    _mock_datastream_response(monkeypatch, make_fake_response, b"<TEI/>")

    ds = DataStream(
        url="https://example.com/fedora/objects/o%3Afoo.testobject1/datastreams/TEI_SOURCE",
        dsid="TEI_SOURCE",
        pid="o:foo.testobject1",
        label="TEI",
        mime_type="text/xml",
    )

    result = ds.export(tmp_path, SPECIAL_DIR_NAME)

    assert result is not None
    assert result.parent == tmp_path
    assert result.name == "TEI_SOURCE.xml"
    assert result.read_bytes() == b"<TEI/>"
