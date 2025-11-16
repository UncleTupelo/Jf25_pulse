#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Data Ingestion API routes for unified file and data upload
Supports multiple file types with automatic detection and routing
"""

import os
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from opencontext.server.middleware.auth import auth_dependency
from opencontext.server.opencontext import OpenContext
from opencontext.server.utils import convert_resp, get_context_lab
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["data_ingestion"])


class IngestFileRequest(BaseModel):
    """File ingestion request with local path"""
    file_path: str
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class BatchIngestRequest(BaseModel):
    """Batch file ingestion request"""
    file_paths: List[str]
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class IngestDirectoryRequest(BaseModel):
    """Directory ingestion request"""
    directory_path: str
    recursive: bool = True
    file_patterns: Optional[List[str]] = None
    ignore_patterns: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class FileTypeInfo(BaseModel):
    """Information about supported file types"""
    extension: str
    processor: str
    description: str


@router.get("/api/data_ingestion/supported_types")
async def get_supported_file_types(_auth: str = auth_dependency):
    """
    Get list of supported file types and their processors
    
    Returns information about all file types that can be ingested
    """
    try:
        # Import processors to get their supported formats
        from opencontext.context_processing.processor.document_processor import DocumentProcessor
        from opencontext.context_processing.processor.excel_processor import ExcelProcessor
        from opencontext.context_processing.processor.structured_data_processor import StructuredDataProcessor
        from opencontext.context_processing.processor.code_processor import CodeProcessor
        
        supported_types = []
        
        # Document processor
        for ext in DocumentProcessor.get_supported_formats():
            supported_types.append({
                "extension": ext,
                "processor": "document_processor",
                "description": "General document processing (PDF, DOCX, images, etc.)"
            })
        
        # Excel processor
        for ext in ExcelProcessor.get_supported_formats():
            supported_types.append({
                "extension": ext,
                "processor": "excel_processor",
                "description": "Advanced Excel processing with cell-level chunking"
            })
        
        # Structured data processor
        for ext in StructuredDataProcessor.get_supported_formats():
            supported_types.append({
                "extension": ext,
                "processor": "structured_data_processor",
                "description": "JSON/YAML structured data processing"
            })
        
        # Code processor
        for ext in CodeProcessor.get_supported_formats():
            supported_types.append({
                "extension": ext,
                "processor": "code_processor",
                "description": "Source code processing with syntax awareness"
            })
        
        return convert_resp(data={
            "supported_types": supported_types,
            "total_types": len(supported_types)
        })
        
    except Exception as e:
        logger.exception(f"Error getting supported file types: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")


@router.post("/api/data_ingestion/ingest_file")
async def ingest_file(
    request: IngestFileRequest,
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Ingest a single file with automatic type detection
    
    The file type is automatically detected and routed to the appropriate processor.
    Supports all file types registered in the processor factory.
    """
    try:
        file_path = Path(request.file_path)
        
        # Validate file exists
        if not file_path.exists():
            return convert_resp(code=404, status=404, message=f"File not found: {request.file_path}")
        
        if not file_path.is_file():
            return convert_resp(code=400, status=400, message=f"Path is not a file: {request.file_path}")
        
        # Detect file type
        file_ext = file_path.suffix.lower()
        file_type = _detect_file_type(file_ext)
        
        logger.info(f"Ingesting file {file_path} (type: {file_type})")
        
        # Add to processing queue
        err_msg = opencontext.add_document(file_path=str(file_path))
        
        if err_msg:
            return convert_resp(code=400, status=400, message=err_msg)
        
        return convert_resp(
            message="File queued for processing successfully",
            data={
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": file_type,
                "metadata": request.metadata,
                "tags": request.tags
            }
        )
        
    except Exception as e:
        logger.exception(f"Error ingesting file: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")


