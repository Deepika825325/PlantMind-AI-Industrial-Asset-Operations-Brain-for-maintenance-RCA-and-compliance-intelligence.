# UI Screen List

## Project Name

**PlantMind AI**

## Project Title

**PlantMind AI: Industrial Asset & Operations Brain for Maintenance, RCA, and Compliance Intelligence**

---

## 1. Purpose of This Document

This document defines the final user interface scope for PlantMind AI.

The goal is to freeze the exact screens, components, user flows, and demo requirements for the project so the UI remains focused, professional, and achievable within the hackathon timeline.

PlantMind AI will have seven main screens only:

1. Dashboard
2. Asset 360 View
3. Ask PlantMind
4. Knowledge Graph
5. Compliance Center
6. RCA Workspace
7. Document Library

No additional major screens should be added during the hackathon unless absolutely required for demo stability.

---

## 2. UI Design Goals

The PlantMind AI interface should feel like an enterprise industrial intelligence platform.

The UI should communicate:

* Asset risk
* Maintenance priority
* Evidence-backed AI reasoning
* Compliance gaps
* Root-cause analysis
* Asset knowledge relationships
* Operational decision support

The UI should be clean, modern, and easy for judges to understand within a short demo.

---

## 3. Recommended UI Stack

| Area               | Recommended Tool                |
| ------------------ | ------------------------------- |
| Frontend Framework | Next.js                         |
| Language           | TypeScript                      |
| Styling            | Tailwind CSS                    |
| UI Components      | Shadcn UI                       |
| Charts             | Recharts                        |
| Knowledge Graph    | React Flow                      |
| Tables             | TanStack Table                  |
| Icons              | Lucide React                    |
| State Management   | React hooks / Zustand if needed |
| API Calls          | Fetch / Axios / TanStack Query  |

---

## 4. Global UI Layout

## 4.1 Main Layout

The application should use a standard dashboard layout.

```text id="f7h92v"
┌─────────────────────────────────────────────────────────────┐
│ Top Header: PlantMind AI | Search | Demo Plant | User Icon   │
├───────────────┬─────────────────────────────────────────────┤
│ Sidebar       │ Main Content Area                           │
│               │                                             │
│ Dashboard     │ Screen-specific content                     │
│ Assets        │                                             │
│ Ask AI        │                                             │
│ Knowledge     │                                             │
│ Compliance    │                                             │
│ RCA           │                                             │
│ Documents     │                                             │
└───────────────┴─────────────────────────────────────────────┘
```

## 4.2 Sidebar Navigation

Sidebar items:

```text id="b4op1y"
Dashboard
Assets
Ask PlantMind
Knowledge Graph
Compliance Center
RCA Workspace
Document Library
```

## 4.3 Top Header

The top header should include:

```text id="1avrbw"
PlantMind AI logo/name
Current plant: Demo Plant A
Global asset search
Demo mode badge
User role: Maintenance Engineer
```

## 4.4 Global UI Elements

Use these elements across screens:

| Component         | Purpose                                    |
| ----------------- | ------------------------------------------ |
| Risk Badge        | Shows Low, Medium, High risk               |
| Health Score Ring | Shows asset health percentage              |
| Citation Card     | Shows source document evidence             |
| Status Badge      | Shows Available, Missing, Overdue, Delayed |
| Asset Selector    | Selects P-101, C-201, or HX-301            |
| Evidence Panel    | Displays linked source documents           |
| Loading Skeleton  | Smooth loading state                       |
| Empty State       | Clean message when no data exists          |
| Demo Data Badge   | Indicates synthetic/public demo data       |

---

## 5. Screen 1: Dashboard

## 5.1 Route

```text id="64egf9"
/dashboard
```

## 5.2 Purpose

The Dashboard gives a plant-level overview of asset health, risk, compliance gaps, and maintenance priorities.

This should be the first screen shown in the demo.

## 5.3 Main User Goal

A maintenance engineer should quickly understand:

* Which asset is most risky?
* How many compliance gaps exist?
* What maintenance actions are open?
* Which asset needs immediate attention?

## 5.4 Required Dashboard Metrics

```text id="n39u9w"
Total Assets: 3
High Risk Assets: 1
Compliance Gaps: 3
Open Maintenance Actions: 4
Average Health Score: 67%
```

## 5.5 Required Components

### 5.5.1 KPI Cards

Display five KPI cards:

