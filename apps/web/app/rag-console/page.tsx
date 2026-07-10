"use client";

import { useState } from "react";
import { apiPost } from "@/lib/api";

type RagSearchRequest = {
  query: string;
  asset_id: string | null;
  document_type: string | null;
  limit: number;
};

type RagSearchHit = {
  rank: number;
  score: number;
  document_id: string;
  chunk_id: string;
  chunk_index: number;
  text: string;
  asset_ids: string[];
  document_type: string;
  source_filename: string;
  matched_terms: string[];
};

type RagSearchResponse = {
  query: string;
  total: number;
  hits: RagSearchHit[];
};

type RagAnswerRequest = {
  question: string;
  asset_id: string | null;
  document_type: string | null;
  limit: number;
};

type RagAnswerCitation = {
  citation_id: string;
  document_id: string;
  chunk_id: string;
  chunk_index: number;
  source_filename: string;
  asset_ids: string[];
  document_type: string;
  score: number;
  matched_terms: string[];
  quoted_text: string;
};

type RagAnswerQuality = {
  grounded: boolean;
  quality_score: number;
  query_coverage: number;
  matched_query_terms: string[];
  missing_query_terms: string[];
  warnings: string[];
};

type RagAnswerResponse = {
  answer_id: string;
  question: string;
  answer: string;
  confidence: number;
  retrieval_status: string;
  total_citations: number;
  citations: RagAnswerCitation[];
  quality: RagAnswerQuality;
};

type RagBenchmarkQuestion = {
  question_id: string;
  question: string;
  asset_id: string | null;
  document_type: string | null;
  expected_terms: string[];
  minimum_quality_score: number;
  minimum_query_coverage: number;
};

type RagEvaluationRequest = {
  questions: RagBenchmarkQuestion[];
};

type RagBenchmarkCaseResult = {
  question_id: string;
  question: string;
  asset_id: string | null;
  passed: boolean;
  retrieval_status: string;
  grounded: boolean;
  confidence: number;
  quality_score: number;
  query_coverage: number;
  total_citations: number;
  matched_expected_terms: string[];
  missing_expected_terms: string[];
  warnings: string[];
};

type RagEvaluationReport = {
  evaluation_id: string;
  generated_at: string;
  summary: {
    total_questions: number;
    passed_questions: number;
    failed_questions: number;
    pass_rate: number;
    average_confidence: number;
    average_quality_score: number;
    average_query_coverage: number;
  };
  results: RagBenchmarkCaseResult[];
};

const benchmarkQuestions: RagBenchmarkQuestion[] = [
  {
    question_id: "RAG-Q-001",
    question: "Why is P-101 vibration high?",
    asset_id: "P-101",
    document_type: null,
    expected_terms: ["vibration", "bearing"],
    minimum_quality_score: 0.25,
    minimum_query_coverage: 0.2,
  },
  {
    question_id: "RAG-Q-002",
    question: "Why is HX-301 heat transfer reduced?",
    asset_id: "HX-301",
    document_type: null,
    expected_terms: ["fouling", "heat transfer"],
    minimum_quality_score: 0.25,
    minimum_query_coverage: 0.2,
  },
  {
    question_id: "RAG-Q-003",
    question: "Why is lubrication evidence important for P-101?",
    asset_id: "P-101",
    document_type: null,
    expected_terms: ["lubrication", "evidence"],
    minimum_quality_score: 0.25,
    minimum_query_coverage: 0.2,
  },
];

function percentage(value: number) {
  return `${Math.round(value * 100)}%`;
}

function badgeClass(status: boolean) {
  return status
    ? "border-emerald-800 bg-emerald-950 text-emerald-300"
    : "border-red-800 bg-red-950 text-red-300";
}

