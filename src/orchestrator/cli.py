# File: src/orchestrator/cli.py
"""Command-line interface for the multi-agent research department orchestrator."""

import argparse
import sys
import logging
from .engine import ResearchDepartmentEngine
from ..physics.runner import execute_simulation_recipe

def configure_logging():
    """Configure scientific, clean terminal logging format."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def main():
    configure_logging()
    logger = logging.getLogger("orchestrator.cli")

    parser = argparse.ArgumentParser(
        description="Theoretical & Computational Physics Research Department (ν = 5/2 FQHE)"
    )
    
    # Execution options
    parser.add_argument(
        "--run", action="store_true",
        help="Execute a full daily multi-agent research cycle."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simulate the multi-agent execution loop without making API calls or commits."
    )
    parser.add_argument(
        "--recipe", type=str, metavar="PATH",
        help="Execute a specific declarative physics simulation recipe YAML."
    )
    parser.add_argument(
        "--sync-graph", action="store_true",
        help="Sync the knowledge graph and print unresolved contradictions."
    )

    args = parser.parse_args()

    # Initialize Engine
    try:
        engine = ResearchDepartmentEngine()
    except Exception as e:
        logger.error(f"Failed to initialize Research Department Engine: {e}")
        sys.exit(1)

    if args.run:
        # Run full cycle
        results = engine.run_daily_cycle(dry_run=args.dry_run)
        logger.info(f"Daily cycle finished with status: {results['status']}")
        for delegation in results["delegations"]:
            logger.info(f"Delegated to {delegation['assigned_division']}: {delegation['mission']} (ID: {delegation['task_id']})")

    elif args.recipe:
        # Execute specific simulation recipe
        try:
            logger.info(f"Running declarative simulation: {args.recipe}")
            results = execute_simulation_recipe(args.recipe, output_dir="simulations/results")
            print("\n=== Simulation Results ===")
            print(f"Recipe ID: {results['recipe_id']}")
            print(f"Title: {results['title']}")
            print(f"Geometry: {results['physics']['geometry']}")
            print(f"Basis Dimension: {results['physics']['basis_dimension']}")
            print(f"Eigenvalues: {results['numerical']['eigenvalues']}")
            print("==========================\n")
        except Exception as e:
            logger.error(f"Failed to execute simulation recipe: {e}")
            sys.exit(1)

    elif args.sync_graph:
        # Build and output graph status
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
