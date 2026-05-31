# File: src/knowledge/parser.py
"""NetworkX-based Markdown frontmatter parser for the Git-native Knowledge Graph."""

import os
import re
import yaml
import logging
import networkx as nx

logger = logging.getLogger("knowledge.parser")

class KnowledgeGraph:
    def __init__(self, kb_path: str = None):
        """
        Initializes the scientific knowledge graph.

        Args:
            kb_path (str): The root path to the 'knowledge_base/' directory.
        """
        self.kb_path = kb_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "knowledge_base")
        self.graph = nx.DiGraph()
        self._frontmatter_regex = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL | re.MULTILINE)

    def build_graph(self):
        """Scans the knowledge base directory recursively and populates the NetworkX graph."""
        self.graph.clear()
        
        if not os.path.exists(self.kb_path):
            logger.warning(f"Knowledge base path does not exist: {self.kb_path}")
            return self.graph

        logger.info(f"Scanning knowledge base at: {self.kb_path}")
        
        # Step 1: Read all frontmatter to register nodes
        for root, _, files in os.walk(self.kb_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    node_data = self._parse_file_frontmatter(file_path)
                    
                    if not node_data or "id" not in node_data:
                        continue
                    
                    node_id = node_data["id"]
                    # Add node with metadata attributes
                    self.graph.add_node(node_id, filepath=file_path, **node_data)
                    logger.debug(f"Registered Knowledge Node: {node_id} ('{node_data.get('title', '')}')")

        # Step 2: Establish relationships (edges) based on evidence/alignments
        for node_id in list(self.graph.nodes):
            node_attrs = self.graph.nodes[node_id]
            
            # Connect programs to hypotheses
            if "core_hypotheses" in node_attrs:
                for target in node_attrs["core_hypotheses"]:
                    if target in self.graph:
                        self.graph.add_edge(node_id, target, relation="core_hypothesis")

            # Connect hypotheses to supporting evidence
            if "supporting_evidence" in node_attrs:
                for target in node_attrs["supporting_evidence"]:
                    if target in self.graph:
                        self.graph.add_edge(node_id, target, relation="supporting_evidence")

            # Connect hypotheses to contradicting evidence
            if "contradicting_evidence" in node_attrs:
                for target in node_attrs["contradicting_evidence"]:
                    if target in self.graph:
                        self.graph.add_edge(node_id, target, relation="contradicting_evidence")

            # Connect contradictions to claims/evidence
            if "supporting_evidence_a" in node_attrs:
                for target in node_attrs["supporting_evidence_a"]:
                    if target in self.graph:
                        self.graph.add_edge(node_id, target, relation="evidence_a")

            if "supporting_evidence_b" in node_attrs:
                for target in node_attrs["supporting_evidence_b"]:
                    if target in self.graph:
                        self.graph.add_edge(node_id, target, relation="evidence_b")

        logger.info(f"Knowledge Graph populated. Nodes: {self.graph.number_of_nodes()}, Edges: {self.graph.number_of_edges()}")
        return self.graph

    def _parse_file_frontmatter(self, file_path: str) -> dict:
        """Helper to extract YAML frontmatter from a markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = self._frontmatter_regex.match(content)
            if match:
                yaml_data = match.group(1)
                return yaml.safe_load(yaml_data) or {}
        except Exception as e:
            logger.error(f"Error parsing frontmatter in {file_path}: {e}")
        return {}

    def get_unresolved_contradictions(self) -> list:
        """Returns all unresolved contradiction nodes."""
        unresolved = []
        for node, data in self.graph.nodes(data=True):
            if node.startswith("C-") and data.get("status") == "unresolved":
                unresolved.append((node, data))
        return unresolved

    def get_hypothesis_status(self, hypothesis_id: str) -> dict:
        """Collects all supporting and contradicting links for a specific hypothesis."""
        if hypothesis_id not in self.graph:
            return {}
        
        node_data = self.graph.nodes[hypothesis_id]
        support = [v for u, v, d in self.graph.out_edges(hypothesis_id, data=True) if d.get("relation") == "supporting_evidence"]
        contradictions = [v for u, v, d in self.graph.out_edges(hypothesis_id, data=True) if d.get("relation") == "contradicting_evidence"]
        
        return {
            "id": hypothesis_id,
            "title": node_data.get("title"),
            "statement": node_data.get("statement"),
            "status": node_data.get("status"),
            "supporting_nodes": support,
            "contradicting_nodes": contradictions
        }
