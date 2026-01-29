---
description: "**AUTO-USE** when user wants to test: 'run tests', 'test module', 'execute tests', 'check tests', 'verify tests'. Runs Odoo tests using Doodba's invoke test command."
---

# Odoo Test Command

Run tests for Odoo modules using Doodba's `invoke test` task.

## What to do:

1. Ask which module(s) to test (can be comma-separated)

2. Ask test scope:
   - Specific module(s)
   - All odoo-sh modules
   - All core/extra/enterprise modules
   - With or without debug mode

3. Execute tests using invoke tasks:
   ```bash
   # Test specific module(s)
   invoke test --modules=module_name
   invoke test --modules=module1,module2

   # Test with debug output
   invoke test --modules=module_name -v
   ```

4. Parse and present test results clearly

5. If tests fail, offer to help debug (user can use odoo-development plugin for code fixes)

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

## Testing Guidelines:

- Use Odoo's TransactionCase for most tests
- Use SingleTransactionCase for tests that don't need rollback
- Use SavepointCase for complex test scenarios
- Mock external API calls
- Test both positive and negative scenarios
- Ensure tests are isolated and repeatable

## After Testing

If tests fail and code fixes are needed:
- Use the **odoo-development** plugin for Odoo code changes
- Re-run tests with `/odoo-test module_name`

---

**Note**: This command runs tests only. For Odoo code development, use the `odoo-development` plugin.
