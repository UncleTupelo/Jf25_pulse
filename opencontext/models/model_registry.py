#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
ML Model Registry Service
Manages storage and retrieval of machine learning models with metadata
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import sqlite3

from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)


class ModelRegistry:
    """
    Service for managing ML models and their metadata
    
    Features:
    - Model upload and storage
    - Metadata management (version, use case, metrics)
    - Model search by tags, use case, or name
    - Model versioning
    - Model file management
    """

    def __init__(self, db_path: str = "./persist/sqlite/app.db", models_dir: str = "./persist/models"):
        """
        Initialize model registry
        
        Args:
            db_path: Path to SQLite database
            models_dir: Directory to store model files
        """
        self.db_path = db_path
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize database tables for model registry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create models table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    description TEXT,
                    use_case TEXT,
                    model_type TEXT,
                    framework TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    tags TEXT,
                    metrics TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    UNIQUE(name, version)
                )
            """)
            
            # Create model embeddings table for semantic search
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_id INTEGER NOT NULL,
                    embedding_text TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_id) REFERENCES ml_models(id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Model registry database initialized successfully")
            
        except Exception as e:
            logger.exception(f"Error initializing model registry database: {e}")

    def register_model(
        self,
        name: str,
        version: str,
        file_path: Optional[str] = None,
        description: Optional[str] = None,
        use_case: Optional[str] = None,
        model_type: Optional[str] = None,
        framework: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
    ) -> Optional[int]:
        """
        Register a new model
        
        Args:
            name: Model name
            version: Model version
            file_path: Path to model file (will be copied to registry)
            description: Model description
            use_case: Primary use case
            model_type: Type of model (e.g., classification, regression, llm)
            framework: ML framework (e.g., pytorch, tensorflow, sklearn)
            tags: List of tags
            metrics: Performance metrics (e.g., {"accuracy": 0.95, "f1": 0.92})
            metadata: Additional metadata
            created_by: Creator name/email
            
        Returns:
            Model ID if successful, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Copy model file if provided
            stored_file_path = None
            file_size = None
            
            if file_path and os.path.exists(file_path):
                # Create directory for this model
                model_dir = self.models_dir / name / version
                model_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                source_path = Path(file_path)
                dest_path = model_dir / source_path.name
                shutil.copy2(file_path, dest_path)
                
                stored_file_path = str(dest_path)
                file_size = dest_path.stat().st_size
                
                logger.info(f"Copied model file from {file_path} to {stored_file_path}")
            
            # Insert model record
            cursor.execute("""
                INSERT INTO ml_models 
                (name, version, description, use_case, model_type, framework, 
                 file_path, file_size, tags, metrics, metadata, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                version,
                description,
                use_case,
                model_type,
                framework,
                stored_file_path,
                file_size,
                json.dumps(tags) if tags else None,
                json.dumps(metrics) if metrics else None,
                json.dumps(metadata) if metadata else None,
                created_by,
            ))
            
            model_id = cursor.lastrowid
            
            # Create embedding text for semantic search
            embedding_text = f"{name} {version} {description or ''} {use_case or ''} {' '.join(tags or [])}"
            cursor.execute("""
                INSERT INTO model_embeddings (model_id, embedding_text)
                VALUES (?, ?)
            """, (model_id, embedding_text))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Registered model: {name} v{version} (ID: {model_id})")
            return model_id
            
        except sqlite3.IntegrityError:
            logger.error(f"Model already exists: {name} v{version}")
            return None
        except Exception as e:
            logger.exception(f"Error registering model: {e}")
            return None

    def get_model(self, model_id: int) -> Optional[Dict[str, Any]]:
        """
        Get model by ID
        
        Args:
            model_id: Model ID
            
        Returns:
            Model dictionary or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM ml_models WHERE id = ?", (model_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_dict(row)
            return None
            
        except Exception as e:
            logger.exception(f"Error getting model: {e}")
            return None

    def get_model_by_name_version(self, name: str, version: str) -> Optional[Dict[str, Any]]:
        """
        Get model by name and version
        
        Args:
            name: Model name
            version: Model version
            
        Returns:
            Model dictionary or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM ml_models WHERE name = ? AND version = ?",
                (name, version)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_dict(row)
            return None
            
        except Exception as e:
            logger.exception(f"Error getting model: {e}")
            return None

    def search_models(
        self,
        query: Optional[str] = None,
        use_case: Optional[str] = None,
        model_type: Optional[str] = None,
        framework: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search models with filters
        
        Args:
            query: Text query for name/description
            use_case: Filter by use case
            model_type: Filter by model type
            framework: Filter by framework
            tags: Filter by tags
            limit: Maximum results
            
        Returns:
            List of matching models
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            sql = "SELECT * FROM ml_models WHERE is_active = 1"
            params = []
            
            if query:
                sql += " AND (name LIKE ? OR description LIKE ? OR use_case LIKE ?)"
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term])
            
            if use_case:
                sql += " AND use_case = ?"
                params.append(use_case)
            
            if model_type:
                sql += " AND model_type = ?"
                params.append(model_type)
            
            if framework:
                sql += " AND framework = ?"
                params.append(framework)
            
            if tags:
                for tag in tags:
                    sql += " AND tags LIKE ?"
                    params.append(f"%{tag}%")
            
            sql += " ORDER BY updated_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_dict(row) for row in rows]
            
        except Exception as e:
            logger.exception(f"Error searching models: {e}")
            return []

    def list_models(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List all active models
        
        Args:
            limit: Maximum results
            
        Returns:
            List of models
        """
        return self.search_models(limit=limit)

    def update_model_metadata(
        self,
        model_id: int,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update model metadata
        
        Args:
            model_id: Model ID
            description: New description
            tags: New tags
            metrics: New metrics
            metadata: New metadata
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if tags is not None:
                updates.append("tags = ?")
                params.append(json.dumps(tags))
            
            if metrics is not None:
                updates.append("metrics = ?")
                params.append(json.dumps(metrics))
            
            if metadata is not None:
                updates.append("metadata = ?")
                params.append(json.dumps(metadata))
            
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(model_id)
                
                sql = f"UPDATE ml_models SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(sql, params)
                conn.commit()
            
            conn.close()
            return True
            
        except Exception as e:
            logger.exception(f"Error updating model metadata: {e}")
            return False

    def delete_model(self, model_id: int, hard_delete: bool = False) -> bool:
        """
        Delete a model
        
        Args:
            model_id: Model ID
            hard_delete: If True, permanently delete; if False, mark as inactive
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if hard_delete:
                # Get file path first
                cursor.execute("SELECT file_path FROM ml_models WHERE id = ?", (model_id,))
                row = cursor.fetchone()
                
                if row and row[0]:
                    # Delete file
                    file_path = Path(row[0])
                    if file_path.exists():
                        file_path.unlink()
                        # Try to remove parent directories if empty
                        try:
                            file_path.parent.rmdir()
                            file_path.parent.parent.rmdir()
                        except:
                            pass
                
                # Delete record
                cursor.execute("DELETE FROM ml_models WHERE id = ?", (model_id,))
                cursor.execute("DELETE FROM model_embeddings WHERE model_id = ?", (model_id,))
            else:
                # Mark as inactive
                cursor.execute(
                    "UPDATE ml_models SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (model_id,)
                )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.exception(f"Error deleting model: {e}")
            return False

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary"""
        data = dict(row)
        
        # Parse JSON fields
        if data.get('tags'):
            try:
                data['tags'] = json.loads(data['tags'])
            except:
                data['tags'] = []
        
        if data.get('metrics'):
            try:
                data['metrics'] = json.loads(data['metrics'])
            except:
                data['metrics'] = {}
        
        if data.get('metadata'):
            try:
                data['metadata'] = json.loads(data['metadata'])
            except:
                data['metadata'] = {}
        
        return data


# Global instance
_model_registry = None


def get_model_registry() -> ModelRegistry:
    """Get global model registry instance"""
    global _model_registry
    if _model_registry is None:
        _model_registry = ModelRegistry()
    return _model_registry
