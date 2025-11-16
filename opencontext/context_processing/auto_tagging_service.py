#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Auto-Tagging Service
Automatically generates tags and keywords from content using LLM
"""

import asyncio
from typing import List, Dict, Any, Optional

from opencontext.llm.global_vlm_client import generate_with_messages_async
from opencontext.utils.logging_utils import get_logger
from opencontext.utils.json_parser import parse_json_from_response

logger = get_logger(__name__)


class AutoTaggingService:
    """
    Service for automatically generating tags and keywords from content
    """

    TAG_EXTRACTION_PROMPT = """You are an expert at analyzing content and extracting relevant tags and keywords.

Given the following content, extract:
1. Main topics (high-level themes)
2. Keywords (important terms and concepts)
3. Entities (people, organizations, locations, products)
4. Categories (content classification)

Content:
{content}

Respond with a JSON object in the following format:
{{
    "topics": ["topic1", "topic2", ...],
    "keywords": ["keyword1", "keyword2", ...],
    "entities": ["entity1", "entity2", ...],
    "categories": ["category1", "category2", ...]
}}

Keep the response concise and relevant. Limit each array to 10 items maximum."""

    def __init__(self, max_content_length: int = 4000):
        """
        Initialize auto-tagging service
        
        Args:
            max_content_length: Maximum content length to send to LLM
        """
        self._max_content_length = max_content_length

    async def generate_tags(self, content: str, title: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Generate tags from content using LLM
        
        Args:
            content: Content to analyze
            title: Optional title to include in analysis
            
        Returns:
            Dictionary with topics, keywords, entities, and categories
        """
        try:
            # Truncate content if too long
            if len(content) > self._max_content_length:
                content = content[:self._max_content_length] + "..."
            
            # Include title if provided
            if title:
                content = f"Title: {title}\n\n{content}"
            
            # Generate prompt
            prompt = self.TAG_EXTRACTION_PROMPT.format(content=content)
            
            # Call LLM
            messages = [
                {"role": "system", "content": "You are a helpful assistant that extracts tags and keywords from content."},
                {"role": "user", "content": prompt}
            ]
            
            response = await generate_with_messages_async(messages)
            
            if not response:
                logger.warning("Empty response from LLM for tag generation")
                return self._get_default_tags()
            
            # Parse JSON response
            tags_data = parse_json_from_response(response)
            
            if not tags_data:
                logger.warning("Failed to parse JSON from LLM response")
                return self._get_default_tags()
            
            # Validate and clean tags
            result = {
                "topics": self._clean_tags(tags_data.get("topics", [])),
                "keywords": self._clean_tags(tags_data.get("keywords", [])),
                "entities": self._clean_tags(tags_data.get("entities", [])),
                "categories": self._clean_tags(tags_data.get("categories", [])),
            }
            
            logger.info(f"Generated tags: {len(result['topics'])} topics, {len(result['keywords'])} keywords, "
                       f"{len(result['entities'])} entities, {len(result['categories'])} categories")
            
            return result
            
        except Exception as e:
            logger.exception(f"Error generating tags: {e}")
            return self._get_default_tags()

    def generate_tags_sync(self, content: str, title: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Synchronous wrapper for generate_tags
        
        Args:
            content: Content to analyze
            title: Optional title to include in analysis
            
        Returns:
            Dictionary with topics, keywords, entities, and categories
        """
        try:
            # Create new event loop for this call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.generate_tags(content, title))
            finally:
                loop.close()
        except Exception as e:
            logger.exception(f"Error in synchronous tag generation: {e}")
            return self._get_default_tags()

    def _clean_tags(self, tags: List[Any]) -> List[str]:
        """Clean and validate tag list"""
        if not isinstance(tags, list):
            return []
        
        cleaned = []
        for tag in tags:
            if isinstance(tag, str):
                tag = tag.strip()
                if tag and len(tag) > 0 and len(tag) < 100:
                    cleaned.append(tag)
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for tag in cleaned:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                unique.append(tag)
        
        return unique[:10]  # Limit to 10 tags

    def _get_default_tags(self) -> Dict[str, List[str]]:
        """Get default empty tags structure"""
        return {
            "topics": [],
            "keywords": [],
            "entities": [],
            "categories": [],
        }

    def extract_tags_from_file_path(self, file_path: str) -> List[str]:
        """
        Extract basic tags from file path and name
        
        Args:
            file_path: Path to file
            
        Returns:
            List of tags extracted from path
        """
        from pathlib import Path
        
        path = Path(file_path)
        tags = []
        
        # Add file stem as tag
        tags.append(path.stem)
        
        # Add file extension
        if path.suffix:
            tags.append(path.suffix.lstrip('.'))
        
        # Add parent directory names
        for parent in path.parents:
            if parent.name and parent.name not in ['.', '..', '/']:
                tags.append(parent.name)
                if len(tags) >= 5:  # Limit parent directory tags
                    break
        
        return tags


# Global instance
_auto_tagging_service = None


def get_auto_tagging_service() -> AutoTaggingService:
    """Get global auto-tagging service instance"""
    global _auto_tagging_service
    if _auto_tagging_service is None:
        _auto_tagging_service = AutoTaggingService()
    return _auto_tagging_service
