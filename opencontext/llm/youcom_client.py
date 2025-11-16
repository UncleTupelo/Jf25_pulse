# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
OpenContext module: youcom_client
You.com API client for running AI agents
"""

import httpx
from typing import Any, Dict, Optional
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class YouComClient:
    """Client for You.com API agent runs"""

    def __init__(self, api_key: str, base_url: str = "https://api-you.com"):
        """
        Initialize You.com API client

        Args:
            api_key: You.com API key
            base_url: Base URL for You.com API (default: https://api-you.com)
        """
        if not api_key:
            raise ValueError("You.com API key must be provided")

        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = 60.0

    def run_agent(
        self,
        agent_id: str,
        input_text: str,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a You.com agent

        Args:
            agent_id: The UUID of the agent to run
            input_text: The input string to send to the agent
            stream: Whether to stream the response (default: False)
            **kwargs: Additional parameters to pass to the API

        Returns:
            Dict containing the API response

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/v1/agents/runs"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "agent": agent_id,
            "input": input_text,
            "stream": stream,
            **kwargs
        }

        try:
            logger.info(f"Running You.com agent {agent_id} with input: {input_text[:100]}...")

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=data, headers=headers)
                response.raise_for_status()

                result = response.json()
                logger.info(f"You.com agent run completed successfully")
                return result

        except httpx.HTTPError as e:
            logger.error(f"You.com API request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling You.com API: {str(e)}")
            raise

    async def run_agent_async(
        self,
        agent_id: str,
        input_text: str,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a You.com agent asynchronously

        Args:
            agent_id: The UUID of the agent to run
            input_text: The input string to send to the agent
            stream: Whether to stream the response (default: False)
            **kwargs: Additional parameters to pass to the API

        Returns:
            Dict containing the API response

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/v1/agents/runs"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "agent": agent_id,
            "input": input_text,
            "stream": stream,
            **kwargs
        }

        try:
            logger.info(f"Running You.com agent {agent_id} (async) with input: {input_text[:100]}...")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()

                result = response.json()
                logger.info(f"You.com agent run completed successfully (async)")
                return result

        except httpx.HTTPError as e:
            logger.error(f"You.com API request failed (async): {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling You.com API (async): {str(e)}")
            raise
