"""Configuration management for Claude Memory skill."""

import os
from pathlib import Path

# Memory database location
MEMORY_DB_PATH = Path(
    os.getenv(
        'CLAUDE_MEMORY_DB_PATH',
        str(Path.home() / '.claude-memory' / 'project_memory.sqlite3')
    )
)

# Ensure the directory exists
MEMORY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Default project path (can be overridden)
DEFAULT_PROJECT_PATH = os.getenv('CLAUDE_PROJECT_PATH', os.getcwd())

# Maximum number of search results to return
MAX_SEARCH_RESULTS = int(os.getenv('CLAUDE_MEMORY_MAX_RESULTS', '50'))

# Session ID for tracking context (can be set by environment)
SESSION_ID = os.getenv('CLAUDE_SESSION_ID', None)
