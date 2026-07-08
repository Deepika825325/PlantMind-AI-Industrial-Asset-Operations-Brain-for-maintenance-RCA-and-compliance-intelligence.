from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

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


@dataclass(frozen=True, slots=True)
class RepositoryRegistry:
    """Collection of repositories used by PlantMind services."""

    assets: AssetRepository
    documents: DocumentRepository
    work_orders: WorkOrderRepository
    rca: RcaRepository
    compliance: ComplianceRepository
    pid: PidRepository


@lru_cache(maxsize=1)
def get_repository_registry() -> RepositoryRegistry:
    """Return the repository registry for the active data mode."""

    return RepositoryRegistry(
        assets=JsonAssetRepository(),
        documents=JsonDocumentRepository(),
        work_orders=JsonWorkOrderRepository(),
        rca=JsonRcaRepository(),
        compliance=JsonComplianceRepository(),
        pid=JsonPidRepository(),
    )