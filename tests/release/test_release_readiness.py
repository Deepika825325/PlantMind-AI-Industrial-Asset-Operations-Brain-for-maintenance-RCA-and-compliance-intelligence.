from __future__ import annotations

from scripts.validate_release_readiness import validate_release_readiness


def test_release_readiness_validation_passes() -> None:
    failures = validate_release_readiness()

    assert failures == []