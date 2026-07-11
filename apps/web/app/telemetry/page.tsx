import TelemetryReplayWorkspace from "@/components/telemetry/TelemetryReplayWorkspace";

export const dynamic = "force-dynamic";

export default function TelemetryPage() {
  return (
    <TelemetryReplayWorkspace
      title="Live telemetry interface"
      description="Polling-based telemetry charts powered by the deterministic historical replay engine. No WebSockets and no live plant connection are used."
      defaultAssetId="P-101"
    />
  );
}