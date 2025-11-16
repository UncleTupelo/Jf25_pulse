# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
OpenContext module: notion_client
Notion API client for syncing and querying knowledge base data
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from notion_client import AsyncClient, Client

from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class NotionClient:
    """Client for Notion API operations"""

    def __init__(self, api_key: str, async_mode: bool = False):
        """
        Initialize Notion API client

        Args:
            api_key: Notion API integration token
            async_mode: Whether to use async client (default: False)
        """
        if not api_key:
            raise ValueError("Notion API key must be provided")

        self.api_key = api_key
        self.async_mode = async_mode

        if async_mode:
            self.client = AsyncClient(auth=api_key)
        else:
            self.client = Client(auth=api_key)

        logger.info("Notion client initialized successfully")

    def create_page(
        self,
        database_id: str,
        properties: Dict[str, Any],
        children: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new page in a Notion database

        Args:
            database_id: The ID of the database to create the page in
            properties: Page properties (title, rich text, etc.)
            children: Optional list of block children to add to the page

        Returns:
            Dict containing the created page data

        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Creating page in database {database_id}")

            params = {"parent": {"database_id": database_id}, "properties": properties}

            if children:
                params["children"] = children

            result = self.client.pages.create(**params)
            logger.info(f"Page created successfully: {result['id']}")
            return result

        except Exception as e:
            logger.error(f"Failed to create Notion page: {str(e)}")
            raise

    def update_page(
        self, page_id: str, properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing Notion page

        Args:
            page_id: The ID of the page to update
            properties: Updated page properties

        Returns:
            Dict containing the updated page data

        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Updating page {page_id}")

            result = self.client.pages.update(page_id=page_id, properties=properties)
            logger.info(f"Page updated successfully: {page_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to update Notion page: {str(e)}")
            raise

    def get_page(self, page_id: str) -> Dict[str, Any]:
        """
        Retrieve a Notion page

        Args:
            page_id: The ID of the page to retrieve

        Returns:
            Dict containing the page data

        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Retrieving page {page_id}")

            result = self.client.pages.retrieve(page_id=page_id)
            logger.info(f"Page retrieved successfully: {page_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to retrieve Notion page: {str(e)}")
            raise

    def query_database(
        self,
        database_id: str,
        filter: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, str]]] = None,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Query a Notion database

        Args:
            database_id: The ID of the database to query
            filter: Optional filter object to narrow results
            sorts: Optional list of sort objects
            page_size: Number of results per page (max 100)

        Returns:
            Dict containing query results

        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Querying database {database_id}")

            params = {"database_id": database_id, "page_size": min(page_size, 100)}

            if filter:
                params["filter"] = filter
            if sorts:
                params["sorts"] = sorts

            result = self.client.databases.query(**params)
            logger.info(
                f"Database query successful: {len(result.get('results', []))} results"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to query Notion database: {str(e)}")
            raise

    def search(
        self,
        query: str,
        filter: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, str]] = None,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Search Notion workspace

        Args:
            query: Search query string
            filter: Optional filter (e.g., {"value": "page", "property": "object"})
            sort: Optional sort object
            page_size: Number of results per page (max 100)

        Returns:
            Dict containing search results

        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Searching Notion workspace: {query}")

            params = {"query": query, "page_size": min(page_size, 100)}

            if filter:
                params["filter"] = filter
            if sort:
                params["sort"] = sort

            result = self.client.search(**params)
            logger.info(
                f"Search successful: {len(result.get('results', []))} results"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to search Notion: {str(e)}")
            raise

    def get_database(self, database_id: str) -> Dict[str, Any]:
        """
        Retrieve database information

        Args:
            database_id: The ID of the database to retrieve

        Returns:
            Dict containing database schema and properties

        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Retrieving database {database_id}")

            result = self.client.databases.retrieve(database_id=database_id)
            logger.info(f"Database retrieved successfully: {database_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to retrieve Notion database: {str(e)}")
            raise

    def append_block_children(
        self, block_id: str, children: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Append blocks to a page or block

        Args:
            block_id: The ID of the parent block or page
            children: List of block objects to append

        Returns:
            Dict containing the response

        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Appending {len(children)} blocks to {block_id}")

            result = self.client.blocks.children.append(
                block_id=block_id, children=children
            )
            logger.info(f"Blocks appended successfully to {block_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to append blocks: {str(e)}")
            raise

    async def create_page_async(
        self,
        database_id: str,
        properties: Dict[str, Any],
        children: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new page in a Notion database asynchronously

        Args:
            database_id: The ID of the database to create the page in
            properties: Page properties (title, rich text, etc.)
            children: Optional list of block children to add to the page

        Returns:
            Dict containing the created page data

        Raises:
            Exception: If the API request fails
        """
        if not self.async_mode:
            raise RuntimeError("Client not initialized in async mode")

        try:
            logger.info(f"Creating page in database {database_id} (async)")

            params = {"parent": {"database_id": database_id}, "properties": properties}

            if children:
                params["children"] = children

            result = await self.client.pages.create(**params)
            logger.info(f"Page created successfully (async): {result['id']}")
            return result

        except Exception as e:
            logger.error(f"Failed to create Notion page (async): {str(e)}")
            raise

    async def query_database_async(
        self,
        database_id: str,
        filter: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, str]]] = None,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Query a Notion database asynchronously

        Args:
            database_id: The ID of the database to query
            filter: Optional filter object to narrow results
            sorts: Optional list of sort objects
            page_size: Number of results per page (max 100)

        Returns:
            Dict containing query results

        Raises:
            Exception: If the API request fails
        """
        if not self.async_mode:
            raise RuntimeError("Client not initialized in async mode")

        try:
            logger.info(f"Querying database {database_id} (async)")

            params = {"database_id": database_id, "page_size": min(page_size, 100)}

            if filter:
                params["filter"] = filter
            if sorts:
                params["sorts"] = sorts

            result = await self.client.databases.query(**params)
            logger.info(
                f"Database query successful (async): {len(result.get('results', []))} results"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to query Notion database (async): {str(e)}")
            raise
