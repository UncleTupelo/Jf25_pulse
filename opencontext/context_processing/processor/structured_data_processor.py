#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Structured Data Processor for JSON and YAML files
Handles complex nested structures with intelligent chunking
"""

import datetime
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from opencontext.context_processing.processor.base_processor import BaseContextProcessor
from opencontext.models.context import (
    ProcessedContext,
    RawContextProperties,
    ContextProperties,
    ExtractedData,
    Chunk,
)
from opencontext.models.enums import ContextSource, ContextType, ContentFormat
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class StructuredDataProcessor(BaseContextProcessor):
    """
    Processor for JSON and YAML files with intelligent structure preservation.
    
    Features:
    - Hierarchical structure detection
    - Schema extraction
    - Path-based indexing
    - Nested object chunking
    - Array handling
    """

    def __init__(self):
        from opencontext.config.global_config import get_config
        config = get_config("processing.structured_data_processor") or {}
        super().__init__(config)
        
        # Configuration
        self._enabled = config.get("enabled", True)
        self._max_depth = config.get("max_depth", 10)
        self._max_array_items_per_chunk = config.get("max_array_items_per_chunk", 50)
        self._preserve_structure = config.get("preserve_structure", True)
        
        logger.info("StructuredDataProcessor initialized")

    def get_name(self) -> str:
        return "structured_data_processor"

    def get_description(self) -> str:
        return "Processor for JSON and YAML files with intelligent structure preservation"

    @staticmethod
    def get_supported_formats() -> List[str]:
        return [".json", ".yaml", ".yml", ".jsonl"]

    def can_process(self, context: Any) -> bool:
        """Check if this processor can handle the context"""
        if not self._enabled:
            return False
            
        if not isinstance(context, RawContextProperties):
            return False
            
        if context.source != ContextSource.LOCAL_FILE:
            return False
            
        if not context.content_path:
            return False
            
        file_path = Path(context.content_path)
        return file_path.exists() and file_path.suffix.lower() in self.get_supported_formats()

    def process(self, context: RawContextProperties) -> List[ProcessedContext]:
        """Process JSON/YAML file and extract structured data"""
        try:
            file_path = Path(context.content_path)
            logger.info(f"Processing structured data file: {file_path}")
            
            # Load the file
            data = self._load_file(file_path)
            if data is None:
                return []
            
            # Extract metadata
            metadata = self._extract_metadata(data, file_path)
            
            # Create chunks from structured data
            chunks = self._create_chunks_from_data(data, file_path.name)
            
            # Create processed context
            processed_context = self._create_processed_context(
                context, chunks, metadata
            )
            
            if processed_context:
                logger.info(f"Successfully processed {file_path}")
                return [processed_context]
            
            return []
            
        except Exception as e:
            logger.exception(f"Error processing structured data file {context.content_path}: {e}")
            return []

    def _load_file(self, file_path: Path) -> Optional[Any]:
        """Load JSON or YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.jsonl':
                    # JSONL format - load all lines
                    return [json.loads(line) for line in f if line.strip()]
                elif file_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:  # .json
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return None

    def _extract_metadata(self, data: Any, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from structured data"""
        metadata = {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "file_type": file_path.suffix.lower(),
            "data_type": type(data).__name__,
        }
        
        # Extract structure information
        if isinstance(data, dict):
            metadata["top_level_keys"] = list(data.keys())
            metadata["num_keys"] = len(data)
        elif isinstance(data, list):
            metadata["num_items"] = len(data)
            if data and isinstance(data[0], dict):
                metadata["item_keys"] = list(data[0].keys())
        
        # Extract schema
        schema = self._extract_schema(data)
        if schema:
            metadata["schema"] = schema
        
        return metadata

    def _extract_schema(self, data: Any, depth: int = 0) -> Optional[Dict[str, Any]]:
        """Extract schema from nested data structure"""
        if depth > self._max_depth:
            return {"type": "max_depth_exceeded"}
        
        if isinstance(data, dict):
            schema = {"type": "object", "properties": {}}
            for key, value in data.items():
                schema["properties"][key] = self._extract_schema(value, depth + 1)
            return schema
        elif isinstance(data, list):
            if not data:
                return {"type": "array", "items": {}}
            # Use first item as representative
            return {
                "type": "array",
                "length": len(data),
                "items": self._extract_schema(data[0], depth + 1)
            }
        else:
            return {"type": type(data).__name__}

    def _create_chunks_from_data(
        self, data: Any, file_name: str, path: str = ""
    ) -> List[Chunk]:
        """Create chunks from structured data with path-based indexing"""
        chunks = []
        
        # Chunk 1: Overview
        overview_text = f"File: {file_name}\n"
        overview_text += f"Type: {type(data).__name__}\n"
        
        if isinstance(data, dict):
            overview_text += f"Top-level keys: {', '.join(list(data.keys())[:10])}\n"
            if len(data) > 10:
                overview_text += f"... and {len(data) - 10} more keys\n"
        elif isinstance(data, list):
            overview_text += f"Array with {len(data)} items\n"
        
        # Add formatted data preview
        preview = json.dumps(data, indent=2, ensure_ascii=False)
        if len(preview) > 500:
            preview = preview[:500] + "\n... (truncated)"
        overview_text += f"\nPreview:\n{preview}\n"
        
        chunks.append(Chunk(
            text=overview_text,
            chunk_index=0,
            keywords=[file_name, "overview", "structure"],
        ))
        
        # Create chunks from content
        if isinstance(data, dict):
            chunks.extend(self._chunk_dict(data, path, file_name, len(chunks)))
        elif isinstance(data, list):
            chunks.extend(self._chunk_list(data, path, file_name, len(chunks)))
        
        return chunks

    def _chunk_dict(
        self, data: Dict, path: str, file_name: str, start_idx: int
    ) -> List[Chunk]:
        """Create chunks from dictionary"""
        chunks = []
        
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, (dict, list)):
                # Create chunk for complex nested structure
                chunk_text = f"Path: {current_path}\n"
                chunk_text += f"Type: {type(value).__name__}\n"
                value_str = json.dumps(value, indent=2, ensure_ascii=False)
                if len(value_str) > 2000:
                    value_str = value_str[:2000] + "\n... (truncated)"
                chunk_text += f"Content:\n{value_str}\n"
                
                chunks.append(Chunk(
                    text=chunk_text,
                    chunk_index=start_idx + len(chunks),
                    keywords=[file_name, key, current_path, type(value).__name__],
                ))
            else:
                # Simple value - can be part of a batch
                chunk_text = f"Path: {current_path}\n"
                chunk_text += f"Value: {value}\n"
                
                chunks.append(Chunk(
                    text=chunk_text,
                    chunk_index=start_idx + len(chunks),
                    keywords=[file_name, key, current_path],
                ))
        
        return chunks

    def _chunk_list(
        self, data: List, path: str, file_name: str, start_idx: int
    ) -> List[Chunk]:
        """Create chunks from list/array"""
        chunks = []
        
        # Process array in batches
        for i in range(0, len(data), self._max_array_items_per_chunk):
            batch = data[i:i + self._max_array_items_per_chunk]
            
            chunk_text = f"Path: {path}\n"
            chunk_text += f"Array items [{i}:{min(i + self._max_array_items_per_chunk, len(data))}]\n"
            
            batch_str = json.dumps(batch, indent=2, ensure_ascii=False)
            if len(batch_str) > 2000:
                batch_str = batch_str[:2000] + "\n... (truncated)"
            chunk_text += f"Content:\n{batch_str}\n"
            
            chunks.append(Chunk(
                text=chunk_text,
                chunk_index=start_idx + len(chunks),
                keywords=[file_name, path, "array", f"items_{i}_{i+len(batch)}"],
            ))
        
        return chunks

    def _create_processed_context(
        self,
        raw_context: RawContextProperties,
        chunks: List[Chunk],
        metadata: Dict[str, Any],
    ) -> Optional[ProcessedContext]:
        """Create ProcessedContext from chunks and metadata"""
        if not chunks:
            return None
        
        # Generate title and summary
        title = metadata["file_name"]
        
        if metadata["data_type"] == "dict":
            summary = f"Structured data with {metadata.get('num_keys', 0)} top-level keys"
        elif metadata["data_type"] == "list":
            summary = f"Array with {metadata.get('num_items', 0)} items"
        else:
            summary = f"Structured data of type {metadata['data_type']}"
        
        # Extract keywords
        keywords = [
            metadata["file_name"],
            metadata["file_type"].lstrip('.'),
            metadata["data_type"],
        ]
        
        if "top_level_keys" in metadata:
            keywords.extend(metadata["top_level_keys"][:10])
        
        # Create ExtractedData
        extracted_data = ExtractedData(
            title=title,
            summary=summary,
            keywords=keywords,
            entities=[],
            context_type=ContextType.SEMANTIC_CONTEXT,
            confidence=95,
            importance=75,
        )
        
        # Create ContextProperties
        context_properties = ContextProperties(
            context_type=ContextType.SEMANTIC_CONTEXT,
            source=raw_context.source,
            create_time=datetime.datetime.now(),
            update_time=datetime.datetime.now(),
            content_path=raw_context.content_path,
            content_format=ContentFormat.TEXT,
            title=title,
            summary=summary,
            tags=keywords,
            additional_metadata={
                **metadata,
                "processor": self.get_name(),
            },
        )
        
        # Create ProcessedContext
        processed_context = ProcessedContext(
            id=raw_context.object_id,
            properties=context_properties,
            chunks=chunks,
            extracted_data=extracted_data,
        )
        
        return processed_context
