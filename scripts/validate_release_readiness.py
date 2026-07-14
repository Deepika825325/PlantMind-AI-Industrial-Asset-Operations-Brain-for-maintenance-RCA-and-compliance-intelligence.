from __future__ import annotations

from pathlib import Path


REQUIRED_DOCS = [
    Path("docs/DEPLOYMENT.md"),
    Path("docs/architecture.md"),
    Path("docs/SECURITY.md"),
    Path("docs/MODEL_CARD.md"),
    Path("docs/DATA_CARD.md"),
    Path("docs/demo_script.md"),
    Path("docs/LIMITATIONS.md"),
]

REQUIRED_FRONTEND_ROUTES = [
    Path("apps/web/app/demo/p101-closed-loop"),
    Path("apps/web/app/asset-health"),
    Path("apps/web/app/incidents"),
    Path("apps/web/app/rca-orchestration"),
    Path("apps/web/app/work-order-lifecycle"),
    Path("apps/web/app/post-maintenance-verification"),
    Path("apps/web/app/compliance-audit-package"),
    Path("apps/web/app/model-registry"),
]

REQUIRED_BACKEND_FILES = [
    Path("apps/api/routes/observability.py"),
    Path("apps/api/routes/security_review.py"),
    Path("apps/api/routes/model_registry.py"),
    Path("apps/api/routes/compliance_evidence_package.py"),
    Path("apps/api/observability/metrics.py"),
    Path("apps/api/security_hardening/policy.py"),
    Path("data/demo/model_registry.json"),
]

REQUIRED_TEST_FILES = [
    Path("tests/observability/test_prometheus_metrics.py"),
    Path("tests/security_hardening/test_security_review_and_policy.py"),
    Path("tests/security_hardening/test_ci_and_secret_policy.py"),
    Path("tests/model_registry/test_model_registry_service_and_api.py"),
]


def validate_release_readiness() -> list[str]:
    failures: list[str] = []

    for path in REQUIRED_DOCS:
        if not path.exists():
            failures.append(
                f"Missing release document: {path}"
            )
            continue

        if path.stat().st_size < 200:
            failures.append(
                f"Release document is too small: {path}"
            )

    for path in REQUIRED_FRONTEND_ROUTES:
        if not path.exists():
            failures.append(
                f"Missing frontend route: {path}"
            )

    for path in REQUIRED_BACKEND_FILES:
        if not path.exists():
            failures.append(
                f"Missing backend release file: {path}"
            )

    for path in REQUIRED_TEST_FILES:
        if not path.exists():
            failures.append(
                f"Missing release test file: {path}"
            )

    workflow = Path(
        ".github/workflows/plantmind-ci.yml"
    )

    if not workflow.exists():
        failures.append(
            "Missing GitHub Actions workflow."
        )
    else:
        workflow_text = workflow.read_text(
            encoding="utf-8"
        )
        for term in [
            "python -m pytest -q",
            "npm run lint",
            "npm run build",
            "docker compose --env-file .env.example build",
            "gitleaks/gitleaks-action",
        ]:
            if term not in workflow_text:
                failures.append(
                    f"CI workflow missing required check: {term}"
                )

    compose_file = Path(
        "docker-compose.yml"
    )

    compose_alt_file = Path(
        "compose.yaml"
    )

    if not compose_file.exists() and not compose_alt_file.exists():
        failures.append(
            "Missing Docker Compose file."
        )

    return failures


def main() -> None:
    failures = validate_release_readiness()

    if failures:
        print("PlantMind Nexus release readiness failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("PlantMind Nexus release readiness passed.")
    print("Validated:")
    print("- Final release documentation")
    print("- Frontend demo routes")
    print("- Backend release endpoints")
    print("- Observability and security controls")
    print("- CI/CD workflow")
    print("- Model registry artifacts")
    print("- Compliance audit package artifacts")


if __name__ == "__main__":
    main()
