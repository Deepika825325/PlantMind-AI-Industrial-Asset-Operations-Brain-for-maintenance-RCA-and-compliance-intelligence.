# Scope Freeze Document

## Project Name

**PlantMind AI**

## Project Title

**PlantMind AI: Industrial Asset & Operations Brain for Maintenance, RCA, and Compliance Intelligence**

---

## 1. Purpose of This Document

This document freezes the final scope of the PlantMind AI project for the hackathon.

The goal of this document is to prevent scope creep and ensure that the project remains focused, demo-ready, technically credible, and achievable within the available development timeline.

After Day 1, the project scope must not be changed unless there is a critical technical blocker. New assets, new modules, new integrations, or major new features should not be added after this point.

---

## 2. Final Problem Statement

Industrial plants generate large amounts of operational knowledge across maintenance logs, inspection reports, SOPs, safety procedures, compliance checklists, sensor readings, incident reports, and engineering documents.

This information is often scattered, difficult to search, and disconnected from asset-level decision-making. Maintenance teams may struggle to quickly answer questions such as:

* Why is an asset showing abnormal behavior?
* Which maintenance action should be taken next?
* What evidence supports a root-cause analysis?
* Which compliance checks are missing?
* Which documents are related to a specific asset or failure?

**PlantMind AI solves this by creating an industrial intelligence layer that connects asset data, maintenance history, documents, sensor signals, compliance evidence, and AI-powered reasoning into one explainable system.**

---

## 3. Final One-Line Pitch

**PlantMind AI is an Industrial Asset & Operations Brain that helps maintenance teams ask questions, investigate failures, generate RCA reports, detect compliance gaps, and understand asset risk using cited evidence from industrial documents and sensor data.**

---

## 4. Frozen Asset Scope

The project will support only three assets.

No additional assets will be added during the hackathon.

| Asset ID | Asset Name     | Asset Type         | Main Use Case                                               |
| -------- | -------------- | ------------------ | ----------------------------------------------------------- |
| P-101    | Pump           | Rotating Equipment | Vibration issue, bearing fault, lubrication compliance      |
| C-201    | Compressor     | Rotating Equipment | RUL prediction, degradation trend, maintenance planning     |
| HX-301   | Heat Exchanger | Process Equipment  | Fouling detection, cleaning evidence, inspection compliance |

---

## 5. Asset Details

### 5.1 P-101: Pump

**Asset ID:** P-101
**Asset Type:** Pump
**Criticality:** High
**Main problem shown in demo:** High vibration and possible bearing wear.

#### Key symptoms

* High vibration
* Abnormal bearing noise
* Slight increase in bearing temperature
* Missed lubrication evidence
* Possible misalignment

#### Main documents

* `P-101_Datasheet.pdf`
* `P-101_Maintenance_Log_Jan2026.pdf`
* `P-101_Inspection_Report_IR-008.pdf`
* `P-101_SOP_Lubrication_and_Bearing_Check.pdf`
* `P-101_Incident_Report_High_Vibration.pdf`
* `P-101_Compliance_Checklist.pdf`
* `P-101_Pump_Drawing.png`

#### Main demo question

```text
Why is P-101 high risk?
```

#### Expected answer behavior

PlantMind AI should explain that P-101 is high risk because vibration is above threshold, maintenance logs mention abnormal bearing noise, and lubrication evidence is missing. The system should cite inspection reports, SOPs, and compliance records.

---

### 5.2 C-201: Compressor

**Asset ID:** C-201
**Asset Type:** Compressor
**Criticality:** Medium to High
**Main problem shown in demo:** Decreasing Remaining Useful Life and unstable operating behavior.

#### Key symptoms

* RUL decreasing
* Outlet temperature increasing
* Pressure ratio instability
* Delayed filter replacement
* Increasing maintenance risk

#### Main documents

* `C-201_Datasheet.pdf`
* `C-201_Maintenance_Log_Feb2026.pdf`
* `C-201_RUL_Report.pdf`
* `C-201_SOP_Compressor_Shutdown.pdf`
* `C-201_Inspection_Report.pdf`
* `C-201_Compliance_Checklist.pdf`
* `C-201_Compressor_Drawing.png`

#### Main demo question

```text
What maintenance should be planned for C-201?
```

#### Expected answer behavior

