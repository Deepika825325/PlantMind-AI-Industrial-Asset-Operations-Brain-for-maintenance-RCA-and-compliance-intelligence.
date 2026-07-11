import { GovernedWorkOrderLifecyclePanel } from "@/components/work-order-lifecycle/GovernedWorkOrderLifecyclePanel";

export default function WorkOrderLifecyclePage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-8">
      <GovernedWorkOrderLifecyclePanel />
    </main>
  );
}