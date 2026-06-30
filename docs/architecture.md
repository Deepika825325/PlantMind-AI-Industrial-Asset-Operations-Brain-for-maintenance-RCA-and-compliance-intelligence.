# Architecture Document

## Project Name

**PlantMind AI**

## Project Title

**PlantMind AI: Industrial Asset & Operations Brain for Maintenance, RCA, and Compliance Intelligence**

---

## 1. Purpose of This Document

This document defines the technical architecture of PlantMind AI.

The goal of this architecture is to build a focused, demo-ready, and technically credible industrial intelligence platform that can ingest industrial documents and sensor data, connect them to asset-level knowledge, and provide maintenance, RCA, and compliance intelligence.

This architecture is designed for the frozen hackathon scope:

* P-101 Pump
* C-201 Compressor
* HX-301 Heat Exchanger

No new asset types, major modules, or large integrations should be added after this architecture is finalized.

---

## 2. Architecture Goals

PlantMind AI must achieve the following goals:

1. Ingest industrial documents such as SOPs, maintenance logs, inspection reports, incident reports, compliance checklists, datasheets, and drawings.
2. Extract asset-specific information from documents.
3. Store document chunks and embeddings for semantic search.
4. Answer user questions using Retrieval-Augmented Generation with source citations.
5. Build asset-level knowledge relationships between documents, symptoms, failures, actions, and compliance requirements.
6. Show asset health, risk, maintenance history, and recommendations.
7. Generate structured RCA reports.
8. Detect missing or overdue compliance evidence.
9. Present everything through a clean Next.js user interface.

---

## 3. High-Level Architecture

```text
                         ┌──────────────────────────────┐
                         │          Next.js UI           │
                         │ Dashboard / Assets / Ask AI   │
                         │ RCA / Compliance / Graph      │
                         └───────────────┬──────────────┘
                                         │
                                         │ REST API
                                         ▼
                         ┌──────────────────────────────┐
                         │         FastAPI Backend       │
                         │ API Routes + Orchestration    │
                         └───────┬──────────────┬───────┘
                                 │              │
                                 │              │
              ┌──────────────────▼───┐      ┌───▼──────────────────┐
              │  Document Pipeline    │      │ Sensor Analytics      │
              │  PDF/Text/Image Input │      │ Trends / RUL / Faults │
              └──────────┬───────────┘      └──────────┬───────────┘
                         │                             │
                         ▼                             ▼
              ┌──────────────────────┐      ┌──────────────────────┐
              │ Chunking + Metadata  │      │ Processed Sensor Data │
              │ Asset Tag Extraction │      │ Health Signals        │
              └──────────┬───────────┘      └──────────┬───────────┘
                         │                             │
                         ▼                             ▼
              ┌──────────────────────┐      ┌──────────────────────┐
              │ pgvector Search Index│      │ PostgreSQL Tables     │
              │ Document Embeddings  │      │ Assets / Events       │
              └──────────┬───────────┘      └──────────┬───────────┘
                         │                             │
                         └──────────────┬──────────────┘
                                        ▼
                         ┌──────────────────────────────┐
                         │     Intelligence Layer        │
                         │ RAG / RCA / Compliance / KG   │
                         └───────────────┬──────────────┘
                                         ▼
                         ┌──────────────────────────────┐
                         │      Evidence-Backed Output   │
                         │ Answers / RCA / Actions       │
                         └──────────────────────────────┘
```

---

## 4. Architecture Summary

PlantMind AI follows a modular architecture.

| Layer                       | Responsibility                                                        |
| --------------------------- | --------------------------------------------------------------------- |
| Frontend Layer              | User interface, dashboards, asset views, chat, RCA, compliance, graph |
| API Layer                   | REST endpoints, request validation, response formatting               |
| Document Intelligence Layer | Text extraction, metadata extraction, chunking, embeddings            |
| Sensor Intelligence Layer   | Processed trends, anomaly signals, RUL/fault outputs                  |
| Retrieval Layer             | Semantic search using vector database                                 |
| Knowledge Graph Layer       | Asset-document-symptom-failure-action relationships                   |
| Reasoning Layer             | RAG answers, RCA generation, compliance summaries                     |
| Storage Layer               | PostgreSQL, pgvector, document files, demo JSON data                  |

---

## 5. Technology Stack

## 5.1 Frontend

