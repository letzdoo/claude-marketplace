"""CSV parser for Odoo access rights."""

import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_access_csv(file_path: Path, module_name: str) -> list[dict]:
    """Parse ir.model.access.csv file for access rights.

    Args:
        file_path: Path to CSV file
        module_name: Odoo module name

    Returns:
        List of extracted access rights
    """
    items = []
    relative_path = str(file_path)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for line_num, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
                access_id = row.get('id', '')
                name = row.get('name', access_id)
                model_id = row.get('model_id:id', '')
                group_id = row.get('group_id:id', '')

                # Parse permissions
                perm_read = row.get('perm_read', '0') == '1'
                perm_write = row.get('perm_write', '0') == '1'
                perm_create = row.get('perm_create', '0') == '1'
                perm_unlink = row.get('perm_unlink', '0') == '1'

                # Extract model name from model_id
                model_name = ''
                if model_id.startswith('model_'):
                    model_name = model_id.replace('model_', '').replace('_', '.')

                items.append({
                    'item_type': 'access_right',
                    'name': access_id,
                    'parent_name': None,
                    'module': module_name,
                    'attributes': {
                        'model_name': model_name,
                        'group': group_id,
                        'perm_read': perm_read,
                        'perm_write': perm_write,
                        'perm_create': perm_create,
                        'perm_unlink': perm_unlink,
                        'display_name': name
                    },
                    'references': [{
                        'file_path': relative_path,
                        'line_number': line_num,
                        'reference_type': 'definition',
                        'context': access_id
                    }]
                })

    except Exception as e:
        logger.error(f"Error parsing CSV {file_path}: {e}")

    return items
