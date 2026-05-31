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
        self.config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}

        # Initialize Adapters
        self.llm = None
        self.github = None
        self.kg = KnowledgeGraph(kb_path=os.path.join(self.workspace_path, "knowledge_base"))

        self._init_adapters()

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
            "dry_run": dry_run
        }

        # Step 3: Consult PI (If LLM is available)
        pi_instruction = "You are the PI. Direct the research department based on the current context."
        pi_prompt = f"Current Research Context:\n{yaml.dump(pi_context)}\nDirect the next actions."
        
        pi_direction = "Initialize standard FQHE exact diagonalization benchmark validation runs."
        if self.llm and not dry_run:
            try:
                pi_direction = self.llm.generate_text(
                    prompt=pi_prompt,
                    system_instruction=pi_instruction,
                    model=self.config.get("models", {}).get("pi")
                )
                logger.info("PI Agent has formulated the scientific roadmap direction.")
            except Exception as e:
                logger.error(f"PI Agent execution failed: {e}. Using default roadmap.")

        # Step 4: Decompose & Delegate tasks
        logger.info(f"PI Direction for today: '{pi_direction[:100]}...'")
        
        delegations = []
        # If dry run or github is not connected, we output simulated delegations
        if dry_run or not self.github or not self.github.is_configured():
            logger.info("Simulating task delegation (Dry Run / Local Mode):")
            delegations.append({
                "task_id": "T-ED-001",
                "assigned_division": "Numerical Division",
                "mission": "Run exact diagonalization validation checks for small systems (N=3 FQHE states)."
            })
        else:
            # Create a real GitHub issue
            issue_title = "[PI Objective] FQHE ED solver benchmark validation"
            issue_body = f"Directed by PI:\n\n{pi_direction}\n\nTask: Verify solver correctness against Laughlin ground states."
            issue_num = self.github.create_issue(
                title=issue_title,
                body=issue_body,
                labels=["status:pending", "division:numerical"]
            )
            if issue_num != -1:
                delegations.append({
                    "task_id": f"Issue #{issue_num}",
                    "assigned_division": "Numerical Division",
                    "mission": "Laughlin state verification"
                })

        logger.info("=== DAILY CYCLE COMPLETE ===")
        return {
            "status": "completed",
            "pi_direction": pi_direction,
            "delegations": delegations
        }
