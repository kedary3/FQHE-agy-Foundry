"""Tests for the Tier 1-4 workflow improvements.

Covers:
- Claim field alias normalization (Tier 1)
- claim_id auto-generation (Tier 1)
- "proposed" status remapping (Tier 1)
- Confidence alias normalization (Tier 1)
- Evidence-type alias normalization (Tier 1)
- Partial output salvage as deferred claims (Tier 2)
- Infrastructure vs schema failure categorization (Tier 4)
- Agent stubs pass Director validation after normalization (Tier 4)
- 3-phase parallel group structure (Tier 2)
- AGENT_OUTPUT_SCHEMA is exported and machine-readable (Tier 4)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.orchestrator.director import (
    AGENT_OUTPUT_SCHEMA,
    Director,
    MalformedAgentOutput,
    _CLAIM_FIELD_ALIASES,
    _EVIDENCE_TYPE_ALIASES,
    _INFRA_FAILURE_KEYWORDS,
)
from src.orchestrator.run_modes import TestRunConfig as WorkflowTestRunConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WORKSPACE = Path(__file__).resolve().parents[1]


def _make_valid_claim(**overrides) -> dict:
    """Produce a minimal canonical-schema claim."""
    base = {
        "claim_id": "test-claim-001",
        "text": "A test claim.",
        "evidence_type": "numerical evidence",
        "support": "Based on fixture data.",
        "limitations": "Finite-size only.",
        "confidence": "medium",
    }
    base.update(overrides)
    return base


def _make_valid_output(task_id: str = "test-01-agent", **overrides) -> dict:
    """Produce a minimal valid agent output."""
    base = {
        "agent_name": "test_agent",
        "agent_role": "Test Agent",
        "task_id": task_id,
        "run_id": "run-test-001",
        "mode": "test",
        "status": "success",
        "summary": "A test output.",
        "claims": [_make_valid_claim(claim_id=f"{task_id}-claim-000")],
        "artifacts": [],
        "errors": [],
        "next_actions": [],
    }
    base.update(overrides)
    return base


director = Director(run_config=WorkflowTestRunConfig())


# ---------------------------------------------------------------------------
# Tier 1: Claim field alias normalization
# ---------------------------------------------------------------------------

class TestClaimFieldAliasNormalization:
    """Verify _normalize_claim maps all known aliases to canonical fields."""

    def test_claim_alias_maps_to_text(self):
        raw = {"claim": "Pfaffian is a candidate.", "evidence_type": "conjecture",
               "support": "x", "limitations": "y", "confidence": "low"}
        result = director._normalize_claim(raw, task_id="t-01", idx=0)
        assert result["text"] == "Pfaffian is a candidate."
        assert "claim" not in result

    def test_challenged_claim_alias_maps_to_text(self):
        raw = {"challenged_claim": "Overclaim detected.", "evidence_type": "numerical evidence",
               "support": "x", "limitations": "y", "confidence": "medium"}
        result = director._normalize_claim(raw, task_id="t-02", idx=0)
        assert result["text"] == "Overclaim detected."
        assert "challenged_claim" not in result

    def test_derivation_summary_alias_maps_to_text(self):
        raw = {"derivation_summary": "PH symmetry holds.", "evidence_type": "exact result",
               "support": "x", "limitations": "y", "confidence": "high"}
        result = director._normalize_claim(raw, task_id="t-03", idx=0)
        assert result["text"] == "PH symmetry holds."

    def test_evidence_classification_alias(self):
        raw = {"text": "x", "evidence_classification": "numerical evidence",
               "support": "s", "limitations": "l", "confidence": "medium"}
        result = director._normalize_claim(raw, task_id="t-04", idx=0)
        assert result["evidence_type"] == "numerical evidence"
        assert "evidence_classification" not in result

    def test_epistemic_status_alias(self):
        raw = {"text": "x", "epistemic_status": "exact_result",
               "support": "s", "limitations": "l", "confidence": "high"}
        result = director._normalize_claim(raw, task_id="t-05", idx=0)
        assert result["evidence_type"] == "exact result"
        assert "epistemic_status" not in result

    def test_all_registered_aliases_are_covered(self):
        """Every alias in _CLAIM_FIELD_ALIASES must survive normalize_claim."""
        for alias in _CLAIM_FIELD_ALIASES:
            raw = {
                alias: "value",
                "support": "s",
                "limitations": "l",
                "confidence": "medium",
                # Avoid 'text' so the alias->text mapping is the only source.
            }
            result = director._normalize_claim(raw, task_id="ta", idx=0)
            assert alias not in result, f"Alias '{alias}' should have been removed."


class TestClaimIdAutoGeneration:
    """claim_id must be auto-generated when missing or blank."""

    def test_missing_claim_id_is_auto_generated(self):
        raw = _make_valid_claim()
        del raw["claim_id"]
        result = director._normalize_claim(raw, task_id="task-lit-001", idx=2)
        assert result["claim_id"] == "task-lit-001-claim-002"

    def test_blank_claim_id_is_auto_generated(self):
        raw = _make_valid_claim(claim_id="")
        result = director._normalize_claim(raw, task_id="task-theory-001", idx=0)
        assert result["claim_id"] == "task-theory-001-claim-000"

    def test_existing_claim_id_is_preserved(self):
        raw = _make_valid_claim(claim_id="explicit-id-99")
        result = director._normalize_claim(raw, task_id="task-x", idx=0)
        assert result["claim_id"] == "explicit-id-99"


class TestEvidenceTypeAliases:
    """Underscore-separated evidence type shorthand must normalize to space-separated."""

    @pytest.mark.parametrize("alias,canonical", list(_EVIDENCE_TYPE_ALIASES.items()))
    def test_evidence_type_alias(self, alias: str, canonical: str):
        raw = _make_valid_claim(evidence_type=alias)
        result = director._normalize_claim(raw, task_id="t", idx=0)
        assert result["evidence_type"] == canonical

    def test_canonical_evidence_type_is_preserved(self):
        raw = _make_valid_claim(evidence_type="exact result")
        result = director._normalize_claim(raw, task_id="t", idx=0)
        assert result["evidence_type"] == "exact result"


class TestConfidenceNormalization:
    """Confidence aliases should normalize to low/medium/high."""

    def test_moderate_normalizes_to_medium(self):
        raw = _make_valid_claim(confidence="Moderate")
        result = director._normalize_claim(raw, task_id="t", idx=0)
        assert result["confidence"] == "medium"

    def test_moderate_with_suffix(self):
        raw = _make_valid_claim(confidence="Moderate—insufficient justification")
        result = director._normalize_claim(raw, task_id="t", idx=0)
        assert result["confidence"] == "medium"

    def test_low_preserved(self):
        raw = _make_valid_claim(confidence="low")
        result = director._normalize_claim(raw, task_id="t", idx=0)
        assert result["confidence"] == "low"

    def test_high_with_upper_case(self):
        raw = _make_valid_claim(confidence="High")
        result = director._normalize_claim(raw, task_id="t", idx=0)
        assert result["confidence"] == "high"


# ---------------------------------------------------------------------------
# Tier 1: "proposed" status remapping
# ---------------------------------------------------------------------------

class TestProposedStatusRemapping:
    """Knowledge Curator's 'proposed' status must be remapped to 'partial'."""

    def test_proposed_becomes_partial(self):
        output = _make_valid_output(status="proposed")
        normalized = director.normalize_agent_output(output)
        assert normalized["status"] == "partial"

    def test_success_status_unchanged(self):
        output = _make_valid_output(status="success")
        normalized = director.normalize_agent_output(output)
        assert normalized["status"] == "success"

    def test_failed_status_unchanged(self):
        output = _make_valid_output(status="failed")
        normalized = director.normalize_agent_output(output)
        assert normalized["status"] == "failed"


