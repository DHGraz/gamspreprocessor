
import pytest

from gamspreprocessor.gams3.apiquery import Gams3Query
from gamspreprocessor.gams3.object import Gams3Object

REQUEST_TIMEOUT = 30
EXPECTED_PAGE_CALLS = 3


def test_initialization():
    "Test that the Fedora3Query class initializes"
    query = Gams3Query(base_url="http://example.com/fedora/")
    assert query.base_url == "http://example.com/fedora"
    assert query.api_url == "http://example.com/fedora/objects"

@pytest.mark.parametrize("pattern,expected", [
    ("o:foo", True),
    ("o:fo?", True),
    ("*foo*", True),
    ("o_foo", True),
    ("o-foo", True),
    ("o.foo2", True),
    ("o:Foo", True),
    ("o*", False),
    ("o?", False),
    ("o/foo", False),
    ("o$foo", False)
])  
def test_is_valid_pid_pattern(pattern, expected):
    query = Gams3Query(base_url="http://example.com/fedora")
    assert query.is_valid_pid_pattern(pattern) == expected


def test_find_objects_single_page(monkeypatch):
    xml = b"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<result xmlns=\"http://www.fedora.info/definitions/1/0/types/\">
    <listSession>
        <cursor>0</cursor>
    </listSession>
    <resultList>
        <objectFields><pid>o:one</pid></objectFields>
        <objectFields><pid>o:two</pid></objectFields>
    </resultList>
</result>
"""

    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        assert timeout == REQUEST_TIMEOUT
        return type(
            "FakeResponse",
            (),
            {
                "content": xml,
                "raise_for_status": staticmethod(lambda: None),
            },
        )()

    monkeypatch.setattr("gamspreprocessor.gams3.apiquery.requests.get", fake_get)

    query = Gams3Query(base_url="http://example.com/fedora")
    objects = list(query.find_objects("o:foo"))

    assert [obj.pid for obj in objects] == ["o:one", "o:two"]
    assert all(isinstance(obj, Gams3Object) for obj in objects)
    assert len(calls) == 1
    assert calls[0] == "http://example.com/fedora/objects?query=pid%7Eo:foo&resultFormat=xml&pid=true"


def test_find_objects_multi_page_uses_refreshed_session_token(monkeypatch):
    page_one = b"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<result xmlns=\"http://www.fedora.info/definitions/1/0/types/\">
    <listSession>
        <token>t1</token>
        <cursor>0</cursor>
    </listSession>
    <resultList>
        <objectFields><pid>o:first</pid></objectFields>
    </resultList>
</result>
"""

    page_two = b"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<result xmlns=\"http://www.fedora.info/definitions/1/0/types/\">
    <listSession>
        <token>t2</token>
        <cursor>25</cursor>
    </listSession>
    <resultList>
        <objectFields><pid>o:second</pid></objectFields>
    </resultList>
</result>
"""

    page_three = b"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<result xmlns=\"http://www.fedora.info/definitions/1/0/types/\">
    <listSession>
        <cursor>50</cursor>
    </listSession>
    <resultList>
        <objectFields><pid>o:third</pid></objectFields>
    </resultList>
</result>
"""

    pages = [page_one, page_two, page_three]
    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        assert timeout == REQUEST_TIMEOUT
        xml = pages.pop(0)
        return type(
            "FakeResponse",
            (),
            {
                "content": xml,
                "raise_for_status": staticmethod(lambda: None),
            },
        )()

    monkeypatch.setattr("gamspreprocessor.gams3.apiquery.requests.get", fake_get)

    query = Gams3Query(base_url="http://example.com/fedora")
    objects = list(query.find_objects("*hsa*"))

    assert [obj.pid for obj in objects] == ["o:first", "o:second", "o:third"]
    assert len(calls) == EXPECTED_PAGE_CALLS
    assert calls[0] == "http://example.com/fedora/objects?query=pid%7E*hsa*&resultFormat=xml&pid=true"
    assert calls[1].endswith("&sessionToken=t1")
    assert calls[2].endswith("&sessionToken=t2")


def test_find_objects_rejects_invalid_pattern():
    query = Gams3Query(base_url="http://example.com/fedora")

    with pytest.raises(ValueError):
        list(query.find_objects("o$foo"))


def test_find_objects_paginates_using_realistic_xml_fixtures(
    lazy_shared_datadir, monkeypatch, make_fake_response
):
    page_one = (lazy_shared_datadir / "query_response.xml").read_bytes()
    page_two = (lazy_shared_datadir / "query_response_page2.xml").read_bytes()
    page_three = (lazy_shared_datadir / "query_response_page3.xml").read_bytes()
    first_token = "41777e25dcd14aaaf3f5f6635729d697"
    second_token = "integration-token-2"
    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        assert timeout == REQUEST_TIMEOUT

        if "sessionToken=" not in url:
            return make_fake_response(page_one, 200)
        if f"sessionToken={first_token}" in url:
            return make_fake_response(page_two, 200)
        if f"sessionToken={second_token}" in url:
            return make_fake_response(page_three, 200)

        raise AssertionError(f"Unexpected URL requested: {url}")

    monkeypatch.setattr("gamspreprocessor.gams3.apiquery.requests.get", fake_get)

    query = Gams3Query(base_url="http://example.com/fedora")
    objects = list(query.find_objects("*hsa*"))
    pids = [obj.pid for obj in objects]

    assert calls[0] == "http://example.com/fedora/objects?query=pid%7E*hsa*&resultFormat=xml&pid=true"
    assert calls[1].endswith(f"sessionToken={first_token}")
    assert calls[2].endswith(f"sessionToken={second_token}")
    assert len(calls) == EXPECTED_PAGE_CALLS
    assert "o:integration.page2.1" in pids
    assert "o:integration.page2.2" in pids
    assert "o:integration.page3.1" in pids