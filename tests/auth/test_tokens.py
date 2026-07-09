from datetime import timedelta

import pytest

from apps.api.auth.tokens import (
    TokenError,
    create_access_token,
    decode_token,
)


def test_access_token_round_trip(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "test-secret",
    )

    token = create_access_token(
        subject="user-1",
        email="user@example.com",
        role="administrator",
    )

    payload = decode_token(
        token,
        expected_type="access",
    )

    assert payload["sub"] == "user-1"
    assert payload["email"] == "user@example.com"
    assert payload["role"] == "administrator"
    assert payload["type"] == "access"


def test_invalid_token_is_rejected() -> None:
    with pytest.raises(TokenError):
        decode_token(
            "not-a-valid-token",
            expected_type="access",
        )


def test_expired_token_is_rejected() -> None:
    token = create_access_token(
        subject="user-1",
        email="user@example.com",
        role="administrator",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(TokenError):
        decode_token(
            token,
            expected_type="access",
        )
