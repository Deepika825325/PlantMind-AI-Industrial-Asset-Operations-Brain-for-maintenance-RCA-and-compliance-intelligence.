import type {
  ReactNode,
} from "react";

import {
  frontendHasPermission,
} from "@/lib/rbac";

type PermissionGateProps = {
  role: string;
  permission: string;
  children: ReactNode;
  fallback?: ReactNode;
};

export default function PermissionGate({
  role,
  permission,
  children,
  fallback = null,
}: PermissionGateProps) {
  if (
    frontendHasPermission(
      role,
      permission
    )
  ) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
}