| KPI               | Value | Meaning                                 |
| ----------------- | ----: | --------------------------------------- |
| Total Assets      |     3 | Frozen demo assets                      |
| High Risk Assets  |     1 | P-101 is high risk                      |
| Compliance Gaps   |     3 | Missing, delayed, or overdue evidence   |
| Open Actions      |     4 | Maintenance actions requiring attention |
| Avg. Health Score |   67% | Average of all asset scores             |

### 5.5.2 Asset Risk Cards

Display three asset cards.

#### P-101 Card

```text id="p7xa98"
Asset: P-101 Pump
Health Score: 62%
Risk: High
Main Issue: High vibration + missing lubrication evidence
Recommended Action: Inspect bearing housing and verify lubrication
```

#### C-201 Card

```text id="hk08b7"
Asset: C-201 Compressor
Health Score: 71%
Risk: Medium
Main Issue: RUL decreasing + delayed filter replacement
Recommended Action: Plan inspection during next maintenance window
```

#### HX-301 Card

```text id="u3vnnx"
Asset: HX-301 Heat Exchanger
Health Score: 68%
Risk: Medium
Main Issue: Fouling suspected + cleaning overdue
Recommended Action: Schedule cleaning inspection
```

### 5.5.3 Risk Distribution Chart

Show a simple chart:

```text id="8vqy1p"
High Risk: 1
Medium Risk: 2
Low Risk: 0
```

### 5.5.4 Recent Alerts Panel

Show recent alerts:

```text id="uz54w6"
P-101 vibration exceeded critical threshold.
P-101 lubrication evidence is missing.
C-201 RUL trend is decreasing.
HX-301 cleaning evidence is overdue.
```

### 5.5.5 Open Maintenance Actions

Show action list:

```text id="ai8io4"
Inspect P-101 bearing housing.
Verify P-101 lubrication level.
Verify C-201 filter replacement.
Schedule HX-301 cleaning inspection.
```

## 5.6 Primary CTA

Each asset card should have:

```text id="4zey95"
View Asset 360
```

## 5.7 Demo Script Usage

During the demo, use this screen to say:

```text id="9t7hp5"
This dashboard shows the current health of our demo plant. P-101 Pump is marked high risk because the system detected high vibration and missing lubrication evidence.
```

## 5.8 Success Criteria

The Dashboard is successful if judges can immediately identify:

```text id="7aao22"
P-101 is the highest-risk asset.
There are compliance gaps.
The system provides maintenance actions.
The UI looks like an industrial operations dashboard.
```

---

## 6. Screen 2: Asset 360 View

## 6.1 Route

```text id="lwgvbc"
/assets/[assetId]
```

Examples:

```text id="vjwdhc"
/assets/P-101
/assets/C-201
/assets/HX-301
```

## 6.2 Purpose

The Asset 360 View gives a complete intelligence profile for a single asset.

It connects asset metadata, health score, sensor trends, maintenance history, documents, compliance status, and RCA recommendations.

## 6.3 Main User Goal

A maintenance engineer should be able to answer:

```text id="620w4o"
What is happening with this asset?
Why is it risky?
What evidence supports the risk?
What action should be taken?
```

## 6.4 Required Header Section

For each asset, display:

```text id="whxwth"
Asset ID
Asset Name
Asset Type
Criticality
Location
Health Score
Risk Level
Main Issue
Recommended Action
```

### P-101 Header Example

```text id="zoo460"
Asset ID: P-101
Asset Name: Cooling Water Circulation Pump
Asset Type: Pump
Criticality: High
Location: Utility Area - Line A
Health Score: 62%
Risk Level: High
Main Issue: High vibration
Recommended Action: Inspect bearing housing and verify lubrication
```

## 6.5 Required Tabs

The Asset 360 page must have six tabs:

```text id="21xkk3"
Overview
Maintenance History
Sensor Trends
Documents
Compliance
RCA
```

---

## 6.6 Tab 1: Overview

### Required Content

Show:

```text id="xkcnag"
Health score
Risk drivers
Latest issue
Possible failure mode
Recommended action
Linked evidence documents
```

### P-101 Overview Example

```text id="954x08"
Risk Drivers:
- Vibration above critical threshold
- Abnormal bearing noise
- Missing lubrication evidence

Possible Failure Mode:
- Bearing wear

Recommended Action:
- Inspect bearing housing
- Verify lubrication level
- Check shaft alignment
```

---

## 6.7 Tab 2: Maintenance History

### Required Content

Show a timeline of maintenance and inspection events.

Example:

| Date       | Event Type              | Description                           | Source       |
| ---------- | ----------------------- | ------------------------------------- | ------------ |
| 2026-01-18 | Maintenance Observation | Abnormal bearing noise observed       | ML-014       |
| 2026-01-21 | Inspection              | Vibration exceeded critical threshold | IR-008       |
| 2026-01-22 | Incident                | Repeated high vibration event         | INC-P101-026 |

