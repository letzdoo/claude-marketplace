# Odoo Doodba Development Plugin

Professional Odoo development toolkit for Claude Code with deep knowledge of Doodba container structure and Odoo best practices.

## Features

- **Module Scaffolding**: Generate properly structured Odoo modules
- **Testing Framework**: Run and manage Odoo tests effectively
- **Addon Management**: Manage addons.yaml configuration
- **Interactive Shell**: Quick access to Odoo shell for debugging
- **Logging**: View and analyze Odoo logs
- **System Info**: Get detailed information about modules and structure
- **Expert Agent**: Specialized Odoo developer with deep knowledge
- **Code Indexing**: Fast code navigation with odoo-indexer MCP server

## Installation

### From a marketplace

```shell
/plugin marketplace add letzdoo/claude-plugins
/plugin install odoo-doodba-dev@letzdoo
```

### Local development

```shell
/plugin marketplace add ./path/to/marketplace
/plugin install odoo-doodba-dev@local
```

## Usage

### Available Commands

- `/odoo-scaffold` - Create a new Odoo module
- `/odoo-test` - Run tests for modules
- `/odoo-addons` - Manage addons.yaml
- `/odoo-shell` - Launch Odoo shell
- `/odoo-logs` - View Odoo logs
- `/odoo-info` - Get system/module information

### Odoo Developer Agent

Switch to the specialized Odoo developer agent for complex development tasks:

```shell
/agents switch odoo-developer
```

This agent has deep knowledge of:
- Doodba directory structure
- Odoo development patterns
- Testing best practices
- Performance optimization
- Security considerations

## Requirements

- Doodba-based Odoo deployment
- Docker and Docker Compose
- Python 3.8.1+ with pyinvoke installed
- Claude Code installed
- Python 3.10+ with uv (for MCP server)

## Key Features

**Leverages Doodba's Invoke Tasks:**
This plugin uses Doodba's built-in `invoke` tasks for all operations, ensuring compatibility and best practices. The commands guide you to use the proper invoke tasks instead of raw docker commands.

