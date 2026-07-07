import Link from "next/link";
import { apiGet } from "@/lib/api";
import { Asset } from "@/lib/types";

export const dynamic = "force-dynamic";

type SensorSignal = {
  sensor_name: string;
  latest_value: number;
  unit: string;
  latest_status: string;
  trend_direction: string;
};

type Health = {
  asset_id: string;
  asset_name: string;
  asset_type: string;
  risk_score: number;
  health_score: number;
  health_label: string;
  risk_level: string;
  sensor_status: string;
  sensor_signals: SensorSignal[];
  summary: string;
};

type ComplianceGap = {
  gap_id: string;
  asset_id: string;
  requirement: string;
  expected_evidence: string;
  current_status: string;
  evidence_file: string;
  gap_severity: string;
  recommended_action: string;
  source_document: string;
};

type WorkOrder = {
  event_id: string;
  asset_id: string;
  asset_name: string;
  event_type: string;
  priority: string;
  status: string;
  created_date: string;
  due_date: string;
  description: string;
  linked_document: string;
  compliance_related: string;
};

type EvidenceDocument = {
  document_id: string;
  title: string;
  document_type: string;
  source_group: string;
  asset_ids: string[];
  tags: string[];
  summary: string;
  relative_path: string;
  word_count: number;
};

type AssetEvidenceResponse = {
  asset_id: string;
  asset: Asset;
  health: Health | null;
  compliance: {
    summary: {
      asset_id: string;
      total_gaps: number;
      high_severity_gaps: number;
      medium_severity_gaps: number;
      compliance_status: string;
      gap_ids: string[];
    } | null;
    gaps: ComplianceGap[];
  };
  work_orders: WorkOrder[];
  documents: EvidenceDocument[];
  graph_subgraph: {
    node_count: number;
    edge_count: number;
    nodes: unknown[];
    edges: unknown[];
  };
  suggested_questions: {
    question_id: string;
    question: string;
    expected_answer_type: string;
    expected_assets: string[];
    expected_sources: string[];
  }[];
};

type PageProps = {
  params: Promise<{
    assetId: string;
  }>;
};

function getRiskBadgeClass(riskLevel: string) {
  if (riskLevel === "High") {
    return "bg-red-100 text-red-700 border-red-200";
  }

  if (riskLevel === "Medium") {
    return "bg-amber-100 text-amber-700 border-amber-200";
  }

  return "bg-emerald-100 text-emerald-700 border-emerald-200";
}

function getStatusTextClass(status: string) {
  if (status === "Critical" || status === "High Risk Non-Compliant") {
    return "text-red-400";
  }

  if (status === "Warning" || status.includes("Medium")) {
    return "text-amber-400";
  }

  return "text-emerald-400";
}

function getHealthBarClass(healthScore: number) {
  if (healthScore < 40) {
    return "bg-red-500";
  }

  if (healthScore < 70) {
    return "bg-amber-500";
  }

  return "bg-emerald-500";
}

