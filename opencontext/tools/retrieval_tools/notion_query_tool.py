# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Notion Query Tool
Retrieves data from Notion databases to enrich local context
"""

from typing import Any, Dict, List, Optional

from opencontext.managers.notion_sync_manager import get_sync_manager
from opencontext.tools.base import BaseTool
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class NotionQueryTool(BaseTool):
    """
    Tool for querying Notion databases

    Enables fetching todos, activities, and notes from Notion
    to enrich the local context with external knowledge base data.
    """

    @classmethod
    def get_name(cls) -> str:
        """Get tool name"""
        return "notion_query"

    @classmethod
    def get_description(cls) -> str:
        """Get tool description"""
        return """Query data from Notion databases to enrich local context.

**What this tool retrieves:**
- Todos and tasks from Notion databases
- Activities and events from Notion
- Notes and documents from Notion knowledge base
- Supports filtering by status, dates, and other properties

**When to use this tool:**
- When you need to access information stored in Notion
- When combining local context with Notion knowledge base
- When checking for updates in Notion databases
- When enriching search results with Notion data

**Requirements:**
- Notion integration must be enabled in configuration
- Appropriate database IDs must be configured
- Valid Notion API key must be provided

**Returns:**
- List of items from specified Notion database
- Includes all relevant properties and metadata
- Results can be combined with local search results"""

    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Get tool parameters"""
        return {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["todos", "activities", "notes"],
                    "description": "Type of data to query from Notion",
                },
                "filter": {
                    "type": "object",
                    "description": "Optional Notion filter object to narrow results. "
                    "Use Notion's filter syntax (e.g., {'property': 'Status', 'select': {'equals': 'Done'}})",
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Maximum number of results to return (1-100)",
                },
            },
            "required": ["query_type"],
        }

    def execute(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute Notion query

        Args:
            query_type: Type of data to query ("todos", "activities", "notes")
            filter: Optional Notion filter object
            limit: Maximum number of results (default 20)

        Returns:
            List of items from Notion database
        """
        query_type = kwargs.get("query_type")
        filter_obj = kwargs.get("filter")
        limit = kwargs.get("limit", 20)

        try:
            # Get sync manager
            sync_manager = get_sync_manager()

            if not sync_manager or not sync_manager.enabled:
                logger.warning("Notion integration not enabled")
                return [
                    {
                        "error": "Notion integration is not enabled. "
                        "Please configure Notion settings in config.yaml"
                    }
                ]

            # Query based on type
            if query_type == "todos":
                results = sync_manager.query_notion_todos(filter=filter_obj)
                return self._format_todos(results[:limit])
            elif query_type == "activities":
                # For now, return empty - can be extended
                logger.info("Activity queries from Notion not yet implemented")
                return []
            elif query_type == "notes":
                # For now, return empty - can be extended
                logger.info("Note queries from Notion not yet implemented")
                return []
            else:
                return [{"error": f"Unknown query type: {query_type}"}]

        except Exception as e:
            logger.error(f"NotionQueryTool execute exception: {str(e)}")
            return [{"error": f"Error querying Notion: {str(e)}"}]

    def _format_todos(self, todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format todos from Notion for consistent output"""
        formatted = []
        for todo in todos:
            formatted.append(
                {
                    "source": "notion",
                    "notion_id": todo.get("notion_id"),
                    "content": todo.get("content"),
                    "status": todo.get("status"),
                    "status_label": "completed" if todo.get("status") == 1 else "pending",
                    "start_time": todo.get("start_time"),
                    "end_time": todo.get("end_time"),
                    "created_time": todo.get("created_time"),
                    "last_edited_time": todo.get("last_edited_time"),
                    "document_type": "notion_todo",
                }
            )
        return formatted
