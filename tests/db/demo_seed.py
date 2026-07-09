from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import delete
from sqlalchemy.orm import Session

from apps.api.db.models.asset import (
    Asset,
    Component,
    Sensor,
)
from apps.api.db.models.compliance import (
    ComplianceAssetSummary,
    ComplianceFinding,
    ComplianceRule,
)
from apps.api.db.models.dataset import (
    AssetHealthSnapshot,
    DatasetSnapshot,
)
from apps.api.db.models.documents import (
    Document,
    DocumentAssetLink,
    DocumentChunk,
)
from apps.api.db.models.operational import (
    Evidence,
    MaintenanceEvent,
    MaintenanceWorkOrder,
    RcaCase,
    RootCause,
)
from apps.api.db.models.organization import (
    Area,
    Plant,
    System,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_json(
    relative_path: str,
) -> dict[str, Any]:
    path = PROJECT_ROOT / relative_path

    return json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )


def _parse_datetime(
    value: str | None,
) -> datetime | None:
    if not value:
        return None

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def _parse_date(
    value: str | None,
) -> date | None:
    if not value:
        return None

    return date.fromisoformat(value)


def _decimal(
    value: Any,
) -> Decimal | None:
    if value is None:
        return None

    return Decimal(str(value))


def _metadata(
    data: dict[str, Any],
    *collection_keys: str,
) -> dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if key not in collection_keys
    }


def clear_demo_database(
    session: Session,
) -> None:
    """Clear only the isolated Day 5 test database."""

    # Important: previous failed inserts can leave the session
    # in a failed transaction state. Roll back first.
    session.rollback()

    models = [
        DocumentAssetLink,
        DocumentChunk,
        Evidence,
        RootCause,
        MaintenanceWorkOrder,
        MaintenanceEvent,
        RcaCase,
        ComplianceFinding,
        ComplianceAssetSummary,
        ComplianceRule,
        AssetHealthSnapshot,
        Document,
        Sensor,
        Component,
        Asset,
        System,
        Area,
        Plant,
        DatasetSnapshot,
    ]

    for model in models:
        session.execute(delete(model))

    session.commit()


