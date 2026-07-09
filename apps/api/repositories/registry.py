from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from apps.api.core.settings import (
    DataMode,
    get_settings,
)
from apps.api.repositories.base import (
    AssetRepository,
    ComplianceRepository,
    DocumentRepository,
    PidRepository,
    RcaRepository,
    WorkOrderRepository,
)
from apps.api.repositories.json.asset_repository import (
    JsonAssetRepository,
)
from apps.api.repositories.json.compliance_repository import (
    JsonComplianceRepository,
)
from apps.api.repositories.json.document_repository import (
    JsonDocumentRepository,
)
from apps.api.repositories.json.pid_repository import (
    JsonPidRepository,
)
from apps.api.repositories.json.rca_repository import (
    JsonRcaRepository,
)
from apps.api.repositories.json.work_order_repository import (
    JsonWorkOrderRepository,
)
from apps.api.repositories.postgres import (
    PostgresAssetRepository,
    PostgresComplianceRepository,
    PostgresDocumentRepository,
    PostgresRcaRepository,
    PostgresWorkOrderRepository,
)


@dataclass(frozen=True, slots=True)
class RepositoryRegistry:
    """Repositories active for the selected data mode."""

    mode: DataMode
    assets: AssetRepository
    documents: DocumentRepository
    work_orders: WorkOrderRepository
    rca: RcaRepository
    compliance: ComplianceRepository
    pid: PidRepository


def _build_demo_registry() -> RepositoryRegistry:
    return RepositoryRegistry(
        mode="demo",
        assets=JsonAssetRepository(),
        documents=JsonDocumentRepository(),
        work_orders=JsonWorkOrderRepository(),
        rca=JsonRcaRepository(),
        compliance=JsonComplianceRepository(),
        pid=JsonPidRepository(),
    )


def _build_postgres_registry() -> RepositoryRegistry:
    return RepositoryRegistry(
        mode="postgres",
        assets=PostgresAssetRepository(),
        documents=PostgresDocumentRepository(),
        work_orders=PostgresWorkOrderRepository(),
        rca=PostgresRcaRepository(),
        compliance=PostgresComplianceRepository(),

        # P&ID persistence is outside Day 5.
        pid=JsonPidRepository(),
    )


@lru_cache(maxsize=1)
def get_repository_registry() -> RepositoryRegistry:
    settings = get_settings()

    if settings.data_mode == "demo":
        return _build_demo_registry()

    return _build_postgres_registry()