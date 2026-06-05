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
    theory_branch_digest: tuple[dict[str, Any], ...] = ()
    theory_to_numerics_handoff: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {
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
            "theory_branch_digest": list(self.theory_branch_digest),
        }
        if self.theory_to_numerics_handoff:
            data["theory_to_numerics_handoff"] = self.theory_to_numerics_handoff
        return data


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
        dialogue_summaries = self.plan_inter_agent_dialogue(objective, memory)
        theory_branch_digest = tuple(memory.get("theory_branch_digest", []))

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
                theory_branch_digest=theory_branch_digest
                if agent_key == "theory_agent"
                else (),
            ).to_dict()
            for idx, (agent_key, spec) in enumerate(task_specs, start=1)
        ]

        return {
            "mode": mode,
            "objective": objective,
            "memory_context": memory,
            "inter_agent_dialogue_summaries": dialogue_summaries,
            "parallel_groups": [
                {
                    "group_id": "planning-and-theory-subagents",
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
            if not isinstance(task.get("theory_branch_digest", []), list):
                raise ValueError("Task theory_branch_digest must be a list.")
            if task.get("theory_to_numerics_handoff") is not None:
                self.validate_theory_to_numerics_handoff(
                    task["theory_to_numerics_handoff"]
                )
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

        for update in output.get("branch_updates", []):
            self.validate_branch_update(update)

        for handoff in output.get("theory_to_numerics_handoffs", []):
            self.validate_theory_to_numerics_handoff(handoff)

        if output.get("agent_name") == "numerics_agent":
            self.validate_numerics_verification_output(output)

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
            "branch_updates": [],
            "theory_to_numerics_handoffs": [],
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
        branch_updates: list[dict[str, Any]] = []
        handoffs: list[dict[str, Any]] = []

        for output in outputs:
            proposed_next_tests.extend(output.get("next_actions", []))
            branch_updates.extend(output.get("branch_updates", []))
            handoffs.extend(output.get("theory_to_numerics_handoffs", []))
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
            "branch_updates": branch_updates,
            "inter_agent_dialogue_summaries": task_graph.get(
                "inter_agent_dialogue_summaries", []
            ),
            "theory_to_numerics_handoffs": handoffs,
            "scientific_status": {
                "accepted_claims": classifications["accepted"],
                "rejected_claims": classifications["rejected"],
                "deferred_claims": classifications["deferred"],
                "unresolved_assumptions": sorted(set(unresolved_assumptions)),
                "proposed_next_tests": sorted(set(proposed_next_tests)),
            },
        }

    def plan_inter_agent_dialogue(
        self,
        objective: str,
        memory_context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Create a bounded Director-validated planning dialogue summary."""
        memory = memory_context or {}
        digest = memory.get("theory_branch_digest", [])
        active_or_deferred = [
            branch
            for branch in digest
            if branch.get("status") in {"active", "deferred"}
        ][:3]
        pruned = [branch for branch in digest if branch.get("status") == "pruned"][:3]

        summary = {
            "dialogue_id": "director-preflight-1",
            "participants": [
                "director_pi",
                "theory_agent",
                "falsification_agent",
                "experiment_bridge_agent",
            ],
            "objective": objective,
            "turn_limit": 6,
            "summary": (
                "Bounded pre-execution planning asks theory to avoid pruned "
                "branches unless revival criteria are met, falsification to "
                "challenge hidden assumptions, and experiment bridge to define "
                "observable handoffs."
            ),
            "turns": [
                {
                    "speaker": "theory_agent",
                    "message": (
                        "Use the branch digest to avoid pruned candidate-consensus "
                        "and finite-size-proof avenues unless their revival criteria "
                        "are explicitly satisfied."
                    ),
                },
                {
                    "speaker": "falsification_agent",
                    "message": (
                        "Challenge any handoff that lacks a specified Hamiltonian "
                        "perturbation, observable, ansatz, or finite-size test."
                    ),
                },
                {
                    "speaker": "experiment_bridge_agent",
                    "message": (
                        "Prefer handoffs tied to observables or sample effects that "
                        "could later be compared with gap, charge, thermal Hall, "
                        "interferometry, disorder, or finite-width constraints."
                    ),
                },
                {
                    "speaker": "director_pi",
                    "message": (
                        "The Director will validate dialogue output, create the final "
                        "task graph, and instantiate numerics only after a credible "
                        "theory artifact is received."
                    ),
                },
            ],
            "refined_goal": (
                "Generate evidence-labeled theory work that either updates the "
                "branch ledger or produces a concrete artifact eligible for a "
                "theory-gated numerics handoff."
            ),
            "assumption_challenges": [
                "Do not treat finite-size trends as thermodynamic proof.",
                "Do not revive pruned avenues without explicit revival criteria.",
            ],
            "handoff_rules": [
                "Numerics may be created only from a Director-validated theory artifact.",
                "A valid handoff must name a Hamiltonian perturbation, observable, ansatz, or finite-size test.",
            ],
            "active_or_deferred_branches": active_or_deferred,
            "pruned_branches_to_avoid": pruned,
            "status": "validated",
        }
        self.validate_inter_agent_dialogue_summary(summary)
        return [summary]

    def validate_inter_agent_dialogue_summary(self, summary: dict[str, Any]) -> None:
        for field in (
            "dialogue_id",
            "participants",
            "summary",
            "turns",
            "refined_goal",
            "assumption_challenges",
            "handoff_rules",
            "status",
        ):
            if field not in summary or summary[field] in (None, "", []):
                raise ValueError(
                    f"Inter-agent dialogue summary missing required field: {field}"
                )
        if summary["status"] != "validated":
            raise ValueError("Inter-agent dialogue summary must be Director-validated.")

    def validate_branch_update(self, update: dict[str, Any]) -> None:
        for field in ("branch_id", "title", "status", "rationale"):
            if field not in update or update[field] in (None, ""):
                raise MalformedAgentOutput(
                    f"Branch update missing required field: {field}"
                )
        if update["status"] not in {"active", "deferred", "pruned", "validated"}:
            raise MalformedAgentOutput(
                f"Invalid branch update status: {update['status']}"
            )
        if update["status"] == "pruned" and not update.get("revival_criteria"):
            raise MalformedAgentOutput(
                "Pruned branch update requires revival_criteria."
            )

    def validate_theory_to_numerics_handoff(self, handoff: dict[str, Any]) -> None:
        for field in (
            "handoff_id",
            "source_task_id",
            "artifact_type",
            "description",
            "required_numerics",
            "evidence_label",
        ):
            if field not in handoff or handoff[field] in (None, "", []):
                raise MalformedAgentOutput(
                    f"Theory-to-numerics handoff missing required field: {field}"
                )
        if handoff["artifact_type"] not in {
            "hamiltonian_perturbation",
            "observable",
            "ansatz",
            "finite_size_test",
        }:
            raise MalformedAgentOutput(
                f"Invalid theory artifact_type: {handoff['artifact_type']}"
            )
        if handoff["evidence_label"] not in EVIDENCE_TYPES:
            raise MalformedAgentOutput(
                f"Invalid handoff evidence_label: {handoff['evidence_label']}"
            )

    def validate_numerics_verification_output(self, output: dict[str, Any]) -> None:
        program = output.get("verification_program")
        if not isinstance(program, dict):
            raise MalformedAgentOutput(
                "Numerics output missing required verification_program object."
            )
        for field in ("description", "path", "status"):
            if field not in program or program[field] in (None, ""):
                raise MalformedAgentOutput(
                    f"Numerics verification_program missing required field: {field}"
                )
        if program["status"] not in {"designed", "written", "executed", "reported"}:
            raise MalformedAgentOutput(
                f"Invalid numerics verification_program status: {program['status']}"
            )

        metadata = output.get("execution_metadata")
        if not isinstance(metadata, dict):
            raise MalformedAgentOutput(
                "Numerics output missing required execution_metadata object."
            )
        for field in (
            "geometry",
            "n_particles",
            "n_flux",
            "shift",
            "basis_dimension",
            "solver",
            "convergence_status",
            "tolerance",
        ):
            if field not in metadata or metadata[field] in (None, ""):
                raise MalformedAgentOutput(
                    f"Numerics execution_metadata missing required field: {field}"
                )

    def extract_valid_theory_handoffs(
        self,
        outputs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        handoffs: list[dict[str, Any]] = []
        for output in outputs:
            if output.get("agent_name") != "theory_agent":
                continue
            if output.get("status") == "failed":
                continue
            for handoff in output.get("theory_to_numerics_handoffs", []):
                self.validate_theory_to_numerics_handoff(handoff)
                handoffs.append(handoff)
        return handoffs

    def append_numerics_tasks_from_handoffs(
        self,
        task_graph: dict[str, Any],
        handoffs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Append numerics tasks only for credible Director-validated theory artifacts."""
        if not handoffs:
            return []

        existing_ids = {task["task_id"] for task in task_graph.get("tasks", [])}
        appended = []
        mode = task_graph.get("mode", self.run_config.mode if self.run_config else "test")
        start_idx = len(task_graph.get("tasks", [])) + 1
        for offset, handoff in enumerate(handoffs, start=0):
            task_id = f"{mode}-{start_idx + offset:02d}-numerics_agent"
            if task_id in existing_ids:
                continue
            task = self._build_numerics_task_from_handoff(
                task_id=task_id,
                objective=task_graph["objective"],
                handoff=handoff,
            )
            appended.append(task)
            task_graph.setdefault("tasks", []).append(task)

        if appended:
            task_graph.setdefault("parallel_groups", []).append(
                {
                    "group_id": "theory-gated-numerics",
                    "task_ids": [task["task_id"] for task in appended],
                    "depends_on": sorted(
                        {handoff["source_task_id"] for handoff in handoffs}
                    ),
                }
            )
        return appended

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
            "Return only schema-valid JSON with agent_name, agent_role, task_id, run_id, mode, status, summary, claims, artifacts, errors, next_actions, and optional branch_updates plus theory_to_numerics_handoffs."
        )
        return instructions

    def _build_numerics_task_from_handoff(
        self,
        *,
        task_id: str,
        objective: str,
        handoff: dict[str, Any],
    ) -> dict[str, Any]:
        config = self.agent_configs.get("numerics_agent", {})
        role = config.get("role", "Numerics Agent")
        deliverables = (
            "Design the smallest verification program that tests the supplied theory artifact.",
            "Write or identify the executable recipe/program and record the artifact path.",
            "Execute the bounded verification when allowed by mode and budget.",
            "Report geometry, particle number, flux, shift, basis size, solver, convergence, tolerance, and limitations.",
            "Label every conclusion as finite-size numerical evidence, exact finite-Hamiltonian result, or another allowed evidence label.",
        )
        command = (
            f"{role} gated command: advance '{objective}' only through Director "
            f"handoff `{handoff['handoff_id']}` from `{handoff['source_task_id']}`. "
            f"Theory artifact type: {handoff['artifact_type']}. Description: "
            f"{handoff['description']} Required numerics: {handoff['required_numerics']}. "
            "Do not run exploratory numerics outside this handoff."
        )
        return AgentTask(
            task_id=task_id,
            agent_name="numerics_agent",
            agent_role=role,
            objective=objective,
            allowed_inputs=(
                "theory_to_numerics_handoff",
                "simulation_fixture",
                "simulation_recipe",
                "durable_memory_context",
            ),
            expected_outputs=(
                "verification_program",
                "simulation_result",
                "claims",
                "artifacts",
            ),
            daily_loop_command=command,
            skill_instructions=tuple(
                self._skill_instructions(
                    agent_key="numerics_agent",
                    role=role,
                    allowed_inputs=(
                        "theory_to_numerics_handoff",
                        "simulation_fixture",
                        "simulation_recipe",
                        "durable_memory_context",
                    ),
                    expected_outputs=(
                        "verification_program",
                        "simulation_result",
                        "claims",
                        "artifacts",
                    ),
                )
            ),
            source_refs=(
                {
                    "kind": "theory_to_numerics_handoff",
                    "path": None,
                    "summary": handoff["description"],
                },
            ),
            bounded_deliverables=deliverables,
            memory_triggers=(
                f"Director accepted theory handoff {handoff['handoff_id']}.",
            ),
            theory_to_numerics_handoff=handoff,
        ).to_dict()


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
