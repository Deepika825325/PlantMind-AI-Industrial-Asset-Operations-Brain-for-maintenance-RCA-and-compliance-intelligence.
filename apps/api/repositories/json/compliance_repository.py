from __future__ import annotations

from typing import Any

from apps.api.repositories.json.data_source import load_demo_json


class JsonComplianceRepository:
    """JSON-backed repository for compliance data."""

    def get_rules(self) -> dict[str, Any]:
        return load_demo_json("compliance_rules.json")

    def get_matrix(self) -> dict[str, Any]:
        return load_demo_json("compliance_matrix.json")