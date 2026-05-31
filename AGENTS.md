# AGENTS.md

## Project Mission

This repository implements a GitHub-based multi-agent theoretical and computational physics research workflow focused on the fractional quantum Hall effect at filling factor ν = 5/2.

The scientific objective is to derive, test, compare, and falsify microscopic descriptions of the half-filled second Landau level. The system must not assume that the Moore-Read Pfaffian, anti-Pfaffian, PH-Pfaffian, composite Fermi liquid, stripe/nematic state, or any other candidate is correct. Candidate descriptions must be treated as hypotheses whose assumptions, approximations, numerical evidence, and experimental consistency are explicitly tracked.

The repository architecture simulates a research department:

- A Director / Principal Investigator agent coordinates the daily research loop.
- Specialized subagents perform literature review, analytical theory, numerical simulation, falsification, experimental comparison, and knowledge curation.
- GitHub acts as persistent scientific memory through issues, branches, pull requests, reports, artifacts, and structured Markdown knowledge files.
- Azure Foundry resources provide production model execution when production mode is enabled.
- Local deterministic fixtures provide safe validation in test mode.

The system must support both test runs and production runs. These modes must remain strictly separated.

---

## Core Scientific Problem

The project studies the microscopic origin of the observed ν = 5/2 fractional quantum Hall plateau.

Every research loop should advance one or more of the following questions:

1. What microscopic Hamiltonian best describes the half-filled second Landau level under experimentally relevant conditions?
2. Which candidate ground states are energetically competitive after finite width, Landau-level mixing, disorder, and spin effects are included?
3. Which candidate descriptions produce incompressibility?
4. Which mechanisms produce the observed excitation gap?
5. Which models predict the correct quasiparticle charge?
6. Which models predict Abelian or non-Abelian quasiparticle statistics?
7. How is particle-hole symmetry preserved or broken?
8. Which predictions survive finite-size scaling?
9. Which assumptions are variational, phenomenological, numerical, or exact?
10. Which claims can be falsified by exact diagonalization, DMRG, perturbation theory, effective field theory, or experiment?

The project must distinguish between:

- exact results
- controlled approximations
- numerical evidence
- variational assumptions
- phenomenological arguments
- conjectures

No final report may present a conjecture, numerical trend, or variational result as an exact result.

---

## Repository Structure

Respect the existing repository layout.

Expected structure:

```text
config/agents/
  YAML definitions of agent roles, prompts, permissions, evidence standards, and output schemas.

src/orchestrator/
  Director logic, daily-loop orchestration, parallel execution, mode configuration, Foundry/GitHub adapters, and reporting.

src/agents/
  Agent classes, factories, validators, and role-specific behavior.

src/physics/
  Inspectable NumPy/SciPy/SymPy physics code, exact diagonalization utilities, Hamiltonian construction, pseudopotential handling, geometry utilities, and validation routines.

src/knowledge/
  Markdown parsing, knowledge-graph construction, citation tracking, and structured research-memory utilities.

simulations/
  Declarative simulation recipes, raw numerical outputs, and simulation metadata.

knowledge_base/
  Structured scientific notes, paper reviews, candidate-state summaries, derivations, falsification logs, and daily reports.

tests/
  Unit, integration, validation, and regression tests.

docs/
  User-facing and developer-facing documentation for orchestration, Foundry integration, daily-loop execution, testing, and production deployment.
```

Do not perform broad structural rewrites unless a task explicitly requires it. Prefer small, reviewable changes that preserve existing public APIs.

---

## Execution Environment Rules

Use `python3`, not `python`.

Use module execution where possible:

```bash
python3 -m pytest
python3 -m src.orchestrator.cli --run --mode test
python3 -m src.orchestrator.cli --run --mode production
```

If the CLI differs from these commands, inspect the repository and report the correct commands in the final summary.

Do not assume a custom shell `PATH`.

Do not assume secrets are available in local development.

Do not print:

- API keys
- GitHub tokens
- Azure Foundry keys
- model deployment secrets
- `.env` contents
- bearer tokens
- connection strings
- personal access tokens

Environment validation may print variable names, but never values.

Acceptable:

```text
Missing required environment variable: AZURE_FOUNDRY_ENDPOINT
```

Not acceptable:

```text
AZURE_FOUNDRY_ENDPOINT=https://...
GITHUB_TOKEN=ghp_...
```