function qualityClass(score: number) {
  if (score >= 0.75) {
    return "border-emerald-800 bg-emerald-950 text-emerald-300";
  }

  if (score >= 0.45) {
    return "border-cyan-800 bg-cyan-950 text-cyan-300";
  }

  if (score >= 0.25) {
    return "border-amber-800 bg-amber-950 text-amber-300";
  }

  return "border-red-800 bg-red-950 text-red-300";
}

export default function RagConsolePage() {
  const [question, setQuestion] = useState("Why is P-101 vibration high?");
  const [assetId, setAssetId] = useState("P-101");
  const [documentType, setDocumentType] = useState("");
  const [limit, setLimit] = useState(5);

  const [searchResult, setSearchResult] =
    useState<RagSearchResponse | null>(null);

  const [answerResult, setAnswerResult] =
    useState<RagAnswerResponse | null>(null);

  const [evaluationReport, setEvaluationReport] =
    useState<RagEvaluationReport | null>(null);

  const [loadingAction, setLoadingAction] = useState("");
  const [error, setError] = useState("");

  const requestFilters = {
    asset_id: assetId || null,
    document_type: documentType || null,
    limit,
  };

  async function runSearch() {
    setLoadingAction("search");
    setError("");
    setSearchResult(null);

    try {
      const payload: RagSearchRequest = {
        query: question,
        ...requestFilters,
      };

      const result = await apiPost<RagSearchRequest, RagSearchResponse>(
        "/rag-indexing/ingestion/search",
        payload
      );

      setSearchResult(result);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to run RAG search"
      );
    } finally {
      setLoadingAction("");
    }
  }

  async function runAnswer() {
    setLoadingAction("answer");
    setError("");
    setAnswerResult(null);

    try {
      const payload: RagAnswerRequest = {
        question,
        ...requestFilters,
      };

      const result = await apiPost<RagAnswerRequest, RagAnswerResponse>(
        "/rag-answering/ingestion/answer",
        payload
      );

      setAnswerResult(result);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to generate RAG answer"
      );
    } finally {
      setLoadingAction("");
    }
  }

  async function runEvaluation() {
    setLoadingAction("evaluation");
    setError("");
    setEvaluationReport(null);

    try {
      const payload: RagEvaluationRequest = {
        questions: benchmarkQuestions,
      };

      const result = await apiPost<RagEvaluationRequest, RagEvaluationReport>(
        "/rag-evaluation/ingestion/run",
        payload
      );

      setEvaluationReport(result);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to run RAG evaluation"
      );
    } finally {
      setLoadingAction("");
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-400">
            RAG Console
          </p>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight">
            Search, answer, cite, and evaluate ingested knowledge
          </h1>

          <p className="mt-3 max-w-3xl text-slate-400">
            Test the production ingestion RAG pipeline using retrieval search,
            evidence-grounded answers, quality scoring, and benchmark regression.
          </p>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-1">
            <h2 className="text-lg font-semibold">Controls</h2>

            <label className="mt-5 block text-sm text-slate-400">
              Asset Filter
            </label>

            <select
              value={assetId}
              onChange={(event) => setAssetId(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            >
              <option value="">All assets</option>
              <option value="P-101">P-101 Pump</option>
              <option value="C-201">C-201 Compressor</option>
              <option value="HX-301">HX-301 Heat Exchanger</option>
            </select>

            <label className="mt-5 block text-sm text-slate-400">
              Document Type
            </label>

            <input
              value={documentType}
              onChange={(event) => setDocumentType(event.target.value)}
              placeholder="Optional, example: inspection_note"
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            />

            <label className="mt-5 block text-sm text-slate-400">
              Retrieval Limit
            </label>

            <input
              type="number"
              min={1}
              max={10}
              value={limit}
              onChange={(event) => setLimit(Number(event.target.value))}
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            />

            <label className="mt-5 block text-sm text-slate-400">
              Question / Search Query
            </label>

            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              rows={6}
              className="mt-2 w-full resize-none rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
            />

            <div className="mt-5 grid gap-3">
              <button
                onClick={runSearch}
                disabled={loadingAction !== "" || question.trim().length < 3}
                className="rounded-xl bg-slate-100 px-5 py-3 font-semibold text-slate-950 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loadingAction === "search" ? "Searching..." : "Run Search"}
              </button>

              <button
                onClick={runAnswer}
                disabled={loadingAction !== "" || question.trim().length < 3}
                className="rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loadingAction === "answer" ? "Answering..." : "Generate Answer"}
              </button>

              <button
                onClick={runEvaluation}
                disabled={loadingAction !== ""}
                className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loadingAction === "evaluation"
                  ? "Evaluating..."
                  : "Run Benchmark"}
              </button>
            </div>

            {error && (
              <p className="mt-5 rounded-xl border border-red-800 bg-red-950/50 p-3 text-sm text-red-300">
                {error}
              </p>
            )}
          </div>

          <div className="space-y-6 lg:col-span-2">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-lg font-semibold">Answer</h2>

              {!answerResult && (
                <div className="mt-5 rounded-2xl border border-dashed border-slate-700 bg-slate-950 p-8 text-center text-slate-500">
                  Generate an answer to see citations, confidence, grounding,
                  and quality scoring.
                </div>
              )}

              {answerResult && (
                <div className="mt-5 space-y-5">
                  <div className="flex flex-wrap gap-2">
                    <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                      {answerResult.retrieval_status}
                    </span>

                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-medium ${qualityClass(
                        answerResult.confidence
                      )}`}
                    >
                      Confidence {percentage(answerResult.confidence)}
                    </span>

                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-medium ${badgeClass(
                        answerResult.quality.grounded
                      )}`}
                    >
                      {answerResult.quality.grounded ? "Grounded" : "Not grounded"}
                    </span>

                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-medium ${qualityClass(
                        answerResult.quality.quality_score
                      )}`}
                    >
                      Quality {percentage(answerResult.quality.quality_score)}
                    </span>

                    <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                      Coverage {percentage(answerResult.quality.query_coverage)}
                    </span>
                  </div>

                  <p className="rounded-2xl border border-slate-800 bg-slate-950 p-5 text-base leading-8 text-slate-100">
                    {answerResult.answer}
                  </p>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <p className="text-sm font-medium text-slate-300">
                        Matched Query Terms
                      </p>

                      <div className="mt-3 flex flex-wrap gap-2">
                        {answerResult.quality.matched_query_terms.map((term) => (
                          <span
                            key={term}
                            className="rounded-full bg-emerald-950 px-3 py-1 text-xs text-emerald-300"
                          >
                            {term}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <p className="text-sm font-medium text-slate-300">
                        Warnings
                      </p>

                      <div className="mt-3 flex flex-wrap gap-2">
                        {answerResult.quality.warnings.length === 0 && (
                          <span className="text-sm text-slate-500">
                            No warnings
                          </span>
                        )}

                        {answerResult.quality.warnings.map((warning) => (
                          <span
                            key={warning}
                            className="rounded-full bg-amber-950 px-3 py-1 text-xs text-amber-300"
                          >
                            {warning}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                    <h3 className="font-semibold">Citations</h3>

                    <div className="mt-4 space-y-4">
                      {answerResult.citations.map((citation) => (
                        <div
                          key={citation.citation_id}
                          className="rounded-2xl border border-slate-800 bg-slate-900 p-4"
                        >
                          <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                            <div>
                              <p className="font-medium text-slate-100">
                                [{citation.citation_id}] {citation.source_filename}
                              </p>

                              <p className="mt-1 text-sm text-slate-500">
                                {citation.document_type} - chunk{" "}
                                {citation.chunk_index}
                              </p>
                            </div>

                            <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                              Score {citation.score}
                            </span>
                          </div>

                          <p className="mt-4 text-sm leading-6 text-slate-300">
                            {citation.quoted_text}
                          </p>

                          <div className="mt-4 flex flex-wrap gap-2">
                            {citation.asset_ids.map((asset) => (
                              <span
                                key={asset}
                                className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300"
                              >
                                {asset}
                              </span>
                            ))}

                            {citation.matched_terms.map((term) => (
                              <span
                                key={term}
                                className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400"
                              >
                                {term}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-lg font-semibold">Search Hits</h2>

              {!searchResult && (
                <div className="mt-5 rounded-2xl border border-dashed border-slate-700 bg-slate-950 p-8 text-center text-slate-500">
                  Run search to inspect retrieved chunks before answering.
                </div>
              )}

              {searchResult && (
                <div className="mt-5 space-y-4">
                  <p className="text-sm text-slate-400">
                    {searchResult.total} hits for &quot;{searchResult.query}&quot;
                  </p>

                  {searchResult.hits.map((hit) => (
                    <div
                      key={hit.chunk_id}
                      className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
                    >
                      <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                        <div>
                          <p className="font-medium">
                            #{hit.rank} {hit.source_filename}
                          </p>

                          <p className="mt-1 text-sm text-slate-500">
                            {hit.document_id} - chunk {hit.chunk_index}
                          </p>
                        </div>

                        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                          Score {hit.score}
                        </span>
                      </div>

                      <p className="mt-4 text-sm leading-6 text-slate-300">
                        {hit.text}
                      </p>

                      <div className="mt-4 flex flex-wrap gap-2">
                        {hit.asset_ids.map((asset) => (
                          <span
                            key={asset}
                            className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300"
                          >
                            {asset}
                          </span>
                        ))}

                        {hit.matched_terms.map((term) => (
                          <span
                            key={term}
                            className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400"
                          >
                            {term}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-lg font-semibold">Evaluation</h2>

              {!evaluationReport && (
                <div className="mt-5 rounded-2xl border border-dashed border-slate-700 bg-slate-950 p-8 text-center text-slate-500">
                  Run the benchmark to validate RAG answer regression quality.
                </div>
              )}

              {evaluationReport && (
                <div className="mt-5 space-y-5">
                  <div className="grid gap-4 md:grid-cols-4">
                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <p className="text-sm text-slate-400">Pass Rate</p>
                      <p className="mt-2 text-2xl font-semibold text-emerald-300">
                        {percentage(evaluationReport.summary.pass_rate)}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <p className="text-sm text-slate-400">Passed</p>
                      <p className="mt-2 text-2xl font-semibold">
                        {evaluationReport.summary.passed_questions}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <p className="text-sm text-slate-400">Failed</p>
                      <p className="mt-2 text-2xl font-semibold text-red-300">
                        {evaluationReport.summary.failed_questions}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <p className="text-sm text-slate-400">Avg Quality</p>
                      <p className="mt-2 text-2xl font-semibold text-cyan-300">
                        {percentage(
                          evaluationReport.summary.average_quality_score
                        )}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    {evaluationReport.results.map((result) => (
                      <div
                        key={result.question_id}
                        className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
                      >
                        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                          <div>
                            <p className="font-medium text-slate-100">
                              {result.question_id}: {result.question}
                            </p>

                            <p className="mt-1 text-sm text-slate-500">
                              {result.retrieval_status} - citations{" "}
                              {result.total_citations}
                            </p>
                          </div>

                          <span
                            className={`rounded-full border px-3 py-1 text-xs font-medium ${badgeClass(
                              result.passed
                            )}`}
                          >
                            {result.passed ? "Passed" : "Failed"}
                          </span>
                        </div>

                        <div className="mt-4 flex flex-wrap gap-2">
                          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                            Quality {percentage(result.quality_score)}
                          </span>

                          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                            Coverage {percentage(result.query_coverage)}
                          </span>

                          {result.warnings.map((warning) => (
                            <span
                              key={warning}
                              className="rounded-full bg-amber-950 px-3 py-1 text-xs text-amber-300"
                            >
                              {warning}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
