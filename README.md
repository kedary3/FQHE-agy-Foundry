# Theoretical & Computational Physics Research Department (ν = 5/2 FQHE)

A GitHub-based multi-agent research workflow focused on deriving, testing, comparing, and falsifying microscopic explanations of the fractional quantum Hall effect (FQHE) at filling factor $\nu = 5/2$.

The architecture simulates a university physics department with specialized agents operating under a Principal Investigator (PI) agent, utilizing GitHub as the persistent scientific memory.

## Repository Layout

* `config/agents/`: YAML definitions of agent roles, prompts, and alignments.
* `src/orchestrator/`: The core multi-agent execution and GitHub client logic.
* `src/agents/`: Custom agent-class behaviors and factory systems.
* `src/physics/`: Inspectable, NumPy/SciPy-based Exact Diagonalization (ED) core.
* `src/knowledge/`: Obsidian-compatible Markdown parsing & NetworkX knowledge graph.
* `simulations/`: Declarative simulation recipes and raw outputs.
* `knowledge_base/`: Structured scientific notebooks, paper reviews, and reports.
* `tests/`: Extensive physics validation and integration test suites.

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
   python -m src.orchestrator.cli --run
   ```

For detailed architectural specifications and design decisions, see the [Implementation Plan](file:///home/kedary3/.gemini/antigravity-cli/brain/1a00e0e7-dcdd-44c9-8465-e7e0b01d326d/implementation_plan.md).
