"""Director / PI logic for evidence-gated daily research loops."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .run_modes import BaseRunConfig


EVIDENCE_TYPES = {
    "exact result",
    "controlled approximation",
    "numerical evidence",
    "variational assumption",
    "phenomenological argument",
    "conjecture",
}

CLAIM_DISPOSITIONS = {"accepted", "rejected", "deferred"}


class MalformedAgentOutput(ValueError):
    """Raised when an agent output does not satisfy the scientific schema."""


@dataclass(frozen=True)
class AgentTask:
    task_id: str
    agent_name: str
    agent_role: str
    objective: str
    required: bool = True
    allowed_inputs: tuple[str, ...] = ()
    expected_outputs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "objective": self.objective,
            "required": self.required,
            "allowed_inputs": list(self.allowed_inputs),
            "expected_outputs": list(self.expected_outputs),
        }


class Director:
    """Director/PI agent that plans, validates, and synthesizes loop outputs."""

    def __init__(
        self,
        agent_configs: dict[str, dict[str, Any]] | None = None,
        run_config: BaseRunConfig | None = None,
    ) -> None:
        self.agent_configs = agent_configs or {}
        self.run_config = run_config

    def generate_daily_plan(
        self,
        objective: str,
        memory_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Break the objective into a bounded, parallel-safe task graph."""
        mode = self.run_config.mode if self.run_config else "test"
        max_tasks = self.run_config.max_task_count if self.run_config else 4

        task_specs = [
            (
                "literature_agent",
                "Literature Agent",
                "Identify relevant prior claims and classify their evidence.",
            ),
            (
                "theory_agent",
                "Theory Agent",
                "Identify analytic assumptions and exact or controlled statements.",
            ),
            (
                "numerics_agent",
                "Numerics Agent",
                "Validate the small Laughlin fixture and report numerical metadata.",
            ),
            (
                "falsification_agent",
                "Falsification Agent",
                "Challenge unsupported claims and propose falsifying tests.",
            ),
            (
                "experiment_bridge_agent",
                "Experiment Bridge Agent",
                "Map claims to experimental observables and unresolved ambiguities.",
            ),
            (
                "knowledge_curator_agent",
                "Knowledge Curator Agent",
                "Prepare non-destructive artifact and ledger updates.",
            ),
        ][:max_tasks]

        tasks = [
            AgentTask(
                task_id=f"{mode}-{idx:02d}-{agent_key}",
                agent_name=agent_key,
                agent_role=role,
                objective=f"{objective} {task_objective}",
                allowed_inputs=("config", "knowledge_base", "simulation_fixture"),
                expected_outputs=("claims", "artifacts", "next_actions"),
            ).to_dict()
            for idx, (agent_key, role, task_objective) in enumerate(task_specs, start=1)
        ]

        return {
            "mode": mode,
            "objective": objective,
            "memory_context": memory_context or {},
            "parallel_groups": [
                {
                    "group_id": "independent-subagents",
                    "task_ids": [task["task_id"] for task in tasks],
                }
            ],
            "tasks": tasks,
        }

    def validate_task_graph(self, task_graph: dict[str, Any]) -> None:
        if not task_graph.get("tasks"):
            raise ValueError("Director produced an empty task graph.")

        seen = set()
        for task in task_graph["tasks"]:
            for field in ("task_id", "agent_name", "agent_role", "objective"):
                if not task.get(field):
                    raise ValueError(f"Task is missing required field: {field}")
            if task["task_id"] in seen:
                raise ValueError(f"Duplicate task id: {task['task_id']}")
            seen.add(task["task_id"])

    def validate_agent_output(self, output: dict[str, Any]) -> None:
        required = {
            "agent_name",
            "agent_role",
            "task_id",
            "run_id",
            "mode",
            "status",
            "summary",
            "claims",
            "artifacts",
            "errors",
            "next_actions",
        }
        missing = sorted(required - set(output))
        if missing:
            raise MalformedAgentOutput(
                f"Agent output missing required field(s): {', '.join(missing)}"
            )

        if output["status"] not in {"success", "partial", "failed"}:
            raise MalformedAgentOutput(f"Invalid agent status: {output['status']}")

        if not isinstance(output["claims"], list):
            raise MalformedAgentOutput("Agent output claims must be a list.")

        for claim in output["claims"]:
            self._validate_claim(claim)

    def mark_malformed_output(
        self,
        task: dict[str, Any],
        run_id: str,
        mode: str,
        error: str,
    ) -> dict[str, Any]:
        return {
            "agent_name": task.get("agent_name", "unknown"),
            "agent_role": task.get("agent_role", "unknown"),
            "task_id": task.get("task_id", "unknown"),
            "run_id": run_id,
            "mode": mode,
            "status": "failed",
            "summary": "Output rejected by Director schema validation.",
            "claims": [],
            "artifacts": [],
            "errors": [error],
            "next_actions": ["Return output matching the required agent schema."],
        }

    def classify_claims(
        self,
        outputs: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        accepted: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        deferred: list[dict[str, Any]] = []

        for output in outputs:
            if output.get("status") == "failed":
                rejected.append(
                    {
                        "claim_id": f"{output.get('task_id')}-failed-output",
                        "text": output.get("summary", "Agent output failed."),
                        "reason": "; ".join(output.get("errors", [])) or "Agent failed.",
                    }
                )
                continue

            for claim in output.get("claims", []):
                disposition = self._claim_disposition(claim, output)
                if disposition == "accepted":
                    accepted.append(claim)
                elif disposition == "rejected":
                    rejected.append(claim)
                else:
                    deferred.append(claim)

        return {
            "accepted": accepted,
            "rejected": rejected,
            "deferred": deferred,
        }

    def synthesize(
        self,
        run_id: str,
        mode: str,
        objective: str,
        task_graph: dict[str, Any],
        outputs: list[dict[str, Any]],
        validation_summary: dict[str, Any],
    ) -> dict[str, Any]:
        classifications = self.classify_claims(outputs)
        unresolved_assumptions = []
        proposed_next_tests = []

        for output in outputs:
            proposed_next_tests.extend(output.get("next_actions", []))
            for claim in output.get("claims", []):
                limitations = claim.get("limitations")
                if limitations:
                    unresolved_assumptions.append(limitations)

        return {
            "run_id": run_id,
            "mode": mode,
            "objective": objective,
            "task_count": len(task_graph.get("tasks", [])),
            "agent_statuses": {
                output.get("task_id"): output.get("status") for output in outputs
            },
            "claim_classification": classifications,
            "validation_summary": validation_summary,
            "scientific_status": {
                "accepted_claims": classifications["accepted"],
                "rejected_claims": classifications["rejected"],
                "deferred_claims": classifications["deferred"],
                "unresolved_assumptions": sorted(set(unresolved_assumptions)),
                "proposed_next_tests": sorted(set(proposed_next_tests)),
            },
        }

    def _validate_claim(self, claim: dict[str, Any]) -> None:
        for field in (
            "claim_id",
            "text",
            "evidence_type",
            "support",
            "limitations",
            "confidence",
        ):
            if field not in claim or claim[field] in (None, ""):
                raise MalformedAgentOutput(
                    f"Claim missing required field: {field}"
                )

        if claim["evidence_type"] not in EVIDENCE_TYPES:
            allowed = ", ".join(sorted(EVIDENCE_TYPES))
            raise MalformedAgentOutput(
                f"Invalid evidence_type '{claim['evidence_type']}'. Allowed: {allowed}"
            )

        if claim["confidence"] not in {"low", "medium", "high"}:
            raise MalformedAgentOutput(
                f"Invalid confidence '{claim['confidence']}'."
            )

    @staticmethod
    def _claim_disposition(
        claim: dict[str, Any],
        output: dict[str, Any],
    ) -> str:
        text = json.dumps(claim, sort_keys=True).lower()
        if output.get("status") == "partial":
            return "deferred"
        if "unsupported" in text or "overclaim" in text:
            return "rejected"
        if claim.get("evidence_type") == "conjecture":
            return "deferred"
        return "accepted"
