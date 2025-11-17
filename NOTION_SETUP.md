# Notion Integration Setup Guide

This guide explains how to set up and use the Notion integration in MineContext. The integration allows you to sync your context data (todos, activities, notes) with Notion databases and query Notion to enrich your local context.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup Steps](#setup-steps)
  - [1. Create Notion Integration](#1-create-notion-integration)
  - [2. Create Notion Databases](#2-create-notion-databases)
  - [3. Configure MineContext](#3-configure-minecontext)
  - [4. Enable Sync](#4-enable-sync)
- [Features](#features)
- [Usage](#usage)
- [Configuration Options](#configuration-options)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

## Overview

The Notion integration provides:

1. **Syncing**: Push todos, activities, and notes from MineContext to Notion databases
2. **Querying**: Fetch data from Notion to enrich local context and search results
3. **Automation**: Optional automatic syncing at configurable intervals
4. **Privacy**: Local-first design - Notion sync is completely optional

## Prerequisites

- MineContext installed and configured
- A Notion account (free or paid)
- Basic understanding of Notion databases

## Setup Steps

### 1. Create Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click **"+ New integration"**
3. Give it a name (e.g., "MineContext Sync")
4. Select the workspace where you want to integrate
5. Under **Capabilities**, ensure the following are enabled:
   - Read content
   - Update content
   - Insert content
6. Click **Submit**
7. Copy the **Internal Integration Token** (starts with `secret_`)

### 2. Create Notion Databases

You need to create three databases in Notion (or use existing ones):

#### Todos Database

Create a database with the following properties:

- **Name** (Title): The todo content
- **Status** (Select): Options: "To Do", "Done"
- **Priority** (Select): Options: "Low", "Medium", "High"
- **Start Date** (Date): When the todo starts
- **Due Date** (Date): When the todo is due
- **Assignee** (Text): Who is assigned

#### Activities Database

Create a database with the following properties:

- **Name** (Title): Activity title
- **Description** (Text): Activity description
- **Date** (Date): Activity date range (start and end)

#### Notes Database

Create a database with the following properties:

- **Name** (Title): Note title
- **Summary** (Text): Note summary
- **Tags** (Multi-select): Tags for categorization
- **Type** (Select): Document type

### 3. Share Databases with Integration

For each database:

1. Click the **"..."** menu in the top-right
2. Click **"Add connections"**
3. Select your MineContext integration
4. Click **"Confirm"**

### 4. Get Database IDs

For each database:

1. Open the database in Notion
2. Copy the URL from your browser
3. Extract the database ID from the URL:
   ```
   https://www.notion.so/{workspace}/{database_id}?v={view_id}
   ```
   The database_id is the 32-character string between the workspace and `?v=`

### 5. Configure MineContext

1. **Update environment variables**:

   Edit your `.env` file (or create from `.env.example`):

   ```bash
   # Notion Integration
   NOTION_API_KEY=secret_your_integration_token_here
   NOTION_TODOS_DB_ID=your_todos_database_id
   NOTION_ACTIVITIES_DB_ID=your_activities_database_id
   NOTION_NOTES_DB_ID=your_notes_database_id
   ```

2. **Update config.yaml**:

   In `config/config.yaml`, find the `storage` section and update the Notion backend configuration:

   ```yaml
   storage:
     enabled: true
     backends:
       # ... existing backends ...

       - name: "notion_sync"
         storage_type: "document_db"
         backend: "notion"
         config:
           enabled: true  # Set to true to enable
           api_key: "${NOTION_API_KEY}"
           databases:
             todos: "${NOTION_TODOS_DB_ID}"
             activities: "${NOTION_ACTIVITIES_DB_ID}"
             notes: "${NOTION_NOTES_DB_ID}"
           sync:
             auto_sync: true  # Enable automatic syncing
             sync_interval: 300  # Sync every 5 minutes
             sync_on_create: true  # Sync immediately when items are created
   ```

## Features

### 1. Manual Syncing

Sync specific data types manually:

```python
from opencontext.managers.notion_sync_manager import get_sync_manager

sync_manager = get_sync_manager()

# Sync todos
sync_manager.sync_todos()

# Sync activities
sync_manager.sync_activities()

# Sync notes
sync_manager.sync_notes()

# Sync everything
sync_manager.sync_all()
```

### 2. Automatic Syncing

When enabled, MineContext will automatically sync data at the configured interval:

```yaml
sync:
  auto_sync: true
  sync_interval: 300  # seconds (5 minutes)
```

### 3. Sync on Create

Immediately sync items when they're created:

```yaml
sync:
  sync_on_create: true
```

### 4. Querying Notion

Use the Notion query tool to fetch data from Notion:

```python
from opencontext.tools.retrieval_tools.notion_query_tool import NotionQueryTool

tool = NotionQueryTool()

# Query todos
results = tool.execute(query_type="todos", limit=20)

# Query with filter
filter_obj = {
    "property": "Status",
    "select": {"equals": "Done"}
}
results = tool.execute(query_type="todos", filter=filter_obj, limit=10)
```

## Usage

### Using via Python API

```python
from opencontext.managers.notion_sync_manager import initialize_sync_manager

# Initialize sync manager
config = {
    "enabled": True,
    "api_key": "secret_your_token",
    "databases": {
        "todos": "db_id_1",
        "activities": "db_id_2",
        "notes": "db_id_3"
    },
    "sync": {
        "auto_sync": True,
        "sync_interval": 300,
        "sync_on_create": True
    }
}

sync_manager = initialize_sync_manager(config)

# Start automatic syncing
sync_manager.start_auto_sync()

# Manually sync specific items
todo_data = {
    "id": 1,
    "content": "Review pull request",
    "status": 0,
    "urgency": 2
}
sync_manager.sync_single_todo(todo_data)

# Get sync status
status = sync_manager.get_sync_status()
print(status)
```

### Using via CLI

When the server is running, syncing happens automatically if enabled. You can check the status via the web interface at `http://localhost:1733`.

## Configuration Options

### Notion Backend Config

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable Notion integration |
| `api_key` | string | - | Notion API integration token |
| `databases.todos` | string | - | Todos database ID |
| `databases.activities` | string | - | Activities database ID |
| `databases.notes` | string | - | Notes database ID |

### Sync Config

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auto_sync` | boolean | `false` | Enable automatic syncing |
| `sync_interval` | integer | `300` | Sync interval in seconds |
| `sync_on_create` | boolean | `false` | Sync immediately on item creation |

## API Reference

### NotionClient

The low-level Notion API client:

```python
from opencontext.llm.notion_client import NotionClient

client = NotionClient(api_key="secret_...")

# Create a page
client.create_page(
    database_id="db_id",
    properties={"Name": {"title": [{"text": {"content": "My Page"}}]}}
)

# Query database
results = client.query_database(
    database_id="db_id",
    filter={"property": "Status", "select": {"equals": "Active"}}
)

# Search workspace
results = client.search(query="my search term")
```

### NotionBackend

Storage backend for syncing:

```python
from opencontext.storage.backends.notion_backend import NotionBackend

backend = NotionBackend()
backend.initialize(config)

# Sync data
backend.sync_todo(todo_data)
backend.sync_activity(activity_data)
backend.sync_note(note_data)

# Query data
todos = backend.query_todos(filter=filter_obj)
```

### NotionSyncManager

High-level sync manager:

```python
from opencontext.managers.notion_sync_manager import NotionSyncManager

manager = NotionSyncManager(config)

# Start/stop auto-sync
manager.start_auto_sync()
manager.stop_auto_sync()

# Manual syncing
manager.sync_todos()
manager.sync_activities()
manager.sync_notes()
manager.sync_all()

# Query from Notion
todos = manager.query_notion_todos()

# Get status
status = manager.get_sync_status()
```

## Troubleshooting

### Authentication Errors

**Error**: `Notion API authentication failed`

**Solution**:
- Verify your API key is correct
- Ensure the integration has the required capabilities
- Check that the integration is connected to your databases

### Database Not Found

**Error**: `Database not found` or `Invalid database ID`

**Solution**:
- Verify the database ID is correct
- Ensure the database is shared with your integration
- Check that you copied the full database ID (32 characters)

### Permission Errors

**Error**: `Integration doesn't have permission`

**Solution**:
- Re-share the database with the integration
- Verify integration capabilities include read, update, and insert

### Sync Not Working

**Issue**: Items not appearing in Notion

**Solution**:
- Check that `enabled: true` in config
- Verify database IDs are correct
- Check logs for error messages
- Ensure auto_sync is enabled or manually trigger sync

### Rate Limiting

**Error**: `Rate limit exceeded`

**Solution**:
- Notion has rate limits (3 requests per second)
- Increase `sync_interval` to reduce frequency
- Reduce batch sizes when syncing

## Privacy and Security

- **Local-First**: Notion integration is completely optional. All data works locally without Notion.
- **API Key Security**: Store API keys in `.env` file, never commit to version control
- **Selective Sync**: Choose which data types to sync
- **Manual Control**: Disable auto-sync for full manual control

## Best Practices

1. **Start with manual sync**: Test sync functionality before enabling auto-sync
2. **Use appropriate intervals**: Don't sync too frequently to avoid rate limits
3. **Monitor logs**: Check logs regularly for sync errors
4. **Backup data**: Keep backups of both local and Notion data
5. **Test filters**: Test Notion filters before using in production
6. **Organize databases**: Use consistent property names across databases

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review Notion API documentation: https://developers.notion.com/
- Open an issue on GitHub
- Contact the MineContext team

## Further Reading

- [Notion API Reference](https://developers.notion.com/reference)
- [Notion Database Properties](https://developers.notion.com/reference/property-object)
- [Notion Filters](https://developers.notion.com/reference/post-database-query-filter)
