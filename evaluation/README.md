# PlantMind Day 3 Evaluation Harness

## Purpose

This folder evaluates PlantMind using actual repository data and, when available, the running API.

The harness covers:

- Entity extraction
- RAG answer correctness, citations, unsupported-claim estimate and latency
- Compliance gap detection
- Knowledge-graph coverage
- RCA quality
- Automatic CSV, JSON, Markdown and chart generation

## Install

From the project root:

```powershell
python -m pip install -r evaluation/requirements-evaluation.txt
```

## Run with the backend

Start FastAPI on `http://127.0.0.1:8000`, then run:

```powershell
python evaluation/run_evaluation.py
```

## Run fully offline

```powershell
python evaluation/run_evaluation.py --offline
```

Offline mode uses an extractive lexical retriever over current PlantMind processed chunks, raw documents and demo JSON. The report records how many answers came from the API and how many used the fallback.

## Outputs

- `evaluation/metrics.json`
- `evaluation/benchmark_results.csv`
- `evaluation/evaluation_report.md`
- `evaluation/rag_results.json`
- `evaluation/charts/*.png`

## Manual retrieval time

No manual timing is invented. To create a real manual-versus-PlantMind comparison:

1. Open `benchmark_questions.json`.
2. Manually answer each question using files without PlantMind.
3. Record the measured duration in `manual_retrieval_seconds`.
4. Rerun the evaluation.

## Interpretation

The command exits successfully even when a target metric is missed. A missed target is a product finding, not a script failure. Technical failures are listed separately in the report.