---

## 6.8 Tab 3: Sensor Trends

### Required Content

Show charts based on processed sensor data.

For P-101:

```text id="cdhpf0"
Vibration trend chart
Bearing fault indicator
Threshold line
```

For C-201:

```text id="tijqvr"
RUL trend chart
Outlet temperature trend
Pressure ratio instability indicator
```

For HX-301:

```text id="6oukuw"
Outlet temperature trend
Pressure drop trend
Efficiency index
```

### Chart Requirements

Each chart should clearly show:

```text id="ilwzvr"
Normal region
Warning region
Current status
Threshold crossing if available
```

---

## 6.9 Tab 4: Documents

### Required Content

Show all documents linked to the selected asset.

Example for P-101:

| Document                                    | Type                 | Date       | Status  | Tags                 |
| ------------------------------------------- | -------------------- | ---------- | ------- | -------------------- |
| P-101_Inspection_Report_IR-008.pdf          | Inspection Report    | 2026-01-21 | Indexed | vibration, bearing   |
| P-101_Maintenance_Log_Jan2026.pdf           | Maintenance Log      | 2026-01-18 | Indexed | bearing noise        |
| P-101_SOP_Lubrication_and_Bearing_Check.pdf | SOP                  | 2026-01-01 | Indexed | lubrication, safety  |
| P-101_Compliance_Checklist.pdf              | Compliance Checklist | 2026-01-23 | Indexed | evidence, compliance |

---

## 6.10 Tab 5: Compliance

### Required Content

Show compliance requirements for the asset.

Example for P-101:

| Requirement                 | Expected Evidence  | Status    | Action                          |
| --------------------------- | ------------------ | --------- | ------------------------------- |
| Weekly vibration inspection | Inspection report  | Available | Continue monitoring             |
| Weekly lubrication check    | Lubrication record | Missing   | Perform check and upload record |

---

## 6.11 Tab 6: RCA

### Required Content

Show:

```text id="1pk85z"
Generate RCA button
Latest RCA report if available
Observed symptoms
Likely root cause
Corrective action
Preventive action
Sources
```

## 6.12 Primary CTA

```text id="165wsw"
Generate RCA
Ask about this asset
View graph relationships
```

## 6.13 Demo Script Usage

Use P-101 Asset 360 in the demo to show:

```text id="12f85z"
PlantMind does not just answer questions. It creates an asset-centered intelligence view by connecting documents, sensor signals, compliance evidence, and maintenance recommendations.
```

## 6.14 Success Criteria

The Asset 360 screen is successful if it clearly shows:

```text id="d6xhng"
Why the asset is risky.
Which evidence supports the issue.
Which action should be taken.
How sensor data and documents connect.
```

---

## 7. Screen 3: Ask PlantMind

## 7.1 Route

```text id="yzc9c6"
/ask
```

## 7.2 Purpose

Ask PlantMind is the natural-language question-answering interface.

It allows users to ask maintenance, compliance, RCA, and asset-risk questions and receive evidence-backed answers with citations.

## 7.3 Main User Goal

A user should be able to ask:

```text id="8f90yh"
Why is this asset risky?
What maintenance should be planned?
What evidence is missing?
What is the likely root cause?
Which documents support this answer?
```

## 7.4 Required Components

### 7.4.1 Chat Input

Placeholder:

```text id="asz3gt"
Ask about asset risk, RCA, maintenance, or compliance...
```

### 7.4.2 Suggested Question Chips

Required suggested questions:

```text id="4ncv7c"
Why is P-101 high risk?
Generate RCA for P-101 high vibration.
Which assets are non-compliant?
What maintenance should be planned for C-201?
What evidence is missing for HX-301?
```

### 7.4.3 Asset Filter

Options:

```text id="1b6mtt"
All Assets
P-101 Pump
C-201 Compressor
HX-301 Heat Exchanger
```

### 7.4.4 Answer Panel

The answer panel should include:

```text id="2o38ay"
Direct answer
Evidence summary
Recommended action
Sources
Confidence indicator
```

### 7.4.5 Citation Cards

Each citation should show:

```text id="uyg0jz"
Document name
Document type
Asset ID
Relevant snippet
```

## 7.5 Required Answer Format

```text id="i4xo8k"
Answer:
<clear explanation>

Evidence:
<short evidence summary>

Recommended Action:
<maintenance or compliance action>

Sources:
1. <document name>
2. <document name>
3. <document name>
```

