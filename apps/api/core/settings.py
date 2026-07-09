from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal


DataMode = Literal[
    "demo",
    "postgres",
]


@dataclass(frozen=True, slots=True)
class Settings:
    data_mode: DataMode
    auth_required: bool = False
    jwt_secret_key: str = (
        "plantmind-development-secret-change-me"
    )
    jwt_issuer: str = "plantmind-api"
    access_token_minutes: int = 30
    refresh_token_days: int = 7
    dev_auth_email: str = "admin@plantmind.local"
    dev_auth_password: str = "plantmind-admin"
    dev_auth_full_name: str = "PlantMind Administrator"
    dev_auth_role: str = "administrator"


def _env_bool(
    name: str,
    default: bool,
) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }


def _env_int(
    name: str,
    default: int,
) -> int:
    value = os.getenv(name)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError as error:
        raise RuntimeError(
            f"{name} must be an integer."
        ) from error


def get_settings() -> Settings:
    """Read and normalize PlantMind runtime settings."""

    raw_mode = os.getenv(
        "PLANTMIND_DATA_BACKEND",
        "json",
    ).strip().lower()

    if raw_mode in {
        "json",
        "demo",
    }:
        data_mode: DataMode = "demo"
    elif raw_mode in {
        "postgres",
        "postgresql",
        "database",
        "db",
    }:
        data_mode = "postgres"
    else:
        raise RuntimeError(
            "Unsupported PLANTMIND_DATA_BACKEND: "
            f"{raw_mode!r}. Expected json/demo "
            "or postgres/database."
        )

    return Settings(
        data_mode=data_mode,
        auth_required=_env_bool(
            "AUTH_REQUIRED",
            False,
        ),
        jwt_secret_key=os.getenv(
            "JWT_SECRET_KEY",
            "plantmind-development-secret-change-me",
        ),
        jwt_issuer=os.getenv(
            "JWT_ISSUER",
            "plantmind-api",
        ),
        access_token_minutes=_env_int(
            "JWT_ACCESS_TOKEN_MINUTES",
            30,
        ),
        refresh_token_days=_env_int(
            "JWT_REFRESH_TOKEN_DAYS",
            7,
        ),
        dev_auth_email=os.getenv(
            "DEMO_AUTH_EMAIL",
            "admin@plantmind.local",
        ),
        dev_auth_password=os.getenv(
            "DEMO_AUTH_PASSWORD",
            "plantmind-admin",
        ),
        dev_auth_full_name=os.getenv(
            "DEMO_AUTH_FULL_NAME",
            "PlantMind Administrator",
        ),
        dev_auth_role=os.getenv(
            "DEMO_AUTH_ROLE",
            "administrator",
        ),
    )
