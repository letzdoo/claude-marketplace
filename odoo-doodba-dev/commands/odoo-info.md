---
description: Get information about Odoo modules, models, and structure
---

# Odoo Info Command

Retrieve detailed information about Odoo installation, modules, and structure in the Doodba environment.

## Path Information:
Use **relative paths** when reading files from the project root: `odoo/...`

## What to do:
1. Ask what information is needed:
   - Module details (version, dependencies, description)
   - Model fields and methods
   - Installed modules
   - Available modules
   - Database structure
   - Doodba configuration

2. For module info, check (RELATIVE PATHS):
   - `odoo/custom/src/private/[module]/__manifest__.py`
   - `odoo/custom/src/[repo]/[module]/__manifest__.py`

3. For system info (RELATIVE PATHS):
   - Odoo version: Check `odoo/custom/src/odoo/odoo/release.py`
   - Active addons: Read `odoo/custom/src/addons.yaml`
   - Repository config: Read `odoo/custom/src/repos.yaml`

4. Present information clearly and offer related actions

## Useful Locations (RELATIVE PATHS):
- Core Odoo: `odoo/custom/src/odoo/`
- Custom modules: `odoo/custom/src/private/`
- Enterprise: `odoo/custom/src/enterprise/` (if applicable)
- OCA modules: `odoo/custom/src/[repo-name]/`
- Auto-linked: `odoo/auto/addons/`
