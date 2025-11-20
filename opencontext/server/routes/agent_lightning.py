# -*- coding: utf-8 -*-

"""Agent Lightning API routes."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from opencontext.config.config_manager import ConfigManager
from opencontext.llm.agent_lightning_client import (
    AgentLightningClient,
    AgentLightningNotConfigured,
)
from opencontext.server.utils import convert_resp
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["agent_lightning"])


class AgentLightningRunRequest(BaseModel):
    """Incoming payload for executing an agent."""

    agent: Optional[str] = Field(None, description="Agent slug or identifier")
    input: str = Field(..., description="Prompt or instruction for the agent")
    stream: bool = False
    parameters: Dict[str, Any] = Field(default_factory=dict)


def _get_agent_lightning_config() -> Dict[str, Any]:
    config_manager = ConfigManager()
    return config_manager.config.get("agent_lightning", {})


def _build_client(config: Dict[str, Any]) -> AgentLightningClient:
    try:
        return AgentLightningClient(
            api_key=config.get("api_key"),
            base_url=config.get("base_url"),
            endpoint=config.get("endpoint", "/api/agents/run"),
            default_agent=config.get("default_agent"),
            workspace=config.get("workspace_path"),
            timeout=config.get("timeout", 60.0),
            client_options=config.get("client_options", {}),
        )
    except AgentLightningNotConfigured as exc:
        logger.error("Agent Lightning configuration error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/api/agent-lightning/run")
async def run_agent_lightning(request: AgentLightningRunRequest):
    """Execute an Agent Lightning workflow and return the raw payload."""

    config = _get_agent_lightning_config()
    if not config.get("enabled", False):
        raise HTTPException(
            status_code=503,
            detail="Agent Lightning integration is not enabled. Set agent_lightning.enabled to true",
        )

    agent_id = request.agent or config.get("default_agent")
    if not agent_id:
        raise HTTPException(status_code=400, detail="No agent specified and no default agent configured")

    client = _build_client(config)
    result = await client.run_agent_async(
        agent_id=agent_id,
        input_text=request.input,
        stream=request.stream,
        parameters=request.parameters,
    )

    return convert_resp(
        data={
            "agent": agent_id,
            "transport": client.transport_mode,
            "result": result,
        }
    )


@router.get("/api/agent-lightning/status")
async def agent_lightning_status():
    """Return configuration information for diagnostics."""

    config = _get_agent_lightning_config()
    enabled = config.get("enabled", False)

    status = {
        "enabled": enabled,
        "default_agent": config.get("default_agent"),
        "base_url": config.get("base_url"),
    }

    if not enabled:
        status["ready"] = False
        return convert_resp(data=status)

    try:
        client = _build_client(config)
        status.update(
            {
                "ready": True,
                "transport": client.transport_mode,
                "endpoint": config.get("endpoint", "/api/agents/run"),
            }
        )
    except HTTPException as exc:
        status["ready"] = False
        status["error"] = exc.detail

    return convert_resp(data=status)
