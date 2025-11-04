---
description: Launch an interactive Odoo shell for debugging and exploration
---

# Odoo Shell Command

Start an interactive Odoo shell session using docker compose (Doodba doesn't provide a shell invoke task).

## What to do:
1. Explain to user that you'll launch an Odoo shell with full ORM access
2. Execute:
   ```bash
   docker compose run --rm odoo odoo shell -d devel
   ```

3. Provide helpful commands they can use:
   ```python
   # Access the environment
   env = self.env

   # Search for records
   users = env['res.users'].search([])

   # Create records
   partner = env['res.partner'].create({'name': 'Test'})

   # Access current user
   env.user

   # Commit changes
   env.cr.commit()
   ```

4. Offer to generate specific commands for their use case

## Use Cases:
- Quick data queries
- Testing model methods
- Debugging data issues
- Exploring model relationships
- Running maintenance scripts

## Notes:
- Default database is usually 'devel'
- You can specify a different database with `-d dbname`
- Changes are not committed automatically - use `env.cr.commit()` to save
