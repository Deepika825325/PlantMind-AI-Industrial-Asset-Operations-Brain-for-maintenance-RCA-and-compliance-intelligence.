from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from apps.api.auth.password import (
    hash_password,
    verify_password,
)
from apps.api.core.settings import (
    get_settings,
)


@dataclass(frozen=True, slots=True)
class UserRecord:
    user_id: str
    email: str
    full_name: str
    role: str
    password_hash: str
    is_active: bool = True


DEVELOPMENT_USERS: dict[str, UserRecord] = {}


def _normalize_email(
    email: str,
) -> str:
    return email.strip().lower()


def ensure_default_development_user() -> None:
    settings = get_settings()
    email = _normalize_email(
        settings.dev_auth_email
    )

    if email in DEVELOPMENT_USERS:
        return

    DEVELOPMENT_USERS[email] = UserRecord(
        user_id="dev-admin",
        email=email,
        full_name=settings.dev_auth_full_name,
        role=settings.dev_auth_role,
        password_hash=hash_password(
            settings.dev_auth_password
        ),
        is_active=True,
    )


def create_development_user(
    *,
    email: str,
    password: str,
    full_name: str,
    role: str,
) -> UserRecord:
    ensure_default_development_user()

    normalized_email = _normalize_email(email)

    if normalized_email in DEVELOPMENT_USERS:
        raise ValueError(
            "A development user with this email already exists."
        )

    user_id = (
        "dev-"
        + normalized_email.replace(
            "@",
            "-at-",
        ).replace(
            ".",
            "-",
        )
    )

    user = UserRecord(
        user_id=user_id,
        email=normalized_email,
        full_name=full_name.strip(),
        role=role.strip().lower(),
        password_hash=hash_password(password),
        is_active=True,
    )

    DEVELOPMENT_USERS[normalized_email] = user

    return user


def get_user_by_email(
    email: str,
) -> UserRecord | None:
    ensure_default_development_user()

    return DEVELOPMENT_USERS.get(
        _normalize_email(email)
    )


def authenticate_user(
    *,
    email: str,
    password: str,
) -> UserRecord | None:
    user = get_user_by_email(email)

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def public_user(
    user: UserRecord,
) -> dict[str, Any]:
    payload = asdict(user)
    payload.pop(
        "password_hash",
        None,
    )

    return payload
