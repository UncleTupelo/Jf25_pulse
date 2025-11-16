#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for Notion integration
Tests the Notion client, backend, and sync manager
"""

import os
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class TestNotionClient(unittest.TestCase):
    """Test cases for NotionClient"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_api_key = "secret_test_key_12345"

    @patch("opencontext.llm.notion_client.Client")
    def test_client_initialization(self, mock_client_class):
        """Test Notion client initialization"""
        from opencontext.llm.notion_client import NotionClient

        client = NotionClient(api_key=self.mock_api_key)
        self.assertIsNotNone(client)
        self.assertEqual(client.api_key, self.mock_api_key)
        mock_client_class.assert_called_once_with(auth=self.mock_api_key)

    def test_client_requires_api_key(self):
        """Test that client requires API key"""
        from opencontext.llm.notion_client import NotionClient

        with self.assertRaises(ValueError):
            NotionClient(api_key="")

    @patch("opencontext.llm.notion_client.Client")
    def test_create_page(self, mock_client_class):
        """Test creating a page in Notion"""
        from opencontext.llm.notion_client import NotionClient

        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.pages.create.return_value = {"id": "page_123", "object": "page"}

        # Create client and page
        client = NotionClient(api_key=self.mock_api_key)
        database_id = "db_123"
        properties = {"Name": {"title": [{"text": {"content": "Test Page"}}]}}

        result = client.create_page(database_id=database_id, properties=properties)

        # Assertions
        self.assertEqual(result["id"], "page_123")
        mock_client.pages.create.assert_called_once()

    @patch("opencontext.llm.notion_client.Client")
    def test_query_database(self, mock_client_class):
        """Test querying a Notion database"""
        from opencontext.llm.notion_client import NotionClient

        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.databases.query.return_value = {"results": [{"id": "page_1"}, {"id": "page_2"}]}

        # Create client and query
        client = NotionClient(api_key=self.mock_api_key)
        database_id = "db_123"

        result = client.query_database(database_id=database_id)

        # Assertions
        self.assertEqual(len(result["results"]), 2)
        mock_client.databases.query.assert_called_once()


