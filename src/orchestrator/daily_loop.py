"""Director-controlled daily research loop entrypoint."""

from __future__ import annotations

import json
import os
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from typing import Any

import yaml

from .client import LLMAdapter
from .director import Director, MalformedAgentOutput
from .github_client import GitHubClient
from .memory import DurableMemoryCollector
from .parallel_runner import ParallelAgentRunner
from .reporting import render_daily_report, write_daily_report, write_json
from .run_modes import BaseRunConfig, get_run_config, validate_environment


class DailyLoopError(RuntimeError):
    """Raised when the daily loop cannot complete safely."""


class DailyLoopRunner:
    """Run the daily research loop in explicit test or production mode."""

    def __init__(
        self,
        workspace_path: str | Path | None = None,
        mode: str = "test",
        run_config: BaseRunConfig | None = None,
        llm_adapter: LLMAdapter | None = None,
        github_client: GitHubClient | None = None,
    ) -> None:
        self.workspace_path = Path(workspace_path or Path.cwd()).resolve()
        self.config = run_config or get_run_config(mode, self.workspace_path)
        self.mode = self.config.mode
        self.llm_adapter = llm_adapter
        self.github_client = github_client

    def run(self, objective: str | None = None) -> dict[str, Any]:
        run_id = _new_run_id(self.mode)
        run_dir = self.config.artifact_root / run_id
        agent_output_dir = run_dir / "agent_outputs"
        failures: list[str] = []
        warnings: list[str] = []
        github_updates: list[str] = []
        artifact_paths: list[str] = []

        validate_environment(self.config)
        project_config = self._load_yaml(self.workspace_path / "config" / "config.yaml")
        agent_configs = self._load_agent_configs()
        memory_context = self._collect_memory_context(project_config)

        if self.config.use_live_foundry and self.llm_adapter is None:
            self.llm_adapter = LLMAdapter(provider=self.config.foundry_provider)

        director = Director(agent_configs=agent_configs, run_config=self.config)
        daily_objective = objective or (
            "Run the daily ν=5/2 FQHE research loop with explicit evidence labels."
        )
        task_graph = director.generate_daily_plan(daily_objective, memory_context)
        director.validate_task_graph(task_graph)

        for task in task_graph["tasks"]:
            task["mode"] = self.mode
            task["run_id"] = run_id

        runner = ParallelAgentRunner(
            run_id=run_id,
            output_dir=agent_output_dir,
            max_parallel_agents=self.config.max_parallel_agents,
        )
        outputs, ledger = runner.run(task_graph["tasks"], self._execute_agent_task)

        validated_outputs = []
        for output in outputs:
            task = _task_by_id(task_graph, output.get("task_id"))
            try:
                director.validate_agent_output(output)
                validated_outputs.append(output)
            except MalformedAgentOutput as exc:
                malformed = director.mark_malformed_output(
                    task=task,
                    run_id=run_id,
                    mode=self.mode,
                    error=str(exc),
                )
                validated_outputs.append(malformed)
                failures.append(f"{task.get('task_id')}: {exc}")

        handoffs = director.extract_valid_theory_handoffs(validated_outputs)
        numerics_tasks = director.append_numerics_tasks_from_handoffs(
            task_graph,
            handoffs,
        )
        if numerics_tasks:
            for task in numerics_tasks:
                task["mode"] = self.mode
                task["run_id"] = run_id
            director.validate_task_graph(task_graph)
            numerics_outputs, numerics_ledger = runner.run(
                numerics_tasks,
                self._execute_agent_task,
            )
            outputs.extend(numerics_outputs)
            ledger.extend(numerics_ledger)
            ledger.sort(key=lambda item: item.get("task_id", ""))
            for output in numerics_outputs:
                task = _task_by_id(task_graph, output.get("task_id"))
                try:
                    director.validate_agent_output(output)
                    validated_outputs.append(output)
                except MalformedAgentOutput as exc:
                    malformed = director.mark_malformed_output(
                        task=task,
                        run_id=run_id,
                        mode=self.mode,
                        error=str(exc),
                    )
                    validated_outputs.append(malformed)
                    failures.append(f"{task.get('task_id')}: {exc}")

        validation_summary = self._run_physics_checks()
        if validation_summary["status"] != "success":
            failures.append("Physics validation failed.")

        synthesis = director.synthesize(
            run_id=run_id,
            mode=self.mode,
            objective=daily_objective,
            task_graph=task_graph,
            outputs=validated_outputs,
            validation_summary=validation_summary,
        )

        required_failures = [
            task["task_id"]
            for task in task_graph["tasks"]
            if task.get("required", True)
            and any(
                output.get("task_id") == task["task_id"]
                and output.get("status") == "failed"
                for output in validated_outputs
            )
        ]
        if required_failures:
            failures.append(
                "Required agent task(s) failed: " + ", ".join(required_failures)
            )

        run_status = "completed" if not failures else "failed"
        if failures and not self.config.fail_on_required_agent_failure:
            run_status = "partial"

        run_dir.mkdir(parents=True, exist_ok=True)
        artifact_paths.append(str(write_json(run_dir / "memory_context.json", memory_context)))
        artifact_paths.append(str(write_json(run_dir / "task_graph.json", task_graph)))
        artifact_paths.append(str(write_json(run_dir / "task_ledger.json", ledger)))
        artifact_paths.append(
            str(write_json(run_dir / "validation_summary.json", validation_summary))
        )

        if self.config.is_production and self.config.github_write_issues:
            preliminary_report = render_daily_report(
                run_id=run_id,
                mode=self.mode,
                objective=daily_objective,
                task_graph=task_graph,
                outputs=validated_outputs,
                validation_summary=validation_summary,
                synthesis=synthesis,
                artifacts=artifact_paths,
                github_updates=["GitHub issue creation pending."],
                failures=failures,
                warnings=warnings,
            )
            github_updates.extend(self._update_github(preliminary_report))
        elif self.config.is_production:
            warnings.append("GitHub writes disabled by DAILY_LOOP_GITHUB_WRITE gate.")

        report = render_daily_report(
            run_id=run_id,
            mode=self.mode,
            objective=daily_objective,
            task_graph=task_graph,
            outputs=validated_outputs,
            validation_summary=validation_summary,
            synthesis=synthesis,
            artifacts=artifact_paths,
            github_updates=github_updates,
            failures=failures,
            warnings=warnings,
        )
        report_path = write_daily_report(run_dir / "daily_report.md", report)
        artifact_paths.append(str(report_path))

        self._write_mode_artifacts(
            run_id=run_id,
            report=report,
            synthesis=synthesis,
            github_updates=github_updates,
            warnings=warnings,
            artifact_paths=artifact_paths,
        )

        summary = {
            "run_id": run_id,
            "mode": self.mode,
            "status": run_status,
            "objective": daily_objective,
            "artifact_dir": str(run_dir),
            "artifacts": artifact_paths,
            "task_count": len(task_graph["tasks"]),
            "agent_statuses": synthesis["agent_statuses"],
            "validation_status": validation_summary["status"],
            "github_updates": github_updates,
            "failures": failures,
            "warnings": warnings,
            "scientific_status": synthesis["scientific_status"],
            "branch_updates": synthesis.get("branch_updates", []),
            "inter_agent_dialogue_summaries": synthesis.get(
                "inter_agent_dialogue_summaries", []
            ),
            "theory_to_numerics_handoffs": synthesis.get(
                "theory_to_numerics_handoffs", []
            ),
        }
        artifact_paths.append(str(write_json(run_dir / "run_summary.json", summary)))

        if self.config.is_production and failures:
            raise DailyLoopError(
                "Production daily loop failed. See run_summary.json for details."
            )

        return summary

    def _execute_agent_task(self, task: dict[str, Any]) -> dict[str, Any]:
        if self.config.use_live_foundry:
            return self._execute_foundry_agent_task(task)

        return _fixture_agent_output(task)

    def _execute_foundry_agent_task(self, task: dict[str, Any]) -> dict[str, Any]:
        if self.llm_adapter is None:
            raise DailyLoopError("Live Foundry execution requested without LLMAdapter.")

        prompt_payload = {
            "task_id": task["task_id"],
            "agent_name": task["agent_name"],
            "agent_role": task["agent_role"],
            "run_id": task["run_id"],
            "mode": self.mode,
            "daily_loop_command": task["daily_loop_command"],
            "skill_instructions": task["skill_instructions"],
            "source_refs": task["source_refs"],
            "bounded_deliverables": task["bounded_deliverables"],
            "memory_triggers": task.get("memory_triggers", []),
            "theory_branch_digest": task.get("theory_branch_digest", []),
            "theory_to_numerics_handoff": task.get("theory_to_numerics_handoff"),
            "expected_outputs": task.get("expected_outputs", []),
        }
        prompt = (
            "Return only valid JSON matching the repository agent output schema. "
            "Do not include Markdown fences. "
            "Use the generated daily_loop_command as the task, not a static role prompt. "
            f"Task payload: {json.dumps(prompt_payload, sort_keys=True)}"
        )
        response = self.llm_adapter.generate_text(
            prompt=prompt,
            system_instruction=(
                "You are a scientific subagent for the ν=5/2 FQHE project. "
                "Every claim must use one allowed evidence label: exact result, "
                "controlled approximation, numerical evidence, variational assumption, "
                "phenomenological argument, or conjecture."
            ),
        )
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError as exc:
            raise DailyLoopError(f"Foundry subagent returned malformed JSON: {exc}") from exc

        return parsed

    def _collect_memory_context(self, project_config: dict[str, Any]) -> dict[str, Any]:
        collector = DurableMemoryCollector(
            workspace_path=self.workspace_path,
            mode=self.mode,
            github_client=self._github_client_for_memory(),
        )
        memory_context = collector.collect()
        memory_context["config_models"] = project_config.get("models", {})
        memory_context["mode_is_canonical"] = self.config.is_production
        return memory_context

    def _github_client_for_memory(self) -> GitHubClient | None:
        if self.github_client is not None:
            return self.github_client

        if self.config.is_test and os.environ.get("DAILY_LOOP_GITHUB_READ") != "true":
            return None

        has_github_env = bool(
            os.environ.get("GITHUB_TOKEN")
            and (
                os.environ.get("RESEARCH_REPOSITORY")
                or os.environ.get("GITHUB_REPOSITORY")
            )
        )
        if not has_github_env:
            return None
        if importlib.util.find_spec("github") is None:
            return None

        try:
            self.github_client = GitHubClient()
        except Exception:
            return None
        return self.github_client

    def _run_physics_checks(self) -> dict[str, Any]:
        fixture_path = self.workspace_path / "simulations" / "results" / "result_example_laughlin.json"
        if not fixture_path.exists():
            return {
                "status": "failed",
                "laughlin_fixture_consumed": False,
                "errors": ["Missing Laughlin validation fixture."],
            }

        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        eigenvalues = data.get("numerical", {}).get("eigenvalues", [])
        lowest = float(eigenvalues[0]) if eigenvalues else None
        solver = data.get("metadata", {}).get("solver")
        success = (
            data.get("metadata", {}).get("status") == "success"
            and solver == "scipy.sparse.linalg.eigsh"
            and lowest is not None
            and abs(lowest) < 1e-10
            and data.get("physics", {}).get("n_particles") == 3
            and data.get("physics", {}).get("n_flux") == 6
        )

        return {
            "status": "success" if success else "failed",
            "laughlin_fixture_consumed": True,
            "fixture_path": str(fixture_path),
            "recipe_id": data.get("recipe_id"),
            "geometry": data.get("physics", {}).get("geometry"),
            "n_particles": data.get("physics", {}).get("n_particles"),
            "n_flux": data.get("physics", {}).get("n_flux"),
            "solver": solver,
            "lowest_eigenvalue": lowest,
            "errors": [] if success else ["Laughlin fixture sanity check failed."],
        }

    def _write_mode_artifacts(
        self,
        *,
        run_id: str,
        report: str,
        synthesis: dict[str, Any],
        github_updates: list[str],
        warnings: list[str],
        artifact_paths: list[str],
    ) -> None:
        if not self.config.write_knowledge_base:
            return

        date = datetime.now(timezone.utc).date().isoformat()
        daily_report_path = (
            self.workspace_path / "knowledge_base" / "daily_reports" / f"{date}.md"
        )
        write_daily_report(daily_report_path, report)
        artifact_paths.append(str(daily_report_path))

        claim_ledger_path = self.workspace_path / "knowledge_base" / "claim_ledger.md"
        falsification_path = self.workspace_path / "knowledge_base" / "falsification_log.md"
        branch_ledger_path = (
            self.workspace_path / "knowledge_base" / "theory_branch_ledger.md"
        )
        _append_markdown_section(
            claim_ledger_path,
            f"## {run_id}\n\n"
            + json.dumps(synthesis["scientific_status"], indent=2)
            + "\n",
        )
        _append_markdown_section(
            falsification_path,
            f"## {run_id}\n\nRejected claims: "
            f"{len(synthesis['scientific_status']['rejected_claims'])}\n",
        )
        branch_artifacts = []
        if synthesis.get("branch_updates"):
            _append_markdown_section(
                branch_ledger_path,
                f"## {run_id}\n\n"
                + json.dumps(
                    {"branches": synthesis.get("branch_updates", [])},
                    indent=2,
                )
                + "\n",
            )
            branch_artifacts.append(str(branch_ledger_path))
        artifact_paths.extend([str(claim_ledger_path), str(falsification_path)])
        artifact_paths.extend(branch_artifacts)

    def _update_github(self, report: str) -> list[str]:
        if self.github_client is None:
            self.github_client = GitHubClient()
        if not self.github_client.is_configured():
            raise DailyLoopError("GitHub mutation requested but client is unconfigured.")

        issue_number = self.github_client.create_issue(
            title=f"Daily research loop: {datetime.now(timezone.utc).date().isoformat()}",
            body=report,
            labels=["daily-loop", f"mode:{self.mode}"],
        )
        if issue_number == -1:
            raise DailyLoopError("GitHub issue creation failed.")

        updates = [f"Created GitHub issue #{issue_number}."]

        if self.config.github_create_prs:
            head_branch = os.environ.get("DAILY_LOOP_PR_HEAD_BRANCH")
            base_branch = os.environ.get("DAILY_LOOP_PR_BASE_BRANCH", "main")
            if not head_branch:
                raise DailyLoopError(
                    "DAILY_LOOP_CREATE_PR=true requires DAILY_LOOP_PR_HEAD_BRANCH."
                )

            pr_number = self.github_client.create_pull_request(
                title=f"Daily loop artifacts: {datetime.now(timezone.utc).date().isoformat()}",
                body=f"Daily loop report issue: #{issue_number}",
                head_branch=head_branch,
                base_branch=base_branch,
            )
            if pr_number == -1:
                raise DailyLoopError("GitHub pull request creation failed.")
            updates.append(f"Created GitHub PR #{pr_number}.")

        return updates

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as handle:
            documents = yaml.safe_load_all(handle)
            for document in documents:
                if isinstance(document, dict):
                    return document
        return {}

    def _load_agent_configs(self) -> dict[str, dict[str, Any]]:
        configs: dict[str, dict[str, Any]] = {}
        root = self.workspace_path / "config" / "agents"
        for path in sorted(root.rglob("*.yaml")):
            data = self._load_yaml(path)
            if data:
                configs[path.stem] = data
        return configs