---

## Required Run Modes

The repository must support two explicit execution modes:

1. Test mode
2. Production mode

Mode selection must be explicit. Do not infer production mode from the presence of secrets alone.

### Test Mode

Test mode is for local development, CI, and safe orchestration validation.

Test mode means: run the full loop machinery, but treat every scientific result
as provisional and noncanonical. It may use Foundry, real models, real agents,
and real repository context when explicitly configured, but its purpose is to
check behavior, artifact validity, Director claim review, and promotion safety.

Test mode must be:

- deterministic
- fast
- low-cost
- safe for CI
- safe without real production secrets
- safe without GitHub mutation
- safe without production Foundry mutation
- based on fixtures, mock clients, or stubbed adapters where appropriate

Test mode should validate:

- configuration loading
- environment validation
- Director task-graph generation
- subagent routing
- parallel execution
- malformed output rejection
- report generation
- artifact writing to a test-safe location
- physics sanity checks using small fixtures
- Foundry adapter health-check behavior with mock or dummy clients
- GitHub adapter behavior with dry-run or mock clients

Test mode must not:

- create production GitHub issues
- create production pull requests
- commit to production branches
- overwrite production knowledge files
- call expensive production models unless explicitly configured
- use unbounded token budgets
- hide exceptions

### Production Mode

Production mode is for the full daily research loop.

Production mode means: run the canonical daily research loop whose outputs are
allowed to update project memory. It writes to durable reports, claim ledgers,
falsification logs, and GitHub artifacts when the explicit gates permit it.
Production mode is authoritative; it is not defined by using a bigger model or
spending more tokens than test mode.

Production mode may:

- call configured Azure Foundry resources
- dispatch multiple subagents in parallel
- mutate GitHub according to explicit configuration gates
- write daily reports to persistent artifact locations
- create or update GitHub issues
- create branches or pull requests if enabled
- update structured knowledge files if enabled
- run larger simulations if enabled

Production mode must:

- require all configured production environment variables
- fail clearly if required configuration is missing
- log structured run metadata
- enforce token and timeout budgets
- preserve all subagent outputs
- validate all scientific claims
- mark incomplete or malformed outputs as failed
- never silently drop exceptions
- never silently skip required agents
- never report success if any required stage failed

Production mode must produce:

- Markdown daily report
- JSON run summary
- task ledger
- agent output artifacts
- validation summary
- falsification log update
- next-loop recommendations

---

## Daily Loop Contract

The daily loop should follow this sequence unless the task explicitly changes it:

1. Load configuration.
2. Resolve run mode.
3. Validate environment.
4. Initialize adapters:
   - Foundry adapter
   - GitHub adapter
   - filesystem artifact writer
   - knowledge-base interface
5. Initialize Director / PI agent.
6. Load current project memory:
   - open research questions
   - prior daily reports
   - unresolved assumptions
   - active candidate states
   - pending simulations
   - known falsification targets
7. Generate daily research plan.
8. Convert research plan into structured subagent tasks.
9. Validate the task graph.
10. Dispatch independent subagent tasks in parallel.
11. Collect subagent outputs.
12. Validate each output against schema and evidence standards.
13. Run required physics/test checks.
14. Ask Director to synthesize results.
15. Classify claims:
   - accepted
   - rejected
   - deferred
16. Update artifacts.
17. Optionally update GitHub.
18. Emit final run summary JSON.
19. Exit with a meaningful status code.

A daily run must not be considered successful unless the final summary exists and required validation stages completed.

---

## Director / PI Agent Requirements

The Director is responsible for scientific coordination and quality control.

The Director must:

- define the daily objective
- decompose the objective into subagent tasks
- assign tasks to appropriate agents
- decide which tasks may run in parallel
- identify dependencies between tasks
- enforce evidence labeling
- reject unsupported claims
- request revision or mark failure when outputs are malformed
- synthesize a final daily report
- identify next-loop tasks

The Director must not:

- claim consensus without evidence
- treat a variational result as exact
- treat finite-size numerical evidence as thermodynamic proof
- ignore unresolved assumptions
- collapse distinct candidate states into one category
- hide failed subagent outputs
- overwrite dissenting falsification findings
- suppress negative results

The Director's final report must include a section titled:

```text
Scientific status of today's loop
```

That section must contain:

