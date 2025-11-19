# Perplexity AI Integration Setup Guide

This guide explains how to set up and use the Perplexity AI integration in MineContext. The integration allows you to sync your conversation history and research queries from Perplexity AI to enrich your local context.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup Steps](#setup-steps)
  - [1. Get Perplexity API Access](#1-get-perplexity-api-access)
  - [2. Configure MineContext](#2-configure-minecontext)
  - [3. Enable Sync](#3-enable-sync)
- [Features](#features)
- [Usage](#usage)
- [Configuration Options](#configuration-options)
- [Troubleshooting](#troubleshooting)

## Overview

The Perplexity AI integration provides:

1. **Conversation Sync**: Automatically sync your Perplexity AI conversation history
2. **Research Context**: Import queries, answers, and source references
3. **Automatic Syncing**: Configurable sync intervals to keep data up-to-date
4. **Privacy**: Local-first design - Perplexity sync is completely optional

## Prerequisites

- MineContext installed and configured
- A Perplexity AI account (free or Pro)
- Perplexity API access (currently in beta)

## Setup Steps

### 1. Get Perplexity API Access

Perplexity AI is gradually rolling out API access. To get your API key:

1. Visit [Perplexity AI API](https://www.perplexity.ai/settings/api) (when available)
2. Sign in with your Perplexity account
3. Navigate to API settings
4. Generate a new API key
5. Copy and securely store your API key

**Note**: As of now, Perplexity AI's API may have limited availability. Check their official documentation or contact their support for API access.

**Alternative Methods**:
- **Manual Export**: Perplexity AI may offer conversation export features
- **Browser Extension**: Use browser automation to capture conversations
- **Beta Access**: Join Perplexity's developer beta program if available

### 2. Configure MineContext

#### Update Environment Variables

Edit your `.env` file (or create from `.env.example`):

```bash
# Perplexity AI Integration
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

#### Update config.yaml

In `config/config.yaml`, find the `capture` section and update the Perplexity configuration:

```yaml
capture:
  # AI conversation integrations
  perplexity:
    enabled: true  # Set to true to enable
    api_key: "${PERPLEXITY_API_KEY}"
    sync_interval: 600  # Sync every 10 minutes (in seconds)
    sync_recent_days: 30  # Sync last 30 days of conversations
```

### 3. Enable Sync

Once configured, restart MineContext. The integration will:

1. Start syncing conversations automatically based on `sync_interval`
2. Capture queries, answers, and source references
3. Store conversations as searchable context in your local database

## Features

### 1. Automatic Syncing

When enabled, MineContext will automatically sync your Perplexity conversations at the configured interval:

```yaml
sync_interval: 600  # Sync every 10 minutes
```

### 2. Historical Data Sync

Control how far back to sync conversations:

```yaml
sync_recent_days: 30  # Sync last 30 days
```

### 3. Rich Context Capture

For each conversation thread, MineContext captures:
- **Query**: Your original question
- **Answer**: Perplexity's AI-generated response
- **Sources**: All reference links and citations
- **Timestamp**: When the conversation occurred

### 4. Searchable Content

All synced Perplexity conversations become part of your local context and are:
- Searchable through MineContext's vector search
- Available for AI-assisted Q&A
- Included in summaries and activity reports

## Usage

### Viewing Synced Conversations

Once syncing is enabled, your Perplexity conversations will appear in:

1. **Chat Interface**: Query your Perplexity history through the chat
2. **Search**: Full-text and semantic search across all conversations
3. **Activity Reports**: Perplexity queries included in daily/weekly summaries

### Manual Sync Trigger

You can manually trigger a sync via the API:

```bash
curl -X POST http://localhost:1733/api/integrations/sync \
  -H "Content-Type: application/json" \
  -d '{"integration_name": "perplexitycapture"}'
```

### Check Sync Status

Get the current sync status:

```bash
curl http://localhost:1733/api/integrations/perplexitycapture/status
```

Response includes:
- Last sync time
- Number of synced threads
- Sync configuration

## Configuration Options

### Perplexity Capture Config

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable Perplexity integration |
| `api_key` | string | - | Perplexity API key |
| `sync_interval` | integer | `600` | Sync interval in seconds (10 minutes) |
| `sync_recent_days` | integer | `30` | Number of recent days to sync |

## Troubleshooting

### API Not Available

**Issue**: Perplexity API is not yet publicly available

**Solutions**:
1. **Check Availability**: Visit [Perplexity's website](https://www.perplexity.ai/) for API updates
2. **Join Beta**: Sign up for their developer beta program
3. **Manual Export**: Use Perplexity's export feature if available
4. **Alternative Integration**: Consider using the ChatGPT integration for AI conversation tracking

### Authentication Errors

**Error**: `Perplexity API authentication failed`

**Solutions**:
- Verify your API key is correct and active
- Check if your API key has the required permissions
- Ensure you're not exceeding rate limits

### No Conversations Syncing

**Issue**: Integration enabled but no data appears

**Solutions**:
- Check that `enabled: true` in config
- Verify API key is set in `.env` file
- Check logs for error messages: `tail -f ~/Library/Application\ Support/MineContext/Data/logs/opencontext.log`
- Ensure you have conversations in the specified date range (`sync_recent_days`)

### Rate Limiting

**Error**: `Rate limit exceeded`

**Solutions**:
- Increase `sync_interval` to reduce sync frequency
- Reduce `sync_recent_days` to sync less historical data
- Check Perplexity's rate limit documentation

### Missing Environment Variable

**Error**: Environment variable not found

**Solutions**:
- Ensure `.env` file exists in project root
- Verify `PERPLEXITY_API_KEY` is set in `.env`
- Restart MineContext after updating `.env`

## Privacy and Security

- **Local-First**: All synced data is stored locally on your device
- **Optional**: Perplexity integration is completely optional
- **API Key Security**: Store your API key in `.env` file, never commit to version control
- **Data Control**: You control what gets synced and can disable at any time

## Best Practices

1. **Start with manual sync**: Test the integration before enabling auto-sync
2. **Reasonable intervals**: Don't sync too frequently (recommended: 10-30 minutes)
3. **Monitor API usage**: Be aware of Perplexity's API quotas and pricing
4. **Limit sync window**: Use `sync_recent_days` to avoid unnecessary API calls
5. **Check logs regularly**: Monitor logs for sync errors or issues
6. **Keep credentials secure**: Never share your API key or commit it to version control

## API Reference

### PerplexityCapture Component

The capture component handles all Perplexity integration:

```python
from opencontext.context_capture.perplexity_capture import PerplexityCapture

# Initialize
capture = PerplexityCapture()

# Configure
config = {
    "enabled": True,
    "api_key": "your_api_key",
    "sync_interval": 600,
    "sync_recent_days": 30
}
capture.initialize(config)

# Start syncing
capture.start()

# Get status
status = capture.get_status()
print(status)

# Stop syncing
capture.stop()
```

### Data Format

Each synced conversation is stored as a context with:

```python
{
    "source": "PERPLEXITY",
    "content_format": "TEXT",
    "raw_data": "Query: ...\n\nAnswer: ...\n\nSources:\n...",
    "metadata": {
        "thread_id": "unique_thread_id",
        "query": "original question",
        "created_at": "ISO timestamp",
        "source_count": number_of_sources
    }
}
```

## Integration Roadmap

Current implementation status:

- [x] Base integration framework
- [x] Configuration schema
- [x] Data capture structure
- [ ] Live API integration (waiting for Perplexity API availability)
- [ ] Real-time sync support
- [ ] Advanced filtering options

## Known Limitations

1. **API Availability**: Perplexity's official API is not yet widely available
2. **Placeholder Implementation**: Some methods are placeholders waiting for API access
3. **No Real-time Updates**: Currently relies on polling-based sync
4. **Export Required**: May need manual export until official API is available

## Alternative Solutions

While waiting for official API access:

1. **Manual Export**: Export conversations from Perplexity and upload via file upload
2. **Browser Extension**: Use a custom extension to capture conversations
3. **Screen Capture**: Use MineContext's screenshot feature to capture Perplexity usage
4. **ChatGPT Integration**: Use ChatGPT integration for similar AI conversation tracking

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review Perplexity AI documentation: https://www.perplexity.ai/
- Check for API updates at Perplexity's website
- Open an issue on GitHub
- Contact the MineContext team

## Further Reading

- [CLOUD_INTEGRATIONS.md](CLOUD_INTEGRATIONS.md) - Overview of all cloud integrations
- [NOTION_SETUP.md](NOTION_SETUP.md) - Similar setup guide for Notion
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- Perplexity AI Documentation: https://www.perplexity.ai/

## Updates and Changes

This integration is under active development. Check back for updates as Perplexity's API becomes more widely available.

**Last Updated**: 2025-11-19
