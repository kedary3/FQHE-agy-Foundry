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
    daily_loop_command: str = ""
    skill_instructions: tuple[str, ...] = ()
    source_refs: tuple[dict[str, Any], ...] = ()
    bounded_deliverables: tuple[str, ...] = ()
    memory_triggers: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "objective": self.objective,
            "required": self.required,
            "allowed_inputs": list(self.allowed_inputs),
            "expected_outputs": list(self.expected_outputs),
            "daily_loop_command": self.daily_loop_command,
            "skill_instructions": list(self.skill_instructions),
            "source_refs": list(self.source_refs),
            "bounded_deliverables": list(self.bounded_deliverables),
            "memory_triggers": list(self.memory_triggers),
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
        """Break the objective into bounded tasks using durable memory signals."""
        mode = self.run_config.mode if self.run_config else "test"
        max_tasks = self.run_config.max_task_count if self.run_config else 4
        memory = memory_context or {}

        task_specs = self._memory_aware_task_specs(objective, memory)[:max_tasks]

        tasks = [
            AgentTask(
                task_id=f"{mode}-{idx:02d}-{agent_key}",
                agent_name=agent_key,
                agent_role=spec["role"],
                objective=spec["objective"],
                allowed_inputs=tuple(spec["allowed_inputs"]),
                expected_outputs=tuple(spec["expected_outputs"]),
                daily_loop_command=spec["daily_loop_command"],
                skill_instructions=tuple(spec["skill_instructions"]),
                source_refs=tuple(spec["source_refs"]),
                bounded_deliverables=tuple(spec["bounded_deliverables"]),
                memory_triggers=tuple(spec["memory_triggers"]),
            ).to_dict()
            for idx, (agent_key, spec) in enumerate(task_specs, start=1)
        ]

        return {
            "mode": mode,
            "objective": objective,
            "memory_context": memory,
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
            for field in (
                "daily_loop_command",
                "skill_instructions",
                "source_refs",
                "bounded_deliverables",
            ):
                if field not in task or task[field] in (None, "", []):
                    raise ValueError(f"Task is missing required field: {field}")
            if not isinstance(task["skill_instructions"], list):
                raise ValueError("Task skill_instructions must be a list.")
            if not isinstance(task["source_refs"], list):
                raise ValueError("Task source_refs must be a list.")
            if not isinstance(task["bounded_deliverables"], list):
                raise ValueError("Task bounded_deliverables must be a list.")
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

    def _memory_aware_task_specs(
        self,
        objective: str,
        memory_context: dict[str, Any],
    ) -> list[tuple[str, dict[str, Any]]]:
        signals = memory_context.get("planning_signals", {})
        failures = signals.get("prior_required_agent_failures", [])
        next_actions = signals.get("pending_next_actions", [])
        assumptions = signals.get("unresolved_assumptions", [])
        fixtures = signals.get("validated_simulation_fixtures", [])
        recipes = signals.get("simulation_recipes", [])
        issues = signals.get("open_github_issues", [])
        rejected_count = signals.get("rejected_claim_count", 0)
        deferred_count = signals.get("deferred_claim_count", 0)
        knowledge_gaps = signals.get("knowledge_gaps", [])

        common_triggers = _compact_triggers(
            [
                f"Rejected claims in durable ledger: {rejected_count}",
                f"Deferred claims in durable ledger: {deferred_count}",
                f"Prior required task failures: {', '.join(failures[:4])}"
                if failures
                else "",
                f"Validated simulation fixtures: {', '.join(_fixture_names(fixtures)[:4])}"
                if fixtures
                else "",
                f"Open GitHub issues available: {len(issues)}",
            ]
        )

        return [
            (
                "literature_agent",
                self._build_task_spec(
                    agent_key="literature_agent",
                    fallback_role="Literature Agent",
                    objective=objective,
                    focus=(
                        "Use prior reports, open issue summaries, and claim-ledger gaps "
                        "to identify the next citation-bounded literature task. Do not "
                        "restate generic candidate-state background unless it resolves a "
                        "recorded claim, assumption, or GitHub issue."
                    ),
                    memory_context=memory_context,
                    source_kinds=(
                        "claim_ledger",
                        "daily_report",
                        "magentic_report",
                        "knowledge_file",
                        "github_issues",
                    ),
                    triggers=common_triggers
                    + _compact_triggers(next_actions[:3] + assumptions[:3]),
                    deliverables=(
                        "At most three literature claims with citation or source identifiers.",
                        "A table separating author claims from validated project evidence.",
                        "Follow-up reading tasks tied to unresolved durable-memory items.",
                    ),
                ),
            ),
            (
                "theory_agent",
                self._build_task_spec(
                    agent_key="theory_agent",
                    fallback_role="Theory Agent",
                    objective=objective,
                    focus=(
                        "Turn unresolved assumptions and rejected overclaims into exact "
                        "or controlled analytical checks for the half-filled second "
                        "Landau level. State the Hamiltonian terms and control "
                        "parameters required before any claim can be accepted."
                    ),
                    memory_context=memory_context,
                    source_kinds=(
                        "claim_ledger",
                        "falsification_log",
                        "daily_report",
                        "knowledge_file",
                    ),
                    triggers=common_triggers
                    + _compact_triggers(assumptions[:5] + knowledge_gaps[:3]),
                    deliverables=(
                        "At most three analytical checks with exact or approximation status.",
                        "Explicit assumptions for finite width, LL mixing, disorder, or spin.",
                        "One falsifiable consequence for the next loop.",
                    ),
                ),
            ),
            (
                "numerics_agent",
                self._build_task_spec(
                    agent_key="numerics_agent",
                    fallback_role="Numerics Agent",
                    objective=objective,
                    focus=(
                        "Use prior validation summaries, simulation recipes, and fixture "
                        "results to select the next bounded numerical action. Preserve "
                        "finite-size caveats and do not convert the Laughlin fixture into "
                        "ν=5/2 evidence."
                    ),
                    memory_context=memory_context,
                    source_kinds=(
                        "simulation_result",
                        "simulation_recipe",
                        "run_summary",
                        "daily_report",
                    ),
                    triggers=common_triggers
                    + _compact_triggers(_fixture_names(fixtures) + _recipe_names(recipes)),
                    deliverables=(
                        "Validate or propose one small deterministic ED recipe.",
                        "Report geometry, particle number, flux, shift, basis size, solver, and tolerance.",
                        "State why the result is finite-size numerical evidence only.",
                    ),
                ),
            ),
            (
                "falsification_agent",
                self._build_task_spec(
                    agent_key="falsification_agent",
                    fallback_role="Falsification Agent",
                    objective=objective,
                    focus=(
                        "Audit the rejected-claim ledger, prior failed agent outputs, "
                        "and unresolved assumptions. Pick the highest-risk overclaim or "
                        "hidden assumption and define a falsification test that can run "
                        "in a future bounded loop."
                    ),
                    memory_context=memory_context,
                    source_kinds=(
                        "falsification_log",
                        "claim_ledger",
                        "run_summary",
                        "github_issues",
                    ),
                    triggers=common_triggers
                    + _compact_triggers(failures[:5] + knowledge_gaps[:5]),
                    deliverables=(
                        "At most three challenged claims or assumptions.",
                        "Severity for each failure mode.",
                        "A concrete next test with required inputs and pass/fail signal.",
                    ),
                ),
            ),
            (
                "experiment_bridge_agent",
                self._build_task_spec(
                    agent_key="experiment_bridge_agent",
                    fallback_role="Experiment Bridge Agent",
                    objective=objective,
                    focus=(
                        "Map durable-memory claims and unresolved assumptions to "
                        "experimental observables. Distinguish direct measurement from "
                        "model-dependent inference for gap, charge, thermal Hall, "
                        "interferometry, disorder, and finite-width effects."
                    ),
                    memory_context=memory_context,
                    source_kinds=(
                        "claim_ledger",
                        "daily_report",
                        "knowledge_file",
                        "github_issues",
                    ),
                    triggers=common_triggers
                    + _compact_triggers(assumptions[:4] + next_actions[:3]),
                    deliverables=(
                        "A compact observable table for at most three candidate discriminants.",
                        "Compatibility notes with explicit uncertainty classification.",
                        "One theory-experiment check for the next loop.",
                    ),
                ),
            ),
            (
                "knowledge_curator_agent",
                self._build_task_spec(
                    agent_key="knowledge_curator_agent",
                    fallback_role="Knowledge Curator Agent",
                    objective=objective,
                    focus=(
                        "Prepare a non-destructive durable-memory update plan from the "
                        "latest reports, run summaries, claim ledger, and falsification "
                        "log. Record previous state before any proposed conclusion change."
                    ),
                    memory_context=memory_context,
                    source_kinds=(
                        "claim_ledger",
                        "falsification_log",
                        "daily_report",
                        "magentic_report",
                        "run_summary",
                    ),
                    triggers=common_triggers
                    + _compact_triggers(next_actions[:5] + assumptions[:5]),
                    deliverables=(
                        "Files or ledger entries that should be updated, without applying writes.",
                        "Claim IDs to add, revise, defer, or reject.",
                        "Revision rationale preserving prior conclusions and falsification findings.",
                    ),
                ),
            ),
        ]

    def _build_task_spec(
        self,
        *,
        agent_key: str,
        fallback_role: str,
        objective: str,
        focus: str,
        memory_context: dict[str, Any],
        source_kinds: tuple[str, ...],
        triggers: list[str],
        deliverables: tuple[str, ...],
    ) -> dict[str, Any]:
        config = self.agent_configs.get(agent_key, {})
        role = config.get("role", fallback_role)
        source_refs = _select_source_refs(memory_context, source_kinds)
        memory_triggers = triggers or ["No prior durable-memory signal was found; create a bootstrap task."]
        command = _compose_daily_loop_command(
            role=role,
            objective=objective,
            focus=focus,
            triggers=memory_triggers,
            source_refs=source_refs,
            deliverables=deliverables,
        )
        allowed_inputs = tuple(config.get("allowed_inputs", ())) or (
            "config",
            "knowledge_base",
            "simulation_fixture",
            "durable_memory_context",
            "github_issue_state",
        )
        expected_outputs = tuple(config.get("expected_outputs", ())) or (
            "claims",
            "artifacts",
            "next_actions",
        )
        return {
            "role": role,
            "objective": f"{objective} {focus}",
            "allowed_inputs": allowed_inputs,
            "expected_outputs": expected_outputs,
            "daily_loop_command": command,
            "skill_instructions": self._skill_instructions(
                agent_key=agent_key,
                role=role,
                allowed_inputs=allowed_inputs,
                expected_outputs=expected_outputs,
            ),
            "source_refs": source_refs,
            "bounded_deliverables": list(deliverables),
            "memory_triggers": memory_triggers,
        }

    def _skill_instructions(
        self,
        *,
        agent_key: str,
        role: str,
        allowed_inputs: tuple[str, ...],
        expected_outputs: tuple[str, ...],
    ) -> list[str]:
        config = self.agent_configs.get(agent_key, {})
        instructions = [
            f"Act as {role}. Scope: {config.get('scope', 'Execute the assigned bounded research task.')}",
            "Treat Pfaffian, anti-Pfaffian, PH-Pfaffian, CFL, stripe/nematic, and other candidates as hypotheses.",
            "Every claim must use exactly one allowed evidence_type label and include support, limitations, and confidence.",
            "Do not present finite-size numerical evidence as thermodynamic proof.",
            f"Allowed inputs: {', '.join(allowed_inputs)}.",
            f"Expected outputs: {', '.join(expected_outputs)}.",
        ]
        evidence_standard = config.get("evidence_standard")
        if evidence_standard:
            instructions.append(f"Evidence standard: {evidence_standard}")
        escalation = config.get("refusal_escalation_criteria", [])
        if escalation:
            instructions.append(
                "Escalate or mark partial/failed when: " + "; ".join(escalation)
            )
        instructions.append(
            "Return only schema-valid JSON with agent_name, agent_role, task_id, run_id, mode, status, summary, claims, artifacts, errors, and next_actions."
        )
        return instructions


def _select_source_refs(
    memory_context: dict[str, Any],
    source_kinds: tuple[str, ...],
    limit: int = 6,
) -> list[dict[str, Any]]:
    refs = []
    for source in memory_context.get("source_index", []):
        if source.get("kind") in source_kinds:
            refs.append(
                {
                    "kind": source.get("kind"),
                    "path": source.get("path"),
                    "summary": source.get("summary"),
                }
            )
        if len(refs) >= limit:
            break
    if refs:
        return refs
    return [
        {
            "kind": "memory_context",
            "path": None,
            "summary": "No matching durable source was available for this role.",
        }
    ]


def _compose_daily_loop_command(
    *,
    role: str,
    objective: str,
    focus: str,
    triggers: list[str],
    source_refs: list[dict[str, Any]],
    deliverables: tuple[str, ...],
) -> str:
    source_list = "; ".join(
        f"{source.get('kind')}:{source.get('path') or 'github'}"
        for source in source_refs
    )
    trigger_list = "; ".join(triggers[:6])
    deliverable_list = "; ".join(deliverables)
    return (
        f"{role} daily command: advance '{objective}' by using durable memory "
        f"sources [{source_list}]. Focus: {focus} Memory triggers: {trigger_list}. "
        f"Bounded deliverables: {deliverable_list}. Do not mutate GitHub or "
        "knowledge-base files from this subagent task; propose updates as artifacts."
    )


def _compact_triggers(values: list[Any]) -> list[str]:
    result = []
    seen = set()
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _fixture_names(fixtures: list[dict[str, Any]]) -> list[str]:
    names = []
    for fixture in fixtures:
        names.append(
            str(
                fixture.get("recipe_id")
                or fixture.get("title")
                or fixture.get("path")
                or "unnamed-fixture"
            )
        )
    return names


def _recipe_names(recipes: list[dict[str, Any]]) -> list[str]:
    names = []
    for recipe in recipes:
        names.append(
            str(
                recipe.get("recipe_id")
                or recipe.get("title")
                or recipe.get("path")
                or "unnamed-recipe"
            )
        )
    return names