- accepted claims
- rejected claims
- deferred claims
- unresolved assumptions
- proposed next tests

---

## Required Subagents

The following subagents should exist as YAML definitions, class configurations, or equivalent repo-native agent specs.

### 1. Director / PI Agent

Suggested file:

```text
config/agents/director_pi.yaml
```

Responsibilities:

- generate daily plan
- construct task graph
- assign subagent tasks
- enforce scientific standards
- synthesize daily report
- decide whether outputs are accepted, rejected, or deferred

Expected outputs:

- task graph
- agent assignment table
- final synthesis
- claim classification
- next-loop recommendations

Escalation criteria:

- subagent output missing required fields
- scientific claim lacks evidence classification
- contradiction between agents
- production resource failure
- simulation failure
- GitHub write failure
- missing artifact

### 2. Literature Agent

Suggested file:

```text
config/agents/literature_agent.yaml
```

Responsibilities:

- review papers
- summarize claims
- extract assumptions
- identify candidate-state predictions
- track citations
- separate author claims from verified results
- identify unresolved disputes in the literature

Expected outputs:

- paper summary
- claim table
- evidence classification
- relevance to ν = 5/2
- open questions
- citations or source identifiers
- proposed follow-up readings

The Literature Agent must not:

- present a paper's claim as established fact without validation
- omit approximations used in a cited work
- ignore finite-size or model-dependence limitations
- fabricate citations

### 3. Theory Agent

Suggested file:

```text
config/agents/theory_agent.yaml
```

Responsibilities:

- derive analytical results
- inspect Hamiltonians and trial wavefunctions
- analyze symmetry constraints
- examine particle-hole symmetry
- derive consequences of finite-width and Landau-level mixing terms
- formulate controlled approximations
- identify assumptions in effective theories

Expected outputs:

- derivation summary
- assumptions
- equations or symbolic expressions
- evidence classification
- limitations
- proposed analytical checks

The Theory Agent must distinguish:

- exact algebraic identities
- perturbative expansions
- mean-field approximations
- variational assumptions
- thermodynamic-limit assumptions
- conjectural extrapolations

### 4. Numerics Agent

Suggested file:

```text
config/agents/numerics_agent.yaml
```

Responsibilities:

- run or prepare exact diagonalization tasks
- inspect simulation recipes
- validate small fixtures
- compare spectra
- compute overlaps where implemented
- track finite-size limitations
- report numerical precision and solver metadata

Expected outputs:

- simulation recipe
- run metadata
- solver used
- parameter values
- eigenvalues or observables
- finite-size caveats
- validation status
- artifact paths

The Numerics Agent must report:

- geometry
- particle number
- flux
- shift
- Hilbert-space or basis dimension
- pseudopotentials
- solver
- convergence status
- numerical tolerance where available

Numerical evidence must not be reported as exact thermodynamic proof.

### 5. Falsification Agent

Suggested file:

```text
config/agents/falsification_agent.yaml
```

Responsibilities:

- challenge assumptions
- search for counterexamples
- identify predictions that distinguish candidate states
- test whether claims survive known perturbations
- inspect whether numerical evidence is overinterpreted
- maintain falsification log

Expected outputs:

- challenged claims
- failure modes
- possible counterexamples
- required tests
- falsification status
- severity level
- recommended next action

The Falsification Agent must be allowed to disagree with the Director, Theory Agent, Literature Agent, and Numerics Agent.

The Director must preserve falsification findings in the final report.

### 6. Experiment Bridge Agent

Suggested file:

```text
config/agents/experiment_bridge_agent.yaml
```

Responsibilities:

- compare theoretical predictions with experimental observables
- track energy scales
- relate candidate states to measured gaps
- compare quasiparticle charge predictions
- compare interferometry or thermal Hall implications
- identify sample-quality, disorder, finite-width, and LL-mixing relevance

Expected outputs:

- observable table
- experimental constraint summary
- candidate-state compatibility notes
- uncertainty classification
- proposed theory-experiment checks

The Experiment Bridge Agent must distinguish:

- direct experimental observation
- inferred quantity
- model-dependent interpretation
- unresolved experimental ambiguity

### 7. Knowledge Curator Agent

Suggested file:

```text
config/agents/knowledge_curator_agent.yaml
```

Responsibilities:

