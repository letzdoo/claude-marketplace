"""Shared utilities for odoo-indexer query scripts.

This module contains all necessary code for query/search scripts to work independently.
"""

import os
import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

def get_config():
    """Get configuration values with fallbacks."""
    # Required settings
    odoo_path = Path(os.getenv('ODOO_PATH', '/home/coder/letzdoo-sh/odoo/custom/src'))

    if not odoo_path.exists():
        # Fallback to common locations
        possible_paths = [
            Path('/home/coder/letzdoo-sh/odoo/custom/src'),
            Path.home() / 'odoo' / 'custom' / 'src',
            Path.cwd() / 'odoo' / 'custom' / 'src',
        ]
        for path in possible_paths:
            if path.exists():
                odoo_path = path
                break

    # Optional settings
    sqlite_db_path = Path(os.getenv('SQLITE_DB_PATH', str(Path.home() / '.odoo-indexer' / 'odoo_indexer.sqlite3')))
    log_level = os.getenv('LOG_LEVEL', 'INFO')

    return {
        'ODOO_PATH': odoo_path,
        'SQLITE_DB_PATH': sqlite_db_path,
        'LOG_LEVEL': log_level,
    }


# ============================================================================
# Database
# ============================================================================

class Database:
    """Lightweight SQLite database manager for Odoo index."""

    def __init__(self, db_path: Path):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        # Create parent directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic commit/rollback."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self):
        """Create database schema if it doesn't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Main indexed items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS indexed_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    parent_name TEXT,
                    module TEXT NOT NULL,
                    attributes TEXT,
                    dependency_depth INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(item_type, name, parent_name, module)
                )
            """)

            # References table for file locations (one-to-many)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS item_references (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    reference_type TEXT NOT NULL,
                    context TEXT,
                    FOREIGN KEY (item_id) REFERENCES indexed_items(id) ON DELETE CASCADE
                )
            """)

            # File tracking for incremental indexing
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    module TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    last_indexed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for fast lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_type ON indexed_items(item_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_name ON indexed_items(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_parent ON indexed_items(parent_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_module ON indexed_items(module)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_type_name ON indexed_items(item_type, name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dependency_depth ON indexed_items(dependency_depth)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ref_item_id ON item_references(item_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ref_file ON item_references(file_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_path ON file_metadata(file_path)")

    def search_items(self, query: str, item_type: Optional[str] = None,
                    module: Optional[str] = None, parent_name: Optional[str] = None,
                    limit: int = 50, offset: int = 0) -> list[dict]:
        """Search for indexed items.

        Args:
            query: Search term (supports SQL LIKE patterns with %)
            item_type: Filter by item type
            module: Filter by module
            parent_name: Filter by parent name
            limit: Maximum results
            offset: Number of results to skip

        Returns:
            List of items with their references
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build query
            where_clauses = ["name LIKE ?"]
            params = [f"%{query}%"]

            if item_type:
                where_clauses.append("item_type = ?")
                params.append(item_type)

            if module:
                where_clauses.append("module = ?")
                params.append(module)

            if parent_name:
                where_clauses.append("parent_name = ?")
                params.append(parent_name)

            params.extend([limit, offset])

            sql = f"""
                SELECT id, item_type, name, parent_name, module, attributes, dependency_depth
                FROM indexed_items
                WHERE {' AND '.join(where_clauses)}
                ORDER BY
                    CASE WHEN name = ? THEN 0 ELSE 1 END,
                    dependency_depth ASC,
                    name ASC
                LIMIT ? OFFSET ?
            """

            # Add the query parameter for exact match comparison
            params.insert(len(params) - 2, query)

            cursor.execute(sql, params)
            items = []

            for row in cursor.fetchall():
                item = {
                    'id': row['id'],
                    'item_type': row['item_type'],
                    'name': row['name'],
                    'parent_name': row['parent_name'],
                    'module': row['module'],
                    'attributes': json.loads(row['attributes']) if row['attributes'] else {},
                    'dependency_depth': row['dependency_depth'],
                    'references': []
                }

                # Get references
                cursor.execute("""
                    SELECT file_path, line_number, reference_type, context
                    FROM item_references
                    WHERE item_id = ?
                    ORDER BY file_path, line_number
                """, (row['id'],))

                for ref_row in cursor.fetchall():
                    item['references'].append({
                        'file': ref_row['file_path'],
                        'line': ref_row['line_number'],
                        'type': ref_row['reference_type'],
                        'context': ref_row['context']
                    })

                items.append(item)

            return items

    def get_item_details(self, item_type: str, name: str,
                        parent_name: Optional[str] = None,
                        module: Optional[str] = None) -> Optional[dict]:
        """Get complete details for a specific item.

        Args:
            item_type: Type of item
            name: Item name
            parent_name: Parent name (optional)
            module: Module name (optional)

        Returns:
            Item details with references and related items
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build query
            where_clauses = ["item_type = ?", "name = ?"]
            params = [item_type, name]

            if parent_name:
                where_clauses.append("parent_name = ?")
                params.append(parent_name)

            if module:
                where_clauses.append("module = ?")
                params.append(module)

            sql = f"""
                SELECT id, item_type, name, parent_name, module, attributes, dependency_depth
                FROM indexed_items
                WHERE {' AND '.join(where_clauses)}
                LIMIT 1
            """

            cursor.execute(sql, params)
            row = cursor.fetchone()

            if not row:
                return None

            item = {
                'id': row['id'],
                'item_type': row['item_type'],
                'name': row['name'],
                'parent_name': row['parent_name'],
                'module': row['module'],
                'attributes': json.loads(row['attributes']) if row['attributes'] else {},
                'dependency_depth': row['dependency_depth'],
                'references': []
            }

            # Get references
            cursor.execute("""
                SELECT file_path, line_number, reference_type, context
                FROM item_references
                WHERE item_id = ?
                ORDER BY file_path, line_number
            """, (row['id'],))

            for ref_row in cursor.fetchall():
                item['references'].append({
                    'file': ref_row['file_path'],
                    'line': ref_row['line_number'],
                    'type': ref_row['reference_type'],
                    'context': ref_row['context']
                })

            # Get related items for models
            if item_type == 'model':
                item['related_items'] = {
                    'fields': self._get_related_items(cursor, 'field', name),
                    'methods': self._get_related_items(cursor, 'function', name),
                    'views': self._get_related_by_attr(cursor, 'view', 'model', name),
                    'actions': self._get_related_by_attr(cursor, 'action', 'res_model', name),
                    'access_rights': self._get_related_by_attr(cursor, 'access_right', 'model_name', name),
                    'rules': self._get_related_by_attr(cursor, 'record_rule', 'model_name', name),
                }

            return item

    def _get_related_items(self, cursor: sqlite3.Cursor, item_type: str,
                          parent_name: str) -> list[dict]:
        """Get items with matching parent_name."""
        cursor.execute("""
            SELECT name, module, attributes
            FROM indexed_items
            WHERE item_type = ? AND parent_name = ?
            ORDER BY name
        """, (item_type, parent_name))

        return [
            {
                'name': row['name'],
                'module': row['module'],
                'attributes': json.loads(row['attributes']) if row['attributes'] else {}
            }
            for row in cursor.fetchall()
        ]

    def _get_related_by_attr(self, cursor: sqlite3.Cursor, item_type: str,
                            attr_key: str, attr_value: str) -> list[dict]:
        """Get items with matching attribute value."""
        cursor.execute("""
            SELECT name, module, attributes
            FROM indexed_items
            WHERE item_type = ?
        """, (item_type,))

        results = []
        for row in cursor.fetchall():
            attrs = json.loads(row['attributes']) if row['attributes'] else {}
            if attrs.get(attr_key) == attr_value:
                results.append({
                    'name': row['name'],
                    'module': row['module'],
                    'attributes': attrs
                })

        return results

    def get_module_stats(self, module: Optional[str] = None) -> dict:
        """Get statistics for modules.

        Args:
            module: Specific module name, or None for all modules

        Returns:
            Statistics dictionary
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if module:
                cursor.execute("""
                    SELECT item_type, COUNT(*) as count
                    FROM indexed_items
                    WHERE module = ?
                    GROUP BY item_type
                """, (module,))

                counts = {row['item_type']: row['count'] for row in cursor.fetchall()}

                return {
                    'module': module,
                    'counts_by_type': counts
                }
            else:
                cursor.execute("""
                    SELECT module, COUNT(*) as total
                    FROM indexed_items
                    GROUP BY module
                    ORDER BY module
                """)

                modules = []
                for row in cursor.fetchall():
                    modules.append({
                        'module': row['module'],
                        'total_items': row['total']
                    })

                return {
                    'total_modules': len(modules),
                    'modules': modules
                }


