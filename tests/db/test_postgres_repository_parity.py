from __future__ import annotations

import os

import pytest
from sqlalchemy import (
    create_engine,
    func,
    select,
)
from sqlalchemy.orm import sessionmaker

from apps.api.db.models.asset import Asset
from apps.api.db.models.documents import (
    DocumentAssetLink,
)
from apps.api.db.models.operational import (
    Evidence,
    MaintenanceWorkOrder,
    RcaCase,
    RootCause,
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
from apps.api.repositories.json.rca_repository import (
    JsonRcaRepository,
)
from apps.api.repositories.json.work_order_repository import (
    JsonWorkOrderRepository,
)
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
from tests.db.demo_seed import (
    seed_demo_database,
)


@pytest.fixture(scope="module")
def postgres_factory():
    database_url = os.getenv(
        "TEST_DATABASE_URL"
    )

    if not database_url:
        pytest.skip(
            "TEST_DATABASE_URL is not set."
        )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    factory = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    with factory() as session:
        seed_demo_database(session)

    yield factory

    engine.dispose()


def test_asset_repository_parity(
    postgres_factory,
) -> None:
    json_repository = JsonAssetRepository()
    postgres_repository = (
        PostgresAssetRepository(
            postgres_factory
        )
    )

    assert (
        postgres_repository.list_assets()
        == json_repository.list_assets()
    )

    assert (
        postgres_repository.get_asset_by_id(
            "P-101"
        )
        == json_repository.get_asset_by_id(
            "P-101"
        )
    )

    assert (
        postgres_repository
        .list_health_scores()
        == json_repository
        .list_health_scores()
    )


def test_document_repository_parity(
    postgres_factory,
) -> None:
    json_repository = JsonDocumentRepository()
    postgres_repository = (
        PostgresDocumentRepository(
            postgres_factory
        )
    )

    document_id = (
        "IR-P101-001_"
        "Pump_Vibration_Inspection"
    )

    assert (
        postgres_repository.list_documents()
        == json_repository.list_documents()
    )

    assert (
        postgres_repository.get_document_by_id(
            document_id
        )
        == json_repository.get_document_by_id(
            document_id
        )
    )

    assert (
        postgres_repository
        .list_document_chunks()
        == json_repository
        .list_document_chunks()
    )

    assert (
        postgres_repository
        .list_chunks_by_document_id(
            document_id
        )
        == json_repository
        .list_chunks_by_document_id(
            document_id
        )
    )

    assert (
        postgres_repository
        .read_document_text(document_id)
        == json_repository
        .read_document_text(document_id)
    )


def test_work_order_repository_parity(
    postgres_factory,
) -> None:
    json_repository = (
        JsonWorkOrderRepository()
    )
    postgres_repository = (
        PostgresWorkOrderRepository(
            postgres_factory
        )
    )

    assert (
        postgres_repository
        .list_work_orders()
        == json_repository
        .list_work_orders()
    )

    assert (
        postgres_repository
        .get_work_order_by_id(
            "MWO-P101-001"
        )
        == json_repository
        .get_work_order_by_id(
            "MWO-P101-001"
        )
    )

    assert (
        postgres_repository
        .list_maintenance_events()
        == json_repository
        .list_maintenance_events()
    )


def test_rca_repository_parity(
    postgres_factory,
) -> None:
    json_repository = JsonRcaRepository()
    postgres_repository = (
        PostgresRcaRepository(
            postgres_factory
        )
    )

    assert (
        postgres_repository.get_dataset()
        == json_repository.get_dataset()
    )

    assert (
        postgres_repository.get_case_by_id(
            "RCA-P101-001"
        )
        == json_repository.get_case_by_id(
            "RCA-P101-001"
        )
    )

    assert (
        postgres_repository
        .list_cases_for_asset("P-101")
        == json_repository
        .list_cases_for_asset("P-101")
    )

    assert (
        postgres_repository.get_evidence(
            "RCA-P101-001",
            "P101-EV-001",
        )
        == json_repository.get_evidence(
            "RCA-P101-001",
            "P101-EV-001",
        )
    )


def test_compliance_repository_parity(
    postgres_factory,
) -> None:
    json_repository = (
        JsonComplianceRepository()
    )
    postgres_repository = (
        PostgresComplianceRepository(
            postgres_factory
        )
    )

    assert (
        postgres_repository.get_rules()
        == json_repository.get_rules()
    )

    assert (
        postgres_repository.get_matrix()
        == json_repository.get_matrix()
    )


def test_p101_relationship_integrity(
    postgres_factory,
) -> None:
    with postgres_factory() as session:
        asset = session.scalar(
            select(Asset).where(
                Asset.asset_code == "P-101"
            )
        )

        assert asset is not None

        case = session.scalar(
            select(RcaCase).where(
                RcaCase.case_code
                == "RCA-P101-001"
            )
        )

        assert case is not None
        assert case.asset_id == asset.id

        root_cause_count = session.scalar(
            select(func.count())
            .select_from(RootCause)
            .where(
                RootCause.rca_case_id
                == case.id
            )
        )

        evidence_count = session.scalar(
            select(func.count())
            .select_from(Evidence)
            .where(
                Evidence.rca_case_id
                == case.id
            )
        )

        work_order_count = session.scalar(
            select(func.count())
            .select_from(
                MaintenanceWorkOrder
            )
            .where(
                MaintenanceWorkOrder
                .rca_case_id
                == case.id
            )
        )

        document_link_count = (
            session.scalar(
                select(func.count())
                .select_from(
                    DocumentAssetLink
                )
                .where(
                    DocumentAssetLink.asset_id
                    == asset.id
                )
            )
        )

        assert root_cause_count == 3
        assert evidence_count == 4
        assert work_order_count == 4
        assert document_link_count > 0