- update knowledge-base files
- maintain structured Markdown notes
- update claim ledgers
- maintain graph-compatible links
- prevent duplicate or contradictory entries
- summarize daily artifacts into persistent memory

Expected outputs:

- files updated
- knowledge nodes created or modified
- claim IDs added or updated
- unresolved assumptions added or updated
- links to reports and artifacts

The Knowledge Curator must not silently overwrite prior scientific conclusions. If a conclusion changes, the previous state and reason for revision must be recorded.

---

## Agent Output Schema

Every subagent output should be structured. Prefer JSON or Markdown with a machine-readable front matter block.

Minimum required fields:

```yaml
agent_name: string
agent_role: string
task_id: string
run_id: string
mode: test | production
status: success | partial | failed
summary: string
claims:
  - claim_id: string
    text: string
    evidence_type: exact result | controlled approximation | numerical evidence | variational assumption | phenomenological argument | conjecture
    support: string
    limitations: string
    confidence: low | medium | high
artifacts:
  - path: string
    type: markdown | json | csv | figure | log | simulation_output | other
errors:
  - string
next_actions:
  - string
```

Malformed outputs must be rejected or marked failed. They must not be silently accepted.

---

## Scientific Evidence Labels

Every claim must use exactly one of the following labels.

### Exact Result

Use only for statements derived without approximation from a specified mathematical model.

Examples:

- exact diagonalization result for a specified finite Hamiltonian
- exact symmetry relation
- exact algebraic identity
- exact consequence of a stated Hamiltonian

Do not use for thermodynamic extrapolations unless mathematically proven.

### Controlled Approximation

Use when there is a small parameter or systematic expansion.

Examples:

- perturbation theory in a specified small parameter
- controlled finite-width expansion
- controlled Landau-level-mixing expansion, if the expansion parameter and regime are explicit

State the control parameter and expected error behavior.

### Numerical Evidence

Use for finite-size exact diagonalization, DMRG, Monte Carlo, variational Monte Carlo, tensor networks, or other numerical results.

State:

- system size
- geometry
- Hamiltonian
- solver
- boundary conditions
- convergence criteria
- limitations

Do not present numerical evidence as exact thermodynamic proof.

### Variational Assumption

Use for claims based on trial wavefunctions, variational ansaetze, or restricted variational spaces.

State what class of states was assumed.

### Phenomenological Argument

Use for arguments based on effective models, experimental fitting, heuristic physical reasoning, or phenomenological field theories.

State what microscopic information is not derived.

### Conjecture

Use for plausible but unproven claims, speculative mechanisms, or proposed research directions.

Conjectures must be clearly marked and assigned follow-up tests where possible.

---

## Claim Disposition Labels

The Director must classify each important claim as one of:

### Accepted

A claim may be accepted only if:

- it has a valid evidence label
- support is provided
- limitations are stated
- no unresolved contradiction blocks its use

Acceptance does not mean final truth. It means accepted for the current project state.

### Rejected

A claim should be rejected if:

- it is unsupported
- it contradicts validated results
- it relies on hidden assumptions
- it fails a required test
- it is malformed or unverifiable

The reason for rejection must be recorded.

### Deferred

A claim should be deferred if:

- more computation is required
- more literature review is required
- there is unresolved disagreement between agents
- required data are unavailable
- the result depends on an untested assumption

Deferred claims should generate next-loop tasks.

---

## Physics Validation Rules

Physics code must be inspectable and reproducible.

Prefer clear NumPy/SciPy/SymPy implementations over opaque or highly optimized code unless performance is explicitly required.

Every simulation artifact should record:

- recipe ID
- date/time
- geometry
- particle number
- flux
- shift
- Hamiltonian terms
- pseudopotentials
- basis size
- solver
- random seed if applicable
- convergence criteria
- eigenvalues or measured observables
- status
- error messages if failed

Small deterministic fixtures should be used for test mode.

For example, the Laughlin validation fixture with N = 3 and N_flux = 6 on the sphere may be used as a sanity check for reporting and numerical validation. The fixture should be treated as a small validation artifact, not as a production-scale result.

---

## Parallel Execution Rules

Parallel execution may be used for independent subagent tasks.

The parallel runner must capture:

- run ID
- task ID
- agent name
- agent role
- start timestamp
- end timestamp
- duration
- status
- exception information
- output artifact path
- token usage if available
- model/deployment metadata if available

