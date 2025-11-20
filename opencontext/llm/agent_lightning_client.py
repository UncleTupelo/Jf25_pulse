# -*- coding: utf-8 -*-

"""Agent Lightning integration helpers."""

from __future__ import annotations

import asyncio
import functools
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class AgentLightningNotConfigured(RuntimeError):
    """Raised when the Agent Lightning client is not properly configured."""


def _is_library_available() -> bool:
    """Return True if the agent_lightning package can be imported."""

    return importlib.util.find_spec("agent_lightning") is not None


class AgentLightningClient:
    """Facade that talks to agent-lightning either locally or via HTTP."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        endpoint: str = "/api/agents/run",
        default_agent: Optional[str] = None,
        workspace: Optional[str] = None,
        timeout: float = 60.0,
        client_options: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") if base_url else None
        self.endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        self.default_agent = default_agent
        self.timeout = timeout
        self.client_options = client_options or {}
        self.workspace = workspace
        if self.workspace:
            Path(self.workspace).expanduser().mkdir(parents=True, exist_ok=True)

        self._library_client: Any = None
        self._supports_async = False
        self._http_headers: Optional[Dict[str, str]] = None

        if _is_library_available():
            self._initialize_library_client()
        else:
            logger.info("agent-lightning library not installed; HTTP fallback will be used")

        if not self._library_client and not self.base_url:
            raise AgentLightningNotConfigured(
                "Agent Lightning requires either the Python package or a base_url"
            )

    @property
    def transport_mode(self) -> str:
        """Return the active transport (library or http)."""

        return "library" if self._library_client else "http"

    def resolve_agent_id(self, agent_id: Optional[str]) -> str:
        """Return the explicit agent identifier to be used for execution."""

        if agent_id:
            return agent_id
        if self.default_agent:
            return self.default_agent
        raise AgentLightningNotConfigured("No agent specified and no default agent configured")

    # ------------------------------------------------------------------
    # Public execution helpers
    # ------------------------------------------------------------------
    def run_agent(
        self,
        *,
        agent_id: Optional[str],
        input_text: str,
        stream: bool = False,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run an agent synchronously."""

        agent_identifier = self.resolve_agent_id(agent_id)
        parameters = parameters or {}

        if self._library_client:
            library_response = self._invoke_library_client(
                agent_identifier, input_text, stream=stream, parameters=parameters
            )
            if library_response is not None:
                return library_response

        return self._run_agent_via_http(
            agent_identifier, input_text, stream=stream, parameters=parameters
        )

    async def run_agent_async(
        self,
        *,
        agent_id: Optional[str],
        input_text: str,
        stream: bool = False,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run an agent asynchronously."""

        agent_identifier = self.resolve_agent_id(agent_id)
        parameters = parameters or {}

        if self._library_client:
            if self._supports_async:
                result = await self._invoke_library_client_async(
                    agent_identifier, input_text, stream=stream, parameters=parameters
                )
                if result is not None:
                    return result

            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                None,
                functools.partial(
                    self.run_agent,
                    agent_id=agent_identifier,
                    input_text=input_text,
                    stream=stream,
                    parameters=parameters,
                ),
            )

        return await self._run_agent_via_http_async(
            agent_identifier, input_text, stream=stream, parameters=parameters
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _initialize_library_client(self) -> None:
        try:
            module = importlib.import_module("agent_lightning")
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(f"Failed to import agent_lightning: {exc}")
            return

        candidate_names = [
            "AgentLightningClient",
            "AgentLightning",
            "LightningClient",
            "Client",
        ]

        client_cls = None
        for name in candidate_names:
            client_cls = getattr(module, name, None)
            if client_cls:
                break

        if not client_cls:
            logger.warning(
                "agent_lightning module found but no known client class is available"
            )
            return

        try:
            init_kwargs = self._build_init_kwargs(client_cls)
            self._library_client = client_cls(**init_kwargs)
            self._supports_async = any(
                hasattr(self._library_client, attr)
                for attr in ("arun", "run_async", "ainvoke", "invoke_async")
            )
            logger.info(
                "Initialized agent-lightning client via %s", client_cls.__name__
            )
        except Exception as exc:
            logger.warning(f"Failed to initialize agent-lightning client: {exc}")
            self._library_client = None

    def _build_init_kwargs(self, client_cls) -> Dict[str, Any]:
        params = inspect.signature(client_cls).parameters
        init_kwargs: Dict[str, Any] = {}
        mapping = {
            "api_key": self.api_key,
            "token": self.api_key,
            "base_url": self.base_url,
            "api_base": self.base_url,
            "workspace": self.workspace,
            "workspace_path": self.workspace,
            "workspace_dir": self.workspace,
            "default_agent": self.default_agent,
            "agent": self.default_agent,
        }

        for key, value in mapping.items():
            if key in params and value:
                init_kwargs[key] = value

        for key, value in self.client_options.items():
            if key in params and value is not None:
                init_kwargs[key] = value

        return init_kwargs

    def _invoke_library_client(
        self,
        agent_id: str,
        input_text: str,
        *,
        stream: bool,
        parameters: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        run_fn = self._resolve_library_callable("sync")
        if not run_fn:
            return None

        call_kwargs = self._build_run_kwargs(
            run_fn, agent_id, input_text, stream=stream, parameters=parameters
        )

        try:
            return run_fn(**call_kwargs)
        except Exception as exc:
            logger.error(f"agent-lightning execution failed: {exc}")
            raise

    async def _invoke_library_client_async(
        self,
        agent_id: str,
        input_text: str,
        *,
        stream: bool,
        parameters: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        run_fn = self._resolve_library_callable("async")
        if not run_fn:
            return None

        call_kwargs = self._build_run_kwargs(
            run_fn, agent_id, input_text, stream=stream, parameters=parameters
        )

        result = run_fn(**call_kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    def _resolve_library_callable(self, mode: str):
        if not self._library_client:
            return None

        candidate_names = [
            "run_agent",
            "run",
            "invoke",
            "execute",
        ]

        async_suffixes = ("arun", "run_async", "ainvoke", "invoke_async")
        sync_suffixes = tuple(candidate_names)

        if mode == "async":
            candidates = list(async_suffixes) + candidate_names
        else:
            candidates = list(sync_suffixes)

        for name in candidates:
            run_fn = getattr(self._library_client, name, None)
            if run_fn:
                return run_fn
        return None

    def _build_run_kwargs(
        self,
        func,
        agent_id: str,
        input_text: str,
        *,
        stream: bool,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        params = inspect.signature(func).parameters
        kwargs: Dict[str, Any] = {}

        self._maybe_assign(params, kwargs, agent_id, ("agent_id", "agent", "id", "slug", "name"))
        self._maybe_assign(
            params,
            kwargs,
            input_text,
            ("input_text", "input", "query", "prompt", "message"),
        )
        self._maybe_assign(params, kwargs, stream, ("stream", "streaming", "as_stream"))
        if parameters:
            self._maybe_assign(
                params,
                kwargs,
                parameters,
                ("parameters", "params", "options", "extra"),
            )

        for key, value in self.client_options.items():
            if key in params and key not in kwargs:
                kwargs[key] = value

        return kwargs

    @staticmethod
    def _maybe_assign(params, kwargs, value, names):
        if value is None:
            return
        for name in names:
            if name in params:
                kwargs[name] = value
                break

    # ------------------------------------------------------------------
    # HTTP fallback helpers
    # ------------------------------------------------------------------
    def _build_http_headers(self) -> Dict[str, str]:
        if self._http_headers is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._http_headers = headers
        return dict(self._http_headers)

    def _build_http_payload(
        self,
        agent_id: str,
        input_text: str,
        *,
        stream: bool,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = {
            "agent": agent_id,
            "input": input_text,
            "stream": stream,
        }
        merged_params = {**self.client_options.get("default_parameters", {}), **parameters}
        if merged_params:
            payload["params"] = merged_params
        return payload

    def _run_agent_via_http(
        self,
        agent_id: str,
        input_text: str,
        *,
        stream: bool,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not self.base_url:
            raise AgentLightningNotConfigured(
                "No base_url configured for agent-lightning HTTP fallback"
            )

        payload = self._build_http_payload(agent_id, input_text, stream=stream, parameters=parameters)
        url = f"{self.base_url}{self.endpoint}"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=payload, headers=self._build_http_headers())
            response.raise_for_status()
            return response.json()

    async def _run_agent_via_http_async(
        self,
        agent_id: str,
        input_text: str,
        *,
        stream: bool,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not self.base_url:
            raise AgentLightningNotConfigured(
                "No base_url configured for agent-lightning HTTP fallback"
            )

        payload = self._build_http_payload(agent_id, input_text, stream=stream, parameters=parameters)
        url = f"{self.base_url}{self.endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=self._build_http_headers())
            response.raise_for_status()
            return response.json()


__all__ = ["AgentLightningClient", "AgentLightningNotConfigured"]
