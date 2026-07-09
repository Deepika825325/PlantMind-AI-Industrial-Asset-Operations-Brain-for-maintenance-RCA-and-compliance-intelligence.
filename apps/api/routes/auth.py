from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)

from apps.api.auth.dependencies import (
    extract_bearer_token,
    get_current_user,
    require_permission,
)
from apps.api.auth.rbac import (
    Permission,
    get_permissions_for_role,
)
from apps.api.auth.schemas import (
    LoginRequest,
    LogoutResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from apps.api.auth.tokens import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    revoke_token,
)
from apps.api.auth.users import (
    authenticate_user,
    create_development_user,
    get_user_by_email,
    public_user,
)
from apps.api.core.settings import (
    get_settings,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def _build_token_response(
    user_payload: dict,
) -> TokenResponse:
    settings = get_settings()

    access_token = create_access_token(
        subject=user_payload["user_id"],
        email=user_payload["email"],
        role=user_payload["role"],
    )
    refresh_token = create_refresh_token(
        subject=user_payload["user_id"],
        email=user_payload["email"],
        role=user_payload["role"],
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=(
            settings.access_token_minutes
            * 60
        ),
        user=UserResponse(**user_payload),
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register_development_user(
    request: RegisterRequest,
) -> dict:
    try:
        user = create_development_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=request.role,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return {
        "status": "registered",
        "user": public_user(user),
    }


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
) -> TokenResponse:
    user = authenticate_user(
        email=request.email,
        password=request.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return _build_token_response(
        public_user(user)
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    request: RefreshRequest,
) -> TokenResponse:
    try:
        payload = decode_token(
            request.refresh_token,
            expected_type="refresh",
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
            detail="Refresh token user no longer exists.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return _build_token_response(
        public_user(user)
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
)
def logout(
    authorization: Annotated[
        str | None,
        Header(alias="Authorization"),
    ] = None,
) -> LogoutResponse:
    token = extract_bearer_token(
        authorization
    )

    try:
        payload = revoke_token(token)
    except TokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error

    return LogoutResponse(
        status="logged_out",
        token_id=payload.get("jti"),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user: dict = Depends(
        get_current_user
    ),
) -> UserResponse:
    return UserResponse(
        **current_user
    )


@router.get(
    "/protected-test",
)
def protected_test(
    current_user: dict = Depends(
        get_current_user
    ),
) -> dict:
    return {
        "status": "authenticated",
        "user": current_user,
    }


@router.get(
    "/permissions/me",
)
def my_permissions(
    current_user: dict = Depends(
        get_current_user
    ),
) -> dict:
    permissions = sorted(
        get_permissions_for_role(
            str(current_user.get("role", ""))
        )
    )

    return {
        "user": current_user,
        "role": current_user.get("role"),
        "permissions": permissions,
    }


@router.post(
    "/rbac-check/work-orders/complete",
)
def rbac_complete_work_order(
    current_user: dict = Depends(
        require_permission(
            Permission.WORK_ORDER_COMPLETE
        )
    ),
) -> dict:
    return {
        "status": "allowed",
        "action": Permission.WORK_ORDER_COMPLETE,
        "user": current_user,
    }


@router.post(
    "/rbac-check/work-orders/approve-high-priority",
)
def rbac_approve_high_priority_work_order(
    current_user: dict = Depends(
        require_permission(
            Permission.WORK_ORDER_APPROVE_HIGH_PRIORITY
        )
    ),
) -> dict:
    return {
        "status": "allowed",
        "action": (
            Permission.WORK_ORDER_APPROVE_HIGH_PRIORITY
        ),
        "user": current_user,
    }


@router.post(
    "/rbac-check/rca/approve",
)
def rbac_approve_rca(
    current_user: dict = Depends(
        require_permission(
            Permission.RCA_APPROVE
        )
    ),
) -> dict:
    return {
        "status": "allowed",
        "action": Permission.RCA_APPROVE,
        "user": current_user,
    }


@router.get(
    "/rbac-check/evidence/read",
)
def rbac_read_evidence(
    current_user: dict = Depends(
        require_permission(
            Permission.EVIDENCE_READ
        )
    ),
) -> dict:
    return {
        "status": "allowed",
        "action": Permission.EVIDENCE_READ,
        "user": current_user,
    }


@router.post(
    "/rbac-check/admin/reset-demo",
)
def rbac_reset_demo(
    current_user: dict = Depends(
        require_permission(
            Permission.ADMIN_RESET_DEMO
        )
    ),
) -> dict:
    return {
        "status": "allowed",
        "action": Permission.ADMIN_RESET_DEMO,
        "user": current_user,
    }
