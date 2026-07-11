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
from apps.api.repositories.registry import (
    get_repository_registry,
)


def test_repository_registry_is_cached():
    get_repository_registry.cache_clear()

    first_registry = get_repository_registry()
    second_registry = get_repository_registry()

    assert first_registry is second_registry

    assert isinstance(
        first_registry.assets,
        JsonAssetRepository,
    )
    assert isinstance(
        first_registry.documents,
        JsonDocumentRepository,
    )
    assert isinstance(
        first_registry.work_orders,
        JsonWorkOrderRepository,
    )
    assert isinstance(
        first_registry.rca,
        JsonRcaRepository,
    )
    assert isinstance(
        first_registry.compliance,
        JsonComplianceRepository,
    )
    assert isinstance(
        first_registry.pid,
        JsonPidRepository,
    )


def test_json_asset_repository():
    repository = JsonAssetRepository()

    assets = repository.list_assets()
    asset = repository.get_asset_by_id(
        "p-101"
    )
    missing_asset = repository.get_asset_by_id(
        "UNKNOWN"
    )
    health_scores = (
        repository.list_health_scores()
    )

    assert len(assets) == 3
    assert asset is not None
    assert asset["asset_id"] == "P-101"
    assert asset["asset_name"] == (
        "Cooling Water Circulation Pump"
    )
    assert missing_asset is None
    assert len(health_scores) == 3


def test_json_document_repository():
    repository = JsonDocumentRepository()

    documents = repository.list_documents()
    document = repository.get_document_by_id(
        "COMP-001_Compliance_Checklist"
    )
    chunks = (
        repository.list_chunks_by_document_id(
            "COMP-001_Compliance_Checklist"
        )
    )
    document_text = repository.read_document_text(
        "COMP-001_Compliance_Checklist"
    )

    assert len(documents) == 19
    assert document is not None
    assert document["document_id"] == (
        "COMP-001_Compliance_Checklist"
    )
    assert len(chunks) > 0
    assert document_text.strip()
    assert (
        repository.get_document_by_id(
            "UNKNOWN"
        )
        is None
    )
    assert (
        repository.read_document_text(
            "UNKNOWN"
        )
        == ""
    )


def test_json_work_order_repository():
    repository = JsonWorkOrderRepository()

    work_orders = repository.list_work_orders()
    work_order = (
        repository.get_work_order_by_id(
            "mwo-p101-001"
        )
    )
    events = (
        repository.list_maintenance_events()
    )
    event = (
        repository.get_maintenance_event_by_id(
            "wo-1001"
        )
    )

    assert len(work_orders) == 9
    assert work_order is not None
    assert work_order["work_order_id"] == (
        "MWO-P101-001"
    )
    assert len(events) == 6
    assert event is not None
    assert event["event_id"] == "WO-1001"
    assert (
        repository.get_work_order_by_id(
            "UNKNOWN"
        )
        is None
    )
    assert (
        repository.get_maintenance_event_by_id(
            "UNKNOWN"
        )
        is None
    )


def test_json_rca_repository():
    repository = JsonRcaRepository()

    dataset = repository.get_dataset()
    cases = repository.list_cases()
    case = repository.get_case_by_id(
        "rca-p101-001"
    )
    asset_cases = (
        repository.list_cases_for_asset(
            "p-101"
        )
    )
    evidence = repository.get_evidence(
        "RCA-P101-001",
        "p101-ev-001",
    )

    assert dataset["case_count"] == 1
    assert len(cases) == 1
    assert case is not None
    assert case["case_id"] == (
        "RCA-P101-001"
    )
    assert len(asset_cases) == 1
    assert evidence is not None
    assert evidence["evidence_id"] == (
        "P101-EV-001"
    )
    assert (
        repository.get_case_by_id(
            "UNKNOWN"
        )
        is None
    )
    assert (
        repository.get_evidence(
            "RCA-P101-001",
            "UNKNOWN",
        )
        is None
    )


def test_json_compliance_repository():
    repository = JsonComplianceRepository()

    rules_data = repository.get_rules()
    matrix_data = repository.get_matrix()

    rules = rules_data.get("rules", [])
    gaps = matrix_data.get("gaps", [])
    asset_summaries = matrix_data.get(
        "asset_compliance_summary",
        [],
    )

    assert len(rules) == 8
    assert rules[0]["rule_id"] == "C001"
    assert len(gaps) == 5
    assert len(asset_summaries) == 3


def test_json_pid_repository():
    repository = JsonPidRepository()

    view = repository.get_view(
        "pid-001"
    )
    image_path = repository.get_image_path(
        "PID-001"
    )

    assert view is not None
    assert view["pid_id"] == "PID-001"
    assert image_path is not None
    assert image_path.is_file()
    assert image_path.name == (
        "PID-001_Demo_Process_Line.png"
    )
    assert (
        repository.get_view(
            "PID-999"
        )
        is None
    )
    assert (
        repository.get_image_path(
            "PID-999"
        )
        is None
    )