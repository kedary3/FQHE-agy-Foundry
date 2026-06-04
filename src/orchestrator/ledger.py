"""Serializable Magentic workflow ledgers.

The PI / Magentic Manager owns these ledgers. Specialist agents only receive
bounded ``PlanStep`` objects and return ``AgentReport`` records.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


EPISTEMIC_STATUS_LABELS = {
    "exact_result",
    "controlled_approximation",
    "numerical_evidence",
    "variational_assumption",
    "phenomenological_argument",
    "conjecture",
    "unresolved",
}

STEP_STATUSES = {"pending", "in_progress", "completed", "failed", "deferred"}


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_run_id(mode: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-{mode}-{uuid4().hex[:8]}"


@dataclass
class PlanStep:
    task_id: str
    goal: str
    suggested_agent: str
    assigned_agent: Optional[str] = None
    status: str = "pending"
    dependencies: List[str] = field(default_factory=list)
    evidence_needed: List[str] = field(default_factory=list)
    attempts: int = 0
    notes: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.status not in STEP_STATUSES:
            raise ValueError(f"Invalid step status: {self.status}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanStep":
        return cls(**data)


@dataclass
class AgentReport:
    task_id: str
    agent_name: str
    assigned_goal: str
    summary: str
    claims: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    computations_performed: List[str] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    tests_run: List[str] = field(default_factory=list)
    uncertainties: List[str] = field(default_factory=list)
    recommended_next_tasks: List[str] = field(default_factory=list)
    epistemic_status: List[str] = field(default_factory=list)
    status: str = "success"

    def __post_init__(self) -> None:
        invalid = set(self.epistemic_status) - EPISTEMIC_STATUS_LABELS
        if invalid:
            raise ValueError(f"Invalid epistemic_status labels: {sorted(invalid)}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentReport":
        return cls(**data)


@dataclass
class TaskLedger:
    objective: str
    run_id: str
    mode: str = "test"
    plan_steps: List[PlanStep] = field(default_factory=list)
    created_at: str = field(default_factory=utc_timestamp)

    @classmethod
    def from_objective(cls, objective: str, mode: str = "test") -> "TaskLedger":
        return cls(objective=objective, mode=mode, run_id=new_run_id(mode))

    def add_plan_step(self, step: PlanStep) -> None:
        self.plan_steps.append(step)

    def get_step(self, task_id: str) -> PlanStep:
        for step in self.plan_steps:
            if step.task_id == task_id:
                return step
        raise KeyError(f"Unknown task_id: {task_id}")

    def assign_step_to_agent(self, task_id: str, agent_name: str) -> None:
        step = self.get_step(task_id)
        step.assigned_agent = agent_name
        step.status = "in_progress"
        step.attempts += 1

    def mark_step_status(self, task_id: str, status: str) -> None:
        if status not in STEP_STATUSES:
            raise ValueError(f"Invalid step status: {status}")
        self.get_step(task_id).status = status

    def dependency_ids_completed(self, step: PlanStep) -> bool:
        completed = {item.task_id for item in self.plan_steps if item.status == "completed"}
        return set(step.dependencies).issubset(completed)

    def next_ready_steps(self, limit: int) -> List[PlanStep]:
        ready = [
            step
            for step in self.plan_steps
            if step.status == "pending" and self.dependency_ids_completed(step)
        ]
        return ready[:limit]

    def completed_count(self) -> int:
        return sum(1 for step in self.plan_steps if step.status == "completed")

    def is_complete(self) -> bool:
        return bool(self.plan_steps) and all(
            step.status in {"completed", "deferred"} for step in self.plan_steps
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": self.objective,
            "run_id": self.run_id,
            "mode": self.mode,
            "created_at": self.created_at,
            "plan_steps": [step.to_dict() for step in self.plan_steps],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskLedger":
        steps = [PlanStep.from_dict(item) for item in data.get("plan_steps", [])]
        return cls(
            objective=data["objective"],
            run_id=data["run_id"],
            mode=data.get("mode", "test"),
            plan_steps=steps,
            created_at=data.get("created_at", utc_timestamp()),
        )


@dataclass
class ProgressLedger:
    facts: List[str] = field(default_factory=list)
    reports: List[AgentReport] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    stall_count: int = 0
    replan_count: int = 0
    replan_requested: bool = False
    _last_progress_marker: int = 0

    def add_fact(self, fact: str) -> None:
        self.facts.append(fact)
        self.events.append({"time": utc_timestamp(), "event": "fact_added", "detail": fact})

    def ingest_report(self, report: AgentReport) -> None:
        self.reports.append(report)
        self.events.append(
            {
                "time": utc_timestamp(),
                "event": "report_ingested",
                "agent": report.agent_name,
                "task_id": report.task_id,
                "status": report.status,
            }
        )

    def detect_stall(self, task_ledger: TaskLedger, max_stall_count: int = 3) -> bool:
        marker = task_ledger.completed_count() + len(self.reports)
        if marker <= self._last_progress_marker:
            self.stall_count += 1
        else:
            self.stall_count = 0
            self._last_progress_marker = marker
        self.replan_requested = self.stall_count >= max_stall_count
        return self.replan_requested

    def request_replan(self, reason: str) -> None:
        self.replan_count += 1
        self.replan_requested = True
        self.events.append({"time": utc_timestamp(), "event": "replan_requested", "reason": reason})

    def clear_replan_request(self) -> None:
        self.replan_requested = False
        self.stall_count = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "facts": list(self.facts),
            "reports": [report.to_dict() for report in self.reports],
            "events": list(self.events),
            "stall_count": self.stall_count,
            "replan_count": self.replan_count,
            "replan_requested": self.replan_requested,
            "last_progress_marker": self._last_progress_marker,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProgressLedger":
        ledger = cls(
            facts=list(data.get("facts", [])),
            reports=[AgentReport.from_dict(item) for item in data.get("reports", [])],
            events=list(data.get("events", [])),
            stall_count=data.get("stall_count", 0),
            replan_count=data.get("replan_count", 0),
            replan_requested=data.get("replan_requested", False),
        )
        ledger._last_progress_marker = data.get("last_progress_marker", 0)
        return ledger


@dataclass
class WorkflowState:
    objective: str
    mode: str
    task_ledger: TaskLedger
    progress_ledger: ProgressLedger = field(default_factory=ProgressLedger)
    final_report: str = ""
    status: str = "initialized"

    @classmethod
    def from_objective(cls, objective: str, mode: str = "test") -> "WorkflowState":
        return cls(
            objective=objective,
            mode=mode,
            task_ledger=TaskLedger.from_objective(objective=objective, mode=mode),
        )

    def add_fact(self, fact: str) -> None:
        self.progress_ledger.add_fact(fact)

    def add_plan_steps(self, steps: List[PlanStep]) -> None:
        for step in steps:
            self.task_ledger.add_plan_step(step)

    def ingest_agent_report(self, report: AgentReport) -> None:
        self.progress_ledger.ingest_report(report)
        if report.status == "success":
            self.task_ledger.mark_step_status(report.task_id, "completed")
        else:
            self.task_ledger.mark_step_status(report.task_id, "failed")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": self.objective,
            "mode": self.mode,
            "status": self.status,
            "task_ledger": self.task_ledger.to_dict(),
            "progress_ledger": self.progress_ledger.to_dict(),
            "final_report": self.final_report,
        }

    def to_json(self, path: Optional[Path] = None) -> str:
        payload = json.dumps(self.to_dict(), indent=2, sort_keys=True)
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(payload, encoding="utf-8")
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        return cls(
            objective=data["objective"],
            mode=data.get("mode", "test"),
            status=data.get("status", "initialized"),
            task_ledger=TaskLedger.from_dict(data["task_ledger"]),
            progress_ledger=ProgressLedger.from_dict(data.get("progress_ledger", {})),
            final_report=data.get("final_report", ""),
        )

    @classmethod
    def from_json(cls, payload: str) -> "WorkflowState":
        return cls.from_dict(json.loads(payload))
