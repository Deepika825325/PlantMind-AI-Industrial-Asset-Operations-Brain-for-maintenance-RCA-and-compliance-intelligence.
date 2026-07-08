from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


JsonObject = dict[str, Any]


class AssetRepository(Protocol):
    """Data-access contract for assets and asset health."""

    def list_assets(self) -> list[JsonObject]:
        ...

    def get_asset_by_id(
        self,
        asset_id: str,
    ) -> JsonObject | None:
        ...

    def list_health_scores(self) -> list[JsonObject]:
        ...


class DocumentRepository(Protocol):
    """Data-access contract for documents and document chunks."""

    def list_documents(self) -> list[JsonObject]:
        ...

    def get_document_by_id(
        self,
        document_id: str,
    ) -> JsonObject | None:
        ...

    def list_document_chunks(self) -> list[JsonObject]:
        ...

    def list_chunks_by_document_id(
        self,
        document_id: str,
    ) -> list[JsonObject]:
        ...

    def read_document_text(
        self,
        document_id: str,
    ) -> str:
        ...


class WorkOrderRepository(Protocol):
    """Data-access contract for work orders and legacy events."""

    def list_work_orders(self) -> list[JsonObject]:
        ...

    def get_work_order_by_id(
        self,
        work_order_id: str,
    ) -> JsonObject | None:
        ...

    def list_maintenance_events(self) -> list[JsonObject]:
        ...

    def get_maintenance_event_by_id(
        self,
        event_id: str,
    ) -> JsonObject | None:
        ...


class RcaRepository(Protocol):
    """Data-access contract for RCA cases and evidence."""

    def get_dataset(self) -> JsonObject:
        ...

    def list_cases(self) -> list[JsonObject]:
        ...

    def get_case_by_id(
        self,
        case_id: str,
    ) -> JsonObject | None:
        ...

    def list_cases_for_asset(
        self,
        asset_id: str,
    ) -> list[JsonObject]:
        ...

    def get_evidence(
        self,
        case_id: str,
        evidence_id: str,
    ) -> JsonObject | None:
        ...


class ComplianceRepository(Protocol):
    """Data-access contract for compliance rules and matrices."""

    def get_rules(self) -> JsonObject:
        ...

    def get_matrix(self) -> JsonObject:
        ...


class PidRepository(Protocol):
    """Data-access contract for P&ID metadata and image files."""

    def get_view(
        self,
        pid_id: str,
    ) -> JsonObject | None:
        ...

    def get_image_path(
        self,
        pid_id: str,
    ) -> Path | None:
        ...