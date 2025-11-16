#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
File upload handler for context capture.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from opencontext.context_capture.base import BaseCaptureComponent
from opencontext.models.context import RawContextProperties
from opencontext.models.enums import ContentFormat, ContextSource
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class FileUploadCapture(BaseCaptureComponent):
    """
    File upload capture component.

    Handles manual file uploads via API or command-line.
    """

    def __init__(self):
        """Initialize file upload capture component."""
        super().__init__(
            name="FileUploadCapture",
            description="Handle manual file uploads",
            source_type=ContextSource.FILE_UPLOAD,
        )
        self._storage_path = None
        self._max_file_size_mb = 100
        self._allowed_extensions = []
        self._uploaded_files = []

    def _validate_config_impl(self, config: Dict[str, Any]) -> bool:
        """
        Validate file upload configuration.

        Args:
            config: Configuration dictionary

        Returns:
            True if configuration is valid
        """
        if "storage_path" not in config or not config["storage_path"]:
            logger.error(f"{self._name}: storage_path is required")
            return False

        return True

    def _initialize_impl(self, config: Dict[str, Any]) -> bool:
        """
        Initialize file upload component.

        Args:
            config: Configuration dictionary

        Returns:
            True if initialization successful
        """
        try:
            self._storage_path = Path(config.get("storage_path"))
            self._max_file_size_mb = config.get("max_file_size_mb", 100)
            self._allowed_extensions = config.get("allowed_extensions", [])

            # Create storage directory if it doesn't exist
            self._storage_path.mkdir(parents=True, exist_ok=True)

            logger.info(f"{self._name}: Initialized with storage path: {self._storage_path}")
            return True

        except Exception as e:
            logger.exception(f"{self._name}: Initialization failed: {str(e)}")
            return False

    def _start_impl(self) -> bool:
        """
        Start file upload handler.

        Returns:
            True if started successfully
        """
        logger.info(f"{self._name}: Started")
        return True

    def _stop_impl(self, graceful: bool = True) -> bool:
        """
        Stop file upload handler.

        Args:
            graceful: Whether to stop gracefully

        Returns:
            True if stopped successfully
        """
        logger.info(f"{self._name}: Stopped")
        return True

    def _capture_impl(self) -> List[RawContextProperties]:
        """
        Process uploaded files.

        Returns:
            List of captured context data
        """
        # File upload capture is primarily event-driven via upload_file method
        # This method can check for new files in the storage directory
        return []

    def upload_file(
        self, file_data: bytes, file_name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[RawContextProperties]:
        """
        Upload and process a file.

        Args:
            file_data: File content as bytes
            file_name: Name of the file
            metadata: Optional metadata dictionary

        Returns:
            RawContextProperties or None if upload fails
        """
        try:
            # Validate file extension
            file_ext = os.path.splitext(file_name)[1].lower()
            if self._allowed_extensions and file_ext not in self._allowed_extensions:
                logger.warning(f"{self._name}: File extension {file_ext} not allowed")
                return None

            # Validate file size
            file_size_mb = len(file_data) / (1024 * 1024)
            if file_size_mb > self._max_file_size_mb:
                logger.warning(
                    f"{self._name}: File size {file_size_mb:.2f}MB exceeds limit "
                    f"{self._max_file_size_mb}MB"
                )
                return None

            # Save file to storage
            file_path = self._storage_path / file_name

            # Avoid overwriting existing files
            if file_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name, ext = os.path.splitext(file_name)
                file_name = f"{name}_{timestamp}{ext}"
                file_path = self._storage_path / file_name

            file_path.write_bytes(file_data)
            logger.info(f"{self._name}: Saved file to {file_path}")

            # Determine content format
            content_format = self._determine_content_format(file_name)

            # Create context
            context_metadata = {
                "file_name": file_name,
                "file_path": str(file_path),
                "file_size": len(file_data),
                "upload_time": datetime.now().isoformat(),
            }

            # Merge with provided metadata
            if metadata:
                context_metadata.update(metadata)

            context = RawContextProperties(
                source=self._source_type,
                content_format=content_format,
                raw_data=file_data,
                metadata=context_metadata,
            )

            self._uploaded_files.append(
                {
                    "file_name": file_name,
                    "file_path": str(file_path),
                    "upload_time": datetime.now(),
                }
            )

            # Trigger callback if set
            if self._callback:
                self._callback([context])

            return context

        except Exception as e:
            logger.exception(f"{self._name}: File upload failed: {str(e)}")
            return None

    def _determine_content_format(self, file_name: str) -> ContentFormat:
        """
        Determine content format based on file extension.

        Args:
            file_name: Name of the file

        Returns:
            ContentFormat enum value
        """
        file_ext = os.path.splitext(file_name)[1].lower()

        # Image formats
        if file_ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
            return ContentFormat.IMAGE

        # Text formats
        if file_ext in [".txt", ".md", ".json", ".csv"]:
            return ContentFormat.TEXT

        # Default to file format
        return ContentFormat.FILE

    def _get_status_impl(self) -> Dict[str, Any]:
        """
        Get file upload handler status.

        Returns:
            Status information dictionary
        """
        return {
            "storage_path": str(self._storage_path),
            "max_file_size_mb": self._max_file_size_mb,
            "allowed_extensions": self._allowed_extensions,
            "uploaded_files_count": len(self._uploaded_files),
        }

    def _get_config_schema_impl(self) -> Dict[str, Any]:
        """
        Get configuration schema for file upload.

        Returns:
            Configuration schema dictionary
        """
        return {
            "properties": {
                "storage_path": {
                    "type": "string",
                    "description": "Path to store uploaded files",
                },
                "max_file_size_mb": {
                    "type": "integer",
                    "description": "Maximum file size in MB",
                    "default": 100,
                    "minimum": 1,
                },
                "allowed_extensions": {
                    "type": "array",
                    "description": "List of allowed file extensions",
                    "items": {"type": "string"},
                },
            },
            "required": ["storage_path"],
        }
