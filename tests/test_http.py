import asyncio

import pytest

from utils.functions import HTTPStatusError, InvalidResponseError, fetch_json


class FakeResponse:
    def __init__(self, status=200, payload=None, error=None):
        self.status = status
        self.payload = payload
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False

    async def json(self):
        if self.error:
            raise self.error
        return self.payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response


@pytest.mark.asyncio
async def test_fetch_json_checks_status_and_returns_object():
    session = FakeSession(FakeResponse(payload={"ok": True}))

    assert await fetch_json(session, "https://example.test", ssl=False) == {"ok": True}
    assert session.calls[0]["ssl"] is False
    assert session.calls[0]["timeout"] == 10


@pytest.mark.asyncio
async def test_fetch_json_rejects_http_errors_and_invalid_schema():
    with pytest.raises(HTTPStatusError):
        await fetch_json(FakeSession(FakeResponse(status=503, payload={})), "https://example.test")

    with pytest.raises(InvalidResponseError):
        await fetch_json(FakeSession(FakeResponse(payload=[])), "https://example.test")


@pytest.mark.asyncio
async def test_fetch_json_converts_timeout_to_request_error():
    from utils.functions import HTTPRequestError

    with pytest.raises(HTTPRequestError):
        await fetch_json(FakeSession(asyncio.TimeoutError()), "https://example.test")
