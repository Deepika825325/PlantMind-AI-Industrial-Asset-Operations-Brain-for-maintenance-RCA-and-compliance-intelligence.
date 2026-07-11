import TelemetryReplayWorkspace from "@/components/telemetry/TelemetryReplayWorkspace";

export const dynamic = "force-dynamic";

export default function SimulationsPage() {
  return (
    <TelemetryReplayWorkspace
      title="Simulation control center"
      description="Create, start, pause, resume, reset, and speed-control deterministic telemetry replays for PlantMind demo scenarios."
      defaultAssetId="P-101"
    />
  );
}