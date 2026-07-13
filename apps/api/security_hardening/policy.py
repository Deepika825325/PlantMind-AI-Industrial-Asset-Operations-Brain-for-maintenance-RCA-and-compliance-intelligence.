from __future__ import annotations

import os
from dataclasses import dataclass, field


DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

DEFAULT_MAX_UPLOAD_BYTES = 10 * 1024 * 1024
DEFAULT_RATE_LIMIT_PER_MINUTE = 600
DEFAULT_JWT_EXPIRY_MINUTES = 60


@dataclass(frozen=True)
class SecurityPolicy:
    allowed_origins: list[str] = field(
        default_factory=list
    )
    max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES
    rate_limit_per_minute: int = DEFAULT_RATE_LIMIT_PER_MINUTE
    jwt_expiry_minutes: int = DEFAULT_JWT_EXPIRY_MINUTES
    protected_admin_prefixes: tuple[str, ...] = (
        "/admin",
    )

    def is_cors_restricted(
        self,
    ) -> bool:
        return "*" not in self.allowed_origins

    def is_upload_allowed(
        self,
        content_length: int | None,
    ) -> bool:
        if content_length is None:
            return True

        return content_length <= self.max_upload_bytes

    def is_jwt_expiry_bounded(
        self,
    ) -> bool:
        return 0 < self.jwt_expiry_minutes <= 120

    def is_admin_path(
        self,
        path: str,
    ) -> bool:
        return any(
            path.startswith(
                prefix
            )
            for prefix in self.protected_admin_prefixes
        )

    def security_headers(
        self,
    ) -> dict[str, str]:
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        }


def load_security_policy_from_environment() -> SecurityPolicy:
    allowed_origins_raw = os.getenv(
        "PLANTMIND_ALLOWED_ORIGINS",
        ",".join(
            DEFAULT_ALLOWED_ORIGINS
        ),
    )

    allowed_origins = [
        origin.strip()
        for origin in allowed_origins_raw.split(
            ","
        )
        if origin.strip()
    ]

    return SecurityPolicy(
        allowed_origins=allowed_origins,
        max_upload_bytes=_int_from_env(
            "PLANTMIND_MAX_UPLOAD_BYTES",
            DEFAULT_MAX_UPLOAD_BYTES,
        ),
        rate_limit_per_minute=_int_from_env(
            "PLANTMIND_RATE_LIMIT_PER_MINUTE",
            DEFAULT_RATE_LIMIT_PER_MINUTE,
        ),
        jwt_expiry_minutes=_int_from_env(
            "PLANTMIND_JWT_EXPIRY_MINUTES",
            DEFAULT_JWT_EXPIRY_MINUTES,
        ),
    )


def _int_from_env(
    key: str,
    default: int,
) -> int:
    value = os.getenv(
        key
    )

    if value is None:
        return default

    try:
        return int(
            value
        )
    except ValueError:
        return default


security_policy = load_security_policy_from_environment()