"Fixtures for testing the gams3 package."


import pytest


class FakeResponse:
    "A fake response object for testing purposes."

    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception(f"HTTP error: {self.status_code}")

@pytest.fixture
def fake_response_cls():
    return FakeResponse

@pytest.fixture(name="make_fake_response")
def _make_fake_response():
    "A fixture that returns a function to create a fake response object."
    def _make(content=b"", status_code=200):
        return FakeResponse(content=content, status_code=status_code)
    return _make