from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from scaffolding.config import ApplicationConfig
from scaffolding.runner import (
    DEFAULT_PHASES,
    complete_step,
    detect_state,
    load_or_init_state,
    next_pending_step,
    phase_status,
    save_state,
)
from scaffolding.steps.local_dependencies import LocalDependenciesStep
from scaffolding.steps.local_deploy import LocalDeployStep
from scaffolding.steps.local_environment import LocalEnvironmentStep
from scaffolding.steps.local_validation import LocalValidationStep


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="create-cornerstone-app",
        description="Cornerstone application setup and local/cloud development CLI.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository to initialize (defaults to the current directory).",
    )
    subparsers = parser.add_subparsers(dest="command")

    status = subparsers.add_parser(
        "status", help="Show setup progress without changing files."
    )
    status.set_defaults(handler=show_status)

    run = subparsers.add_parser("run", help="Start or resume application setup.")
    run.add_argument(
        "--plan",
        action="store_true",
        help="Show the next local steps without executing commands.",
    )
    run.set_defaults(handler=run_setup)

    return parser


def show_status(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    state = detect_state(repo_root)
    if state is None:
        print("Cornerstone application setup")
        print("Status: Not initialized")
        print("Run `./create-cornerstone-app run` to begin.")
        return 0

    print("Cornerstone application setup")
    print(f"Status: {state.get('status', 'unknown')}")
    print(f"Provider: {state.get('provider', 'aws')}")
    print(f"Next step: {next_pending_step(state) or 'complete'}")
    for phase, status in phase_status(state).items():
        marker = "x" if status == "complete" else ">" if status == "pending" else " "
        print(f"  [{marker}] {phase}")
    return 0


def run_setup(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    state = load_or_init_state(repo_root)
    completed = set(state.get("completed_steps") or [])
    state["pending_steps"] = [
        phase for phase in DEFAULT_PHASES if phase not in completed
    ]
    next_step = next_pending_step(state)

    print("Cornerstone application setup")
    print("Starting Cornerstone application setup.")
    print(f"State file: {repo_root / '.cornerstone' / 'state.json'}")
    print(f"Next step: {next_step or 'complete'}")
    if args.plan or next_step is None:
        if args.plan:
            print(
                "Plan: configure, specialize, local environment, dependencies, database, validation"
            )
        return 0

    config = ApplicationConfig.from_repository_root(repo_root)
    state["configuration"] = config.as_dict()
    save_state(repo_root, state)

    steps = {
        "configure": lambda: None,
        "specialize": lambda: None,
        "local_environment": lambda: LocalEnvironmentStep(repo_root, config).execute(),
        "local_dependencies": lambda: LocalDependenciesStep(repo_root).execute(),
        "local_database": lambda: LocalDeployStep(repo_root).execute(),
        "local_validation": lambda: LocalValidationStep(repo_root).execute(),
    }

    for step_name in (
        "configure",
        "specialize",
        "local_environment",
        "local_dependencies",
        "local_database",
        "local_validation",
    ):
        if step_name in completed:
            continue
        print(f"Running: {step_name}")
        try:
            steps[step_name]()
        except (
            OSError,
            RuntimeError,
            subprocess.CalledProcessError,
            json.JSONDecodeError,
        ) as exc:
            state["status"] = "failed"
            state["failed_step"] = step_name
            state["error"] = str(exc)
            save_state(repo_root, state)
            print(f"Failed during {step_name}: {exc}")
            print(
                "Progress was preserved. Re-run the command after correcting the problem."
            )
            return 1
        complete_step(state, step_name)
        save_state(repo_root, state)

    print("Local development environment validated.")
    print("Cloud provider selection will be added in a later milestone.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        args.command = "run"
        args.plan = False
        args.handler = run_setup
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
