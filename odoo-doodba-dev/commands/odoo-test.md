---
description: Run Odoo tests for specific modules with proper configuration
---

# Odoo Test Command

Run tests for Odoo modules using Doodba's invoke tasks.

## What to do:
1. Ask which module(s) to test (can be comma-separated)
2. Ask test scope:
   - Current module (default if in module directory)
   - Specific module(s)
   - All odoo-sh/core/extra/enterprise modules
   - With or without debug mode

3. Execute tests using invoke tasks:
   ```bash
   # Test current module (when in module directory)
   invoke test

   # Test specific module(s)
   invoke test --modules=module_name
   invoke test --modules=module1,module2
   ```

4. Parse and present test results clearly
5. If tests fail, offer to help debug and fix issues

## Testing Guidelines:
- Use Odoo's TransactionCase for most tests
- Use SingleTransactionCase for tests that don't need rollback
- Use SavepointCase for complex test scenarios
- Mock external API calls
- Test both positive and negative scenarios
- Ensure tests are isolated and repeatable

## Invoke Task Options:
- `--modules`: Comma-separated list of modules to test
- `--core`: Test all core addons
- `--extra`: Test all extra addons
- `--private`: Test all private addons
- `--enterprise`: Test all enterprise addons
- `--skip`: Comma-separated list of modules to skip
- `--debugpy`: Run tests with debugger for VSCode
- `--cur-file`: Specify file to detect module from
- `--mode`: 'init' (default) or 'update'
