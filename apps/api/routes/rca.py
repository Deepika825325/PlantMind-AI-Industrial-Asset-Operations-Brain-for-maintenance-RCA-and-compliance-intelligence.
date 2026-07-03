from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from apps.api.services.rca_service import (
    get_rca_case,
    get_rca_cases_for_asset,
    get_rca_evidence,
    get_rca_statistics,
    list_rca_cases,
)


router = APIRouter(
    prefix="/rca",
    tags=["Root Cause Analysis"],
)


def handle_service_error(error: Exception) -> None:
    if isinstance(error, FileNotFoundError):
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    if isinstance(error, ValueError):
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    raise HTTPException(
        status_code=500,
        detail="Unexpected RCA service error",
    ) from error


@router.get("")
def get_rca_cases(
    asset_id: str | None = Query(
        default=None,
        description="Filter RCA cases by asset ID",
    ),
    severity: str | None = Query(
        default=None,
        description="Filter RCA cases by severity",
    ),
    incident_status: str | None = Query(
        default=None,
        description="Filter RCA cases by incident status",
    ),
) -> dict[str, Any]:
    try:
        return list_rca_cases(
            asset_id=asset_id,
            severity=severity,
            incident_status=incident_status,
        )
    except Exception as error:
        handle_service_error(error)
        raise


@router.get("/statistics")
def get_statistics() -> dict[str, Any]:
    try:
        return get_rca_statistics()
    except Exception as error:
        handle_service_error(error)
        raise


@router.get("/asset/{asset_id}")
def get_cases_for_asset(
    asset_id: str,
) -> dict[str, Any]:
    try:
        cases = get_rca_cases_for_asset(asset_id)

        return {
            "asset_id": asset_id.upper(),
            "case_count": len(cases),
            "cases": cases,
        }
    except Exception as error:
        handle_service_error(error)
        raise


@router.get("/{case_id}")
def get_case(
    case_id: str,
) -> dict[str, Any]:
    try:
        case = get_rca_case(case_id)

        if case is None:
            raise HTTPException(
                status_code=404,
                detail=f"RCA case not found: {case_id}",
            )

        return case
    except HTTPException:
        raise
    except Exception as error:
        handle_service_error(error)
        raise


@router.get("/{case_id}/evidence/{evidence_id}")
def get_case_evidence(
    case_id: str,
    evidence_id: str,
) -> dict[str, Any]:
    try:
        case = get_rca_case(case_id)

        if case is None:
            raise HTTPException(
                status_code=404,
                detail=f"RCA case not found: {case_id}",
            )

        evidence = get_rca_evidence(
            case_id=case_id,
            evidence_id=evidence_id,
        )

        if evidence is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Evidence not found: {evidence_id} "
                    f"for RCA case {case_id}"
                ),
            )

        return {
            "case_id": case_id,
            "asset_id": case.get("asset_id"),
            "evidence": evidence,
        }
    except HTTPException:
        raise
    except Exception as error:
        handle_service_error(error)
        raise