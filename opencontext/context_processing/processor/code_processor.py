#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Code Processor for source code files with syntax-aware chunking
Supports multiple programming languages
"""

import datetime
import re
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


class CodeProcessor(BaseContextProcessor):
    """
    Processor for source code files with syntax-aware chunking.
    
    Features:
    - Multi-language support (Python, JavaScript, Java, C++, Go, etc.)
    - Function/class detection
    - Import/dependency extraction
    - Comment extraction
    - Docstring parsing
    """

    # Language-specific patterns
    LANGUAGE_PATTERNS = {
        "python": {
            "function": r"^\s*def\s+(\w+)",
            "class": r"^\s*class\s+(\w+)",
            "import": r"^\s*(?:from\s+[\w.]+\s+)?import\s+(.+)",
            "comment": r"^\s*#(.+)",
            "docstring": r'^\s*"""(.+?)"""',
        },
        "javascript": {
            "function": r"^\s*(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?\()",
            "class": r"^\s*class\s+(\w+)",
            "import": r"^\s*import\s+(.+)",
            "comment": r"^\s*//(.+)",
            "block_comment": r"/\*(.+?)\*/",
        },
        "java": {
            "function": r"^\s*(?:public|private|protected)?\s+(?:static\s+)?[\w<>]+\s+(\w+)\s*\(",
            "class": r"^\s*(?:public\s+)?class\s+(\w+)",
            "import": r"^\s*import\s+(.+);",
            "comment": r"^\s*//(.+)",
            "block_comment": r"/\*(.+?)\*/",
        },
        "go": {
            "function": r"^\s*func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)",
            "struct": r"^\s*type\s+(\w+)\s+struct",
            "import": r"^\s*import\s+(.+)",
            "comment": r"^\s*//(.+)",
            "block_comment": r"/\*(.+?)\*/",
        },
    }

    # File extension to language mapping
    EXTENSION_TO_LANGUAGE = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "javascript",
        ".tsx": "javascript",
        ".java": "java",
        ".go": "go",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".rs": "rust",
    }

    def __init__(self):
        from opencontext.config.global_config import get_config
        config = get_config("processing.code_processor") or {}
        super().__init__(config)
        
        # Configuration
        self._enabled = config.get("enabled", True)
        self._max_lines_per_chunk = config.get("max_lines_per_chunk", 100)
        self._extract_functions = config.get("extract_functions", True)
        self._extract_classes = config.get("extract_classes", True)
        self._extract_imports = config.get("extract_imports", True)
        self._extract_comments = config.get("extract_comments", True)
        
        logger.info("CodeProcessor initialized")

    def get_name(self) -> str:
        return "code_processor"

    def get_description(self) -> str:
        return "Processor for source code files with syntax-aware chunking"

    @staticmethod
    def get_supported_formats() -> List[str]:
        return list(CodeProcessor.EXTENSION_TO_LANGUAGE.keys())

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
        """Process code file and extract structured information"""
        try:
            file_path = Path(context.content_path)
            logger.info(f"Processing code file: {file_path}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code_content = f.read()
            
            # Detect language
            language = self._detect_language(file_path)
            
            # Extract metadata
            metadata = self._extract_code_metadata(code_content, language, file_path)
            
            # Create chunks from code
            chunks = self._create_chunks_from_code(code_content, language, file_path.name)
            
            # Create processed context
            processed_context = self._create_processed_context(
                context, chunks, metadata, language
            )
            
            if processed_context:
                logger.info(f"Successfully processed {file_path}")
                return [processed_context]
            
            return []
            
        except Exception as e:
            logger.exception(f"Error processing code file {context.content_path}: {e}")
            return []

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        ext = file_path.suffix.lower()
        return self.EXTENSION_TO_LANGUAGE.get(ext, "unknown")

    def _extract_code_metadata(
        self, code: str, language: str, file_path: Path
    ) -> Dict[str, Any]:
        """Extract metadata from code"""
        lines = code.split('\n')
        
        metadata = {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "language": language,
            "total_lines": len(lines),
            "non_empty_lines": sum(1 for line in lines if line.strip()),
        }
        
        # Extract functions, classes, imports based on language
        if language in self.LANGUAGE_PATTERNS:
            patterns = self.LANGUAGE_PATTERNS[language]
            
            if self._extract_functions and "function" in patterns:
                functions = re.findall(patterns["function"], code, re.MULTILINE)
                metadata["functions"] = [f for group in functions for f in (group if isinstance(group, tuple) else [group]) if f]
                metadata["num_functions"] = len(metadata["functions"])
            
            if self._extract_classes and "class" in patterns:
                classes = re.findall(patterns["class"], code, re.MULTILINE)
                metadata["classes"] = classes
                metadata["num_classes"] = len(classes)
            
            if self._extract_imports and "import" in patterns:
                imports = re.findall(patterns["import"], code, re.MULTILINE)
                metadata["imports"] = imports[:20]  # Limit to first 20
                metadata["num_imports"] = len(imports)
        
        return metadata

    def _create_chunks_from_code(
        self, code: str, language: str, file_name: str
    ) -> List[Chunk]:
        """Create chunks from code with syntax awareness"""
        chunks = []
        lines = code.split('\n')
        
        # Chunk 1: File overview
        overview_text = f"Code File: {file_name}\n"
        overview_text += f"Language: {language}\n"
        overview_text += f"Total Lines: {len(lines)}\n"
        
        # Add a preview of the first few lines
        preview_lines = min(20, len(lines))
        overview_text += f"\nFirst {preview_lines} lines:\n"
        overview_text += '\n'.join(lines[:preview_lines])
        
        chunks.append(Chunk(
            text=overview_text,
            chunk_index=0,
            keywords=[file_name, language, "code", "overview"],
        ))
        
        # Chunk 2+: Code sections
        # Try to split by functions/classes if possible
        if language in self.LANGUAGE_PATTERNS:
            chunks.extend(self._chunk_by_syntax(code, language, file_name))
        else:
            # Fallback to line-based chunking
            chunks.extend(self._chunk_by_lines(lines, file_name, len(chunks)))
        
        return chunks

    def _chunk_by_syntax(
        self, code: str, language: str, file_name: str
    ) -> List[Chunk]:
        """Create chunks based on syntax elements (functions, classes)"""
        chunks = []
        patterns = self.LANGUAGE_PATTERNS.get(language, {})
        lines = code.split('\n')
        
        # Find all function/class definitions
        elements = []
        for i, line in enumerate(lines):
            for element_type in ["function", "class", "struct"]:
                if element_type in patterns:
                    match = re.match(patterns[element_type], line)
                    if match:
                        name = match.group(1) if match.lastindex else "unknown"
                        elements.append({
                            "type": element_type,
                            "name": name,
                            "line": i,
                        })
        
        # Create chunks for each element with context
        for i, element in enumerate(elements):
            start_line = element["line"]
            # Determine end line (next element or end of file)
            end_line = elements[i + 1]["line"] if i + 1 < len(elements) else len(lines)
            
            chunk_lines = lines[start_line:end_line]
            chunk_text = f"{element['type'].capitalize()}: {element['name']}\n"
            chunk_text += f"Lines {start_line + 1}-{end_line}\n\n"
            chunk_text += '\n'.join(chunk_lines)
            
            chunks.append(Chunk(
                text=chunk_text,
                chunk_index=len(chunks) + 1,
                keywords=[file_name, language, element["type"], element["name"]],
                entities=[element["name"]],
            ))
        
        # If no elements found, fall back to line-based chunking
        if not chunks:
            chunks = self._chunk_by_lines(lines, file_name, 1)
        
        return chunks

    def _chunk_by_lines(
        self, lines: List[str], file_name: str, start_idx: int
    ) -> List[Chunk]:
        """Create chunks based on line count"""
        chunks = []
        
        for i in range(0, len(lines), self._max_lines_per_chunk):
            chunk_lines = lines[i:i + self._max_lines_per_chunk]
            
            chunk_text = f"Lines {i + 1}-{i + len(chunk_lines)}\n\n"
            chunk_text += '\n'.join(chunk_lines)
            
            chunks.append(Chunk(
                text=chunk_text,
                chunk_index=start_idx + len(chunks),
                keywords=[file_name, f"lines_{i+1}_{i+len(chunk_lines)}"],
            ))
        
        return chunks

    def _create_processed_context(
        self,
        raw_context: RawContextProperties,
        chunks: List[Chunk],
        metadata: Dict[str, Any],
        language: str,
    ) -> Optional[ProcessedContext]:
        """Create ProcessedContext from chunks and metadata"""
        if not chunks:
            return None
        
        # Generate title and summary
        title = metadata["file_name"]
        summary = f"{language.capitalize()} code with {metadata['total_lines']} lines"
        
        if "num_functions" in metadata:
            summary += f", {metadata['num_functions']} functions"
        if "num_classes" in metadata:
            summary += f", {metadata['num_classes']} classes"
        
        # Extract keywords
        keywords = [metadata["file_name"], language, "code"]
        
        if "functions" in metadata:
            keywords.extend(metadata["functions"][:10])
        if "classes" in metadata:
            keywords.extend(metadata["classes"][:10])
        
        # Extract entities (function and class names)
        entities = []
        if "functions" in metadata:
            entities.extend(metadata["functions"])
        if "classes" in metadata:
            entities.extend(metadata["classes"])
        
        # Create ExtractedData
        extracted_data = ExtractedData(
            title=title,
            summary=summary,
            keywords=keywords,
            entities=entities[:20],  # Limit entities
            context_type=ContextType.SEMANTIC_CONTEXT,
            confidence=90,
            importance=80,
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