# ---------------------------------------------------------------------------
# Tier 1: Full pipeline — normalize then validate
# ---------------------------------------------------------------------------

class TestNormalizeThenValidate:
    """After normalization the Director must accept previously-rejected outputs."""

    def test_literature_agent_output_with_aliases_passes(self):
        """Simulate the exact output that was rejected in production run."""
        output = {
            "agent_name": "literature_agent",
            "agent_role": "Literature Agent",
            "task_id": "production-01-literature_agent",
            "run_id": "test-run-001",
            "mode": "production",
            "status": "partial",
            "summary": "Advanced daily ν=5/2 FQHE literature review.",
            "claims": [
                {
                    # Uses the 'claim' alias — was rejected before
                    "claim": "The Pfaffian and anti-Pfaffian ground states are numerically competitive.",
                    "evidence_type": "numerical evidence",
                    "support": "Exact diagonalization studies on systems up to 32 electrons.",
                    "limitations": "Finite-size limitations; lack of controlled extrapolation.",
                    "confidence": "moderate",  # alias for medium
                }
            ],
            "artifacts": [],
            "errors": [],
            "next_actions": ["Follow-up reading: review LL mixing."],
        }
        normalized = director.normalize_agent_output(output)
        # Should not raise
        director.validate_agent_output(normalized)
        assert normalized["claims"][0]["text"] == "The Pfaffian and anti-Pfaffian ground states are numerically competitive."
        assert normalized["claims"][0]["confidence"] == "medium"
        assert "claim_id" in normalized["claims"][0]

    def test_knowledge_curator_proposed_output_passes(self):
        """Knowledge Curator's 'proposed' status with claim_id must pass after normalization."""
        output = {
            "agent_name": "knowledge_curator_agent",
            "agent_role": "Knowledge Curator Agent",
            "task_id": "production-05-knowledge_curator_agent",
            "run_id": "test-run-001",
            "mode": "production",
            "status": "proposed",  # remapped to partial
            "summary": "Prepared non-destructive durable-memory update plan.",
            "claims": [
                {
                    "claim_id": "c_001",
                    "claim_text": "The Pfaffian state is a ground state candidate.",  # alias
                    "evidence_type": "controlled approximation",
                    "support": "Numerical studies with finite-size systems.",
                    "limitations": "Finite-size gaps are not thermodynamic proof.",
                    "confidence": "medium",
                }
            ],
            "artifacts": [],
            "errors": [],
            "next_actions": ["Review theory_branch_ledger.md."],
        }
        normalized = director.normalize_agent_output(output)
        director.validate_agent_output(normalized)
        assert normalized["status"] == "partial"

    def test_theory_agent_output_with_derivation_summary_passes(self):
        output = {
            "agent_name": "theory_agent",
            "agent_role": "Theory Agent",
            "task_id": "production-02-theory_agent",
            "run_id": "test-run-001",
            "mode": "production",
            "status": "partial",
            "summary": "Three analytical checks proposed.",
            "claims": [
                {
                    # derivation_summary alias
                    "derivation_summary": "PH symmetry holds in pure SLL with Coulomb interaction.",
                    "evidence_classification": "exact result",  # alias for evidence_type
                    "support": "Hamiltonian commutes with PH operator.",
                    "limitations": "Finite thickness and disorder neglected.",
                    "confidence": "high",
                }
            ],
            "artifacts": [],
            "errors": [],
            "next_actions": ["Run finite-size scaling."],
        }
        normalized = director.normalize_agent_output(output)
        director.validate_agent_output(normalized)
        claim = normalized["claims"][0]
        assert claim["text"] == "PH symmetry holds in pure SLL with Coulomb interaction."
        assert claim["evidence_type"] == "exact result"


