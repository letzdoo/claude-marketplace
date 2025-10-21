"""MCP tool implementations for Odoo index."""

import logging
from typing import Optional

import config
from database import Database

logger = logging.getLogger(__name__)

# Global database instance
_db: Optional[Database] = None


def get_db() -> Database:
    """Get or create database instance."""
    global _db
    if _db is None:
        _db = Database(config.SQLITE_DB_PATH)
    return _db


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
        Concise search results with only essential info (file location of definition)
    """
    db = get_db()

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

            # Add key attributes only (description, type info)
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
    db = get_db()

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
    db = get_db()

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
    db = get_db()

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
    db = get_db()

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
    db = get_db()

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
        XML IDs with their details including model, file location, line numbers, and pagination info
    """
    db = get_db()

    try:
        # Search for all item types that represent XML IDs
        # In Odoo, views, actions, menus, rules, and other xml_id items all have XML IDs
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
        # (same logic as db.search_items)
        items.sort(key=lambda x: (
            0 if x['name'] == query else 1,  # Exact match first
            x.get('dependency_depth', 0),     # Then by dependency depth
            x['name']                          # Then by name
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
