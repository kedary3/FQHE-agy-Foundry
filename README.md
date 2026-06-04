# Magentic Physics Research Department for nu = 5/2 FQHE

This repository implements a manager-led multi-agent workflow for deriving,
testing, comparing, and falsifying microscopic explanations of the nu = 5/2
fractional quantum Hall state.

The project models a physics research department. A PI / Magentic Manager owns
the shared context, facts, plan, progress ledger, delegation policy, stall
detection, replanning, and final synthesis. Specialist agents receive bounded
research subtasks and return evidence-bearing artifacts; they do not control the
global workflow.

## What Makes This Magentic

This is not a fixed sequential pipeline, a simple concurrent worker pool, or a
group chat among peers. The Magentic pattern used here is:

1. The PI / Magentic Manager gathers facts into shared context.
2. The manager creates an initial research plan.
3. The manager dynamically delegates bounded tasks to specialist agents.
4. Specialist agents return structured reports with evidence and assumptions.
5. The manager updates a progress ledger after each report.
6. The manager detects stalls and requests replanning when progress stops.
7. The manager synthesizes the final research report from the validated record.

The manager is the only component that owns the global plan and progress ledger.

## Scientific Scope

The workflow must not assume that the Moore-Read Pfaffian, anti-Pfaffian,
PH-Pfaffian, composite Fermi liquid, stripe or nematic state, or any other
candidate is correct. Candidate descriptions are hypotheses to derive, test,
compare, and falsify.

Core physics targets include:

- incompressibility
- excitation gap
- quasiparticle charge
- quasiparticle statistics
- particle-hole symmetry
- finite-width corrections
- Landau-level mixing
- disorder
- spin polarization
- experimentally relevant energy scales

Every scientific claim must be tagged as one of: exact result, controlled
approximation, numerical evidence, variational assumption, phenomenological
argument, conjecture, or unresolved.

## Repository Architecture

Intended directories:

- `config/agents/`: role definitions, prompts, permissions, and evidence rules.
- `config/workflows/`: Magentic workflow configuration.
- `src/orchestrator/`: PI manager, ledgers, run modes, adapters, CLI, and reports.
- `src/agents/`: base agent interfaces and deterministic or live agent adapters.
- `src/physics/`: inspectable NumPy/SciPy/SymPy physics and ED utilities.
- `src/knowledge/`: Markdown parsing, graph construction, and research memory.
- `simulations/`: declarative recipes, raw outputs, and simulation metadata.
- `knowledge_base/`: persistent notes, claim ledgers, falsification logs, reports.
- `reports/`: generated Magentic loop Markdown reports.
- `tests/`: orchestration, schema, fixture, and regression tests.

## Test Mode

Test mode runs locally with deterministic or mock agents. It does not require
Azure, OpenAI, Anthropic, Gemini, or GitHub credentials. It does not create
GitHub branches, issues, or pull requests.

Test mode validates:

- Magentic orchestration state transitions
- progress ledger serialization
- report schema and required sections
- safe status output that does not print secrets
- the N = 3, N_flux = 6 Laughlin validation fixture on the sphere

Run the deterministic Magentic loop:

```bash
python3 -m src.orchestrator.cli --mode test --objective "Validate the N=3 Laughlin fixture and propose next nu=5/2 tests"
```

Run the full test suite:

```bash
python3 -m pytest
```

## Production Mode

Production mode is reserved for live LLM deployments and GitHub integration. It
is expected to create or update branches, issues, pull requests, reports,
simulation artifacts, and knowledge-base files only when explicit configuration
gates permit those writes.

Production mode must require explicit environment variables for live services
and must never infer production execution from the mere presence of secrets.
Missing configuration should fail with variable names only, never values.

Planned live wiring:

```bash
python3 -m src.orchestrator.cli --mode production --objective "Run the daily nu=5/2 research loop"
```

## Safety And Reproducibility

- Never print API keys, bearer tokens, connection strings, or environment values.
- All live integrations must support dry-run or mock mode for tests.
- Every production artifact must include provenance: run ID, mode, objective,
  agent, task ID, evidence labels, assumptions, files changed, and tests run.
- Numerical evidence must report geometry, particle number, flux, shift, solver,
  basis size, convergence status, and limitations.
- Finite-size numerical trends must never be presented as thermodynamic proof.
