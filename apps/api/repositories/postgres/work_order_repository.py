from __future__ import annotations

from sqlalchemy import func, select

from apps.api.db.models.operational import (
    MaintenanceEvent,
    MaintenanceWorkOrder,
)
from apps.api.repositories.postgres.base import (
    JsonObject,
    PostgresRepositoryBase,
    clone_payload,
)


class PostgresWorkOrderRepository(
    PostgresRepositoryBase,
):
    """PostgreSQL work-order and event repository."""

    def list_work_orders(
        self,
    ) -> list[JsonObject]:
        with self._session_factory() as session:
            work_orders = session.scalars(
                select(MaintenanceWorkOrder)
                .where(
                    MaintenanceWorkOrder
                    .deleted_at.is_(None)
                )
                .order_by(
                    MaintenanceWorkOrder.source_order,
                    MaintenanceWorkOrder
                    .work_order_code,
                )
            ).all()

            return [
                clone_payload(work_order.payload)
                for work_order in work_orders
            ]

    def get_work_order_by_id(
        self,
        work_order_id: str,
    ) -> JsonObject | None:
        with self._session_factory() as session:
            work_order = session.scalar(
                select(MaintenanceWorkOrder)
                .where(
                    func.upper(
                        MaintenanceWorkOrder
                        .work_order_code
                    )
                    == work_order_id.upper(),
                    MaintenanceWorkOrder
                    .deleted_at.is_(None),
                )
            )

            if work_order is None:
                return None

            return clone_payload(
                work_order.payload
            )

    def list_maintenance_events(
        self,
    ) -> list[JsonObject]:
        with self._session_factory() as session:
            events = session.scalars(
                select(MaintenanceEvent)
                .where(
                    MaintenanceEvent
                    .deleted_at.is_(None)
                )
                .order_by(
                    MaintenanceEvent.source_order,
                    MaintenanceEvent.event_code,
                )
            ).all()

            return [
                clone_payload(event.payload)
                for event in events
            ]

    def get_maintenance_event_by_id(
        self,
        event_id: str,
    ) -> JsonObject | None:
        with self._session_factory() as session:
            event = session.scalar(
                select(MaintenanceEvent)
                .where(
                    func.upper(
                        MaintenanceEvent.event_code
                    )
                    == event_id.upper(),
                    MaintenanceEvent
                    .deleted_at.is_(None),
                )
            )

            if event is None:
                return None

            return clone_payload(event.payload)