| Technology     | Purpose                                                       |
| -------------- | ------------------------------------------------------------- |
| Next.js        | Main web application framework                                |
| TypeScript     | Type-safe frontend development                                |
| Tailwind CSS   | Styling                                                       |
| Shadcn UI      | Clean reusable UI components                                  |
| Recharts       | Charts for health score, sensor trends, and risk distribution |
| React Flow     | Knowledge graph visualization                                 |
| TanStack Table | Document and compliance tables                                |

## 5.2 Backend

| Technology | Purpose                                |
| ---------- | -------------------------------------- |
| FastAPI    | Backend REST API                       |
| Python     | AI, data processing, and backend logic |
| Pydantic   | Request and response validation        |
| SQLAlchemy | Database ORM                           |
| Uvicorn    | FastAPI runtime server                 |

## 5.3 AI and Data Layer

| Technology                                                   | Purpose                           |
| ------------------------------------------------------------ | --------------------------------- |
| LangChain or LlamaIndex                                      | RAG pipeline orchestration        |
| Sentence Transformers / OpenAI embeddings / local embeddings | Document embeddings               |
| pgvector                                                     | Vector similarity search          |
| scikit-learn                                                 | Baseline anomaly/fault/RUL models |
| pandas                                                       | Dataset preprocessing             |
| NetworkX or Neo4j                                            | Knowledge graph representation    |

## 5.4 Storage

| Storage                   | Purpose                    |
| ------------------------- | -------------------------- |
| PostgreSQL                | Structured data storage    |
| pgvector                  | Document embedding storage |
| Local filesystem or MinIO | Raw document storage       |
| JSON files                | Demo-ready seed data       |
| CSV files                 | Processed sensor datasets  |

---

## 6. Major System Components

---

## 6.1 Frontend Application

### Location

```text
apps/web/
```

### Responsibility

The frontend provides all user-facing screens for PlantMind AI.

### Screens

```text
Dashboard
Asset 360 View
Ask PlantMind
Knowledge Graph
Compliance Center
RCA Workspace
Document Library
```

### Frontend responsibilities

* Show plant-level dashboard metrics.
* Display asset cards for P-101, C-201, and HX-301.
* Show asset health, risk, sensor trends, documents, and recommendations.
* Provide chat interface for asking industrial questions.
* Display cited answers from RAG pipeline.
* Show knowledge graph relationships.
* Generate and display RCA reports.
* Show compliance evidence status.
* Display indexed document library.

### Frontend API communication

The frontend communicates with the backend through REST APIs.

Example:

```text
GET /api/assets
GET /api/assets/P-101
POST /api/ask
POST /api/rca/generate
GET /api/compliance
GET /api/graph
GET /api/documents
```

---

## 6.2 Backend API

### Location

```text
apps/api/
```

### Responsibility

The backend acts as the central orchestration layer.

It receives requests from the frontend, calls the correct service, fetches data from storage, runs retrieval or reasoning logic, and returns structured responses.

### Backend routes

```text
routes/
├── assets.py
├── documents.py
├── ask.py
├── rca.py
├── compliance.py
├── graph.py
└── health.py
```

### Backend services

```text
services/
├── ingestion_service.py
├── rag_service.py
├── graph_service.py
├── rca_service.py
├── compliance_service.py
├── health_score_service.py
├── sensor_service.py
└── citation_service.py
```

---

## 6.3 Document Intelligence Pipeline

### Responsibility

The document intelligence pipeline converts raw industrial documents into searchable, structured, and citable knowledge.

### Input document types

```text
PDF
TXT
Markdown
PNG
JPG
JPEG
```

### Supported document categories

```text
Datasheet
Maintenance Log
Inspection Report
SOP
Incident Report
Compliance Checklist
RUL Report
Cleaning Record
Drawing
```

### Pipeline flow

```text
Raw Document
    ↓
Text Extraction
    ↓
Asset Tag Detection
    ↓
Document Type Detection
    ↓
Metadata Extraction
    ↓
Chunking
    ↓
Embedding Generation
    ↓
Vector Storage
    ↓
Metadata Storage
    ↓
Citation-Ready Retrieval
```

### Document processing architecture

```text
┌──────────────────────┐
│ Raw Document Folder  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Text/Image Extractor │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Metadata Extractor   │
│ asset_id, doc_type   │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Chunking Engine      │
│ 500 tokens + overlap │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Embedding Generator  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ pgvector Index       │
└──────────────────────┘
```

### Chunking strategy

```text
chunk_size = 500 tokens
chunk_overlap = 80 tokens
```

### Chunk metadata

Each document chunk must store:

