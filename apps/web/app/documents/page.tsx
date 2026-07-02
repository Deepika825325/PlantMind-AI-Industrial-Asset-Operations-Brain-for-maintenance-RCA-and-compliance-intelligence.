"use client";

import { useEffect, useMemo, useState } from "react";
import { apiGet } from "@/lib/api";

type DocumentItem = {
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

type DocumentsResponse = {
  total: number;
  documents: DocumentItem[];
};

function getDocTypeClass(type: string) {
  if (type.includes("SOP")) {
    return "bg-cyan-100 text-cyan-700 border-cyan-200";
  }

  if (type.includes("Inspection")) {
    return "bg-emerald-100 text-emerald-700 border-emerald-200";
  }

  if (type.includes("Incident")) {
    return "bg-red-100 text-red-700 border-red-200";
  }

  if (type.includes("Compliance")) {
    return "bg-amber-100 text-amber-700 border-amber-200";
  }

  if (type.includes("P&ID")) {
    return "bg-violet-100 text-violet-700 border-violet-200";
  }

  return "bg-slate-100 text-slate-700 border-slate-200";
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedAsset, setSelectedAsset] = useState("ALL");
  const [selectedType, setSelectedType] = useState("ALL");
  const [searchText, setSearchText] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDocuments() {
      try {
        setLoading(true);
        const result = await apiGet<DocumentsResponse>("/documents");
        setDocuments(result.documents);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load documents");
      } finally {
        setLoading(false);
      }
    }

    loadDocuments();
  }, []);

  const documentTypes = useMemo(() => {
    const types = new Set(documents.map((document) => document.document_type));
    return Array.from(types).sort();
  }, [documents]);

  const filteredDocuments = useMemo(() => {
    return documents.filter((document) => {
      const matchesAsset =
        selectedAsset === "ALL" || document.asset_ids.includes(selectedAsset);

      const matchesType =
        selectedType === "ALL" || document.document_type === selectedType;

      const query = searchText.toLowerCase();

      const matchesSearch =
        !query ||
        document.title.toLowerCase().includes(query) ||
        document.document_id.toLowerCase().includes(query) ||
        document.summary.toLowerCase().includes(query) ||
        document.tags.join(" ").toLowerCase().includes(query);

      return matchesAsset && matchesType && matchesSearch;
    });
  }, [documents, selectedAsset, selectedType, searchText]);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            Document Library
          </p>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight">
            Industrial Knowledge Base
          </h1>

          <p className="mt-3 max-w-3xl text-slate-400">
            Browse SOPs, inspection reports, incident reports, compliance files,
            P&ID metadata, and public-source references used by PlantMind AI.
          </p>
        </div>

        {loading && (
          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
            Loading documents...
          </div>
        )}

        {error && (
          <div className="mt-8 rounded-2xl border border-red-800 bg-red-950/40 p-6 text-red-300">
            {error}
          </div>
        )}

        {!loading && !error && (
          <>
            <div className="mt-8 grid gap-4 md:grid-cols-4">
              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Total Documents</p>
                <p className="mt-3 text-3xl font-semibold">{documents.length}</p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Filtered Results</p>
                <p className="mt-3 text-3xl font-semibold text-cyan-400">
                  {filteredDocuments.length}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Document Types</p>
                <p className="mt-3 text-3xl font-semibold text-amber-400">
                  {documentTypes.length}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Assets Covered</p>
                <p className="mt-3 text-3xl font-semibold text-emerald-400">
                  3
                </p>
              </div>
            </div>

            <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <label className="text-sm text-slate-400">Search</label>
                  <input
                    value={searchText}
                    onChange={(event) => setSearchText(event.target.value)}
                    placeholder="Search title, ID, tag, summary..."
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  />
                </div>

                <div>
                  <label className="text-sm text-slate-400">Asset</label>
                  <select
                    value={selectedAsset}
                    onChange={(event) => setSelectedAsset(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  >
                    <option value="ALL">All Assets</option>
                    <option value="P-101">P-101</option>
                    <option value="C-201">C-201</option>
                    <option value="HX-301">HX-301</option>
                  </select>
                </div>

                <div>
                  <label className="text-sm text-slate-400">Document Type</label>
                  <select
                    value={selectedType}
                    onChange={(event) => setSelectedType(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                  >
                    <option value="ALL">All Types</option>
                    {documentTypes.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="mt-8 grid gap-5 lg:grid-cols-2">
              {filteredDocuments.map((document) => (
                <div
                  key={`${document.document_id}-${document.relative_path}`}
                  className="rounded-2xl border border-slate-800 bg-slate-900 p-6"
                >
                  <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div>
                      <h2 className="text-lg font-semibold">{document.title}</h2>
                      <p className="mt-1 text-sm text-slate-500">
                        {document.document_id}
                      </p>
                    </div>

                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-medium ${getDocTypeClass(
                        document.document_type
                      )}`}
                    >
                      {document.document_type}
                    </span>
                  </div>

                  <p className="mt-4 line-clamp-4 text-sm leading-6 text-slate-300">
                    {document.summary}
                  </p>

                  <div className="mt-5 flex flex-wrap gap-2">
                    {document.asset_ids.map((asset) => (
                      <span
                        key={asset}
                        className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300"
                      >
                        {asset}
                      </span>
                    ))}

                    {document.tags.slice(0, 5).map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className="mt-5 grid gap-3 text-sm md:grid-cols-2">
                    <div className="rounded-xl bg-slate-950 p-3">
                      <p className="text-xs uppercase tracking-wider text-slate-500">
                        Source Group
                      </p>
                      <p className="mt-1 text-slate-300">{document.source_group}</p>
                    </div>

                    <div className="rounded-xl bg-slate-950 p-3">
                      <p className="text-xs uppercase tracking-wider text-slate-500">
                        Word Count
                      </p>
                      <p className="mt-1 text-slate-300">{document.word_count}</p>
                    </div>
                  </div>

                  <p className="mt-4 text-xs text-slate-500">
                    Path: {document.relative_path}
                  </p>
                </div>
              ))}
            </div>
          </>
        )}
      </section>
    </main>
  );
}