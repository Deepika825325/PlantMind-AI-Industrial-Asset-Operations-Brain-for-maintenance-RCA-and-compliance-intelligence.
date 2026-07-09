from apps.api.auth.password import (
    hash_password,
    verify_password,
)


def test_bcrypt_password_hashing_round_trip() -> None:
    password_hash = hash_password(
        "strong-password"
    )

    assert password_hash != "strong-password"
    assert verify_password(
        "strong-password",
        password_hash,
    )
    assert not verify_password(
        "wrong-password",
        password_hash,
    )
