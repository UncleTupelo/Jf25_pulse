"""Lightweight checks for the Agent Lightning client."""

import asyncio
from typing import Any, Dict

from unittest import mock

from opencontext.llm.agent_lightning_client import AgentLightningClient


class _FakeResponse:
    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        self.payload = kwargs.pop("payload")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        return _FakeResponse(self.payload)


class _FakeClient:
    def __init__(self, *args, **kwargs):
        self.payload = kwargs.pop("payload")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, *args, **kwargs):
        return _FakeResponse(self.payload)


def test_http_fallback_sync():
    payload = {"result": "ok", "transport": "http"}
    with mock.patch("httpx.Client", lambda *args, **kwargs: _FakeClient(payload=payload)):
        client = AgentLightningClient(
            base_url="http://localhost:9999",
            default_agent="demo",
        )
        result = client.run_agent(agent_id=None, input_text="ping")
        assert result == payload


def test_http_fallback_async():
    payload = {"result": "async-ok", "transport": "http"}

    async def _run():
        with mock.patch(
            "httpx.AsyncClient",
            lambda *args, **kwargs: _FakeAsyncClient(payload=payload),
        ):
            client = AgentLightningClient(
                base_url="http://localhost:9999",
                default_agent="demo",
            )
            return await client.run_agent_async(agent_id=None, input_text="ping")

    assert asyncio.run(_run()) == payload