# ---------------------------------------------------------------------------
# Tier 2: Partial output salvage
# ---------------------------------------------------------------------------

class TestPartialOutputSalvage:
    """Partial agent outputs must contribute deferred claims, not be discarded."""

    def test_partial_output_claims_become_deferred(self):
        output = _make_valid_output(status="partial")
        result = director.classify_claims([output])
        assert len(result["deferred"]) == 1
        assert len(result["accepted"]) == 0
        assert len(result["rejected"]) == 0

    def test_failed_output_contributes_rejected_entry(self):
        output = _make_valid_output(status="failed", errors=["Schema error"], claims=[])
        result = director.classify_claims([output])
        assert len(result["rejected"]) == 1
        assert result["rejected"][0]["claim_id"].endswith("-failed-output")

    def test_success_output_with_conjecture_is_deferred(self):
        output = _make_valid_output(
            status="success",
            claims=[_make_valid_claim(evidence_type="conjecture", claim_id="c1")],
        )
        result = director.classify_claims([output])
        assert len(result["deferred"]) == 1

    def test_partial_claim_has_salvage_flag(self):
        output = _make_valid_output(status="partial")
        result = director.classify_claims([output])
        assert result["deferred"][0].get("_salvaged_from_partial") is True


# ---------------------------------------------------------------------------
# Tier 4: Infrastructure vs schema failure categorization
# ---------------------------------------------------------------------------

