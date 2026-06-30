# PlantMind AI

## Industrial Asset & Operations Brain for Maintenance, RCA, and Compliance Intelligence

PlantMind AI is an industrial knowledge intelligence platform that converts scattered maintenance records, SOPs, inspection reports, incident reports, compliance checklists, asset datasheets, engineering drawings, and sensor trends into an explainable asset intelligence system.

It helps maintenance and operations teams answer asset-specific questions, investigate failures, generate root-cause analysis reports, detect missing compliance evidence, and recommend maintenance actions using cited evidence.

---

## 1. Project Overview

Industrial plants generate large volumes of operational knowledge across many disconnected sources:

* Maintenance logs
* Inspection reports
* Standard Operating Procedures
* Safety procedures
* Compliance checklists
* Incident reports
* Asset datasheets
* Engineering drawings
* Sensor and condition-monitoring data

When an asset begins showing abnormal behavior, engineers often need to manually search across multiple files and systems to understand what happened, what evidence exists, what action should be taken, and whether compliance requirements are satisfied.

PlantMind AI solves this by creating an **Industrial Asset & Operations Brain**.

The system connects documents, sensor trends, asset metadata, symptoms, failure modes, compliance requirements, and maintenance recommendations into one explainable workflow.

---

## 2. One-Line Pitch

**PlantMind AI helps industrial maintenance teams move from scattered documents and sensor signals to evidence-backed maintenance decisions, RCA reports, and compliance actions.**

---

## 3. Demo Plant Scope

The project is intentionally scoped to three industrial assets only.

| Asset ID | Asset Name     | Asset Type         | Main Demo Use Case                                               |
| -------- | -------------- | ------------------ | ---------------------------------------------------------------- |
| P-101    | Pump           | Rotating Equipment | High vibration, bearing wear, missing lubrication evidence       |
| C-201    | Compressor     | Rotating Equipment | Decreasing RUL, pressure instability, maintenance planning       |
| HX-301   | Heat Exchanger | Process Equipment  | Fouling suspicion, reduced efficiency, overdue cleaning evidence |

This scope is frozen to keep the project focused, technically credible, and demo-ready.

---

## 4. Core Features

## 4.1 Ask PlantMind

A Retrieval-Augmented Generation assistant that answers industrial maintenance and compliance questions with source citations.

Example questions:

```text
Why is P-101 high risk?
Generate RCA for P-101 high vibration.
Which assets are non-compliant?
What maintenance should be planned for C-201?
What evidence is missing for HX-301?
```

Example output:

```text
P-101 is marked as high risk because inspection report IR-008 shows vibration above the critical threshold, the maintenance log mentions abnormal bearing noise, and the compliance checklist shows missing weekly lubrication evidence.

Recommended Action:
Inspect the bearing housing, verify lubrication level, check shaft alignment, and schedule maintenance before continued operation increases failure risk.

Sources:
1. P-101_Inspection_Report_IR-008.pdf
2. P-101_Maintenance_Log_Jan2026.pdf
3. P-101_SOP_Lubrication_and_Bearing_Check.pdf
4. P-101_Compliance_Checklist.pdf
```

---

## 4.2 Asset 360 View

Each asset has a complete intelligence profile showing:

* Asset metadata
* Health score
* Risk level
* Main risk drivers
* Sensor trends
* Maintenance history
* Linked documents
* Compliance status
* Recommended action
* RCA summary

Example:

| Asset                 | Health Score | Risk Level | Main Issue                                    |
| --------------------- | -----------: | ---------- | --------------------------------------------- |
| P-101 Pump            |          62% | High       | High vibration + missing lubrication evidence |
| C-201 Compressor      |          71% | Medium     | RUL decreasing + delayed filter replacement   |
| HX-301 Heat Exchanger |          68% | Medium     | Fouling suspected + cleaning overdue          |

---

## 4.3 Root Cause Analysis Assistant

PlantMind AI generates structured RCA reports using document evidence, maintenance history, inspection findings, SOPs, compliance status, and sensor signals.

RCA report sections:

