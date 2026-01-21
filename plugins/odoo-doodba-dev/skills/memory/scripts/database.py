"""Database management for Claude Memory skill."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from config import MEMORY_DB_PATH


class MemoryDatabase:
    """Manages the SQLite database for storing project memory."""

    def __init__(self, db_path: Path = MEMORY_DB_PATH):
        """Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self):
        """Create the database schema if it doesn't exist."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # Create memory_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    context TEXT,
                    category TEXT,
                    project_path TEXT NOT NULL,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(key, project_path)
                )
            """)

            # Create memory_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    project_path TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for fast lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_key
                ON memory_items(key)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_category
                ON memory_items(category)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_project
                ON memory_items(project_path)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_created
                ON memory_items(created_at)
            """)

            conn.commit()
        finally:
            conn.close()

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection.

        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def store_memory(
        self,
        key: str,
        value: str,
        project_path: str,
        context: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """Store or update a memory item.

        Args:
            key: Unique key for the memory item
            value: The memory content
            project_path: Path to the project this memory belongs to
            context: Additional context about the memory
            category: Category of the memory (e.g., "decision", "requirement")
            tags: List of tags for searching

        Returns:
            The ID of the stored memory item
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            tags_json = json.dumps(tags) if tags else None
            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO memory_items (key, value, context, category, project_path, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(key, project_path) DO UPDATE SET
                    value = excluded.value,
                    context = excluded.context,
                    category = excluded.category,
                    tags = excluded.tags,
                    updated_at = excluded.updated_at
            """, (key, value, context, category, project_path, tags_json, now, now))

            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def retrieve_memory(
        self,
        key: str,
        project_path: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a memory item by key.

        Args:
            key: The key of the memory item
            project_path: Path to the project

        Returns:
            Dictionary with memory item data, or None if not found
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, key, value, context, category, project_path, tags, created_at, updated_at
                FROM memory_items
                WHERE key = ? AND project_path = ?
            """, (key, project_path))

            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'key': row['key'],
                    'value': row['value'],
                    'context': row['context'],
                    'category': row['category'],
                    'project_path': row['project_path'],
                    'tags': json.loads(row['tags']) if row['tags'] else [],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
        finally:
            conn.close()

    def search_memory(
        self,
        project_path: str,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search memory items.

        Args:
            project_path: Path to the project
            query: Search query (searches in key, value, and context)
            category: Filter by category
            tags: Filter by tags (returns items with any of the specified tags)
            limit: Maximum number of results

        Returns:
            List of matching memory items
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            sql = """
                SELECT id, key, value, context, category, project_path, tags, created_at, updated_at
                FROM memory_items
                WHERE project_path = ?
            """
            params = [project_path]

            if query:
                sql += " AND (key LIKE ? OR value LIKE ? OR context LIKE ?)"
                query_pattern = f"%{query}%"
                params.extend([query_pattern, query_pattern, query_pattern])

            if category:
                sql += " AND category = ?"
                params.append(category)

            if tags:
                # Search for items that contain any of the specified tags
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append("tags LIKE ?")
                    params.append(f'%"{tag}"%')
                sql += f" AND ({' OR '.join(tag_conditions)})"

            sql += " ORDER BY updated_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(sql, params)

            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'key': row['key'],
                    'value': row['value'],
                    'context': row['context'],
                    'category': row['category'],
                    'project_path': row['project_path'],
                    'tags': json.loads(row['tags']) if row['tags'] else [],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })

            return results
        finally:
            conn.close()

    def list_all_memory(
        self,
        project_path: str,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List all memory items for a project.

        Args:
            project_path: Path to the project
            category: Optional category filter
            limit: Maximum number of results

        Returns:
            List of memory items
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            if category:
                cursor.execute("""
                    SELECT id, key, value, context, category, project_path, tags, created_at, updated_at
                    FROM memory_items
                    WHERE project_path = ? AND category = ?
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (project_path, category, limit))
            else:
                cursor.execute("""
                    SELECT id, key, value, context, category, project_path, tags, created_at, updated_at
                    FROM memory_items
                    WHERE project_path = ?
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (project_path, limit))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'key': row['key'],
                    'value': row['value'],
                    'context': row['context'],
                    'category': row['category'],
                    'project_path': row['project_path'],
                    'tags': json.loads(row['tags']) if row['tags'] else [],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })

            return results
        finally:
            conn.close()

    def delete_memory(
        self,
        key: str,
        project_path: str
    ) -> bool:
        """Delete a memory item.

        Args:
            key: The key of the memory item
            project_path: Path to the project

        Returns:
            True if deleted, False if not found
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM memory_items
                WHERE key = ? AND project_path = ?
            """, (key, project_path))

            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def clear_memory(
        self,
        project_path: str,
        category: Optional[str] = None
    ) -> int:
        """Clear memory items.

        Args:
            project_path: Path to the project
            category: If provided, only clear items in this category

        Returns:
            Number of items deleted
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            if category:
                cursor.execute("""
                    DELETE FROM memory_items
                    WHERE project_path = ? AND category = ?
                """, (project_path, category))
            else:
                cursor.execute("""
                    DELETE FROM memory_items
                    WHERE project_path = ?
                """, (project_path,))

            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def export_memory(
        self,
        project_path: str
    ) -> List[Dict[str, Any]]:
        """Export all memory items for a project.

        Args:
            project_path: Path to the project

        Returns:
            List of all memory items
        """
        return self.list_all_memory(project_path, limit=999999)

    def import_memory(
        self,
        items: List[Dict[str, Any]],
        project_path: str,
        overwrite: bool = False
    ) -> int:
        """Import memory items.

        Args:
            items: List of memory items to import
            project_path: Path to the project
            overwrite: If True, overwrite existing items with same key

        Returns:
            Number of items imported
        """
        count = 0
        for item in items:
            if not overwrite:
                # Check if item already exists
                existing = self.retrieve_memory(item['key'], project_path)
                if existing:
                    continue

            self.store_memory(
                key=item['key'],
                value=item['value'],
                project_path=project_path,
                context=item.get('context'),
                category=item.get('category'),
                tags=item.get('tags')
            )
            count += 1

        return count

    def record_session(
        self,
        session_id: str,
        project_path: str
    ):
        """Record a session access.

        Args:
            session_id: Unique session identifier
            project_path: Path to the project
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO memory_sessions (session_id, project_path, started_at, last_accessed)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    last_accessed = excluded.last_accessed
            """, (session_id, project_path, now, now))

            conn.commit()
        finally:
            conn.close()

    def get_stats(self, project_path: str) -> Dict[str, Any]:
        """Get statistics about stored memory.

        Args:
            project_path: Path to the project

        Returns:
            Dictionary with statistics
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # Total items
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM memory_items
                WHERE project_path = ?
            """, (project_path,))
            total = cursor.fetchone()['count']

            # Items by category
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM memory_items
                WHERE project_path = ?
                GROUP BY category
            """, (project_path,))
            by_category = {row['category'] or 'uncategorized': row['count']
                          for row in cursor.fetchall()}

            # Most recent update
            cursor.execute("""
                SELECT MAX(updated_at) as last_update
                FROM memory_items
                WHERE project_path = ?
            """, (project_path,))
            last_update = cursor.fetchone()['last_update']

            return {
                'total_items': total,
                'by_category': by_category,
                'last_update': last_update,
                'database_path': str(self.db_path)
            }
        finally:
            conn.close()
