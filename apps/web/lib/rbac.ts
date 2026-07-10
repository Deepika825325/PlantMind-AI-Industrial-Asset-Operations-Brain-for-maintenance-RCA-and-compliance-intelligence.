export const FrontendPermission = {
  ADMIN_RESET_DEMO: "admin.reset_demo",
  ADMIN_RELOAD_CACHE: "admin.reload_cache",
  EVIDENCE_READ: "evidence.read",
  EVIDENCE_WRITE: "evidence.write",
  RCA_APPROVE: "rca.approve",
  WORK_ORDER_COMPLETE: "work_order.complete",
  WORK_ORDER_APPROVE_HIGH_PRIORITY:
    "work_order.approve_high_priority",
  COMPLIANCE_APPROVE: "compliance.approve",
} as const;

export const FrontendRole = {
  PLANT_MANAGER: "plant_manager",
  RELIABILITY_ENGINEER: "reliability_engineer",
  MAINTENANCE_ENGINEER: "maintenance_engineer",
  TECHNICIAN: "technician",
  SAFETY_OFFICER: "safety_officer",
  DATA_SCIENTIST: "data_scientist",
  ADMINISTRATOR: "administrator",
  AUDITOR: "auditor",
} as const;

const readOnlyPermissions = [
  "asset.read",
  "document.read",
  FrontendPermission.EVIDENCE_READ,
  "rca.read",
  "work_order.read",
  "compliance.read",
];

const allPermissions = [
  ...readOnlyPermissions,
  FrontendPermission.ADMIN_RESET_DEMO,
  FrontendPermission.ADMIN_RELOAD_CACHE,
  FrontendPermission.EVIDENCE_WRITE,
  FrontendPermission.RCA_APPROVE,
  FrontendPermission.WORK_ORDER_COMPLETE,
  FrontendPermission.WORK_ORDER_APPROVE_HIGH_PRIORITY,
  FrontendPermission.COMPLIANCE_APPROVE,
  "model.read",
];

const rolePermissions: Record<string, string[]> = {
  [FrontendRole.ADMINISTRATOR]: allPermissions,

  [FrontendRole.PLANT_MANAGER]: [
    ...readOnlyPermissions,
    FrontendPermission.RCA_APPROVE,
    FrontendPermission.WORK_ORDER_APPROVE_HIGH_PRIORITY,
    FrontendPermission.COMPLIANCE_APPROVE,
  ],

  [FrontendRole.RELIABILITY_ENGINEER]: [
    ...readOnlyPermissions,
    FrontendPermission.EVIDENCE_WRITE,
    FrontendPermission.RCA_APPROVE,
  ],

  [FrontendRole.MAINTENANCE_ENGINEER]: [
    ...readOnlyPermissions,
    FrontendPermission.WORK_ORDER_COMPLETE,
    FrontendPermission.WORK_ORDER_APPROVE_HIGH_PRIORITY,
  ],

  [FrontendRole.TECHNICIAN]: [
    ...readOnlyPermissions,
    FrontendPermission.WORK_ORDER_COMPLETE,
  ],

  [FrontendRole.SAFETY_OFFICER]: [
    ...readOnlyPermissions,
    FrontendPermission.EVIDENCE_WRITE,
    FrontendPermission.COMPLIANCE_APPROVE,
  ],

  [FrontendRole.DATA_SCIENTIST]: [
    ...readOnlyPermissions,
    "model.read",
  ],

  [FrontendRole.AUDITOR]: readOnlyPermissions,
};

const roleAliases: Record<string, string> = {
  admin: FrontendRole.ADMINISTRATOR,
  administrator: FrontendRole.ADMINISTRATOR,
  auditor: FrontendRole.AUDITOR,
  technician: FrontendRole.TECHNICIAN,
  "plant manager": FrontendRole.PLANT_MANAGER,
  plant_manager: FrontendRole.PLANT_MANAGER,
  "reliability engineer":
    FrontendRole.RELIABILITY_ENGINEER,
  reliability_engineer:
    FrontendRole.RELIABILITY_ENGINEER,
  "maintenance engineer":
    FrontendRole.MAINTENANCE_ENGINEER,
  "maintenance manager":
    FrontendRole.MAINTENANCE_ENGINEER,
  maintenance_engineer:
    FrontendRole.MAINTENANCE_ENGINEER,
  maintenance_manager:
    FrontendRole.MAINTENANCE_ENGINEER,
  "safety officer": FrontendRole.SAFETY_OFFICER,
  safety_officer: FrontendRole.SAFETY_OFFICER,
  "data scientist": FrontendRole.DATA_SCIENTIST,
  data_scientist: FrontendRole.DATA_SCIENTIST,
};

export type FrontendAction = {
  label: string;
  permission: string;
  area: string;
  description: string;
};

export const frontendActions: FrontendAction[] = [
  {
    label: "Reset Demo",
    permission: FrontendPermission.ADMIN_RESET_DEMO,
    area: "Administration",
    description:
      "Restore the deterministic PlantMind demo state.",
  },
  {
    label: "Reload Cache",
    permission: FrontendPermission.ADMIN_RELOAD_CACHE,
    area: "Administration",
    description:
      "Clear runtime data cache and revalidate source data.",
  },
  {
    label: "Complete Work Order",
    permission: FrontendPermission.WORK_ORDER_COMPLETE,
    area: "Maintenance",
    description:
      "Move a maintenance work order to completed state.",
  },
  {
    label: "Approve High-Priority Work Order",
    permission:
      FrontendPermission.WORK_ORDER_APPROVE_HIGH_PRIORITY,
    area: "Maintenance",
    description:
      "Approve execution for high-risk maintenance work.",
  },
  {
    label: "Approve RCA",
    permission: FrontendPermission.RCA_APPROVE,
    area: "RCA",
    description:
      "Approve a root-cause analysis decision.",
  },
  {
    label: "Write Evidence",
    permission: FrontendPermission.EVIDENCE_WRITE,
    area: "Evidence",
    description:
      "Upload or update decision evidence.",
  },
  {
    label: "Approve Compliance Resolution",
    permission: FrontendPermission.COMPLIANCE_APPROVE,
    area: "Compliance",
    description:
      "Approve closure of a compliance gap.",
  },
];

export function normalizeFrontendRole(
  role: string
): string {
  const normalized = role
    .trim()
    .toLowerCase()
    .replaceAll("-", "_");

  return roleAliases[normalized] ?? normalized;
}

export function getFrontendPermissionsForRole(
  role: string
): string[] {
  const normalizedRole = normalizeFrontendRole(role);

  return rolePermissions[normalizedRole] ?? [];
}

export function frontendHasPermission(
  role: string,
  permission: string
): boolean {
  return getFrontendPermissionsForRole(
    role
  ).includes(permission);
}