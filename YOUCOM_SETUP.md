# You.com API Setup - Joef-JR-API

Quick setup guide for your You.com API integration.

## Your Configuration

- **Agent Name:** Joef-JR-API
- **Agent ID:** `76e9f5ab-fd40-4dc8-b88f-5ceb3664d170` ✓ (Already configured)
- **API Key:** `ydc-sk-8f86...ab` (You need to set the full key)

## Setup Steps

### 1. Set Your API Key

Replace `your-full-api-key-here` with your complete API key:

```bash
export YOUCOM_API_KEY="ydc-sk-8f86your-full-key-here"
```

### 2. Test the Integration

Run the test script:

```bash
python test_youcom_api.py
```

Expected output:
```
============================================================
You.com API Test - Joef-JR-API
============================================================

🔧 Testing You.com API Integration
   Agent: Joef-JR-API
   Agent ID: 76e9f5ab-fd40-4dc8-b88f-5ceb3664d170
   API Key: ydc-sk-8f8...xxxx

✓ Client initialized successfully

📤 Sending test request to Joef-JR-API...
✓ Request successful!

📥 Response:
------------------------------------------------------------
[Agent response will appear here]
------------------------------------------------------------

============================================================
✅ All tests passed!
============================================================
```

## Usage Examples

### Python

```python
from opencontext.llm.youcom_client import YouComClient

# Initialize client (uses YOUCOM_API_KEY from environment)
client = YouComClient(api_key="ydc-sk-8f86...")

# Run your Joef-JR-API agent
result = client.run_agent(
    agent_id="76e9f5ab-fd40-4dc8-b88f-5ceb3664d170",
    input_text="Your question or input here"
)

print(result)
```

### cURL

```bash
curl -X POST http://127.0.0.1:1733/api/youcom/agent/run \
  -H 'Content-Type: application/json' \
  -d '{
    "input": "Your question here",
    "stream": false
  }'
```

Note: When using the API endpoint, the default agent (Joef-JR-API) is automatically used.

### TypeScript (Frontend)

```typescript
import { runDefaultYouComAgent } from '@renderer/services/youcom-service'

// Simple usage - uses your Joef-JR-API agent automatically
const result = await runDefaultYouComAgent("Your question here")
console.log(result)
```

## Checking Status

Verify your configuration:

```bash
curl http://127.0.0.1:1733/api/youcom/status
```

Should return:
```json
{
  "enabled": true,
  "api_key_configured": true,
  "default_agent_id": "76e9f5ab-fd40-4dc8-b88f-5ceb3664d170",
  "base_url": "https://api-you.com",
  "ready": true
}
```

## Troubleshooting

### API Key Not Configured

If you see this error:
```
You.com API key not configured. Please set YOUCOM_API_KEY environment variable
```

Make sure you've set the environment variable:
```bash
echo $YOUCOM_API_KEY  # Should show your key
```

### Agent Not Found

If the agent ID is incorrect, you'll get a 400 error. Your agent ID is already configured correctly: `76e9f5ab-fd40-4dc8-b88f-5ceb3664d170`

## Permanent Setup

To make the API key permanent, add it to your shell profile:

**For bash (~/.bashrc or ~/.bash_profile):**
```bash
echo 'export YOUCOM_API_KEY="ydc-sk-8f86your-full-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**For zsh (~/.zshrc):**
```bash
echo 'export YOUCOM_API_KEY="ydc-sk-8f86your-full-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## Next Steps

1. Set your full API key
2. Run `python test_youcom_api.py` to verify
3. Start using the Joef-JR-API agent in your application!

For more detailed API documentation, see `YOUCOM_API_USAGE.md`.
