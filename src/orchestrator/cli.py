# File: src/orchestrator/cli.py
"""Command-line interface for the multi-agent research department orchestrator."""

import argparse
import logging
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - exercised in minimal test envs.
    def load_dotenv(dotenv_path=None, override=False, **kwargs):
        path = Path(dotenv_path or Path.cwd() / ".env")
        if not path.exists():
            return False
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip().strip("'\"")
            if not name:
                continue
            if override or name not in os.environ:
                os.environ[name] = value
        return True

from .client import LLMAdapter
from .daily_loop import DailyLoopError, DailyLoopRunner
from .engine import ResearchDepartmentEngine
from .magentic_manager import PIManager
from ..physics.runner import execute_simulation_recipe


DEFAULT_MAGENTIC_OBJECTIVE = (
    "Validate the N=3 Laughlin fixture and propose next nu=5/2 tests"
)
PRODUCTION_ENV_VARS = (
    "AZURE_AI_PROJECT_ENDPOINT",
    "FOUNDRY_AGENT_ID",
    "RESEARCH_REPOSITORY",
)


def configure_logging() -> None:
    """Configure scientific, clean terminal logging format."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def _load_workflow_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _validate_production_environment(env: dict) -> None:
    missing = [name for name in PRODUCTION_ENV_VARS if not env.get(name)]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required production environment variables: {joined}")


def _run_magentic_mode(args: argparse.Namespace, logger: logging.Logger) -> None:
    config_path = Path(args.config or "config/workflows/magentic.yaml")
    config = _load_workflow_config(config_path)

    if args.mode == "production":
        _validate_production_environment(os.environ)

    manager_config = config.get("manager", {})
    parallelism = config.get("parallelism", {})
    manager = PIManager(
        max_rounds=int(manager_config.get("max_rounds", 12)),
        max_parallel_agents=int(parallelism.get("max_parallel_agents", 3)),
        max_stall_count=int(manager_config.get("max_stall_count", 3)),
        max_replans=int(manager_config.get("max_replans", 3)),
    )
    objective = args.objective or DEFAULT_MAGENTIC_OBJECTIVE
    state = manager.run_test_loop(objective)
    state.mode = args.mode
    state.task_ledger.mode = args.mode

    artifacts = config.get("artifacts", {})
    ledger_root = Path(artifacts.get("ledger_path", ".magentic/ledgers/"))
    reports_root = Path(artifacts.get("reports_path", "reports/"))
    ledger_path = ledger_root / f"{state.task_ledger.run_id}.json"
    report_path = reports_root / f"{state.task_ledger.run_id}.md"

    state.to_json(ledger_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(state.final_report, encoding="utf-8")

    logger.info("Magentic loop finished with status: %s", state.status)
    logger.info("Ledger written: %s", ledger_path)
    logger.info("Report written: %s", report_path)


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
        "--mode",
        choices=("test", "production"),
        default=None,
        help=(
            "Run the Magentic manager loop in explicit test or production mode. "
            "With --run, use the legacy Director-controlled daily loop."
        ),
    )
    parser.add_argument(
        "--objective",
        type=str,
        default=None,
        help="Research objective for the Magentic manager loop.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Optional Magentic workflow config path.",
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

    if args.run:
        if args.mode:
            try:
                summary = DailyLoopRunner(mode=args.mode).run()
            except DailyLoopError as exc:
                logger.error("Daily loop failed: %s", exc)
                sys.exit(1)
            except Exception as exc:
                logger.error("Daily loop could not start: %s", exc)
                sys.exit(1)

            logger.info("Daily loop finished with status: %s", summary["status"])
            logger.info("Run summary: %s", summary["artifacts"][-1])
            return

        try:
            engine = ResearchDepartmentEngine()
        except Exception as exc:
            logger.error("Failed to initialize Research Department Engine: %s", exc)
            sys.exit(1)

        results = engine.run_daily_cycle(dry_run=args.dry_run)
        logger.info("Daily cycle finished with status: %s", results["status"])

        for delegation in results["delegations"]:
            logger.info(
                "Delegated to %s: %s (ID: %s)",
                delegation["assigned_division"],
                delegation["mission"],
                delegation["task_id"],
            )

    elif args.mode:
        try:
            _run_magentic_mode(args, logger)
        except Exception as exc:
            logger.error("Magentic loop failed: %s", exc)
            sys.exit(1)

    elif args.recipe:
        try:
            engine = ResearchDepartmentEngine()
        except Exception as exc:
            logger.error("Failed to initialize Research Department Engine: %s", exc)
            sys.exit(1)

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
        try:
            engine = ResearchDepartmentEngine()
        except Exception as exc:
            logger.error("Failed to initialize Research Department Engine: %s", exc)
            sys.exit(1)

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
