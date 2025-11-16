# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Notion Sync Manager - handles bidirectional synchronization between local storage and Notion
"""

import asyncio
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from opencontext.storage.backends.notion_backend import NotionBackend
from opencontext.storage.global_storage import get_storage
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class NotionSyncManager:
    """
    Manager for syncing data between local storage and Notion.
    Supports both manual and automated syncing.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Notion Sync Manager

        Args:
            config: Configuration dict with sync settings
        """
        self.config = config
        self.notion_backend: Optional[NotionBackend] = None
        self.enabled = config.get("enabled", False)
        self.auto_sync = config.get("sync", {}).get("auto_sync", False)
        self.sync_interval = config.get("sync", {}).get("sync_interval", 300)
        self.sync_on_create = config.get("sync", {}).get("sync_on_create", False)

        self._sync_thread = None
        self._stop_sync = threading.Event()
        self._last_sync_times = {
            "todos": None,
            "activities": None,
            "notes": None,
        }

        if self.enabled:
            self._initialize_notion_backend()

    def _initialize_notion_backend(self) -> bool:
        """Initialize the Notion backend"""
        try:
            self.notion_backend = NotionBackend()
            success = self.notion_backend.initialize(self.config)

            if success:
                logger.info("Notion sync manager initialized successfully")
            else:
                logger.warning("Notion backend initialization failed")
                self.enabled = False

            return success

        except Exception as e:
            logger.error(f"Failed to initialize Notion sync manager: {e}")
            self.enabled = False
            return False

    def start_auto_sync(self):
        """Start automatic syncing in a background thread"""
        if not self.enabled or not self.auto_sync:
            logger.info("Auto-sync not enabled")
            return

        if self._sync_thread and self._sync_thread.is_alive():
            logger.warning("Auto-sync thread already running")
            return

        logger.info(f"Starting auto-sync thread (interval: {self.sync_interval} seconds)")
        self._stop_sync.clear()
        self._sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._sync_thread.start()

    def stop_auto_sync(self):
        """Stop the automatic syncing thread"""
        if self._sync_thread and self._sync_thread.is_alive():
            logger.info("Stopping auto-sync thread")
            self._stop_sync.set()
            self._sync_thread.join(timeout=10)

    def _sync_loop(self):
        """Background sync loop"""
        while not self._stop_sync.is_set():
            try:
                self.sync_all()
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")

            # Wait for next sync interval or stop event
            self._stop_sync.wait(timeout=self.sync_interval)

    def sync_all(self) -> Dict[str, int]:
        """
        Sync all data types to Notion

        Returns:
            Dict with counts of synced items per type
        """
        if not self.enabled or not self.notion_backend:
            logger.debug("Notion sync not enabled")
            return {"todos": 0, "activities": 0, "notes": 0}

        results = {
            "todos": self.sync_todos(),
            "activities": self.sync_activities(),
            "notes": self.sync_notes(),
        }

        logger.info(f"Sync completed: {results}")
        return results

    def sync_todos(self) -> int:
        """
        Sync todos to Notion

        Returns:
            Number of todos synced
        """
        if not self.enabled or not self.notion_backend:
            return 0

        try:
            storage = get_storage()
            if not storage:
                logger.warning("Storage not available")
                return 0

            # Get todos created/updated since last sync
            todos = storage.get_todos(limit=100)

            synced_count = 0
            for todo in todos:
                # Skip if already synced (check metadata or sync timestamp)
                # For now, sync all - in production, track sync state
                result = self.notion_backend.sync_todo(todo)
                if result:
                    synced_count += 1

            self._last_sync_times["todos"] = datetime.now()
            logger.info(f"Synced {synced_count} todos to Notion")
            return synced_count

        except Exception as e:
            logger.error(f"Failed to sync todos: {e}")
            return 0

    def sync_activities(self) -> int:
        """
        Sync activities to Notion

        Returns:
            Number of activities synced
        """
        if not self.enabled or not self.notion_backend:
            return 0

        try:
            storage = get_storage()
            if not storage:
                logger.warning("Storage not available")
                return 0

            # Get recent activities
            activities = storage.get_activities(limit=100)

            synced_count = 0
            for activity in activities:
                result = self.notion_backend.sync_activity(activity)
                if result:
                    synced_count += 1

            self._last_sync_times["activities"] = datetime.now()
            logger.info(f"Synced {synced_count} activities to Notion")
            return synced_count

        except Exception as e:
            logger.error(f"Failed to sync activities: {e}")
            return 0

    def sync_notes(self) -> int:
        """
        Sync notes/vaults to Notion

        Returns:
            Number of notes synced
        """
        if not self.enabled or not self.notion_backend:
            return 0

        try:
            storage = get_storage()
            if not storage:
                logger.warning("Storage not available")
                return 0

            # Get recent vaults
            vaults = storage.get_vaults(limit=100)

            synced_count = 0
            for vault in vaults:
                result = self.notion_backend.sync_note(vault)
                if result:
                    synced_count += 1

            self._last_sync_times["notes"] = datetime.now()
            logger.info(f"Synced {synced_count} notes to Notion")
            return synced_count

        except Exception as e:
            logger.error(f"Failed to sync notes: {e}")
            return 0

    def sync_single_todo(self, todo_data: Dict[str, Any]) -> Optional[str]:
        """
        Sync a single todo to Notion

        Args:
            todo_data: Todo data dict

        Returns:
            Notion page ID if successful, None otherwise
        """
        if not self.enabled or not self.notion_backend:
            return None

        if self.sync_on_create:
            return self.notion_backend.sync_todo(todo_data)

        return None

    def sync_single_activity(self, activity_data: Dict[str, Any]) -> Optional[str]:
        """
        Sync a single activity to Notion

        Args:
            activity_data: Activity data dict

        Returns:
            Notion page ID if successful, None otherwise
        """
        if not self.enabled or not self.notion_backend:
            return None

        if self.sync_on_create:
            return self.notion_backend.sync_activity(activity_data)

        return None

    def sync_single_note(self, note_data: Dict[str, Any]) -> Optional[str]:
        """
        Sync a single note to Notion

        Args:
            note_data: Note data dict

        Returns:
            Notion page ID if successful, None otherwise
        """
        if not self.enabled or not self.notion_backend:
            return None

        if self.sync_on_create:
            return self.notion_backend.sync_note(note_data)

        return None

    def query_notion_todos(self, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query todos from Notion

        Args:
            filter: Optional Notion filter

        Returns:
            List of todo data dicts
        """
        if not self.enabled or not self.notion_backend:
            return []

        return self.notion_backend.query_todos(filter=filter)

    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current sync status

        Returns:
            Dict with sync status information
        """
        return {
            "enabled": self.enabled,
            "auto_sync": self.auto_sync,
            "sync_interval": self.sync_interval,
            "last_sync_times": self._last_sync_times,
            "auto_sync_running": self._sync_thread is not None and self._sync_thread.is_alive(),
        }


# Global sync manager instance
_sync_manager: Optional[NotionSyncManager] = None


def initialize_sync_manager(config: Dict[str, Any]) -> NotionSyncManager:
    """
    Initialize the global sync manager

    Args:
        config: Notion sync configuration

    Returns:
        Initialized NotionSyncManager instance
    """
    global _sync_manager
    _sync_manager = NotionSyncManager(config)
    return _sync_manager


def get_sync_manager() -> Optional[NotionSyncManager]:
    """Get the global sync manager instance"""
    return _sync_manager
