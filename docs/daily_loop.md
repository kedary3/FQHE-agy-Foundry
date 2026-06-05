# Daily Loop

The Director-controlled daily loop has two explicit modes.

## Test Mode

Test mode runs the full loop machinery, but the scientific result is provisional and noncanonical. It is intended for CI, local development, and safety checks.

Use:

```bash
python3 -m src.orchestrator.cli --run --mode test
```

Test mode:

- uses deterministic local subagent fixtures by default
- consumes the small Laughlin validation result at `simulations/results/result_example_laughlin.json`
- writes artifacts under `artifacts/test/<run_id>/`
- does not mutate GitHub
- does not update canonical knowledge-base memory
- does not require production Foundry secrets

## Production Mode

Production mode is the canonical daily research loop. Its outputs are allowed to update durable project memory.

Use:

```bash
python3 -m src.orchestrator.cli --run --mode production
```

Production mode:

- requires `AZURE_AI_PROJECT_ENDPOINT`, `FOUNDRY_AGENT_NAME`, and `RESEARCH_REPOSITORY`
- may use optional `FOUNDRY_AGENT_VERSION` when a specific Foundry agent version is required
- may use optional `FOUNDRY_AGENT_API_VERSION`; defaults to `v1`
- uses the configured Foundry agent through `AIProjectClient.send_request(...)` against the Azure project agent protocol endpoint
- routes to `/agents/<agent-name>/endpoint/protocols/openai/responses?api-version=<version>`, so the runtime does not parse a model name
- dispatches specialized subagent tasks under the Director
- writes artifacts under `artifacts/production/<run_id>/`
- writes durable reports and ledgers under `knowledge_base/`
- refuses clean success if required validation or required agents fail

GitHub writes are gated. Set `DAILY_LOOP_GITHUB_WRITE=true` to allow production issue creation. Set `DAILY_LOOP_CREATE_PR=true` plus `DAILY_LOOP_PR_HEAD_BRANCH=<existing-branch>` to create a PR from an existing branch. No PR is created by default, and the loop does not invent branches or commit local files implicitly.

## Director and Subagents

The Director lives in `src/orchestrator/director.py`. It generates the task graph, validates subagent output schemas, enforces evidence labels, rejects malformed claims, and synthesizes the final report.

Daily subagent work is generated from durable memory, not static role prompts. Before planning, `DailyLoopRunner` collects a sanitized memory context from:

- `knowledge_base/claim_ledger.md`
- `knowledge_base/falsification_log.md`
- recent `knowledge_base/daily_reports/*.md`
- recent `artifacts/test/*` and `artifacts/production/*` run summaries, ledgers, validation summaries, and agent outputs
- `simulations/results/*.json`
- `simulations/recipes/*.yaml`
- `reports/*.md`
- open GitHub issue state when a configured read-capable GitHub client is available

The collected memory is written to `memory_context.json`. Each task in `task_graph.json` includes:

- `daily_loop_command`
- `memory_triggers`
- `source_refs`
- `skill_instructions`
- `bounded_deliverables`

GitHub issue reads do not enable GitHub writes. Test mode skips live GitHub issue reads unless a test client is injected or `DAILY_LOOP_GITHUB_READ=true` is set. Production writes remain gated by `DAILY_LOOP_GITHUB_WRITE=true` and PR creation remains gated separately.

Required agent configs live in `config/agents/`:

- `director_pi.yaml`
- `literature_agent.yaml`
- `theory_agent.yaml`
- `numerics_agent.yaml`
- `falsification_agent.yaml`
- `experiment_bridge_agent.yaml`
- `knowledge_curator_agent.yaml`

Each subagent output must classify every claim as exactly one of:

- exact result
- controlled approximation
- numerical evidence
- variational assumption
- phenomenological argument
- conjecture

## Inspecting Reports

Each run writes:

- `daily_report.md`
- `run_summary.json`
- `task_graph.json`
- `task_ledger.json`
- `validation_summary.json`
- `agent_outputs/*.json`

For test runs, inspect:

```text
artifacts/test/<run_id>/daily_report.md
```

For production runs, inspect:

```text
artifacts/production/<run_id>/daily_report.md
knowledge_base/daily_reports/<YYYY-MM-DD>.md
```

The report always includes `Scientific status of today's loop`, with accepted, rejected, and deferred claims plus unresolved assumptions and next tests.
