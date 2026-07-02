export default function Loading() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-100">
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center">
        <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
          PlantMind AI
        </p>
        <p className="mt-4 text-lg text-slate-300">Loading intelligence layer...</p>
      </div>
    </main>
  );
}