class TestNotionBackend(unittest.TestCase):
    """Test cases for NotionBackend"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "enabled": True,
            "api_key": "secret_test_key_12345",
            "databases": {
                "todos": "db_todos_123",
                "activities": "db_activities_456",
                "notes": "db_notes_789",
            },
        }

    @patch("opencontext.storage.backends.notion_backend.NotionClient")
    def test_backend_initialization(self, mock_client_class):
        """Test Notion backend initialization"""
        from opencontext.storage.backends.notion_backend import NotionBackend

        backend = NotionBackend()
        result = backend.initialize(self.config)

        self.assertTrue(result)
        self.assertTrue(backend.is_enabled())
        mock_client_class.assert_called_once()

    def test_backend_disabled_when_not_configured(self):
        """Test backend is disabled when enabled=False"""
        from opencontext.storage.backends.notion_backend import NotionBackend

        config = {"enabled": False}
        backend = NotionBackend()
        result = backend.initialize(config)

        self.assertFalse(result)
        self.assertFalse(backend.is_enabled())

    @patch("opencontext.storage.backends.notion_backend.NotionClient")
    def test_sync_todo(self, mock_client_class):
        """Test syncing a todo to Notion"""
        from opencontext.storage.backends.notion_backend import NotionBackend

        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.create_page.return_value = {"id": "page_123"}

        # Initialize backend
        backend = NotionBackend()
        backend.initialize(self.config)

        # Sync todo
        todo_data = {
            "id": 1,
            "content": "Test todo",
            "status": 0,
            "urgency": 1,
            "start_time": datetime.now(),
        }

        page_id = backend.sync_todo(todo_data)

        # Assertions
        self.assertEqual(page_id, "page_123")
        mock_client.create_page.assert_called_once()

    @patch("opencontext.storage.backends.notion_backend.NotionClient")
    def test_sync_activity(self, mock_client_class):
        """Test syncing an activity to Notion"""
        from opencontext.storage.backends.notion_backend import NotionBackend

        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.create_page.return_value = {"id": "page_456"}

        # Initialize backend
        backend = NotionBackend()
        backend.initialize(self.config)

        # Sync activity
        activity_data = {
            "id": 1,
            "title": "Test activity",
            "content": "Activity description",
            "start_time": datetime.now(),
            "end_time": datetime.now(),
        }

        page_id = backend.sync_activity(activity_data)

        # Assertions
        self.assertEqual(page_id, "page_456")
        mock_client.create_page.assert_called_once()

    @patch("opencontext.storage.backends.notion_backend.NotionClient")
    def test_query_todos(self, mock_client_class):
        """Test querying todos from Notion"""
        from opencontext.storage.backends.notion_backend import NotionBackend

        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.query_database.return_value = {
            "results": [
                {
                    "id": "page_1",
                    "properties": {
                        "Name": {"title": [{"plain_text": "Todo 1"}]},
                        "Status": {"select": {"name": "To Do"}},
                    },
                }
            ]
        }

        # Initialize backend
        backend = NotionBackend()
        backend.initialize(self.config)

        # Query todos
        todos = backend.query_todos()

        # Assertions
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["notion_id"], "page_1")
        mock_client.query_database.assert_called_once()


class TestNotionSyncManager(unittest.TestCase):
    """Test cases for NotionSyncManager"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "enabled": True,
            "api_key": "secret_test_key_12345",
            "databases": {
                "todos": "db_todos_123",
                "activities": "db_activities_456",
                "notes": "db_notes_789",
            },
            "sync": {
                "auto_sync": False,
                "sync_interval": 300,
                "sync_on_create": False,
            },
        }

    @patch("opencontext.managers.notion_sync_manager.NotionBackend")
    def test_sync_manager_initialization(self, mock_backend_class):
        """Test sync manager initialization"""
        from opencontext.managers.notion_sync_manager import NotionSyncManager

        # Setup mock
        mock_backend = MagicMock()
        mock_backend_class.return_value = mock_backend
        mock_backend.initialize.return_value = True

        # Initialize manager
        manager = NotionSyncManager(self.config)

        # Assertions
        self.assertTrue(manager.enabled)
        mock_backend_class.assert_called_once()
        mock_backend.initialize.assert_called_once_with(self.config)

    def test_sync_manager_disabled_when_not_configured(self):
        """Test sync manager is disabled when enabled=False"""
        from opencontext.managers.notion_sync_manager import NotionSyncManager

        config = {"enabled": False}
        manager = NotionSyncManager(config)

        self.assertFalse(manager.enabled)

    @patch("opencontext.managers.notion_sync_manager.get_storage")
    @patch("opencontext.managers.notion_sync_manager.NotionBackend")
    def test_sync_todos(self, mock_backend_class, mock_get_storage):
        """Test syncing todos"""
        from opencontext.managers.notion_sync_manager import NotionSyncManager

        # Setup mocks
        mock_backend = MagicMock()
        mock_backend_class.return_value = mock_backend
        mock_backend.initialize.return_value = True
        mock_backend.sync_todo.return_value = "page_123"

        mock_storage = MagicMock()
        mock_get_storage.return_value = mock_storage
        mock_storage.get_todos.return_value = [
            {"id": 1, "content": "Todo 1"},
            {"id": 2, "content": "Todo 2"},
        ]

        # Initialize manager and sync
        manager = NotionSyncManager(self.config)
        count = manager.sync_todos()

        # Assertions
        self.assertEqual(count, 2)
        self.assertEqual(mock_backend.sync_todo.call_count, 2)

    @patch("opencontext.managers.notion_sync_manager.NotionBackend")
    def test_get_sync_status(self, mock_backend_class):
        """Test getting sync status"""
        from opencontext.managers.notion_sync_manager import NotionSyncManager

        # Setup mock
        mock_backend = MagicMock()
        mock_backend_class.return_value = mock_backend
        mock_backend.initialize.return_value = True

        # Initialize manager
        manager = NotionSyncManager(self.config)
        status = manager.get_sync_status()

        # Assertions
        self.assertTrue(status["enabled"])
        self.assertFalse(status["auto_sync"])
        self.assertEqual(status["sync_interval"], 300)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestNotionClient))
    suite.addTests(loader.loadTestsFromTestCase(TestNotionBackend))
    suite.addTests(loader.loadTestsFromTestCase(TestNotionSyncManager))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 70)
    print("Notion Integration Unit Tests")
    print("=" * 70)
    print()

    success = run_tests()

    print()
    print("=" * 70)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 70)

    sys.exit(0 if success else 1)