* Problem statement
* Observed symptoms
* Evidence
* Timeline
* Possible causes
* Most likely root cause
* Corrective action
* Preventive action
* Confidence level
* Source documents

Example RCA use case:

```text
Asset: P-101
Issue: High vibration
```

Expected RCA conclusion:

```text
Most Likely Root Cause:
Bearing wear caused by lubrication degradation or possible shaft misalignment.

Corrective Action:
Inspect bearing housing, verify lubrication level, check shaft alignment, inspect mounting bolts, and replace bearing if vibration remains above threshold.

Preventive Action:
Add weekly lubrication evidence verification, monitor vibration trend automatically, and trigger alerts when vibration crosses warning threshold.
```

---

## 4.4 Compliance Evidence Checker

The Compliance Center detects missing, overdue, available, or delayed evidence.

Example compliance matrix:

| Asset  | Requirement                     | Evidence                           | Status    |
| ------ | ------------------------------- | ---------------------------------- | --------- |
| P-101  | Weekly vibration inspection     | P-101_Inspection_Report_IR-008.pdf | Available |
| P-101  | Weekly lubrication check        | Missing                            | Missing   |
| C-201  | Monthly compressor inspection   | C-201_Inspection_Report.pdf        | Available |
| C-201  | Filter replacement verification | C-201_Maintenance_Log_Feb2026.pdf  | Delayed   |
| HX-301 | Pressure test report            | HX-301_SOP_Pressure_Test.pdf       | Available |
| HX-301 | Cleaning and fouling inspection | Missing or overdue                 | Overdue   |

---

## 4.5 Asset Knowledge Graph

PlantMind AI connects assets, documents, symptoms, failure modes, maintenance actions, and compliance requirements.

Example graph path:

```text
P-101 Pump
  → High Vibration
  → Bearing Wear
  → Lubrication Evidence Missing
  → SOP-PUMP-01
  → Weekly Lubrication Inspection
  → Inspect Bearing Housing
```

Supported graph node types:

* Asset
* Document
* Symptom
* Failure Mode
* Maintenance Action
* Compliance Requirement

Supported graph relationships:

* `HAS_DOCUMENT`
* `HAS_SYMPTOM`
* `INDICATES_FAILURE`
* `REQUIRES_ACTION`
* `HAS_COMPLIANCE_REQUIREMENT`
* `EVIDENCE_FOR`

---

## 5. Demo Story

The primary demo story focuses on **P-101 Pump**.

```text
P-101 is showing high vibration.

PlantMind AI explains that the risk is caused by vibration above threshold, abnormal bearing noise, and missing lubrication evidence.

It cites inspection reports, maintenance logs, SOPs, and compliance checklists.

It shows the relationship between the asset, symptom, possible failure mode, evidence, and maintenance action.

It generates a root-cause analysis report.

It detects missing compliance evidence.

It recommends corrective and preventive maintenance action.
```

Final demo workflow:

```text
Dashboard
  ↓
Ask PlantMind
  ↓
Asset 360 View
  ↓
Knowledge Graph
  ↓
RCA Workspace
  ↓
Compliance Center
  ↓
Document Library
```

---

## 6. System Architecture

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

## 7. Technology Stack

## 7.1 Frontend

| Technology     | Purpose                             |
| -------------- | ----------------------------------- |
| Next.js        | Main frontend framework             |
| TypeScript     | Type-safe UI development            |
| Tailwind CSS   | Styling                             |
| Shadcn UI      | Reusable UI components              |
| Recharts       | Charts and trends                   |
| React Flow     | Knowledge graph visualization       |
| TanStack Table | Tables for documents and compliance |
| Lucide React   | Icons                               |

---

## 7.2 Backend

| Technology | Purpose                                   |
| ---------- | ----------------------------------------- |
| FastAPI    | Backend REST API                          |
| Python     | AI, data processing, and backend services |
| Pydantic   | Request and response validation           |
| SQLAlchemy | Database ORM                              |
| Uvicorn    | FastAPI runtime                           |

---

## 7.3 AI and Data Layer

