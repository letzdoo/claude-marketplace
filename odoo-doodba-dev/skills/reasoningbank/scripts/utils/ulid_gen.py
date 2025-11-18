"""ULID generation utility for ReasoningBank."""

from ulid import ULID


def generate_ulid() -> str:
    """Generate a new ULID string."""
    return str(ULID())


def generate_memory_id() -> str:
    """Generate a memory ID with prefix."""
    return f"rm_{generate_ulid()}"


def generate_task_id() -> str:
    """Generate a task ID with prefix."""
    return f"task_{generate_ulid()}"


def generate_run_id() -> str:
    """Generate a MaTTS run ID with prefix."""
    return f"matts_{generate_ulid()}"