```json
{
  "chunk_id": "chunk-p101-ir008-001",
  "asset_id": "P-101",
  "document_id": "IR-008",
  "file_name": "P-101_Inspection_Report_IR-008.pdf",
  "document_type": "Inspection Report",
  "chunk_index": 1,
  "chunk_text": "Inspection Report IR-008 shows vibration above critical threshold..."
}
```

---

## 6.4 Retrieval-Augmented Generation Pipeline

### Responsibility

The RAG pipeline answers user questions using retrieved industrial evidence.

### RAG flow

```text
User Question
    ↓
Query Understanding
    ↓
Asset ID Detection
    ↓
Vector Search
    ↓
Metadata Filtering
    ↓
Top-K Evidence Retrieval
    ↓
Prompt Construction
    ↓
LLM Answer Generation
    ↓
Citation Formatting
    ↓
Response to UI
```

### RAG architecture

```text
┌──────────────────────┐
│ User Question        │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Asset Detection      │
│ P-101 / C-201 / HX   │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Vector Search        │
│ pgvector similarity  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Evidence Ranking     │
│ Top-K chunks         │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ RAG Prompt Builder   │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ LLM Reasoning        │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Cited Answer         │
└──────────────────────┘
```

### Retrieval rules

1. If the question contains an asset ID, filter search by that asset.
2. If the question asks about compliance, prioritize compliance checklists and SOPs.
3. If the question asks about RCA, prioritize incident reports, inspection reports, maintenance logs, and SOPs.
4. If the question asks about maintenance planning, prioritize RUL reports, inspection reports, and maintenance logs.
5. Every answer must include source documents.
6. If evidence is missing, the system must say that evidence was not found.

### Top-K retrieval setting

```text
top_k = 5
```

### Required answer format

```text
Answer:
<clear explanation>

Recommended Action:
<actionable maintenance recommendation>

Sources:
1. <source document>
2. <source document>
3. <source document>
```

---

## 6.5 Knowledge Graph Layer

### Responsibility

The knowledge graph connects industrial knowledge into explainable relationships.

### Graph model

```text
Asset → Document → Symptom → Failure Mode → Maintenance Action → Compliance Requirement
```

### Node types

```text
Asset
Document
Symptom
Failure Mode
Maintenance Action
Compliance Requirement
```

### Edge types

```text
HAS_DOCUMENT
HAS_SYMPTOM
INDICATES_FAILURE
REQUIRES_ACTION
HAS_COMPLIANCE_REQUIREMENT
EVIDENCE_FOR
```

### Example graph path

```text
P-101
  → High Vibration
  → Bearing Wear
  → Inspect Bearing Housing
  → Weekly Lubrication Check
  → P-101_Compliance_Checklist.pdf
```

### Graph storage options

For the hackathon, use one of the following:

| Option           | Recommendation                        |
| ---------------- | ------------------------------------- |
| JSON-based graph | Best for fastest implementation       |
| NetworkX         | Good for Python-side graph processing |
| Neo4j            | Good for advanced demo if time allows |

### Recommended MVP approach

Use `knowledge_graph.json` for the first version.

Reason:

* Easy to build
* Easy to debug
* Easy to visualize with React Flow
* No extra infrastructure needed

### Graph JSON format

```json
{
  "nodes": [
    {
      "id": "P-101",
      "label": "P-101 Pump",
      "type": "Asset"
    },
    {
      "id": "High Vibration",
      "label": "High Vibration",
      "type": "Symptom"
    }
  ],
  "edges": [
    {
      "source": "P-101",
      "target": "High Vibration",
      "relationship": "HAS_SYMPTOM",
      "evidence": "P-101_Inspection_Report_IR-008.pdf"
    }
  ]
}
```

---

## 6.6 Sensor Intelligence Layer

### Responsibility

The sensor intelligence layer provides predictive-maintenance context.

It is not the main system, but it increases technical credibility.

### Asset-to-dataset mapping

| Asset                 | Dataset                   | Sensor Intelligence Output                |
| --------------------- | ------------------------- | ----------------------------------------- |
| P-101 Pump            | CWRU Bearing Dataset      | Bearing fault / vibration risk            |
| C-201 Compressor      | NASA C-MAPSS              | Remaining Useful Life trend               |
| HX-301 Heat Exchanger | Tennessee Eastman Process | Process anomaly / fouling-style deviation |

### Sensor pipeline

