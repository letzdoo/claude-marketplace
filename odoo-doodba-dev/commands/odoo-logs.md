---
name: odoo-logs
description: View and analyze Odoo logs effectively
---

# Odoo Logs Command

View and filter Odoo logs using Doodba's invoke tasks.

## What to do:
1. Ask what they want to see:
   - Recent errors
   - Specific container logs
   - Follow logs in real-time
   - All recent activity

2. Use invoke logs task:
   ```bash
   # View recent logs (default: last 10 lines, following)
   invoke logs

   # View more lines
   invoke logs --tail=100

   # View without following
   invoke logs --follow=False

   # View specific container(s)
   invoke logs --container=odoo
   invoke logs --container=odoo,db
   ```

3. For more advanced filtering, can combine with grep:
   ```bash
   # Filter by level
   invoke logs --follow=False | grep ERROR
   invoke logs --follow=False | grep WARNING

   # Search for specific module
   invoke logs --follow=False | grep "module_name"
   ```

4. Help interpret log messages and suggest solutions

## Log Reading Tips:
- ERROR: Critical issues needing immediate attention
- WARNING: Potential problems, may need investigation
- INFO: Normal operations, useful for debugging flow
- DEBUG: Detailed information, enable in dev only

## Invoke Task Options:
- `--tail`: Number of lines to show (default: 10)
- `--follow`: Follow log output in real-time (default: True)
- `--container`: Specific container(s) to show logs from (comma-separated)