export default async function AssetDetailPage({ params }: PageProps) {
  const { assetId } = await params;
  const decodedAssetId = decodeURIComponent(assetId).toUpperCase();

  const data = await apiGet<AssetEvidenceResponse>(
    `/assets/${encodeURIComponent(decodedAssetId)}/evidence`
  );

  const asset = data.asset;
  const health = data.health;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <Link href="/assets" className="text-sm text-cyan-400 hover:text-cyan-300">
              ← Back to Assets
            </Link>

            <p className="mt-6 text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
              Asset 360
            </p>

            <h1 className="mt-4 text-4xl font-semibold tracking-tight">
              {asset.asset_id} · {asset.asset_name}
            </h1>

            <p className="mt-3 max-w-3xl text-slate-400">
              Complete evidence traceability across health signals, compliance gaps,
              maintenance work orders, source documents, and graph relationships.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Current Risk
            </p>

            <div className="mt-3 flex items-center gap-3">
              <p className="text-3xl font-semibold">{asset.risk_score}</p>
              <span
                className={`rounded-full border px-3 py-1 text-xs font-medium ${getRiskBadgeClass(
                  asset.risk_level
                )}`}
              >
                {asset.risk_level} Risk
              </span>
            </div>
          </div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Health Score</p>
            <p className="mt-3 text-3xl font-semibold">
              {asset.health_score}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Sensor Status</p>
            <p className={`mt-3 text-2xl font-semibold ${getStatusTextClass(asset.sensor_status)}`}>
              {asset.sensor_status}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Compliance Gaps</p>
            <p className="mt-3 text-3xl font-semibold text-amber-400">
              {data.compliance.gaps.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Evidence Documents</p>
            <p className="mt-3 text-3xl font-semibold text-cyan-400">
              {data.documents.length}
            </p>
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-xl font-semibold">Risk Story</h2>

          <p className="mt-4 text-sm leading-7 text-slate-300">
            {asset.critical_story}
          </p>

          <div className="mt-5">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Health</span>
              <span>{asset.health_score}/100</span>
            </div>

            <div className="mt-2 h-2 rounded-full bg-slate-800">
              <div
                className={`h-2 rounded-full ${getHealthBarClass(asset.health_score)}`}
                style={{ width: `${asset.health_score}%` }}
              />
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href={`/ask?asset=${asset.asset_id}`}
              className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-300"
            >
              Ask PlantMind about {asset.asset_id}
            </Link>

            <Link
              href={`/compliance?asset=${asset.asset_id}`}
              className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:border-cyan-400 hover:text-white"
            >
              View Compliance Gaps
            </Link>

            <Link
              href={`/knowledge-graph?asset=${asset.asset_id}`}
              className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:border-cyan-400 hover:text-white"
            >
              View Graph Context
            </Link>
          </div>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">Sensor Signals</h2>

            <div className="mt-5 space-y-4">
              {health?.sensor_signals.map((signal) => (
                <div
                  key={signal.sensor_name}
                  className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{signal.sensor_name}</p>
                      <p className="mt-1 text-sm text-slate-500">
                        Trend: {signal.trend_direction}
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="text-2xl font-semibold">
                        {signal.latest_value}
                        <span className="ml-1 text-sm text-slate-500">
                          {signal.unit}
                        </span>
                      </p>

                      <p className={`mt-1 text-sm ${getStatusTextClass(signal.latest_status)}`}>
                        {signal.latest_status}
                      </p>
                    </div>
                  </div>
                </div>
              ))}

              {!health?.sensor_signals.length && (
                <p className="text-sm text-slate-500">No sensor signals found.</p>
              )}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">Compliance Gaps</h2>

            <div className="mt-5 space-y-4">
              {data.compliance.gaps.map((gap) => (
                <div
                  key={gap.gap_id}
                  className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-semibold">{gap.gap_id}</p>
                      <p className="mt-2 text-sm text-slate-300">
                        {gap.requirement}
                      </p>
                    </div>

                    <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-medium text-red-700">
                      {gap.gap_severity}
                    </span>
                  </div>

                  <p className="mt-4 text-sm text-slate-400">
                    Expected: {gap.expected_evidence}
                  </p>

                  <p className="mt-2 text-sm text-amber-300">
                    Action: {gap.recommended_action}
                  </p>
                </div>
              ))}

              {!data.compliance.gaps.length && (
                <p className="text-sm text-slate-500">No compliance gaps found.</p>
              )}
            </div>
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Maintenance Work Orders</h2>
            <span className="text-sm text-slate-500">
              {data.work_orders.length} work orders
            </span>
          </div>

          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            {data.work_orders.map((order) => (
              <div
                key={order.event_id}
                className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-semibold">{order.event_id}</p>
                    <p className="mt-2 text-sm text-slate-300">
                      {order.event_type}
                    </p>
                  </div>

                  <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                    {order.priority}
                  </span>
                </div>

                <p className="mt-4 text-sm leading-6 text-slate-400">
                  {order.description}
                </p>

                <div className="mt-4 flex justify-between text-xs text-slate-500">
                  <span>Status: {order.status}</span>
                  <span>Due: {order.due_date}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Evidence Documents</h2>
            <span className="text-sm text-slate-500">
              {data.documents.length} documents
            </span>
          </div>

          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            {data.documents.map((document) => (
              <Link
                key={`${document.document_id}-${document.relative_path}`}
                href={`/documents/${encodeURIComponent(document.document_id)}`}
                className="rounded-2xl border border-slate-800 bg-slate-950 p-5 transition hover:border-cyan-500"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-semibold">{document.title}</p>
                    <p className="mt-1 text-sm text-slate-500">
                      {document.document_id}
                    </p>
                  </div>

                  <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                    {document.document_type}
                  </span>
                </div>

                <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-400">
                  {document.summary}
                </p>
              </Link>
            ))}
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-xl font-semibold">Suggested Questions</h2>

          <div className="mt-5 grid gap-3 lg:grid-cols-2">
            {data.suggested_questions.slice(0, 6).map((item) => (
              <Link
                key={item.question_id}
                href={`/ask?asset=${asset.asset_id}`}
                className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-300 transition hover:border-cyan-500 hover:text-white"
              >
                {item.question}
              </Link>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
