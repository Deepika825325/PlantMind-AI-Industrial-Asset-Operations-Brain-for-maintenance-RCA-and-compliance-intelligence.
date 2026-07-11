from __future__ import annotations

from typing import Any

from apps.api.repositories.json.data_source import load_demo_json


class JsonAssetRepository:
    """JSON-backed repository for assets and health scores."""

    def list_assets(self) -> list[dict[str, Any]]:
        data = load_demo_json("assets.json")
        return data.get("assets", [])

    def get_asset_by_id(
        self,
        asset_id: str,
    ) -> dict[str, Any] | None:
        normalized_asset_id = asset_id.upper()

        for asset in self.list_assets():
            if (
                asset.get("asset_id", "").upper()
                == normalized_asset_id
            ):
                return asset

        return None

    def list_health_scores(self) -> list[dict[str, Any]]:
        data = load_demo_json("health_scores.json")
        return data.get("health_scores", [])