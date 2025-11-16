#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Enhanced Search Service
Provides advanced search capabilities across all data types with filtering and ranking
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from opencontext.storage.global_storage import get_storage
from opencontext.models.enums import ContextType
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class EnhancedSearchService:
    """
    Advanced search service with multi-source search, filtering, and ranking
    """

    def __init__(self):
        self.storage = get_storage()

    def search(
        self,
        query: str,
        top_k: int = 10,
        context_types: Optional[List[str]] = None,
        file_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        min_relevance: float = 0.0,
        sort_by: str = "relevance",  # relevance, date, importance
    ) -> List[Dict[str, Any]]:
        """
        Advanced search with multiple filters
        
        Args:
            query: Search query
            top_k: Number of results to return
            context_types: Filter by context types
            file_types: Filter by file types (e.g., ["pdf", "docx"])
            tags: Filter by tags
            date_from: Filter by creation date (from)
            date_to: Filter by creation date (to)
            min_relevance: Minimum relevance score
            sort_by: Sort criteria
            
        Returns:
            List of search results with metadata
        """
        try:
            # Build filters
            filters = {}
            
            if context_types:
                filters["context_types"] = context_types
            
            # Perform vector search
            results = self.storage.search_context(
                query=query,
                top_k=top_k * 2,  # Get more results for filtering
                context_types=context_types,
            )
            
            if not results:
                return []
            
            # Apply additional filters
            filtered_results = []
            
            for result in results:
                # Filter by relevance score
                if result.get("distance", 1.0) < min_relevance:
                    continue
                
                metadata = result.get("metadata", {})
                
                # Filter by file type
                if file_types:
                    file_ext = metadata.get("file_extension", "").lstrip('.')
                    if file_ext not in file_types:
                        continue
                
                # Filter by tags
                if tags:
                    result_tags = metadata.get("tags", [])
                    if not any(tag in result_tags for tag in tags):
                        continue
                
                # Filter by date
                if date_from or date_to:
                    created = metadata.get("created_time")
                    if created:
                        try:
                            created_dt = datetime.fromisoformat(created)
                            if date_from and created_dt < date_from:
                                continue
                            if date_to and created_dt > date_to:
                                continue
                        except:
                            pass
                
                # Enhance result with additional info
                enhanced_result = {
                    **result,
                    "relevance_score": 1.0 - result.get("distance", 0.0),
                    "importance": metadata.get("importance", 50),
                }
                
                filtered_results.append(enhanced_result)
            
            # Sort results
            if sort_by == "relevance":
                filtered_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            elif sort_by == "date":
                filtered_results.sort(
                    key=lambda x: x.get("metadata", {}).get("created_time", ""),
                    reverse=True
                )
            elif sort_by == "importance":
                filtered_results.sort(key=lambda x: x.get("importance", 0), reverse=True)
            
            return filtered_results[:top_k]
            
        except Exception as e:
            logger.exception(f"Error in enhanced search: {e}")
            return []

    def search_by_tags(
        self, tags: List[str], top_k: int = 10, match_all: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search by tags only
        
        Args:
            tags: List of tags to search for
            top_k: Number of results to return
            match_all: If True, require all tags to match; if False, match any
            
        Returns:
            List of matching results
        """
        try:
            # For now, perform a vector search with tag-based query
            # In a full implementation, this would query a tag index
            query = " ".join(tags)
            
            results = self.search(
                query=query,
                top_k=top_k,
                tags=tags if not match_all else None,
            )
            
            if match_all:
                # Filter to only results with all tags
                filtered = []
                for result in results:
                    result_tags = result.get("metadata", {}).get("tags", [])
                    if all(tag in result_tags for tag in tags):
                        filtered.append(result)
                return filtered[:top_k]
            
            return results
            
        except Exception as e:
            logger.exception(f"Error in tag-based search: {e}")
            return []

    def search_recent(
        self, days: int = 7, top_k: int = 20, context_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for recently added content
        
        Args:
            days: Number of days to look back
            top_k: Number of results to return
            context_types: Filter by context types
            
        Returns:
            List of recent results
        """
        try:
            date_from = datetime.now() - timedelta(days=days)
            
            # Use a generic query to get all recent content
            results = self.search(
                query="",
                top_k=top_k,
                context_types=context_types,
                date_from=date_from,
                sort_by="date",
            )
            
            return results
            
        except Exception as e:
            logger.exception(f"Error in recent search: {e}")
            return []

    def search_similar(
        self, context_id: str, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find similar content to a given context
        
        Args:
            context_id: ID of the context to find similar items for
            top_k: Number of similar results to return
            
        Returns:
            List of similar results
        """
        try:
            # Get the context
            context = self.storage.get_context_by_id(context_id)
            
            if not context:
                logger.warning(f"Context not found: {context_id}")
                return []
            
            # Use context summary or title for similarity search
            query = context.get("summary") or context.get("title") or ""
            
            if not query:
                return []
            
            results = self.search(query=query, top_k=top_k + 1)
            
            # Remove the original context from results
            filtered = [r for r in results if r.get("id") != context_id]
            
            return filtered[:top_k]
            
        except Exception as e:
            logger.exception(f"Error in similarity search: {e}")
            return []

    def get_facets(
        self, query: Optional[str] = None, context_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get search facets (aggregations) for filtering
        
        Args:
            query: Optional search query to scope facets
            context_types: Filter by context types
            
        Returns:
            Dictionary with facet counts
        """
        try:
            # Get search results or all contexts
            if query:
                results = self.search(query=query, top_k=100, context_types=context_types)
            else:
                # Get sample of contexts for facets
                results = self.storage.search_context(query="", top_k=100)
            
            facets = {
                "file_types": {},
                "context_types": {},
                "tags": {},
                "date_ranges": {
                    "last_day": 0,
                    "last_week": 0,
                    "last_month": 0,
                    "older": 0,
                },
            }
            
            now = datetime.now()
            
            for result in results:
                metadata = result.get("metadata", {})
                
                # File type facet
                file_ext = metadata.get("file_extension", "unknown").lstrip('.')
                facets["file_types"][file_ext] = facets["file_types"].get(file_ext, 0) + 1
                
                # Context type facet
                ctx_type = metadata.get("context_type", "unknown")
                facets["context_types"][ctx_type] = facets["context_types"].get(ctx_type, 0) + 1
                
                # Tags facet
                for tag in metadata.get("tags", [])[:5]:  # Limit tags per result
                    facets["tags"][tag] = facets["tags"].get(tag, 0) + 1
                
                # Date range facet
                created = metadata.get("created_time")
                if created:
                    try:
                        created_dt = datetime.fromisoformat(created)
                        days_ago = (now - created_dt).days
                        
                        if days_ago < 1:
                            facets["date_ranges"]["last_day"] += 1
                        elif days_ago < 7:
                            facets["date_ranges"]["last_week"] += 1
                        elif days_ago < 30:
                            facets["date_ranges"]["last_month"] += 1
                        else:
                            facets["date_ranges"]["older"] += 1
                    except:
                        pass
            
            # Sort tags by count and limit
            facets["tags"] = dict(
                sorted(facets["tags"].items(), key=lambda x: x[1], reverse=True)[:20]
            )
            
            return facets
            
        except Exception as e:
            logger.exception(f"Error getting facets: {e}")
            return {}


# Global instance
_enhanced_search_service = None


def get_enhanced_search_service() -> EnhancedSearchService:
    """Get global enhanced search service instance"""
    global _enhanced_search_service
    if _enhanced_search_service is None:
        _enhanced_search_service = EnhancedSearchService()
    return _enhanced_search_service
