import Link from "next/link";

import PermissionGate from "@/components/auth/PermissionGate";
import {
  FrontendRole,
  frontendActions,
  frontendHasPermission,
  getFrontendPermissionsForRole,
  normalizeFrontendRole,
} from "@/lib/rbac";

export const dynamic = "force-dynamic";

type RbacPageProps = {
  searchParams?: Promise<{
    role?: string | string[];
  }>;
};

const roles = [
  FrontendRole.ADMINISTRATOR,
  FrontendRole.PLANT_MANAGER,
  FrontendRole.RELIABILITY_ENGINEER,
  FrontendRole.MAINTENANCE_ENGINEER,
  FrontendRole.TECHNICIAN,
  FrontendRole.SAFETY_OFFICER,
  FrontendRole.DATA_SCIENTIST,
  FrontendRole.AUDITOR,
];

function getRoleLabel(role: string): string {
  return role
    .split("_")
    .map(
      (part) =>
        part.charAt(0).toUpperCase() +
        part.slice(1)
    )
    .join(" ");
}

export default async function RbacPage({
  searchParams,
}: RbacPageProps) {
  const params = searchParams
    ? await searchParams
    : {};

  const rawRole = Array.isArray(params.role)
    ? params.role[0]
    : params.role;

  const selectedRole = normalizeFrontendRole(
    rawRole || FrontendRole.AUDITOR
  );

  const visibleActions = frontendActions.filter(
    (action) =>
      frontendHasPermission(
        selectedRole,
        action.permission
      )
  );

  const hiddenActions = frontendActions.filter(
    (action) =>
      !frontendHasPermission(
        selectedRole,
        action.permission
      )
  );

  const permissions =
    getFrontendPermissionsForRole(selectedRole);

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-slate-100 sm:px-6">
      <section className="mx-auto max-w-7xl">
        <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
          PlantMind RBAC
        </p>

        <div className="mt-4 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              Action Visibility Control
            </h1>

            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
              Frontend actions are hidden when the selected role does not have the required backend permission.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Selected role
            </p>

            <p className="mt-2 text-lg font-semibold text-cyan-300">
              {getRoleLabel(selectedRole)}
            </p>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          {roles.map((role) => (
            <Link
              key={role}
              href={`/rbac?role=${encodeURIComponent(role)}`}
              className={
                role === selectedRole
                  ? "rounded-full bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950"
                  : "rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-cyan-500 hover:text-cyan-300"
              }
            >
              {getRoleLabel(role)}
            </Link>
          ))}
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          <section className="rounded-2xl border border-emerald-900/60 bg-emerald-950/20 p-6 lg:col-span-2">
            <h2 className="text-xl font-semibold text-emerald-300">
              Visible actions
            </h2>

            <p className="mt-2 text-sm text-slate-400">
              These buttons are rendered for this role.
            </p>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {frontendActions.map((action) => (
                <PermissionGate
                  key={action.permission}
                  role={selectedRole}
                  permission={action.permission}
                >
                  <div className="rounded-2xl border border-emerald-800 bg-slate-950 p-4">
                    <p className="text-xs uppercase tracking-wider text-emerald-400">
                      {action.area}
                    </p>

                    <h3 className="mt-2 text-lg font-semibold">
                      {action.label}
                    </h3>

                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      {action.description}
                    </p>

                    <button
                      type="button"
                      className="mt-4 rounded-full bg-emerald-400 px-4 py-2 text-sm font-semibold text-slate-950"
                    >
                      Allowed
                    </button>
                  </div>
                </PermissionGate>
              ))}

              {!visibleActions.length ? (
                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4 text-sm text-slate-400">
                  No write actions are visible for this role.
                </div>
              ) : null}
            </div>
          </section>

          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">
              Hidden actions
            </h2>

            <p className="mt-2 text-sm text-slate-400">
              These actions are not rendered as buttons.
            </p>

            <div className="mt-6 space-y-3">
              {hiddenActions.map((action) => (
                <div
                  key={action.permission}
                  className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
                >
                  <p className="font-medium text-slate-300">
                    {action.label}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Missing permission: {action.permission}
                  </p>
                </div>
              ))}
            </div>
          </section>
        </div>

        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-xl font-semibold">
            Effective permissions
          </h2>

          <div className="mt-4 flex flex-wrap gap-2">
            {permissions.map((permission) => (
              <span
                key={permission}
                className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs text-slate-300"
              >
                {permission}
              </span>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}