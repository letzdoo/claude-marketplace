# Odoo Query Plugin

Connect to Odoo instances via XML-RPC and perform read-only queries to investigate issues.

## Setup

Before using this plugin, ensure you have Python 3 with xmlrpc.client available (included in standard library).

## Configuration

Users must provide connection details:
- **URL**: Odoo instance URL (e.g., https://mycompany.odoo.com)
- **Database**: Database name
- **Login**: Username/email
- **API Key**: API key (Settings > Users > API Keys) or password

## Available Commands

- `/odoo-query` - Connect to Odoo and run read-only queries

## Security Notes

- Only READ operations are allowed (search, read, search_read, fields_get)
- Never execute write, create, unlink, or any modifying operations
- API keys are preferred over passwords for security
- Credentials are only used for the current session
