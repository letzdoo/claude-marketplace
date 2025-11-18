#!/usr/bin/env python3
"""Get Odoo project context summary for development tasks.

This provides a focused overview of the Odoo codebase structure,
highlighting key models, modules, and architectural patterns.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional
from collections import defaultdict

import config
from database import Database

logger = logging.getLogger(__name__)


def get_custom_modules(db: Database) -> list[dict]:
    """Get list of custom (non-core) modules.

    Args:
        db: Database instance

    Returns:
        List of module info dicts
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Get all modules with their item counts
        cursor.execute("""
            SELECT
                module,
                dependency_depth,
                COUNT(DISTINCT CASE WHEN item_type = 'model' THEN id END) as model_count,
                COUNT(DISTINCT CASE WHEN item_type = 'field' THEN id END) as field_count,
                COUNT(DISTINCT CASE WHEN item_type = 'view' THEN id END) as view_count,
                COUNT(DISTINCT CASE WHEN item_type = 'action' THEN id END) as action_count,
                COUNT(DISTINCT CASE WHEN item_type = 'menu' THEN id END) as menu_count
            FROM indexed_items
            GROUP BY module
            ORDER BY dependency_depth DESC, module ASC
        """)

        modules = []
        for row in cursor.fetchall():
            # Consider modules with high dependency depth as custom modules
            # (they depend on core modules, so they're likely custom)
            if row['dependency_depth'] > 5 or row['module'].startswith(('custom_', 'letzdoo_', 'l10n_')):
                modules.append({
                    'name': row['module'],
                    'depth': row['dependency_depth'],
                    'models': row['model_count'],
                    'fields': row['field_count'],
                    'views': row['view_count'],
                    'actions': row['action_count'],
                    'menus': row['menu_count']
                })

        return modules


def get_recent_models(db: Database, limit: int = 10) -> list[dict]:
    """Get recently indexed models (likely being worked on).

    Args:
        db: Database instance
        limit: Maximum number of models

    Returns:
        List of model info dicts
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                name,
                module,
                attributes,
                created_at
            FROM indexed_items
            WHERE item_type = 'model'
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        models = []
        for row in cursor.fetchall():
            attrs = json.loads(row['attributes']) if row['attributes'] else {}
            models.append({
                'name': row['name'],
                'module': row['module'],
                'description': attrs.get('description', ''),
                'type': attrs.get('model_type', 'regular'),
                'inherits': attrs.get('inherits', []),
                'updated': row['created_at']
            })

        return models


def get_key_models(db: Database, limit: int = 15) -> list[dict]:
    """Get most important models (by field count and references).

    Args:
        db: Database instance
        limit: Maximum number of models

    Returns:
        List of model info dicts
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                i.name,
                i.module,
                i.attributes,
                COUNT(DISTINCT f.id) as field_count,
                COUNT(DISTINCT v.id) as view_count
            FROM indexed_items i
            LEFT JOIN indexed_items f ON f.item_type = 'field' AND f.parent_name = i.name
            LEFT JOIN indexed_items v ON v.item_type = 'view' AND json_extract(v.attributes, '$.model') = i.name
            WHERE i.item_type = 'model'
            GROUP BY i.name, i.module, i.attributes
            ORDER BY (field_count + view_count * 2) DESC
            LIMIT ?
        """, (limit,))

        models = []
        for row in cursor.fetchall():
            attrs = json.loads(row['attributes']) if row['attributes'] else {}
            models.append({
                'name': row['name'],
                'module': row['module'],
                'description': attrs.get('description', ''),
                'field_count': row['field_count'],
                'view_count': row['view_count'],
                'type': attrs.get('model_type', 'regular')
            })

        return models


def get_security_overview(db: Database) -> dict:
    """Get security configuration overview.

    Args:
        db: Database instance

    Returns:
        Security stats dict
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Count record rules
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM indexed_items
            WHERE item_type = 'record_rule'
        """)
        rule_count = cursor.fetchone()['count']

        # Count access rights
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM indexed_items
            WHERE item_type = 'access_right'
        """)
        access_count = cursor.fetchone()['count']

        # Get models without security
        cursor.execute("""
            SELECT i.name, i.module
            FROM indexed_items i
            WHERE i.item_type = 'model'
            AND NOT EXISTS (
                SELECT 1 FROM indexed_items ar
                WHERE ar.item_type = 'access_right'
                AND json_extract(ar.attributes, '$.model_name') = i.name
            )
            AND json_extract(i.attributes, '$.model_type') = 'regular'
            LIMIT 10
        """)

        models_without_security = [
            {'name': row['name'], 'module': row['module']}
            for row in cursor.fetchall()
        ]

        return {
            'record_rules': rule_count,
            'access_rights': access_count,
            'models_without_access': models_without_security
        }