class TestInfrastructureVsSchemaFailure:
    """Infrastructure errors must be labeled differently from schema failures."""

    @pytest.mark.parametrize("keyword", list(_INFRA_FAILURE_KEYWORDS))
    def test_infra_keyword_detected(self, keyword: str):
        output = _make_valid_output(
            status="failed",
            errors=[f"Subagent raised {keyword}: connection lost"],
            claims=[],
        )
        result = director.classify_claims([output])
        assert result["rejected"][0]["failure_category"] == "infrastructure-failure"

    def test_schema_failure_categorized_correctly(self):
        output = _make_valid_output(
            status="failed",
            errors=["Claim missing required field: claim_id"],
            claims=[],
        )
        result = director.classify_claims([output])
        assert result["rejected"][0]["failure_category"] == "schema-failure"


# ---------------------------------------------------------------------------
# Tier 4: AGENT_OUTPUT_SCHEMA is machine-readable and exportable
# ---------------------------------------------------------------------------

class TestAgentOutputSchema:
    """AGENT_OUTPUT_SCHEMA must be a machine-readable dict usable in prompts."""

    def test_schema_has_required_keys(self):
        assert "required_top_level_fields" in AGENT_OUTPUT_SCHEMA
        assert "claim_required_fields" in AGENT_OUTPUT_SCHEMA
        assert "valid_evidence_types" in AGENT_OUTPUT_SCHEMA
        assert "valid_confidence_values" in AGENT_OUTPUT_SCHEMA

    def test_schema_is_json_serializable(self):
        serialized = json.dumps(AGENT_OUTPUT_SCHEMA)
        parsed = json.loads(serialized)
        assert parsed["valid_confidence_values"] == ["low", "medium", "high"]

    def test_schema_claim_fields_match_validator(self):
        """Schema claim fields must match what _validate_claim actually checks."""
        expected_fields = {"claim_id", "text", "evidence_type", "support", "limitations", "confidence"}
        schema_fields = set(AGENT_OUTPUT_SCHEMA["claim_required_fields"])
        assert schema_fields == expected_fields

    def test_schema_evidence_types_match_evidence_types_constant(self):
        from src.orchestrator.director import EVIDENCE_TYPES
        assert set(AGENT_OUTPUT_SCHEMA["valid_evidence_types"]) == EVIDENCE_TYPES


# ---------------------------------------------------------------------------
# Tier 2: 3-phase parallel group structure
# ---------------------------------------------------------------------------

