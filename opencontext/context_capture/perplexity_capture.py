#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Perplexity AI integration for context capture.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from opencontext.context_capture.base import BaseCaptureComponent
from opencontext.models.context import RawContextProperties
from opencontext.models.enums import ContentFormat, ContextSource
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class PerplexityCapture(BaseCaptureComponent):
    """
    Perplexity AI capture component.

    Syncs conversation history and summaries from Perplexity AI.
    """

    def __init__(self):
        """Initialize Perplexity capture component."""
        super().__init__(
            name="PerplexityCapture",
            description="Sync conversations from Perplexity AI",
            source_type=ContextSource.PERPLEXITY,
        )
        self._api_key = None
        self._sync_recent_days = 30
        self._synced_thread_ids = set()
        self._last_sync_time = None

    def _validate_config_impl(self, config: Dict[str, Any]) -> bool:
        """
        Validate Perplexity configuration.

        Args:
            config: Configuration dictionary

        Returns:
            True if configuration is valid
        """
        if "api_key" not in config or not config["api_key"]:
            logger.error(f"{self._name}: api_key is required")
            return False

        return True

    def _initialize_impl(self, config: Dict[str, Any]) -> bool:
        """
        Initialize Perplexity capture component.

        Args:
            config: Configuration dictionary

        Returns:
            True if initialization successful
        """
        try:
            self._api_key = config.get("api_key")
            self._sync_recent_days = config.get("sync_recent_days", 30)

            logger.info(f"{self._name}: Initialized (Perplexity API integration required)")
            return True

        except Exception as e:
            logger.exception(f"{self._name}: Initialization failed: {str(e)}")
            return False

    def _start_impl(self) -> bool:
        """
        Start Perplexity capture.

        Returns:
            True if started successfully
        """
        logger.info(f"{self._name}: Started")
        return True

    def _stop_impl(self, graceful: bool = True) -> bool:
        """
        Stop Perplexity capture.

        Args:
            graceful: Whether to stop gracefully

        Returns:
            True if stopped successfully
        """
        logger.info(f"{self._name}: Stopped")
        return True

    def _capture_impl(self) -> List[RawContextProperties]:
        """
        Capture Perplexity conversations.

        Returns:
            List of captured context data
        """
        contexts = []

        try:
            # Calculate date range for sync
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self._sync_recent_days)

            # Get threads in date range
            threads = self._get_threads(start_date, end_date)

            for thread in threads:
                thread_id = thread.get("id")

                # Skip if already synced
                if thread_id in self._synced_thread_ids:
                    continue

                # Create context from thread
                context = self._create_context_from_thread(thread)
                if context:
                    contexts.append(context)
                    self._synced_thread_ids.add(thread_id)

            if contexts:
                self._last_sync_time = datetime.now()
                logger.info(f"{self._name}: Captured {len(contexts)} threads")

        except Exception as e:
            logger.exception(f"{self._name}: Capture failed: {str(e)}")

        return contexts

    def _get_threads(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get Perplexity threads in date range.

        Args:
            start_date: Start date for sync
            end_date: End date for sync

        Returns:
            List of thread dictionaries
        """
        logger.info(f"{self._name}: Getting threads (Perplexity API integration required)")

        # Placeholder: Return empty list
        # Note: This would require Perplexity AI's API support for retrieving threads
        # Implementation would depend on their API endpoints and authentication

        return []

    def _create_context_from_thread(self, thread: Dict[str, Any]) -> Optional[RawContextProperties]:
        """
        Create context from Perplexity thread.

        Args:
            thread: Thread dictionary

        Returns:
            RawContextProperties or None
        """
        try:
            thread_id = thread.get("id")
            query = thread.get("query", "")
            answer = thread.get("answer", "")
            sources = thread.get("sources", [])
            created_time = thread.get("created_at")

            # Format thread as text
            thread_text = f"Query: {query}\n\n"
            thread_text += f"Answer: {answer}\n\n"

            if sources:
                thread_text += "Sources:\n"
                for i, source in enumerate(sources, 1):
                    thread_text += (
                        f"{i}. {source.get('title', 'Unknown')}: {source.get('url', '')}\n"
                    )

            context = RawContextProperties(
                source=self._source_type,
                content_format=ContentFormat.TEXT,
                raw_data=thread_text.encode("utf-8"),
                metadata={
                    "thread_id": thread_id,
                    "query": query,
                    "created_at": created_time,
                    "source_count": len(sources),
                },
            )

            return context

        except Exception as e:
            logger.exception(f"{self._name}: Failed to create context from thread: {str(e)}")
            return None

    def _get_status_impl(self) -> Dict[str, Any]:
        """
        Get Perplexity capture status.

        Returns:
            Status information dictionary
        """
        return {
            "last_sync_time": self._last_sync_time.isoformat() if self._last_sync_time else None,
            "synced_threads_count": len(self._synced_thread_ids),
            "sync_recent_days": self._sync_recent_days,
        }

    def _get_config_schema_impl(self) -> Dict[str, Any]:
        """
        Get configuration schema for Perplexity.

        Returns:
            Configuration schema dictionary
        """
        return {
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "Perplexity AI API Key",
                },
                "sync_recent_days": {
                    "type": "integer",
                    "description": "Number of recent days to sync",
                    "default": 30,
                    "minimum": 1,
                },
            },
            "required": ["api_key"],
        }