| Technology                                | Purpose                        |
| ----------------------------------------- | ------------------------------ |
| LangChain or LlamaIndex                   | RAG orchestration              |
| Sentence Transformers / OpenAI Embeddings | Embedding generation           |
| PostgreSQL                                | Structured data storage        |
| pgvector                                  | Semantic vector search         |
| pandas                                    | Data preprocessing             |
| scikit-learn                              | Baseline ML models             |
| NetworkX or JSON graph                    | Knowledge graph representation |

---

## 8. Dataset Strategy

PlantMind AI uses a hybrid dataset strategy.

## 8.1 Public Predictive Maintenance Datasets

| Dataset                           | Asset Mapping         | Use Case                                    |
| --------------------------------- | --------------------- | ------------------------------------------- |
| NASA C-MAPSS                      | C-201 Compressor      | Remaining Useful Life prediction            |
| CWRU Bearing Dataset              | P-101 Pump            | Bearing fault and vibration classification  |
| Tennessee Eastman Process Dataset | HX-301 Heat Exchanger | Process anomaly and fouling-style deviation |

These datasets provide technical credibility for predictive maintenance and sensor intelligence.

---

## 8.2 Synthetic Industrial Documents

Synthetic industrial documents are used for RAG, RCA, compliance checking, and knowledge graph generation.

The synthetic document pack includes:

* Datasheets
* Maintenance logs
* Inspection reports
* SOPs
* Incident reports
* Compliance checklists
* Simple engineering drawings

Synthetic documents are used because real industrial maintenance documents are usually confidential or unavailable for public hackathon use.

All synthetic documents are clearly treated as demo data.

---

## 9. Synthetic Document Pack

## 9.1 P-101 Pump Documents

```text
P-101_Datasheet.pdf
P-101_Maintenance_Log_Jan2026.pdf
P-101_Inspection_Report_IR-008.pdf
P-101_SOP_Lubrication_and_Bearing_Check.pdf
P-101_Incident_Report_High_Vibration.pdf
P-101_Compliance_Checklist.pdf
P-101_Pump_Drawing.png
```

Main story:

```text
P-101 is high risk because it has high vibration, abnormal bearing noise, slightly elevated bearing temperature, and missing lubrication evidence.
```

---

## 9.2 C-201 Compressor Documents

```text
C-201_Datasheet.pdf
C-201_Maintenance_Log_Feb2026.pdf
C-201_RUL_Report.pdf
C-201_SOP_Compressor_Shutdown.pdf
C-201_Inspection_Report.pdf
C-201_Compliance_Checklist.pdf
C-201_Compressor_Drawing.png
```

Main story:

```text
C-201 has a decreasing RUL trend, unstable pressure ratio, increasing outlet temperature, and delayed filter replacement verification.
```

---

## 9.3 HX-301 Heat Exchanger Documents

```text
HX-301_Datasheet.pdf
HX-301_Inspection_Report.pdf
HX-301_Cleaning_Record.pdf
HX-301_SOP_Pressure_Test.pdf
HX-301_Compliance_Checklist.pdf
HX-301_Incident_Report_Low_Efficiency.pdf
HX-301_Heat_Exchanger_Drawing.png
```

Main story:

```text
HX-301 has suspected fouling because outlet temperature is below target, pressure drop is increasing, and cleaning evidence is overdue or missing.
```

---

## 10. UI Screens

PlantMind AI includes seven main screens.

| Screen            | Purpose                                                    |
| ----------------- | ---------------------------------------------------------- |
| Dashboard         | Plant-level health, risk, compliance, and action overview  |
| Asset 360 View    | Complete intelligence profile for each asset               |
| Ask PlantMind     | Natural-language industrial Q&A with citations             |
| Knowledge Graph   | Visual explanation of asset-document-failure relationships |
| Compliance Center | Evidence availability and compliance gap detection         |
| RCA Workspace     | Structured root-cause analysis generation                  |
| Document Library  | Indexed document list with metadata and tags               |

---

## 11. API Overview