```text
Raw Public Dataset
    ↓
Preprocessing
    ↓
Feature Engineering
    ↓
Baseline Model or Rule Engine
    ↓
Processed CSV / JSON
    ↓
Health Score Service
    ↓
Dashboard + Asset 360
```

### MVP sensor outputs

```text
p101_vibration_trend.csv
p101_fault_summary.json
c201_rul_predictions.csv
c201_sensor_trend.csv
hx301_process_trend.csv
hx301_fouling_summary.json
```

### Important design decision

The system should not depend on real-time sensor streaming.

For hackathon demo, use preprocessed CSV and JSON outputs.

This keeps the demo stable and avoids unnecessary infrastructure complexity.

---

## 6.7 Health Score Service

### Responsibility

The health score service calculates asset health and risk level.

### MVP approach

Use rule-based scoring.

### Formula

```text
Base health score = 100

Subtract:
- 20 points for critical sensor anomaly
- 15 points for missing compliance evidence
- 10 points for overdue maintenance
- 10 points for repeated maintenance symptom
- 5 points for delayed evidence
```

### Risk level rules

```text
Health Score >= 80: Low Risk
Health Score 65-79: Medium Risk
Health Score < 65: High Risk
```

### Frozen demo scores

| Asset  | Health Score | Risk Level | Main Reason                                   |
| ------ | -----------: | ---------- | --------------------------------------------- |
| P-101  |           62 | High       | High vibration + missing lubrication evidence |
| C-201  |           71 | Medium     | RUL decreasing + delayed filter replacement   |
| HX-301 |           68 | Medium     | Fouling suspected + cleaning overdue          |

### Health score output format

```json
{
  "asset_id": "P-101",
  "health_score": 62,
  "risk_level": "High",
  "risk_drivers": [
    "Vibration above threshold",
    "Abnormal bearing noise",
    "Missing lubrication evidence"
  ],
  "recommended_action": "Inspect bearing housing and verify lubrication"
}
```

---

## 6.8 RCA Service

### Responsibility

The RCA service generates structured root-cause analysis reports.

### RCA input

```json
{
  "asset_id": "P-101",
  "issue": "High vibration"
}
```

### RCA pipeline

```text
Asset + Issue
    ↓
Retrieve inspection reports
    ↓
Retrieve maintenance logs
    ↓
Retrieve incident reports
    ↓
Retrieve SOPs
    ↓
Retrieve compliance checklist
    ↓
Generate structured RCA
    ↓
Attach citations
```

### RCA output sections

```text
Problem Statement
Observed Symptoms
Evidence
Timeline
Possible Causes
Most Likely Root Cause
Corrective Action
Preventive Action
Confidence Level
Sources
```

### RCA output format

```json
{
  "asset_id": "P-101",
  "issue": "High vibration",
  "problem_statement": "P-101 is showing repeated high vibration events during normal operation.",
  "observed_symptoms": [
    "Vibration above threshold",
    "Abnormal bearing noise",
    "Missing lubrication evidence"
  ],
  "likely_root_cause": "Bearing wear caused by lubrication degradation or possible shaft misalignment.",
  "corrective_action": "Inspect bearing housing, verify lubrication, check alignment, and replace bearing if required.",
  "preventive_action": "Add weekly lubrication evidence verification and vibration trend alert.",
  "confidence": "Medium-High",
  "sources": [
    "P-101_Inspection_Report_IR-008.pdf",
    "P-101_Maintenance_Log_Jan2026.pdf",
    "P-101_Compliance_Checklist.pdf"
  ]
}
```

---

## 6.9 Compliance Service

### Responsibility

The compliance service detects missing, overdue, available, or delayed evidence.

### Compliance statuses

```text
Available
Missing
Overdue
Delayed
Not Required
```

### Compliance matrix

| Asset  | Requirement                     | Evidence                           | Status    |
| ------ | ------------------------------- | ---------------------------------- | --------- |
| P-101  | Weekly vibration inspection     | P-101_Inspection_Report_IR-008.pdf | Available |
| P-101  | Weekly lubrication check        | Missing                            | Missing   |
| C-201  | Monthly compressor inspection   | C-201_Inspection_Report.pdf        | Available |
| C-201  | Filter replacement verification | C-201_Maintenance_Log_Feb2026.pdf  | Delayed   |
| HX-301 | Pressure test report            | HX-301_SOP_Pressure_Test.pdf       | Available |
| HX-301 | Cleaning and fouling inspection | Missing or overdue                 | Overdue   |

### Compliance service output

