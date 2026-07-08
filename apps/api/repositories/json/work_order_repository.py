from __future__ import annotations

from typing import Any

from apps.api.repositories.json.data_source import load_demo_json


class JsonWorkOrderRepository:
    """JSON-backed repository for work orders and maintenance events."""

    def list_work_orders(self) -> list[dict[str, Any]]:
        data = load_demo_json("maintenance_work_orders.json")
        return data.get("work_orders", [])

    def get_work_order_by_id(
        self,
        work_order_id: str,
    ) -> dict[str, Any] | None:
        normalized_work_order_id = work_order_id.upper()

        for work_order in self.list_work_orders():
            if (
                work_order.get("work_order_id", "").upper()
                == normalized_work_order_id
            ):
                return work_order

        return None

    def list_maintenance_events(self) -> list[dict[str, Any]]:
        data = load_demo_json("maintenance_events.json")
        return data.get("events", [])

    def get_maintenance_event_by_id(
        self,
        event_id: str,
    ) -> dict[str, Any] | None:
        normalized_event_id = event_id.upper()

        for event in self.list_maintenance_events():
            if (
                event.get("event_id", "").upper()
                == normalized_event_id
            ):
                return event

        return None
    