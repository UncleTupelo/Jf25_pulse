# API Reference Guide

Complete API documentation for the enhanced central data repository features.

## Base URL

```
http://localhost:1733
```

## Authentication

Currently, authentication is disabled by default in development mode. For production, set `api_auth.enabled: true` in config.yaml.

## API Endpoints

### Data Ingestion

#### GET /api/data_ingestion/supported_types

Get list of all supported file types and their processors.

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "supported_types": [
      {
        "extension": ".xlsx",
        "processor": "excel_processor",
        "description": "Advanced Excel processing with cell-level chunking"
      },
      {
        "extension": ".json",
        "processor": "structured_data_processor",
        "description": "JSON/YAML structured data processing"
      },
      ...
    ],
    "total_types": 45
  }
}
```

#### POST /api/data_ingestion/ingest_file

Ingest a single file with automatic type detection.

**Request Body:**
```json
{
  "file_path": "/path/to/file.xlsx",
  "metadata": {
    "project": "analysis",
    "author": "John Doe"
  },
  "tags": ["financial", "Q1-2024"]
}
```

**Response:**
```json
{
  "code": 200,
  "message": "File queued for processing successfully",
  "data": {
    "file_path": "/path/to/file.xlsx",
    "file_name": "file.xlsx",
    "file_type": "excel",
    "metadata": {...},
    "tags": [...]
  }
}
```

#### POST /api/data_ingestion/ingest_batch

Ingest multiple files in batch.

**Request Body:**
```json
{
  "file_paths": [
    "/path/to/file1.py",
    "/path/to/file2.json"
  ],
  "metadata": {},
  "tags": ["batch1"]
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Batch ingestion completed: 2 successful, 0 failed",
  "data": {
    "total": 2,
    "successful": 2,
    "failed": 0,
    "results": [
      {
        "file_path": "/path/to/file1.py",
        "file_name": "file1.py",
        "file_type": "code",
        "status": "queued"
      },
      ...
    ]
  }
}
```

#### POST /api/data_ingestion/ingest_directory

Ingest all files from a directory.

**Request Body:**
```json
{
  "directory_path": "/path/to/project",
  "recursive": true,
  "file_patterns": ["*.py", "*.json"],
  "ignore_patterns": ["**/node_modules/**"],
  "metadata": {},
  "tags": ["project-import"]
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Directory ingestion completed: 15 successful, 0 failed",
  "data": {
    "directory": "/path/to/project",
    "total_files": 15,
    "successful": 15,
    "failed": 0,
    "results": [...]
  }
}
```

#### POST /api/data_ingestion/upload

Upload a file via HTTP multipart form data.

**Form Data:**
- `file`: File upload
- `metadata`: Optional JSON string
- `tags`: Optional JSON string

**Response:**
```json
{
  "code": 200,
  "message": "File uploaded and queued for processing successfully",
  "data": {
    "file_name": "document.pdf",
    "file_path": "./uploads/document.pdf",
    "file_size": 1048576,
    "file_type": "document"
  }
}
```

### Enhanced Search

#### POST /api/search/enhanced

Perform advanced search with multiple filters.

**Request Body:**
```json
{
  "query": "machine learning",
  "top_k": 10,
  "context_types": ["semantic_context"],
  "file_types": ["pdf", "py"],
  "tags": ["ml", "research"],
  "date_from": "2024-01-01T00:00:00",
  "date_to": "2024-12-31T23:59:59",
  "min_relevance": 0.7,
  "sort_by": "relevance"
}
```

**Parameters:**
- `query` (required): Search query string
- `top_k`: Number of results (default: 10)
- `context_types`: Array of context types to filter
- `file_types`: Array of file extensions (without dot)
- `tags`: Array of tags to filter by
- `date_from`: ISO datetime string (inclusive)
- `date_to`: ISO datetime string (inclusive)
- `min_relevance`: Minimum relevance score (0.0-1.0)
- `sort_by`: "relevance", "date", or "importance"

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "results": [
      {
        "id": "context-123",
        "title": "ML Research Paper",
        "summary": "...",
        "distance": 0.15,
        "relevance_score": 0.85,
        "importance": 80,
        "metadata": {
          "file_extension": ".pdf",
          "tags": ["ml", "research"],
          "created_time": "2024-03-15T10:30:00",
          ...
        }
      },
      ...
    ],
    "total": 10,
    "query": "machine learning",
    "filters": {...},
    "sort_by": "relevance"
  }
}
```