```json
{
  "total_requirements": 6,
  "available": 3,
  "missing": 1,
  "overdue": 1,
  "delayed": 1,
  "gaps": [
    {
      "asset_id": "P-101",
      "requirement": "Weekly lubrication check",
      "status": "Missing",
      "recommended_action": "Perform lubrication check and upload evidence"
    },
    {
      "asset_id": "HX-301",
      "requirement": "Cleaning and fouling inspection",
      "status": "Overdue",
      "recommended_action": "Schedule cleaning inspection"
    }
  ]
}
```

---

## 7. API Architecture

## 7.1 API Route Summary

| Method | Endpoint                        | Purpose                           |
| ------ | ------------------------------- | --------------------------------- |
| GET    | `/api/assets`                   | Get all assets                    |
| GET    | `/api/assets/{asset_id}`        | Get asset details                 |
| GET    | `/api/assets/{asset_id}/health` | Get health score and risk drivers |
| GET    | `/api/assets/{asset_id}/events` | Get maintenance events            |
| GET    | `/api/documents`                | Get document library              |
| GET    | `/api/documents/{document_id}`  | Get document details              |
| POST   | `/api/documents/ingest`         | Ingest documents                  |
| POST   | `/api/ask`                      | Ask PlantMind question            |
| POST   | `/api/rca/generate`             | Generate RCA report               |
| GET    | `/api/compliance`               | Get compliance matrix             |
| GET    | `/api/compliance/summary`       | Get compliance summary            |
| GET    | `/api/graph`                    | Get full knowledge graph          |
| GET    | `/api/graph/{asset_id}`         | Get asset-specific graph          |

---

## 7.2 Example API: Ask PlantMind

### Endpoint

```text
POST /api/ask
```

### Request

```json
{
  "question": "Why is P-101 high risk?",
  "asset_id": "P-101"
}
```

### Response

```json
{
  "answer": "P-101 is marked as high risk because inspection report IR-008 shows vibration above threshold, the maintenance log mentions abnormal bearing noise, and the compliance checklist shows missing lubrication evidence.",
  "recommended_action": "Inspect bearing housing, verify lubrication level, check shaft alignment, and schedule maintenance.",
  "sources": [
    {
      "document_id": "IR-008",
      "file_name": "P-101_Inspection_Report_IR-008.pdf",
      "document_type": "Inspection Report"
    },
    {
      "document_id": "ML-014",
      "file_name": "P-101_Maintenance_Log_Jan2026.pdf",
      "document_type": "Maintenance Log"
    },
    {
      "document_id": "CC-P101-001",
      "file_name": "P-101_Compliance_Checklist.pdf",
      "document_type": "Compliance Checklist"
    }
  ]
}
```

---

## 7.3 Example API: Generate RCA

### Endpoint

```text
POST /api/rca/generate
```

### Request

```json
{
  "asset_id": "P-101",
  "issue": "High vibration"
}
```

### Response

```json
{
  "asset_id": "P-101",
  "issue": "High vibration",
  "problem_statement": "P-101 is showing repeated high vibration events during normal operation.",
  "observed_symptoms": [
    "Vibration above threshold",
    "Abnormal bearing noise",
    "Missing lubrication evidence"
  ],
  "possible_causes": [
    "Bearing wear",
    "Lubrication degradation",
    "Shaft misalignment",
    "Loose mounting"
  ],
  "likely_root_cause": "Bearing wear caused by lubrication degradation or possible shaft misalignment.",
  "corrective_action": "Inspect bearing housing, verify lubrication, check alignment, and replace bearing if required.",
  "preventive_action": "Add weekly lubrication evidence verification and vibration trend alert.",
  "confidence": "Medium-High",
  "sources": [
    "P-101_Inspection_Report_IR-008.pdf",
    "P-101_Maintenance_Log_Jan2026.pdf",
    "P-101_Compliance_Checklist.pdf"
  ]
}
```

---

## 8. Database Architecture

## 8.1 PostgreSQL Tables

### assets

Stores asset metadata.

```text
assets
├── id
├── asset_id
├── asset_name
├── asset_type
├── criticality
├── location
├── health_score
├── risk_level
├── main_issue
├── recommended_action
├── created_at
└── updated_at
```

### documents

Stores document metadata.

```text
documents
├── id
├── document_id
├── file_name
├── asset_id
├── document_type
├── document_date
├── source_type
├── file_path
├── indexed
├── summary
├── created_at
└── updated_at
```

### document_chunks

Stores chunks and vector embeddings.

