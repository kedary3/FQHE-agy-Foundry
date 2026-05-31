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
        "",
        "## Agent task graph",
    ]

    for task in task_graph.get("tasks", []):
        lines.append(
            f"- `{task['task_id']}` -> {task['agent_role']}: {task['objective']}"
        )

    lines.extend(["", "## Subagent results"])
    for output in outputs:
        lines.append(
            f"- `{output.get('task_id')}` {output.get('agent_role')} "
            f"status=`{output.get('status')}`: {output.get('summary')}"
        )

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
