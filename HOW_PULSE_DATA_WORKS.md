# How Pulse Data Works in Your MineContext Fork

## Overview

Your MineContext fork works like **ChatGPT Pulse** - it captures, stores, and intelligently uses context from everything you do. Here's how it all works:

## Architecture: The Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  1. Screenshots     2. Chat Messages    3. Documents        │
│  (Your screen)      (Conversations)     (Files you work on) │
└───────────┬─────────────────┬─────────────────┬────────────┘
            │                 │                 │
            ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   PROCESSING LAYER                           │
├─────────────────────────────────────────────────────────────┤
│  • VLM processes images                                      │
│  • Text extracted from documents                             │
│  • Conversations stored with metadata                        │
│  • Everything chunked and embedded                           │
└───────────┬─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  • SQLite: Conversations, messages, metadata                │
│  • ChromaDB: Vector embeddings for semantic search          │
│  • File System: Raw screenshots and documents               │
└───────────┬─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                 CONSUMPTION LAYER (AI Usage)                 │
├─────────────────────────────────────────────────────────────┤
│  • Context Agent: Retrieves relevant past context           │
│  • Completions: GitHub Copilot-like suggestions             │
│  • Generation: Content creation with context awareness      │
└─────────────────────────────────────────────────────────────┘
```

## How Chat Data (Pulse) is Captured

### 1. **Conversation Storage**

When you chat with the AI, here's what happens:

**API Endpoints** (opencontext/server/routes/):
- `POST /api/agent/chat/conversations` - Creates a new conversation
- `POST /api/agent/chat/message` - Stores each message you send
- `GET /api/agent/chat/conversations` - Lists all your past conversations

**Storage Location:**
```
~/.opencontext/
  ├── contexts.db          # SQLite database with conversations
  ├── chroma/              # Vector embeddings for semantic search
  └── screenshots/         # Captured screen images
```

### 2. **What Gets Stored Per Conversation**

```python
Conversation {
  id: int                   # Unique ID
  title: str               # Auto-generated from first message
  user_id: str             # Your user identifier
  created_at: timestamp    # When conversation started
  updated_at: timestamp    # Last activity
  metadata: json           # Extra data (page context, document IDs)
  page_name: str           # Where chat happened (e.g., "home", "creation")
  status: str              # "active" or "archived"
}
```

### 3. **What Gets Stored Per Message**

```python
Message {
  id: int                   # Unique ID
  conversation_id: int      # Links to parent conversation
  role: str                 # "user" or "assistant"
  content: str              # The actual message text
  is_complete: bool         # For streaming messages
  token_count: int          # Token usage tracking
  created_at: timestamp     # When message was sent
  updated_at: timestamp     # Last edit/update
}
```

### 4. **Vector Embeddings (Semantic Search)**

Every piece of text (messages, documents, screenshots) gets:
1. **Chunked** into smaller pieces
2. **Embedded** using your embedding model (configured in config.yaml)
3. **Stored** in ChromaDB with metadata

This allows the AI to find relevant past conversations even if you don't use exact keywords!

## How You.com API Fits In

Now with the You.com integration I just built, you can:

```python
# Use your Joef-JR-API agent to process context
from opencontext.llm.youcom_client import YouComClient

client = YouComClient(api_key=os.getenv("YOUCOM_API_KEY"))

# Send accumulated context to your agent
result = client.run_agent(
    agent_id="76e9f5ab-fd40-4dc8-b88f-5ceb3664d170",
    input_text=f"Based on my recent work: {context_from_minecontext}..."
)
```

## Enabling "Pulse" Features

Edit `config/config.yaml`:

```yaml
# Screenshot capture (like ChatGPT Pulse)
capture:
  screenshot:
    enabled: true              # ← Turn this ON
    capture_interval: 5        # Every 5 seconds
    storage_path: "./screenshots"

  # File monitoring (watches your work files)
  file_monitor:
    enabled: true              # ← Turn this ON
    recursive: true
    monitor_paths: "./doc"     # Directory to watch

  # Vault monitoring (document libraries)
  vault_document_monitor:
    enabled: true              # ← Turn this ON
    monitor_interval: 30
```

## How to Access Your Pulse Data

### From Frontend (TypeScript)

```typescript
import { getConversationList } from '@renderer/services/conversation-service'
import { getMessagesByConversation } from '@renderer/services/messages-service'

