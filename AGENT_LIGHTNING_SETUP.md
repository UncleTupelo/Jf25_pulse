# Agent Lightning integration guide

This guide explains how to install the optional [agent-lightning](https://github.com/UncleTupelo/agent-lightning)
dependency and wire it up to MineContext.

## 1. Install the dependency

The integration is shipped as an optional extra so that existing environments are not forced to
download the Git-based package. Use `uv` or `pip` to install it:

```bash
# Using uv
uv sync --extra agents

# Using pip
pip install -e .[agents]
```

> **Note:** The dependency is pulled directly from GitHub. Make sure the machine running the command
> can reach `https://github.com/UncleTupelo/agent-lightning`.

## 2. Configure MineContext

Update `config/config.yaml` and enable the `agent_lightning` block:

```yaml
agent_lightning:
  enabled: true
  api_key: "${AGENT_LIGHTNING_API_KEY}"
  base_url: "http://127.0.0.1:8001"   # Optional when the Python package is installed locally
  endpoint: "/api/agents/run"
  default_agent: "pulse-lightning"
  workspace_path: "${CONTEXT_PATH:.}/agent_lightning"
  timeout: 60
```

Set the required secrets as environment variables before launching the backend:

```bash
export AGENT_LIGHTNING_API_KEY="replace-with-your-token"
opencontext start --port 1733
```

The configuration supports two execution modes:

1. **Library mode** – When the Python package is installed, the backend will instantiate your
   agent-lightning workspace directly. This is ideal for local experiments.
2. **HTTP mode** – When no Python client is available, requests will be proxied to the REST endpoint
   defined by `base_url + endpoint`. Use this mode when agent-lightning runs in a separate process.

## 3. Call the API

Use the new REST endpoints to interact with your agents:

```bash
# Check status
curl http://127.0.0.1:1733/api/agent-lightning/status | jq

# Run an agent
curl -X POST http://127.0.0.1:1733/api/agent-lightning/run \
  -H 'Content-Type: application/json' \
  -d '{
        "agent": "pulse-lightning",
        "input": "Create a project update based on my recent captures",
        "parameters": {"temperature": 0.4}
      }'
```

The response contains the raw payload returned by agent-lightning together with metadata about the
transport used (`library` vs `http`).

## 4. Programmatic usage

You can also call the integration from Python code by reusing the new client:

```python
from opencontext.llm.agent_lightning_client import AgentLightningClient

client = AgentLightningClient(
    api_key="your-token",
    base_url="http://127.0.0.1:8001",
    default_agent="pulse-lightning",
)

result = client.run_agent(agent_id=None, input_text="Summarize today's work")
print(result)
```

This helper automatically switches between the local library and HTTP transport depending on what is available.
