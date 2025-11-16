#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
ChatGPT conversation integration for context capture.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from opencontext.context_capture.base import BaseCaptureComponent
from opencontext.models.context import RawContextProperties
from opencontext.models.enums import ContextSource, ContentFormat
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class ChatGPTCapture(BaseCaptureComponent):
    """
    ChatGPT conversation capture component.
    
    Syncs conversation history from ChatGPT.
    """

    def __init__(self):
        """Initialize ChatGPT capture component."""
        super().__init__(
            name="ChatGPTCapture",
            description="Sync conversations from ChatGPT",
            source_type=ContextSource.CHATGPT,
        )
        self._api_key = None
        self._sync_recent_days = 30
        self._synced_conversation_ids = set()
        self._last_sync_time = None

    def _validate_config_impl(self, config: Dict[str, Any]) -> bool:
        """
        Validate ChatGPT configuration.
        
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
        Initialize ChatGPT capture component.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if initialization successful
        """
        try:
            self._api_key = config.get("api_key")
            self._sync_recent_days = config.get("sync_recent_days", 30)
            
            logger.info(f"{self._name}: Initialized (ChatGPT API integration required)")
            return True
            
        except Exception as e:
            logger.exception(f"{self._name}: Initialization failed: {str(e)}")
            return False

    def _start_impl(self) -> bool:
        """
        Start ChatGPT capture.
        
        Returns:
            True if started successfully
        """
        logger.info(f"{self._name}: Started")
        return True

    def _stop_impl(self, graceful: bool = True) -> bool:
        """
        Stop ChatGPT capture.
        
        Args:
            graceful: Whether to stop gracefully
            
        Returns:
            True if stopped successfully
        """
        logger.info(f"{self._name}: Stopped")
        return True

    def _capture_impl(self) -> List[RawContextProperties]:
        """
        Capture ChatGPT conversations.
        
        Returns:
            List of captured context data
        """
        contexts = []
        
        try:
            # Calculate date range for sync
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self._sync_recent_days)
            
            # Get conversations in date range
            conversations = self._get_conversations(start_date, end_date)
            
            for conv in conversations:
                conv_id = conv.get("id")
                
                # Skip if already synced
                if conv_id in self._synced_conversation_ids:
                    continue
                
                # Create context from conversation
                context = self._create_context_from_conversation(conv)
                if context:
                    contexts.append(context)
                    self._synced_conversation_ids.add(conv_id)
            
            if contexts:
                self._last_sync_time = datetime.now()
                logger.info(f"{self._name}: Captured {len(contexts)} conversations")
                
        except Exception as e:
            logger.exception(f"{self._name}: Capture failed: {str(e)}")
        
        return contexts

    def _get_conversations(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get ChatGPT conversations in date range.
        
        Args:
            start_date: Start date for sync
            end_date: End date for sync
            
        Returns:
            List of conversation dictionaries
        """
        logger.info(f"{self._name}: Getting conversations (ChatGPT API integration required)")
        
        # Placeholder: Return empty list
        # Note: ChatGPT does not have an official API for retrieving conversation history
        # This would require:
        # 1. Using unofficial methods or browser automation
        # 2. Parsing exported conversation data
        # 3. Or waiting for official API support
        
        return []

    def _create_context_from_conversation(
        self, 
        conversation: Dict[str, Any]
    ) -> Optional[RawContextProperties]:
        """
        Create context from ChatGPT conversation.
        
        Args:
            conversation: Conversation dictionary
            
        Returns:
            RawContextProperties or None
        """
        try:
            conv_id = conversation.get("id")
            title = conversation.get("title", "Untitled")
            messages = conversation.get("messages", [])
            created_time = conversation.get("created_at")
            
            # Format conversation as text
            conversation_text = f"Conversation: {title}\n\n"
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                conversation_text += f"{role.upper()}: {content}\n\n"
            
            context = RawContextProperties(
                source=self._source_type,
                content_format=ContentFormat.TEXT,
                raw_data=conversation_text.encode("utf-8"),
                metadata={
                    "conversation_id": conv_id,
                    "title": title,
                    "created_at": created_time,
                    "message_count": len(messages),
                }
            )
            
            return context
            
        except Exception as e:
            logger.exception(f"{self._name}: Failed to create context from conversation: {str(e)}")
            return None

    def _get_status_impl(self) -> Dict[str, Any]:
        """
        Get ChatGPT capture status.
        
        Returns:
            Status information dictionary
        """
        return {
            "last_sync_time": self._last_sync_time.isoformat() if self._last_sync_time else None,
            "synced_conversations_count": len(self._synced_conversation_ids),
            "sync_recent_days": self._sync_recent_days,
        }

    def _get_config_schema_impl(self) -> Dict[str, Any]:
        """
        Get configuration schema for ChatGPT.
        
        Returns:
            Configuration schema dictionary
        """
        return {
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "OpenAI API Key",
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