```text
document_chunks
├── id
├── document_id
├── asset_id
├── file_name
├── document_type
├── chunk_index
├── chunk_text
├── embedding
├── created_at
└── updated_at
```

### maintenance_events

Stores maintenance and inspection events.

```text
maintenance_events
├── id
├── event_id
├── asset_id
├── event_date
├── event_type
├── description
├── recommended_action
├── source_document_id
├── created_at
└── updated_at
```

### compliance_requirements

Stores compliance evidence status.

```text
compliance_requirements
├── id
├── asset_id
├── requirement
├── expected_evidence
├── status
├── evidence_file
├── gap_reason
├── recommended_action
├── created_at
└── updated_at
```

### health_scores

Stores asset health score and risk drivers.

```text
health_scores
├── id
├── asset_id
├── health_score
├── risk_level
├── risk_drivers
├── recommended_action
├── updated_at
```

### rca_reports

Stores generated RCA reports.

```text
rca_reports
├── id
├── asset_id
├── issue
├── problem_statement
├── observed_symptoms
├── possible_causes
├── likely_root_cause
├── corrective_action
├── preventive_action
├── confidence
├── sources
├── created_at
└── updated_at
```

---

## 8.2 Vector Search Table

### document_chunks with pgvector

Recommended schema concept:

```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id TEXT,
    asset_id TEXT,
    file_name TEXT,
    document_type TEXT,
    chunk_index INTEGER,
    chunk_text TEXT,
    embedding VECTOR(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

The vector dimension depends on the embedding model.

Example:

| Embedding Model        | Vector Dimension |
| ---------------------- | ---------------: |
| all-MiniLM-L6-v2       |              384 |
| text-embedding-3-small |             1536 |

Use the correct vector dimension based on the selected embedding model.

---

## 9. Data Flow

## 9.1 Document Ingestion Data Flow

```text
Synthetic Documents
    ↓
ingest_documents.py
    ↓
Text Extraction
    ↓
Metadata Extraction
    ↓
Chunking
    ↓
Embedding
    ↓
PostgreSQL + pgvector
    ↓
Ask PlantMind / RCA / Compliance / Graph
```

## 9.2 Ask PlantMind Data Flow

```text
User asks: "Why is P-101 high risk?"
    ↓
Frontend sends POST /api/ask
    ↓
Backend detects asset_id = P-101
    ↓
Vector search filters chunks by P-101
    ↓
Top evidence chunks retrieved
    ↓
RAG prompt created
    ↓
LLM generates cited answer
    ↓
Backend returns answer + sources
    ↓
Frontend displays answer and citations
```

## 9.3 RCA Data Flow

```text
User selects P-101 + High vibration
    ↓
Frontend sends POST /api/rca/generate
    ↓
Backend retrieves P-101 evidence
    ↓
RCA service structures findings
    ↓
LLM or template generates RCA report
    ↓
Sources are attached
    ↓
Frontend displays RCA report
```

## 9.4 Compliance Data Flow

```text
Compliance matrix loaded
    ↓
Compliance service checks status
    ↓
Missing / overdue / delayed evidence identified
    ↓
Summary generated
    ↓
Frontend displays compliance gaps
```

## 9.5 Knowledge Graph Data Flow

```text
Document metadata + extracted facts
    ↓
Graph service creates nodes and edges
    ↓
knowledge_graph.json or graph database updated
    ↓
Frontend fetches /api/graph
    ↓
React Flow renders graph
```

---

## 10. Deployment Architecture

## 10.1 Local Development

```text
Developer Machine
├── Next.js frontend
├── FastAPI backend
├── PostgreSQL + pgvector
└── Local document storage
```

## 10.2 Docker-Based Development

Use Docker Compose for stable setup.

```text
docker-compose.yml
├── web
├── api
├── postgres
└── optional-minio
```

### Recommended services

```yaml
services:
  web:
    description: Next.js frontend

  api:
    description: FastAPI backend

  postgres:
    description: PostgreSQL database with pgvector

  minio:
    description: Optional object storage for documents
