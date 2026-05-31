# File: src/orchestrator/engine.py
"""The core coordination engine managing the scientific multi-agent execution loop."""

import os
import yaml
import logging
from .client import LLMAdapter
from .github_client import GitHubClient
from ..knowledge.parser import KnowledgeGraph

logger = logging.getLogger("orchestrator.engine")

class ResearchDepartmentEngine:
    def __init__(self, workspace_path: str = None):
        """
        Initializes the research department engine.

        Args:
            workspace_path (str): Root directory of the repository.
        """
        self.workspace_path = workspace_path or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_path = os.path.join(self.workspace_path, "config", "config.yaml")
        
        # Load Global Config
        self.config = self._load_yaml_document(self.config_path)
        self.agents = self._load_yaml_tree(os.path.join(self.workspace_path, "config", "agents"))
        self.programs = self._load_yaml_tree(os.path.join(self.workspace_path, "config", "programs"))

        # Initialize Adapters
        self.llm = None
        self.github = None
        paths = self.config.get("paths", {})
        kb_path = os.path.join(self.workspace_path, paths.get("knowledge_base", "knowledge_base"))
        self.kg = KnowledgeGraph(kb_path=kb_path)

        self._init_adapters()

    @staticmethod
    def _load_yaml_document(path: str) -> dict:
        """Load the first non-empty YAML document from a file."""
        if not os.path.exists(path):
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            documents = yaml.safe_load_all(f)
            for document in documents:
                if isinstance(document, dict):
                    return document
        return {}

    def _load_yaml_tree(self, root_path: str) -> dict:
        """Load YAML files under a directory into an id-keyed dictionary."""
        records = {}
        if not os.path.exists(root_path):
            logger.warning(f"YAML config path does not exist: {root_path}")
            return records

        for current_root, _, files in os.walk(root_path):
            for filename in sorted(files):
                if not filename.endswith((".yaml", ".yml")):
                    continue

                path = os.path.join(current_root, filename)
                try:
                    data = self._load_yaml_document(path)
                except yaml.YAMLError as e:
                    logger.error(f"Failed to parse YAML config {path}: {e}")
                    continue

                if not data:
                    continue

                record_id = data.get("id") or os.path.splitext(os.path.relpath(path, root_path))[0]
                records[record_id] = data

        return dict(sorted(records.items()))

    def _init_adapters(self):
        """Prepares LLM and GitHub client wrappers, catching configuration errors cleanly."""
        try:
            self.llm = LLMAdapter()
            logger.info("LLM Adapter initialized successfully.")
        except Exception as e:
            logger.warning(f"LLM Adapter could not be initialized: {e}. Running in restricted mode.")

        try:
            self.github = GitHubClient()
            if self.github.is_configured():
                logger.info("GitHub Client connected successfully.")
            else:
                logger.warning("GitHub Client is unconfigured. Running in local-only mode.")
        except Exception as e:
            logger.warning(f"GitHub Client initialization failed: {e}. Running in local-only mode.")

    def _agent_model(self, agent_id: str, model_key: str) -> str:
        """Resolve an agent model from agent YAML first, then global config."""
        agent = self.agents.get(agent_id, {})
        return agent.get("default_model") or self.config.get("models", {}).get(model_key)

    def _program_context(self) -> list:
        """Return compact program metadata suitable for PI prompts."""
        context = []
        for program_id, program in self.programs.items():
            context.append({
                "id": program_id,
                "name": program.get("name"),
                "assigned_division": program.get("assigned_division"),
                "core_hypotheses": program.get("core_hypotheses", []),
                "active_questions": program.get("active_questions", []),
                "key_benchmarks": program.get("key_benchmarks", [])
            })
        return context

    @staticmethod
    def _label_slug(value: str, max_length: int = 40) -> str:
        """Convert free-form config labels to GitHub-label-safe slugs."""
        slug = ''.join(ch.lower() if ch.isalnum() else '-' for ch in value)
        slug = '-'.join(part for part in slug.split('-') if part)
        return slug[:max_length].rstrip("-")

    def _suggest_agent_for_division(self, division: str) -> str:
        """Map a configured division string to the closest worker agent id."""
        division_l = (division or "").lower()
        if "numerical" in division_l:
            return "A-PHYS"
        if "analytical" in division_l or "theory" in division_l:
            return "A-THEO"
        if "literature" in division_l:
            return "A-LIT"
        if "verification" in division_l or "referee" in division_l:
            return "A-REPRO"
        return "A-COOR"

    def _build_program_delegations(self, pi_direction: str) -> list:
        """Turn configured research programs into concrete daily tasks."""
        if not self.programs:
            return [{
                "task_id": "T-ED-001",
                "assigned_division": "Numerical Division",
                "program_id": None,
                "suggested_agent": "A-PHYS",
                "mission": "Run exact diagonalization validation checks for small systems (N=3 FQHE states).",
                "source_direction": pi_direction
            }]

        max_delegations = int(self.config.get("orchestration", {}).get("max_daily_delegations", 3))
        delegations = []
        for program_id, program in list(self.programs.items())[:max_delegations]:
            active_questions = program.get("active_questions", [])
            focus = active_questions[0] if active_questions else program.get("description", "Advance this research program.").strip()
            division = program.get("assigned_division", "Research Division")
            delegations.append({
                "task_id": f"T-{program_id}",
                "assigned_division": division,
                "program_id": program_id,
                "suggested_agent": self._suggest_agent_for_division(division),
                "mission": f"{program.get('name', program_id)}: {focus}",
                "source_direction": pi_direction
            })

        return delegations

    def run_daily_cycle(self, dry_run: bool = False) -> dict:
        """
        Executes a single complete daily cycle of the physics department.
        
        1. Sync the Knowledge Graph.
        2. Scan for open Contradictions & active Hypotheses.
        3. Consult the PI Agent for global scientific direction.
        4. Decompose PI objectives into active issues.
        5. Trigger assigned worker agents.
        """
        logger.info("=== STARTING DAILY RESEARCH CYCLE ===")
        
        # Step 1: Sync the Knowledge Graph
        self.kg.build_graph()
        unresolved_c = self.kg.get_unresolved_contradictions()
        logger.info(f"Sync complete. Found {len(unresolved_c)} unresolved scientific contradictions.")

        # Step 2: Assemble PI context
        pi_context = {
            "workspace": self.workspace_path,
            "total_hypotheses": len([n for n in self.kg.graph.nodes if n.startswith("H-")]),
            "unresolved_contradictions": [c[0] for c in unresolved_c],
            "agents": list(self.agents.keys()),
            "active_programs": self._program_context(),
            "dry_run": dry_run
        }

        # Step 3: Consult PI (If LLM is available)
        pi_agent = self.agents.get("A-PI", {})
        pi_instruction = pi_agent.get(
            "system_prompt_template",
            "You are the PI. Direct the research department based on the current context."
        ).strip()
        pi_prompt = f"Current Research Context:\n{yaml.dump(pi_context, sort_keys=False)}\nDirect the next actions."
        
        pi_direction = "Initialize standard FQHE exact diagonalization benchmark validation runs."
        if self.llm and not dry_run:
            try:
                pi_direction = self.llm.generate_text(
                    prompt=pi_prompt,
                    system_instruction=pi_instruction,
                    model=self._agent_model("A-PI", "pi")
                )
                logger.info("PI Agent has formulated the scientific roadmap direction.")
            except Exception as e:
                logger.error(f"PI Agent execution failed: {e}. Using default roadmap.")

        # Step 4: Decompose & Delegate tasks
        logger.info(f"PI Direction for today: '{pi_direction[:100]}...'")
        
        delegations = self._build_program_delegations(pi_direction)
        # If dry run or github is not connected, we output local delegations
        if dry_run or not self.github or not self.github.is_configured():
            logger.info("Prepared task delegation plan (Dry Run / Local Mode).")
        else:
            created_delegations = []
            for delegation in delegations:
                program_id = delegation.get("program_id")
                issue_title = f"[PI Objective][{program_id or 'ED'}] {delegation['mission'][:80]}"
                issue_body = (
                    f"Directed by PI:\n\n{pi_direction}\n\n"
                    f"Assigned division: {delegation['assigned_division']}\n"
                    f"Suggested agent: {delegation['suggested_agent']}\n\n"
                    f"Task: {delegation['mission']}"
                )
                labels = [
                    "status:pending",
                    f"division:{self._label_slug(delegation['assigned_division'])}",
                    f"agent:{self._label_slug(delegation['suggested_agent'])}"
                ]
                if program_id:
                    labels.append(f"program:{self._label_slug(program_id)}")

                issue_num = self.github.create_issue(
                    title=issue_title,
                    body=issue_body,
                    labels=labels
                )
                if issue_num != -1:
                    delegation = dict(delegation)
                    delegation["task_id"] = f"Issue #{issue_num}"
                    created_delegations.append(delegation)
            delegations = created_delegations

        logger.info("=== DAILY CYCLE COMPLETE ===")
        return {
            "status": "completed",
            "pi_direction": pi_direction,
            "delegations": delegations
        }
