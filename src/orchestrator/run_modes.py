"""Explicit daily-loop mode configuration and environment validation."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


class RunModeConfigurationError(RuntimeError):
    """Raised when a run mode is missing required configuration."""


@dataclass(frozen=True)
class BaseRunConfig:
    mode: str
    foundry_provider: str
    foundry_model: str | None
    max_task_count: int
    max_parallel_agents: int
    write_permissions: bool
    artifact_root: Path
    github_mutation_policy: str
    github_write_issues: bool
    github_create_prs: bool
    simulation_budget: dict[str, int | float | str]
    timeout_seconds: int
    use_sample_fixtures: bool
    use_live_foundry: bool
    required_env: tuple[str, ...] = field(default_factory=tuple)
    allow_dummy_env: bool = False
    write_knowledge_base: bool = False
    fail_on_required_agent_failure: bool = True

    @property
    def is_production(self) -> bool:
        return self.mode == "production"

    @property
    def is_test(self) -> bool:
        return self.mode == "test"


@dataclass(frozen=True)
class TestRunConfig(BaseRunConfig):
    mode: str = "test"
    foundry_provider: str = "stub"
    foundry_model: str | None = "fixture-model"
    max_task_count: int = 4
    max_parallel_agents: int = 2
    write_permissions: bool = False
    artifact_root: Path = Path("artifacts/test")
    github_mutation_policy: str = "disabled"
    github_write_issues: bool = False
    github_create_prs: bool = False
    simulation_budget: dict[str, int | float | str] = field(
        default_factory=lambda: {
            "fixture": "simulations/results/result_example_laughlin.json",
            "max_particles": 3,
            "max_seconds": 30,
        }
    )
    timeout_seconds: int = 120
    use_sample_fixtures: bool = True
    use_live_foundry: bool = False
    allow_dummy_env: bool = True
    write_knowledge_base: bool = False
    fail_on_required_agent_failure: bool = False


@dataclass(frozen=True)
class ProductionRunConfig(BaseRunConfig):
    mode: str = "production"
    foundry_provider: str = "foundry_agent"
    foundry_model: str | None = None
    max_task_count: int = 6
    max_parallel_agents: int = 3
    write_permissions: bool = True
    artifact_root: Path = Path("artifacts/production")
    github_mutation_policy: str = "explicit-gate"
    github_write_issues: bool = False
    github_create_prs: bool = False
    simulation_budget: dict[str, int | float | str] = field(
        default_factory=lambda: {
            "max_particles": 12,
            "max_seconds": 1800,
        }
    )
    timeout_seconds: int = 1800
    use_sample_fixtures: bool = False
    use_live_foundry: bool = True
    required_env: tuple[str, ...] = (
        "AZURE_AI_PROJECT_ENDPOINT",
        "FOUNDRY_AGENT_ID",
        "RESEARCH_REPOSITORY",
    )
    allow_dummy_env: bool = False
    write_knowledge_base: bool = True
    fail_on_required_agent_failure: bool = True


def get_run_config(
    mode: str,
    workspace_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> BaseRunConfig:
    """Return a mode config with workspace-relative artifact paths."""
    selected = mode.strip().lower()
    current_env = env or os.environ

    if selected == "test":
        config: BaseRunConfig = TestRunConfig()
    elif selected == "production":
        config = ProductionRunConfig(
            github_write_issues=current_env.get("DAILY_LOOP_GITHUB_WRITE") == "true",
            github_create_prs=current_env.get("DAILY_LOOP_CREATE_PR") == "true",
        )
    else:
        raise RunModeConfigurationError(
            "Unsupported run mode. Use 'test' or 'production'."
        )

    if workspace_path is None:
        return config

    workspace = Path(workspace_path)
    return _with_workspace_paths(config, workspace)


def validate_environment(
    config: BaseRunConfig,
    env: Mapping[str, str] | None = None,
) -> None:
    """Validate required env vars by name only; never prints or returns values."""
    current_env = env or os.environ
    missing = [
        name
        for name in config.required_env
        if not current_env.get(name) or not current_env.get(name, "").strip()
    ]

    if missing and not config.allow_dummy_env:
        joined = ", ".join(missing)
        raise RunModeConfigurationError(
            f"Missing required environment variable(s) for {config.mode} mode: {joined}"
        )


def _with_workspace_paths(config: BaseRunConfig, workspace: Path) -> BaseRunConfig:
    artifact_root = config.artifact_root
    if not artifact_root.is_absolute():
        artifact_root = workspace / artifact_root

    if isinstance(config, TestRunConfig):
        return TestRunConfig(artifact_root=artifact_root)

    if isinstance(config, ProductionRunConfig):
        return ProductionRunConfig(
            artifact_root=artifact_root,
            github_write_issues=config.github_write_issues,
            github_create_prs=config.github_create_prs,
        )

    raise TypeError(f"Unsupported config type: {type(config)!r}")
