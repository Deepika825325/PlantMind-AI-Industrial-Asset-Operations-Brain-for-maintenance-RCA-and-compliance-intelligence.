import {
  EmptyState,
} from "@/components/system";

export default function NotFound() {
  return (
    <main className="min-h-[calc(100vh-8rem)] min-w-0 bg-slate-950 px-4 py-8 text-slate-100 sm:px-6">
      <div className="mx-auto w-full max-w-7xl">
        <EmptyState
          title="PlantMind page not found"
          message="The requested route or industrial resource does not exist in this demo environment."
          actionLabel="Return to dashboard"
          actionHref="/"
        />
      </div>
    </main>
  );
}
