export default function DemoModeBanner() {
  return (
    <div className="w-full border-b border-cyan-900/70 bg-cyan-950/40">
      <div className="mx-auto flex max-w-7xl flex-col gap-1 px-4 py-3 sm:px-6 lg:flex-row lg:items-center lg:justify-between">
        <p className="font-medium text-cyan-100">
          PlantMind Demo Environment
        </p>

        <p className="break-words text-sm text-cyan-200/80">
          Seed data loaded for P-101, C-201 and HX-301
        </p>
      </div>
    </div>
  );
}