## 7.6 Example Query: P-101 Risk

### User Question

```text id="eadhzi"
Why is P-101 high risk?
```

### Expected Answer

```text id="vgiyl5"
P-101 is marked as high risk because inspection report IR-008 shows vibration above the critical threshold, the maintenance log mentions abnormal bearing noise, and the compliance checklist shows missing weekly lubrication evidence.

The most likely issue is bearing wear caused by lubrication degradation or possible shaft misalignment.

Recommended Action:
Inspect the bearing housing, verify lubrication level, check shaft alignment, and schedule maintenance before continued operation increases failure risk.

Sources:
1. P-101_Inspection_Report_IR-008.pdf
2. P-101_Maintenance_Log_Jan2026.pdf
3. P-101_SOP_Lubrication_and_Bearing_Check.pdf
4. P-101_Compliance_Checklist.pdf
```

## 7.7 Error State

If no evidence is found, show:

```text id="a3sydt"
PlantMind could not find enough evidence in the indexed documents to answer this confidently. Try selecting an asset or asking about maintenance, RCA, or compliance.
```

## 7.8 Demo Script Usage

Use this screen to prove RAG:

```text id="ubioo8"
Every answer is grounded in indexed maintenance documents and includes citations. This is important because industrial teams need evidence, not unsupported AI suggestions.
```

## 7.9 Success Criteria

Ask PlantMind is successful if:

```text id="e9csm1"
The user can ask the five primary demo questions.
Each answer includes citations.
The answer is asset-specific.
The recommendation is clear and safe.
```

---

## 8. Screen 4: Knowledge Graph

## 8.1 Route

```text id="n2ruvm"
/graph
```

## 8.2 Purpose

The Knowledge Graph screen visually explains relationships between assets, documents, symptoms, failure modes, maintenance actions, and compliance requirements.

## 8.3 Main User Goal

A user should understand:

```text id="v2r846"
Which symptoms are connected to an asset?
Which documents support the diagnosis?
Which failure modes are possible?
Which actions and compliance requirements are linked?
```

## 8.4 Required Components

```text id="zk3egq"
Graph canvas
Asset filter
Node details side panel
Relationship legend
Evidence list
```

## 8.5 Node Types

The graph must support only these node types:

| Node Type              | Example                            |
| ---------------------- | ---------------------------------- |
| Asset                  | P-101 Pump                         |
| Document               | P-101_Inspection_Report_IR-008.pdf |
| Symptom                | High Vibration                     |
| Failure Mode           | Bearing Wear                       |
| Maintenance Action     | Inspect Bearing Housing            |
| Compliance Requirement | Weekly Lubrication Check           |

## 8.6 Edge Types

The graph must support only these edge types:

```text id="kztg73"
HAS_DOCUMENT
HAS_SYMPTOM
INDICATES_FAILURE
REQUIRES_ACTION
HAS_COMPLIANCE_REQUIREMENT
EVIDENCE_FOR
```

## 8.7 Required Graph Paths

### P-101 Path

```text id="hyi00p"
P-101 Pump
→ High Vibration
→ Bearing Wear
→ Inspect Bearing Housing
→ Weekly Lubrication Check
→ P-101_Compliance_Checklist.pdf
```

### C-201 Path

```text id="e60y6x"
C-201 Compressor
→ Decreasing RUL
→ Compressor Inspection
→ Verify Filter Replacement
→ C-201_RUL_Report.pdf
```

### HX-301 Path

```text id="6elgze"
HX-301 Heat Exchanger
→ Reduced Outlet Temperature
→ Fouling Suspected
→ Cleaning Inspection
→ HX-301_Compliance_Checklist.pdf
```

## 8.8 Node Click Behavior

When a user clicks a node, show side panel.

Example for `Bearing Wear`:

```text id="4l4oc3"
Node: Bearing Wear
Type: Failure Mode

Connected Asset:
P-101 Pump

Connected Symptoms:
- High vibration
- Abnormal bearing noise

Evidence:
- P-101_Inspection_Report_IR-008.pdf
- P-101_Maintenance_Log_Jan2026.pdf

Recommended Actions:
- Inspect bearing housing
- Verify lubrication
- Check shaft alignment
```

## 8.9 Demo Script Usage

Use this screen to say:

```text id="1ix5ps"
This graph makes PlantMind explainable. It shows how P-101 is connected to high vibration, how that indicates bearing wear, and which documents support the recommendation.
```

## 8.10 Success Criteria

The Knowledge Graph screen is successful if judges understand:

