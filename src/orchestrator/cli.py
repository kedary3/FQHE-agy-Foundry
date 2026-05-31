# File: src/orchestrator/cli.py
"""Command-line interface for the multi-agent research department orchestrator."""

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from .client import LLMAdapter
from .engine import ResearchDepartmentEngine
from ..physics.runner import execute_simulation_recipe


def configure_logging() -> None:
    """Configure scientific, clean terminal logging format."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> None:
    load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
    configure_logging()

    logger = logging.getLogger("orchestrator.cli")

    parser = argparse.ArgumentParser(
        description="Theoretical & Computational Physics Research Department (ν = 5/2 FQHE)"
    )

    parser.add_argument(
        "--run",
        action="store_true",
        help="Execute a full daily multi-agent research cycle.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the multi-agent execution loop without making API calls or commits.",
    )
    parser.add_argument(
        "--recipe",
        type=str,
        metavar="PATH",
        help="Execute a specific declarative physics simulation recipe YAML.",
    )
    parser.add_argument(
        "--sync-graph",
        action="store_true",
        help="Sync the knowledge graph and print unresolved contradictions.",
    )
    parser.add_argument(
        "--check-provider",
        action="store_true",
        help="Check configured LLM provider connectivity with a minimal prompt. Secrets are not printed.",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        help=(
            "Provider override for --check-provider. "
            "Supported: gemini, openai, anthropic, azure_openai, foundry_agent."
        ),
    )

    args = parser.parse_args()

    if args.check_provider:
        try:
            adapter = LLMAdapter(provider=args.provider)
            response = adapter.generate_text(
                "Reply with exactly: OK",
                system_instruction=(
                    "You are testing connectivity. "
                    "Do not include credentials or environment details."
                ),
            )
            status = "ok" if response.strip() else "empty_response"
            print(f"Provider connectivity status: {status}")
            print(f"Provider: {adapter.provider}")
        except Exception as exc:
            logger.error("Provider connectivity check failed: %s", exc)
            sys.exit(1)
        return

    try:
        engine = ResearchDepartmentEngine()
    except Exception as exc:
        logger.error("Failed to initialize Research Department Engine: %s", exc)
        sys.exit(1)

    if args.run:
        results = engine.run_daily_cycle(dry_run=args.dry_run)
        logger.info("Daily cycle finished with status: %s", results["status"])

        for delegation in results["delegations"]:
            logger.info(
                "Delegated to %s: %s (ID: %s)",
                delegation["assigned_division"],
                delegation["mission"],
                delegation["task_id"],
            )

    elif args.recipe:
        try:
            logger.info("Running declarative simulation: %s", args.recipe)
            results = execute_simulation_recipe(
                args.recipe,
                output_dir="simulations/results",
            )

            print("\n=== Simulation Results ===")
            print(f"Recipe ID: {results['recipe_id']}")
            print(f"Title: {results['title']}")
            print(f"Geometry: {results['physics']['geometry']}")
            print(f"Basis Dimension: {results['physics']['basis_dimension']}")
            print(f"Eigenvalues: {results['numerical']['eigenvalues']}")
            print("==========================\n")

        except Exception as exc:
            logger.error("Failed to execute simulation recipe: %s", exc)
            sys.exit(1)

    elif args.sync_graph:
        engine.kg.build_graph()
        unresolved = engine.kg.get_unresolved_contradictions()

        print("\n=== Knowledge Graph Sync ===")
        print(f"Total Registered Nodes: {engine.kg.graph.number_of_nodes()}")
        print(f"Total Directed Relationships: {engine.kg.graph.number_of_edges()}")
        print(f"Unresolved Contradictions ({len(unresolved)}):")

        for node_id, data in unresolved:
            print(f"  - {node_id}: {data.get('title')} (Topic: {data.get('topic')})")

        print("============================\n")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