// Get all past conversations
const conversations = await getConversationList()

// Get specific conversation messages
const messages = await getMessagesByConversation(conversationId)
```

### From Backend (Python)

```python
from opencontext.storage.global_storage import get_storage

storage = get_storage()

# Search by semantic similarity
results = storage.search_context(
    query="What did I work on yesterday?",
    top_k=10
)

# Get all conversations
conversations = storage.list_conversations()
```

### From API (cURL)

```bash
# List all conversations
curl http://127.0.0.1:1733/api/agent/chat/conversations

# Get specific conversation
curl http://127.0.0.1:1733/api/agent/chat/conversations/123

# Get messages in a conversation
curl http://127.0.0.1:1733/api/agent/chat/123/messages
```

## Real-World Example: How It All Connects

Let's say you're working on a project:

1. **You chat** with the AI about your task
   - ✓ Conversation created in database
   - ✓ Messages stored with timestamps
   - ✓ Text embedded for semantic search

2. **Screenshots capture** your work
   - ✓ Images saved to disk
   - ✓ VLM processes them (extracts text/context)
   - ✓ Embedded and searchable

3. **You edit documents** in your monitored folder
   - ✓ File changes detected
   - ✓ Content extracted and processed
   - ✓ Added to context database

4. **Later, you ask**: *"What was I working on this morning?"*
   - ✓ Context Agent searches embeddings
   - ✓ Finds relevant screenshots, messages, documents
   - ✓ Returns comprehensive summary with sources

5. **Bonus**: Use your Joef-JR-API agent
   ```typescript
   import { runDefaultYouComAgent } from '@renderer/services/youcom-service'

   // Send context to your custom agent
   const summary = await runDefaultYouComAgent(
     "Summarize my work from the captured context"
   )
   ```

6. **New**: Launch an Agent Lightning workflow directly from MineContext
   ```bash
   # Check integration status
   curl http://127.0.0.1:1733/api/agent-lightning/status | jq

   # Trigger your default Lightning agent
   curl -X POST http://127.0.0.1:1733/api/agent-lightning/run \
     -H 'Content-Type: application/json' \
     -d '{
           "input": "Draft a recap using the latest captured context",
           "parameters": {"temperature": 0.3}
         }'
   ```

## Database Schema

Your SQLite database (`~/.opencontext/contexts.db`) has these main tables:

```sql
-- Conversations
CREATE TABLE conversations (
  id INTEGER PRIMARY KEY,
  title TEXT,
  user_id TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  metadata JSON,
  page_name TEXT,
  status TEXT
);

-- Messages
CREATE TABLE messages (
  id INTEGER PRIMARY KEY,
  conversation_id INTEGER,
  role TEXT,
  content TEXT,
  is_complete BOOLEAN,
  token_count INTEGER,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY(conversation_id) REFERENCES conversations(id)
);

-- Context items (screenshots, documents)
CREATE TABLE contexts (
  id TEXT PRIMARY KEY,
  type TEXT,
  source_path TEXT,
  metadata JSON,
  created_at TIMESTAMP,
  -- ... more fields
);
```

## Privacy & Local-First

Everything is stored **locally** by default:
- ✓ Database on your machine
- ✓ Screenshots on your disk
- ✓ Only embeddings/API calls go to cloud (your configured LLM)
- ✓ You.com API only gets what you explicitly send

## Next Steps

1. **Set up You.com API**:
   ```bash
   export YOUCOM_API_KEY="ydc-sk-8f86your-full-key"
   python test_youcom_api.py
   ```

2. **Enable pulse features** in `config/config.yaml`

3. **Start chatting** - everything gets captured automatically!

4. **Query your context**:
   ```bash
   curl -X POST http://127.0.0.1:1733/api/vector_search \
     -H 'Content-Type: application/json' \
     -d '{"query": "what did I work on yesterday?", "top_k": 5}'
   ```

## Summary

Your MineContext fork is a **local-first, context-aware AI assistant** that:
- 📸 Captures everything (screenshots, chats, documents)
- 🧠 Processes and embeds for intelligent retrieval
- 💾 Stores locally in SQLite + ChromaDB
- 🔍 Retrieves relevant context when you need it
- 🚀 Now integrates with your custom You.com agent (Joef-JR-API)!

All your conversations, messages, and context are being captured as you use it - just like ChatGPT Pulse, but open-source and under your control!