```text id="wqd7sp"
PlantMind is not only doing text search.
It is connecting industrial entities.
The recommendation is explainable through relationships.
```

---

## 9. Screen 5: Compliance Center

## 9.1 Route

```text id="1ajvmz"
/compliance
```

## 9.2 Purpose

The Compliance Center shows required evidence, available evidence, missing evidence, overdue checks, and delayed verification.

## 9.3 Main User Goal

A user should quickly answer:

```text id="os5j6t"
Which assets have compliance gaps?
What evidence is missing?
What action should be taken?
Which documents support compliance?
```

## 9.4 Required Components

```text id="pvx5ei"
Compliance summary cards
Compliance table
Status filters
Asset filter
Generate compliance summary button
Gap recommendation panel
```

## 9.5 Summary Cards

Show:

| Metric               | Value |
| -------------------- | ----: |
| Total Requirements   |     6 |
| Available Evidence   |     3 |
| Missing Evidence     |     1 |
| Overdue Evidence     |     1 |
| Delayed Verification |     1 |

## 9.6 Compliance Table

Required rows:

| Asset  | Requirement                     | Expected Evidence      | Status    | Recommended Action                          |
| ------ | ------------------------------- | ---------------------- | --------- | ------------------------------------------- |
| P-101  | Weekly vibration inspection     | Inspection report      | Available | Continue vibration monitoring               |
| P-101  | Weekly lubrication check        | Lubrication record     | Missing   | Perform lubrication check and upload record |
| C-201  | Monthly compressor inspection   | Inspection report      | Available | Continue inspection cycle                   |
| C-201  | Filter replacement verification | Maintenance log        | Delayed   | Verify filter replacement completion        |
| HX-301 | Pressure test report            | Pressure test evidence | Available | Keep pressure evidence updated              |
| HX-301 | Cleaning and fouling inspection | Cleaning record        | Overdue   | Schedule cleaning inspection                |

## 9.7 Status Badge Rules

Use these statuses only:

```text id="u43n5d"
Available
Missing
Overdue
Delayed
Not Required
```

## 9.8 Compliance Summary Output

When the user clicks:

```text id="kwuvq8"
Generate Compliance Summary
```

Show:

```text id="f2klc4"
PlantMind found compliance gaps for two assets.

1. P-101 has missing weekly lubrication evidence.
2. HX-301 has overdue cleaning and fouling inspection evidence.
3. C-201 has available monthly inspection evidence, but filter replacement verification is delayed.

Recommended next steps:
- Upload or complete P-101 lubrication record.
- Schedule HX-301 cleaning inspection.
- Verify C-201 filter replacement completion.
```

## 9.9 Demo Script Usage

Use this screen to say:

```text id="pqwwmw"
PlantMind connects maintenance risk with compliance evidence. For P-101, the technical risk is high vibration, but the compliance gap is missing lubrication evidence.
```

## 9.10 Success Criteria

The Compliance Center is successful if:

```text id="gib3s0"
Missing evidence is easy to identify.
Status badges are clear.
The system recommends next actions.
The compliance story supports the maintenance story.
```

---

## 10. Screen 6: RCA Workspace

## 10.1 Route

```text id="gxlbuq"
/rca
```

## 10.2 Purpose

The RCA Workspace generates structured root-cause analysis reports using evidence from documents, symptoms, maintenance logs, inspection reports, and SOPs.

## 10.3 Main User Goal

A maintenance engineer should be able to generate a usable RCA report for an asset issue.

## 10.4 Required Components

```text id="8dj6xc"
Asset selector
Issue selector
Generate RCA button
RCA report panel
Evidence panel
Export/copy button
```

## 10.5 Supported RCA Cases

Only these cases are in scope:

| Asset  | Issue                        |
| ------ | ---------------------------- |
| P-101  | High vibration               |
| C-201  | Decreasing RUL               |
| HX-301 | Low heat transfer efficiency |

## 10.6 RCA Input Example

```text id="piibpo"
Asset: P-101 Pump
Issue: High vibration
```

## 10.7 RCA Output Sections

The RCA report must include:

```text id="8992d8"
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

## 10.8 Expected RCA Output for P-101

```text id="a270p2"
RCA Report: P-101 High Vibration

Problem Statement:
P-101 is showing repeated high vibration events during normal operation.

Observed Symptoms:
- Vibration above threshold
- Abnormal bearing noise
- Slightly elevated bearing temperature
- Missing lubrication evidence

