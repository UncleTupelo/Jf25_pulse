# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Notion storage backend for syncing context data to Notion databases
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from opencontext.llm.notion_client import NotionClient
from opencontext.storage.base_storage import IStorageBackend, StorageType
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class NotionBackend(IStorageBackend):
    """
    Notion storage backend for syncing and querying data from Notion databases.
    This backend enables optional integration with Notion knowledge base.
    """

    def __init__(self):
        self._client: Optional[NotionClient] = None
        self._initialized = False
        self._config = None
        self._database_mappings = {}

    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize Notion backend

        Args:
            config: Configuration dict with keys:
                - api_key: Notion API integration token
                - databases: Dict mapping data types to database IDs
                - enabled: Whether Notion sync is enabled

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self._config = config

            if not config.get("enabled", False):
                logger.info("Notion integration is disabled in config")
                self._initialized = False
                return False

            api_key = config.get("api_key")
            if not api_key:
                logger.error("Notion API key not provided in config")
                return False

            # Initialize Notion client
            self._client = NotionClient(api_key=api_key)

            # Store database mappings
            self._database_mappings = config.get("databases", {})

            if not self._database_mappings:
                logger.warning(
                    "No database mappings configured for Notion integration"
                )

            self._initialized = True
            logger.info("Notion backend initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Notion backend: {e}")
            self._initialized = False
            return False

    def get_name(self) -> str:
        """Get storage backend name"""
        return "notion"

    def get_storage_type(self) -> StorageType:
        """Get storage type"""
        return StorageType.DOCUMENT_DB

    def is_enabled(self) -> bool:
        """Check if Notion integration is enabled and initialized"""
        return self._initialized and self._client is not None

    def sync_todo(self, todo_data: Dict[str, Any]) -> Optional[str]:
        """
        Sync a todo item to Notion

        Args:
            todo_data: Todo data dict with keys:
                - id: Todo ID
                - content: Todo content/description
                - status: Todo status (0=pending, 1=completed)
                - urgency: Urgency level
                - start_time: Start datetime
                - end_time: End datetime
                - assignee: Assignee name

        Returns:
            Notion page ID if successful, None otherwise
        """
        if not self.is_enabled():
            logger.debug("Notion backend not enabled, skipping todo sync")
            return None

        database_id = self._database_mappings.get("todos")
        if not database_id:
            logger.warning("No database mapping for 'todos'")
            return None

        try:
            # Build Notion properties based on todo data
            properties = self._build_todo_properties(todo_data)

            # Create page in Notion
            result = self._client.create_page(
                database_id=database_id, properties=properties
            )

            page_id = result.get("id")
            logger.info(f"Todo synced to Notion: {page_id}")
            return page_id

        except Exception as e:
            logger.error(f"Failed to sync todo to Notion: {e}")
            return None

    def sync_activity(self, activity_data: Dict[str, Any]) -> Optional[str]:
        """
        Sync an activity to Notion

        Args:
            activity_data: Activity data dict with keys:
                - id: Activity ID
                - title: Activity title
                - content: Activity content
                - start_time: Start datetime
                - end_time: End datetime
                - metadata: Additional metadata (JSON string)

        Returns:
            Notion page ID if successful, None otherwise
        """
        if not self.is_enabled():
            logger.debug("Notion backend not enabled, skipping activity sync")
            return None

        database_id = self._database_mappings.get("activities")
        if not database_id:
            logger.warning("No database mapping for 'activities'")
            return None

        try:
            # Build Notion properties
            properties = self._build_activity_properties(activity_data)

            # Create page in Notion
            result = self._client.create_page(
                database_id=database_id, properties=properties
            )

            page_id = result.get("id")
            logger.info(f"Activity synced to Notion: {page_id}")
            return page_id

        except Exception as e:
            logger.error(f"Failed to sync activity to Notion: {e}")
            return None

    def sync_note(self, note_data: Dict[str, Any]) -> Optional[str]:
        """
        Sync a note/vault to Notion

        Args:
            note_data: Note data dict with keys:
                - id: Note ID
                - title: Note title
                - summary: Note summary
                - content: Note content
                - tags: Tags (string or list)
                - document_type: Document type

        Returns:
            Notion page ID if successful, None otherwise
        """
        if not self.is_enabled():
            logger.debug("Notion backend not enabled, skipping note sync")
            return None

        database_id = self._database_mappings.get("notes")
        if not database_id:
            logger.warning("No database mapping for 'notes'")
            return None

        try:
            # Build Notion properties
            properties = self._build_note_properties(note_data)

            # Build content blocks
            children = self._build_note_content_blocks(note_data.get("content", ""))

            # Create page in Notion
            result = self._client.create_page(
                database_id=database_id, properties=properties, children=children
            )

            page_id = result.get("id")
            logger.info(f"Note synced to Notion: {page_id}")
            return page_id

        except Exception as e:
            logger.error(f"Failed to sync note to Notion: {e}")
            return None

    def query_todos(
        self, filter: Optional[Dict[str, Any]] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query todos from Notion database

        Args:
            filter: Optional Notion filter object
            limit: Maximum number of results

        Returns:
            List of todo data dicts
        """
        if not self.is_enabled():
            logger.debug("Notion backend not enabled, skipping query")
            return []

        database_id = self._database_mappings.get("todos")
        if not database_id:
            logger.warning("No database mapping for 'todos'")
            return []

        try:
            result = self._client.query_database(
                database_id=database_id, filter=filter, page_size=limit
            )

            # Parse results into standardized format
            todos = []
            for page in result.get("results", []):
                todo = self._parse_todo_from_notion(page)
                if todo:
                    todos.append(todo)

            logger.info(f"Retrieved {len(todos)} todos from Notion")
            return todos

        except Exception as e:
            logger.error(f"Failed to query todos from Notion: {e}")
            return []

    def _build_todo_properties(self, todo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build Notion page properties for a todo"""
        properties = {
            "Name": {"title": [{"text": {"content": todo_data.get("content", "")[:2000]}}]},
        }

        # Add status if available
        status = todo_data.get("status", 0)
        status_text = "Done" if status == 1 else "To Do"
        properties["Status"] = {"select": {"name": status_text}}

        # Add urgency if available
        urgency = todo_data.get("urgency", 0)
        if urgency:
            urgency_text = "High" if urgency >= 2 else "Medium" if urgency >= 1 else "Low"
            properties["Priority"] = {"select": {"name": urgency_text}}

        # Add dates if available
        if todo_data.get("start_time"):
            properties["Start Date"] = {
                "date": {"start": todo_data["start_time"].isoformat() if isinstance(todo_data["start_time"], datetime) else todo_data["start_time"]}
            }

        if todo_data.get("end_time"):
            properties["Due Date"] = {
                "date": {"start": todo_data["end_time"].isoformat() if isinstance(todo_data["end_time"], datetime) else todo_data["end_time"]}
            }

        # Add assignee if available
        if todo_data.get("assignee"):
            properties["Assignee"] = {"rich_text": [{"text": {"content": todo_data["assignee"]}}]}

        return properties

    def _build_activity_properties(
        self, activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Notion page properties for an activity"""
        properties = {
            "Name": {"title": [{"text": {"content": activity_data.get("title", "")[:2000]}}]},
        }

        # Add description/content as rich text
        if activity_data.get("content"):
            properties["Description"] = {
                "rich_text": [{"text": {"content": activity_data["content"][:2000]}}]
            }

        # Add date range if available
        if activity_data.get("start_time") and activity_data.get("end_time"):
            properties["Date"] = {
                "date": {
                    "start": activity_data["start_time"].isoformat() if isinstance(activity_data["start_time"], datetime) else activity_data["start_time"],
                    "end": activity_data["end_time"].isoformat() if isinstance(activity_data["end_time"], datetime) else activity_data["end_time"],
                }
            }

        return properties

    def _build_note_properties(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build Notion page properties for a note"""
        properties = {
            "Name": {"title": [{"text": {"content": note_data.get("title", "")[:2000]}}]},
        }

        # Add summary
        if note_data.get("summary"):
            properties["Summary"] = {
                "rich_text": [{"text": {"content": note_data["summary"][:2000]}}]
            }

        # Add tags
        tags = note_data.get("tags", "")
        if tags:
            if isinstance(tags, str):
                tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            else:
                tag_list = tags
            properties["Tags"] = {"multi_select": [{"name": tag} for tag in tag_list[:10]]}

        # Add document type
        if note_data.get("document_type"):
            properties["Type"] = {"select": {"name": note_data["document_type"]}}

        return properties

    def _build_note_content_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Build Notion block children from note content"""
        if not content:
            return []

        # Split content into paragraphs and create blocks
        # Notion has a 2000 character limit per text block
        blocks = []
        paragraphs = content.split("\n\n")

        for para in paragraphs[:100]:  # Limit to 100 blocks
            if not para.strip():
                continue

            # Split long paragraphs
            if len(para) > 2000:
                chunks = [para[i : i + 2000] for i in range(0, len(para), 2000)]
                for chunk in chunks:
                    blocks.append(
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": chunk}}]
                            },
                        }
                    )
            else:
                blocks.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": para}}]
                        },
                    }
                )

        return blocks

    def _parse_todo_from_notion(self, page: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a Notion page into a todo data dict"""
        try:
            properties = page.get("properties", {})

            # Extract title/content
            title_prop = properties.get("Name", {})
            title_content = ""
            if title_prop.get("title"):
                title_content = "".join(
                    [t.get("plain_text", "") for t in title_prop["title"]]
                )

            # Extract status
            status_prop = properties.get("Status", {})
            status_text = status_prop.get("select", {}).get("name", "")
            status = 1 if status_text == "Done" else 0

            # Extract dates
            start_time = None
            end_time = None

            start_date_prop = properties.get("Start Date", {})
            if start_date_prop.get("date"):
                start_time = start_date_prop["date"].get("start")

            due_date_prop = properties.get("Due Date", {})
            if due_date_prop.get("date"):
                end_time = due_date_prop["date"].get("start")

            return {
                "notion_id": page.get("id"),
                "content": title_content,
                "status": status,
                "start_time": start_time,
                "end_time": end_time,
                "created_time": page.get("created_time"),
                "last_edited_time": page.get("last_edited_time"),
            }

        except Exception as e:
            logger.error(f"Failed to parse todo from Notion page: {e}")
            return None