```

## 10.3 Hackathon Deployment

Recommended deployment:

| Component    | Deployment Option                                       |
| ------------ | ------------------------------------------------------- |
| Frontend     | Vercel                                                  |
| Backend      | Render, Railway, Fly.io, or Docker VM                   |
| Database     | Supabase PostgreSQL with pgvector or Railway PostgreSQL |
| File storage | Local demo folder, Supabase storage, or MinIO           |
| Demo data    | Seeded JSON + database tables                           |

### Simplest deployment option

For fastest hackathon deployment:

```text
Frontend: Vercel
Backend: Render
Database: Supabase PostgreSQL with pgvector
Documents: Preloaded demo files
```

---

## 11. Security and Safety Architecture

PlantMind AI is a decision-support system, not an autonomous plant control system.

### Safety boundaries

The system must not:

* Start or stop equipment.
* Automatically execute work orders.
* Override safety procedures.
* Provide safety-critical control commands.
* Claim guaranteed fault diagnosis.
* Replace qualified engineers.

### Safe wording

Use phrases like:

```text
Recommended action
Suggested inspection
Possible failure mode
Likely root cause
Evidence indicates
Requires engineer review
```

Avoid phrases like:

```text
Guaranteed failure
Must shut down immediately
Automatically execute
Confirmed root cause
```

### Data safety

For hackathon demo:

* Use synthetic documents.
* Do not include confidential industrial data.
* Clearly mention public and synthetic dataset usage.
* Do not claim that synthetic documents are real plant records.

---

## 12. Reliability and Demo Stability

To keep the final demo stable, PlantMind AI should support fallback data.

### Fallback strategy

| Feature                | Fallback                                      |
| ---------------------- | --------------------------------------------- |
| RAG answer is weak     | Use suggested questions with strong retrieval |
| LLM response is slow   | Use cached demo answer                        |
| Sensor model not ready | Use precomputed CSV trend                     |
| Graph service fails    | Load static `knowledge_graph.json`            |
| Document upload fails  | Use preloaded indexed documents               |
| RCA generation is slow | Use pre-generated RCA template                |
| Deployment issue       | Run local Docker version                      |

### Cached demo files

```text
data/demo/assets.json
data/demo/documents.json
data/demo/compliance_matrix.json
data/demo/health_scores.json
data/demo/knowledge_graph.json
data/demo/demo_answers.json
```

---

## 13. File and Folder Architecture

```text
plantmind-ai/
│
├── README.md
├── docker-compose.yml
├── .env.example
│
├── apps/
│   ├── web/
│   │   ├── app/
│   │   │   ├── dashboard/
│   │   │   ├── assets/
│   │   │   │   └── [assetId]/
│   │   │   ├── ask/
│   │   │   ├── graph/
│   │   │   ├── compliance/
│   │   │   ├── rca/
│   │   │   └── documents/
│   │   ├── components/
│   │   │   ├── asset-card.tsx
│   │   │   ├── health-score.tsx
│   │   │   ├── risk-badge.tsx
│   │   │   ├── evidence-panel.tsx
│   │   │   ├── knowledge-graph.tsx
│   │   │   └── citation-card.tsx
│   │   └── lib/
│   │
│   └── api/
│       ├── main.py
│       ├── routes/
│       │   ├── assets.py
│       │   ├── documents.py
│       │   ├── ask.py
│       │   ├── rca.py
│       │   ├── compliance.py
│       │   ├── graph.py
│       │   └── health.py
│       ├── services/
│       │   ├── ingestion_service.py
│       │   ├── rag_service.py
│       │   ├── graph_service.py
│       │   ├── rca_service.py
│       │   ├── compliance_service.py
│       │   ├── health_score_service.py
│       │   ├── sensor_service.py
│       │   └── citation_service.py
│       ├── models/
│       ├── db/
│       └── schemas/
│
├── data/
│   ├── raw/
│   │   ├── public/
│   │   │   ├── cmapss/
│   │   │   ├── cwru_bearing/
│   │   │   └── tennessee_eastman/
│   │   └── documents/
│   │       ├── P-101/
│   │       ├── C-201/
│   │       └── HX-301/
│   ├── processed/
│   │   ├── p101/
│   │   ├── c201/
│   │   └── hx301/
│   └── demo/
│
├── notebooks/
│   ├── 01_cmapss_rul_baseline.ipynb
│   ├── 02_cwru_bearing_fault_baseline.ipynb
│   └── 03_hx301_process_anomaly_baseline.ipynb
│
├── scripts/
│   ├── ingest_documents.py
│   ├── build_vector_index.py
│   ├── build_knowledge_graph.py
│   ├── seed_assets.py
│   ├── seed_demo_data.py
│   └── generate_synthetic_docs.py
│
└── docs/
    ├── scope_freeze.md
    ├── architecture.md
    ├── dataset_plan.md
    ├── ui_screen_list.md
    └── demo_script.md
