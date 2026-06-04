from src.orchestrator.ledger import AgentReport, PlanStep, WorkflowState


def test_ledger_initializes_from_objective():
    state = WorkflowState.from_objective("Validate Magentic ledger.", mode="test")

    assert state.objective == "Validate Magentic ledger."
    assert state.task_ledger.objective == state.objective
    assert state.task_ledger.run_id


def test_facts_plan_steps_and_reports_can_be_added():
    state = WorkflowState.from_objective("Check state transitions.")
    state.add_fact("The manager owns the progress ledger.")
    step = PlanStep(
        task_id="task-1",
        goal="Return a bounded specialist report.",
        suggested_agent="literature",
    )
    state.add_plan_steps([step])
    state.task_ledger.assign_step_to_agent("task-1", "literature")

    report = AgentReport(
        task_id="task-1",
        agent_name="literature",
        assigned_goal=step.goal,
        summary="done",
        epistemic_status=["unresolved"],
    )
    state.ingest_agent_report(report)

    assert state.progress_ledger.facts == ["The manager owns the progress ledger."]
    assert state.task_ledger.get_step("task-1").status == "completed"
    assert state.progress_ledger.reports[0].agent_name == "literature"


def test_stalled_progress_is_detected():
    state = WorkflowState.from_objective("Detect stalls.")

    stalled = state.progress_ledger.detect_stall(state.task_ledger, max_stall_count=1)

    assert stalled is True
    assert state.progress_ledger.replan_requested is True


def test_ledger_serializes_and_deserializes():
    state = WorkflowState.from_objective("Round-trip state.")
    state.add_fact("Serializable fact.")
    state.add_plan_steps(
        [
            PlanStep(
                task_id="task-1",
                goal="Serialize this step.",
                suggested_agent="critic",
            )
        ]
    )

    restored = WorkflowState.from_json(state.to_json())

    assert restored.objective == state.objective
    assert restored.progress_ledger.facts == ["Serializable fact."]
    assert restored.task_ledger.plan_steps[0].task_id == "task-1"
