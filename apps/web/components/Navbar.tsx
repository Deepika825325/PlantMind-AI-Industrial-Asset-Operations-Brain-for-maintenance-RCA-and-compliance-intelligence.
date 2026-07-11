"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { label: "Dashboard", href: "/" },
  { label: "Ask PlantMind", href: "/ask" },
  { label: "RAG Console", href: "/rag-console" },
  { label: "Assets", href: "/assets" },
  { label: "P&ID", href: "/pid" },
  { label: "Compliance", href: "/compliance" },
  { label: "Maintenance", href: "/maintenance" },
  { label: "RCA", href: "/rca" },
  { label: "Documents", href: "/documents" },
  { label: "Ingestion", href: "/ingestion" },
  { label: "RBAC", href: "/rbac" },
  {
    label: "Knowledge Graph",
    href: "/knowledge-graph",
  },
];

function isActivePath(
  pathname: string,
  href: string
) {
  if (href === "/") {
    return pathname === "/";
  }

  return pathname.startsWith(href);
}

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/90 backdrop-blur">
      <nav className="mx-auto flex max-w-[1600px] flex-col gap-4 px-6 py-4 lg:flex-row lg:items-center lg:justify-between">
        <Link
          href="/"
          className="text-sm font-semibold tracking-[0.35em] text-cyan-400"
        >
          PLANTMIND AI
        </Link>

        <div className="flex flex-wrap items-center gap-2">
          {navItems.map((item) => {
            const active = isActivePath(
              pathname,
              item.href
            );

            return (
              <Link
                key={item.href}
                href={item.href}
                className={
                  active
                    ? "rounded-full bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition"
                    : "rounded-full px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-800 hover:text-white"
                }
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </header>
  );
}
