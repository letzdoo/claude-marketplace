"""Configuration management for ReasoningBank."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class RetrieveConfig:
    """Configuration for retrieval."""
    k: int = 3
    alpha: float = 0.65
    beta: float = 0.15
    gamma: float = 0.20
    delta: float = 0.10
    recency_half_life_days: int = 45
    duplicate_threshold: float = 0.87
    embedding_model: str = "voyage-3"


@dataclass
class JudgeConfig:
    """Configuration for judge."""
    model: str = "claude-sonnet-4-5-20250929"
    temperature: float = 0.0
    max_tokens: int = 1024


@dataclass
class DistillConfig:
    """Configuration for distillation."""
    max_items_per_traj: int = 3
    redact_pii: bool = True
    model: str = "claude-sonnet-4-5-20250929"
    temperature: float = 0.3
    max_tokens: int = 2048


@dataclass
class ConsolidateConfig:
    """Configuration for consolidation."""
    run_every_new_items: int = 20
    contradiction_threshold: float = 0.60
    prune_age_days: int = 180
    min_confidence_keep: float = 0.30
    dedup_threshold: float = 0.87


@dataclass
class MattsConfig:
    """Configuration for MaTTS."""
    enabled: bool = True
    parallel_k: int = 6
    sequential_r: int = 3


@dataclass
class DatabaseConfig:
    """Configuration for database."""
    path: str = "~/.reasoningbank/memory.db"


@dataclass
class LearningConfig:
    """Configuration for learning rates."""
    initial_confidence_success: float = 0.75
    initial_confidence_failure: float = 0.65
    learning_rate: float = 0.05
    success_delta: float = 1.0
    failure_delta: float = -0.5


@dataclass
class Config:
    """Main configuration for ReasoningBank."""
    retrieve: RetrieveConfig = field(default_factory=RetrieveConfig)
    judge: JudgeConfig = field(default_factory=JudgeConfig)
    distill: DistillConfig = field(default_factory=DistillConfig)
    consolidate: ConsolidateConfig = field(default_factory=ConsolidateConfig)
    matts: MattsConfig = field(default_factory=MattsConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    learning: LearningConfig = field(default_factory=LearningConfig)


def load_config(config_path: str = None) -> Config:
    """Load configuration from YAML file."""
    if config_path is None:
        # Try to find config.yaml in the skill directory
        skill_dir = Path(__file__).parent.parent
        config_path = skill_dir / "config.yaml"

    if not Path(config_path).exists():
        # Return default config if file doesn't exist
        return Config()

    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)

    rb_config = data.get('reasoningbank', {})

    return Config(
        retrieve=RetrieveConfig(**rb_config.get('retrieve', {})),
        judge=JudgeConfig(**rb_config.get('judge', {})),
        distill=DistillConfig(**rb_config.get('distill', {})),
        consolidate=ConsolidateConfig(**rb_config.get('consolidate', {})),
        matts=MattsConfig(**rb_config.get('matts', {})),
        database=DatabaseConfig(**rb_config.get('database', {})),
        learning=LearningConfig(**rb_config.get('learning', {})),
    )


def get_anthropic_api_key() -> str:
    """Get Anthropic API key from environment."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Please set it to use ReasoningBank."
        )
    return api_key