PlantMind AI should explain that C-201 has a decreasing RUL trend and should be scheduled for inspection or maintenance within the recommended window. The answer should cite the RUL report, inspection report, and compressor SOP.

---

### 5.3 HX-301: Heat Exchanger

**Asset ID:** HX-301
**Asset Type:** Heat Exchanger
**Criticality:** Medium
**Main problem shown in demo:** Possible fouling and missing cleaning evidence.

#### Key symptoms

* Outlet temperature below target
* Pressure drop increasing
* Fouling suspected
* Cleaning overdue
* Cleaning evidence missing

#### Main documents

* `HX-301_Datasheet.pdf`
* `HX-301_Inspection_Report.pdf`
* `HX-301_Cleaning_Record.pdf`
* `HX-301_SOP_Pressure_Test.pdf`
* `HX-301_Compliance_Checklist.pdf`
* `HX-301_Incident_Report_Low_Efficiency.pdf`
* `HX-301_Heat_Exchanger_Drawing.png`

#### Main demo question

```text
What evidence is missing for HX-301?
```

#### Expected answer behavior

PlantMind AI should identify that HX-301 has suspected fouling and missing or overdue cleaning evidence. It should cite the inspection report, cleaning record, and compliance checklist.

---

## 6. Frozen Feature Scope

PlantMind AI will include only the following five core modules.

---

## 6.1 Module 1: Industrial Document Intelligence

### Objective

To ingest, parse, chunk, tag, and index industrial documents so users can ask asset-specific questions and receive answers with citations.

### Supported document types

* Maintenance logs
* SOPs
* Inspection reports
* Incident reports
* Compliance checklists
* Asset datasheets
* Simple drawings or P&ID-style images

### Extracted information

The document intelligence pipeline should extract:

* Asset IDs
* Equipment names
* Failure symptoms
* Fault types
* Maintenance actions
* Inspection results
* Compliance requirements
* Missing evidence
* Dates
* Work order IDs
* Document type
* Source file name

### Example extracted data

```json
{
  "asset_id": "P-101",
  "document_type": "Inspection Report",
  "symptoms": ["high vibration", "bearing noise"],
  "possible_failure": "bearing wear",
  "recommended_action": "inspect bearing housing and verify lubrication",
  "compliance_gap": "lubrication evidence missing"
}
```

### Required output

The system must support cited answers such as:

```text
P-101 is high risk because IR-008 reports vibration above threshold, ML-014 mentions abnormal bearing noise, and the compliance checklist shows missing lubrication evidence.

Sources:
1. P-101_Inspection_Report_IR-008.pdf
2. P-101_Maintenance_Log_Jan2026.pdf
3. P-101_Compliance_Checklist.pdf
```

---

## 6.2 Module 2: Asset Knowledge Graph

### Objective

To connect assets, documents, symptoms, failure modes, actions, and compliance requirements in a visual and queryable graph.

### Graph structure

The graph should follow this relationship pattern:

```text
Asset → Document → Symptom → Failure Mode → Maintenance Action → Compliance Requirement
```

### Example graph for P-101

```text
P-101
 ├── has_symptom: High Vibration
 ├── has_symptom: Bearing Noise
 ├── possible_failure: Bearing Wear
 ├── linked_document: P-101_Inspection_Report_IR-008.pdf
 ├── linked_document: P-101_SOP_Lubrication_and_Bearing_Check.pdf
 ├── recommended_action: Inspect bearing housing
 ├── recommended_action: Verify lubrication
 └── compliance_requirement: Weekly lubrication inspection
```

### Graph nodes

The graph will contain only these node types:

* Asset
* Document
* Symptom
* Failure Mode
* Maintenance Action
* Compliance Requirement

### Graph edges

The graph will contain only these edge types:

* `HAS_DOCUMENT`
* `HAS_SYMPTOM`
* `INDICATES_FAILURE`
* `REQUIRES_ACTION`
* `HAS_COMPLIANCE_REQUIREMENT`
* `EVIDENCE_FOR`

### Required UI behavior

The knowledge graph screen should allow the user to:

* View asset relationships
* Click a node
* See connected evidence
* Understand why a recommendation was generated

---

## 6.3 Module 3: Maintenance Intelligence

### Objective

To provide a simple asset health and risk view using document evidence, sensor signals, and rules.

### Required fields per asset

Each asset should display:

