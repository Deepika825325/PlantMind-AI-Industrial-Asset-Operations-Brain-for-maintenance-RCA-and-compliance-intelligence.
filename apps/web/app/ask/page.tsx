"use client";

import { useState } from "react";
import { apiPost } from "@/lib/api";
import { AskRequest, AskResponse } from "@/lib/types";

const sampleQuestions = [
  "Why is P-101 high risk?",
  "What is the likely root cause of P-101 vibration?",
  "Why is C-201 medium risk?",
  "Why is HX-301 suspected to be fouled?",
  "Which assets are non-compliant?",
];

function getConfidenceClass(score: number) {
  if (score >= 0.8) {
    return "text-emerald-300 bg-emerald-950 border-emerald-800";
  }

  if (score >= 0.6) {
    return "text-cyan-300 bg-cyan-950 border-cyan-800";
  }

  if (score >= 0.4) {
    return "text-amber-300 bg-amber-950 border-amber-800";
  }

  return "text-red-300 bg-red-950 border-red-800";
}

export default function AskPage() {
  const [question, setQuestion] = useState("Why is P-101 high risk?");
  const [assetId, setAssetId] = useState("P-101");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [error, setError] = useState("");

  async function handleAsk(customQuestion?: string, customAsset?: string) {
    const finalQuestion = customQuestion || question;
    const finalAsset = customAsset !== undefined ? customAsset : assetId;

    setLoading(true);
    setError("");
    setResponse(null);

    try {
      const payload: AskRequest = {
        question: finalQuestion,
        asset_id: finalAsset || null,
        top_k: 5,
      };

      const result = await apiPost<AskRequest, AskResponse>("/ask", payload);
      setResponse(result);
      setQuestion(finalQuestion);
      setAssetId(finalAsset);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function useSample(sample: string) {
    let nextAsset = "";

    if (sample.includes("P-101")) {
      nextAsset = "P-101";
    } else if (sample.includes("C-201")) {
      nextAsset = "C-201";
    } else if (sample.includes("HX-301")) {
      nextAsset = "HX-301";
    }

    setQuestion(sample);
    setAssetId(nextAsset);
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            Ask PlantMind
          </p>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight">
            Evidence-backed industrial AI assistant
          </h1>

          <p className="mt-3 max-w-3xl text-slate-400">
            Ask about asset risk, RCA, compliance gaps, maintenance actions,
            and document evidence. PlantMind returns citations and retrieved context.
          </p>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-1">
            <h2 className="text-lg font-semibold">Question</h2>

            <label className="mt-5 block text-sm text-slate-400">
              Asset Filter
            </label>

            <select
              value={assetId}
              onChange={(event) => setAssetId(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            >
              <option value="">Auto detect</option>
              <option value="P-101">P-101 Pump</option>
              <option value="C-201">C-201 Compressor</option>
              <option value="HX-301">HX-301 Heat Exchanger</option>
            </select>

            <label className="mt-5 block text-sm text-slate-400">
              Ask a question
            </label>

            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              rows={6}
              className="mt-2 w-full resize-none rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            />

            <button
              onClick={() => handleAsk()}
              disabled={loading || question.trim().length < 3}
              className="mt-5 w-full rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Retrieving evidence..." : "Ask PlantMind"}
            </button>

            {error && (
              <p className="mt-4 rounded-xl border border-red-800 bg-red-950/50 p-3 text-sm text-red-300">
                {error}
              </p>
            )}

            <div className="mt-8">
              <p className="text-sm font-medium text-slate-300">
                Sample Questions
              </p>

              <div className="mt-3 space-y-2">
                {sampleQuestions.map((sample) => (
                  <button
                    key={sample}
                    onClick={() => useSample(sample)}
                    className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-left text-sm text-slate-300 transition hover:border-cyan-500 hover:text-white"
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-2">
            <h2 className="text-lg font-semibold">Answer</h2>

            {!response && !loading && (
              <div className="mt-6 rounded-2xl border border-dashed border-slate-700 bg-slate-950 p-8 text-center text-slate-500">
                Ask a question to see answer, citations, confidence, and retrieved evidence.
              </div>
            )}

            {loading && (
              <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950 p-8 text-center text-slate-400">
                Retrieving source chunks and generating evidence-backed answer...
              </div>
            )}

            {response && (
              <div className="mt-6 space-y-6">
                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-6">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-cyan-400/10 px-3 py-1 text-xs font-medium text-cyan-300">
                      {response.answer_mode}
                    </span>

                    <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                      {response.answer_type}
                    </span>

                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-medium ${getConfidenceClass(
                        response.confidence_score
                      )}`}
                    >
                      Confidence {Math.round(response.confidence_score * 100)}%
                    </span>

                    {response.detected_assets.map((asset) => (
                      <span
                        key={asset}
                        className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300"
                      >
                        {asset}
                      </span>
                    ))}
                  </div>

                  <p className="mt-5 text-lg leading-8 text-slate-100">
                    {response.answer}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-6">
                  <h3 className="font-semibold">Supporting Sources</h3>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {response.supporting_sources.map((source) => (
                      <span
                        key={source}
                        className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-sm text-slate-300"
                      >
                        {source}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-6">
                  <h3 className="font-semibold">Citations</h3>

                  <div className="mt-4 space-y-4">
                    {response.citations.map((citation) => (
                      <div
                        key={citation.citation_id}
                        className="rounded-2xl border border-slate-800 bg-slate-900 p-4"
                      >
                        <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                          <div>
                            <p className="font-medium text-slate-100">
                              [{citation.citation_id}] {citation.document_title}
                            </p>

                            <p className="mt-1 text-sm text-slate-500">
                              {citation.section_title} · {citation.document_type}
                            </p>
                          </div>

                          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                            {citation.document_id}
                          </span>
                        </div>

                        <p className="mt-4 text-sm leading-6 text-slate-300">
                          {citation.evidence_excerpt}
                        </p>

                        <p className="mt-3 text-xs text-slate-500">
                          Path: {citation.relative_path}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-6">
                  <h3 className="font-semibold">Suggested Follow-ups</h3>

                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    {response.suggested_followups.map((followup) => (
                      <button
                        key={followup}
                        onClick={() => handleAsk(followup, "")}
                        className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-left text-sm text-slate-300 transition hover:border-cyan-500 hover:text-white"
                      >
                        {followup}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-6">
                  <h3 className="font-semibold">Retrieved Evidence Chunks</h3>

                  <div className="mt-4 space-y-4">
                    {response.retrieved_context.map((chunk) => (
                      <div
                        key={chunk.chunk_id}
                        className="rounded-2xl border border-slate-800 bg-slate-900 p-4"
                      >
                        <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                          <div>
                            <p className="font-medium text-slate-100">
                              {chunk.document_title}
                            </p>

                            <p className="mt-1 text-sm text-slate-500">
                              {chunk.section_title}
                            </p>
                          </div>

                          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                            Score {chunk.score}
                          </span>
                        </div>

                        <p className="mt-4 line-clamp-6 text-sm leading-6 text-slate-300">
                          {chunk.chunk_text}
                        </p>

                        <p className="mt-3 text-xs text-slate-500">
                          Source: {chunk.document_id}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}