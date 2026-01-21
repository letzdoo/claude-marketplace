"""
Database schema and utilities for ReasoningBank.

Schema based on the ReasoningBank paper's memory structure with
extensions for consolidation, governance, and MaTTS orchestration.
"""

import aiosqlite
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_DB_PATH = os.path.expanduser("~/.reasoningbank/memory.db")


class Database:
    """Async SQLite database manager for ReasoningBank."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def init_schema(self):
        """Initialize database schema with all required tables."""
        async with aiosqlite.connect(self.db_path) as db:
            # Enable WAL mode for better concurrency
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA foreign_keys=ON")

            # Patterns table - stores reasoning memories
            # Reuses existing pattern storage concept
            await db.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    confidence REAL DEFAULT 0.7,
                    usage_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_used TEXT DEFAULT CURRENT_TIMESTAMP,
                    tenant_id TEXT DEFAULT 'default'
                )
            """)

            # Embeddings for retrieval
            await db.execute("""
                CREATE TABLE IF NOT EXISTS pattern_embeddings (
                    id TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    dims INTEGER NOT NULL,
                    vector BLOB NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id) REFERENCES patterns(id) ON DELETE CASCADE
                )
            """)

            # Links between memories for governance
            await db.execute("""
                CREATE TABLE IF NOT EXISTS pattern_links (
                    src_id TEXT NOT NULL,
                    dst_id TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (src_id, dst_id, relation),
                    FOREIGN KEY (src_id) REFERENCES patterns(id) ON DELETE CASCADE,
                    FOREIGN KEY (dst_id) REFERENCES patterns(id) ON DELETE CASCADE
                )
            """)

            # Task trajectory archive
            await db.execute("""
                CREATE TABLE IF NOT EXISTS task_trajectories (
                    task_id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    query TEXT NOT NULL,
                    trajectory_json TEXT NOT NULL,
                    started_at TEXT,
                    ended_at TEXT,
                    judge_label TEXT,
                    judge_conf REAL,
                    matts_run_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # MaTTS run bookkeeping
            await db.execute("""
                CREATE TABLE IF NOT EXISTS matts_runs (
                    run_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    k INTEGER NOT NULL,
                    status TEXT DEFAULT 'completed',
                    summary TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Events for audit trail
            await db.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    entity_id TEXT,
                    entity_type TEXT,
                    data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Performance metrics
            await db.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    context TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for performance
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_patterns_type
                ON patterns(type)
            """)

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_patterns_tenant
                ON patterns(tenant_id)
            """)

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_pattern_links_src
                ON pattern_links(src_id)
            """)

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_pattern_links_dst
                ON pattern_links(dst_id)
            """)

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_trajectories_label
                ON task_trajectories(judge_label)
            """)

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_type
                ON events(event_type)
            """)

            await db.commit()

    async def get_connection(self) -> aiosqlite.Connection:
        """Get a database connection."""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys=ON")
        return conn

    async def insert_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        confidence: float = 0.7,
        tenant_id: str = "default"
    ) -> None:
        """Insert a new reasoning memory pattern."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            await db.execute("""
                INSERT INTO patterns (id, type, pattern_data, confidence, tenant_id)
                VALUES (?, ?, ?, ?, ?)
            """, (pattern_id, pattern_type, json.dumps(pattern_data), confidence, tenant_id))
            await db.commit()

    async def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a pattern by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            async with db.execute("""
                SELECT * FROM patterns WHERE id = ?
            """, (pattern_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def get_all_patterns(
        self,
        pattern_type: str = "reasoning_memory",
        tenant_id: str = "default"
    ) -> List[Dict[str, Any]]:
        """Get all patterns of a given type."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            async with db.execute("""
                SELECT * FROM patterns
                WHERE type = ? AND tenant_id = ?
                ORDER BY created_at DESC
            """, (pattern_type, tenant_id)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def update_pattern_usage(
        self,
        pattern_id: str,
        confidence_delta: float = 0.0
    ) -> None:
        """Update pattern usage statistics."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            await db.execute("""
                UPDATE patterns
                SET usage_count = usage_count + 1,
                    last_used = CURRENT_TIMESTAMP,
                    confidence = MIN(1.0, MAX(0.0, confidence + ?))
                WHERE id = ?
            """, (confidence_delta, pattern_id))
            await db.commit()

    async def insert_embedding(
        self,
        pattern_id: str,
        model: str,
        vector: bytes,
        dims: int
    ) -> None:
        """Insert an embedding for a pattern."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            await db.execute("""
                INSERT OR REPLACE INTO pattern_embeddings (id, model, dims, vector)
                VALUES (?, ?, ?, ?)
            """, (pattern_id, model, dims, vector))
            await db.commit()

    async def get_embedding(self, pattern_id: str) -> Optional[bytes]:
        """Get embedding for a pattern."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            async with db.execute("""
                SELECT vector FROM pattern_embeddings WHERE id = ?
            """, (pattern_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row['vector']
                return None

    async def get_all_embeddings(self, model: str) -> List[tuple]:
        """Get all embeddings for a model."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            async with db.execute("""
                SELECT id, vector, dims FROM pattern_embeddings WHERE model = ?
            """, (model,)) as cursor:
                return await cursor.fetchall()

    async def insert_link(
        self,
        src_id: str,
        dst_id: str,
        relation: str,
        weight: float = 1.0
    ) -> None:
        """Insert a link between two patterns."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            await db.execute("""
                INSERT OR REPLACE INTO pattern_links (src_id, dst_id, relation, weight)
                VALUES (?, ?, ?, ?)
            """, (src_id, dst_id, relation, weight))
            await db.commit()

    async def get_links(
        self,
        pattern_id: str,
        relation: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all links for a pattern."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            if relation:
                query = """
                    SELECT * FROM pattern_links
                    WHERE (src_id = ? OR dst_id = ?) AND relation = ?
                """
                params = (pattern_id, pattern_id, relation)
            else:
                query = """
                    SELECT * FROM pattern_links
                    WHERE src_id = ? OR dst_id = ?
                """
                params = (pattern_id, pattern_id)

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def insert_trajectory(
        self,
        task_id: str,
        agent_id: str,
        query: str,
        trajectory_json: str,
        started_at: Optional[str] = None,
        ended_at: Optional[str] = None,
        judge_label: Optional[str] = None,
        judge_conf: Optional[float] = None,
        matts_run_id: Optional[str] = None
    ) -> None:
        """Insert a task trajectory."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            await db.execute("""
                INSERT OR REPLACE INTO task_trajectories
                (task_id, agent_id, query, trajectory_json, started_at, ended_at,
                 judge_label, judge_conf, matts_run_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (task_id, agent_id, query, trajectory_json, started_at,
                  ended_at, judge_label, judge_conf, matts_run_id))
            await db.commit()

    async def insert_matts_run(
        self,
        run_id: str,
        task_id: str,
        mode: str,
        k: int,
        summary: str,
        status: str = "completed"
    ) -> None:
        """Insert a MaTTS run record."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            await db.execute("""
                INSERT INTO matts_runs (run_id, task_id, mode, k, status, summary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (run_id, task_id, mode, k, status, summary))
            await db.commit()

    async def log_event(
        self,
        event_type: str,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an event for audit trail."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            await db.execute("""
                INSERT INTO events (event_type, entity_id, entity_type, data)
                VALUES (?, ?, ?, ?)
            """, (event_type, entity_id, entity_type,
                  json.dumps(data) if data else None))
            await db.commit()

    async def log_metric(
        self,
        metric_name: str,
        metric_value: float,
        context: Optional[str] = None
    ) -> None:
        """Log a performance metric."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            await db.execute("""
                INSERT INTO performance_metrics (metric_name, metric_value, context)
                VALUES (?, ?, ?)
            """, (metric_name, metric_value, context))
            await db.commit()

    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        db = await self.get_connection()
        try:
            stats = {}

            # Count patterns
            async with db.execute("""
                SELECT COUNT(*) as count FROM patterns
                WHERE type = 'reasoning_memory'
            """) as cursor:
                row = await cursor.fetchone()
                stats['total_memories'] = row['count']

            # Count trajectories
            async with db.execute("""
                SELECT COUNT(*) as count FROM task_trajectories
            """) as cursor:
                row = await cursor.fetchone()
                stats['total_trajectories'] = row['count']

            # Success rate
            async with db.execute("""
                SELECT
                    SUM(CASE WHEN judge_label = 'Success' THEN 1 ELSE 0 END) as successes,
                    SUM(CASE WHEN judge_label = 'Failure' THEN 1 ELSE 0 END) as failures
                FROM task_trajectories
                WHERE judge_label IS NOT NULL
            """) as cursor:
                row = await cursor.fetchone()
                total = (row['successes'] or 0) + (row['failures'] or 0)
                stats['success_rate'] = (
                    (row['successes'] or 0) / total if total > 0 else 0.0
                )

            # Average confidence
            async with db.execute("""
                SELECT AVG(confidence) as avg_conf FROM patterns
                WHERE type = 'reasoning_memory'
            """) as cursor:
                row = await cursor.fetchone()
                stats['avg_confidence'] = row['avg_conf'] or 0.0

            # Most used memories
            async with db.execute("""
                SELECT id, pattern_data, usage_count
                FROM patterns
                WHERE type = 'reasoning_memory'
                ORDER BY usage_count DESC
                LIMIT 5
            """) as cursor:
                rows = await cursor.fetchall()
                stats['top_memories'] = [
                    {
                        'id': row['id'],
                        'title': json.loads(row['pattern_data']).get('title', 'Untitled'),
                        'usage_count': row['usage_count']
                    }
                    for row in rows
                ]

            return stats
        finally:
            await db.close()

    async def prune_old_patterns(
        self,
        min_confidence: float = 0.3,
        max_age_days: int = 180
    ) -> int:
        """Prune old, unused patterns."""
        db = await self.get_connection()
        try:
            result = await db.execute("""
                DELETE FROM patterns
                WHERE type = 'reasoning_memory'
                  AND usage_count = 0
                  AND confidence < ?
                  AND julianday('now') - julianday(created_at) > ?
            """, (min_confidence, max_age_days))
            await db.commit()
            return result.rowcount
        finally:
            await db.close()


# Singleton instance
_db: Optional[Database] = None


def get_database(db_path: str = DEFAULT_DB_PATH) -> Database:
    """Get or create database instance."""
    global _db
    if _db is None or _db.db_path != db_path:
        _db = Database(db_path)
    return _db
