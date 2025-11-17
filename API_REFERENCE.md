# Cloud Integrations API Reference

This document provides a quick reference for the cloud integrations API endpoints.

## Base URL

```
http://localhost:1733
```

## Authentication

All API endpoints require authentication (if enabled in config). Include the API key in the request headers:

```
X-API-Key: your_api_key
```

## Endpoints

### 1. Trigger Manual Sync

Manually trigger a sync for a specific integration.

**Endpoint:** `POST /api/integrations/sync`

**Request Body:**
```json
{
  "integration_name": "googledrivecapture"
}
```

**Supported Integration Names:**
- `googledrivecapture`
- `icloudcapture`
- `onedrivecapture`
- `notioncapture`
- `chatgptcapture`
- `perplexitycapture`
- `fileuploadcapture`

**Response:**
```json
{
  "code": 0,
  "data": {
    "integration": "googledrivecapture",
    "captured_items": 5,
    "message": "Successfully synced 5 items"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:1733/api/integrations/sync \
  -H "Content-Type: application/json" \
  -d '{"integration_name": "googledrivecapture"}'
```

---

### 2. Get All Integrations Status

Get status information for all configured integrations.

**Endpoint:** `GET /api/integrations/status`

**Response:**
```json
{
  "code": 0,
  "data": {
    "integrations": [
      {
        "name": "googledrivecapture",
        "enabled": true,
        "running": true,
        "last_sync_time": "2025-01-16T10:30:00",
        "status": {
          "authenticated": true,
          "synced_files_count": 42
        }
      }
    ]
  }
}
```

**Example:**
```bash
curl http://localhost:1733/api/integrations/status
```

---

### 3. Get Specific Integration Status

Get detailed status for a specific integration.

**Endpoint:** `GET /api/integrations/{integration_name}/status`

**Path Parameters:**
- `integration_name` - Name of the integration (lowercase)

**Response:**
```json
{
  "code": 0,
  "data": {
    "name": "googledrivecapture",
    "enabled": true,
    "running": true,
    "status": {
      "authenticated": true,
      "last_sync_time": "2025-01-16T10:30:00",
      "synced_files_count": 42,
      "sync_folders": ["Documents", "Work"],
      "file_types": ["*.pdf", "*.docx"]
    }
  }
}
```

**Example:**
```bash
curl http://localhost:1733/api/integrations/googledrivecapture/status
```

---

### 4. Upload File

Upload a file for context ingestion.

**Endpoint:** `POST /api/integrations/upload`

**Request:** Multipart form data

**Form Fields:**
- `file` - The file to upload

**Response:**
```json
{
  "code": 0,
  "data": {
    "file_name": "document.pdf",
    "file_size": 1024000,
    "content_type": "application/pdf",
    "message": "File uploaded successfully"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:1733/api/integrations/upload \
  -F "file=@/path/to/document.pdf"
```

---

### 5. Start Integration

Start a specific integration component.

**Endpoint:** `POST /api/integrations/{integration_name}/start`

**Path Parameters:**
- `integration_name` - Name of the integration to start

**Response:**
```json
{
  "code": 0,
  "data": {
    "message": "Integration 'googledrivecapture' started successfully"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:1733/api/integrations/googledrivecapture/start
```

---

### 6. Stop Integration

Stop a specific integration component.

**Endpoint:** `POST /api/integrations/{integration_name}/stop`

**Path Parameters:**
- `integration_name` - Name of the integration to stop

**Response:**
```json
{
  "code": 0,
  "data": {
    "message": "Integration 'googledrivecapture' stopped successfully"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:1733/api/integrations/googledrivecapture/stop
```

---

## Error Responses

All endpoints may return error responses with appropriate HTTP status codes:

**404 Not Found:**
```json
{
  "detail": "Integration 'unknown' not found"
}
```

**400 Bad Request:**
```json
{
  "detail": "Integration 'googledrivecapture' is not running"
}
```

**500 Internal Server Error:**
```json
{
  "code": 500,
  "status": 500,
  "message": "Sync failed: connection timeout"
}
```

## Common Use Cases

### 1. Check if Integration is Running

```bash
# Get status
curl http://localhost:1733/api/integrations/googledrivecapture/status | jq '.data.running'
```

### 2. Sync All Integrations

```bash
# Loop through all integrations
for integration in googledrivecapture icloudcapture onedrivecapture notioncapture; do
  curl -X POST http://localhost:1733/api/integrations/sync \
    -H "Content-Type: application/json" \
    -d "{\"integration_name\": \"$integration\"}"
  echo ""
done
```

### 3. Upload Multiple Files

```bash
# Upload all PDFs in a directory
for file in /path/to/docs/*.pdf; do
  curl -X POST http://localhost:1733/api/integrations/upload \
    -F "file=@$file"
  echo ""
done
```

### 4. Monitor Integration Status

```bash
# Continuously monitor status
watch -n 10 'curl -s http://localhost:1733/api/integrations/status | jq'
```

## Response Codes

- `0` - Success
- `400` - Bad Request (invalid parameters, integration not running, etc.)
- `404` - Not Found (integration doesn't exist)
- `500` - Internal Server Error (sync failed, authentication error, etc.)

## Notes

- All timestamps are in ISO 8601 format
- Integration names are case-insensitive (converted to lowercase)
- File upload size limits are configurable in `config.yaml`
- Sync operations are asynchronous and return immediately
- Status endpoints provide real-time information