* Asset ID
* Asset name
* Health score
* Risk level
* Main reason for risk
* Latest anomaly
* Recommended maintenance action
* Linked evidence documents

### Health score rules

The health score will be rule-based for the hackathon.

Example scoring logic:

```text
Base health score = 100

Subtract:
- 20 points for high-risk sensor anomaly
- 15 points for missing compliance evidence
- 10 points for overdue maintenance
- 10 points for repeated symptom in maintenance logs
- 5 points for stale SOP or old inspection record
```

### Final demo health scores

The following values are frozen for the demo:

| Asset  | Health Score | Risk Level | Main Reason                                   |
| ------ | -----------: | ---------- | --------------------------------------------- |
| P-101  |          62% | High       | High vibration + missing lubrication evidence |
| C-201  |          71% | Medium     | RUL decreasing + delayed filter replacement   |
| HX-301 |          68% | Medium     | Fouling suspected + cleaning overdue          |

### Required output

PlantMind AI should explain asset risk in natural language with evidence.

Example:

```text
P-101 has a health score of 62% and is marked High Risk because vibration has exceeded the threshold, bearing noise was reported in the maintenance log, and lubrication evidence is missing from the compliance checklist.
```

---

## 6.4 Module 4: RCA Assistant

### Objective

To generate a root-cause analysis report for an asset issue using available evidence.

### Supported RCA inputs

Only the following RCA cases are in scope:

| Asset  | RCA Issue                    |
| ------ | ---------------------------- |
| P-101  | High vibration               |
| C-201  | Decreasing RUL               |
| HX-301 | Low heat transfer efficiency |

### RCA output sections

The RCA assistant must generate:

1. Problem statement
2. Observed symptoms
3. Evidence
4. Timeline
5. Possible causes
6. Most likely root cause
7. Corrective action
8. Preventive action
9. Confidence level
10. Source documents

### Example RCA output for P-101

```text
RCA Report: P-101 High Vibration

Problem Statement:
P-101 is showing repeated high vibration events during normal operation.

Observed Symptoms:
- Vibration above threshold
- Abnormal bearing noise
- Slightly elevated bearing temperature
- Missing lubrication evidence

Evidence:
- Inspection Report IR-008 reports vibration above threshold.
- Maintenance Log ML-014 mentions abnormal bearing noise.
- SOP-PUMP-01 requires weekly lubrication checks.
- Compliance checklist shows lubrication evidence is missing.

Possible Causes:
1. Bearing wear
2. Lubrication degradation
3. Shaft misalignment
4. Loose mounting

Most Likely Root Cause:
Bearing wear caused by lubrication degradation or misalignment.

Corrective Action:
Inspect bearing housing, verify lubrication level, check shaft alignment, and replace bearing if vibration remains above threshold.

Preventive Action:
Add weekly lubrication evidence verification and vibration trend alert.

Confidence:
Medium-High

Sources:
1. P-101_Inspection_Report_IR-008.pdf
2. P-101_Maintenance_Log_Jan2026.pdf
3. P-101_SOP_Lubrication_and_Bearing_Check.pdf
4. P-101_Compliance_Checklist.pdf
```

---

## 6.5 Module 5: Compliance Evidence Checker

### Objective

To detect missing, overdue, or available compliance evidence for the three frozen assets.

### Supported compliance checks

| Asset  | Requirement                     | Expected Evidence    | Frozen Status     |
| ------ | ------------------------------- | -------------------- | ----------------- |
| P-101  | Weekly vibration inspection     | Inspection report    | Available         |
| P-101  | Weekly lubrication check        | Lubrication record   | Missing           |
| C-201  | Monthly compressor inspection   | Inspection report    | Available         |
| C-201  | Filter replacement verification | Maintenance log      | Delayed           |
| HX-301 | Pressure test                   | Pressure test report | Available         |
| HX-301 | Cleaning and fouling inspection | Cleaning record      | Overdue / Missing |

### Compliance status values

Only these status values are allowed:

* Available
* Missing
* Overdue
* Delayed
* Not Required

### Required output

The compliance module should answer questions like:

```text
Which assets are non-compliant?
```

Expected answer:

```text
PlantMind found compliance gaps for two assets:

1. P-101: Weekly lubrication evidence is missing.
2. HX-301: Cleaning and fouling inspection evidence is overdue or missing.

C-201 has available monthly inspection evidence, but filter replacement is delayed.
```

