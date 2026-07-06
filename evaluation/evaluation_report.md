# PlantMind Evaluation Report

Generated at: `2026-07-06T11:32:28.933418Z`

## Execution Summary

- Benchmark questions: **20**
- API answers: **20**
- Offline fallback answers: **0**
- Technical evaluation errors: **0**

Results are calculated from the current repository state. No metric is manually substituted or fabricated.

## Target Metrics

| Target | Actual | Requirement | Status |
|---|---:|---:|---|
| entity_extraction_f1 | 0.936 | >= 0.9 | PASS |
| citation_precision | 1.000 | >= 0.85 | PASS |
| citation_coverage | 1.000 | >= 0.9 | PASS |
| compliance_gap_recall | 1.000 | >= 0.8 | PASS |
| graph_link_completeness | 1.000 | >= 0.9 | PASS |
| unsupported_claim_rate | 0.075 | < 0.1 | PASS |
| average_answer_latency_seconds | 0.022 | < 5.0 | PASS |

## Entity Extraction

- Precision: **100.0%**
- Recall: **88.0%**
- F1: **93.6%**
- Equipment-tag accuracy: **80.0%**
- Failure-mode accuracy: **90.0%**
- Work-order ID accuracy: **100.0%**

## RAG

- Answer correctness: **91.7%**
- Citation precision: **100.0%**
- Citation recall: **95.0%**
- Citation coverage: **100.0%**
- Unsupported-claim rate: **7.5%**
- Average answer latency: **0.022 seconds**

The unsupported-claim metric is a lexical support estimate against returned or retrieved evidence. It is not an LLM-based factuality judge.

## Compliance

- Gap-detection precision: **93.3%**
- Gap-detection recall: **100.0%**
- Gap-detection F1: **96.5%**
- Severity accuracy: **100.0%**
- Evidence-link accuracy: **95.5%**

## Knowledge Graph

- Node coverage: **100.0%**
- Edge coverage: **100.0%**
- Asset-document linkage accuracy: **100.0%**
- Broken-link count: **0**

## RCA

- Root-cause top-1 accuracy: **100.0%**
- Evidence coverage: **100.0%**
- Counter-evidence coverage: **100.0%**
- Action relevance: **100.0%**

## Charts

- `charts/accuracy_by_module.png`
- `charts/citation_performance.png`
- `charts/latency_comparison.png`
- `charts/manual_vs_plantmind_retrieval_time.png`
- `charts/compliance_detection_performance.png`

## Manual Retrieval Timing

Manual retrieval time has not been measured. Fill `manual_retrieval_seconds` in `benchmark_questions.json` and rerun the evaluation to produce a true comparison.

## Generated Outputs

- `metrics.json`
- `benchmark_results.csv`
- `evaluation_report.md`
- `rag_results.json`
- `charts/accuracy_by_module.png`
- `charts/citation_performance.png`
- `charts/latency_comparison.png`
- `charts/manual_vs_plantmind_retrieval_time.png`
- `charts/compliance_detection_performance.png`
