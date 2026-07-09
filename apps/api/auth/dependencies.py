from __future__ import annotations

from typing import Annotated, Any

from fastapi import Header, HTTPException, status

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
