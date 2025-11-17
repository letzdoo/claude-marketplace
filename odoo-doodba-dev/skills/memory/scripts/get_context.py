#!/usr/bin/env python3
"""Get a coherent context summary of the project state."""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

from config import DEFAULT_PROJECT_PATH, SESSION_ID
from database import MemoryDatabase


def format_context_summary(items_by_category, format='text'):
    """Format the context summary for output.

    Args:
        items_by_category: Dictionary of category -> list of items
        format: Output format ('text' or 'markdown')

    Returns:
        Formatted string
    """
    if not items_by_category:
        return "No context available for this project."

    lines = []

    if format == 'markdown':
        lines.append("# Project Context Summary")
        lines.append("")
    else:
        lines.append("PROJECT CONTEXT SUMMARY")
        lines.append("=" * 70)
        lines.append("")

    # Define category order and titles for consistency (improves cache hits)
    category_config = [
        ('decision', 'Key Decisions', 'Important architectural and design decisions'),
        ('requirement', 'Requirements', 'User requirements and specifications'),
        ('context', 'Current Context', 'Current project state and ongoing work'),
        ('finding', 'Important Findings', 'Discoveries and insights'),
        ('error', 'Known Issues & Solutions', 'Error patterns and their solutions'),
        ('config', 'Configuration', 'Configuration decisions and settings'),
        ('todo', 'Pending Items', 'Future work and tasks'),
        ('reference', 'References', 'External references and documentation'),
    ]

    # Process categories in consistent order
    for category, title, description in category_config:
        if category not in items_by_category:
            continue

        items = items_by_category[category]
        if not items:
            continue

        if format == 'markdown':
            lines.append(f"## {title}")
            lines.append(f"*{description}*")
            lines.append("")
        else:
            lines.append(f"{title.upper()}")
            lines.append("-" * 70)
            lines.append(description)
            lines.append("")

        for item in items:
            key = item['key']
            value = item['value']
            context = item.get('context', '')
            tags = item.get('tags', [])

            if format == 'markdown':
                lines.append(f"### {key}")
                lines.append(f"**Value:** {value}")
                if context:
                    lines.append(f"**Context:** {context}")
                if tags:
                    lines.append(f"**Tags:** {', '.join(tags)}")
                lines.append("")
            else:
                lines.append(f"• {key}")
                lines.append(f"  {value}")
                if context:
                    lines.append(f"  Context: {context}")
                if tags:
                    lines.append(f"  Tags: {', '.join(tags)}")
                lines.append("")

        lines.append("")

    # Handle uncategorized items
    if None in items_by_category or 'uncategorized' in items_by_category:
        uncategorized = items_by_category.get(None, []) + items_by_category.get('uncategorized', [])
        if uncategorized:
            if format == 'markdown':
                lines.append("## Other Items")
                lines.append("")
            else:
                lines.append("OTHER ITEMS")
                lines.append("-" * 70)
                lines.append("")

            for item in uncategorized:
                key = item['key']
                value = item['value']

                if format == 'markdown':
                    lines.append(f"### {key}")
                    lines.append(f"{value}")
                    lines.append("")
                else:
                    lines.append(f"• {key}: {value}")
                    lines.append("")

    return '\n'.join(lines)


def main():
    """Main entry point for the get_context script."""
    parser = argparse.ArgumentParser(
        description='Get a coherent context summary of the project state'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'markdown', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--category',
        help='Filter by specific category',
        default=None
    )
    parser.add_argument(
        '--days',
        type=int,
        help='Only show items updated in the last N days',
        default=None
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum items per category (default: 10)'
    )
    parser.add_argument(
        '--project',
        help='Project path (defaults to current directory)',
        default=DEFAULT_PROJECT_PATH
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Show all items (no limit per category)'
    )

    args = parser.parse_args()

    # Normalize project path
    project_path = str(Path(args.project).resolve())

    try:
        db = MemoryDatabase()

        # Record session if available
        if SESSION_ID:
            db.record_session(SESSION_ID, project_path)

        # Get all memory items
        if args.category:
            all_items = db.list_all_memory(
                project_path=project_path,
                category=args.category,
                limit=9999 if args.all else args.limit
            )
        else:
            all_items = db.list_all_memory(
                project_path=project_path,
                limit=9999  # Get all, we'll limit per category
            )

        # Filter by date if specified
        if args.days:
            cutoff_date = datetime.now() - timedelta(days=args.days)
            cutoff_str = cutoff_date.isoformat()
            all_items = [
                item for item in all_items
                if item['updated_at'] >= cutoff_str
            ]

        # Group by category
        items_by_category = defaultdict(list)
        for item in all_items:
            category = item.get('category') or 'uncategorized'
            items_by_category[category].append(item)

        # Limit items per category (unless --all specified)
        if not args.all and not args.category:
            for category in items_by_category:
                items_by_category[category] = items_by_category[category][:args.limit]

        # Output based on format
        if args.format == 'json':
            output = {
                'project_path': project_path,
                'generated_at': datetime.now().isoformat(),
                'filters': {
                    'category': args.category,
                    'days': args.days,
                    'limit_per_category': None if args.all else args.limit
                },
                'categories': {
                    category: items
                    for category, items in items_by_category.items()
                }
            }
            print(json.dumps(output, indent=2))
        else:
            # Text or markdown format
            summary = format_context_summary(items_by_category, args.format)
            print(summary)

            # Add footer with stats
            if args.format == 'text':
                total_items = sum(len(items) for items in items_by_category.values())
                print("")
                print("=" * 70)
                print(f"Total items shown: {total_items}")
                if args.days:
                    print(f"Filtered to last {args.days} days")
                if not args.all:
                    print(f"Showing up to {args.limit} items per category")
                print(f"Project: {project_path}")

    except Exception as e:
        if args.format == 'json':
            result = {
                'success': False,
                'error': str(e)
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Error retrieving context: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