| Method | Endpoint                        | Purpose                  |
| ------ | ------------------------------- | ------------------------ |
| GET    | `/api/assets`                   | Get all assets           |
| GET    | `/api/assets/{asset_id}`        | Get asset details        |
| GET    | `/api/assets/{asset_id}/health` | Get asset health score   |
| GET    | `/api/assets/{asset_id}/events` | Get maintenance history  |
| GET    | `/api/documents`                | Get document library     |
| POST   | `/api/documents/ingest`         | Ingest documents         |
| POST   | `/api/ask`                      | Ask PlantMind question   |
| POST   | `/api/rca/generate`             | Generate RCA report      |
| GET    | `/api/compliance`               | Get compliance matrix    |
| GET    | `/api/compliance/summary`       | Get compliance summary   |
| GET    | `/api/graph`                    | Get knowledge graph      |
| GET    | `/api/graph/{asset_id}`         | Get asset-specific graph |

---

## 12. Example API Request

## Ask PlantMind

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

## 13. Project Folder Structure

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

## 14. Installation and Setup

## 14.1 Prerequisites

Install the following:

```text
Node.js 20+
Python 3.10+
PostgreSQL 15+
pgvector extension
Git
Docker and Docker Compose
```

---

## 14.2 Clone Repository

```bash
git clone https://github.com/<your-username>/plantmind-ai.git
cd plantmind-ai
```

---

## 14.3 Environment Setup

Create environment file:

```bash
cp .env.example .env
```

Example `.env`:

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

## 14.4 Backend Setup

```bash
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

For Windows PowerShell:

```powershell
cd apps/api
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## 14.5 Frontend Setup

```bash
cd apps/web
npm install
npm run dev
```

Frontend will run at:

```text
http://localhost:3000
```

Backend will run at:

```text
http://localhost:8000
```

---

## 14.6 Docker Setup

```bash
docker-compose up --build
```

Recommended local services:

```text
web        → Next.js frontend
api        → FastAPI backend
postgres   → PostgreSQL with pgvector
minio      → Optional document storage
```

---

## 15. Data Preparation

## 15.1 Generate Synthetic Documents

```bash
python scripts/generate_synthetic_docs.py
```

Expected output:

```text
data/raw/documents/P-101/
data/raw/documents/C-201/
data/raw/documents/HX-301/
```

---

## 15.2 Seed Demo Data

```bash
python scripts/seed_demo_data.py
```

Expected output:

```text
data/demo/assets.json
data/demo/documents.json
data/demo/compliance_matrix.json
data/demo/health_scores.json
data/demo/knowledge_graph.json
data/demo/rag_seed_questions.json
data/demo/demo_answers.json
```

---

## 15.3 Ingest Documents

```bash
python scripts/ingest_documents.py
```

---

## 15.4 Build Vector Index

```bash
python scripts/build_vector_index.py
```

---

## 15.5 Build Knowledge Graph

```bash
python scripts/build_knowledge_graph.py
```

---

## 16. Health Score Logic

PlantMind AI uses explainable rule-based health scoring for the hackathon MVP.

```text
Base health score = 100

Subtract:
- 20 points for critical sensor anomaly
- 15 points for missing compliance evidence
- 10 points for overdue maintenance
- 10 points for repeated maintenance symptom
- 5 points for delayed evidence
```

Risk level rules:

```text
Health Score >= 80: Low Risk
Health Score 65-79: Medium Risk
Health Score < 65: High Risk
```

Frozen demo scores:

| Asset  | Health Score | Risk Level |
| ------ | -----------: | ---------- |
| P-101  |           62 | High       |
| C-201  |           71 | Medium     |
| HX-301 |           68 | Medium     |

---

## 17. RAG Pipeline

PlantMind AI uses a Retrieval-Augmented Generation pipeline.

```text
User Question
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

Retrieval rules:

1. If the question contains an asset ID, filter retrieved chunks by that asset.
2. Compliance questions prioritize compliance checklists and SOPs.
3. RCA questions prioritize inspection reports, incident reports, maintenance logs, and SOPs.
4. Maintenance planning questions prioritize RUL reports, inspection reports, and maintenance logs.
5. Every answer must include source documents.
6. If evidence is missing, the system must clearly say that evidence was not found.

---

## 18. Knowledge Graph Model

PlantMind AI uses a lightweight graph model.

```text
Asset → Document → Symptom → Failure Mode → Maintenance Action → Compliance Requirement
```

Example:

```text
P-101
 ├── has_symptom: High Vibration
 ├── has_symptom: Bearing Noise
 ├── possible_failure: Bearing Wear
 ├── linked_document: P-101_Inspection_Report_IR-008.pdf
 ├── linked_document: P-101_SOP_Lubrication_and_Bearing_Check.pdf
 ├── recommended_action: Inspect bearing housing
 └── compliance_requirement: Weekly lubrication inspection