The parallel runner must not allow one failed subagent to disappear silently.

If a required subagent fails, the daily loop must either:

- fail the run, or
- mark the run as partial and explicitly explain why the failure does not invalidate the whole loop

Production mode must never report clean success when required subagents failed.

---

## Foundry Integration Rules

Do not redesign the Foundry client if one already exists. Wrap existing functionality only as needed.

The Foundry adapter should support:

- health check
- model/deployment resolution
- test stub or mock client
- production client
- structured errors
- timeout budget
- token budget
- retry policy where appropriate
- clear distinction between authentication failure, configuration failure, model failure, and malformed response

Production mode must fail clearly if Foundry configuration is missing or invalid.

Test mode may use dummy Foundry values or a mock Foundry client.

No Foundry secret may be printed.

---

## GitHub Integration Rules

GitHub is the persistent project memory, but writes must be gated.

Test mode must not mutate GitHub unless explicitly configured to use a safe test repository or dry-run branch.

Production mode may perform GitHub writes only if enabled by configuration.

Possible production writes:

- create or update daily-loop issue
- commit artifacts to a configured branch
- create a pull request
- comment on an issue
- update project-tracking files
- attach or link reports

Every GitHub write should be logged in the run summary.

If GitHub write mode is disabled, the system should still write local artifacts.

Do not print GitHub tokens.

---

## Artifact Rules

Each run should have a unique run ID.

Suggested format:

```text
YYYYMMDD-HHMMSS-mode-shortuuid
```

Artifacts should be written under a mode-specific location.

Suggested paths:

```text
artifacts/test/<run_id>/
artifacts/production/<run_id>/
knowledge_base/daily_reports/<YYYY-MM-DD>.md
knowledge_base/falsification_log.md
knowledge_base/claim_ledger.md
```

Required artifacts for a completed daily loop:

```text
run_summary.json
daily_report.md
task_graph.json
task_ledger.json
agent_outputs/
validation_summary.json
```

Production runs should preserve raw agent outputs even when the Director rejects the claims.

---

## Report Requirements

The daily report must include:

```text
# Daily Research Loop Report

## Run metadata
## Mode
## Daily objective
## Director plan
## Agent task graph
## Subagent results
## Physics and validation checks
## Scientific status of today's loop
## Accepted claims
## Rejected claims
## Deferred claims
## Unresolved assumptions
## Artifacts written
## GitHub updates
## Failures and warnings
## Recommended next loop
```

The report must explicitly state whether it was produced in test mode or production mode.

The report must not hide failed tasks.

The report must not present unsupported scientific claims as accepted results.

---

## Testing Requirements

Before completing orchestration changes, run:

```bash
python3 -m pytest
```

Add or update tests for:

- test mode does not require real production secrets
- production mode requires production configuration
- `.env` loading does not print secrets
- missing Foundry configuration fails clearly
- Director produces a valid task graph
- task graph schema is validated
- parallel runner executes independent mock tasks
- parallel runner records failed tasks
- malformed subagent output is rejected
- daily report is generated in test mode
- run summary JSON is generated in test mode
- GitHub writes are disabled in test mode by default
- sample Laughlin fixture is consumed correctly
- production mode refuses to run without required environment variables
- scientific claims without evidence labels are rejected

If tests fail, report:

- exact command run
- failing test names
- failure reason
- suspected cause
- files likely involved
- proposed next fix

Do not claim tests pass unless they were actually run and passed.

---

## Coding Standards

Prefer:

- explicit dataclasses or Pydantic-style schemas if the repo already uses them
- typed function signatures
- small functions
- structured logging
- deterministic tests
- clear exceptions
- narrow adapters around external services
- dependency injection for testability

Avoid:

- broad rewrites
- hidden global state
- printing secrets
- hard-coded production paths
- hard-coded model names unless placed in config
- unbounded retries
- unbounded parallelism
- swallowing exceptions
- vague scientific summaries
- unsupported claims
- changing public APIs without need

---

## Dependency Rules

Use existing dependencies when possible.

The repository dependency set may include:

- google-genai
- openai
- anthropic
- pyyaml
- pygithub
- numpy
- scipy
- pandas
- matplotlib
- networkx
- h5py
- pytest
- numba
- jinja2
- sympy

Do not add new dependencies unless clearly justified.

If adding a dependency:

