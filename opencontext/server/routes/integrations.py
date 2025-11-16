# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Cloud integrations and manual sync routes
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel

from opencontext.server.middleware.auth import auth_dependency
from opencontext.server.opencontext import OpenContext
from opencontext.server.utils import convert_resp, get_context_lab
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["integrations"])


class SyncRequest(BaseModel):
    """Request model for manual sync triggers."""
    integration_name: str


class IntegrationStatusResponse(BaseModel):
    """Response model for integration status."""
    name: str
    enabled: bool
    running: bool
    last_sync_time: Optional[str]
    status: dict


@router.post("/api/integrations/sync")
async def trigger_sync(
    request: SyncRequest,
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Manually trigger a sync for a specific integration.
    
    Args:
        request: Sync request containing integration name
        
    Returns:
        Sync result with status and captured items count
    """
    try:
        integration_name = request.integration_name.lower()
        
        # Get the capture manager
        capture_manager = opencontext._capture_manager
        
        # Check if component exists
        if integration_name not in capture_manager._components:
            raise HTTPException(
                status_code=404,
                detail=f"Integration '{integration_name}' not found"
            )
        
        # Get the component
        component = capture_manager._components[integration_name]
        
        # Check if component is running
        if not component.is_running():
            raise HTTPException(
                status_code=400,
                detail=f"Integration '{integration_name}' is not running"
            )
        
        # Trigger capture
        contexts = component.capture()
        
        logger.info(f"Manual sync for {integration_name} captured {len(contexts)} items")
        
        return convert_resp(
            data={
                "integration": integration_name,
                "captured_items": len(contexts),
                "message": f"Successfully synced {len(contexts)} items"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error triggering sync: {e}")
        return convert_resp(
            code=500,
            status=500,
            message=f"Sync failed: {str(e)}"
        )


@router.get("/api/integrations/status")
async def get_integrations_status(
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Get status of all configured integrations.
    
    Returns:
        List of integration statuses
    """
    try:
        capture_manager = opencontext._capture_manager
        
        integrations = []
        for name, component in capture_manager._components.items():
            status = component.get_status()
            integrations.append({
                "name": name,
                "enabled": True,  # If registered, it's enabled
                "running": component.is_running(),
                "last_sync_time": status.get("last_capture_time"),
                "status": status,
            })
        
        return convert_resp(data={"integrations": integrations})
        
    except Exception as e:
        logger.exception(f"Error getting integrations status: {e}")
        return convert_resp(
            code=500,
            status=500,
            message=f"Failed to get status: {str(e)}"
        )


@router.get("/api/integrations/{integration_name}/status")
async def get_integration_status(
    integration_name: str,
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Get status of a specific integration.
    
    Args:
        integration_name: Name of the integration
        
    Returns:
        Integration status details
    """
    try:
        capture_manager = opencontext._capture_manager
        
        integration_name = integration_name.lower()
        
        if integration_name not in capture_manager._components:
            raise HTTPException(
                status_code=404,
                detail=f"Integration '{integration_name}' not found"
            )
        
        component = capture_manager._components[integration_name]
        status = component.get_status()
        
        return convert_resp(
            data={
                "name": integration_name,
                "enabled": True,
                "running": component.is_running(),
                "status": status,
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting integration status: {e}")
        return convert_resp(
            code=500,
            status=500,
            message=f"Failed to get status: {str(e)}"
        )


@router.post("/api/integrations/upload")
async def upload_file(
    file: UploadFile = File(...),
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Upload a file for context ingestion.
    
    Args:
        file: File to upload
        
    Returns:
        Upload result with file information
    """
    try:
        capture_manager = opencontext._capture_manager
        
        # Check if file upload component exists
        file_upload_name = "fileuploadcapture"
        if file_upload_name not in capture_manager._components:
            raise HTTPException(
                status_code=503,
                detail="File upload integration not configured"
            )
        
        component = capture_manager._components[file_upload_name]
        
        # Read file content
        file_data = await file.read()
        
        # Upload file using the component
        context = component.upload_file(
            file_data=file_data,
            file_name=file.filename,
            metadata={
                "content_type": file.content_type,
                "size": len(file_data),
            }
        )
        
        if context is None:
            raise HTTPException(
                status_code=400,
                detail="File upload failed - check file type and size"
            )
        
        logger.info(f"File uploaded successfully: {file.filename}")
        
        return convert_resp(
            data={
                "file_name": file.filename,
                "file_size": len(file_data),
                "content_type": file.content_type,
                "message": "File uploaded successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error uploading file: {e}")
        return convert_resp(
            code=500,
            status=500,
            message=f"Upload failed: {str(e)}"
        )


@router.post("/api/integrations/{integration_name}/start")
async def start_integration(
    integration_name: str,
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Start a specific integration.
    
    Args:
        integration_name: Name of the integration to start
        
    Returns:
        Success message
    """
    try:
        capture_manager = opencontext._capture_manager
        integration_name = integration_name.lower()
        
        success = capture_manager.start_component(integration_name)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to start integration '{integration_name}'"
            )
        
        return convert_resp(
            data={"message": f"Integration '{integration_name}' started successfully"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error starting integration: {e}")
        return convert_resp(
            code=500,
            status=500,
            message=f"Failed to start integration: {str(e)}"
        )


@router.post("/api/integrations/{integration_name}/stop")
async def stop_integration(
    integration_name: str,
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Stop a specific integration.
    
    Args:
        integration_name: Name of the integration to stop
        
    Returns:
        Success message
    """
    try:
        capture_manager = opencontext._capture_manager
        integration_name = integration_name.lower()
        
        success = capture_manager.stop_component(integration_name)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to stop integration '{integration_name}'"
            )
        
        return convert_resp(
            data={"message": f"Integration '{integration_name}' stopped successfully"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error stopping integration: {e}")
        return convert_resp(
            code=500,
            status=500,
            message=f"Failed to stop integration: {str(e)}"
        )