**Odoo Code Indexing:**
This plugin includes the [odoo-indexer-mcp](https://github.com/letzdoo/odoo-indexer-mcp) server that provides fast code navigation through:
- Search for models, fields, methods, views, and other Odoo elements
- Get detailed information about any indexed item
- Find references across the codebase
- List and analyze modules
- Fast AST and XML parsing with incremental updates
- Pure SQLite database for quick searches (<50ms)

## Examples

### Create a new module

```shell
/odoo-scaffold
```

Then develop iteratively using the odoo-developer agent:

```shell
/agents switch odoo-developer
```

"Create a custom field on sale.order to track customer project code, add it to the form view, and write tests for it"

### Use Code Indexing (MCP Tools)

The odoo-indexer MCP server provides tools accessible to Claude:

```python
# Search for a model
mcp__odoo_indexer__search_odoo_index(query="sale.order", item_type="model")

# Get detailed information about a model
mcp__odoo_indexer__get_item_details(item_type="model", name="sale.order")

# Find all references to a field
mcp__odoo_indexer__find_references(item_type="field", name="partner_id")

# List all modules
mcp__odoo_indexer__list_modules()

# Search by specific attributes
mcp__odoo_indexer__search_by_attribute(item_type="model", attribute="inherit", value="mail.thread")
```

### Test your changes

```shell
/odoo-test
# This will guide you to use: invoke test --modules=my_module
```

### View logs during development

```shell
/odoo-logs
# This will guide you to use: invoke logs --tail=100
```

## Best Practices

1. **Always work in `odoo/custom/src/private/`** for custom modules (relative path from project root)
2. **Write tests first** or alongside your code (TDD)
3. **Use inheritance** instead of modifying core files
4. **Check security** - always define access rights and record rules
5. **Test in isolation** - each module should be independently testable
6. **Follow naming conventions** - snake_case for technical, proper names for display

## Plugin Structure

```
odoo-doodba-dev/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── odoo-scaffold.md
│   ├── odoo-test.md
│   ├── odoo-addons.md
│   ├── odoo-shell.md
│   ├── odoo-logs.md
│   └── odoo-info.md
├── agents/
│   └── odoo-developer.md
├── CLAUDE.md
└── README.md
```

## Doodba Directory Structure

Understanding the Doodba structure is key to effective development.

### Path Mapping
**IMPORTANT:** Use relative paths from the project root. Doodba mounts `odoo/` to `/opt/odoo/` in containers.

**Relative Paths** (where you edit files from project root):
- **Core Odoo**: `odoo/custom/src/odoo/`
- **Enterprise Modules**: `odoo/custom/src/enterprise/` (if applicable)
- **Custom/Private Modules**: `odoo/custom/src/private/`
- **Third-party Repos**: `odoo/custom/src/[repo-name]/`
- **Configuration Files**:
  - Module activation: `odoo/custom/src/addons.yaml`
  - Repository setup: `odoo/custom/src/repos.yaml`

**Container Paths** (used in docker commands):
- Everything under `/opt/odoo/...`
- Example: Host `odoo/custom/src/private/my_module/` becomes `/opt/odoo/custom/src/private/my_module/` in the container

## Development Workflow

1. **Scaffold** a new module using `/odoo-scaffold`
2. **Switch** to the odoo-developer agent for implementation
3. **Develop** models, views, and business logic
4. **Test** using `/odoo-test` continuously
5. **Debug** issues with `/odoo-shell` and `/odoo-logs`
6. **Manage** module activation with `/odoo-addons`

## Module Development Best Practices

### Model Development
- Inherit from proper base classes (models.Model, models.TransientModel, models.AbstractModel)
- Use proper field types and attributes
- Implement computed fields with @api.depends
- Override CRUD methods correctly (create, write, unlink)
- Use proper SQL constraints and Python constraints
- Follow naming conventions: _name, _description, _inherit, _inherits

### View Development
- Follow proper XML structure
- Use inheritance correctly (xpath, position)
- Implement proper security (groups attribute)
- Use proper widget types
- Follow UI/UX guidelines

### Testing Strategy
- Use TransactionCase for most tests
- Use SingleTransactionCase for tests that don't need rollback
- Use SavepointCase for complex test scenarios
- Mock external API calls
- Test both positive and negative scenarios
- Ensure tests are isolated and repeatable

### Security Considerations
- Always define access rights (ir.model.access.csv)
- Implement record rules when needed (security.xml)
- Use groups to control feature access
- Never skip security setup
- Test with different user roles

### Performance Optimization
- Use search_count() instead of len(search())
- Batch operations when possible
- Use read() instead of browsing for simple data access
- Add database indexes for frequently searched fields
- Use _sql_constraints for database-level validation

## Common Development Patterns

### Creating a New Model
```python
from odoo import models, fields, api

class CustomModel(models.Model):
    _name = 'custom.model'
    _description = 'Custom Model Description'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], default='draft')

    @api.depends('field1', 'field2')
    def _compute_something(self):
        for record in self:
            record.computed_field = record.field1 + record.field2
```

### Extending Existing Models
```python
class SaleOrderExtension(models.Model):
    _inherit = 'sale.order'

    custom_field = fields.Char()

    def action_confirm(self):
        # Custom logic before
        res = super().action_confirm()
        # Custom logic after
        return res
```

### Writing Tests
```python
from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestModuleName(TransactionCase):

    def setUp(self):
        super().setUp()
        # Setup test data

    def test_something(self):
        """Test description"""
        # Arrange
        # Act
        # Assert
```

## Debugging Tips

- Use `import pdb; pdb.set_trace()` for interactive debugging
- Use logging: `_logger.info()`, `_logger.warning()`, `_logger.error()`
- Check logs with `/odoo-logs`
- Use `/odoo-shell` for quick tests and data exploration
- Enable developer mode in UI for debugging views

## Support

For issues or questions about this plugin, contact letzdoo development team or open an issue in the plugin repository.

## License

This plugin is provided as-is for professional Odoo development within Doodba environments.

## About

Created by letzdoo for professional Odoo development with Doodba.
