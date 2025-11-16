# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Context capture module - responsible for capturing context information from various sources
"""

from opencontext.context_capture.base import BaseCaptureComponent
from opencontext.context_capture.screenshot import ScreenshotCapture
from opencontext.context_capture.vault_document_monitor import VaultDocumentMonitor
from opencontext.context_capture.cloud_adapter_base import CloudAdapterBase
from opencontext.context_capture.google_drive_capture import GoogleDriveCapture
from opencontext.context_capture.icloud_capture import ICloudCapture
from opencontext.context_capture.onedrive_capture import OneDriveCapture
from opencontext.context_capture.notion_capture import NotionCapture
from opencontext.context_capture.chatgpt_capture import ChatGPTCapture
from opencontext.context_capture.perplexity_capture import PerplexityCapture
from opencontext.context_capture.file_upload_capture import FileUploadCapture

__all__ = [
    "BaseCaptureComponent",
    "ScreenshotCapture",
    "VaultDocumentMonitor",
    "CloudAdapterBase",
    "GoogleDriveCapture",
    "ICloudCapture",
    "OneDriveCapture",
    "NotionCapture",
    "ChatGPTCapture",
    "PerplexityCapture",
    "FileUploadCapture",
]
