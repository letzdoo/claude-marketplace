---
description: "**AUTO-USE** on first plugin use or when user reports setup issues. Validates environment, installs dependencies, and builds the code indexer. Use when: 'setup', 'install', 'configure', 'indexer not found', 'not working'."
---

# Doodba Setup Command

Launch the setup agent to perform complete environment validation and indexer setup.

## Your Role

1. Launch the `odoo-setup` agent:
   ```
   subagent_type: odoo-doodba-dev:odoo-setup
   prompt: "Perform complete Doodba environment setup and return final status report"
   ```

2. The agent will autonomously:
   - Check prerequisites (Docker, Python, uv)
   - Detect or prompt for Odoo path
   - Build the code indexer database (2-5 minutes)
   - Validate indexer works
   - Return a concise status report

3. Display the agent's final report to the user

## Troubleshooting

If setup fails, guide the user:

### Docker not found
```
Install Docker: https://docs.docker.com/get-docker/
Then re-run: /odoo-setup
```

### Python version too old
```
Install Python 3.10+:
  curl https://pyenv.run | bash
  pyenv install 3.10
  pyenv global 3.10

Then re-run: /odoo-setup
```

### Odoo path not detected
```
Set manually:
  export ODOO_PATH="/path/to/odoo/custom/src"

Then re-run: /odoo-setup
```

### Indexer build fails
```
Manual rebuild:
  cd skills/odoo-indexer
  uv sync
  uv run scripts/update_index.py --clear --full
```

## Re-running Setup

Setup can be re-run anytime to:
- Verify environment
- Rebuild indexer after code changes
- Fix configuration issues
