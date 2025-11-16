#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Base class for cloud storage adapters.
Provides common functionality for cloud storage integrations.
"""

import abc
from datetime import datetime
from typing import Any, Dict, List, Optional

from opencontext.context_capture.base import BaseCaptureComponent
from opencontext.models.context import RawContextProperties
from opencontext.models.enums import ContextSource, ContentFormat
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class CloudAdapterBase(BaseCaptureComponent):
    """
    Base class for cloud storage adapters.
    
    Provides common functionality for all cloud storage integrations including:
    - Authentication management
    - File metadata extraction
    - Selective folder syncing
    - Rate limiting and error handling
    """

    def __init__(self, name: str, description: str, source_type: ContextSource):
        """
        Initialize cloud adapter.
        
        Args:
            name: Adapter name
            description: Adapter description
            source_type: Cloud storage source type
        """
        super().__init__(name, description, source_type)
        self._authenticated = False
        self._sync_folders = []
        self._file_types = []
        self._last_sync_time = None
        self._synced_file_ids = set()  # Track synced files to avoid duplicates

    def _validate_config_impl(self, config: Dict[str, Any]) -> bool:
        """
        Validate cloud adapter configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if configuration is valid
        """
        # Check for required authentication fields (to be implemented by subclasses)
        if not self._validate_auth_config(config):
            logger.error(f"{self._name}: Authentication configuration is invalid")
            return False
            
        # Validate sync_interval
        if "sync_interval" in config:
            try:
                interval = int(config["sync_interval"])
                if interval < 60:
                    logger.warning(f"{self._name}: sync_interval less than 60 seconds may cause rate limiting")
            except (ValueError, TypeError):
                logger.error(f"{self._name}: sync_interval must be an integer")
                return False
        
        return True

    def _initialize_impl(self, config: Dict[str, Any]) -> bool:
        """
        Initialize cloud adapter with configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if initialization successful
        """
        try:
            # Store sync configuration
            self._sync_folders = config.get("sync_folders", [])
            self._file_types = config.get("file_types", [])
            
            # Attempt authentication
            if not self._authenticate(config):
                logger.error(f"{self._name}: Authentication failed")
                return False
                
            self._authenticated = True
            logger.info(f"{self._name}: Successfully authenticated")
            return True
            
        except Exception as e:
            logger.exception(f"{self._name}: Initialization failed: {str(e)}")
            return False

    def _start_impl(self) -> bool:
        """
        Start the cloud adapter.
        
        Returns:
            True if started successfully
        """
        if not self._authenticated:
            logger.error(f"{self._name}: Cannot start - not authenticated")
            return False
            
        logger.info(f"{self._name}: Started successfully")
        return True

    def _stop_impl(self, graceful: bool = True) -> bool:
        """
        Stop the cloud adapter.
        
        Args:
            graceful: Whether to stop gracefully
            
        Returns:
            True if stopped successfully
        """
        logger.info(f"{self._name}: Stopped")
        return True

    def _capture_impl(self) -> List[RawContextProperties]:
        """
        Capture files from cloud storage.
        
        Returns:
            List of captured context data
        """
        if not self._authenticated:
            logger.warning(f"{self._name}: Not authenticated, skipping capture")
            return []
            
        try:
            # Get list of files to sync
            files = self._list_files()
            
            # Filter files based on sync folders and file types
            filtered_files = self._filter_files(files)
            
            # Download and process files
            contexts = []
            for file_info in filtered_files:
                # Skip if already synced
                file_id = file_info.get("id")
                if file_id in self._synced_file_ids:
                    continue
                    
                # Download file content
                content = self._download_file(file_info)
                if content is None:
                    continue
                    
                # Create context from file
                context = self._create_context_from_file(file_info, content)
                if context:
                    contexts.append(context)
                    self._synced_file_ids.add(file_id)
            
            if contexts:
                self._last_sync_time = datetime.now()
                logger.info(f"{self._name}: Captured {len(contexts)} items")
                
            return contexts
            
        except Exception as e:
            logger.exception(f"{self._name}: Capture failed: {str(e)}")
            return []

    def _filter_files(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter files based on sync folders and file types.
        
        Args:
            files: List of file information dictionaries
            
        Returns:
            Filtered list of files
        """
        filtered = []
        for file_info in files:
            # Check folder filter
            if self._sync_folders:
                file_path = file_info.get("path", "")
                if not any(folder in file_path for folder in self._sync_folders):
                    continue
                    
            # Check file type filter
            if self._file_types:
                file_name = file_info.get("name", "")
                if not any(file_name.endswith(ft.replace("*", "")) for ft in self._file_types):
                    continue
                    
            filtered.append(file_info)
            
        return filtered

    def _create_context_from_file(
        self, 
        file_info: Dict[str, Any], 
        content: bytes
    ) -> Optional[RawContextProperties]:
        """
        Create a RawContextProperties object from file information and content.
        
        Args:
            file_info: File metadata dictionary
            content: File content as bytes
            
        Returns:
            RawContextProperties object or None if creation fails
        """
        try:
            file_name = file_info.get("name", "unknown")
            file_path = file_info.get("path", "")
            file_size = file_info.get("size", 0)
            modified_time = file_info.get("modified_time")
            
            # Determine content format
            content_format = ContentFormat.FILE
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                content_format = ContentFormat.IMAGE
            elif file_name.lower().endswith(('.txt', '.md', '.json', '.csv')):
                content_format = ContentFormat.TEXT
            
            # Create context properties
            context = RawContextProperties(
                source=self._source_type,
                content_format=content_format,
                raw_data=content,
                metadata={
                    "file_name": file_name,
                    "file_path": file_path,
                    "file_size": file_size,
                    "modified_time": modified_time.isoformat() if modified_time else None,
                    "cloud_source": self._source_type.value,
                    "file_id": file_info.get("id"),
                }
            )
            
            return context
            
        except Exception as e:
            logger.exception(f"{self._name}: Failed to create context from file: {str(e)}")
            return None

    def _get_status_impl(self) -> Dict[str, Any]:
        """
        Get adapter status.
        
        Returns:
            Status information dictionary
        """
        return {
            "authenticated": self._authenticated,
            "last_sync_time": self._last_sync_time.isoformat() if self._last_sync_time else None,
            "synced_files_count": len(self._synced_file_ids),
            "sync_folders": self._sync_folders,
            "file_types": self._file_types,
        }

    # Abstract methods to be implemented by subclasses

    @abc.abstractmethod
    def _validate_auth_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate authentication configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if authentication config is valid
        """

    @abc.abstractmethod
    def _authenticate(self, config: Dict[str, Any]) -> bool:
        """
        Authenticate with cloud service.
        
        Args:
            config: Configuration dictionary containing credentials
            
        Returns:
            True if authentication successful
        """

    @abc.abstractmethod
    def _list_files(self) -> List[Dict[str, Any]]:
        """
        List files from cloud storage.
        
        Returns:
            List of file information dictionaries
        """

    @abc.abstractmethod
    def _download_file(self, file_info: Dict[str, Any]) -> Optional[bytes]:
        """
        Download file content from cloud storage.
        
        Args:
            file_info: File information dictionary
            
        Returns:
            File content as bytes, or None if download fails
        """