Evidence:
- Inspection Report IR-008 reports vibration above acceptable threshold.
- Maintenance Log ML-014 mentions abnormal bearing noise.
- SOP-PUMP-01 requires weekly lubrication checks.
- Compliance checklist shows lubrication evidence is missing.

Timeline:
- Previous inspection recorded normal vibration.
- Recent maintenance log reported abnormal bearing noise.
- Latest inspection shows vibration above threshold.
- Compliance review found missing lubrication evidence.

Possible Causes:
1. Bearing wear
2. Lubrication degradation
3. Shaft misalignment
4. Loose mounting
5. Operating load variation

Most Likely Root Cause:
Bearing wear caused by lubrication degradation or possible shaft misalignment.

Corrective Action:
Inspect the bearing housing, verify lubrication level and lubricant quality, check shaft alignment, inspect mounting bolts, and replace the bearing if vibration remains above threshold.

Preventive Action:
Add weekly lubrication evidence verification, monitor vibration trend automatically, and trigger alerts when vibration crosses warning threshold.

Confidence:
Medium-High

Sources:
1. P-101_Inspection_Report_IR-008.pdf
2. P-101_Maintenance_Log_Jan2026.pdf
3. P-101_SOP_Lubrication_and_Bearing_Check.pdf
4. P-101_Compliance_Checklist.pdf
```

## 10.9 Demo Script Usage

Use this screen to say:

```text id="skt0jc"
Normally, RCA preparation requires engineers to manually collect logs, inspection reports, SOPs, and evidence. PlantMind organizes this information into a structured RCA report with citations.
```

## 10.10 Success Criteria

The RCA Workspace is successful if:

```text id="fg5jtl"
The RCA is structured.
The root cause is evidence-backed.
The corrective and preventive actions are clear.
Sources are visible.
```

---

## 11. Screen 7: Document Library

## 11.1 Route

```text id="iar819"
/documents
```

## 11.2 Purpose

The Document Library shows all indexed documents, extracted metadata, asset tags, document types, and indexing status.

## 11.3 Main User Goal

A user should know:

```text id="2f0jhq"
Which documents are indexed?
Which asset is each document linked to?
What tags were extracted?
Which documents were used as evidence?
```

## 11.4 Required Components

```text id="2jwgcc"
Document table
Asset filter
Document type filter
Indexing status badge
Extracted tags
Document detail drawer
Upload/preload button
```

## 11.5 Document Table Columns

| Column         | Description                           |
| -------------- | ------------------------------------- |
| Document Name  | File name                             |
| Asset ID       | Linked asset                          |
| Document Type  | SOP, inspection, log, checklist, etc. |
| Date           | Document date                         |
| Extracted Tags | Important terms                       |
| Status         | Indexed / Pending / Failed            |
| Actions        | View details                          |

## 11.6 Required Document Rows

### P-101 Documents

```text id="2pgz19"
P-101_Datasheet.pdf
P-101_Maintenance_Log_Jan2026.pdf
P-101_Inspection_Report_IR-008.pdf
P-101_SOP_Lubrication_and_Bearing_Check.pdf
P-101_Incident_Report_High_Vibration.pdf
P-101_Compliance_Checklist.pdf
P-101_Pump_Drawing.png
```

### C-201 Documents

```text id="3d6rlu"
C-201_Datasheet.pdf
C-201_Maintenance_Log_Feb2026.pdf
C-201_RUL_Report.pdf
C-201_SOP_Compressor_Shutdown.pdf
C-201_Inspection_Report.pdf
C-201_Compliance_Checklist.pdf
C-201_Compressor_Drawing.png
```

### HX-301 Documents

```text id="y4g4ig"
HX-301_Datasheet.pdf
HX-301_Inspection_Report.pdf
HX-301_Cleaning_Record.pdf
HX-301_SOP_Pressure_Test.pdf
HX-301_Compliance_Checklist.pdf
HX-301_Incident_Report_Low_Efficiency.pdf
HX-301_Heat_Exchanger_Drawing.png
```

## 11.7 Document Detail Drawer

When a user clicks a document, show:

```text id="k688pk"
Document ID
File name
Asset ID
Document type
Document date
Extracted tags
Short summary
Linked graph nodes
Used in answers
```

## 11.8 Demo Script Usage

Use this screen if judges ask how the system knows the information:

```text id="xdp3n8"
This library shows the indexed document base. Each document is linked to an asset, classified by type, tagged, embedded, and made available for cited retrieval.
```

## 11.9 Success Criteria

The Document Library is successful if:

```text id="7dax2b"
All demo documents are visible.
Each document has asset metadata.
Indexing status is clear.
Documents support citations in Ask PlantMind and RCA.
```

---

## 12. Primary Demo Flow Across Screens

The final demo should follow this exact UI flow:

```text id="xp96q3"
Dashboard
    ↓
