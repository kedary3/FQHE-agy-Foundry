import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.orchestrator.daily_loop import DailyLoopRunner
from src.orchestrator.client import _foundry_credential
from src.orchestrator.director import Director, MalformedAgentOutput
from src.orchestrator.memory import DurableMemoryCollector
from src.orchestrator.parallel_runner import ParallelAgentRunner
from src.orchestrator.run_modes import (
    ProductionRunConfig,
    RunModeConfigurationError,
    TestRunConfig as DailyTestRunConfig,
    validate_environment,
)


WORKSPACE = Path(__file__).resolve().parents[1]


def test_test_mode_does_not_require_real_production_secrets(tmp_path):
    config = DailyTestRunConfig(artifact_root=tmp_path)

    validate_environment(config, env={})


def test_production_mode_requires_foundry_configuration():
    config = ProductionRunConfig()

    with pytest.raises(RunModeConfigurationError, match="AZURE_AI_PROJECT_ENDPOINT"):
        validate_environment(config, env={})


def test_production_mode_rejects_azure_cli_auth():
    config = ProductionRunConfig()

    with pytest.raises(RunModeConfigurationError, match="FOUNDRY_AUTH_MODE=azure_cli"):
        validate_environment(
            config,
            env={
                "AZURE_AI_PROJECT_ENDPOINT": "https://example.invalid",
                "FOUNDRY_AGENT_ID": "agent",
                "RESEARCH_REPOSITORY": "owner/repo",
                "FOUNDRY_AUTH_MODE": "azure_cli",
            },
        )


def test_foundry_credential_includes_azure_cli_when_explicitly_requested(monkeypatch):
    monkeypatch.setenv("FOUNDRY_AUTH_MODE", "azure_cli")

    credential = _foundry_credential()

    assert credential.__class__.__name__ == "ChainedTokenCredential"


def test_director_produces_valid_task_graph():
    director = Director(run_config=DailyTestRunConfig())

    task_graph = director.generate_daily_plan("Validate the daily loop.")
    director.validate_task_graph(task_graph)

    assert task_graph["mode"] == "test"
    assert task_graph["tasks"]
    assert task_graph["tasks"][0]["agent_name"] == "literature_agent"
    assert task_graph["tasks"][0]["daily_loop_command"]
    assert task_graph["tasks"][0]["skill_instructions"]