@router.post("/api/data_ingestion/ingest_batch")
async def ingest_batch(
    request: BatchIngestRequest,
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Ingest multiple files in batch
    
    All files are validated and added to the processing queue.
    Returns status for each file.
    """
    try:
        results = []
        successful = 0
        failed = 0
        
        for file_path_str in request.file_paths:
            file_path = Path(file_path_str)
            
            # Validate file
            if not file_path.exists():
                results.append({
                    "file_path": file_path_str,
                    "status": "error",
                    "message": "File not found"
                })
                failed += 1
                continue
            
            if not file_path.is_file():
                results.append({
                    "file_path": file_path_str,
                    "status": "error",
                    "message": "Path is not a file"
                })
                failed += 1
                continue
            
            # Add to processing queue
            err_msg = opencontext.add_document(file_path=str(file_path))
            
            if err_msg:
                results.append({
                    "file_path": file_path_str,
                    "status": "error",
                    "message": err_msg
                })
                failed += 1
            else:
                results.append({
                    "file_path": file_path_str,
                    "file_name": file_path.name,
                    "file_type": _detect_file_type(file_path.suffix.lower()),
                    "status": "queued"
                })
                successful += 1
        
        return convert_resp(
            message=f"Batch ingestion completed: {successful} successful, {failed} failed",
            data={
                "total": len(request.file_paths),
                "successful": successful,
                "failed": failed,
                "results": results
            }
        )
        
    except Exception as e:
        logger.exception(f"Error in batch ingestion: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")


@router.post("/api/data_ingestion/ingest_directory")
async def ingest_directory(
    request: IngestDirectoryRequest,
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Ingest all files from a directory
    
    Scans directory and ingests all supported file types.
    Supports recursive scanning and file pattern filtering.
    """
    try:
        dir_path = Path(request.directory_path)
        
        # Validate directory exists
        if not dir_path.exists():
            return convert_resp(code=404, status=404, message=f"Directory not found: {request.directory_path}")
        
        if not dir_path.is_dir():
            return convert_resp(code=400, status=400, message=f"Path is not a directory: {request.directory_path}")
        
        # Collect files
        files = []
        if request.recursive:
            files = list(dir_path.rglob("*"))
        else:
            files = list(dir_path.glob("*"))
        
        # Filter files
        files = [f for f in files if f.is_file()]
        
        # Apply file patterns if specified
        if request.file_patterns:
            import fnmatch
            filtered_files = []
            for f in files:
                for pattern in request.file_patterns:
                    if fnmatch.fnmatch(f.name, pattern):
                        filtered_files.append(f)
                        break
            files = filtered_files
        
        # Apply ignore patterns if specified
        if request.ignore_patterns:
            import fnmatch
            filtered_files = []
            for f in files:
                should_ignore = False
                for pattern in request.ignore_patterns:
                    if fnmatch.fnmatch(str(f), pattern):
                        should_ignore = True
                        break
                if not should_ignore:
                    filtered_files.append(f)
            files = filtered_files
        
        # Ingest files
        results = []
        successful = 0
        failed = 0
        
        for file_path in files:
            err_msg = opencontext.add_document(file_path=str(file_path))
            
            if err_msg:
                results.append({
                    "file_path": str(file_path),
                    "status": "error",
                    "message": err_msg
                })
                failed += 1
            else:
                results.append({
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "file_type": _detect_file_type(file_path.suffix.lower()),
                    "status": "queued"
                })
                successful += 1
        
        return convert_resp(
            message=f"Directory ingestion completed: {successful} successful, {failed} failed",
            data={
                "directory": str(dir_path),
                "total_files": len(files),
                "successful": successful,
                "failed": failed,
                "results": results[:100]  # Limit results to first 100
            }
        )
        
    except Exception as e:
        logger.exception(f"Error in directory ingestion: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")


@router.post("/api/data_ingestion/upload")
async def upload_file(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Upload a file via HTTP multipart form data
    
    The file is saved to a temporary location and then ingested.
    """
    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path("./uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_path = upload_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File uploaded: {file_path}")
        
        # Add to processing queue
        err_msg = opencontext.add_document(file_path=str(file_path))
        
        if err_msg:
            # Clean up file if processing failed
            file_path.unlink(missing_ok=True)
            return convert_resp(code=400, status=400, message=err_msg)
        
        return convert_resp(
            message="File uploaded and queued for processing successfully",
            data={
                "file_name": file.filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "file_type": _detect_file_type(Path(file.filename).suffix.lower())
            }
        )
        
    except Exception as e:
        logger.exception(f"Error uploading file: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")


def _detect_file_type(extension: str) -> str:
    """Detect file type from extension"""
    from opencontext.context_processing.processor.excel_processor import ExcelProcessor
    from opencontext.context_processing.processor.structured_data_processor import StructuredDataProcessor
    from opencontext.context_processing.processor.code_processor import CodeProcessor
    
    if extension in ExcelProcessor.get_supported_formats():
        return "excel"
    elif extension in StructuredDataProcessor.get_supported_formats():
        return "structured_data"
    elif extension in CodeProcessor.get_supported_formats():
        return "code"
    elif extension in [".pdf", ".docx", ".doc", ".txt", ".md"]:
        return "document"
    elif extension in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]:
        return "image"
    else:
        return "unknown"
