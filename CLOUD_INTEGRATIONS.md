# Cloud Integrations Guide

This guide provides detailed instructions for enabling and configuring cloud integrations in MineContext.

## Table of Contents

- [Overview](#overview)
- [Google Drive Integration](#google-drive-integration)
- [iCloud Integration](#icloud-integration)
- [OneDrive Integration](#onedrive-integration)
- [Notion Integration](#notion-integration)
- [ChatGPT Integration](#chatgpt-integration)
- [Perplexity AI Integration](#perplexity-ai-integration)
- [File Upload](#file-upload)
- [API Usage](#api-usage)
- [Troubleshooting](#troubleshooting)

## Overview

MineContext now supports multiple cloud storage and productivity tool integrations to automatically ingest context from various sources. Each integration can be configured independently and supports both automatic syncing and manual triggers.

### Supported Integrations

- **Cloud Storage**: Google Drive, iCloud, OneDrive
- **Productivity Tools**: Notion
- **AI Conversations**: ChatGPT, Perplexity AI
- **File Upload**: Manual file uploads via API or CLI

## Google Drive Integration

### Prerequisites

1. A Google Cloud Platform account
2. Google Drive API enabled
3. OAuth2 credentials (Client ID and Client Secret)

### Setup Steps

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Drive API

2. **Create OAuth2 Credentials**
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Configure the consent screen if prompted
   - Choose "Desktop application" as the application type
   - Download the credentials JSON file

3. **Configure MineContext**

   Edit `config/config.yaml`:

   ```yaml
   capture:
     google_drive:
       enabled: true
       client_id: "YOUR_CLIENT_ID"
       client_secret: "YOUR_CLIENT_SECRET"
       api_key: "YOUR_API_KEY"  # Optional
       sync_interval: 300  # Sync every 5 minutes
       sync_folders:  # Optional: Specific folders to sync
         - "Work Documents"
         - "Personal Notes"
       file_types:  # File patterns to sync
         - "*.txt"
         - "*.md"
         - "*.pdf"
         - "*.docx"
   ```

4. **Set Environment Variables (Alternative)**

   ```bash
   export GOOGLE_DRIVE_CLIENT_ID="your_client_id"
   export GOOGLE_DRIVE_CLIENT_SECRET="your_client_secret"
   export GOOGLE_DRIVE_API_KEY="your_api_key"
   ```

### Notes

- First sync may take longer as it processes all files
- Large files are handled with streaming to minimize memory usage
- Google Docs, Sheets, and Slides are exported to compatible formats

## iCloud Integration

### Prerequisites

1. Apple ID with iCloud Drive enabled
2. Two-factor authentication configured
3. App-specific password (recommended)

### Setup Steps

1. **Generate App-Specific Password**
   - Go to [appleid.apple.com](https://appleid.apple.com/)
   - Sign in and navigate to Security section
   - Generate an app-specific password

2. **Configure MineContext**

   Edit `config/config.yaml`:

   ```yaml
   capture:
     icloud:
       enabled: true
       apple_id: "your.email@icloud.com"
       password: "YOUR_APP_SPECIFIC_PASSWORD"
       sync_interval: 300
       sync_folders:
         - "Documents"
         - "Desktop"
       file_types:
         - "*.txt"
         - "*.md"
         - "*.pdf"
   ```

3. **Set Environment Variables (Alternative)**

   ```bash
   export ICLOUD_APPLE_ID="your.email@icloud.com"
   export ICLOUD_PASSWORD="your_app_specific_password"
   ```

### Notes

- Uses pyicloud library (install separately: `pip install pyicloud`)
- May require manual authentication on first run
- Respects iCloud Drive folder structure

## OneDrive Integration

### Prerequisites

1. Microsoft account with OneDrive access
2. Azure AD application registration
3. Client ID and Client Secret

### Setup Steps

1. **Register Azure AD Application**
   - Go to [Azure Portal](https://portal.azure.com/)
   - Navigate to "Azure Active Directory" > "App registrations"
   - Click "New registration"
   - Set redirect URI to `http://localhost:8080`
   - Create a client secret under "Certificates & secrets"

2. **Grant API Permissions**
   - In your app registration, go to "API permissions"
   - Add Microsoft Graph permissions:
     - `Files.Read.All`
     - `Files.ReadWrite.All` (if write access needed)

3. **Configure MineContext**

   Edit `config/config.yaml`:

   ```yaml
   capture:
     onedrive:
       enabled: true
       client_id: "YOUR_CLIENT_ID"
       client_secret: "YOUR_CLIENT_SECRET"
       tenant_id: "YOUR_TENANT_ID"  # Optional, defaults to "common"
       sync_interval: 300
       sync_folders:
         - "Documents"
         - "Projects"
       file_types:
         - "*.txt"
         - "*.md"
         - "*.docx"
         - "*.xlsx"
   ```

4. **Set Environment Variables (Alternative)**

   ```bash
   export ONEDRIVE_CLIENT_ID="your_client_id"
   export ONEDRIVE_CLIENT_SECRET="your_client_secret"
   export ONEDRIVE_TENANT_ID="your_tenant_id"
   ```

### Notes

- Uses Microsoft Graph API
- Supports both personal and business accounts
- First run requires browser-based authentication

## Notion Integration

### Prerequisites

1. Notion account
2. Notion Integration API token

### Setup Steps

1. **Create Notion Integration**
   - Go to [Notion Integrations](https://www.notion.so/my-integrations)
   - Click "New integration"
   - Name your integration (e.g., "MineContext")
   - Select the workspace to integrate with
   - Copy the "Internal Integration Token"

2. **Share Databases/Pages with Integration**
   - For each database or page you want to sync:
     - Click the "..." menu
     - Select "Add connections"
     - Choose your integration

3. **Get Database IDs (Optional)**
   - Open a database in Notion
   - Copy the URL: `https://notion.so/workspace/DATABASE_ID?v=...`
   - The `DATABASE_ID` is the 32-character string

4. **Configure MineContext**

   Edit `config/config.yaml`:

   ```yaml
   capture:
     notion:
       enabled: true
       api_key: "YOUR_INTEGRATION_TOKEN"
       sync_interval: 300
       sync_databases:  # Optional: Specific databases to sync
         - "database_id_1"
         - "database_id_2"
       sync_pages: true  # Sync all accessible pages
   ```

5. **Set Environment Variables (Alternative)**

   ```bash
   export NOTION_API_KEY="your_integration_token"
   ```

### Notes

- Only syncs databases/pages shared with the integration
- Supports rich text formatting conversion to markdown
- Handles nested pages and linked databases

## ChatGPT Integration

### Prerequisites

1. OpenAI account
2. OpenAI API key

### Setup Steps

1. **Get OpenAI API Key**
   - Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy and store it securely

2. **Configure MineContext**

   Edit `config/config.yaml`:

   ```yaml
   capture:
     chatgpt:
       enabled: true
       api_key: "YOUR_OPENAI_API_KEY"
       sync_interval: 600  # Sync every 10 minutes
       sync_recent_days: 30  # Sync last 30 days of conversations
   ```

3. **Set Environment Variables (Alternative)**

   ```bash
   export OPENAI_API_KEY="your_api_key"
   ```

### Notes

- Currently requires export/import of conversation data
- OpenAI doesn't provide official API for conversation history
- Alternative: Manual export from ChatGPT settings

## Perplexity AI Integration

### Prerequisites

1. Perplexity AI account
2. API access (if available)

### Setup Steps

1. **Get Perplexity API Key**
   - Check Perplexity AI documentation for API access
   - Generate or copy your API key

2. **Configure MineContext**

   Edit `config/config.yaml`:

   ```yaml
   capture:
     perplexity:
       enabled: true
       api_key: "YOUR_PERPLEXITY_API_KEY"
       sync_interval: 600
       sync_recent_days: 30
   ```

3. **Set Environment Variables (Alternative)**

   ```bash
   export PERPLEXITY_API_KEY="your_api_key"
   ```

### Notes

- Implementation depends on Perplexity AI API availability
- Captures queries, answers, and source references

## File Upload

The file upload feature allows manual ingestion of files via API or command-line.

### Configuration

Edit `config/config.yaml`:

```yaml
capture:
  file_upload:
    enabled: true
    storage_path: "${CONTEXT_PATH:.}/uploads"
    max_file_size_mb: 100
    allowed_extensions:
      - ".txt"
      - ".md"
      - ".pdf"
      - ".docx"
      - ".xlsx"
      - ".json"
      - ".jpg"
      - ".png"
```

### Usage

See [API Usage](#api-usage) section for file upload endpoint details.

## API Usage

### Manual Sync Trigger

Trigger a sync for any integration:

```bash
curl -X POST http://localhost:1733/api/integrations/sync \
  -H "Content-Type: application/json" \
  -d '{"integration_name": "googledrivecapture"}'
```

### Get Integration Status

Get status of all integrations:

```bash
curl http://localhost:1733/api/integrations/status
```

Get status of specific integration:

```bash
curl http://localhost:1733/api/integrations/googledrivecapture/status
```

### Upload File

Upload a file via API:

```bash
curl -X POST http://localhost:1733/api/integrations/upload \
  -F "file=@/path/to/your/file.pdf"
```

### Start/Stop Integration

Start an integration:

```bash
curl -X POST http://localhost:1733/api/integrations/googledrivecapture/start
```

Stop an integration:

```bash
curl -X POST http://localhost:1733/api/integrations/googledrivecapture/stop
```

## Troubleshooting

### Common Issues

**Integration not starting**
- Check configuration in `config.yaml`
- Verify API credentials are correct
- Check logs in `~/Library/Application Support/MineContext/Data/logs/`

**Authentication failures**
- Regenerate API keys/tokens
- Ensure OAuth2 flow completed successfully
- Check firewall/network settings

**Files not syncing**
- Verify `sync_folders` and `file_types` filters
- Check file permissions in cloud storage
- Review sync_interval setting

**High API usage**
- Increase `sync_interval` to reduce frequency
- Limit `sync_folders` to specific directories
- Adjust `file_types` to include only necessary formats

### Getting Help

- Check logs: `tail -f ~/Library/Application\ Support/MineContext/Data/logs/opencontext.log`
- Enable debug mode in config: `logging.level: DEBUG`
- Report issues: [GitHub Issues](https://github.com/volcengine/MineContext/issues)

## Best Practices

1. **Start with manual sync** to test configuration before enabling automatic syncing
2. **Use specific folders** instead of syncing entire drive to reduce processing time
3. **Set reasonable sync_intervals** (5-10 minutes recommended) to avoid rate limiting
4. **Monitor API usage** to stay within quota limits
5. **Use file type filters** to ingest only relevant document types
6. **Keep credentials secure** using environment variables instead of config file
7. **Regular backups** of your MineContext data directory
