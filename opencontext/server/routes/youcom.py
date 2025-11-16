# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
You.com API routes
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from opencontext.config.config_manager import ConfigManager
from opencontext.llm.youcom_client import YouComClient
from opencontext.server.utils import convert_resp
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["youcom"])


class AgentRunRequest(BaseModel):
    """Request model for running a You.com agent"""
    agent_id: Optional[str] = None
    input: str
    stream: bool = False


class AgentRunResponse(BaseModel):
    """Response model for agent run"""
    success: bool
    data: dict
    message: Optional[str] = None


@router.post("/api/youcom/agent/run")
async def run_youcom_agent(request: AgentRunRequest):
    """
    Run a You.com agent

    Args:
        request: AgentRunRequest containing agent_id, input, and stream settings

    Returns:
        Response containing the agent run results
    """
    try:
        # Get configuration
        config_manager = ConfigManager()
        youcom_config = config_manager.config.get("youcom_api", {})

        if not youcom_config.get("enabled", False):
            raise HTTPException(
                status_code=503,
                detail="You.com API integration is not enabled. Please enable it in config.yaml"
            )

        api_key = youcom_config.get("api_key")
        if not api_key or api_key == "${YOUCOM_API_KEY}":
            raise HTTPException(
                status_code=500,
                detail="You.com API key not configured. Please set YOUCOM_API_KEY environment variable"
            )

        base_url = youcom_config.get("base_url", "https://api-you.com")

        # Use provided agent_id or fall back to default
        agent_id = request.agent_id or youcom_config.get("default_agent_id")
        if not agent_id:
            raise HTTPException(
                status_code=400,
                detail="No agent_id provided and no default_agent_id configured"
            )

        # Initialize client and run agent
        client = YouComClient(api_key=api_key, base_url=base_url)
        result = await client.run_agent_async(
            agent_id=agent_id,
            input_text=request.input,
            stream=request.stream
        )

        logger.info(f"Successfully ran You.com agent {agent_id}")
        return convert_resp(data={
            "success": True,
            "agent_id": agent_id,
            "result": result
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running You.com agent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run You.com agent: {str(e)}"
        )


@router.get("/api/youcom/status")
async def youcom_status():
    """
    Check You.com API configuration status

    Returns:
        Configuration status and availability
    """
    try:
        config_manager = ConfigManager()
        youcom_config = config_manager.config.get("youcom_api", {})

        enabled = youcom_config.get("enabled", False)
        api_key_configured = bool(
            youcom_config.get("api_key") and
            youcom_config.get("api_key") != "${YOUCOM_API_KEY}"
        )
        default_agent = youcom_config.get("default_agent_id")

        return convert_resp(data={
            "enabled": enabled,
            "api_key_configured": api_key_configured,
            "default_agent_id": default_agent,
            "base_url": youcom_config.get("base_url", "https://api-you.com"),
            "ready": enabled and api_key_configured
        })

    except Exception as e:
        logger.error(f"Error checking You.com status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check You.com status: {str(e)}"
        )
