#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Example script demonstrating Notion integration usage
This shows how to use the Notion client, backend, and sync manager
"""

import os
from datetime import datetime
from pathlib import Path

# Add project root to path
import sys

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def example_notion_client():
    """Example: Using the Notion client directly"""
    from opencontext.llm.notion_client import NotionClient

    print("=" * 70)
    print("Example 1: Notion Client")
    print("=" * 70)

    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        print("⚠️  NOTION_API_KEY not set. Skipping client example.")
        return

    try:
        # Initialize client
        client = NotionClient(api_key=api_key)
        print("✓ Client initialized")

        # Example: Search workspace
        print("\n📝 Searching Notion workspace...")
        results = client.search(query="test", page_size=5)
        print(f"   Found {len(results.get('results', []))} results")

        # Example: Get database
        database_id = os.getenv("NOTION_TODOS_DB_ID")
        if database_id:
            print(f"\n🗄️  Getting database {database_id[:8]}...")
            db = client.get_database(database_id=database_id)
            print(f"   Database title: {db.get('title', [{}])[0].get('plain_text', 'N/A')}")
        else:
            print("\n⚠️  NOTION_TODOS_DB_ID not set. Skipping database example.")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_notion_backend():
    """Example: Using the Notion backend for syncing"""
    from opencontext.storage.backends.notion_backend import NotionBackend

    print("\n" + "=" * 70)
    print("Example 2: Notion Backend")
    print("=" * 70)

    config = {
        "enabled": True,
        "api_key": os.getenv("NOTION_API_KEY"),
        "databases": {
            "todos": os.getenv("NOTION_TODOS_DB_ID"),
            "activities": os.getenv("NOTION_ACTIVITIES_DB_ID"),
            "notes": os.getenv("NOTION_NOTES_DB_ID"),
        },
    }

    if not config["api_key"]:
        print("⚠️  NOTION_API_KEY not set. Skipping backend example.")
        return

    try:
        # Initialize backend
        backend = NotionBackend()
        success = backend.initialize(config)

        if not success:
            print("❌ Backend initialization failed")
            return

        print("✓ Backend initialized")

        # Example: Sync a todo
        if config["databases"]["todos"]:
            print("\n📋 Syncing a todo...")
            todo_data = {
                "id": 1,
                "content": "Example todo from MineContext integration",
                "status": 0,
                "urgency": 2,
                "start_time": datetime.now(),
                "assignee": "Test User",
            }

            page_id = backend.sync_todo(todo_data)
            if page_id:
                print(f"   ✓ Todo synced to Notion: {page_id[:8]}...")
            else:
                print("   ⚠️  Todo sync failed")

        # Example: Query todos
        if config["databases"]["todos"]:
            print("\n🔍 Querying todos from Notion...")
            todos = backend.query_todos(limit=5)
            print(f"   Retrieved {len(todos)} todos")
            for i, todo in enumerate(todos[:3], 1):
                print(f"   {i}. {todo.get('content', 'N/A')[:50]}")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_sync_manager():
    """Example: Using the Notion sync manager"""
    from opencontext.managers.notion_sync_manager import NotionSyncManager

    print("\n" + "=" * 70)
    print("Example 3: Notion Sync Manager")
    print("=" * 70)

    config = {
        "enabled": True,
        "api_key": os.getenv("NOTION_API_KEY"),
        "databases": {
            "todos": os.getenv("NOTION_TODOS_DB_ID"),
            "activities": os.getenv("NOTION_ACTIVITIES_DB_ID"),
            "notes": os.getenv("NOTION_NOTES_DB_ID"),
        },
        "sync": {
            "auto_sync": False,  # Set to True to enable automatic syncing
            "sync_interval": 300,
            "sync_on_create": False,
        },
    }

    if not config["api_key"]:
        print("⚠️  NOTION_API_KEY not set. Skipping sync manager example.")
        return

    try:
        # Initialize sync manager
        manager = NotionSyncManager(config)

        if not manager.enabled:
            print("❌ Sync manager not enabled")
            return

        print("✓ Sync manager initialized")

        # Get sync status
        print("\n📊 Sync status:")
        status = manager.get_sync_status()
        print(f"   Enabled: {status['enabled']}")
        print(f"   Auto-sync: {status['auto_sync']}")
        print(f"   Sync interval: {status['sync_interval']}s")

        # Example: Manual sync (commented out to avoid spamming Notion)
        # print("\n🔄 Running manual sync...")
        # results = manager.sync_all()
        # print(f"   Synced: {results}")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("Notion Integration Examples")
    print("=" * 70)
    print()

    # Check if API key is set
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        print("⚠️  No Notion API key found!")
        print("\nTo run these examples:")
        print("  1. Get your API key from https://www.notion.so/my-integrations")
        print("  2. Set environment variable: export NOTION_API_KEY='your_key'")
        print("  3. Optionally set database IDs:")
        print("     export NOTION_TODOS_DB_ID='your_database_id'")
        print("     export NOTION_ACTIVITIES_DB_ID='your_database_id'")
        print("     export NOTION_NOTES_DB_ID='your_database_id'")
        print()
        return

    # Run examples
    example_notion_client()
    example_notion_backend()
    example_sync_manager()

    print("\n" + "=" * 70)
    print("✅ Examples completed!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  - Check NOTION_SETUP.md for detailed setup instructions")
    print("  - Configure your Notion databases in config.yaml")
    print("  - Enable auto-sync if desired")
    print()


if __name__ == "__main__":
    main()
