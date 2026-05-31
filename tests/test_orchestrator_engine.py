from pathlib import Path

from src.orchestrator.engine import ResearchDepartmentEngine


WORKSPACE = Path(__file__).resolve().parents[1]


def _disable_adapters(self):
    self.llm = None
    self.github = None


def test_yaml_loader_accepts_trailing_document_marker(tmp_path):
    config_path = tmp_path / "agent.yaml"
    config_path.write_text(
        "id: A-TEST\nrole: Test Agent\nsystem_prompt_template: >\n  Test prompt.\n---\n",
        encoding="utf-8",
    )

    data = ResearchDepartmentEngine._load_yaml_document(str(config_path))

    assert data["id"] == "A-TEST"
    assert data["role"] == "Test Agent"


def test_engine_loads_agent_and_program_configs(monkeypatch):
    monkeypatch.setattr(ResearchDepartmentEngine, "_init_adapters", _disable_adapters)

    engine = ResearchDepartmentEngine(workspace_path=str(WORKSPACE))

    assert engine.agents["A-PI"]["role"] == "Principal Investigator (PI)"
    assert engine.programs["P-CF"]["name"] == "Composite Fermion Descriptions"
    assert engine._agent_model("A-PI", "pi") == "gemini-2.5-pro"


def test_engine_loads_numerical_division_agent_tree(monkeypatch):
    monkeypatch.setattr(ResearchDepartmentEngine, "_init_adapters", _disable_adapters)

    engine = ResearchDepartmentEngine(workspace_path=str(WORKSPACE))
    numerical_lead = engine.agents["A-PHYS"]

    assert numerical_lead["role"] == "Numerical Division Lead"
    assert numerical_lead["managed_groups"] == [
        "A-ED",
        "A-DMRG",
        "A-MC",
        "A-VAL",
        "A-DATA",
    ]
    assert engine.agents["A-ED"]["reports_to"] == "A-PHYS"
    assert engine.agents["A-DMRG"]["reports_to"] == "A-PHYS"
    assert "Disagreement" in numerical_lead["independence_policy"]


def test_dry_run_delegates_from_program_configs(monkeypatch):
    monkeypatch.setattr(ResearchDepartmentEngine, "_init_adapters", _disable_adapters)
    engine = ResearchDepartmentEngine(workspace_path=str(WORKSPACE))

    result = engine.run_daily_cycle(dry_run=True)

    assert result["status"] == "completed"
    assert len(result["delegations"]) == engine.config["orchestration"]["max_daily_delegations"]
    assert result["delegations"][0]["program_id"] == "P-CF"
    assert result["delegations"][0]["suggested_agent"] == "A-THEO"
    assert "Composite Fermion Descriptions" in result["delegations"][0]["mission"]
