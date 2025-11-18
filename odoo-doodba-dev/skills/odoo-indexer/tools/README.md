# Indexer Tool Wrappers

Simplified bash wrappers for common indexer operations.

## Installation

Make scripts executable:
```bash
chmod +x tools/*.sh
```

## Available Tools

### 0. get_context.sh (START HERE)

Get comprehensive project context overview:
```bash
./tools/get_context.sh
./tools/get_context.sh --format markdown
./tools/get_context.sh --section models  # Show only models section
```

**Shows**: Overview stats, custom modules, key models, recent models, security overview, view patterns, inheritance patterns, computed fields

**When to use**: At session start, before feature implementation, during code review

### 1. search_model.sh

Search for models:
```bash
./tools/search_model.sh "sale.order"
./tools/search_model.sh "sale%" 10  # Limit to 10 results
```

### 2. get_model_details.sh

Get complete model details:
```bash
./tools/get_model_details.sh "sale.order"
```

Returns: fields, methods, views, actions, location

### 3. validate_field.sh

Validate a field exists in a model:
```bash
./tools/validate_field.sh "sale.order" "partner_id"
```

Returns: field details if exists, empty if not found

### 4. search_xml_id.sh

Find XML IDs:
```bash
./tools/search_xml_id.sh "action_view_task"
./tools/search_xml_id.sh "action_view_task" "project"  # In specific module
```

### 5. list_modules.sh

List all modules:
```bash
./tools/list_modules.sh
./tools/list_modules.sh "sale*"  # With pattern
```

### 6. module_stats.sh

Get module statistics:
```bash
./tools/module_stats.sh "sale"
```

Returns: model count, field count, dependencies

## Usage in Agents

Agents can use these wrappers for simpler syntax:

**Before** (direct script call):
```bash
cd skills/odoo-indexer
uv run scripts/get_details.py model "sale.order"
```

**After** (using wrapper):
```bash
./skills/odoo-indexer/tools/get_model_details.sh "sale.order"
```

## Benefits

- ✅ Shorter command syntax
- ✅ Auto-handle directory changes
- ✅ Built-in validation
- ✅ Helpful usage messages
- ✅ Parameter defaults

## Notes

- All scripts automatically `cd` to indexer directory
- Error messages guide correct usage
- Optional parameters have sensible defaults
- Requires `uv` to be installed
