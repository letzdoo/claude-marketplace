---
name: odoo-query
description: Connect to Odoo instances via XML-RPC for read-only queries to investigate issues and explore data. Use when user asks to "query odoo", "connect to odoo", "investigate odoo data", "read odoo records", or needs to explore an Odoo instance.
---

# Odoo Query Skill

Connect to Odoo instances via XML-RPC and perform read-only queries to investigate issues.

## When to Use This Skill

Use this skill when the user needs to:
- Query data from a live Odoo instance
- Investigate issues by exploring Odoo records
- Read model definitions and field structures
- Search for specific records using domains

## Available Commands

- `/odoo-query` - Connect to Odoo and run read-only queries

## Configuration

Users must provide connection details:
- **URL**: Odoo instance URL (e.g., https://mycompany.odoo.com)
- **Database**: Database name
- **Login**: Username/email
- **API Key**: API key (Settings > Users > API Keys) or password

## Security Notes

- Only READ operations are allowed (search, read, search_read, fields_get)
- Never execute write, create, unlink, or any modifying operations
- API keys are preferred over passwords for security
- Credentials are only used for the current session

## Example Usage

```python
# Search for partners
records = models.execute_kw(db, uid, password,
    'res.partner', 'search_read',
    [[['is_company', '=', True]]],
    {'fields': ['name', 'email'], 'limit': 10})

# Get model fields
fields = models.execute_kw(db, uid, password,
    'sale.order', 'fields_get',
    [], {'attributes': ['string', 'type', 'required']})
```
