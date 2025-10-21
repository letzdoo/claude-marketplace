"""Manifest parser for Odoo module metadata."""

import ast
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def parse_manifest(file_path: Path, module_name: str) -> Optional[dict]:
    """Parse __manifest__.py or __openerp__.py file.

    Args:
        file_path: Path to manifest file
        module_name: Odoo module name

    Returns:
        Module metadata item or None if parsing fails
    """
    relative_path = str(file_path)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Parse the manifest file (it's just a dict assignment)
        tree = ast.parse(source)

        # Find the dict in the file
        manifest_dict = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                manifest_dict = _parse_dict(node)
                break

        if not manifest_dict:
            return None

        # Extract key fields
        name = manifest_dict.get('name', module_name)
        version = manifest_dict.get('version', '1.0.0')
        category = manifest_dict.get('category', 'Uncategorized')
        author = manifest_dict.get('author', '')
        description = manifest_dict.get('description', '')
        depends = manifest_dict.get('depends', [])
        installable = manifest_dict.get('installable', True)
        application = manifest_dict.get('application', False)
        auto_install = manifest_dict.get('auto_install', False)
        license_type = manifest_dict.get('license', 'LGPL-3')

        return {
            'item_type': 'module',
            'name': module_name,
            'parent_name': None,
            'module': module_name,
            'attributes': {
                'display_name': name,
                'version': version,
                'category': category,
                'author': author,
                'description': description[:500] if description else '',  # Truncate long descriptions
                'depends': depends,
                'installable': installable,
                'application': application,
                'auto_install': auto_install,
                'license': license_type
            },
            'references': [{
                'file_path': relative_path,
                'line_number': 1,
                'reference_type': 'definition',
                'context': module_name
            }]
        }

    except Exception as e:
        logger.error(f"Error parsing manifest {file_path}: {e}")
        return None


def _parse_dict(node: ast.Dict) -> dict:
    """Parse an AST Dict node to a Python dict."""
    result = {}

    for key_node, value_node in zip(node.keys, node.values):
        # Get key
        if isinstance(key_node, ast.Constant):
            key = key_node.value
        elif isinstance(key_node, ast.Str):
            key = key_node.s
        else:
            continue

        # Get value
        value = _parse_value(value_node)
        result[key] = value

    return result


def _parse_value(node: ast.AST):
    """Parse an AST value node to a Python value."""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.List):
        return [_parse_value(elt) for elt in node.elts]
    elif isinstance(node, ast.Tuple):
        return [_parse_value(elt) for elt in node.elts]
    elif isinstance(node, ast.Dict):
        return _parse_dict(node)
    elif isinstance(node, ast.Name):
        if node.id in ('True', 'False', 'None'):
            return {'True': True, 'False': False, 'None': None}[node.id]
        return node.id
    return None
