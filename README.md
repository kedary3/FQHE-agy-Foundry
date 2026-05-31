# Theoretical & Computational Physics Research Department (nu = 5/2 FQHE)

A GitHub-based multi-agent research workflow focused on deriving, testing, comparing, and falsifying microscopic explanations of the fractional quantum Hall effect (FQHE) at filling factor $\nu = 5/2$.

The architecture is intended to simulate a university physics department with specialized agents operating under a Principal Investigator (PI) agent, using GitHub as persistent scientific memory. The current implementation includes the orchestration shell, YAML-defined agent and program metadata, a local/dry-run delegation loop, a GitHub issue adapter, and a small exact-diagonalization validation core.

## Repository Layout

* `config/agents/`: YAML definitions of agent roles, prompts, and alignments.
* `config/programs/`: YAML definitions of research programs and benchmark targets.
* `src/orchestrator/`: The core multi-agent execution and GitHub client logic.
* `src/physics/`: Inspectable, NumPy/SciPy-based Exact Diagonalization (ED) core.
* `src/knowledge/`: Obsidian-compatible Markdown parsing and NetworkX knowledge graph.
* `simulations/`: Declarative simulation recipes and raw outputs.
* `knowledge_base/`: Structured scientific notebooks, paper reviews, and reports.
* `tests/`: Focused physics and orchestration regression tests.

## Managed Agent Tree

The department is organized as a PI-led research tree with specialized divisions.
The Numerical Division is explicitly split into independent subgroups:

```text
Numerical Division
├── Exact Diagonalization Group
├── DMRG/Tensor Network Group
├── Monte Carlo Group
├── Validation & Benchmark Group
└── Data Analysis Group
```

The ED and DMRG/Tensor Network groups are expected to maintain independent
numerical pipelines. Disagreement between them is scientifically valuable: it
should be preserved as a tracked result, then investigated by validation,
benchmarking, and referee review rather than collapsed into premature consensus.

## Getting Started

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Set up your GitHub token and LLM API keys:
   ```bash
   export GITHUB_TOKEN="your_github_pat"
   export GEMINI_API_KEY="your_gemini_key"
   # Optional: export OPENAI_API_KEY="your_openai_key"
   ```

3. **Run Orchestration Suite (Local Development):**
   ```bash
   python -m src.orchestrator.cli --dry-run --run
   ```

4. **Run a Physics Recipe:**
   ```bash
   python -m src.orchestrator.cli --recipe simulations/recipes/example_laughlin_recipe.yaml
   ```

5. **Run Tests:**
   ```bash
   pytest
   ```
