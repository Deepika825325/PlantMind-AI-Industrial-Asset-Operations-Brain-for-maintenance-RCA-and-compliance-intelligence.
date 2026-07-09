from __future__ import annotations

import base64
import hashlib
import hmac
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from apps.api.core.settings import (
    get_settings,
)


class TokenError(ValueError):
    """Raised when token verification fails."""


REVOKED_TOKEN_IDS: set[str] = set()


def _base64url_encode(
    raw: bytes,
) -> str:
    return (
        base64.urlsafe_b64encode(raw)
        .rstrip(b"=")
        .decode("ascii")
    )


def _base64url_decode(
    value: str,
) -> bytes:
    padding = "=" * (-len(value) % 4)

    return base64.urlsafe_b64decode(
        value + padding
    )


def _json_encode(
    payload: dict[str, Any],
) -> bytes:
    return json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _sign(
    signing_input: str,
    secret: str,
) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()

    return _base64url_encode(digest)


def create_token(
    *,
    subject: str,
    email: str,
    role: str,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta

    header = {
        "alg": "HS256",
        "typ": "JWT",
    }
    payload = {
        "iss": settings.jwt_issuer,
        "sub": subject,
        "email": email,
        "role": role,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": str(uuid.uuid4()),
    }

    encoded_header = _base64url_encode(
        _json_encode(header)
    )
    encoded_payload = _base64url_encode(
        _json_encode(payload)
    )

    signing_input = (
        f"{encoded_header}.{encoded_payload}"
    )
    signature = _sign(
        signing_input,
        settings.jwt_secret_key,
    )

    return (
        f"{signing_input}.{signature}"
    )


def create_access_token(
    *,
    subject: str,
    email: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()

    return create_token(
        subject=subject,
        email=email,
        role=role,
        token_type="access",
        expires_delta=(
            expires_delta
            or timedelta(
                minutes=settings.access_token_minutes
            )
        ),
    )


def create_refresh_token(
    *,
    subject: str,
    email: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()

    return create_token(
        subject=subject,
        email=email,
        role=role,
        token_type="refresh",
        expires_delta=(
            expires_delta
            or timedelta(
                days=settings.refresh_token_days
            )
        ),
    )


def decode_token(
    token: str,
    *,
    expected_type: str | None = None,
    verify_revocation: bool = True,
) -> dict[str, Any]:
    settings = get_settings()

    try:
        encoded_header, encoded_payload, signature = (
            token.split(".")
        )
    except ValueError as error:
        raise TokenError(
            "Token must contain three JWT segments."
        ) from error

    signing_input = (
        f"{encoded_header}.{encoded_payload}"
    )
    expected_signature = _sign(
        signing_input,
        settings.jwt_secret_key,
    )

    if not hmac.compare_digest(
        signature,
        expected_signature,
    ):
        raise TokenError(
            "Token signature is invalid."
        )

    try:
        header = json.loads(
            _base64url_decode(
                encoded_header
            )
        )
        payload = json.loads(
            _base64url_decode(
                encoded_payload
            )
        )
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
        ValueError,
    ) as error:
        raise TokenError(
            "Token payload is invalid."
        ) from error

    if header.get("alg") != "HS256":
        raise TokenError(
            "Unsupported token algorithm."
        )

    if payload.get("iss") != settings.jwt_issuer:
        raise TokenError(
            "Token issuer is invalid."
        )

    now = int(
        datetime.now(timezone.utc).timestamp()
    )

    if int(payload.get("exp", 0)) <= now:
        raise TokenError(
            "Token has expired."
        )

    if expected_type and payload.get("type") != expected_type:
        raise TokenError(
            "Token type is invalid."
        )

    if (
        verify_revocation
        and payload.get("jti") in REVOKED_TOKEN_IDS
    ):
        raise TokenError(
            "Token has been revoked."
        )

    return payload


def revoke_token(
    token: str,
) -> dict[str, Any]:
    payload = decode_token(
        token,
        verify_revocation=False,
    )

    token_id = payload.get("jti")

    if token_id:
        REVOKED_TOKEN_IDS.add(
            str(token_id)
        )

    return payload
