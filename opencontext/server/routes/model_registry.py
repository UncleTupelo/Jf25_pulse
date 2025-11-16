#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
ML Model Registry API routes
Provides CRUD operations for managing ML models
"""

import os
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from opencontext.models.model_registry import get_model_registry
from opencontext.server.middleware.auth import auth_dependency
from opencontext.server.utils import convert_resp
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["model_registry"])


class RegisterModelRequest(BaseModel):
    """Model registration request"""
    name: str
    version: str
    file_path: Optional[str] = None
    description: Optional[str] = None
    use_case: Optional[str] = None
    model_type: Optional[str] = None
    framework: Optional[str] = None
    tags: Optional[List[str]] = None
    metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class UpdateModelRequest(BaseModel):
    """Model metadata update request"""
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchModelsRequest(BaseModel):
    """Model search request"""
    query: Optional[str] = None
    use_case: Optional[str] = None
    model_type: Optional[str] = None
    framework: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 20


@router.post("/api/models/register")
async def register_model(
    request: RegisterModelRequest,
    _auth: str = auth_dependency,
):
    """
    Register a new ML model
    
    Registers model metadata and optionally copies model file to registry.
    Model name and version must be unique.
    """
    try:
        registry = get_model_registry()
        
        model_id = registry.register_model(
            name=request.name,
            version=request.version,
            file_path=request.file_path,
            description=request.description,
            use_case=request.use_case,
            model_type=request.model_type,
            framework=request.framework,
            tags=request.tags,
            metrics=request.metrics,
            metadata=request.metadata,
            created_by=request.created_by,
        )
        
        if model_id is None:
            return convert_resp(
                code=400,
                status=400,
                message=f"Failed to register model. Model {request.name} v{request.version} may already exist."
            )
        
        return convert_resp(
            message="Model registered successfully",
            data={
                "model_id": model_id,
                "name": request.name,
                "version": request.version,
            }
        )
        
    except Exception as e:
        logger.exception(f"Error registering model: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")


@router.post("/api/models/upload")
async def upload_model(
    name: str = Form(...),
    version: str = Form(...),
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    use_case: Optional[str] = Form(None),
    model_type: Optional[str] = Form(None),
    framework: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string
    metrics: Optional[str] = Form(None),  # JSON string
    created_by: Optional[str] = Form(None),
    _auth: str = auth_dependency,
):
    """
    Upload and register a model file
    
    Uploads model file via multipart form data and registers it in the registry.
    """
    try:
        import json
        from pathlib import Path
        
        # Save uploaded file temporarily
        upload_dir = Path("./uploads/models")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file_path = upload_dir / file.filename
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Model file uploaded: {temp_file_path}")
        
        # Parse JSON fields
        tags_list = json.loads(tags) if tags else None
        metrics_dict = json.loads(metrics) if metrics else None
        
        # Register model
        registry = get_model_registry()
        
        model_id = registry.register_model(
            name=name,
            version=version,
            file_path=str(temp_file_path),
            description=description,
            use_case=use_case,
            model_type=model_type,
            framework=framework,
            tags=tags_list,
            metrics=metrics_dict,
            created_by=created_by,
        )
        
        # Clean up temp file
        temp_file_path.unlink(missing_ok=True)
        
        if model_id is None:
            return convert_resp(
                code=400,
                status=400,
                message=f"Failed to register model. Model {name} v{version} may already exist."
            )
        
        return convert_resp(
            message="Model uploaded and registered successfully",
            data={
                "model_id": model_id,
                "name": name,
                "version": version,
                "file_name": file.filename,
                "file_size": len(content),
            }
        )
        
    except Exception as e:
        logger.exception(f"Error uploading model: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")


@router.get("/api/models/{model_id}")
async def get_model(
    model_id: int,
    _auth: str = auth_dependency,
):
    """
    Get model by ID
    
    Returns model metadata including version, use case, metrics, etc.
    """
    try:
        registry = get_model_registry()
        
        model = registry.get_model(model_id)
        
        if not model:
            return convert_resp(code=404, status=404, message="Model not found")
        
        return convert_resp(data={"model": model})
        
    except Exception as e:
        logger.exception(f"Error getting model: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")


@router.get("/api/models/{model_id}/download")
async def download_model(
    model_id: int,
    _auth: str = auth_dependency,
):
    """
    Download model file
    
    Returns the model file for download
    """
    try:
        registry = get_model_registry()
        
        model = registry.get_model(model_id)
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        file_path = model.get("file_path")
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Model file not found")
        
        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=os.path.basename(file_path),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error downloading model: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/api/models/search")
async def search_models(
    request: SearchModelsRequest,
    _auth: str = auth_dependency,
):
    """
    Search models with filters
    
    Supports filtering by:
    - Text query (searches name, description, use case)
    - Use case
    - Model type
    - Framework
    - Tags
    """
    try:
        registry = get_model_registry()
        
        models = registry.search_models(
            query=request.query,
            use_case=request.use_case,
            model_type=request.model_type,
            framework=request.framework,
            tags=request.tags,
            limit=request.limit,
        )
        
        return convert_resp(
            data={
                "models": models,
                "total": len(models),
                "filters": {
                    "query": request.query,
                    "use_case": request.use_case,
                    "model_type": request.model_type,
                    "framework": request.framework,
                    "tags": request.tags,
                }
            }
        )
        
    except Exception as e:
        logger.exception(f"Error searching models: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")


@router.get("/api/models")
async def list_models(
    limit: int = Query(default=50, description="Maximum number of results"),
    _auth: str = auth_dependency,
):
    """
    List all active models
    
    Returns list of all models ordered by most recently updated
    """
    try:
        registry = get_model_registry()
        
        models = registry.list_models(limit=limit)
        
        return convert_resp(
            data={
                "models": models,
                "total": len(models),
            }
        )
        
    except Exception as e:
        logger.exception(f"Error listing models: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")


@router.put("/api/models/{model_id}")
async def update_model(
    model_id: int,
    request: UpdateModelRequest,
    _auth: str = auth_dependency,
):
    """
    Update model metadata
    
    Updates description, tags, metrics, and custom metadata
    """
    try:
        registry = get_model_registry()
        
        success = registry.update_model_metadata(
            model_id=model_id,
            description=request.description,
            tags=request.tags,
            metrics=request.metrics,
            metadata=request.metadata,
        )
        
        if not success:
            return convert_resp(code=400, status=400, message="Failed to update model")
        
        return convert_resp(message="Model updated successfully")
        
    except Exception as e:
        logger.exception(f"Error updating model: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")


@router.delete("/api/models/{model_id}")
async def delete_model(
    model_id: int,
    hard_delete: bool = Query(default=False, description="Permanently delete model file"),
    _auth: str = auth_dependency,
):
    """
    Delete a model
    
    By default, marks model as inactive (soft delete).
    With hard_delete=true, permanently deletes the model file and record.
    """
    try:
        registry = get_model_registry()
        
        success = registry.delete_model(model_id, hard_delete=hard_delete)
        
        if not success:
            return convert_resp(code=404, status=404, message="Model not found")
        
        delete_type = "permanently deleted" if hard_delete else "deactivated"
        return convert_resp(message=f"Model {delete_type} successfully")
        
    except Exception as e:
        logger.exception(f"Error deleting model: {e}")
        return convert_resp(code=500, status=500, message=f"Internal server error: {str(e)}")
