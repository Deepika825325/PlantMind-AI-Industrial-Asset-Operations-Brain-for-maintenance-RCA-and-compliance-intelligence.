from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[4]
RCA_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "demo"
    / "rca_cases.json"
)


def _normalize(value: str | None) -> str:
    return str(value or "").strip().lower()


class JsonRcaRepository:
    """JSON-backed repository for RCA cases and evidence."""

    def get_dataset(self) -> dict[str, Any]:
        if not RCA_DATA_PATH.exists():
            raise FileNotFoundError(
                f"RCA dataset was not found: {RCA_DATA_PATH}"
            )

        try:
            with RCA_DATA_PATH.open(
                "r",
                encoding="utf-8-sig",
            ) as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"RCA dataset contains invalid JSON: {exc}"
            ) from exc

        cases = data.get("cases")

        if not isinstance(cases, list):
            raise ValueError(
                "RCA dataset must contain a 'cases' array"
            )

        declared_count = data.get("case_count")

        if (
            declared_count is not None
            and declared_count != len(cases)
        ):
            raise ValueError(
                "RCA case_count does not match "
                "the number of cases"
            )

        return data

    def list_cases(self) -> list[dict[str, Any]]:
        return self.get_dataset()["cases"]

    def get_case_by_id(
        self,
        case_id: str,
    ) -> dict[str, Any] | None:
        normalized_case_id = _normalize(case_id)

        for case in self.list_cases():
            if (
                _normalize(case.get("case_id"))
                == normalized_case_id
            ):
                return case

        return None

    def list_cases_for_asset(
        self,
        asset_id: str,
    ) -> list[dict[str, Any]]:
        normalized_asset_id = _normalize(asset_id)

        matching_cases = [
            case
            for case in self.list_cases()
            if (
                _normalize(case.get("asset_id"))
                == normalized_asset_id
            )
        ]

        matching_cases.sort(
            key=lambda item: item.get(
                "detected_at",
                "",
            ),
            reverse=True,
        )

        return matching_cases

    def get_evidence(
        self,
        case_id: str,
        evidence_id: str,
    ) -> dict[str, Any] | None:
        case = self.get_case_by_id(case_id)

        if case is None:
            return None

        normalized_evidence_id = _normalize(
            evidence_id
        )

        for evidence in case.get("evidence", []):
            if (
                _normalize(
                    evidence.get("evidence_id")
                )
                == normalized_evidence_id
            ):
                return evidence

        return None