```

For the MVP, the graph can be stored as:

```text
data/demo/knowledge_graph.json
```

This can later be upgraded to Neo4j.

---

## 19. Deployment Plan

Recommended hackathon deployment:

| Component    | Deployment Option                             |
| ------------ | --------------------------------------------- |
| Frontend     | Vercel                                        |
| Backend      | Render, Railway, Fly.io, or Docker VM         |
| Database     | Supabase PostgreSQL with pgvector             |
| File Storage | Local demo folder, Supabase Storage, or MinIO |
| Demo Data    | Seeded JSON and database tables               |

Simplest deployment:

```text
Frontend: Vercel
Backend: Render
Database: Supabase PostgreSQL with pgvector
Documents: Preloaded demo files
```

---

## 20. Demo Questions

The system must confidently answer these five questions:

```text
Why is P-101 high risk?
```

```text
Generate RCA for P-101 high vibration.
```

```text
Which assets are non-compliant?
```

```text
What maintenance should be planned for C-201?
```

```text
What evidence is missing for HX-301?
```

---

## 21. Out of Scope

PlantMind AI is not intended to be a full industrial operations platform during the hackathon.

The following are out of scope:

* Full CMMS replacement
* Full ERP replacement
* SAP integration
* IBM Maximo integration
* Real-time IoT streaming
* Live equipment control
* Multi-plant support
* Full user-role management
* Mobile application
* 3D CAD viewer
* Advanced OCR for complex engineering drawings
* Automatic work-order execution
* Safety-critical autonomous decision-making

---

## 22. Safety and Responsible Use

PlantMind AI is a decision-support system.

It does not replace qualified engineers, maintenance teams, safety officers, or plant operators.

The system should use safe wording such as:

```text
Recommended action
Suggested inspection
Possible failure mode
Likely root cause
Evidence indicates
Requires engineer review
```

The system should avoid unsafe claims such as:

```text
Guaranteed failure
Confirmed root cause
Shut down immediately
Automatically execute maintenance
No engineer review needed
```

Final maintenance and safety decisions must remain with qualified plant personnel.

---

## 23. Project Success Criteria

The project is successful if the final demo proves:

| Capability             | Proof                                                     |
| ---------------------- | --------------------------------------------------------- |
| RAG                    | Answers questions with cited source documents             |
| Asset Intelligence     | Shows asset health, risk, history, and recommendations    |
| Predictive Maintenance | Shows vibration, RUL, or process trend                    |
| RCA                    | Generates structured root-cause reports                   |
| Compliance             | Detects missing, delayed, and overdue evidence            |
| Knowledge Graph        | Shows asset-symptom-failure-document-action relationships |
| Demo Readiness         | Tells one clear industrial maintenance story              |

---

## 24. Final Demo Statement

PlantMind AI converts scattered industrial knowledge into actionable maintenance intelligence.

It helps plant teams move from:

```text
Documents + Sensor Trends
        ↓
Evidence
        ↓
Asset Risk
        ↓
Root Cause
        ↓
Compliance Gap
        ↓
Maintenance Recommendation
```

The core value is simple:

**PlantMind AI helps maintenance teams find evidence faster, understand failures better, and make safer, more explainable maintenance decisions.**

---

## 25. Repository Status

Current project phase:

```text
Day 1: Final scope freeze and documentation
```

Completed Day 1 documents:

```text
docs/scope_freeze.md
docs/architecture.md
docs/dataset_plan.md
docs/ui_screen_list.md
docs/demo_script.md
README.md
```

Next phase:

```text
Synthetic document generation
Demo data seeding
Backend API implementation
Frontend dashboard implementation
RAG pipeline integration
```
