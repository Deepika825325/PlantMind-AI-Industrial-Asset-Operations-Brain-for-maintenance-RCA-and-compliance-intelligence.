from __future__ import annotations


class Role:
    PLANT_MANAGER = "plant_manager"
    RELIABILITY_ENGINEER = "reliability_engineer"
    MAINTENANCE_ENGINEER = "maintenance_engineer"
    TECHNICIAN = "technician"
    SAFETY_OFFICER = "safety_officer"
    DATA_SCIENTIST = "data_scientist"
    ADMINISTRATOR = "administrator"
    AUDITOR = "auditor"


class Permission:
    SYSTEM_ADMIN = "system.admin"

    ADMIN_RESET_DEMO = "admin.reset_demo"
    ADMIN_RELOAD_CACHE = "admin.reload_cache"

    ASSET_READ = "asset.read"
    DOCUMENT_READ = "document.read"

    EVIDENCE_READ = "evidence.read"
    EVIDENCE_WRITE = "evidence.write"

    RCA_READ = "rca.read"
    RCA_APPROVE = "rca.approve"

    WORK_ORDER_READ = "work_order.read"
    WORK_ORDER_COMPLETE = "work_order.complete"
    WORK_ORDER_APPROVE_HIGH_PRIORITY = (
        "work_order.approve_high_priority"
    )

    COMPLIANCE_READ = "compliance.read"
    COMPLIANCE_APPROVE = "compliance.approve"

    MODEL_READ = "model.read"


READ_ONLY_PERMISSIONS = {
    Permission.ASSET_READ,
    Permission.DOCUMENT_READ,
    Permission.EVIDENCE_READ,
    Permission.RCA_READ,
    Permission.WORK_ORDER_READ,
    Permission.COMPLIANCE_READ,
}

ALL_PERMISSIONS = {
    value
    for key, value in Permission.__dict__.items()
    if key.isupper()
    and isinstance(value, str)
}

ROLE_ALIASES = {
    "plant manager": Role.PLANT_MANAGER,
    "plant-manager": Role.PLANT_MANAGER,
    "plant_manager": Role.PLANT_MANAGER,
    "reliability engineer": Role.RELIABILITY_ENGINEER,
    "reliability-engineer": Role.RELIABILITY_ENGINEER,
    "reliability_engineer": Role.RELIABILITY_ENGINEER,
    "maintenance engineer": Role.MAINTENANCE_ENGINEER,
    "maintenance-engineer": Role.MAINTENANCE_ENGINEER,
    "maintenance_engineer": Role.MAINTENANCE_ENGINEER,
    "maintenance manager": Role.MAINTENANCE_ENGINEER,
    "maintenance-manager": Role.MAINTENANCE_ENGINEER,
    "maintenance_manager": Role.MAINTENANCE_ENGINEER,
    "technician": Role.TECHNICIAN,
    "safety officer": Role.SAFETY_OFFICER,
    "safety-officer": Role.SAFETY_OFFICER,
    "safety_officer": Role.SAFETY_OFFICER,
    "data scientist": Role.DATA_SCIENTIST,
    "data-scientist": Role.DATA_SCIENTIST,
    "data_scientist": Role.DATA_SCIENTIST,
    "administrator": Role.ADMINISTRATOR,
    "admin": Role.ADMINISTRATOR,
    "auditor": Role.AUDITOR,
}


ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.ADMINISTRATOR: set(ALL_PERMISSIONS),

    Role.PLANT_MANAGER: {
        *READ_ONLY_PERMISSIONS,
        Permission.RCA_APPROVE,
        Permission.WORK_ORDER_APPROVE_HIGH_PRIORITY,
        Permission.COMPLIANCE_APPROVE,
    },

    Role.RELIABILITY_ENGINEER: {
        *READ_ONLY_PERMISSIONS,
        Permission.EVIDENCE_WRITE,
        Permission.RCA_APPROVE,
    },

    Role.MAINTENANCE_ENGINEER: {
        Permission.ASSET_READ,
        Permission.DOCUMENT_READ,
        Permission.EVIDENCE_READ,
        Permission.RCA_READ,
        Permission.WORK_ORDER_READ,
        Permission.WORK_ORDER_COMPLETE,
        Permission.WORK_ORDER_APPROVE_HIGH_PRIORITY,
        Permission.COMPLIANCE_READ,
    },

    Role.TECHNICIAN: {
        Permission.ASSET_READ,
        Permission.DOCUMENT_READ,
        Permission.EVIDENCE_READ,
        Permission.RCA_READ,
        Permission.WORK_ORDER_READ,
        Permission.WORK_ORDER_COMPLETE,
        Permission.COMPLIANCE_READ,
    },

    Role.SAFETY_OFFICER: {
        Permission.ASSET_READ,
        Permission.DOCUMENT_READ,
        Permission.EVIDENCE_READ,
        Permission.EVIDENCE_WRITE,
        Permission.RCA_READ,
        Permission.WORK_ORDER_READ,
        Permission.COMPLIANCE_READ,
        Permission.COMPLIANCE_APPROVE,
    },

    Role.DATA_SCIENTIST: {
        Permission.ASSET_READ,
        Permission.DOCUMENT_READ,
        Permission.EVIDENCE_READ,
        Permission.RCA_READ,
        Permission.WORK_ORDER_READ,
        Permission.COMPLIANCE_READ,
        Permission.MODEL_READ,
    },

    Role.AUDITOR: set(READ_ONLY_PERMISSIONS),
}


def normalize_role(
    role: str,
) -> str:
    normalized = (
        role.strip()
        .lower()
        .replace("-", "_")
    )

    return ROLE_ALIASES.get(
        normalized,
        normalized,
    )


def get_permissions_for_role(
    role: str,
) -> set[str]:
    normalized_role = normalize_role(role)

    return set(
        ROLE_PERMISSIONS.get(
            normalized_role,
            set(),
        )
    )


def has_permission(
    role: str,
    permission: str,
) -> bool:
    permissions = get_permissions_for_role(role)

    return (
        Permission.SYSTEM_ADMIN in permissions
        or permission in permissions
    )


def user_has_permission(
    user: dict,
    permission: str,
) -> bool:
    return has_permission(
        str(user.get("role", "")),
        permission,
    )
