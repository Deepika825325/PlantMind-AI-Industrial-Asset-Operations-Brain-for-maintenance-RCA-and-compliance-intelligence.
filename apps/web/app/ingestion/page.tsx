"use client";

import { useState } from "react";
import { apiPost } from "@/lib/api";

type IngestionRequest = {
  source_path: string;
  asset_ids: string[];
  document_type: string;
};

type IngestionChunk = {
  chunk_id: string;
  chunk_index: number;
  text: string;
  token_estimate?: number;
};

type IngestionResponse = {
  document_id: string;
  status: string;
  lifecycle_status: string;
  upload_status: string;
  processing_status: string;
  source_filename: string;
  source_path: string;
  stored_raw_path: string;
  object_storage_path: string;
  normalized_text_path?: string | null;
  chunk_manifest_path?: string | null;
  manifest_path: string;
  checksum_sha256: string;
  file_size_bytes: number;
  document_type: string;
  asset_ids: string[];
  text_extract_status?: string;
  text_preview?: string | null;
  chunk_count?: number;
  is_duplicate?: boolean;
  duplicate_of_document_id?: string | null;
  chunks?: IngestionChunk[];
};

const samplePaths = [
  {
    label: "P-101 inspection note",
    sourcePath: "data/raw/inspection_reports/p101_inspection_report.txt",
    assetId: "P-101",
    documentType: "inspection_note",
  },
  {
    label: "HX-301 inspection note",
    sourcePath: "data/raw/inspection_reports/hx301_inspection_report.txt",
    assetId: "HX-301",
    documentType: "inspection_note",
  },
  {
    label: "P-101 SOP",
    sourcePath: "data/raw/sops/p101_maintenance_sop.txt",
    assetId: "P-101",
    documentType: "sop",
  },
];

function parseAssetIds(value: string) {
  return value
    .split(",")
    .map((asset) => asset.trim())
    .filter(Boolean);
}

function formatBytes(value: number) {
  if (!Number.isFinite(value)) {
    return "0 B";
  }

  if (value < 1024) {
    return `${value} B`;
  }

  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }

  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

