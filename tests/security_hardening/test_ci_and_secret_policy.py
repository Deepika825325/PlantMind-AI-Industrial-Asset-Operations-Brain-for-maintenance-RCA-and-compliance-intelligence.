from __future__ import annotations

import subprocess
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/plantmind-ci.yml")


def test_github_actions_workflow_contains_required_day29_checks() -> None:
    assert WORKFLOW_PATH.exists()

    workflow = WORKFLOW_PATH.read_text(
        encoding="utf-8"
    )

    required_terms = [
        "Backend tests, Docker and evaluation smoke",
        "Frontend lint, type check and build",
        "Secret and source security checks",
        "python -m pytest -q",
        "npm run lint",
        "npx tsc --noEmit",
        "npm run build",
        "docker compose --env-file .env.example config --quiet",
        "docker compose --env-file .env.example build",
        "pip-audit",
        "Evaluation smoke test",
        "gitleaks/gitleaks-action",
    ]

    for term in required_terms:
        assert term in workflow


def test_no_local_environment_files_are_tracked() -> None:
    tracked_files = subprocess.check_output(
        [
            "git",
            "ls-files",
        ],
        text=True,
    ).splitlines()

    forbidden_files = {
        ".env",
        ".env.local",
        "apps/web/.env.local",
    }

    assert forbidden_files.isdisjoint(
        set(
            tracked_files
        )
    )


def test_day29_observability_and_security_tests_exist() -> None:
    assert Path(
        "tests/observability/test_prometheus_metrics.py"
    ).exists()
    assert Path(
        "tests/security_hardening/test_security_review_and_policy.py"
    ).exists()