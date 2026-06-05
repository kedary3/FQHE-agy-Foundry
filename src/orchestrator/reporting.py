"""Daily loop report and JSON summary rendering."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json(path: str | Path, data: dict[str, Any] | list[Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return target


def render_daily_report(
    *,
    run_id: str,
    mode: str,
    objective: str,
    task_graph: dict[str, Any],
    outputs: list[dict[str, Any]],
    validation_summary: dict[str, Any],
    synthesis: dict[str, Any],
    artifacts: list[str],
    github_updates: list[str],
    failures: list[str],
    warnings: list[str],
) -> str:
    status = synthesis["scientific_status"]
    memory_context = task_graph.get("memory_context", {})
    planning_signals = memory_context.get("planning_signals", {})
    github_issue_state = memory_context.get("sources", {}).get("github_issues", {})
    branch_digest = memory_context.get("theory_branch_digest", [])
    dialogue_summaries = synthesis.get(
        "inter_agent_dialogue_summaries",
        task_graph.get("inter_agent_dialogue_summaries", []),
    )
    branch_updates = synthesis.get("branch_updates", [])
    theory_handoffs = synthesis.get("theory_to_numerics_handoffs", [])

    lines = [
        "# Daily Research Loop Report",
        "",
        "## Run metadata",
        f"- Run ID: `{run_id}`",
        f"- Mode: `{mode.upper()}`",
        "",
        "## Mode",
        _mode_description(mode),
        "",
        "## Daily objective",
        objective,
        "",
        "## Director plan",
        f"- Planned tasks: {len(task_graph.get('tasks', []))}",
        f"- Parallel groups: {len(task_graph.get('parallel_groups', []))}",
        f"- Durable memory sources indexed: {len(memory_context.get('source_index', []))}",
        f"- Prior required task failures considered: {len(planning_signals.get('prior_required_agent_failures', []))}",
        f"- Rejected claims considered: {planning_signals.get('rejected_claim_count', 0)}",
        f"- Open GitHub issues considered: {len(planning_signals.get('open_github_issues', []))}",
        "",
        "## Theory branch ledger digest",
    ]

    if branch_digest:
        for branch in branch_digest[:8]:
            lines.append(
                f"- `{branch.get('status')}` `{branch.get('branch_id')}`: "
                f"{branch.get('title')} Revival: {branch.get('revival_criteria') or 'not applicable'}"
            )
    else:
        lines.append("- No prior branch ledger entries were available.")

    lines.extend(
        [
            "",
            "## Inter-agent dialogue summaries",
        ]
    )
    if dialogue_summaries:
        for dialogue in dialogue_summaries:
            lines.append(
                f"- `{dialogue.get('dialogue_id')}` status=`{dialogue.get('status')}` "
                f"participants={', '.join(dialogue.get('participants', []))}: "
                f"{dialogue.get('summary')}"
            )
            lines.append(f"- Refined goal: {dialogue.get('refined_goal')}")
            for turn in dialogue.get("turns", [])[:6]:
                lines.append(
                    f"- Planning turn `{turn.get('speaker')}`: {turn.get('message')}"
                )
            for rule in dialogue.get("handoff_rules", [])[:3]:
                lines.append(f"- Handoff rule: {rule}")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Durable memory sources",
        ]
    )

    for source in memory_context.get("source_index", [])[:10]:
        path = source.get("path") or "github"
        lines.append(
            f"- `{source.get('kind')}` `{path}`: {source.get('summary', '')}"
        )
    if not memory_context.get("source_index"):
        lines.append("- None indexed.")
    if github_issue_state and not github_issue_state.get("available"):
        lines.append(f"- GitHub issue read state: {github_issue_state.get('error')}")

    lines.extend(
        [
            "",
            "## Agent task graph",
        ]
    )

    for task in task_graph.get("tasks", []):
        lines.append(
            f"- `{task['task_id']}` -> {task['agent_role']}: "
            f"{task.get('daily_loop_command', task['objective'])}"
        )

    lines.extend(["", "## Subagent results"])
    for output in outputs:
        lines.append(
            f"- `{output.get('task_id')}` {output.get('agent_role')} "
            f"status=`{output.get('status')}`: {output.get('summary')}"
        )

    lines.extend(["", "## Branch updates"])
    if branch_updates:
        for update in branch_updates:
            lines.append(
                f"- `{update.get('status')}` `{update.get('branch_id')}`: "
                f"{update.get('title')} Rationale: {update.get('rationale')}"
            )
            if update.get("status") == "pruned":
                lines.append(
                    f"- Revival criteria for `{update.get('branch_id')}`: "
                    f"{update.get('revival_criteria')}"
                )
    else:
        lines.append("- None.")

    lines.extend(["", "## Theory to numerics handoffs"])
    if theory_handoffs:
        for handoff in theory_handoffs:
            lines.append(
                f"- `{handoff.get('handoff_id')}` type=`{handoff.get('artifact_type')}` "
                f"from `{handoff.get('source_task_id')}`: {handoff.get('description')}"
            )
            lines.append(f"- Required numerics: {handoff.get('required_numerics')}")
    else:
        lines.append("- None accepted; numerics was not instantiated.")

    lines.extend(
        [
            "",
            "## Physics and validation checks",
            f"- Status: `{validation_summary.get('status')}`",
            f"- Laughlin fixture consumed: `{validation_summary.get('laughlin_fixture_consumed')}`",
            f"- Lowest eigenvalue: `{validation_summary.get('lowest_eigenvalue')}`",
            f"- Solver: `{validation_summary.get('solver')}`",
            "",
            "## Scientific status of today's loop",
            "",
            "## Accepted claims",
        ]
    )
    _append_claims(lines, status["accepted_claims"])

    lines.append("")
    lines.append("## Rejected claims")
    _append_claims(lines, status["rejected_claims"])

    lines.append("")
    lines.append("## Deferred claims")
    _append_claims(lines, status["deferred_claims"])

    lines.extend(["", "## Unresolved assumptions"])
    if status["unresolved_assumptions"]:
        lines.extend(f"- {item}" for item in status["unresolved_assumptions"])
    else:
        lines.append("- None recorded.")

    lines.extend(["", "## Artifacts written"])
    lines.extend(f"- `{artifact}`" for artifact in artifacts)

    lines.extend(["", "## GitHub updates"])
    if github_updates:
        lines.extend(f"- {update}" for update in github_updates)
    else:
        lines.append("- None.")

    lines.extend(["", "## Failures and warnings"])
    if failures:
        lines.extend(f"- FAILURE: {failure}" for failure in failures)
    if warnings:
        lines.extend(f"- WARNING: {warning}" for warning in warnings)
    if not failures and not warnings:
        lines.append("- None.")

    lines.extend(["", "## Recommended next loop"])
    next_tests = status["proposed_next_tests"]
    if next_tests:
        lines.extend(f"- {item}" for item in next_tests)
    else:
        lines.append("- Re-run the validation loop with a more specific objective.")

    lines.append("")
    return "\n".join(lines)


def write_daily_report(path: str | Path, report: str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report, encoding="utf-8")
    return target


def _append_claims(lines: list[str], claims: list[dict[str, Any]]) -> None:
    if not claims:
        lines.append("- None.")
        return

    for claim in claims:
        evidence = claim.get("evidence_type", "unclassified")
        text = claim.get("text", claim.get("reason", "No text provided."))
        lines.append(f"- `{evidence}` {text}")


def _mode_description(mode: str) -> str:
    if mode == "test":
        return (
            "TEST mode runs the full loop machinery, but scientific results are "
            "provisional and noncanonical. Production memory and GitHub writes "
            "are disabled by default."
        )

    return (
        "PRODUCTION mode is the canonical daily research loop. Outputs may update "
        "durable project memory and GitHub artifacts when explicit gates permit."
    )