def get_view_patterns(db: Database) -> dict:
    """Get common view patterns in the codebase.

    Args:
        db: Database instance

    Returns:
        View pattern stats
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                json_extract(attributes, '$.view_type') as view_type,
                COUNT(*) as count
            FROM indexed_items
            WHERE item_type = 'view'
            GROUP BY view_type
            ORDER BY count DESC
        """)

        view_types = {
            row['view_type'] or 'unknown': row['count']
            for row in cursor.fetchall()
        }

        return view_types


def get_inheritance_patterns(db: Database) -> list[dict]:
    """Get models with complex inheritance patterns.

    Args:
        db: Database instance

    Returns:
        List of models with inheritance info
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                name,
                module,
                attributes
            FROM indexed_items
            WHERE item_type = 'model'
            AND json_array_length(json_extract(attributes, '$.inherits')) > 0
            ORDER BY json_array_length(json_extract(attributes, '$.inherits')) DESC
            LIMIT 20
        """)

        models = []
        for row in cursor.fetchall():
            attrs = json.loads(row['attributes']) if row['attributes'] else {}
            inherits = attrs.get('inherits', [])
            if inherits:
                models.append({
                    'name': row['name'],
                    'module': row['module'],
                    'inherits': inherits,
                    'inherit_count': len(inherits)
                })

        return models


