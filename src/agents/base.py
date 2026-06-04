"""Base agent contract for bounded Magentic subtasks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.orchestrator.ledger import AgentReport, PlanStep, WorkflowState


@dataclass
class BaseAgent:
    name: str
    capabilities: List[str] = field(default_factory=list)

    def run(self, task: PlanStep, state: WorkflowState) -> AgentReport:
        raise NotImplementedError
