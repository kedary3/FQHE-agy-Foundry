from src.orchestrator.magentic_manager import PIManager


def test_manager_creates_nonempty_plan():
    manager = PIManager()

    plan = manager.create_plan("Validate nu=5/2 workflow.")

    assert plan
    assert {step.suggested_agent for step in plan} >= {"literature", "numerical_ed", "critic"}
    assert all("Daily command from durable memory" in step.goal for step in plan)
    assert all(step.notes for step in plan)


def test_manager_selects_agents_dynamically_from_state():
    manager = PIManager(max_parallel_agents=2)
    state = manager.run_test_loop("Prime a deterministic loop.")

    completed_agents = {
        step.assigned_agent
        for step in state.task_ledger.plan_steps
        if step.status == "completed"
    }

    assert "literature" in completed_agents
    assert "numerical_ed" in completed_agents
    assert state.progress_ledger.reports


def test_manager_can_run_test_loop_to_completion():
    manager = PIManager()

    state = manager.run_test_loop(
        "Validate the N=3 Laughlin fixture and propose next nu=5/2 tests"
    )

    assert state.status == "completed"
    assert state.task_ledger.is_complete()
    assert state.final_report


def test_final_report_contains_required_scientific_sections():
    manager = PIManager()

    state = manager.run_test_loop("Validate report sections.")
    report = state.final_report

    assert "# Objective" in report
    assert "# Evidence" in report
    assert "# Unresolved Gaps" in report
    assert "# Recommended Next Tasks" in report
    assert "`numerical_evidence`" in report
    assert "exact_result" in report
    assert "controlled_approximation" in report
    assert "variational_assumption" in report
    assert "phenomenological_argument" in report
    assert "conjecture" in report
    assert "unresolved" in report
