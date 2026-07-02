import Link from "next/link";
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

type DocumentChunk = {
  chunk_id: string;
  document_id: string;
  document_title: string;
  document_type: string;
  source_group: string;
  section_title: string;
  asset_ids: string[];
  tags: string[];
  chunk_text: string;
  chunk_word_count: number;
  chunk_character_count: number;
  relative_path: string;
  created_at: string;
};

type ChunksResponse = {
  document_id: string;
  total_chunks: number;
  chunks: DocumentChunk[];
};

type PageProps = {
  params: Promise<{
    documentId: string;
  }>;
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

export default async function DocumentDetailPage({ params }: PageProps) {
  const { documentId } = await params;
  const decodedDocumentId = decodeURIComponent(documentId);

  const document = await apiGet<DocumentItem>(
    `/documents/${encodeURIComponent(decodedDocumentId)}`
  );

  let chunks: ChunksResponse | null = null;

  try {
    chunks = await apiGet<ChunksResponse>(
      `/documents/${encodeURIComponent(decodedDocumentId)}/chunks`
    );
  } catch {
    chunks = null;
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div>
          <Link href="/documents" className="text-sm text-cyan-400 hover:text-cyan-300">
            ← Back to Documents
          </Link>

          <p className="mt-6 text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            Document Evidence
          </p>

          <div className="mt-4 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="text-4xl font-semibold tracking-tight">
                {document.title}
              </h1>

              <p className="mt-3 max-w-3xl text-slate-400">
                {document.summary}
              </p>
            </div>

            <span
              className={`rounded-full border px-4 py-2 text-sm font-medium ${getDocTypeClass(
                document.document_type
              )}`}
            >
              {document.document_type}
            </span>
          </div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Document ID</p>
            <p className="mt-3 break-words text-lg font-semibold">
              {document.document_id}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Source Group</p>
            <p className="mt-3 text-2xl font-semibold text-cyan-400">
              {document.source_group}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Word Count</p>
            <p className="mt-3 text-3xl font-semibold">
              {document.word_count}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">Chunks</p>
            <p className="mt-3 text-3xl font-semibold text-amber-400">
              {chunks?.total_chunks || 0}
            </p>
          </div>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">Metadata</h2>

            <div className="mt-5 space-y-5">
              <div>
                <p className="text-sm text-slate-500">Assets</p>

                <div className="mt-2 flex flex-wrap gap-2">
                  {document.asset_ids.map((asset) => (
                    <Link
                      key={asset}
                      href={`/assets/${asset}`}
                      className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300 hover:bg-cyan-400 hover:text-slate-950"
                    >
                      {asset}
                    </Link>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-sm text-slate-500">Tags</p>

                <div className="mt-2 flex flex-wrap gap-2">
                  {document.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-sm text-slate-500">Relative Path</p>
                <p className="mt-2 break-words rounded-xl bg-slate-950 p-3 text-sm text-slate-300">
                  {document.relative_path}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-2">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Document Chunks</h2>
              <span className="text-sm text-slate-500">
                {chunks?.total_chunks || 0} chunks
              </span>
            </div>

            <div className="mt-5 space-y-4">
              {chunks?.chunks.map((chunk) => (
                <div
                  key={chunk.chunk_id}
                  className="rounded-2xl border border-slate-800 bg-slate-950 p-5"
                >
                  <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div>
                      <p className="font-semibold">{chunk.section_title}</p>
                      <p className="mt-1 text-sm text-slate-500">
                        {chunk.chunk_id}
                      </p>
                    </div>

                    <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                      {chunk.chunk_word_count} words
                    </span>
                  </div>

                  <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-300">
                    {chunk.chunk_text}
                  </p>
                </div>
              ))}

              {!chunks?.chunks.length && (
                <p className="rounded-2xl border border-slate-800 bg-slate-950 p-6 text-sm text-slate-500">
                  No chunks found for this document.
                </p>
              )}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}