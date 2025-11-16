# Enhanced Central Data Repository Features

This document describes the new features added to transform MineContext/Jf25_pulse into a comprehensive central data repository with multi-source integration.

## Table of Contents

- [Overview](#overview)
- [Phase 1: Data Ingestion](#phase-1-data-ingestion)
- [Phase 2: Context Enrichment](#phase-2-context-enrichment)
- [Phase 3: Model Integration](#phase-3-model-integration)
- [Phase 4: Enhanced Search](#phase-4-enhanced-search)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Examples](#examples)

## Overview

The enhanced system provides:

1. **Universal Data Ingestion** - Ingest files of any type with automatic processing
2. **Intelligent Metadata Extraction** - Automatic metadata and tag generation
3. **ML Model Registry** - Store and manage ML models with versioning
4. **Advanced Search** - Multi-filter search across all data types
5. **Comprehensive APIs** - RESTful APIs for all operations

## Phase 1: Data Ingestion

### New File Processors

#### ExcelProcessor
Processes Excel files (.xlsx, .xls) with advanced features:

- **Sheet-level processing** - Each sheet processed independently
- **Cell-level chunking** - Configurable row batching (default: 100 rows/chunk)
- **Formula extraction** - Captures Excel formulas with cell references
- **Comment extraction** - Extracts cell comments
- **Table detection** - Identifies Excel table structures
- **Summary statistics** - Calculates stats for numeric columns

**Configuration:**
```yaml
processing:
  excel_processor:
    enabled: true
    max_rows_per_chunk: 100
    extract_formulas: true
    extract_comments: true
    detect_tables: true
```

#### StructuredDataProcessor
Processes JSON and YAML files (.json, .yaml, .yml, .jsonl):

- **Structure preservation** - Maintains hierarchical structure
- **Schema extraction** - Automatically extracts data schema
- **Path-based indexing** - Each data path is indexed
- **Nested object handling** - Intelligently chunks complex structures
- **Array chunking** - Configurable batch size for large arrays

**Configuration:**
```yaml
processing:
  structured_data_processor:
    enabled: true
    max_depth: 10
    max_array_items_per_chunk: 50
    preserve_structure: true
```

#### CodeProcessor
Processes source code files (Python, JavaScript, Java, Go, C++, etc.):

- **Multi-language support** - 15+ programming languages
- **Syntax-aware chunking** - Chunks by functions/classes
- **Function detection** - Extracts function names and signatures
- **Class detection** - Identifies class definitions
- **Import extraction** - Lists dependencies
- **Comment extraction** - Captures inline and block comments

**Configuration:**
```yaml
processing:
  code_processor:
    enabled: true
    max_lines_per_chunk: 100
    extract_functions: true
    extract_classes: true
    extract_imports: true
    extract_comments: true
```

**Supported Languages:**
- Python (.py)
- JavaScript/TypeScript (.js, .jsx, .ts, .tsx)
- Java (.java)
- Go (.go)
- C/C++ (.c, .cpp, .h, .hpp)
- C# (.cs)
- Ruby (.rb)
- PHP (.php)
- Swift (.swift)
- Kotlin (.kt)
- Rust (.rs)

### Data Ingestion API

#### Get Supported File Types
```bash
GET /api/data_ingestion/supported_types
```

Returns list of all supported file types and their processors.

#### Ingest Single File
```bash
POST /api/data_ingestion/ingest_file
Content-Type: application/json

{
  "file_path": "/path/to/file.xlsx",
  "metadata": {"project": "analysis"},
  "tags": ["financial", "Q1-2024"]
}
```

#### Batch Ingestion
```bash
POST /api/data_ingestion/ingest_batch
Content-Type: application/json

{
  "file_paths": [
    "/path/to/file1.py",
    "/path/to/file2.json",
    "/path/to/data.xlsx"
  ],
  "tags": ["batch1"]
}
```

#### Directory Ingestion
```bash
POST /api/data_ingestion/ingest_directory
Content-Type: application/json

{
  "directory_path": "/path/to/project",
  "recursive": true,
  "file_patterns": ["*.py", "*.json"],
  "ignore_patterns": ["**/node_modules/**", "**/.git/**"],
  "tags": ["project-import"]
}
```

#### File Upload
```bash
POST /api/data_ingestion/upload
Content-Type: multipart/form-data

file=@local_file.xlsx
metadata={"source": "upload"}
tags=["uploaded"]
```

## Phase 2: Context Enrichment

### MetadataExtractor

Comprehensive metadata extraction from various file types.

**Extracted Metadata:**

**Basic (All Files):**
- File name, path, size
- Created, modified, accessed times
- File extension, MIME type
- File permissions

**PDF Files:**
- Author, title, subject, keywords
- Creator, producer
- Page count
- First page text preview

**DOCX Files:**
- Core properties (title, author, subject)
- Created/modified dates
- Last modified by
- Paragraph and table counts
- Text preview

**Excel Files:**
- Workbook properties
- Creator, last modified by
- Sheet names and count
- Row/column counts per sheet

**Images:**
- Format, mode, dimensions
- EXIF data (camera, GPS, etc.)

**Code Files:**
- Total lines, non-empty lines
- Comment line count
- File encoding
- Encoding confidence

**Usage:**
```python
from opencontext.context_processing.metadata_extractor import get_metadata_extractor

extractor = get_metadata_extractor()
metadata = extractor.extract_metadata("/path/to/file.pdf")
```

### AutoTaggingService

LLM-powered automatic tag generation from content.

**Features:**
- Topic extraction
- Keyword generation
- Entity identification
- Category classification
- Path-based tag extraction

**Generated Tags:**
- `topics` - High-level themes
- `keywords` - Important terms
- `entities` - People, organizations, locations
- `categories` - Content classification

**Usage:**
```python
from opencontext.context_processing.auto_tagging_service import get_auto_tagging_service

service = get_auto_tagging_service()
tags = service.generate_tags_sync(
    content="Your document content...",
    title="Document Title"
)
# Returns: {"topics": [...], "keywords": [...], "entities": [...], "categories": [...]}
```

## Phase 3: Model Integration

### ModelRegistry

Complete ML model management system with versioning and metadata.

**Features:**
- Model registration with metadata
- Version management (unique name + version)
- File storage and organization
- Performance metrics tracking
- Tag-based organization
- Search and discovery

**Model Metadata:**
- `name` - Model name
- `version` - Model version
- `description` - Model description
- `use_case` - Primary use case
- `model_type` - Type (classification, regression, llm, etc.)
- `framework` - ML framework (pytorch, tensorflow, sklearn, etc.)
- `tags` - List of tags
- `metrics` - Performance metrics (accuracy, F1, etc.)
- `metadata` - Custom metadata

### Model Registry API

#### Register Model
```bash
POST /api/models/register
Content-Type: application/json

{
  "name": "sentiment-classifier",
  "version": "1.0.0",
  "description": "BERT-based sentiment analysis model",
  "use_case": "sentiment-analysis",
  "model_type": "classification",
  "framework": "pytorch",
  "file_path": "/path/to/model.pt",
  "tags": ["nlp", "sentiment", "bert"],
  "metrics": {
    "accuracy": 0.95,
    "f1": 0.94,
    "precision": 0.96
  },
  "created_by": "user@example.com"
}
```

#### Upload Model
```bash
POST /api/models/upload
Content-Type: multipart/form-data

name=sentiment-classifier
version=1.0.0
description=Sentiment analysis model
use_case=sentiment-analysis
model_type=classification
framework=pytorch
file=@model.pt
tags=["nlp", "sentiment"]
metrics={"accuracy": 0.95}
```

#### Get Model
```bash
GET /api/models/{model_id}
```

#### Download Model
```bash
GET /api/models/{model_id}/download
```

#### Search Models
```bash
POST /api/models/search
Content-Type: application/json

{
  "query": "sentiment",
  "use_case": "sentiment-analysis",
  "model_type": "classification",
  "framework": "pytorch",
  "tags": ["nlp"],
  "limit": 20
}
```

#### List All Models
```bash
GET /api/models?limit=50
```

#### Update Model
```bash
PUT /api/models/{model_id}
Content-Type: application/json

{
  "description": "Updated description",
  "tags": ["nlp", "sentiment", "production"],
  "metrics": {
    "accuracy": 0.96,
    "f1": 0.95
  }
}
```

#### Delete Model
```bash
# Soft delete (mark as inactive)
DELETE /api/models/{model_id}

# Hard delete (remove file and record)
DELETE /api/models/{model_id}?hard_delete=true
```

## Phase 4: Enhanced Search

### EnhancedSearchService

Advanced search with multi-filter support and ranking.

**Features:**
- Multi-filter search
- Tag-based search
- Recent content search
- Similarity search
- Search facets for UI
- Multiple sorting options

**Filters:**
- `context_types` - Filter by context type
- `file_types` - Filter by file extension
- `tags` - Filter by tags
- `date_from/date_to` - Date range
- `min_relevance` - Minimum relevance score

**Sorting:**
- `relevance` - By semantic similarity (default)
- `date` - By creation date
- `importance` - By importance score

### Enhanced Search API

#### Advanced Search
```bash
POST /api/search/enhanced
Content-Type: application/json

{
  "query": "machine learning analysis",
  "top_k": 10,
  "context_types": ["semantic_context"],
  "file_types": ["pdf", "docx"],
  "tags": ["research", "ml"],
  "date_from": "2024-01-01T00:00:00",
  "date_to": "2024-12-31T23:59:59",
  "min_relevance": 0.7,
  "sort_by": "relevance"
}
```

#### Tag Search
```bash
POST /api/search/by_tags
Content-Type: application/json

{
  "tags": ["machine-learning", "nlp"],
  "top_k": 10,
  "match_all": false
}
```

#### Recent Content
```bash
GET /api/search/recent?days=7&top_k=20
```

#### Similar Content
```bash
POST /api/search/similar
Content-Type: application/json

{
  "context_id": "context-123",
  "top_k": 10
}
```

#### Search Facets
```bash
GET /api/search/facets?query=machine%20learning
```

Returns aggregations:
```json
{
  "facets": {
    "file_types": {
      "pdf": 45,
      "docx": 23,
      "xlsx": 12
    },
    "context_types": {
      "semantic_context": 67,
      "activity_context": 13
    },
    "tags": {
      "machine-learning": 34,
      "data-science": 28
    },
    "date_ranges": {
      "last_day": 5,
      "last_week": 23,
      "last_month": 47,
      "older": 15
    }
  }
}
```

## Configuration

### Full Configuration Example

```yaml
# Document processing
document_processing:
  enabled: true
  batch_size: 3
  max_image_size: 1024
  dpi: 200
  text_threshold_per_page: 50

# Context processing
processing:
  enabled: true
  
  # Excel processor
  excel_processor:
    enabled: true
    max_rows_per_chunk: 100
    extract_formulas: true
    extract_comments: true
    detect_tables: true
  
  # Structured data processor
  structured_data_processor:
    enabled: true
    max_depth: 10
    max_array_items_per_chunk: 50
    preserve_structure: true
  
  # Code processor
  code_processor:
    enabled: true
    max_lines_per_chunk: 100
    extract_functions: true
    extract_classes: true
    extract_imports: true
    extract_comments: true
```

## Examples

### Example 1: Ingest Project Directory

```bash
curl -X POST http://localhost:1733/api/data_ingestion/ingest_directory \
  -H "Content-Type: application/json" \
  -d '{
    "directory_path": "/home/user/my-project",
    "recursive": true,
    "file_patterns": ["*.py", "*.json", "*.md"],
    "ignore_patterns": ["**/__pycache__/**", "**/node_modules/**"],
    "tags": ["my-project", "source-code"]
  }'
```

### Example 2: Upload and Register ML Model

```bash
# Upload model file
curl -X POST http://localhost:1733/api/models/upload \
  -F "name=my-classifier" \
  -F "version=2.0.0" \
  -F "description=Production classifier model" \
  -F "use_case=classification" \
  -F "model_type=classification" \
  -F "framework=pytorch" \
  -F 'tags=["production", "classification"]' \
  -F 'metrics={"accuracy": 0.97, "f1": 0.96}' \
  -F "file=@model.pt"
```

### Example 3: Enhanced Search

```bash
# Search for recent ML-related documents
curl -X POST http://localhost:1733/api/search/enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning model training",
    "top_k": 20,
    "file_types": ["pdf", "py"],
    "tags": ["machine-learning"],
    "date_from": "2024-01-01T00:00:00",
    "sort_by": "date"
  }'
```

### Example 4: Batch File Ingestion

```python
import requests

files = [
    "/data/reports/q1_analysis.xlsx",
    "/data/reports/q2_analysis.xlsx",
    "/data/code/analysis.py",
    "/data/config/settings.json"
]

response = requests.post(
    "http://localhost:1733/api/data_ingestion/ingest_batch",
    json={
        "file_paths": files,
        "tags": ["quarterly-reports", "2024"],
        "metadata": {"project": "analysis-2024"}
    }
)

print(response.json())
```

### Example 5: Search Models and Download

```python
import requests

# Search for models
response = requests.post(
    "http://localhost:1733/api/models/search",
    json={
        "query": "sentiment",
        "model_type": "classification",
        "tags": ["nlp"]
    }
)

models = response.json()["data"]["models"]

# Download best model
if models:
    model_id = models[0]["id"]
    response = requests.get(
        f"http://localhost:1733/api/models/{model_id}/download"
    )
    
    with open("downloaded_model.pt", "wb") as f:
        f.write(response.content)
```

## Best Practices

1. **File Organization**
   - Use consistent naming conventions
   - Organize files in logical directories
   - Use meaningful tags

2. **Model Management**
   - Always version your models
   - Include comprehensive metrics
   - Document use cases clearly
   - Use semantic versioning (major.minor.patch)

3. **Metadata**
   - Add relevant tags during ingestion
   - Include project/source information
   - Use date filters for temporal data

4. **Search**
   - Start with broad queries, then refine with filters
   - Use facets to understand available filters
   - Combine multiple search types for best results

5. **Performance**
   - Use batch operations for large datasets
   - Configure chunking sizes appropriately
   - Monitor storage usage

## Troubleshooting

### Common Issues

**1. File Not Found**
- Ensure file paths are absolute
- Check file permissions
- Verify file exists before ingestion

**2. Model Registration Fails**
- Check for duplicate name+version
- Ensure file path is valid
- Verify model file is accessible

**3. Search Returns No Results**
- Check spelling in query
- Verify filters aren't too restrictive
- Try broader search terms
- Check if data was actually ingested

**4. Slow Processing**
- Reduce batch sizes in config
- Process smaller directories
- Check system resources

## Future Enhancements

Planned features:
- Notion integration (Phase 5)
- Google Drive integration (Phase 5)
- Automated workflows (Phase 6)
- Web UI for model registry (Phase 3)
- Query history and saved searches (Phase 4)

## Support

For issues and questions:
- GitHub Issues: https://github.com/UncleTupelo/Jf25_pulse/issues
- Documentation: This file and README.md
