from contextvars import ContextVar, Token


_request_id_context: ContextVar[str | None] = ContextVar(
    "plantmind_request_id",
    default=None,
)


def set_request_id(
    request_id: str,
) -> Token:
    return _request_id_context.set(
        request_id
    )


def reset_request_id(
    token: Token,
) -> None:
    _request_id_context.reset(
        token
    )


def get_request_id() -> str | None:
    return _request_id_context.get()