---

## 7. Frozen UI Scope

PlantMind AI will include only seven screens.

No additional major screens should be added.

---

## 7.1 Dashboard

### Purpose

To show the overall plant asset health and risk summary.

### Required components

* Total assets count
* High-risk assets count
* Compliance gaps count
* Open maintenance actions count
* Average health score
* Asset cards
* Risk distribution chart
* Recent alerts

### Frozen dashboard metrics

```text
Total Assets: 3
High Risk Assets: 1
Compliance Gaps: 3
Open Maintenance Actions: 4
Average Health Score: 67%
```

---

## 7.2 Asset 360 View

### Purpose

To show detailed information for one asset.

### Required tabs

* Overview
* Maintenance History
* Sensor Trends
* Documents
* Compliance
* RCA

### Required content

* Asset metadata
* Health score
* Risk level
* Latest issue
* Recommended action
* Linked documents
* Sensor trend chart
* Compliance status

---

## 7.3 Ask PlantMind

### Purpose

To allow users to ask natural-language questions about assets, maintenance, RCA, and compliance.

### Required features

* Chat input
* Suggested question chips
* Cited answers
* Source document list
* Asset filter

### Frozen suggested questions

```text
Why is P-101 high risk?
What evidence is missing for HX-301?
What maintenance should be planned for C-201?
Generate RCA for P-101.
Which assets are non-compliant?
```

---

## 7.4 Knowledge Graph

### Purpose

To visually show relationships between assets, symptoms, failures, documents, and actions.

### Required features

* Graph visualization
* Node click side panel
* Asset filter
* Evidence display

### Required graph library

Use React Flow or an equivalent graph visualization library.

---

## 7.5 Compliance Center

### Purpose

To show compliance requirements and missing evidence.

### Required features

* Compliance table
* Status badges
* Evidence file link
* Gap summary
* Generate compliance summary button

---

## 7.6 RCA Workspace

### Purpose

To generate structured root-cause analysis reports.

### Required features

* Asset selector
* Issue selector
* Generate RCA button
* RCA report output
* Source citations

---

## 7.7 Document Library

### Purpose

To show all indexed documents and extracted metadata.

### Required features

* Document table
* Asset filter
* Document type filter
* Extracted tags
* Indexing status
* Source file name

---

## 8. Frozen Dataset Scope

The project will use a combination of public datasets and synthetic documents.

---

## 8.1 Public Datasets

### Dataset 1: NASA C-MAPSS

**Mapped asset:** C-201 Compressor
**Purpose:** RUL prediction and degradation trend demonstration.

Use C-MAPSS to simulate compressor degradation and remaining useful life.

### Dataset 2: Case Western Reserve University Bearing Dataset

**Mapped asset:** P-101 Pump
**Purpose:** Bearing fault and vibration classification.

Use bearing vibration data to support the pump high-vibration use case.

### Dataset 3: Tennessee Eastman Process Dataset

**Mapped asset:** HX-301 Heat Exchanger
**Purpose:** Process anomaly detection and heat-transfer deviation simulation.

Use process variables to simulate abnormal heat exchanger behavior.

---

## 8.2 Synthetic Document Dataset

Synthetic industrial documents will be created for all three assets.

### P-101 documents

```text
P-101_Datasheet.pdf
P-101_Maintenance_Log_Jan2026.pdf
P-101_Inspection_Report_IR-008.pdf
P-101_SOP_Lubrication_and_Bearing_Check.pdf
P-101_Incident_Report_High_Vibration.pdf
P-101_Compliance_Checklist.pdf
P-101_Pump_Drawing.png
```

### C-201 documents

```text
C-201_Datasheet.pdf
C-201_Maintenance_Log_Feb2026.pdf
C-201_RUL_Report.pdf
C-201_SOP_Compressor_Shutdown.pdf
C-201_Inspection_Report.pdf
C-201_Compliance_Checklist.pdf
C-201_Compressor_Drawing.png
```

### HX-301 documents

```text
HX-301_Datasheet.pdf
HX-301_Inspection_Report.pdf
HX-301_Cleaning_Record.pdf
HX-301_SOP_Pressure_Test.pdf
HX-301_Compliance_Checklist.pdf
HX-301_Incident_Report_Low_Efficiency.pdf
HX-301_Heat_Exchanger_Drawing.png
```

