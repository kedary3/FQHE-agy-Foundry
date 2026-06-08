"""Durable research-memory collection for daily-loop planning."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml


AUTHORIZATION_BEARER_RE = re.compile(
    r"(Authorization\s*:\s*Bearer\s+)[A-Za-z0-9._\-+/=]+",
    re.IGNORECASE,
)
INLINE_BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9._\-+/=]+", re.IGNORECASE)
KNOWN_TOKEN_RE = re.compile(
    r"\b(?:gh[pousr]_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{12,}|AIza[0-9A-Za-z_\-]{20,})\b"
)
SECRET_ASSIGNMENT_RE = re.compile(
    r"\b([A-Z0-9_]*(?:TOKEN|KEY|SECRET|PASSWORD|CONNECTION_STRING)[A-Z0-9_]*)\s*[:=]\s*([^\s,;\"'\]\}]+)"
)


class DurableMemoryCollector:
    """Summarize repository and optional GitHub state for bounded planning."""

    def __init__(
        self,
        workspace_path: str | Path,
        mode: str,
        github_client: Any | None = None,
        max_recent_runs: int = 6,
        max_recent_reports: int = 5,
    ) -> None:
        self.workspace_path = Path(workspace_path).resolve()
        self.mode = mode
        self.github_client = github_client
        self.max_recent_runs = max_recent_runs
        self.max_recent_reports = max_recent_reports

    def collect(self) -> dict[str, Any]:
        """Return a sanitized, compact memory context for the Director."""
        context: dict[str, Any] = {
            "workspace": str(self.workspace_path),
            "mode": self.mode,
            "sources": {},
            "source_index": [],
            "planning_signals": {
                "prior_required_agent_failures": [],
                "rejected_claim_count": 0,
                "accepted_claim_count": 0,
                "deferred_claim_count": 0,
                "pending_next_actions": [],
                "unresolved_assumptions": [],
                "validated_simulation_fixtures": [],
                "simulation_recipes": [],
                "open_github_issues": [],
                "knowledge_gaps": [],
            },
            "theory_branch_digest": [],
        }

        self._collect_knowledge_base(context)
        self._collect_artifact_runs(context)
        self._collect_simulation_artifacts(context)
        self._collect_ad_hoc_reports(context)
        self._collect_github_issue_state(context)
        self._deduplicate_planning_signals(context)
        return context

    def _collect_knowledge_base(self, context: dict[str, Any]) -> None:
        kb_root = self.workspace_path / "knowledge_base"
        claim_ledger = kb_root / "claim_ledger.md"
        falsification_log = kb_root / "falsification_log.md"
        theory_branch_ledger = kb_root / "theory_branch_ledger.md"
        daily_reports_root = kb_root / "daily_reports"

        context["sources"]["claim_ledger"] = self._summarize_claim_ledger(claim_ledger)
        self._add_source(
            context,
            kind="claim_ledger",
            path=claim_ledger,
            summary=context["sources"]["claim_ledger"].get("summary", ""),
        )
        self._merge_claim_signals(context, context["sources"]["claim_ledger"])

        context["sources"]["falsification_log"] = self._summarize_falsification_log(
            falsification_log
        )
        self._add_source(
            context,
            kind="falsification_log",
            path=falsification_log,
            summary=context["sources"]["falsification_log"].get("summary", ""),
        )

        context["sources"]["theory_branch_ledger"] = self._summarize_theory_branch_ledger(
            theory_branch_ledger
        )
        context["theory_branch_digest"] = context["sources"][
            "theory_branch_ledger"
        ].get("digest", [])
        self._add_source(
            context,
            kind="theory_branch_ledger",
            path=theory_branch_ledger,
            summary=context["sources"]["theory_branch_ledger"].get("summary", ""),
        )

        daily_reports = []
        if daily_reports_root.exists():
            for path in sorted(daily_reports_root.glob("*.md"), reverse=True)[
                : self.max_recent_reports
            ]:
                summary = self._summarize_markdown(path, kind="daily_report")
                daily_reports.append(summary)
                self._add_source(
                    context,
                    kind="daily_report",
                    path=path,
                    summary=summary.get("summary", ""),
                )
                self._merge_report_signals(context, summary)
        context["sources"]["daily_reports"] = daily_reports

        knowledge_files = []
        if kb_root.exists():
            excluded = {claim_ledger.resolve(), falsification_log.resolve()}
            for path in sorted(kb_root.rglob("*.md")):
                if path.resolve() in excluded or "daily_reports" in path.parts:
                    continue
                summary = self._summarize_markdown(path, kind="knowledge_file")
                knowledge_files.append(summary)
                self._add_source(
                    context,
                    kind="knowledge_file",
                    path=path,
                    summary=summary.get("summary", ""),
                )
        context["sources"]["knowledge_files"] = knowledge_files[:20]

    def _collect_artifact_runs(self, context: dict[str, Any]) -> None:
        artifact_root = self.workspace_path / "artifacts"
        run_dirs: list[Path] = []
        for mode_root in (artifact_root / "production", artifact_root / "test"):
            if mode_root.exists():
                run_dirs.extend(path for path in mode_root.iterdir() if path.is_dir())

        run_dirs = sorted(run_dirs, key=lambda path: path.name, reverse=True)[
            : self.max_recent_runs
        ]
        runs = []
        for run_dir in run_dirs:
            if not self._is_complete_run_dir(run_dir):
                continue
            run_summary_data = self._read_json(run_dir / "run_summary.json")
            validation_data = self._read_json(run_dir / "validation_summary.json")
            run_summary = run_summary_data if isinstance(run_summary_data, dict) else {}
            validation_summary = validation_data if isinstance(validation_data, dict) else {}
            task_ledger = self._read_json(run_dir / "task_ledger.json")
            agent_outputs = self._summarize_agent_outputs(run_dir / "agent_outputs")

            summary = {
                "run_id": run_summary.get("run_id", run_dir.name),
                "mode": run_summary.get("mode", _mode_from_run_dir(run_dir)),
                "status": run_summary.get("status", "unknown"),
                "validation_status": run_summary.get(
                    "validation_status",
                    validation_summary.get("status", "unknown"),
                ),
                "task_count": run_summary.get("task_count"),
                "failures": run_summary.get("failures", [])[:5],
                "warnings": run_summary.get("warnings", [])[:5],
                "agent_statuses": run_summary.get("agent_statuses", {}),
                "agent_output_failures": agent_outputs["failed_outputs"],
                "agent_next_actions": agent_outputs["next_actions"],
            }
            runs.append(summary)
            self._add_source(
                context,
                kind="run_summary",
                path=run_dir / "run_summary.json",
                summary=(
                    f"{summary['run_id']} status={summary['status']} "
                    f"validation={summary['validation_status']}"
                ),
            )
            self._merge_run_signals(context, summary, task_ledger)
        context["sources"]["recent_runs"] = runs

    @staticmethod
    def _is_complete_run_dir(run_dir: Path) -> bool:
        required = (
            "run_summary.json",
            "task_graph.json",
            "task_ledger.json",
            "validation_summary.json",
            "daily_report.md",
        )
        return all((run_dir / name).exists() for name in required)

    def _collect_simulation_artifacts(self, context: dict[str, Any]) -> None:
        simulations_root = self.workspace_path / "simulations"
        results = []
        for path in sorted((simulations_root / "results").glob("*.json")):
            loaded = self._read_json(path)
            data = loaded if isinstance(loaded, dict) else {}
            physics = data.get("physics", {})
            numerical = data.get("numerical", {})
            metadata = data.get("metadata", {})
            eigenvalues = numerical.get("eigenvalues", [])
            summary = {
                "path": self._rel(path),
                "recipe_id": data.get("recipe_id"),
                "title": data.get("title"),
                "status": metadata.get("status"),
                "geometry": physics.get("geometry"),
                "n_particles": physics.get("n_particles"),
                "n_flux": physics.get("n_flux"),
                "shift": physics.get("shift"),
                "basis_dimension": physics.get("basis_dimension"),
                "solver": metadata.get("solver"),
                "lowest_eigenvalue": eigenvalues[0] if eigenvalues else None,
            }
            results.append(summary)
            self._add_source(
                context,
                kind="simulation_result",
                path=path,
                summary=(
                    f"{summary.get('recipe_id')} status={summary.get('status')} "
                    f"geometry={summary.get('geometry')} N={summary.get('n_particles')} "
                    f"N_flux={summary.get('n_flux')}"
                ),
            )
            if summary["status"] == "success":
                context["planning_signals"]["validated_simulation_fixtures"].append(
                    summary
                )
        context["sources"]["simulation_results"] = results

        recipes = []
        for path in sorted((simulations_root / "recipes").glob("*.yaml")):
            data = self._read_yaml(path)
            summary = {
                "path": self._rel(path),
                "recipe_id": data.get("recipe_id") or data.get("id"),
                "title": data.get("title") or data.get("name"),
                "geometry": _get_nested(data, ("physics", "geometry")),
                "n_particles": _get_nested(data, ("physics", "n_particles")),
                "n_flux": _get_nested(data, ("physics", "n_flux")),
            }
            recipes.append(summary)
            self._add_source(
                context,
                kind="simulation_recipe",
                path=path,
                summary=summary.get("title") or summary.get("recipe_id") or path.name,
            )
            context["planning_signals"]["simulation_recipes"].append(summary)
        context["sources"]["simulation_recipes"] = recipes

    def _collect_ad_hoc_reports(self, context: dict[str, Any]) -> None:
        reports_root = self.workspace_path / "reports"
        reports = []
        if reports_root.exists():
            for path in sorted(reports_root.glob("*.md"), reverse=True)[
                : self.max_recent_reports
            ]:
                summary = self._summarize_markdown(path, kind="magentic_report")
                reports.append(summary)
                self._add_source(
                    context,
                    kind="magentic_report",
                    path=path,
                    summary=summary.get("summary", ""),
                )
                self._merge_report_signals(context, summary)
        context["sources"]["magentic_reports"] = reports

    def _collect_github_issue_state(self, context: dict[str, Any]) -> None:
        issue_state: dict[str, Any] = {
            "available": False,
            "issues": [],
            "error": None,
            "labels_queried": [],
        }
        client = self.github_client
        if client is None:
            issue_state["error"] = "GitHub client not provided."
            context["sources"]["github_issues"] = issue_state
            return

        try:
            if not client.is_configured():
                issue_state["error"] = "GitHub client not configured."
                context["sources"]["github_issues"] = issue_state
                return

            if hasattr(client, "get_open_issues"):
                raw_issues = client.get_open_issues(limit=20)
                issue_state["labels_queried"] = ["all-open"]
            else:
                labels = [
                    "daily-loop",
                    "status:pending",
                    "falsification",
                    "needs-triage",
                ]
                issue_state["labels_queried"] = labels
                raw_issues = []
                seen_numbers = set()
                for label in labels:
                    for issue in client.get_issues_by_label(label):
                        number = getattr(issue, "number", None)
                        if number in seen_numbers:
                            continue
                        seen_numbers.add(number)
                        raw_issues.append(issue)

            issue_state["available"] = True
            issue_state["issues"] = [_normalize_issue(issue) for issue in raw_issues]
            context["planning_signals"]["open_github_issues"].extend(
                issue_state["issues"]
            )
            self._add_source(
                context,
                kind="github_issues",
                summary=f"Open GitHub issues available: {len(issue_state['issues'])}",
            )
        except Exception as exc:  # pragma: no cover - exercised with fake clients in tests.
            issue_state["error"] = sanitize_text(f"{type(exc).__name__}: {exc}")

        context["sources"]["github_issues"] = issue_state

    def _summarize_claim_ledger(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {
                "path": self._rel(path),
                "exists": False,
                "summary": "Claim ledger is missing.",
                "accepted_claim_count": 0,
                "rejected_claim_count": 0,
                "deferred_claim_count": 0,
                "pending_next_actions": [],
                "unresolved_assumptions": [],
            }

        text = self._read_text(path, tail=True)
        objects = _extract_json_objects(text)
        accepted = []
        rejected = []
        deferred = []
        next_actions = []
        assumptions = []
        for item in objects:
            accepted.extend(item.get("accepted_claims", []))
            rejected.extend(item.get("rejected_claims", []))
            deferred.extend(item.get("deferred_claims", []))
            next_actions.extend(item.get("proposed_next_tests", []))
            assumptions.extend(item.get("unresolved_assumptions", []))

        return {
            "path": self._rel(path),
            "exists": True,
            "summary": (
                f"Claim ledger contains {len(accepted)} accepted, "
                f"{len(rejected)} rejected, and {len(deferred)} deferred claims "
                "in parsed recent sections."
            ),
            "accepted_claim_count": len(accepted),
            "rejected_claim_count": len(rejected),
            "deferred_claim_count": len(deferred),
            "pending_next_actions": _dedupe_strings(next_actions)[:10],
            "unresolved_assumptions": _dedupe_strings(assumptions)[:10],
            "recent_excerpt": text,
        }

    def _summarize_falsification_log(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {
                "path": self._rel(path),
                "exists": False,
                "summary": "Falsification log is missing.",
                "recorded_rejected_claims": 0,
            }

        text = self._read_text(path, tail=True)
        counts = [int(match) for match in re.findall(r"Rejected claims:\s*(\d+)", text)]
        return {
            "path": self._rel(path),
            "exists": True,
            "summary": f"Falsification log records {sum(counts)} rejected claims across recent entries.",
            "recorded_rejected_claims": sum(counts),
            "recent_excerpt": text,
        }

    def _summarize_theory_branch_ledger(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {
                "path": self._rel(path),
                "exists": False,
                "summary": "Theory branch ledger is missing.",
                "digest": [],
            }

        text = self._read_text(path, tail=True)
        objects = _extract_json_objects(text)
        entries = []
        for item in objects:
            raw_entries = item.get("branches", [])
            if isinstance(raw_entries, list):
                entries.extend(entry for entry in raw_entries if isinstance(entry, dict))
            if all(
                key in item
                for key in ("branch_id", "title", "status", "rationale")
            ):
                entries.append(item)

        if not entries:
            entries = _extract_branch_table_rows(text)

        digest = []
        for entry in entries:
            status = entry.get("status")
            if status not in {"active", "deferred", "pruned", "validated"}:
                continue
            digest.append(
                {
                    "branch_id": sanitize_text(str(entry.get("branch_id", "")))[:80],
                    "title": sanitize_text(str(entry.get("title", "")))[:160],
                    "status": status,
                    "rationale": sanitize_text(str(entry.get("rationale", "")))[:220],
                    "revival_criteria": sanitize_text(
                        str(entry.get("revival_criteria", ""))
                    )[:220],
                }
            )

        digest = _dedupe_dicts(digest, key_fields=("branch_id", "title"))[:12]
        counts = {status: 0 for status in ("active", "deferred", "pruned", "validated")}
        for entry in digest:
            counts[entry["status"]] += 1
        return {
            "path": self._rel(path),
            "exists": True,
            "summary": (
                "Theory branch ledger contains "
                f"{counts['active']} active, {counts['deferred']} deferred, "
                f"{counts['pruned']} pruned, and {counts['validated']} validated branches "
                "in the bounded digest."
            ),
            "digest": digest,
            "recent_excerpt": text,
        }

    def _summarize_markdown(self, path: Path, kind: str) -> dict[str, Any]:
        text = self._read_text(path)
        headings = [
            line.lstrip("# ").strip()
            for line in text.splitlines()
            if line.startswith("#")
        ][:8]
        failures = [
            line.strip("- ").strip()
            for line in text.splitlines()
            if "FAILURE:" in line or "failed" in line.lower()
        ][:5]
        next_actions = _section_bullets(text, "Recommended next loop")[:5]
        next_actions.extend(_section_bullets(text, "Recommended Next Tasks")[:5])
        assumptions = _section_bullets(text, "Unresolved assumptions")[:5]
        assumptions.extend(_section_bullets(text, "Unresolved Gaps")[:5])
        summary = "; ".join(headings[:3]) if headings else path.name
        return {
            "kind": kind,
            "path": self._rel(path),
            "summary": summary,
            "headings": headings,
            "failures": _dedupe_strings(failures),
            "next_actions": _dedupe_strings(next_actions),
            "unresolved_assumptions": _dedupe_strings(assumptions),
            "excerpt": text,
        }

    def _summarize_agent_outputs(self, output_dir: Path) -> dict[str, Any]:
        failed_outputs = []
        next_actions = []
        if not output_dir.exists():
            return {"failed_outputs": failed_outputs, "next_actions": next_actions}

        for path in sorted(output_dir.glob("*.json")):
            loaded = self._read_json(path)
            data = loaded if isinstance(loaded, dict) else {}
            if data.get("status") == "failed":
                failed_outputs.append(
                    {
                        "path": self._rel(path),
                        "task_id": data.get("task_id"),
                        "agent_name": data.get("agent_name"),
                        "errors": data.get("errors", [])[:3],
                    }
                )
            next_actions.extend(data.get("next_actions", []))
        return {
            "failed_outputs": failed_outputs[:10],
            "next_actions": _dedupe_strings(next_actions)[:10],
        }

    def _merge_claim_signals(
        self,
        context: dict[str, Any],
        claim_summary: dict[str, Any],
    ) -> None:
        signals = context["planning_signals"]
        signals["accepted_claim_count"] += claim_summary.get("accepted_claim_count", 0)
        signals["rejected_claim_count"] += claim_summary.get("rejected_claim_count", 0)
        signals["deferred_claim_count"] += claim_summary.get("deferred_claim_count", 0)
        signals["pending_next_actions"].extend(
            claim_summary.get("pending_next_actions", [])
        )
        signals["unresolved_assumptions"].extend(
            claim_summary.get("unresolved_assumptions", [])
        )

    def _merge_run_signals(
        self,
        context: dict[str, Any],
        run_summary: dict[str, Any],
        task_ledger: dict[str, Any] | list[Any],
    ) -> None:
        signals = context["planning_signals"]
        for failure in run_summary.get("failures", []):
            if "Required agent task(s) failed:" in failure:
                failed_ids = failure.split(":", 1)[1].split(",")
                signals["prior_required_agent_failures"].extend(
                    item.strip() for item in failed_ids if item.strip()
                )
        for task_id, status in run_summary.get("agent_statuses", {}).items():
            if status == "failed":
                signals["prior_required_agent_failures"].append(task_id)
        for failed_output in run_summary.get("agent_output_failures", []):
            task_id = failed_output.get("task_id")
            if task_id:
                signals["prior_required_agent_failures"].append(task_id)
        signals["pending_next_actions"].extend(run_summary.get("agent_next_actions", []))

        if isinstance(task_ledger, list):
            for record in task_ledger:
                if record.get("status") == "failed":
                    signals["prior_required_agent_failures"].append(
                        record.get("task_id", "unknown-task")
                    )

    def _merge_report_signals(
        self,
        context: dict[str, Any],
        report_summary: dict[str, Any],
    ) -> None:
        signals = context["planning_signals"]
        signals["pending_next_actions"].extend(report_summary.get("next_actions", []))
        signals["unresolved_assumptions"].extend(
            report_summary.get("unresolved_assumptions", [])
        )
        if report_summary.get("failures"):
            signals["knowledge_gaps"].extend(report_summary["failures"])

    def _deduplicate_planning_signals(self, context: dict[str, Any]) -> None:
        signals = context["planning_signals"]
        for key in (
            "prior_required_agent_failures",
            "pending_next_actions",
            "unresolved_assumptions",
            "knowledge_gaps",
        ):
            signals[key] = _dedupe_strings(signals.get(key, []))[:20]
        signals["validated_simulation_fixtures"] = _dedupe_dicts(
            signals.get("validated_simulation_fixtures", []),
            key_fields=("path", "recipe_id"),
        )[:10]
        signals["simulation_recipes"] = _dedupe_dicts(
            signals.get("simulation_recipes", []),
            key_fields=("path", "recipe_id"),
        )[:10]
        signals["open_github_issues"] = _dedupe_dicts(
            signals.get("open_github_issues", []),
            key_fields=("number", "title"),
        )[:20]

    def _read_json(self, path: Path) -> dict[str, Any] | list[Any]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return _sanitize_data(data)

    def _read_yaml(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except (OSError, yaml.YAMLError):
            return {}
        if not isinstance(data, dict):
            return {}
        return _sanitize_data(data)

    def _read_text(self, path: Path, *, tail: bool = False, max_chars: int = 4000) -> str:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return ""
        text = sanitize_text(text)
        if len(text) <= max_chars:
            return text
        if tail:
            return "[truncated]\n" + text[-max_chars:]
        return text[:max_chars] + "\n[truncated]"

    def _add_source(
        self,
        context: dict[str, Any],
        *,
        kind: str,
        path: Path | None = None,
        summary: str = "",
    ) -> None:
        context["source_index"].append(
            {
                "kind": kind,
                "path": self._rel(path) if path else None,
                "summary": sanitize_text(summary),
            }
        )

    def _rel(self, path: Path | None) -> str | None:
        if path is None:
            return None
        try:
            return str(path.resolve().relative_to(self.workspace_path))
        except ValueError:
            return str(path)


def sanitize_text(text: str) -> str:
    """Redact common secret-bearing tokens from memory text."""
    redacted = text
    redacted = re.sub(r"://([^/\s:@]+):([^@\s/]+)@", r"://<redacted>:<redacted>@", redacted)
    redacted = AUTHORIZATION_BEARER_RE.sub(r"\1<redacted>", redacted)
    redacted = INLINE_BEARER_RE.sub("Bearer <redacted>", redacted)
    redacted = KNOWN_TOKEN_RE.sub("<redacted>", redacted)
    redacted = SECRET_ASSIGNMENT_RE.sub(
        lambda match: f"{match.group(1)}=<redacted>",
        redacted,
    )
    return redacted


def _sanitize_data(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [_sanitize_data(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _sanitize_data(item) for key, item in value.items()}
    return value


def _normalize_issue(issue: Any) -> dict[str, Any]:
    labels = []
    for label in getattr(issue, "labels", []) or []:
        labels.append(getattr(label, "name", str(label)))

    return {
        "number": getattr(issue, "number", None),
        "title": sanitize_text(str(getattr(issue, "title", ""))),
        "state": getattr(issue, "state", "open"),
        "labels": labels,
        "updated_at": str(getattr(issue, "updated_at", "")) or None,
        "url": getattr(issue, "html_url", None),
    }


def _extract_json_objects(text: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    objects: list[dict[str, Any]] = []
    index = 0
    while index < len(text):
        start = text.find("{", index)
        if start == -1:
            break
        try:
            parsed, offset = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue
        if isinstance(parsed, dict):
            objects.append(_sanitize_data(parsed))
        index = start + offset
    return objects


def _section_bullets(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    bullets = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("# ").strip().lower()
            if in_section and title != heading.lower():
                break
            in_section = title == heading.lower()
            continue
        if in_section and stripped.startswith("- "):
            bullets.append(sanitize_text(stripped[2:].strip()))
    return bullets


def _extract_branch_table_rows(text: str) -> list[dict[str, Any]]:
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "branch_id" in stripped.lower():
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 5 or set(cells[0]) <= {"-"}:
            continue
        rows.append(
            {
                "branch_id": cells[0],
                "title": cells[1],
                "status": cells[2].lower(),
                "rationale": cells[3],
                "revival_criteria": cells[4],
            }
        )
    return rows


def _dedupe_strings(values: list[Any]) -> list[str]:
    seen = set()
    result = []
    placeholders = {"none", "none.", "none recorded", "none recorded.", "n/a"}
    for value in values:
        text = sanitize_text(str(value)).strip()
        if not text or text.lower() in placeholders or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _dedupe_dicts(
    values: list[dict[str, Any]],
    *,
    key_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for item in values:
        key = tuple(item.get(field) for field in key_fields)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _get_nested(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _mode_from_run_dir(run_dir: Path) -> str:
    if run_dir.parent.name in {"test", "production"}:
        return run_dir.parent.name
    return "unknown"
