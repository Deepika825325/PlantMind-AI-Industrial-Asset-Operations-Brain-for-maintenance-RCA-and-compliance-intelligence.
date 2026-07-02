import Link from "next/link";

const navItems = [
  { label: "Dashboard", href: "/" },
  { label: "Ask PlantMind", href: "/ask" },
  { label: "Assets", href: "/assets" },
  { label: "Compliance", href: "/compliance" },
  { label: "Documents", href: "/documents" },
  { label: "Knowledge Graph", href: "/knowledge-graph" },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/90 backdrop-blur">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-sm font-semibold tracking-[0.35em] text-cyan-400">
          PLANTMIND AI
        </Link>

        <div className="hidden items-center gap-2 md:flex">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-full px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-800 hover:text-white"
            >
              {item.label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}