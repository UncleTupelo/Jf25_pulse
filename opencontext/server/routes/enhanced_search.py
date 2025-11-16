#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Enhanced Search API routes
Provides advanced search capabilities with filtering, facets, and ranking
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from opencontext.context_processing.enhanced_search_service import get_enhanced_search_service
from opencontext.server.middleware.auth import auth_dependency
from opencontext.server.utils import convert_resp
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["enhanced_search"])


class EnhancedSearchRequest(BaseModel):
    """Enhanced search request with filters"""
    query: str
    top_k: int = 10
    context_types: Optional[List[str]] = None
    file_types: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    date_from: Optional[str] = None  # ISO format
    date_to: Optional[str] = None  # ISO format
    min_relevance: float = 0.0
    sort_by: str = "relevance"  # relevance, date, importance


class TagSearchRequest(BaseModel):
    """Tag-based search request"""
    tags: List[str]
    top_k: int = 10
    match_all: bool = False


class SimilarSearchRequest(BaseModel):
    """Similarity search request"""
    context_id: str
    top_k: int = 10


@router.post("/api/search/enhanced")
async def enhanced_search(
    request: EnhancedSearchRequest,
    _auth: str = auth_dependency,
):
    """
    Perform enhanced search with multiple filters and sorting options
    
    Supports filtering by:
    - Context types (e.g., semantic, activity, entity)
    - File types (e.g., pdf, docx, xlsx)
    - Tags
    - Date ranges
    - Relevance score threshold
    
    Sorting options:
    - relevance (default)
    - date
    - importance
    """
    try:
        search_service = get_enhanced_search_service()
        
        # Parse dates if provided
        date_from = None
        date_to = None
        
        if request.date_from:
            try:
                date_from = datetime.fromisoformat(request.date_from)
            except:
                return convert_resp(
                    code=400,
                    status=400,
                    message=f"Invalid date_from format: {request.date_from}"
                )
        
        if request.date_to:
            try:
                date_to = datetime.fromisoformat(request.date_to)
            except:
                return convert_resp(
                    code=400,
                    status=400,
                    message=f"Invalid date_to format: {request.date_to}"
                )
        
        # Perform search
        results = search_service.search(
            query=request.query,
            top_k=request.top_k,
            context_types=request.context_types,
            file_types=request.file_types,
            tags=request.tags,
            date_from=date_from,
            date_to=date_to,
            min_relevance=request.min_relevance,
            sort_by=request.sort_by,
        )
        
        return convert_resp(
            data={
                "results": results,
                "total": len(results),
                "query": request.query,
                "filters": {
                    "context_types": request.context_types,
                    "file_types": request.file_types,
                    "tags": request.tags,
                    "date_from": request.date_from,
                    "date_to": request.date_to,
                    "min_relevance": request.min_relevance,
                },
                "sort_by": request.sort_by,
            }
        )
        
    except Exception as e:
        logger.exception(f"Error in enhanced search: {e}")
        return convert_resp(code=500, status=500, message=f"Search failed: {str(e)}")


@router.post("/api/search/by_tags")
async def search_by_tags(
    request: TagSearchRequest,
    _auth: str = auth_dependency,
):
    """
    Search by tags only
    
    Can match any tag (match_all=False) or require all tags (match_all=True)
    """
    try:
        search_service = get_enhanced_search_service()
        
        results = search_service.search_by_tags(
            tags=request.tags,
            top_k=request.top_k,
            match_all=request.match_all,
        )
        
        return convert_resp(
            data={
                "results": results,
                "total": len(results),
                "tags": request.tags,
                "match_all": request.match_all,
            }
        )
        
    except Exception as e:
        logger.exception(f"Error in tag search: {e}")
        return convert_resp(code=500, status=500, message=f"Tag search failed: {str(e)}")


@router.get("/api/search/recent")
async def search_recent(
    days: int = Query(default=7, description="Number of days to look back"),
    top_k: int = Query(default=20, description="Number of results"),
    context_types: Optional[List[str]] = Query(default=None),
    _auth: str = auth_dependency,
):
    """
    Get recently added content
    
    Returns content added within the specified number of days, sorted by date
    """
    try:
        search_service = get_enhanced_search_service()
        
        results = search_service.search_recent(
            days=days,
            top_k=top_k,
            context_types=context_types,
        )
        
        return convert_resp(
            data={
                "results": results,
                "total": len(results),
                "days": days,
                "context_types": context_types,
            }
        )
        
    except Exception as e:
        logger.exception(f"Error in recent search: {e}")
        return convert_resp(code=500, status=500, message=f"Recent search failed: {str(e)}")


@router.post("/api/search/similar")
async def search_similar(
    request: SimilarSearchRequest,
    _auth: str = auth_dependency,
):
    """
    Find content similar to a given context
    
    Uses the context's content to find semantically similar items
    """
    try:
        search_service = get_enhanced_search_service()
        
        results = search_service.search_similar(
            context_id=request.context_id,
            top_k=request.top_k,
        )
        
        return convert_resp(
            data={
                "results": results,
                "total": len(results),
                "context_id": request.context_id,
            }
        )
        
    except Exception as e:
        logger.exception(f"Error in similarity search: {e}")
        return convert_resp(code=500, status=500, message=f"Similarity search failed: {str(e)}")


@router.get("/api/search/facets")
async def get_search_facets(
    query: Optional[str] = Query(default=None, description="Optional query to scope facets"),
    context_types: Optional[List[str]] = Query(default=None),
    _auth: str = auth_dependency,
):
    """
    Get search facets (aggregations) for filtering
    
    Returns counts for:
    - File types
    - Context types
    - Popular tags
    - Date ranges
    
    This helps build a faceted search UI
    """
    try:
        search_service = get_enhanced_search_service()
        
        facets = search_service.get_facets(
            query=query,
            context_types=context_types,
        )
        
        return convert_resp(
            data={
                "facets": facets,
                "query": query,
                "context_types": context_types,
            }
        )
        
    except Exception as e:
        logger.exception(f"Error getting facets: {e}")
        return convert_resp(code=500, status=500, message=f"Failed to get facets: {str(e)}")