export default function IngestionPage() {
  const [sourcePath, setSourcePath] = useState("");
  const [assetIds, setAssetIds] = useState("P-101");
  const [documentType, setDocumentType] = useState("inspection_note");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<IngestionResponse | null>(null);
  const [error, setError] = useState("");

  async function registerDocument() {
    setLoading(true);
    setError("");
    setResponse(null);

    try {
      const payload: IngestionRequest = {
        source_path: sourcePath.trim(),
        asset_ids: parseAssetIds(assetIds),
        document_type: documentType.trim(),
      };

      const result = await apiPost<IngestionRequest, IngestionResponse>(
        "/ingestion/documents/local-file",
        payload
      );

      setResponse(result);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to register document"
      );
    } finally {
      setLoading(false);
    }
  }

  function applySample(sample: (typeof samplePaths)[number]) {
    setSourcePath(sample.sourcePath);
    setAssetIds(sample.assetId);
    setDocumentType(sample.documentType);
    setResponse(null);
    setError("");
  }

  const canSubmit =
    sourcePath.trim().length > 3 &&
    documentType.trim().length > 1 &&
    parseAssetIds(assetIds).length > 0;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            Document Ingestion
          </p>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight">
            Register documents into the PlantMind ingestion pipeline
          </h1>

          <p className="mt-3 max-w-3xl text-slate-400">
            Register local files available to the API server, normalize text,
            create chunk manifests, and prepare the document for RAG indexing.
          </p>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-1">
            <h2 className="text-lg font-semibold">Register Local File</h2>

            <label className="mt-5 block text-sm text-slate-400">
              Source Path
            </label>

            <input
              value={sourcePath}
              onChange={(event) => setSourcePath(event.target.value)}
              placeholder="Example: data/raw/sops/p101_maintenance_sop.txt"
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            />

            <label className="mt-5 block text-sm text-slate-400">
              Asset IDs
            </label>

            <input
              value={assetIds}
              onChange={(event) => setAssetIds(event.target.value)}
              placeholder="Example: P-101, HX-301"
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            />

            <label className="mt-5 block text-sm text-slate-400">
              Document Type
            </label>

            <select
              value={documentType}
              onChange={(event) => setDocumentType(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            >
              <option value="inspection_note">inspection_note</option>
              <option value="sop">sop</option>
              <option value="incident_report">incident_report</option>
              <option value="maintenance_record">maintenance_record</option>
              <option value="compliance_checklist">compliance_checklist</option>
              <option value="manual">manual</option>
              <option value="drawing">drawing</option>
            </select>

            <button
              onClick={registerDocument}
              disabled={loading || !canSubmit}
              className="mt-5 w-full rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Registering document..." : "Register Document"}
            </button>

            {error && (
              <p className="mt-5 rounded-xl border border-red-800 bg-red-950/50 p-3 text-sm text-red-300">
                {error}
              </p>
            )}

            <div className="mt-8">
              <p className="text-sm font-medium text-slate-300">
                Sample Paths
              </p>

              <div className="mt-3 space-y-2">
                {samplePaths.map((sample) => (
                  <button
                    key={sample.label}
                    onClick={() => applySample(sample)}
                    className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-left text-sm text-slate-300 transition hover:border-cyan-500 hover:text-white"
                  >
                    <span className="block font-medium text-slate-200">
                      {sample.label}
                    </span>

                    <span className="mt-1 block text-xs text-slate-500">
                      {sample.sourcePath}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-6 lg:col-span-2">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-lg font-semibold">Ingestion Result</h2>

              {!response && !loading && (
                <div className="mt-5 rounded-2xl border border-dashed border-slate-700 bg-slate-950 p-8 text-center text-slate-500">
                  Register a local file to see document ID, storage paths,
                  checksum, and chunk details.
                </div>
              )}

              {loading && (
                <div className="mt-5 rounded-2xl border border-slate-800 bg-slate-950 p-8 text-center text-slate-400">
                  Normalizing document and generating ingestion metadata...
                </div>
              )}

              {response && (
                <div className="mt-5 space-y-6">
                  <div className="grid gap-4 md:grid-cols-4">
                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <p className="text-sm text-slate-400">Status</p>
                      <p className="mt-2 text-xl font-semibold text-emerald-300">
                        {response.lifecycle_status}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        {response.processing_status}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <p className="text-sm text-slate-400">Chunks</p>
                      <p className="mt-2 text-xl font-semibold text-cyan-300">
                        {response.chunk_count ?? 0}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <p className="text-sm text-slate-400">File Size</p>
                      <p className="mt-2 text-xl font-semibold">
                        {formatBytes(response.file_size_bytes)}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <p className="text-sm text-slate-400">Assets</p>
                      <p className="mt-2 text-xl font-semibold">
                        {response.asset_ids.join(", ")}
                      </p>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                    <h3 className="font-semibold">Document Metadata</h3>

                    <div className="mt-4 grid gap-4 text-sm md:grid-cols-2">
                      <div>
                        <p className="text-slate-500">Document ID</p>
                        <p className="mt-1 break-all text-slate-200">
                          {response.document_id}
                        </p>
                      </div>

                      <div>
                        <p className="text-slate-500">Filename</p>
                        <p className="mt-1 break-all text-slate-200">
                          {response.source_filename}
                        </p>
                      </div>

                      <div>
                        <p className="text-slate-500">Document Type</p>
                        <p className="mt-1 text-slate-200">
                          {response.document_type}
                        </p>
                      </div>

                      <div>
                        <p className="text-slate-500">SHA256</p>
                        <p className="mt-1 break-all text-slate-200">
                          {response.checksum_sha256}
                        </p>
                      </div>

                      <div>
                        <p className="text-slate-500">Object Storage Path</p>
                        <p className="mt-1 break-all text-slate-200">
                          {response.object_storage_path}
                        </p>
                      </div>

                      <div>
                        <p className="text-slate-500">Manifest Path</p>
                        <p className="mt-1 break-all text-slate-200">
                          {response.manifest_path}
                        </p>
                      </div>

                      <div>
                        <p className="text-slate-500">Chunk Manifest Path</p>
                        <p className="mt-1 break-all text-slate-200">
                          {response.chunk_manifest_path || "Not chunked"}
                        </p>
                      </div>

                      <div>
                        <p className="text-slate-500">Duplicate Status</p>
                        <p className="mt-1 break-all text-slate-200">
                          {response.is_duplicate
                            ? `Duplicate of ${response.duplicate_of_document_id ?? "existing document"}`
                            : "New document"}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                    <h3 className="font-semibold">Next Action</h3>

                    <p className="mt-3 text-sm leading-6 text-slate-300">
                      After registering documents, open the RAG Console and run
                      Build Index from the backend API or rerun your indexing
                      endpoint before searching newly ingested content.
                    </p>
                  </div>

                  {response.chunks && response.chunks.length > 0 && (
                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                      <h3 className="font-semibold">Chunk Preview</h3>

                      <div className="mt-4 space-y-4">
                        {response.chunks.slice(0, 5).map((chunk) => (
                          <div
                            key={chunk.chunk_id}
                            className="rounded-2xl border border-slate-800 bg-slate-900 p-4"
                          >
                            <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                              <p className="font-medium text-slate-100">
                                Chunk {chunk.chunk_index}
                              </p>

                              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                                {chunk.chunk_id}
                              </span>
                            </div>

                            <p className="mt-4 text-sm leading-6 text-slate-300">
                              {chunk.text}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
