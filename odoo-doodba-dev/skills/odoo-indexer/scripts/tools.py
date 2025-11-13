"""MCP tool implementations for Odoo index.

This module provides the public API for MCP (Model Context Protocol) tools.
All implementations are delegated to query_shared.py for consistency.
"""

import logging
from typing import Optional

# Import all tool implementations from query_shared
from query_shared import (
    search_odoo_index,
    get_item_details,
    list_modules,
    get_module_stats,
    find_references,
    search_by_attribute,
    search_xml_id,
)

logger = logging.getLogger(__name__)

# Re-export all functions for backward compatibility
__all__ = [
    'search_odoo_index',
    'get_item_details',
    'list_modules',
    'get_module_stats',
    'find_references',
    'search_by_attribute',
    'search_xml_id',
]
