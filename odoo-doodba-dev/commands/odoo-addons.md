---
description: Manage addons.yaml configuration and install/uninstall modules. AUTO-USE when user says "install module", "activate addon", "add to addons.yaml", "enable module", "uninstall", or needs to configure module installation. Uses Doodba's invoke install/uninstall tasks. Essential after creating new modules or when managing module dependencies.
---

# Odoo Addons Management

Manage module installation and addons.yaml configuration using Doodba's invoke tasks.

## What to do:
1. Ask what the user wants to do:
   - Install module(s)
   - Uninstall module(s)
   - View/edit addons.yaml
   - Update module translations

2. Use invoke tasks for module management:
   ```bash
   # Install modules
   invoke install --modules=module_name
   invoke install --private    # Install all private modules
   invoke install --core       # Install all core modules
   invoke install --extra      # Install all extra modules

   # Uninstall modules
   invoke uninstall --modules=module_name

   # Update translations
   invoke updatepot --module=module_name
   invoke updatepot --all
   ```

3. For manual addons.yaml editing:
   - File location: `odoo/custom/src/addons.yaml`
   - Determine the correct repository section (private, web, server-tools, etc.)
   - Add the module name in the proper format
   - After changes: `invoke img-build` to rebuild

4. Show the user what changed and next steps

## Important Notes:
- Modules in `odoo/custom/src/private/` are automatically linked
- External modules need to be in `repos.yaml` first
- Use wildcards carefully: `- module_*` matches all starting with "module_"
- After manual addons.yaml changes, rebuild: `invoke img-build`
- After installing, restart Odoo: `invoke restart`

## Invoke Task Options:

**install**:
- `--modules`: Comma-separated list of modules
- `--core`: Install all core addons
- `--extra`: Install all extra addons
- `--private`: Install all private addons
- `--enterprise`: Install all enterprise addons

**uninstall**:
- `--modules`: Comma-separated list of modules to uninstall

**updatepot**:
- `--module`: Specific module to update translations
- `--all`: Update all modules
- `--repo`: Update all modules from a specific repository
