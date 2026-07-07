from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.services.evidence_integrity_service import (
    UNSUPPORTED_ANSWER,
)


client = TestClient(app)

VALID_STATUSES = {
    "Verified",
    "Partially verified",
    "Unavailable",
}

VALID_QUALITY_RATINGS = {
    "High",
    "Medium-High",
    "Medium",
    "Derived",
}


def assert_decision_trace(
    payload: dict,
    expected_supported: bool = True,
) -> dict:
    assert "decision_trace" in payload

    trace = payload["decision_trace"]

    assert isinstance(trace, dict)
    assert trace["supported"] is expected_supported
    assert isinstance(trace["answer"], str)
    assert trace["answer"].strip()

    confidence = trace["confidence"]

    assert isinstance(
        confidence,
        (
            int,
            float,
        ),
    )
    assert 0 <= confidence <= 1

    explanation = trace[
        "confidence_explanation"
    ]

    assert isinstance(explanation, dict)
    assert 0 <= explanation["score"] <= 1
    assert 0 <= explanation["percentage"] <= 100
    assert isinstance(
        explanation["label"],
        str,
    )
    assert isinstance(
        explanation["why"],
        list,
    )
    assert isinstance(
        explanation["verified_source_count"],
        int,
    )
    assert isinstance(
        explanation["partial_source_count"],
        int,
    )
    assert isinstance(
        explanation["independent_source_count"],
        int,
    )
    assert isinstance(
        explanation["conflict_count"],
        int,
    )
    assert isinstance(
        explanation["missing_evidence_count"],
        int,
    )

    list_fields = [
        "evidence_used",
        "evidence_not_found",
        "reasoning_summary",
        "rules_applied",
        "conflicting_evidence",
    ]

    for field in list_fields:
        assert isinstance(
            trace[field],
            list,
        )

    assert (
        trace["recommended_action"]
        is None
        or isinstance(
            trace["recommended_action"],
            str,
        )
    )

    assert (
        trace["verification_method"]
        is None
        or isinstance(
            trace["verification_method"],
            str,
        )
    )

    for citation in trace[
        "evidence_used"
    ]:
        assert citation[
            "validation_status"
        ] in VALID_STATUSES

        assert citation[
            "evidence_excerpt"
        ].strip()

        validation_details = citation[
            "validation_details"
        ]

        required_validation_fields = [
            "reference_exists",
            "evidence_id_exists",
            "referenced_section_exists",
            "excerpt_not_empty",
            "asset_matches",
            "physical_file_exists",
        ]

        for field in required_validation_fields:
            assert field in validation_details

        source_quality = citation[
            "source_quality"
        ]

        assert isinstance(
            source_quality["label"],
            str,
        )

        assert source_quality[
            "rating"
        ] in VALID_QUALITY_RATINGS

    return trace


def test_unsupported_answer_constant():
    assert UNSUPPORTED_ANSWER == (
        "PlantMind could not find sufficient "
        "evidence to support a reliable conclusion."
    )


def test_ask_returns_supported_decision_trace():
    response = client.post(
        "/ask",
        json={
            "question": (
                "What is the likely root cause "
                "of P-101 vibration?"
            ),
            "asset_id": "P-101",
            "top_k": 5,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    trace = assert_decision_trace(
        payload
    )

    assert trace["evidence_used"]
    assert trace["reasoning_summary"]
    assert trace["rules_applied"]
    assert payload["supported"] is True


def test_rca_returns_verified_decision_trace():
    response = client.get(
        "/rca/RCA-P101-001"
    )

    assert response.status_code == 200

    payload = response.json()

    trace = assert_decision_trace(
        payload
    )

    assert payload["case_id"] == (
        "RCA-P101-001"
    )
    assert payload["asset_id"] == "P-101"
    assert len(trace["evidence_used"]) >= 3

    assert all(
        citation["validation_status"]
        == "Verified"
        for citation in trace[
            "evidence_used"
        ]
    )


def test_compliance_returns_evidence_aware_trace():
    response = client.get(
        "/compliance/assets/"
        "P-101/audit-package"
    )

    assert response.status_code == 200

    payload = response.json()

    trace = assert_decision_trace(
        payload
    )

    assert payload["asset"]["asset_id"] == (
        "P-101"
    )
    assert trace["evidence_used"]
    assert trace["evidence_not_found"]
    assert trace["rules_applied"]

    assert all(
        citation["validation_status"]
        == "Verified"
        for citation in trace[
            "evidence_used"
        ]
    )


def test_maintenance_returns_enriched_detail():
    response = client.get(
        "/maintenance/work-orders/"
        "MWO-P101-004"
    )

    assert response.status_code == 200

    payload = response.json()

    trace = assert_decision_trace(
        payload
    )

    assert payload["work_order_id"] == (
        "MWO-P101-004"
    )
    assert payload["asset_id"] == "P-101"
    assert trace["evidence_used"]
    assert trace["recommended_action"]
    assert trace["verification_method"]


def test_unknown_rca_case_returns_404():
    response = client.get(
        "/rca/RCA-UNKNOWN-999"
    )

    assert response.status_code == 404


def test_unknown_work_order_returns_404():
    response = client.get(
        "/maintenance/work-orders/"
        "MWO-UNKNOWN-999"
    )

    assert response.status_code == 404
