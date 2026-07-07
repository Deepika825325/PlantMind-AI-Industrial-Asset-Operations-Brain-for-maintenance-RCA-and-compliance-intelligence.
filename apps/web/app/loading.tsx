import {
  LoadingState,
} from "@/components/system";

export default function GlobalLoading() {
  return (
    <main className="min-h-[calc(100vh-8rem)] min-w-0 bg-slate-950 px-4 py-8 text-slate-100 sm:px-6">
      <div className="mx-auto w-full max-w-7xl">
        <LoadingState
          title="Loading PlantMind workspace"
          message="Retrieving asset, maintenance, compliance and operational intelligence."
        />
      </div>
    </main>
  );
}
