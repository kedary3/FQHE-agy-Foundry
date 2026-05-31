# AGENTS.md

## Project Mission

This repository models a GitHub-backed theoretical and computational physics department investigating microscopic explanations of the fractional quantum Hall effect at filling factor nu = 5/2. The workflow must generate, test, reproduce, compare, falsify, and document hypotheses without assuming that any candidate state is correct.

## Safety Rules

- Do not print, commit, or hardcode secrets.
- Do not commit `.env`; keep local credentials in `.env` only.
- Keep `.env` ignored and `.env.example` placeholder-only.
- If real keys or tokens appear in tracked files, stop and report them before editing.
- Do not overclaim physics results or promote conjectures to evidence.

## Preferred Architecture

- Manage research around hypotheses, contradictions, benchmarks, decisions, and reproducible simulation recipes.
- Keep the pipeline explicit: Research Agent -> Independent Reproduction Agent -> Referee Agent -> Accepted Knowledge Base.
- Treat contradictions between theory, numerics, and experiment as first-class research targets.
- Use Microsoft Foundry as a managed orchestration/provider layer, not as a replacement for local execution or GitHub memory.
- Preserve the Antigravity/local CLI workflow.

## Test Commands

- `pytest`
- `pytest tests/test_orchestrator_engine.py tests/test_ed_validation.py`
- `python -m src.orchestrator.cli --dry-run --run`
- `python -m src.orchestrator.cli --check-provider --provider gemini`

## Numerical Reproducibility

Record geometry, particle number, flux, shift, sector, pseudopotentials, interaction model, Landau-level mixing settings, finite-width model, solver, tolerances, random seeds, runtime environment, and commit hash for numerical results. Prefer deterministic seeds and NumPy/SciPy sparse linear algebra before optional compiled kernels.

## Claim Classification

Classify claims conservatively as conjecture, analytic derivation, numerical evidence, reproduced numerical evidence, experimental observation, contradiction, or accepted benchmark. Negative results and failed reproductions are valid research outputs.

## Physics Claims

Avoid language implying that Moore-Read Pfaffian, anti-Pfaffian, PH-Pfaffian, composite fermion, parton, stripe/nematic, or any other proposed state is established unless the repository contains reproduced evidence supporting that exact claim.