def seed_demo_database(
    session: Session,
) -> None:
    clear_demo_database(session)

    assets_data = _load_json(
        "data/demo/assets.json"
    )
    health_data = _load_json(
        "data/demo/health_scores.json"
    )
    documents_data = _load_json(
        "data/demo/documents.json"
    )
    chunks_data = _load_json(
        "data/processed/document_chunks.json"
    )
    rca_data = _load_json(
        "data/demo/rca_cases.json"
    )
    work_orders_data = _load_json(
        "data/demo/maintenance_work_orders.json"
    )
    events_data = _load_json(
        "data/demo/maintenance_events.json"
    )
    rules_data = _load_json(
        "data/demo/compliance_rules.json"
    )
    matrix_data = _load_json(
        "data/demo/compliance_matrix.json"
    )

    snapshots = [
        (
            "rca_cases",
            _metadata(rca_data, "cases"),
        ),
        (
            "compliance_rules",
            _metadata(rules_data, "rules"),
        ),
        (
            "compliance_matrix",
            _metadata(
                matrix_data,
                "asset_compliance_summary",
                "gaps",
            ),
        ),
        (
            "documents",
            _metadata(
                documents_data,
                "documents",
            ),
        ),
        (
            "document_chunks",
            _metadata(
                chunks_data,
                "chunks",
            ),
        ),
        (
            "maintenance_work_orders",
            _metadata(
                work_orders_data,
                "work_orders",
            ),
        ),
        (
            "maintenance_events",
            _metadata(
                events_data,
                "events",
            ),
        ),
    ]

    session.add_all(
        [
            DatasetSnapshot(
                dataset_key=key,
                payload=payload,
            )
            for key, payload in snapshots
        ]
    )

    plant = Plant(
        plant_code="PLANT-DEMO-01",
        name="PlantMind Demo Plant",
    )

    session.add(plant)
    session.flush()

    area = Area(
        plant_id=plant.id,
        area_code="AREA-DEMO-01",
        name="PlantMind Demo Process Area",
    )

    session.add(area)
    session.flush()

    system = System(
        area_id=area.id,
        system_code="SYSTEM-DEMO-01",
        name="PlantMind Demo Process System",
    )

    session.add(system)
    session.flush()

    asset_map: dict[str, Asset] = {}

    for index, payload in enumerate(
        assets_data["assets"]
    ):
        asset = Asset(
            system_id=system.id,
            asset_code=payload["asset_id"],
            name=payload["asset_name"],
            asset_type=payload["asset_type"],
            status="active",
            risk_score=payload.get(
                "risk_score"
            ),
            health_score=payload.get(
                "health_score"
            ),
            source_order=index,
            payload=payload,
        )

        session.add(asset)
        session.flush()

        asset_map[
            payload["asset_id"]
        ] = asset

    for index, payload in enumerate(
        health_data["health_scores"]
    ):
        session.add(
            AssetHealthSnapshot(
                asset_id=asset_map[
                    payload["asset_id"]
                ].id,
                source_order=index,
                payload=payload,
            )
        )

    document_map: dict[str, Document] = {}

    for index, payload in enumerate(
        documents_data["documents"]
    ):
        document = Document(
            document_code=payload[
                "document_id"
            ],
            title=payload["title"],
            document_type=payload[
                "document_type"
            ],
            source_group=payload.get(
                "source_group"
            ),
            relative_path=payload.get(
                "relative_path"
            ),
            word_count=payload.get(
                "word_count",
                0,
            ),
            source_order=index,
            payload=payload,
        )

        session.add(document)
        session.flush()

        document_map[
            payload["document_id"]
        ] = document

        for asset_code in payload.get(
            "asset_ids",
            [],
        ):
            asset = asset_map.get(
                asset_code
            )

            if asset is not None:
                session.add(
                    DocumentAssetLink(
                        document_id=document.id,
                        asset_id=asset.id,
                    )
                )

    for index, payload in enumerate(
        chunks_data["chunks"]
    ):
        document = document_map.get(
            payload["document_id"]
        )

        if document is None:
            continue

        chunk_code = payload["chunk_id"]
        chunk_suffix = chunk_code.rsplit(
            "_",
            1,
        )[-1]

        try:
            chunk_index = int(
                chunk_suffix
            )
        except ValueError:
            chunk_index = index

        session.add(
            DocumentChunk(
                document_id=document.id,
                chunk_code=chunk_code,
                chunk_index=chunk_index,
                source_order=index,
                payload=payload,
                created_at=_parse_datetime(
                    payload.get(
                        "created_at"
                    )
                ),
            )
        )

    case_map: dict[str, RcaCase] = {}

    for case_index, payload in enumerate(
        rca_data["cases"]
    ):
        case = RcaCase(
            case_code=payload["case_id"],
            asset_id=asset_map[
                payload["asset_id"]
            ].id,
            title=payload["title"],
            incident_status=payload[
                "incident_status"
            ],
            severity=payload["severity"],
            detected_at=_parse_datetime(
                payload.get("detected_at")
            ),
            overall_confidence=_decimal(
                payload.get(
                    "overall_confidence"
                )
            ),
            source_order=case_index,
            payload=payload,
        )

        session.add(case)
        session.flush()

        case_map[
            payload["case_id"]
        ] = case

        for index, root_payload in enumerate(
            payload.get(
                "root_causes",
                [],
            )
        ):
            session.add(
                RootCause(
                    cause_code=root_payload[
                        "cause_id"
                    ],
                    rca_case_id=case.id,
                    rank=root_payload["rank"],
                    title=root_payload[
                        "title"
                    ],
                    category=root_payload.get(
                        "category"
                    ),
                    confidence=_decimal(
                        root_payload.get(
                            "confidence"
                        )
                    ),
                    source_order=index,
                    payload=root_payload,
                )
            )

        for index, evidence_payload in enumerate(
            payload.get(
                "evidence",
                [],
            )
        ):
            source_reference = (
                evidence_payload.get(
                    "document_id"
                )
            )

            document = document_map.get(
                str(source_reference)
            )

            session.add(
                Evidence(
                    evidence_code=(
                        evidence_payload[
                            "evidence_id"
                        ]
                    ),
                    rca_case_id=case.id,
                    document_id=(
                        document.id
                        if document
                        else None
                    ),
                    source_reference=(
                        str(source_reference)
                        if source_reference
                        else None
                    ),
                    document_type=(
                        evidence_payload.get(
                            "document_type"
                        )
                    ),
                    excerpt=(
                        evidence_payload.get(
                            "excerpt"
                        )
                    ),
                    source_order=index,
                    payload=evidence_payload,
                )
            )

    for index, payload in enumerate(
        work_orders_data["work_orders"]
    ):
        linked_case = case_map.get(
            payload.get(
                "linked_rca_case_id"
            )
        )

        session.add(
            MaintenanceWorkOrder(
                work_order_code=payload[
                    "work_order_id"
                ],
                asset_id=asset_map[
                    payload["asset_id"]
                ].id,
                rca_case_id=(
                    linked_case.id
                    if linked_case
                    else None
                ),
                title=payload["title"],
                description=payload.get(
                    "description"
                ),
                maintenance_type=payload[
                    "maintenance_type"
                ],
                priority=payload["priority"],
                status=payload["status"],
                due_at=_parse_datetime(
                    payload.get("due_at")
                ),
                owner_role=payload.get(
                    "owner_role"
                ),
                risk_score=payload.get(
                    "risk_score"
                ),
                confidence=_decimal(
                    payload.get(
                        "confidence"
                    )
                ),
                source_order=index,
                payload=payload,
                created_at=_parse_datetime(
                    payload.get(
                        "created_at"
                    )
                ),
            )
        )

    for index, payload in enumerate(
        events_data["events"]
    ):
        asset = asset_map.get(
            payload.get("asset_id")
        )

        session.add(
            MaintenanceEvent(
                event_code=payload[
                    "event_id"
                ],
                asset_id=(
                    asset.id
                    if asset
                    else None
                ),
                event_type=payload[
                    "event_type"
                ],
                priority=payload.get(
                    "priority"
                ),
                status=payload.get(
                    "status"
                ),
                created_on=_parse_date(
                    payload.get(
                        "created_date"
                    )
                ),
                due_on=_parse_date(
                    payload.get(
                        "due_date"
                    )
                ),
                source_order=index,
                payload=payload,
            )
        )

    for index, payload in enumerate(
        rules_data["rules"]
    ):
        session.add(
            ComplianceRule(
                rule_code=payload[
                    "rule_id"
                ],
                name=payload[
                    "rule_name"
                ],
                description=payload.get(
                    "description"
                ),
                default_severity=payload[
                    "default_severity"
                ],
                evaluation_type=payload[
                    "evaluation_type"
                ],
                source_order=index,
                payload=payload,
            )
        )

    for index, payload in enumerate(
        matrix_data[
            "asset_compliance_summary"
        ]
    ):
        session.add(
            ComplianceAssetSummary(
                asset_id=asset_map[
                    payload["asset_id"]
                ].id,
                source_order=index,
                payload=payload,
            )
        )

    for index, payload in enumerate(
        matrix_data["gaps"]
    ):
        session.add(
            ComplianceFinding(
                finding_code=payload[
                    "gap_id"
                ],
                asset_id=asset_map[
                    payload["asset_id"]
                ].id,
                rule_id=None,
                requirement=payload[
                    "requirement"
                ],
                current_status=payload[
                    "current_status"
                ],
                severity=payload[
                    "gap_severity"
                ],
                source_order=index,
                payload=payload,
            )
        )

    session.commit()