#### POST /api/search/by_tags

Search by tags only.

**Request Body:**
```json
{
  "tags": ["machine-learning", "nlp"],
  "top_k": 10,
  "match_all": false
}
```

**Parameters:**
- `tags` (required): Array of tags
- `top_k`: Number of results
- `match_all`: If true, require all tags; if false, match any tag

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "results": [...],
    "total": 8,
    "tags": ["machine-learning", "nlp"],
    "match_all": false
  }
}
```

#### GET /api/search/recent

Get recently added content.

**Query Parameters:**
- `days`: Number of days to look back (default: 7)
- `top_k`: Number of results (default: 20)
- `context_types`: Optional array of context types

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "results": [...],
    "total": 15,
    "days": 7,
    "context_types": null
  }
}
```

#### POST /api/search/similar

Find content similar to a given context.

**Request Body:**
```json
{
  "context_id": "context-123",
  "top_k": 10
}
```

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "results": [...],
    "total": 10,
    "context_id": "context-123"
  }
}
```

#### GET /api/search/facets

Get search facets (aggregations) for filtering.

**Query Parameters:**
- `query`: Optional search query to scope facets
- `context_types`: Optional array of context types

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "facets": {
      "file_types": {
        "pdf": 45,
        "docx": 23,
        "py": 18,
        ...
      },
      "context_types": {
        "semantic_context": 67,
        "activity_context": 13
      },
      "tags": {
        "machine-learning": 34,
        "data-science": 28,
        ...
      },
      "date_ranges": {
        "last_day": 5,
        "last_week": 23,
        "last_month": 47,
        "older": 15
      }
    },
    "query": null,
    "context_types": null
  }
}
```

### Model Registry

#### POST /api/models/register

Register a new ML model.

**Request Body:**
```json
{
  "name": "sentiment-classifier",
  "version": "1.0.0",
  "file_path": "/path/to/model.pt",
  "description": "BERT-based sentiment analysis",
  "use_case": "sentiment-analysis",
  "model_type": "classification",
  "framework": "pytorch",
  "tags": ["nlp", "sentiment", "bert"],
  "metrics": {
    "accuracy": 0.95,
    "f1": 0.94,
    "precision": 0.96,
    "recall": 0.93
  },
  "metadata": {
    "training_data": "IMDB reviews",
    "epochs": 10,
    "batch_size": 32
  },
  "created_by": "user@example.com"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Model registered successfully",
  "data": {
    "model_id": 1,
    "name": "sentiment-classifier",
    "version": "1.0.0"
  }
}
```

#### POST /api/models/upload

Upload and register a model file.

**Form Data:**
- `name` (required): Model name
- `version` (required): Model version
- `file` (required): Model file
- `description`: Model description
- `use_case`: Primary use case
- `model_type`: Type of model
- `framework`: ML framework
- `tags`: JSON array string
- `metrics`: JSON object string
- `created_by`: Creator email/name

**Response:**
```json
{
  "code": 200,
  "message": "Model uploaded and registered successfully",
  "data": {
    "model_id": 1,
    "name": "sentiment-classifier",
    "version": "1.0.0",
    "file_name": "model.pt",
    "file_size": 438902784
  }
}
```

#### GET /api/models/{model_id}