Ask PlantMind
    ↓
Asset 360 View for P-101
    ↓
Knowledge Graph
    ↓
RCA Workspace
    ↓
Compliance Center
    ↓
Optional: Document Library
```

## 12.1 Demo Flow Detail

### Step 1

Open Dashboard and show:

```text id="kxr13v"
P-101 is high risk.
```

### Step 2

Open Ask PlantMind and ask:

```text id="5fzqmm"
Why is P-101 high risk?
```

### Step 3

Open Asset 360 for P-101 and show:

```text id="jexgyd"
Vibration trend
Maintenance history
Linked documents
Recommended action
```

### Step 4

Open Knowledge Graph and show:

```text id="tdyyi5"
P-101 → High Vibration → Bearing Wear → Lubrication Missing → SOP Requirement
```

### Step 5

Open RCA Workspace and generate:

```text id="tcfekm"
RCA for P-101 high vibration
```

### Step 6

Open Compliance Center and show:

```text id="ycdlgp"
P-101 lubrication evidence missing.
HX-301 cleaning evidence overdue.
C-201 filter verification delayed.
```

### Step 7

Optional: Open Document Library and show:

```text id="v9bk1x"
All cited documents are indexed and linked to assets.
```

---

## 13. Required Reusable Components

## 13.1 AssetCard

Used in:

```text id="3r4wns"
Dashboard
Assets overview
```

Displays:

```text id="rkq4rn"
Asset ID
Asset name
Asset type
Health score
Risk level
Main issue
Recommended action
```

## 13.2 HealthScore

Used in:

```text id="863mrm"
Dashboard
Asset 360
```

Displays:

```text id="93k6h1"
Numeric health score
Visual ring or progress bar
Risk label
```

## 13.3 RiskBadge

Allowed values:

```text id="c27229"
Low
Medium
High
```

## 13.4 StatusBadge

Allowed values:

```text id="ksm7qe"
Available
Missing
Overdue
Delayed
Not Required
Indexed
Pending
Failed
```

## 13.5 CitationCard

Displays:

```text id="mlcayj"
Document name
Document type
Asset ID
Short evidence snippet
```

## 13.6 EvidencePanel

Displays:

```text id="tf21gf"
Source documents
Evidence snippets
Linked symptoms
Linked actions
```

## 13.7 KnowledgeGraph

Displays:

```text id="6f8o45"
Nodes
Edges
Asset filter
Node side panel
```

## 13.8 ComplianceTable

Displays:

```text id="dj4do3"
Asset
Requirement
Expected evidence
Status
Recommended action
```

## 13.9 RCAReport

Displays:

```text id="9qjyia"
Problem statement
Evidence
Root cause
Corrective action
Preventive action
Sources
```

---

## 14. UI Data Contracts

## 14.1 Asset Object

```json id="v6cv08"
{
  "asset_id": "P-101",
  "asset_name": "Cooling Water Circulation Pump",
  "asset_type": "Pump",
  "criticality": "High",
  "location": "Utility Area - Line A",
  "health_score": 62,
  "risk_level": "High",
  "main_issue": "High vibration + missing lubrication evidence",
  "recommended_action": "Inspect bearing housing and verify lubrication"
}
```

## 14.2 Document Object

```json id="7vvxpu"
{
  "document_id": "IR-008",
  "file_name": "P-101_Inspection_Report_IR-008.pdf",
  "asset_id": "P-101",
  "document_type": "Inspection Report",
  "document_date": "2026-01-21",
  "status": "Indexed",
  "tags": ["vibration", "bearing", "inspection"],
  "summary": "P-101 vibration exceeded critical threshold."
}
```

## 14.3 Compliance Object

```json id="y0h35w"
{
  "asset_id": "P-101",
  "requirement": "Weekly lubrication check",
  "expected_evidence": "Lubrication record",
  "status": "Missing",
  "evidence_file": null,
  "recommended_action": "Perform lubrication check and upload record"
}
```

## 14.4 Ask PlantMind Response Object

```json id="7jyw48"
{
  "answer": "P-101 is marked as high risk because vibration is above threshold and lubrication evidence is missing.",
  "recommended_action": "Inspect bearing housing and verify lubrication.",
  "confidence": "Medium-High",
  "sources": [
    {
      "document_id": "IR-008",
      "file_name": "P-101_Inspection_Report_IR-008.pdf",
      "document_type": "Inspection Report",
      "snippet": "Measured vibration exceeded critical threshold."
    }
  ]
}
```

## 14.5 Graph Object

```json id="pn3o8p"
{
  "nodes": [
    {
      "id": "P-101",
      "label": "P-101 Pump",
      "type": "Asset"
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

## 15. Empty, Loading, and Error States

## 15.1 Loading State

Use loading skeletons for:

```text id="b4yy9g"
Dashboard cards
Asset details
Ask PlantMind answer
RCA generation
Graph loading
Compliance table
Document table
```

## 15.2 Empty State

Example:

```text id="bl6kj9"
No documents found for this asset.
```

Example:

```text id="762zg4"
No compliance gaps found for the selected filter.
```

## 15.3 Error State

Example:

```text id="50tro1"
Unable to load PlantMind data. Please check the backend service or reload the page.
```

## 15.4 RAG No-Evidence State

Example:

```text id="wse9ga"
PlantMind could not find enough evidence in the indexed documents to answer this confidently.
```

---

## 16. UI Priority Plan

## 16.1 Must-Have Screens

These must be completed first:

```text id="9f6d1t"
Dashboard
Ask PlantMind
Asset 360 View
RCA Workspace
Compliance Center
```

## 16.2 Should-Have Screens

Complete after must-have screens:

```text id="vcbk4s"
Knowledge Graph
Document Library
```

## 16.3 Nice-to-Have UI Polish

Only add if time remains:

```text id="5izw3o"
Dark mode
Advanced filters
Export PDF button
Animated graph transitions
Advanced search
User profile
```

---

## 17. UI Build Order

Recommended implementation order:

```text id="tsx4yt"
1. Global layout and sidebar
2. Dashboard
3. Asset 360 View
4. Ask PlantMind
5. Compliance Center
6. RCA Workspace
7. Document Library
8. Knowledge Graph
9. UI polish and demo fixes
```

Reason:

* Dashboard gives immediate visual progress.
* Asset 360 establishes the core product.
* Ask PlantMind proves AI.
* Compliance and RCA prove workflow.
* Graph adds advanced credibility.

---

## 18. Design Tone and Visual Style

The UI should feel:

```text id="6530qf"
Industrial
Reliable
Modern
Evidence-backed
Enterprise-ready
Calm
Professional
```

Avoid making it look like:

```text id="8mhs64"
A generic chatbot
A student-only dashboard
A flashy AI toy
A complex ERP
A fake IoT control panel
```

## 18.1 Suggested Visual Style

Use:

```text id="cx68a8"
White or near-white background
Dark sidebar
Clear card layout
Compact tables
Professional status badges
Simple line charts
Clean typography
Moderate spacing
```

## 18.2 Important UI Principle

Every major AI output should show evidence.

For example:

```text id="xdcehu"
Do not only show:
"P-101 is high risk."

Show:
"P-101 is high risk because vibration exceeded threshold, bearing noise was recorded, and lubrication evidence is missing."

Then show sources.
```

---

## 19. Final UI Acceptance Checklist

Before final demo, verify:

```text id="29ifza"
[ ] Sidebar navigation works.
[ ] Dashboard shows all frozen metrics.
[ ] P-101 is clearly marked High Risk.
[ ] Asset 360 opens for P-101, C-201, and HX-301.
[ ] Ask PlantMind shows suggested questions.
[ ] Ask PlantMind answers include citations.
[ ] Knowledge Graph shows P-101 relationship path.
[ ] Compliance Center shows missing, overdue, and delayed evidence.
[ ] RCA Workspace generates P-101 high vibration RCA.
[ ] Document Library shows all synthetic documents.
[ ] Health scores match frozen scope.
[ ] Risk levels match frozen scope.
[ ] Demo flow can be completed in 6 to 8 minutes.
[ ] UI does not include unnecessary extra screens.
```

---

## 20. Final UI Scope Statement

PlantMind AI will include exactly seven major UI screens:

```text id="xa2afw"
Dashboard
Asset 360 View
Ask PlantMind
Knowledge Graph
Compliance Center
RCA Workspace
Document Library
```

These screens support the final product workflow:

```text id="o9qt9y"
Asset Risk
    ↓
Evidence-backed AI Answer
    ↓
Asset 360 Investigation
    ↓
Knowledge Graph Explanation
    ↓
Root-Cause Analysis
    ↓
Compliance Gap Detection
    ↓
Maintenance Recommendation
```

The UI scope is intentionally focused on making the project demo-ready, credible, and understandable for hackathon judges.

This UI screen list is now frozen.
