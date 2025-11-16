#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Storage backend package initialization file
"""

from .chromadb_backend import ChromaDBBackend
from .notion_backend import NotionBackend
from .sqlite_backend import SQLiteBackend

try:
    __all__ = ["SQLiteBackend", "ChromaDBBackend", "NotionBackend"]
except ImportError:
    __all__ = ["SQLiteBackend", "ChromaDBBackend", "NotionBackend"]