Get model by ID.

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "model": {
      "id": 1,
      "name": "sentiment-classifier",
      "version": "1.0.0",
      "description": "BERT-based sentiment analysis",
      "use_case": "sentiment-analysis",
      "model_type": "classification",
      "framework": "pytorch",
      "file_path": "./persist/models/sentiment-classifier/1.0.0/model.pt",
      "file_size": 438902784,
      "tags": ["nlp", "sentiment", "bert"],
      "metrics": {...},
      "metadata": {...},
      "created_at": "2024-03-15T10:30:00",
      "updated_at": "2024-03-15T10:30:00",
      "created_by": "user@example.com",
      "is_active": 1
    }
  }
}
```

#### GET /api/models/{model_id}/download

Download model file.

**Response:**
Binary file download with appropriate headers.

#### POST /api/models/search

Search models with filters.

**Request Body:**
```json
{
  "query": "sentiment",
  "use_case": "sentiment-analysis",
  "model_type": "classification",
  "framework": "pytorch",
  "tags": ["nlp"],
  "limit": 20
}
```

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "models": [...],
    "total": 5,
    "filters": {
      "query": "sentiment",
      "use_case": "sentiment-analysis",
      ...
    }
  }
}
```

#### GET /api/models

List all active models.

**Query Parameters:**
- `limit`: Maximum number of results (default: 50)

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "models": [...],
    "total": 12
  }
}
```

#### PUT /api/models/{model_id}

Update model metadata.

**Request Body:**
```json
{
  "description": "Updated description",
  "tags": ["nlp", "sentiment", "production"],
  "metrics": {
    "accuracy": 0.96,
    "f1": 0.95
  },
  "metadata": {
    "deployed": true,
    "deployment_date": "2024-03-20"
  }
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Model updated successfully"
}
```

#### DELETE /api/models/{model_id}

Delete a model.

**Query Parameters:**
- `hard_delete`: If true, permanently delete file and record (default: false)

**Response:**
```json
{
  "code": 200,
  "message": "Model deactivated successfully"
}
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "code": 400,
  "message": "Error description",
  "status": 400
}
```

**Common Error Codes:**
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

## Rate Limiting

Currently, there is no rate limiting. For production deployments, consider implementing rate limiting.

## Pagination

For endpoints that return lists, results are limited by the `limit` or `top_k` parameter. Future versions may include cursor-based pagination.

## Webhooks

Webhook support is planned for Phase 5 (Multi-Platform Integration).

## SDK Examples

### Python

```python
import requests

class DataRepositoryClient:
    def __init__(self, base_url="http://localhost:1733"):
        self.base_url = base_url
    
    def ingest_file(self, file_path, tags=None, metadata=None):
        response = requests.post(
            f"{self.base_url}/api/data_ingestion/ingest_file",
            json={
                "file_path": file_path,
                "tags": tags or [],
                "metadata": metadata or {}
            }
        )
        return response.json()
    
    def search(self, query, **filters):
        response = requests.post(
            f"{self.base_url}/api/search/enhanced",
            json={"query": query, **filters}
        )
        return response.json()
    
    def register_model(self, name, version, **kwargs):
        response = requests.post(
            f"{self.base_url}/api/models/register",
            json={"name": name, "version": version, **kwargs}
        )
        return response.json()

# Usage
client = DataRepositoryClient()
result = client.ingest_file("/path/to/file.xlsx", tags=["data"])
```

### JavaScript/TypeScript

```javascript
class DataRepositoryClient {
  constructor(baseUrl = 'http://localhost:1733') {
    this.baseUrl = baseUrl;
  }

  async ingestFile(filePath, tags = [], metadata = {}) {
    const response = await fetch(`${this.baseUrl}/api/data_ingestion/ingest_file`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath, tags, metadata })
    });
    return response.json();
  }

  async search(query, filters = {}) {
    const response = await fetch(`${this.baseUrl}/api/search/enhanced`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, ...filters })
    });
    return response.json();
  }

  async registerModel(name, version, options = {}) {
    const response = await fetch(`${this.baseUrl}/api/models/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, version, ...options })
    });
    return response.json();
  }
}

// Usage
const client = new DataRepositoryClient();
const result = await client.ingestFile('/path/to/file.xlsx', ['data']);
```

## Changelog

### v0.2.0 (Current)
- Added Excel, JSON/YAML, and code processors
- Added unified data ingestion API
- Added metadata extraction service
- Added auto-tagging service
- Added enhanced search with filters
- Added ML model registry

### v0.1.0 (Base)
- Initial MineContext features
- Screenshot capture
- Document processing
- Basic vector search
