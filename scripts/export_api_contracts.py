from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from fastapi.testclient import TestClient

from apps.api.main import app


OUTPUT_DIR = PROJECT_ROOT / "contracts" / "api"

EXCLUDED_PREFIXES = (
    "/docs",
    "/redoc",
    "/openapi.json",
)

METHODS_TO_EXPORT = {
    "GET",
}


def safe_filename(
    method: str,
    path: str,
) -> str:
    normalized = path.strip("/") or "root"
    normalized = normalized.replace("/", "__")
    normalized = re.sub(
        r"[^A-Za-z0-9_.-]+",
        "_",
        normalized,
    )

    return f"{method.lower()}__{normalized}.json"


def is_exportable_route(
    path: str,
    methods: set[str],
) -> bool:
    if any(
        path.startswith(prefix)
        for prefix in EXCLUDED_PREFIXES
    ):
        return False

    if "{" in path or "}" in path:
        return False

    return bool(
        METHODS_TO_EXPORT.intersection(methods)
    )


def normalize_body(
    response_body: Any,
) -> Any:
    if isinstance(response_body, dict):
        response_body.pop(
            "reset_at",
            None,
        )
        response_body.pop(
            "audit_id",
            None,
        )
        response_body.pop(
            "created_at",
            None,
        )

    return response_body


def export_contracts() -> list[dict[str, Any]]:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    client = TestClient(app)

    manifest: list[dict[str, Any]] = []

    for route in app.routes:
        path = getattr(
            route,
            "path",
            "",
        )
        methods = set(
            getattr(
                route,
                "methods",
                set(),
            )
        )

        if not is_exportable_route(
            path,
            methods,
        ):
            continue

        for method in sorted(
            METHODS_TO_EXPORT.intersection(methods)
        ):
            response = client.request(
                method,
                path,
                headers={
                    "X-Request-ID": (
                        f"contract-{method.lower()}-"
                        f"{path.strip('/').replace('/', '-') or 'root'}"
                    ),
                },
            )

            try:
                body = response.json()
            except ValueError:
                body = response.text

            output_path = OUTPUT_DIR / safe_filename(
                method,
                path,
            )

            contract = {
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "request_id": response.headers.get(
                    "X-Request-ID"
                ),
                "body": normalize_body(body),
            }

            output_path.write_text(
                json.dumps(
                    contract,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            manifest.append(
                {
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "fixture": str(
                        output_path.relative_to(
                            PROJECT_ROOT
                        )
                    ).replace(
                        "\\",
                        "/",
                    ),
                }
            )

    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return manifest


if __name__ == "__main__":
    exported = export_contracts()

    print(
        f"Exported {len(exported)} API contract fixtures."
    )