1. Explain why existing dependencies are insufficient.
2. Add it to the appropriate dependency file.
3. Add or update tests.
4. Document any new configuration requirement.

---

## Security Rules

Never print secrets.

Never commit secrets.

Never place secrets in reports.

Never place secrets in run summaries.

Never echo `.env`.

Never include bearer tokens in exceptions.

If an exception may contain a secret-bearing URL or header, sanitize it before logging.

Recommended sanitizer behavior:

```text
Authorization: Bearer <redacted>
GITHUB_TOKEN=<redacted>
AZURE_FOUNDRY_KEY=<redacted>
OPENAI_API_KEY=<redacted>
GEMINI_API_KEY=<redacted>
```

---

## Configuration Rules

Configuration should be explicit and mode-aware.

Suggested configuration areas:

```yaml
mode: test | production

foundry:
  enabled: true
  endpoint_env: AZURE_FOUNDRY_ENDPOINT
  api_key_env: AZURE_FOUNDRY_API_KEY
  deployment_env: AZURE_FOUNDRY_DEPLOYMENT
  timeout_seconds: 120

github:
  enabled: true
  dry_run: true
  token_env: GITHUB_TOKEN
  repository: owner/repo
  write_issues: false
  write_branches: false
  create_prs: false

orchestration:
  max_parallel_agents: 3
  max_tasks: 8
  fail_on_required_agent_failure: true
  artifact_root: artifacts/test

budgets:
  max_tokens_per_agent: 8000
  max_total_tokens: 40000
  max_runtime_seconds: 1800

validation:
  require_evidence_labels: true
  reject_malformed_outputs: true
  require_daily_report: true
```

Test configuration should use safe defaults.

Production configuration should require explicit enablement for external writes.

---

## CLI Rules

The CLI should make mode explicit.

Preferred command shape:

```bash
python3 -m src.orchestrator.cli --run --mode test
python3 -m src.orchestrator.cli --run --mode production
```

Useful additional flags:

```bash
--dry-run
--config path/to/config.yaml
--max-parallel-agents 4
--artifact-root artifacts/test
--no-github-write
--foundry-health-check
```

If CLI behavior differs, document the actual command.

---

## Error Handling Rules

Errors must be structured and actionable.

Configuration errors should say which variable or file is missing.

Agent-output errors should identify:

- agent name
- task ID
- missing field
- invalid evidence label
- malformed artifact path
- schema violation

Foundry errors should distinguish:

- missing configuration
- authentication failure
- timeout
- rate limit
- model/deployment unavailable
- malformed response

GitHub errors should distinguish:

- missing token
- insufficient permissions
- repository not found
- branch conflict
- issue/PR creation failure
- dry-run blocked mutation

Production mode must not hide stack traces from logs, but final user-facing summaries should be concise and sanitized.

---

## Final Response Requirements for Codex Tasks

At the end of any Codex task, report:

```text
Summary:
- Files changed:
- Main implementation:
- Tests added/updated:
- Commands run:
- Tests passed:
- Tests failed:
- Artifacts produced:
- Remaining gaps:
- Exact test-loop command:
- Exact production-loop command:
```

Do not claim to have run a command if it was not run.

Do not claim production deployment unless production deployment actually occurred.

Do not claim GitHub mutation unless it actually occurred.

---

## Definition of Done

A daily-loop orchestration task is complete only when:

1. Test mode can run without production secrets.
2. Production mode refuses to run without required production configuration.
3. The Director can generate or load a valid task graph.
4. Independent subagent tasks can execute in parallel.
5. Subagent outputs are validated.
6. Claims are evidence-labeled.
7. Malformed scientific outputs are rejected.
8. A Markdown daily report is generated.
9. A JSON run summary is generated.
10. Relevant tests pass.
11. The final response lists exact commands run and remaining gaps.

---

## Non-Negotiable Constraints

- Use `python3`, not `python`.
- Keep test and production modes separated.
- Never print secrets.
- Never silently accept malformed subagent output.
- Never silently skip failed required agents.
- Never present unsupported scientific claims as accepted.
- Never treat finite-size numerical evidence as thermodynamic proof.
- Never perform GitHub writes in test mode unless explicitly configured.
- Never perform broad rewrites when a targeted patch is sufficient.
- Always preserve falsification findings.
- Always report unresolved assumptions.
