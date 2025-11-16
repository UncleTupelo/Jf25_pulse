# You.com API Integration

This document describes how to use the You.com API integration in MineContext.

## Configuration

1. Set the `YOUCOM_API_KEY` environment variable with your You.com API key:

```bash
export YOUCOM_API_KEY="your-api-key-here"
```

2. (Optional) Update the configuration in `config/config.yaml` if needed:

```yaml
youcom_api:
  enabled: true
  base_url: "https://api-you.com"
  api_key: "${YOUCOM_API_KEY}"
  default_agent_id: "76e9f5ab-fd40-4dc8-b88f-5ceb3664d170"
```

## Backend Usage

### Python Client

```python
from opencontext.llm.youcom_client import YouComClient

# Initialize client
client = YouComClient(api_key="your-api-key")

# Run an agent
result = client.run_agent(
    agent_id="76e9f5ab-fd40-4dc8-b88f-5ceb3664d170",
    input_text="What is the weather today?",
    stream=False
)

print(result)
```

### Async Usage

```python
import asyncio
from opencontext.llm.youcom_client import YouComClient

async def main():
    client = YouComClient(api_key="your-api-key")

    result = await client.run_agent_async(
        agent_id="76e9f5ab-fd40-4dc8-b88f-5ceb3664d170",
        input_text="What is the weather today?",
        stream=False
    )

    print(result)

asyncio.run(main())
```

## API Endpoints

### Run Agent

**Endpoint:** `POST /api/youcom/agent/run`

**Request Body:**
```json
{
  "agent_id": "76e9f5ab-fd40-4dc8-b88f-5ceb3664d170",  // Optional, uses default if not provided
  "input": "Your input text here",
  "stream": false
}
```

**Response:**
```json
{
  "code": 200,
  "status": 200,
  "message": "success",
  "data": {
    "success": true,
    "agent_id": "76e9f5ab-fd40-4dc8-b88f-5ceb3664d170",
    "result": {
      // You.com API response data
    }
  }
}
```

### Check Status

**Endpoint:** `GET /api/youcom/status`

**Response:**
```json
{
  "code": 200,
  "status": 200,
  "message": "success",
  "data": {
    "enabled": true,
    "api_key_configured": true,
    "default_agent_id": "76e9f5ab-fd40-4dc8-b88f-5ceb3664d170",
    "base_url": "https://api-you.com",
    "ready": true
  }
}
```

## Frontend Usage

### TypeScript/React

```typescript
import { runYouComAgent, getYouComStatus, runDefaultYouComAgent } from '@renderer/services/youcom-service'

// Check if You.com API is configured
const status = await getYouComStatus()
console.log('You.com API ready:', status?.ready)

// Run an agent with specific ID
const result = await runYouComAgent({
  agent_id: "76e9f5ab-fd40-4dc8-b88f-5ceb3664d170",
  input: "What is the weather today?",
  stream: false
})

console.log('Agent result:', result)

// Run with default agent
const defaultResult = await runDefaultYouComAgent("What is the weather today?")
console.log('Default agent result:', defaultResult)
```

## cURL Examples

### Run Agent

```bash
curl --request POST \
  --url 'http://127.0.0.1:1733/api/youcom/agent/run' \
  --header 'Content-Type: application/json' \
  --data '{
    "agent_id": "76e9f5ab-fd40-4dc8-b88f-5ceb3664d170",
    "input": "What is the weather today?",
    "stream": false
  }'
```

### Check Status

```bash
curl --request GET \
  --url 'http://127.0.0.1:1733/api/youcom/status' \
  --header 'Content-Type: application/json'
```

## Error Handling

The API will return appropriate HTTP status codes and error messages:

- `400 Bad Request` - Missing required parameters or invalid agent_id
- `500 Internal Server Error` - API key not configured or You.com API errors
- `503 Service Unavailable` - You.com API integration is disabled in config

Example error response:
```json
{
  "code": 500,
  "status": 500,
  "message": "You.com API key not configured. Please set YOUCOM_API_KEY environment variable",
  "data": null
}
```

## Dependencies

The following Python package is required and has been added to `pyproject.toml`:

- `httpx` - HTTP client for making API requests

Install dependencies:
```bash
pip install -e .
# or with uv:
uv pip install -e .
```