def get_computed_fields(db: Database, limit: int = 20) -> list[dict]:
    """Get fields with compute methods.

    Args:
        db: Database instance
        limit: Maximum number of fields

    Returns:
        List of computed fields
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                name,
                parent_name,
                module,
                attributes
            FROM indexed_items
            WHERE item_type = 'field'
            AND json_extract(attributes, '$.compute') IS NOT NULL
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        fields = []
        for row in cursor.fetchall():
            attrs = json.loads(row['attributes']) if row['attributes'] else {}
            fields.append({
                'field': row['name'],
                'model': row['parent_name'],
                'module': row['module'],
                'compute_method': attrs.get('compute', ''),
                'stored': attrs.get('store', False)
            })

        return fields


def format_context_text(context: dict) -> str:
    """Format context as readable text.

    Args:
        context: Context dictionary

    Returns:
        Formatted text
    """
    lines = []
    lines.append("=" * 80)
    lines.append("ODOO PROJECT CONTEXT SUMMARY")
    lines.append("=" * 80)
    lines.append("")

    # Overview
    if 'overview' in context:
        lines.append("OVERVIEW")
        lines.append("-" * 80)
        lines.append(f"Total Modules: {context['overview']['total_modules']}")
        lines.append(f"Total Models: {context['overview']['total_models']}")
        lines.append(f"Total Fields: {context['overview']['total_fields']}")
        lines.append(f"Total Views: {context['overview']['total_views']}")
        lines.append("")

    # Custom modules
    if 'custom_modules' in context and context['custom_modules']:
        lines.append("CUSTOM MODULES")
        lines.append("-" * 80)
        for mod in context['custom_modules'][:10]:
            lines.append(f"• {mod['name']}")
            lines.append(f"  Models: {mod['models']}, Fields: {mod['fields']}, " +
                        f"Views: {mod['views']}, Depth: {mod['depth']}")
        lines.append("")

    # Key models
    if 'key_models' in context and context['key_models']:
        lines.append("KEY MODELS (Most Referenced)")
        lines.append("-" * 80)
        for model in context['key_models'][:10]:
            desc = f" - {model['description']}" if model.get('description') else ""
            lines.append(f"• {model['name']}{desc}")
            lines.append(f"  Module: {model['module']}, Fields: {model['field_count']}, " +
                        f"Views: {model['view_count']}")
        lines.append("")

    # Recent models
    if 'recent_models' in context and context['recent_models']:
        lines.append("RECENTLY INDEXED MODELS (Likely being worked on)")
        lines.append("-" * 80)
        for model in context['recent_models'][:5]:
            desc = f" - {model['description']}" if model.get('description') else ""
            lines.append(f"• {model['name']}{desc}")
            lines.append(f"  Module: {model['module']}, Type: {model['type']}")
            if model.get('inherits'):
                lines.append(f"  Inherits: {', '.join(model['inherits'])}")
        lines.append("")

    # Security overview
    if 'security' in context:
        sec = context['security']
        lines.append("SECURITY OVERVIEW")
        lines.append("-" * 80)
        lines.append(f"Record Rules: {sec['record_rules']}")
        lines.append(f"Access Rights: {sec['access_rights']}")
        if sec['models_without_access']:
            lines.append(f"\nModels without access rights ({len(sec['models_without_access'])}):")
            for model in sec['models_without_access'][:5]:
                lines.append(f"  • {model['name']} ({model['module']})")
        lines.append("")

    # View patterns
    if 'view_patterns' in context:
        lines.append("VIEW PATTERNS")
        lines.append("-" * 80)
        for view_type, count in sorted(context['view_patterns'].items(),
                                       key=lambda x: x[1], reverse=True):
            lines.append(f"• {view_type}: {count}")
        lines.append("")

    # Inheritance patterns
    if 'inheritance_patterns' in context and context['inheritance_patterns']:
        lines.append("COMPLEX INHERITANCE PATTERNS")
        lines.append("-" * 80)
        for model in context['inheritance_patterns'][:5]:
            lines.append(f"• {model['name']} ({model['module']})")
            lines.append(f"  Inherits from: {', '.join(model['inherits'])}")
        lines.append("")

    # Computed fields
    if 'computed_fields' in context and context['computed_fields']:
        lines.append("COMPUTED FIELDS (Sample)")
        lines.append("-" * 80)
        for field in context['computed_fields'][:10]:
            stored = " [stored]" if field.get('stored') else ""
            lines.append(f"• {field['model']}.{field['field']}{stored}")
            lines.append(f"  Compute: {field['compute_method']} ({field['module']})")
        lines.append("")

    lines.append("=" * 80)
    lines.append("Use specific indexer commands for detailed information on any item")
    lines.append("=" * 80)

    return '\n'.join(lines)


def format_context_markdown(context: dict) -> str:
    """Format context as markdown.

    Args:
        context: Context dictionary

    Returns:
        Formatted markdown
    """
    lines = []
    lines.append("# Odoo Project Context Summary")
    lines.append("")

    # Overview
    if 'overview' in context:
        lines.append("## Overview")
        lines.append("")
        lines.append(f"- **Total Modules**: {context['overview']['total_modules']}")
        lines.append(f"- **Total Models**: {context['overview']['total_models']}")
        lines.append(f"- **Total Fields**: {context['overview']['total_fields']}")
        lines.append(f"- **Total Views**: {context['overview']['total_views']}")
        lines.append("")

    # Custom modules
    if 'custom_modules' in context and context['custom_modules']:
        lines.append("## Custom Modules")
        lines.append("")
        for mod in context['custom_modules'][:10]:
            lines.append(f"### {mod['name']}")
            lines.append(f"- Models: {mod['models']}, Fields: {mod['fields']}, " +
                        f"Views: {mod['views']}")
            lines.append(f"- Dependency Depth: {mod['depth']}")
            lines.append("")

    # Key models
    if 'key_models' in context and context['key_models']:
        lines.append("## Key Models (Most Referenced)")
        lines.append("")
        for model in context['key_models'][:10]:
            desc = f" - {model['description']}" if model.get('description') else ""
            lines.append(f"### `{model['name']}`{desc}")
            lines.append(f"- Module: `{model['module']}`")
            lines.append(f"- Fields: {model['field_count']}, Views: {model['view_count']}")
            lines.append("")

    # Recent models
    if 'recent_models' in context and context['recent_models']:
        lines.append("## Recently Indexed Models")
        lines.append("")
        lines.append("*Likely being worked on recently*")
        lines.append("")
        for model in context['recent_models'][:5]:
            desc = f" - {model['description']}" if model.get('description') else ""
            lines.append(f"### `{model['name']}`{desc}")
            lines.append(f"- Module: `{model['module']}`")
            lines.append(f"- Type: {model['type']}")
            if model.get('inherits'):
                lines.append(f"- Inherits: {', '.join(f'`{i}`' for i in model['inherits'])}")
            lines.append("")

    # Security overview
    if 'security' in context:
        sec = context['security']
        lines.append("## Security Overview")
        lines.append("")
        lines.append(f"- **Record Rules**: {sec['record_rules']}")
        lines.append(f"- **Access Rights**: {sec['access_rights']}")
        if sec['models_without_access']:
            lines.append("")
            lines.append(f"### Models Without Access Rights ({len(sec['models_without_access'])})")
            lines.append("")
            for model in sec['models_without_access'][:5]:
                lines.append(f"- `{model['name']}` ({model['module']})")
            lines.append("")

    # View patterns
    if 'view_patterns' in context:
        lines.append("## View Patterns")
        lines.append("")
        for view_type, count in sorted(context['view_patterns'].items(),
                                       key=lambda x: x[1], reverse=True):
            lines.append(f"- **{view_type}**: {count}")
        lines.append("")

    # Inheritance patterns
    if 'inheritance_patterns' in context and context['inheritance_patterns']:
        lines.append("## Complex Inheritance Patterns")
        lines.append("")
        for model in context['inheritance_patterns'][:5]:
            lines.append(f"### `{model['name']}` ({model['module']})")
            lines.append(f"Inherits from: {', '.join(f'`{i}`' for i in model['inherits'])}")
            lines.append("")

    # Computed fields
    if 'computed_fields' in context and context['computed_fields']:
        lines.append("## Computed Fields (Sample)")
        lines.append("")
        for field in context['computed_fields'][:10]:
            stored = " *[stored]*" if field.get('stored') else ""
            lines.append(f"- `{field['model']}.{field['field']}`{stored}")
            lines.append(f"  - Compute: `{field['compute_method']}` ({field['module']})")
        lines.append("")

    lines.append("---")
    lines.append("*Use specific indexer commands for detailed information on any item*")

    return '\n'.join(lines)


def main():
    """Main entry point for get_context script."""
    parser = argparse.ArgumentParser(
        description='Get Odoo project context summary'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'markdown', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--section',
        choices=['overview', 'modules', 'models', 'security', 'views', 'inheritance', 'computed'],
        help='Show only specific section',
        default=None
    )

    args = parser.parse_args()

    try:
        db = Database(config.SQLITE_DB_PATH)

        # Gather context information
        context = {}

        # Get overview stats
        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(DISTINCT module) FROM indexed_items")
            total_modules = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM indexed_items WHERE item_type = 'model'")
            total_models = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM indexed_items WHERE item_type = 'field'")
            total_fields = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM indexed_items WHERE item_type = 'view'")
            total_views = cursor.fetchone()[0]

        context['overview'] = {
            'total_modules': total_modules,
            'total_models': total_models,
            'total_fields': total_fields,
            'total_views': total_views
        }

        # Get section-specific data
        if not args.section or args.section in ('modules',):
            context['custom_modules'] = get_custom_modules(db)

        if not args.section or args.section in ('models',):
            context['key_models'] = get_key_models(db)
            context['recent_models'] = get_recent_models(db)

        if not args.section or args.section in ('security',):
            context['security'] = get_security_overview(db)

        if not args.section or args.section in ('views',):
            context['view_patterns'] = get_view_patterns(db)

        if not args.section or args.section in ('inheritance',):
            context['inheritance_patterns'] = get_inheritance_patterns(db)

        if not args.section or args.section in ('computed',):
            context['computed_fields'] = get_computed_fields(db)

        # Output based on format
        if args.format == 'json':
            print(json.dumps(context, indent=2))
        elif args.format == 'markdown':
            print(format_context_markdown(context))
        else:
            print(format_context_text(context))

    except Exception as e:
        if args.format == 'json':
            result = {
                'success': False,
                'error': str(e)
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Error retrieving context: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