def test_memory_collector_reads_durable_artifacts_and_github_issue_state(tmp_path):
    (tmp_path / "knowledge_base" / "daily_reports").mkdir(parents=True)
    (tmp_path / "knowledge_base" / "claim_ledger.md").write_text(
        "\n".join(
            [
                "# claim_ledger",
                "## run-1",
                json.dumps(
                    {
                        "accepted_claims": [{"claim_id": "A", "text": "accepted"}],
                        "rejected_claims": [{"claim_id": "R", "text": "rejected"}],
                        "deferred_claims": [{"claim_id": "D", "text": "deferred"}],
                        "unresolved_assumptions": ["GITHUB_TOKEN=ghp_secretvalue"],
                        "proposed_next_tests": ["Return output matching schema."],
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "knowledge_base" / "falsification_log.md").write_text(
        "# falsification_log\n\n## run-1\n\nRejected claims: 1\n",
        encoding="utf-8",
    )
    (tmp_path / "knowledge_base" / "daily_reports" / "2026-06-01.md").write_text(
        "# Daily Research Loop Report\n\n## Recommended next loop\n- Add nu=5/2 ED recipe.\n",
        encoding="utf-8",
    )

    run_dir = tmp_path / "artifacts" / "test" / "run-1"
    (run_dir / "agent_outputs").mkdir(parents=True)
    (run_dir / "run_summary.json").write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "mode": "test",
                "status": "failed",
                "validation_status": "success",
                "agent_statuses": {"test-01-literature_agent": "failed"},
                "failures": [
                    "Required agent task(s) failed: test-01-literature_agent"
                ],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "task_ledger.json").write_text(
        json.dumps([{"task_id": "test-01-literature_agent", "status": "failed"}]),
        encoding="utf-8",
    )
    (run_dir / "validation_summary.json").write_text(
        json.dumps({"status": "success"}),
        encoding="utf-8",
    )
    (run_dir / "agent_outputs" / "test-01-literature_agent.json").write_text(
        json.dumps(
            {
                "task_id": "test-01-literature_agent",
                "agent_name": "literature_agent",
                "status": "failed",
                "errors": ["malformed output"],
                "next_actions": ["Repair literature schema."],
            }
        ),
        encoding="utf-8",
    )

    (tmp_path / "simulations" / "results").mkdir(parents=True)
    (tmp_path / "simulations" / "recipes").mkdir(parents=True)
    (tmp_path / "simulations" / "results" / "fixture.json").write_text(
        json.dumps(
            {
                "recipe_id": "fixture",
                "physics": {
                    "geometry": "sphere",
                    "n_particles": 3,
                    "n_flux": 6,
                    "shift": 3,
                    "basis_dimension": 5,
                },
                "numerical": {"eigenvalues": [0.0]},
                "metadata": {
                    "status": "success",
                    "solver": "scipy.sparse.linalg.eigsh",
                },
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "simulations" / "recipes" / "recipe.yaml").write_text(
        "recipe_id: next-ed\nphysics:\n  geometry: sphere\n",
        encoding="utf-8",
    )

    class FakeGitHubClient:
        def is_configured(self):
            return True

        def get_open_issues(self, limit=20):
            return [
                SimpleNamespace(
                    number=7,
                    title="Resolve deferred ν=5/2 gap claim",
                    state="open",
                    labels=[SimpleNamespace(name="daily-loop")],
                    html_url="https://example.invalid/7",
                )
            ]

    memory = DurableMemoryCollector(
        workspace_path=tmp_path,
        mode="test",
        github_client=FakeGitHubClient(),
    ).collect()

    signals = memory["planning_signals"]
    assert signals["accepted_claim_count"] == 1
    assert signals["rejected_claim_count"] == 1
    assert signals["deferred_claim_count"] == 1
    assert "test-01-literature_agent" in signals["prior_required_agent_failures"]
    assert signals["validated_simulation_fixtures"][0]["recipe_id"] == "fixture"
    assert signals["open_github_issues"][0]["number"] == 7
    assert "ghp_secretvalue" not in json.dumps(memory)


def test_director_generates_memory_aware_daily_commands():
    memory_context = {
        "planning_signals": {
            "prior_required_agent_failures": ["production-01-literature_agent"],
            "rejected_claim_count": 6,
            "deferred_claim_count": 2,
            "pending_next_actions": ["Return output matching the required schema."],
            "unresolved_assumptions": ["Fixture is not ν=5/2 evidence."],
            "validated_simulation_fixtures": [
                {
                    "path": "simulations/results/result_example_laughlin.json",
                    "recipe_id": "example_laughlin",
                }
            ],
            "simulation_recipes": [
                {
                    "path": "simulations/recipes/example_laughlin_recipe.yaml",
                    "recipe_id": "example_laughlin",
                }
            ],
            "open_github_issues": [{"number": 3, "title": "Follow up"}],
            "knowledge_gaps": ["Subagent execution raised an exception."],
        },
        "source_index": [
            {
                "kind": "claim_ledger",
                "path": "knowledge_base/claim_ledger.md",
                "summary": "Rejected claims exist.",
            },
            {
                "kind": "falsification_log",
                "path": "knowledge_base/falsification_log.md",
                "summary": "Repeated rejected claims.",
            },
            {
                "kind": "simulation_result",
                "path": "simulations/results/result_example_laughlin.json",
                "summary": "Laughlin fixture success.",
            },
            {
                "kind": "github_issues",
                "path": None,
                "summary": "One open issue.",
            },
        ],
    }
    director = Director(run_config=DailyTestRunConfig())

    task_graph = director.generate_daily_plan(
        "Advance durable-memory planning.",
        memory_context,
    )
    director.validate_task_graph(task_graph)

    literature_task = task_graph["tasks"][0]
    numerics_task = next(
        task for task in task_graph["tasks"] if task["agent_name"] == "numerics_agent"
    )
    falsification_task = next(
        task
        for task in task_graph["tasks"]
        if task["agent_name"] == "falsification_agent"
    )

    assert "durable memory sources" in literature_task["daily_loop_command"]
    assert "knowledge_base/claim_ledger.md" in literature_task["daily_loop_command"]
    assert "example_laughlin" in numerics_task["daily_loop_command"]
    assert "production-01-literature_agent" in " ".join(
        falsification_task["memory_triggers"]
    )
    assert literature_task["bounded_deliverables"]


def test_parallel_runner_executes_mock_agents_concurrently(tmp_path):
    runner = ParallelAgentRunner(
        run_id="test-run",
        output_dir=tmp_path / "agent_outputs",
        max_parallel_agents=2,
    )
    tasks = [
        {
            "task_id": f"task-{idx}",
            "agent_name": "mock_agent",
            "agent_role": "Mock Agent",
            "mode": "test",
        }
        for idx in range(2)
    ]

    def executor(task):
        time.sleep(0.2)
        return {
            "agent_name": task["agent_name"],
            "agent_role": task["agent_role"],
            "task_id": task["task_id"],
            "run_id": "test-run",
            "mode": "test",
            "status": "success",
            "summary": "ok",
            "claims": [],
            "artifacts": [],
            "errors": [],
            "next_actions": [],
        }

    started = time.perf_counter()
    outputs, ledger = runner.run(tasks, executor)
    elapsed = time.perf_counter() - started

    assert elapsed < 0.35
    assert len(outputs) == 2
    assert all(item["status"] == "success" for item in ledger)


def test_malformed_subagent_output_is_rejected():
    director = Director(run_config=DailyTestRunConfig())
    output = {
        "agent_name": "bad_agent",
        "agent_role": "Bad Agent",
        "task_id": "bad-1",
        "run_id": "run",
        "mode": "test",
        "status": "success",
        "summary": "bad",
        "claims": [
            {
                "claim_id": "bad-claim",
                "text": "This lacks a valid label.",
                "evidence_type": "proof",
                "support": "none",
                "limitations": "none",
                "confidence": "high",
            }
        ],
        "artifacts": [],
        "errors": [],
        "next_actions": [],
    }

    with pytest.raises(MalformedAgentOutput, match="Invalid evidence_type"):
        director.validate_agent_output(output)


def test_daily_report_and_summary_are_generated_in_test_mode(tmp_path):
    runner = DailyLoopRunner(
        workspace_path=WORKSPACE,
        run_config=DailyTestRunConfig(artifact_root=tmp_path),
    )

    summary = runner.run(objective="Validate deterministic test loop.")

    assert summary["status"] in {"completed", "partial"}
    report_path = Path(summary["artifact_dir"]) / "daily_report.md"
    summary_path = Path(summary["artifact_dir"]) / "run_summary.json"
    assert report_path.exists()
    assert summary_path.exists()
    report = report_path.read_text(encoding="utf-8")
    assert "TEST mode" in report
    assert "Scientific status of today's loop" in report
    assert "Durable memory sources" in report
    assert (Path(summary["artifact_dir"]) / "memory_context.json").exists()
    task_graph = json.loads(
        (Path(summary["artifact_dir"]) / "task_graph.json").read_text(
            encoding="utf-8"
        )
    )
    assert all(task["daily_loop_command"] for task in task_graph["tasks"])


def test_test_mode_disables_github_writes_by_default(tmp_path):
    runner = DailyLoopRunner(
        workspace_path=WORKSPACE,
        run_config=DailyTestRunConfig(artifact_root=tmp_path),
    )

    summary = runner.run(objective="Check GitHub gate.")

    assert summary["github_updates"] == []
    assert "knowledge_base/daily_reports" not in json.dumps(summary["artifacts"])


def test_sample_laughlin_fixture_is_consumed_correctly(tmp_path):
    runner = DailyLoopRunner(
        workspace_path=WORKSPACE,
        run_config=DailyTestRunConfig(artifact_root=tmp_path),
    )

    validation = runner._run_physics_checks()

    assert validation["status"] == "success"
    assert validation["laughlin_fixture_consumed"] is True
    assert validation["solver"] == "scipy.sparse.linalg.eigsh"
    assert validation["lowest_eigenvalue"] == pytest.approx(0.0, abs=1e-10)