class TestThreePhaseParallelGroups:
    """Daily plan must produce 3 execution phases mirroring a physics department."""

    def test_plan_has_three_phases(self):
        d = Director(run_config=WorkflowTestRunConfig())
        plan = d.generate_daily_plan("Test FQHE daily loop.")
        group_ids = [g["group_id"] for g in plan["parallel_groups"]]
        assert "phase-1-evidence-gathering" in group_ids
        assert "phase-2-challenge-and-bridge" in group_ids
        assert "phase-3-knowledge-curation" in group_ids

    def test_phase1_contains_literature_and_theory(self):
        d = Director(run_config=WorkflowTestRunConfig())
        plan = d.generate_daily_plan("Test FQHE daily loop.")
        phase1 = next(g for g in plan["parallel_groups"] if g["group_id"] == "phase-1-evidence-gathering")
        ids = " ".join(phase1["task_ids"])
        assert "literature_agent" in ids
        assert "theory_agent" in ids

    def test_phase2_contains_falsification_and_experiment_bridge(self):
        d = Director(run_config=WorkflowTestRunConfig())
        plan = d.generate_daily_plan("Test FQHE daily loop.")
        phase2 = next(g for g in plan["parallel_groups"] if g["group_id"] == "phase-2-challenge-and-bridge")
        ids = " ".join(phase2["task_ids"])
        assert "falsification_agent" in ids
        assert "experiment_bridge_agent" in ids

    def test_phase3_contains_knowledge_curator(self):
        d = Director(run_config=WorkflowTestRunConfig())
        plan = d.generate_daily_plan("Test FQHE daily loop.")
        phase3 = next(g for g in plan["parallel_groups"] if g["group_id"] == "phase-3-knowledge-curation")
        ids = " ".join(phase3["task_ids"])
        assert "knowledge_curator_agent" in ids

    def test_phase3_depends_on_phases_1_and_2(self):
        d = Director(run_config=WorkflowTestRunConfig())
        plan = d.generate_daily_plan("Test FQHE daily loop.")
        phase3 = next(g for g in plan["parallel_groups"] if g["group_id"] == "phase-3-knowledge-curation")
        phase1 = next(g for g in plan["parallel_groups"] if g["group_id"] == "phase-1-evidence-gathering")
        phase2 = next(g for g in plan["parallel_groups"] if g["group_id"] == "phase-2-challenge-and-bridge")
        depends = set(phase3.get("depends_on", []))
        assert depends >= set(phase1["task_ids"]) | set(phase2["task_ids"])


# ---------------------------------------------------------------------------
# Tier 3: Rotating focus topics in skill instructions
# ---------------------------------------------------------------------------

class TestRotatingFocusTopics:
    """Skill instructions must include rotating focus topics to prevent stale loops."""

    def test_skill_instructions_contain_focus_rotation(self):
        d = Director(run_config=WorkflowTestRunConfig())
        instructions = d._skill_instructions(
            agent_key="literature_agent",
            role="Literature Agent",
            allowed_inputs=("config",),
            expected_outputs=("claims",),
            loop_index=0,
        )
        combined = " ".join(instructions)
        assert "focus rotation" in combined.lower() or "Today's focus rotation" in combined

    def test_focus_rotates_with_loop_index(self):
        d = Director(run_config=WorkflowTestRunConfig())
        instr0 = " ".join(d._skill_instructions(
            agent_key="theory_agent", role="Theory Agent",
            allowed_inputs=(), expected_outputs=(), loop_index=0,
        ))
        instr1 = " ".join(d._skill_instructions(
            agent_key="theory_agent", role="Theory Agent",
            allowed_inputs=(), expected_outputs=(), loop_index=1,
        ))
        assert instr0 != instr1  # Different focus topic

    def test_schema_block_included_in_skill_instructions(self):
        d = Director(run_config=WorkflowTestRunConfig())
        instructions = d._skill_instructions(
            agent_key="falsification_agent",
            role="Falsification Agent",
            allowed_inputs=("config",),
            expected_outputs=("claims",),
        )
        combined = " ".join(instructions)
        assert "claim_id" in combined
        assert "evidence_type" in combined
        assert "REQUIRED OUTPUT SCHEMA" in combined
