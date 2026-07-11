from __future__ import annotations

from typing import Annotated, Any, Callable

from fastapi import (
    Depends,
    Header,
    HTTPException,
    status,
)

from apps.api.audit.service import (
    actor_from_user,
    record_audit_event,
)
from apps.api.auth.rbac import (
    user_has_permission,
)
from apps.api.auth.tokens import (
    TokenError,
    decode_token,
)
from apps.api.auth.users import (
    get_user_by_email,
    public_user,
)
from apps.api.core.settings import (
    get_settings,
)


def extract_bearer_token(
    authorization: str | None,
) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must use Bearer token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return token


def get_current_user(
    authorization: Annotated[
        str | None,
        Header(alias="Authorization"),
    ] = None,
) -> dict[str, Any]:
    token = extract_bearer_token(
        authorization
    )

    try:
        payload = decode_token(
            token,
            expected_type="access",
        )
    except TokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error

    email = str(
        payload.get("email", "")
    )

    user = get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return public_user(user)


def get_optional_current_user(
    authorization: Annotated[
        str | None,
        Header(alias="Authorization"),
    ] = None,
) -> dict[str, Any] | None:
    if not authorization:
        return None

    return get_current_user(
        authorization
    )


def _record_permission_audit(
    *,
    permission: str,
    outcome: str,
    current_user: dict[str, Any] | None,
    reason: str,
    auth_required: bool = True,
) -> None:
    record_audit_event(
        action=permission,
        entity_type="authorization",
        outcome=outcome,
        actor=actor_from_user(
            current_user
        ),
        reason=reason,
        metadata={
            "permission": permission,
            "auth_required": auth_required,
            "role": (
                current_user or {}
            ).get("role"),
        },
    )


def _raise_forbidden(
    permission: str,
    current_user: dict[str, Any],
) -> None:
    _record_permission_audit(
        permission=permission,
        outcome="denied",
        current_user=current_user,
        reason="User role does not have the required permission.",
    )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "User role is not allowed to perform "
            f"this action: {permission}"
        ),
    )


def require_permission(
    permission: str,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def dependency(
        current_user: dict[str, Any] = Depends(
            get_current_user
        ),
    ) -> dict[str, Any]:
        if not user_has_permission(
            current_user,
            permission,
        ):
            _raise_forbidden(
                permission,
                current_user,
            )

        _record_permission_audit(
            permission=permission,
            outcome="allowed",
            current_user=current_user,
            reason="User role has the required permission.",
        )

        return current_user

    return dependency


def require_auth_if_enabled(
    authorization: Annotated[
        str | None,
        Header(alias="Authorization"),
    ] = None,
) -> dict[str, Any] | None:
    settings = get_settings()

    if not settings.auth_required:
        return None

    return get_current_user(
        authorization
    )


def require_permission_if_auth_enabled(
    permission: str,
) -> Callable[[str | None], dict[str, Any] | None]:
    def dependency(
        authorization: Annotated[
            str | None,
            Header(alias="Authorization"),
        ] = None,
    ) -> dict[str, Any] | None:
        settings = get_settings()

        if not settings.auth_required:
            _record_permission_audit(
                permission=permission,
                outcome="skipped_auth_not_required",
                current_user=None,
                reason=(
                    "AUTH_REQUIRED is false; permission "
                    "check was skipped."
                ),
                auth_required=False,
            )

            return None

        current_user = get_current_user(
            authorization
        )

        if not user_has_permission(
            current_user,
            permission,
        ):
            _raise_forbidden(
                permission,
                current_user,
            )

        _record_permission_audit(
            permission=permission,
            outcome="allowed",
            current_user=current_user,
            reason="User role has the required permission.",
            auth_required=True,
        )

        return current_user

    return dependency
