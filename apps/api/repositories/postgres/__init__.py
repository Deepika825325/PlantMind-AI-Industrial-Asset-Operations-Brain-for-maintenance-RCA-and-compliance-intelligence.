from apps.api.repositories.postgres.asset_repository import (
    PostgresAssetRepository,
)
from apps.api.repositories.postgres.compliance_repository import (
    PostgresComplianceRepository,
)
from apps.api.repositories.postgres.document_repository import (
    PostgresDocumentRepository,
)
from apps.api.repositories.postgres.rca_repository import (
    PostgresRcaRepository,
)
from apps.api.repositories.postgres.work_order_repository import (
    PostgresWorkOrderRepository,
)


__all__ = [
    "PostgresAssetRepository",
    "PostgresComplianceRepository",
    "PostgresDocumentRepository",
    "PostgresRcaRepository",
    "PostgresWorkOrderRepository",
]