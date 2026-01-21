#!/usr/bin/env python3
"""
Odoo XML-RPC Query Tool

Read-only queries to Odoo instances via XML-RPC.
SECURITY: Only read operations are allowed.
"""

import argparse
import ast
import json
import sys
import xmlrpc.client
from urllib.parse import urlparse


class OdooXMLRPC:
    """Odoo XML-RPC client for read-only operations."""

    # Whitelist of allowed methods (READ-ONLY)
    ALLOWED_METHODS = frozenset([
        'search',
        'search_read',
        'read',
        'fields_get',
        'search_count',
        'name_get',
        'name_search',
        'default_get',
        'check_access_rights',
        'check_access_rule',
    ])

    def __init__(self, url: str, db: str, login: str, api_key: str):
        """Initialize connection parameters."""
        self.url = url.rstrip('/')
        self.db = db
        self.login = login
        self.api_key = api_key
        self.uid = None
        self.common = None
        self.models = None

    def connect(self) -> dict:
        """Establish connection and authenticate."""
        try:
            # Common endpoint for authentication
            self.common = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/common',
                allow_none=True
            )

            # Authenticate
            self.uid = self.common.authenticate(
                self.db, self.login, self.api_key, {}
            )

            if not self.uid:
                return {
                    'success': False,
                    'error': 'Authentication failed. Check credentials.'
                }

            # Models endpoint for queries
            self.models = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/object',
                allow_none=True
            )

            # Get version info
            version = self.common.version()

            return {
                'success': True,
                'uid': self.uid,
                'server_version': version.get('server_version', 'unknown'),
                'server_serie': version.get('server_serie', 'unknown'),
            }

        except xmlrpc.client.Fault as e:
            return {'success': False, 'error': f'XML-RPC Fault: {e.faultString}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def execute(self, model: str, method: str, *args, **kwargs) -> dict:
        """Execute a method on a model (read-only only)."""
        # Security check: only allow whitelisted methods
        if method not in self.ALLOWED_METHODS:
            return {
                'success': False,
                'error': f'Method "{method}" not allowed. Only read operations permitted.'
            }

        if not self.uid or not self.models:
            conn = self.connect()
            if not conn['success']:
                return conn

        try:
            result = self.models.execute_kw(
                self.db, self.uid, self.api_key,
                model, method,
                list(args),
                kwargs
            )
            return {'success': True, 'data': result}

        except xmlrpc.client.Fault as e:
            return {'success': False, 'error': f'XML-RPC Fault: {e.faultString}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_read(self, model: str, domain: list = None, fields: list = None,
                    limit: int = None, offset: int = 0, order: str = None) -> dict:
        """Search and read records."""
        domain = domain or []
        kwargs = {'offset': offset}

        if fields:
            kwargs['fields'] = fields
        if limit:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order

        result = self.execute(model, 'search_read', domain, **kwargs)

        if result['success']:
            return {
                'success': True,
                'action': 'search_read',
                'model': model,
                'count': len(result['data']),
                'data': result['data']
            }
        return result

    def search_count(self, model: str, domain: list = None) -> dict:
        """Count records matching domain."""
        domain = domain or []
        result = self.execute(model, 'search_count', domain)

        if result['success']:
            return {
                'success': True,
                'action': 'search_count',
                'model': model,
                'count': result['data']
            }
        return result

    def read(self, model: str, ids: list, fields: list = None) -> dict:
        """Read specific records by ID."""
        kwargs = {}
        if fields:
            kwargs['fields'] = fields

        result = self.execute(model, 'read', ids, **kwargs)

        if result['success']:
            return {
                'success': True,
                'action': 'read',
                'model': model,
                'count': len(result['data']),
                'data': result['data']
            }
        return result

    def fields_get(self, model: str, attributes: list = None) -> dict:
        """Get field definitions for a model."""
        attributes = attributes or ['string', 'type', 'required', 'readonly',
                                     'relation', 'selection', 'help']

        result = self.execute(model, 'fields_get', [], {'attributes': attributes})

        if result['success']:
            # Format fields for readability
            fields_data = {}
            for name, info in result['data'].items():
                fields_data[name] = {
                    'type': info.get('type'),
                    'string': info.get('string'),
                    'required': info.get('required', False),
                    'readonly': info.get('readonly', False),
                }
                if info.get('relation'):
                    fields_data[name]['relation'] = info['relation']
                if info.get('selection'):
                    fields_data[name]['selection'] = info['selection']

            return {
                'success': True,
                'action': 'fields_get',
                'model': model,
                'field_count': len(fields_data),
                'fields': fields_data
            }
        return result

    def list_models(self) -> dict:
        """List all accessible models."""
        result = self.search_read(
            'ir.model',
            domain=[('transient', '=', False)],
            fields=['model', 'name', 'state'],
            limit=500,
            order='model'
        )

        if result['success']:
            models = [
                {'model': r['model'], 'name': r['name'], 'state': r.get('state', 'base')}
                for r in result['data']
            ]
            return {
                'success': True,
                'action': 'list_models',
                'count': len(models),
                'models': models
            }
        return result


def parse_domain(domain_str: str) -> list:
    """Parse domain string to Python list."""
    if not domain_str or domain_str == '[]':
        return []

    try:
        return ast.literal_eval(domain_str)
    except (ValueError, SyntaxError) as e:
        raise ValueError(f'Invalid domain syntax: {e}')


def parse_fields(fields_str: str) -> list:
    """Parse comma-separated fields to list."""
    if not fields_str:
        return None

    return [f.strip() for f in fields_str.split(',') if f.strip()]


def parse_ids(ids_str: str) -> list:
    """Parse comma-separated IDs to list of integers."""
    if not ids_str:
        return []

    return [int(i.strip()) for i in ids_str.split(',') if i.strip()]


def main():
    parser = argparse.ArgumentParser(
        description='Odoo XML-RPC Query Tool (Read-Only)'
    )
    parser.add_argument('--url', required=True, help='Odoo instance URL')
    parser.add_argument('--db', required=True, help='Database name')
    parser.add_argument('--login', required=True, help='Username/email')
    parser.add_argument('--api-key', required=True, help='API key or password')
    parser.add_argument('--action', required=True,
                        choices=['test', 'list_models', 'fields_get',
                                 'search_read', 'search_count', 'read'],
                        help='Action to perform')
    parser.add_argument('--model', help='Model name (e.g., sale.order)')
    parser.add_argument('--domain', default='[]', help='Search domain')
    parser.add_argument('--fields', help='Comma-separated field names')
    parser.add_argument('--ids', help='Comma-separated record IDs')
    parser.add_argument('--limit', type=int, help='Maximum records to return')
    parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    parser.add_argument('--order', help='Sort order (e.g., "name asc")')

    args = parser.parse_args()

    # Initialize client
    client = OdooXMLRPC(args.url, args.db, args.login, args.api_key)

    try:
        if args.action == 'test':
            result = client.connect()
            if result['success']:
                result['message'] = 'Connection successful!'

        elif args.action == 'list_models':
            conn = client.connect()
            if not conn['success']:
                result = conn
            else:
                result = client.list_models()

        elif args.action == 'fields_get':
            if not args.model:
                result = {'success': False, 'error': '--model is required for fields_get'}
            else:
                result = client.fields_get(args.model)

        elif args.action == 'search_read':
            if not args.model:
                result = {'success': False, 'error': '--model is required for search_read'}
            else:
                domain = parse_domain(args.domain)
                fields = parse_fields(args.fields)
                result = client.search_read(
                    args.model,
                    domain=domain,
                    fields=fields,
                    limit=args.limit,
                    offset=args.offset,
                    order=args.order
                )

        elif args.action == 'search_count':
            if not args.model:
                result = {'success': False, 'error': '--model is required for search_count'}
            else:
                domain = parse_domain(args.domain)
                result = client.search_count(args.model, domain=domain)

        elif args.action == 'read':
            if not args.model:
                result = {'success': False, 'error': '--model is required for read'}
            elif not args.ids:
                result = {'success': False, 'error': '--ids is required for read'}
            else:
                ids = parse_ids(args.ids)
                fields = parse_fields(args.fields)
                result = client.read(args.model, ids, fields=fields)

        else:
            result = {'success': False, 'error': f'Unknown action: {args.action}'}

    except ValueError as e:
        result = {'success': False, 'error': str(e)}
    except Exception as e:
        result = {'success': False, 'error': f'Unexpected error: {str(e)}'}

    # Output JSON
    print(json.dumps(result, indent=2, default=str))

    # Exit with appropriate code
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