# ============================================================================
# Tool implementations (for scripts that need them)
# ============================================================================

def search_odoo_index(
    query: str,
    item_type: Optional[str] = None,
    module: Optional[str] = None,
    parent_name: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """Search for indexed Odoo elements (returns concise results).

    Args:
        query: Search term (supports SQL LIKE patterns with %)
        item_type: Filter by type (model/field/function/view/menu/action/etc)
        module: Filter by module name
        parent_name: Filter by parent (e.g., model name for fields)
        limit: Maximum results (default: 20)
        offset: Number of results to skip for pagination (default: 0)

    Returns:
        Concise search results with only essential info
    """
    config = get_config()
    db = Database(config['SQLITE_DB_PATH'])

    try:
        # Get the paginated results
        items = db.search_items(query, item_type, module, parent_name, limit, offset)

        # Get total count (without limit/offset)
        all_items = db.search_items(query, item_type, module, parent_name, limit=999999)
        total = len(all_items)

        # Return concise results - only definition location
        concise_results = []
        for item in items:
            # Find the definition reference
            definition_ref = next(
                (ref for ref in item['references'] if ref['type'] == 'definition'),
                item['references'][0] if item['references'] else None
            )

            concise_item = {
                'name': item['name'],
                'type': item['item_type'],
                'module': item['module'],
            }

            if item['parent_name']:
                concise_item['parent'] = item['parent_name']

            if definition_ref:
                concise_item['file'] = definition_ref['file']
                concise_item['line'] = definition_ref['line']

            # Add key attributes only
            attrs = item.get('attributes', {})
            if 'description' in attrs:
                concise_item['description'] = attrs['description']
            if 'field_type' in attrs:
                concise_item['field_type'] = attrs['field_type']
            if 'model_type' in attrs:
                concise_item['model_type'] = attrs['model_type']
            if 'view_type' in attrs:
                concise_item['view_type'] = attrs['view_type']

            concise_results.append(concise_item)

        # Calculate pagination info
        has_more = (offset + len(concise_results)) < total
        next_offset = offset + limit if has_more else None

        return {
            'total': total,
            'limit': limit,
            'offset': offset,
            'returned': len(concise_results),
            'has_more': has_more,
            'next_offset': next_offset,
            'results': concise_results
        }
    except Exception as e:
        logger.error(f"Error searching index: {e}")
        return {'error': str(e), 'total': 0, 'limit': limit, 'offset': offset, 'returned': 0, 'results': []}


def get_item_details(
    item_type: str,
    name: str,
    parent_name: Optional[str] = None,
    module: Optional[str] = None
) -> dict:
    """Get complete details for a specific item.

    Args:
        item_type: Type of item (model/field/function/view/etc)
        name: Item name
        parent_name: Parent name (optional, for fields/methods)
        module: Module name (optional, to disambiguate)

    Returns:
        Item details with references and related items
    """
    config = get_config()
    db = Database(config['SQLITE_DB_PATH'])

    try:
        item = db.get_item_details(item_type, name, parent_name, module)

        if item:
            return item
        else:
            return {'error': 'Item not found'}
    except Exception as e:
        logger.error(f"Error getting item details: {e}")
        return {'error': str(e)}


def list_modules(pattern: Optional[str] = None) -> dict:
    """List all indexed Odoo modules.

    Args:
        pattern: Filter by module name pattern (optional)

    Returns:
        List of modules with statistics
    """
    config = get_config()
    db = Database(config['SQLITE_DB_PATH'])

    try:
        stats = db.get_module_stats()

        modules = stats.get('modules', [])

        # Filter by pattern if provided
        if pattern:
            pattern_lower = pattern.lower()
            modules = [m for m in modules if pattern_lower in m['module'].lower()]

        return {
            'total_modules': len(modules),
            'modules': modules
        }
    except Exception as e:
        logger.error(f"Error listing modules: {e}")
        return {'error': str(e), 'total_modules': 0, 'modules': []}


def get_module_stats(module: str) -> dict:
    """Get detailed statistics for a specific module.

    Args:
        module: Module name

    Returns:
        Module statistics
    """
    config = get_config()
    db = Database(config['SQLITE_DB_PATH'])

    try:
        stats = db.get_module_stats(module)
        return stats
    except Exception as e:
        logger.error(f"Error getting module stats: {e}")
        return {'error': str(e)}


def find_references(
    item_type: str,
    name: str,
    reference_type: Optional[str] = None
) -> dict:
    """Find all references to a specific item.

    Args:
        item_type: Type of item
        name: Item name
        reference_type: Filter by reference type (optional)

    Returns:
        All references to the item
    """
    config = get_config()
    db = Database(config['SQLITE_DB_PATH'])

    try:
        # Search for the item
        items = db.search_items(name, item_type, limit=1)

        if not items:
            return {'error': 'Item not found', 'references': []}

        item = items[0]
        references = item['references']

        # Filter by reference type if provided
        if reference_type:
            references = [r for r in references if r['type'] == reference_type]

        return {
            'item': name,
            'item_type': item_type,
            'total_references': len(references),
            'references': references
        }
    except Exception as e:
        logger.error(f"Error finding references: {e}")
        return {'error': str(e), 'references': []}


def search_by_attribute(
    item_type: str,
    attribute_filters: dict,
    module: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """Search items by their attributes.

    Args:
        item_type: Type of item to search
        attribute_filters: Dict of attribute filters (e.g., {"field_type": "Many2one"})
        module: Filter by module (optional)
        limit: Maximum results (default: 20)
        offset: Number of results to skip for pagination (default: 0)

    Returns:
        Matching items with pagination info
    """
    config = get_config()
    db = Database(config['SQLITE_DB_PATH'])

    try:
        # Get all items of this type
        items = db.search_items('%', item_type, module, limit=999999)

        # Filter by attributes
        matching_items = []
        for item in items:
            attributes = item.get('attributes', {})

            # Check if all filters match
            match = True
            for key, value in attribute_filters.items():
                if attributes.get(key) != value:
                    match = False
                    break

            if match:
                matching_items.append(item)

        # Apply pagination
        total = len(matching_items)
        paginated_items = matching_items[offset:offset + limit]
        has_more = (offset + len(paginated_items)) < total
        next_offset = offset + limit if has_more else None

        return {
            'total': total,
            'limit': limit,
            'offset': offset,
            'returned': len(paginated_items),
            'has_more': has_more,
            'next_offset': next_offset,
            'results': paginated_items
        }
    except Exception as e:
        logger.error(f"Error searching by attribute: {e}")
        return {'error': str(e), 'total': 0, 'limit': limit, 'offset': offset, 'returned': 0, 'results': []}


def search_xml_id(
    query: str,
    module: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """Search for XML IDs by name pattern.

    Args:
        query: Search term (supports SQL LIKE patterns with %, e.g., 'action_view_%')
        module: Filter by module name (optional)
        limit: Maximum results (default: 20)
        offset: Number of results to skip for pagination (default: 0)

    Returns:
        XML IDs with their details
    """
    config = get_config()
    db = Database(config['SQLITE_DB_PATH'])

    try:
        # Search for all item types that represent XML IDs
        items = []

        # Search for generic xml_id items
        xml_items = db.search_items(query, 'xml_id', module, limit=999999)
        items.extend(xml_items)

        # Also search views (they have XML IDs too)
        view_items = db.search_items(query, 'view', module, limit=999999)
        items.extend(view_items)

        # Search actions
        action_items = db.search_items(query, 'action', module, limit=999999)
        items.extend(action_items)

        # Search menus
        menu_items = db.search_items(query, 'menu', module, limit=999999)
        items.extend(menu_items)

        # Search rules
        rule_items = db.search_items(query, 'record_rule', module, limit=999999)
        items.extend(rule_items)

        # Search scheduled actions
        cron_items = db.search_items(query, 'scheduled_action', module, limit=999999)
        items.extend(cron_items)

        # Search report templates
        report_items = db.search_items(query, 'report_template', module, limit=999999)
        items.extend(report_items)

        # Sort by exact match priority, then dependency depth, then name
        items.sort(key=lambda x: (
            0 if x['name'] == query else 1,
            x.get('dependency_depth', 0),
            x['name']
        ))

        # Apply pagination
        total = len(items)
        paginated_items = items[offset:offset + limit]
        has_more = (offset + len(paginated_items)) < total
        next_offset = offset + limit if has_more else None

        return {
            'total': total,
            'limit': limit,
            'offset': offset,
            'returned': len(paginated_items),
            'has_more': has_more,
            'next_offset': next_offset,
            'results': paginated_items
        }
    except Exception as e:
        logger.error(f"Error searching XML IDs: {e}")
        return {'error': str(e), 'total': 0, 'limit': limit, 'offset': offset, 'returned': 0, 'results': []}