```

---

## 14. Environment Variables

Use `.env.example`.

```env
# Backend
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/plantmind

# Vector Database
VECTOR_DIMENSION=384

# Embedding Model
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=gpt-4o-mini

# Storage
DOCUMENT_STORAGE_PATH=./data/raw/documents

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

---

## 15. Key Design Decisions

## 15.1 Use Next.js for UI

Reason:

* Fast frontend development
* Good routing
* Easy dashboard creation
* Easy deployment on Vercel
* Strong ecosystem for charts and graph UI

## 15.2 Use FastAPI for backend

Reason:

* Python-friendly AI development
* Easy REST API development
* Works well with ML/RAG pipelines
* Good integration with Pydantic and SQLAlchemy

## 15.3 Use PostgreSQL + pgvector

Reason:

* One database can store structured data and embeddings.
* Easier deployment than separate vector database.
* Good enough for hackathon scale.
* Supports semantic search through vector similarity.

## 15.4 Use synthetic documents

Reason:

* Real industrial documents are hard to access.
* Synthetic documents allow controlled citations.
* The demo can be stable and consistent.
* It matches the hackathon problem statement well.

## 15.5 Use rule-based health scoring first

Reason:

* Explainable
* Fast to implement
* Stable in demo
* Easy for judges to understand

## 15.6 Use public datasets as proxies

Reason:

* Adds technical credibility.
* Shows predictive-maintenance capability.
* Avoids dependency on unavailable real plant sensor data.

---

## 16. MVP Architecture

The minimum viable architecture for a successful demo is:

```text
Next.js UI
    ↓
FastAPI backend
    ↓
Preloaded demo JSON + PostgreSQL
    ↓
RAG using indexed synthetic documents
    ↓
Static knowledge_graph.json
    ↓
Rule-based health and compliance services
```

### MVP must support

```text
Dashboard
Asset 360
Ask PlantMind
RCA Workspace
Compliance Center
Knowledge Graph
Document Library
```

### MVP does not require

```text
Live IoT streaming
Real-time model inference
Complex OCR
Neo4j
User authentication
SAP/Maximo integration
Full document upload workflow
```

---

## 17. Future Architecture Extensions

These are not part of the hackathon build, but can be mentioned as future scope.

| Future Extension      | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| CMMS Integration      | Connect to SAP PM, IBM Maximo, or Fiix                     |
| Real-Time IoT         | Stream sensor data through MQTT or Kafka                   |
| Advanced OCR          | Extract symbols and tags from complex engineering drawings |
| Multi-Plant Support   | Support multiple sites and asset hierarchies               |
| Work Order Automation | Generate draft work orders for engineer approval           |
| Role-Based Access     | Engineer, manager, compliance officer views                |
| Advanced Digital Twin | Connect knowledge graph to physical asset models           |
| Enterprise Search     | Search across all plant knowledge repositories             |

---

## 18. Architecture Success Criteria

The architecture is successful if PlantMind AI can demonstrate the following:

| Capability                | Architecture Component Responsible |
| ------------------------- | ---------------------------------- |
| Asset dashboard           | Frontend + Asset API               |
| Health score              | Health Score Service               |
| Sensor trend              | Sensor Service + processed CSV     |
| RAG answer with citations | RAG Service + pgvector             |
| RCA report                | RCA Service                        |
| Compliance gap detection  | Compliance Service                 |
| Knowledge graph           | Graph Service + React Flow         |
| Document library          | Document Service                   |
| Stable demo flow          | Demo JSON fallback data            |

---

## 19. Final Architecture Statement

PlantMind AI uses a modular architecture with a Next.js frontend, FastAPI backend, PostgreSQL database, pgvector semantic search, document intelligence pipeline, knowledge graph layer, rule-based health scoring, RCA generation, and compliance evidence checking.

The architecture is intentionally scoped to three industrial assets:

```text
P-101 Pump
C-201 Compressor
HX-301 Heat Exchanger
```

The final demo architecture supports this workflow:

```text
Industrial Documents + Sensor Trends
        ↓
Document Intelligence + Metadata Extraction
        ↓
Vector Search + Knowledge Graph
        ↓
RAG Answers + RCA + Compliance Checking
        ↓
Evidence-Backed Maintenance Recommendation
```

PlantMind AI is not a full CMMS, ERP, or real-time control system. It is an explainable industrial intelligence layer that helps maintenance teams convert scattered asset knowledge into faster, safer, evidence-backed decisions.
