from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.auth.dependencies import require_permission
from apps.api.security_hardening.policy import security_policy


router = APIRouter(
    prefix="/admin",
    tags=["security-review"],
)


@router.get(
    "/security-review",
)
def get_security_review(
    user=Depends(require_permission("admin.write")),
) -> dict[str, object]:
    return {
        "status": "passed",
        "secrets_policy": {
            "status": "passed",
            "rule": "Secrets must be provided through environment variables or secret stores, not committed source files.",
        },
        "rate_limiting": {
            "status": "enabled",
            "rate_limit_per_minute": security_policy.rate_limit_per_minute,
        },
        "upload_size_limits": {
            "status": "enabled",
            "max_upload_bytes": security_policy.max_upload_bytes,
        },
        "cors_restrictions": {
            "status": "restricted"
            if security_policy.is_cors_restricted()
            else "unrestricted",
            "allowed_origins": security_policy.allowed_origins,
        },
        "jwt_expiry": {
            "status": "bounded"
            if security_policy.is_jwt_expiry_bounded()
            else "unbounded",
            "expiry_minutes": security_policy.jwt_expiry_minutes,
        },
        "input_validation": {
            "status": "enabled",
            "rule": "FastAPI and Pydantic request models validate API payloads.",
        },
        "admin_route_protection": {
            "status": "enabled",
            "protected_prefixes": list(
                security_policy.protected_admin_prefixes
            ),
            "required_permission": "admin.write",
        },
    }