---

## 9. Frozen Technical Scope

### Frontend

* Next.js
* TypeScript
* Tailwind CSS
* Shadcn UI
* Recharts
* React Flow
* TanStack Table

### Backend

* FastAPI
* Python
* PostgreSQL
* pgvector
* SQLAlchemy or equivalent ORM

### AI / Data Layer

* Document chunking
* Metadata extraction
* Embeddings
* Vector search
* RAG answer generation
* Rule-based health score
* Rule-based compliance checking
* Knowledge graph generation
* Basic anomaly or RUL scoring

### Storage

* PostgreSQL for structured data
* pgvector for embeddings
* Local folder or MinIO for documents
* Optional NetworkX or Neo4j for graph representation

---

## 10. Out of Scope

The following are explicitly out of scope and must not be added during the hackathon.

### Product scope exclusions

* Full CMMS replacement
* Full ERP replacement
* SAP integration
* IBM Maximo integration
* Real-time IoT streaming system
* Full industrial digital twin
* Multi-plant support
* Mobile application
* Full user-role and permission system
* 3D CAD viewer
* Support for more than three assets
* Support for every industrial document format
* Advanced OCR for complex engineering drawings
* Live sensor hardware integration

### AI scope exclusions

* Fully autonomous maintenance decision-making
* Safety-critical control recommendations
* Real-time plant control
* Automatic work-order execution
* Guaranteed fault diagnosis
* Large-scale model training from scratch

### UI scope exclusions

* Admin panel
* Billing page
* Team management
* Notification system
* Mobile-responsive perfection
* Dark mode as a priority feature
* Complex dashboard customization

---

## 11. Final Demo Scope

The final demo must focus on one strong story:

**P-101 Pump is high risk because of high vibration, abnormal bearing noise, and missing lubrication evidence. PlantMind AI explains the issue, cites documents, shows the knowledge graph, generates RCA, and recommends corrective and preventive action.**

### Demo flow

1. Open dashboard.
2. Show P-101 marked as high risk.
3. Ask: `Why is P-101 high risk?`
4. Show cited answer.
5. Open Asset 360 for P-101.
6. Show vibration trend and linked documents.
7. Open Knowledge Graph.
8. Show relation: `P-101 → High Vibration → Bearing Wear → Lubrication Missing → SOP Requirement`.
9. Generate RCA for P-101.
10. Open Compliance Center.
11. Show missing lubrication evidence for P-101 and overdue cleaning evidence for HX-301.
12. End with maintenance recommendation.

---

## 12. Primary Demo Questions

The system must confidently answer these five questions:

```text
Why is P-101 high risk?
```

```text
What evidence is missing for HX-301?
```

```text
What maintenance should be planned for C-201?
```

```text
Generate RCA for P-101 high vibration.
```

```text
Which assets are non-compliant?
```

If the system answers these five questions well, the demo is successful.

---

## 13. Success Criteria

The project will be considered successful if it demonstrates the following:

| Capability             | Required Proof                                              |
| ---------------------- | ----------------------------------------------------------- |
| RAG                    | Answers industrial questions with source citations          |
| Asset Intelligence     | Shows health, risk, history, and recommendations            |
| RCA                    | Generates structured root-cause reports                     |
| Compliance             | Detects missing and overdue evidence                        |
| Knowledge Graph        | Connects assets, symptoms, failures, documents, and actions |
| Predictive Maintenance | Shows sensor trend or RUL-based risk                        |
| Demo Readiness         | Tells one clear maintenance story from data to decision     |

---

## 14. Final Frozen Statement

PlantMind AI is an Industrial Asset & Operations Brain focused on three assets only:

* P-101 Pump
* C-201 Compressor
* HX-301 Heat Exchanger

It ingests maintenance records, SOPs, inspection reports, incident reports, compliance checklists, asset datasheets, simple drawings, and public/synthetic sensor datasets.

It provides five core capabilities:

1. Ask PlantMind with cited answers
2. Asset 360 health and risk view
3. Root Cause Analysis assistant
4. Compliance evidence checker
5. Asset knowledge graph

The final demo will show how PlantMind AI identifies why P-101 is high risk, links evidence across documents, generates a root-cause analysis, detects compliance gaps, and recommends corrective maintenance actions.

This scope is now frozen.