def run_daily_loop(
    mode: str = "test",
    workspace_path: str | Path | None = None,
    objective: str | None = None,
) -> dict[str, Any]:
    return DailyLoopRunner(workspace_path=workspace_path, mode=mode).run(
        objective=objective
    )


def _fixture_agent_output(task: dict[str, Any]) -> dict[str, Any]:
    evidence = "numerical evidence" if "numerics" in task["agent_name"] else "conjecture"
    if "theory" in task["agent_name"]:
        evidence = "controlled approximation"
    if "falsification" in task["agent_name"]:
        evidence = "phenomenological argument"

    output = {
        "agent_name": task["agent_name"],
        "agent_role": task["agent_role"],
        "task_id": task["task_id"],
        "run_id": task["run_id"],
        "mode": task["mode"],
        "status": "success",
        "summary": f"Completed deterministic {task['agent_role']} fixture task.",
        "claims": [
            {
                "claim_id": f"{task['task_id']}-claim-1",
                "text": (
                    "The N=3, N_flux=6 Laughlin fixture is suitable as a small "
                    "orchestration sanity check, not as ν=5/2 production evidence."
                ),
                "evidence_type": evidence,
                "support": "Uses the checked fixture and explicit mode separation.",
                "limitations": "Fixture is a small ν=1/3 validation artifact, not a ν=5/2 result.",
                "confidence": "medium",
            }
        ],
        "artifacts": [],
        "errors": [],
        "next_actions": [
            "Promote only after production mode validates live Foundry and GitHub gates."
        ],
        "branch_updates": [],
        "theory_to_numerics_handoffs": [],
    }

    if task["agent_name"] == "theory_agent":
        output["branch_updates"] = [
            {
                "branch_id": "finite-width-llm-perturbation",
                "title": "Finite-width and Landau-level-mixing perturbation check",
                "status": "active",
                "rationale": (
                    "A bounded Hamiltonian perturbation can be specified without "
                    "assuming a candidate state is correct."
                ),
                "revival_criteria": "",
            }
        ]
        output["theory_to_numerics_handoffs"] = [
            {
                "handoff_id": f"{task['task_id']}-handoff-1",
                "source_task_id": task["task_id"],
                "artifact_type": "hamiltonian_perturbation",
                "description": (
                    "Compare the small Laughlin fixture Hamiltonian with an explicit "
                    "bounded delta-V1 pseudopotential perturbation as an orchestration "
                    "verification program, not as ν=5/2 evidence."
                ),
                "required_numerics": (
                    "Design, write, execute, and report a deterministic finite-size "
                    "fixture check that records solver metadata and finite-size caveats."
                ),
                "evidence_label": "controlled approximation",
            }
        ]

    if task["agent_name"] == "numerics_agent":
        handoff = task.get("theory_to_numerics_handoff", {})
        output["summary"] = (
            "Completed deterministic gated Numerics Agent fixture task for "
            f"handoff `{handoff.get('handoff_id', 'unknown')}`."
        )
        output["claims"][0]["text"] = (
            "The gated numerics fixture verifies that a Director-approved theory "
            "handoff can produce a bounded finite-size verification report; it is "
            "not thermodynamic ν=5/2 evidence."
        )
        output["artifacts"] = [
            {
                "path": "simulations/results/result_example_laughlin.json",
                "type": "simulation_output",
            }
        ]
        output["verification_program"] = {
            "description": (
                "Use the existing deterministic Laughlin fixture result as the "
                "bounded verification program for orchestration plumbing."
            ),
            "path": "simulations/results/result_example_laughlin.json",
            "status": "reported",
        }
        output["execution_metadata"] = {
            "geometry": "sphere",
            "n_particles": 3,
            "n_flux": 6,
            "shift": 3,
            "basis_dimension": 5,
            "solver": "scipy.sparse.linalg.eigsh",
            "convergence_status": "success",
            "tolerance": 1e-10,
        }

    return output


def _new_run_id(mode: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{mode}-{uuid4().hex[:8]}"


def _task_by_id(task_graph: dict[str, Any], task_id: str | None) -> dict[str, Any]:
    for task in task_graph.get("tasks", []):
        if task.get("task_id") == task_id:
            return task
    return {}


def _append_markdown_section(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else f"# {path.stem}\n\n"
    path.write_text(existing.rstrip() + "\n\n" + text, encoding="utf-8")
