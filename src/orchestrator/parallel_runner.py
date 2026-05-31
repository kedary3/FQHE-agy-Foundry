"""Parallel subagent execution with explicit task ledger capture."""

from __future__ import annotations

import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable


AgentExecutor = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass
class TaskExecutionRecord:
    run_id: str
    task_id: str
    agent_name: str
    agent_role: str
    start_timestamp: str
    end_timestamp: str | None = None
    duration_seconds: float | None = None
    status: str = "running"
    token_metadata: dict[str, Any] = field(default_factory=dict)
    cost_metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    output_artifact_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "token_metadata": self.token_metadata,
            "cost_metadata": self.cost_metadata,
            "errors": self.errors,
            "output_artifact_path": self.output_artifact_path,
        }


class ParallelAgentRunner:
    """Run independent subagent tasks concurrently and preserve all outcomes."""

    def __init__(
        self,
        run_id: str,
        output_dir: str | Path,
        max_parallel_agents: int,
    ) -> None:
        self.run_id = run_id
        self.output_dir = Path(output_dir)
        self.max_parallel_agents = max(1, max_parallel_agents)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        tasks: list[dict[str, Any]],
        executor: AgentExecutor,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        outputs: list[dict[str, Any]] = []
        ledger: list[dict[str, Any]] = []

        with ThreadPoolExecutor(max_workers=self.max_parallel_agents) as pool:
            future_to_task = {
                pool.submit(self._execute_one, task, executor): task
                for task in tasks
            }

            for future in as_completed(future_to_task):
                output, record = future.result()
                outputs.append(output)
                ledger.append(record.to_dict())

        outputs.sort(key=lambda item: item.get("task_id", ""))
        ledger.sort(key=lambda item: item.get("task_id", ""))
        return outputs, ledger

    def _execute_one(
        self,
        task: dict[str, Any],
        executor: AgentExecutor,
    ) -> tuple[dict[str, Any], TaskExecutionRecord]:
        started = perf_counter()
        record = TaskExecutionRecord(
            run_id=self.run_id,
            task_id=task["task_id"],
            agent_name=task["agent_name"],
            agent_role=task["agent_role"],
            start_timestamp=_utc_now(),
        )

        try:
            output = executor(task)
            record.status = output.get("status", "success")
            record.token_metadata = output.get("token_metadata", {})
            record.cost_metadata = output.get("cost_metadata", {})
        except Exception as exc:
            output = {
                "agent_name": task["agent_name"],
                "agent_role": task["agent_role"],
                "task_id": task["task_id"],
                "run_id": self.run_id,
                "mode": task.get("mode", "unknown"),
                "status": "failed",
                "summary": "Subagent execution raised an exception.",
                "claims": [],
                "artifacts": [],
                "errors": [f"{type(exc).__name__}: {exc}"],
                "next_actions": ["Inspect exception and rerun the failed task."],
            }
            record.status = "failed"
            record.errors.append(traceback.format_exc(limit=5))

        artifact_path = self.output_dir / f"{task['task_id']}.json"
        artifact_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
        record.output_artifact_path = str(artifact_path)
        record.end_timestamp = _utc_now()
        record.duration_seconds = round(perf_counter() - started, 6)
        if output.get("errors"):
            record.errors.extend(str(error) for error in output["errors"])

        return output, record


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
