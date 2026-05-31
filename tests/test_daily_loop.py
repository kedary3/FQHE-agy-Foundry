import json
import time
from pathlib import Path

import pytest

from src.orchestrator.daily_loop import DailyLoopRunner
from src.orchestrator.director import Director, MalformedAgentOutput
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


def test_director_produces_valid_task_graph():
    director = Director(run_config=DailyTestRunConfig())

    task_graph = director.generate_daily_plan("Validate the daily loop.")
    director.validate_task_graph(task_graph)

    assert task_graph["mode"] == "test"
    assert task_graph["tasks"]
    assert task_graph["tasks"][0]["agent_name"] == "literature_agent"


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
    assert "TEST mode" in report_path.read_text(encoding="utf-8")
    assert "Scientific status of today's loop" in report_path.read_text(
        encoding="utf-8"
    )


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
