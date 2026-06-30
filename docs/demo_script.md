# Demo Script

## Project Name

**PlantMind AI**

## Project Title

**PlantMind AI: Industrial Asset & Operations Brain for Maintenance, RCA, and Compliance Intelligence**

---

## 1. Demo Objective

The goal of this demo is to show how PlantMind AI transforms scattered industrial documents, maintenance records, sensor trends, inspection reports, SOPs, and compliance checklists into an explainable asset intelligence system.

The demo should prove that PlantMind AI can:

1. Identify high-risk industrial assets.
2. Explain asset risk using cited evidence.
3. Connect maintenance records, SOPs, symptoms, and failures.
4. Generate root-cause analysis reports.
5. Detect missing compliance evidence.
6. Recommend maintenance actions.
7. Provide a realistic industrial workflow for plant maintenance teams.

---

## 2. Demo Theme

**From scattered industrial documents to actionable maintenance intelligence.**

PlantMind AI acts as an industrial operations brain that helps maintenance engineers and plant teams answer critical questions such as:

* Why is this asset at risk?
* What evidence supports this issue?
* What is the likely root cause?
* Which maintenance action should be taken?
* Which compliance evidence is missing?
* Which documents are related to this asset?

---

## 3. Demo Scope

The demo is intentionally limited to three industrial assets.

| Asset ID | Asset Name     | Asset Type         | Demo Role                                                   |
| -------- | -------------- | ------------------ | ----------------------------------------------------------- |
| P-101    | Pump           | Rotating Equipment | Main demo asset for high vibration, RCA, and compliance gap |
| C-201    | Compressor     | Rotating Equipment | RUL degradation and maintenance planning                    |
| HX-301   | Heat Exchanger | Process Equipment  | Fouling suspicion and missing cleaning evidence             |

The primary demo story focuses on **P-101 Pump**.

---

## 4. Recommended Demo Duration

Total recommended duration: **6 to 8 minutes**

| Section             |   Duration |
| ------------------- | ---------: |
| Opening pitch       | 45 seconds |
| Dashboard overview  | 60 seconds |
| Ask PlantMind query | 90 seconds |
| Asset 360 view      | 90 seconds |
| Knowledge graph     | 60 seconds |
| RCA generation      | 90 seconds |
| Compliance center   | 60 seconds |
| Closing statement   | 30 seconds |

---

## 5. Demo Persona

The demo should be presented from the perspective of a maintenance engineer, reliability engineer, or plant operations manager.

### Demo user persona

**Name:** Maintenance Engineer
**Goal:** Quickly understand why an asset is at risk and decide what action should be taken.
**Pain point:** Relevant information is scattered across PDFs, logs, SOPs, inspections, and compliance records.
**PlantMind AI value:** Gives one explainable, evidence-backed view of asset risk and maintenance action.

---

## 6. Opening Script

### Presenter Script

“Industrial plants generate huge amounts of operational knowledge across maintenance logs, SOPs, inspection reports, compliance checklists, incident reports, sensor data, and engineering drawings.

But this knowledge is usually scattered across multiple systems and documents. When an asset starts showing abnormal behavior, engineers spend a lot of time searching for evidence, connecting symptoms, checking SOPs, and preparing root-cause reports.

PlantMind AI solves this problem by creating an Industrial Asset and Operations Brain.

For this demo, we have frozen the plant scope to three assets: P-101 Pump, C-201 Compressor, and HX-301 Heat Exchanger.

PlantMind AI helps teams ask questions, understand asset risk, generate RCA reports, find compliance gaps, and recommend maintenance actions using cited evidence.”

---

## 7. Demo Step 1: Dashboard Overview

### Screen

`Dashboard`

### Goal

Show that PlantMind AI gives a quick plant-level health and risk summary.

### User Action

Open the PlantMind AI dashboard.

### What to Show

The dashboard should display:

```text
Total Assets: 3
High Risk Assets: 1
Compliance Gaps: 3
Open Maintenance Actions: 4
Average Health Score: 67%
```

Asset cards:

```text
P-101 Pump
Health: 62%
Risk: High
Reason: High vibration + missing lubrication evidence

C-201 Compressor
Health: 71%
Risk: Medium
Reason: RUL decreasing + delayed filter replacement

HX-301 Heat Exchanger
Health: 68%
Risk: Medium
Reason: Fouling suspected + cleaning overdue
```

### Presenter Script

“This dashboard gives a quick view of plant health. We currently have three assets in scope.

P-101 Pump is marked as high risk with a health score of 62 percent. The system has identified high vibration and missing lubrication evidence.

C-201 Compressor has medium risk because the RUL trend is decreasing.

HX-301 Heat Exchanger also has medium risk because fouling is suspected and cleaning evidence is overdue.

For the rest of the demo, I will focus mainly on P-101 because it shows the complete workflow from risk detection to root-cause analysis and compliance checking.”

### Expected Outcome

The judge should understand that PlantMind AI is not just a chatbot. It starts with an asset-level intelligence dashboard.

---

## 8. Demo Step 2: Ask PlantMind

### Screen

`Ask PlantMind`

### Goal

Show RAG-based industrial question answering with source citations.

### User Action

Click the suggested question:

```text
Why is P-101 high risk?
```

Or type:

```text
Why is P-101 high risk?
```

### Expected PlantMind Answer

```text
P-101 is marked as high risk because multiple evidence sources indicate a developing rotating-equipment issue.

Inspection Report IR-008 shows that vibration readings exceeded the acceptable threshold. The maintenance log mentions abnormal bearing noise during recent operation. The compliance checklist also shows that weekly lubrication evidence is missing.

Based on this evidence, the most likely issue is bearing wear caused by lubrication degradation or possible shaft misalignment.

Recommended action:
Inspect the bearing housing, verify lubrication level, check shaft alignment, and schedule maintenance before continued operation increases failure risk.

Sources:
1. P-101_Inspection_Report_IR-008.pdf
2. P-101_Maintenance_Log_Jan2026.pdf
3. P-101_SOP_Lubrication_and_Bearing_Check.pdf
4. P-101_Compliance_Checklist.pdf
```

### Presenter Script

“Now I will ask PlantMind why P-101 is high risk.

The answer is not generic. It is grounded in actual indexed documents. PlantMind connects the inspection report, maintenance log, SOP, and compliance checklist.

It explains that vibration is above threshold, bearing noise was reported, and weekly lubrication evidence is missing.

Most importantly, every answer includes source citations. This is critical for industrial use cases because engineers need evidence, not just AI-generated suggestions.”

### Expected Outcome

The judge should see that the system can answer maintenance questions using document-grounded RAG with citations.

---

## 9. Demo Step 3: Asset 360 View

### Screen

`Asset 360 View`

### Goal

Show a complete asset-level intelligence page for P-101.

### User Action

Open:

```text
Assets → P-101 Pump
```

### What to Show

The P-101 Asset 360 page should include:

```text
Asset ID: P-101
Asset Name: Pump
Asset Type: Rotating Equipment
Criticality: High
Health Score: 62%
Risk Level: High
Latest Issue: High vibration
Recommended Action: Inspect bearing housing and verify lubrication
```

Tabs to show:

```text
Overview
Maintenance History
Sensor Trends
Documents
Compliance
RCA
```

### Show Overview Tab

Display:

```text
Main Risk Driver:
High vibration + missing lubrication evidence

Possible Failure Mode:
Bearing wear

Recommended Maintenance:
Inspect bearing housing, check lubrication, verify shaft alignment, replace bearing if required.
```

### Show Sensor Trends Tab

Display a vibration trend chart.

Example trend:

```text
Day 1: Normal
Day 2: Normal
Day 3: Slight increase
Day 4: Warning
Day 5: Above threshold
Day 6: Above threshold
```

### Show Documents Tab

Display linked evidence documents:

```text
P-101_Inspection_Report_IR-008.pdf
P-101_Maintenance_Log_Jan2026.pdf
P-101_SOP_Lubrication_and_Bearing_Check.pdf
P-101_Compliance_Checklist.pdf
```

### Presenter Script

“This is the Asset 360 view for P-101.

Instead of making engineers search across different files and systems, PlantMind brings everything into one asset page.

Here we can see the health score, risk level, latest issue, sensor trend, linked documents, compliance status, and recommended action.

The vibration trend shows that the issue is not isolated. It has been increasing over time.

The document section shows all evidence files connected to this asset. These are the same documents used by the AI assistant to explain the risk.”

### Expected Outcome

The judge should understand that PlantMind AI provides a complete asset-centered workflow, not only a question-answering interface.

---

## 10. Demo Step 4: Knowledge Graph

### Screen

`Knowledge Graph`

### Goal

Show that PlantMind AI connects industrial knowledge as relationships.

### User Action

Open the Knowledge Graph screen and filter by:

```text
Asset: P-101
```

### What to Show

Graph path:

```text
P-101
  → High Vibration
  → Bearing Wear
  → Lubrication Evidence Missing
  → SOP-PUMP-01
  → Weekly Lubrication Inspection
  → Inspect Bearing Housing
```

### Node Types

The graph should show these node categories:

```text
Asset
Symptom
Failure Mode
Document
Maintenance Action
Compliance Requirement
```

### Example Node Click

Click node:

```text
Bearing Wear
```

Side panel should show:

```text
Node: Bearing Wear

Connected Asset:
P-101

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

### Presenter Script

“This knowledge graph is what makes PlantMind more than a document chatbot.

It connects the asset P-101 with symptoms, possible failure modes, source documents, maintenance actions, and compliance requirements.

For example, P-101 is connected to high vibration. High vibration indicates possible bearing wear. Bearing wear is linked to missing lubrication evidence and the lubrication SOP.

This helps engineers understand why the AI reached its conclusion and what evidence supports the recommendation.”

### Expected Outcome

The judge should see explainability through graph relationships.

---

## 11. Demo Step 5: RCA Workspace

### Screen

`RCA Workspace`

### Goal

Show automatic root-cause analysis generation.

### User Action

Select:

```text
Asset: P-101
Issue: High vibration
```

Click:

```text
Generate RCA
```

### Expected RCA Output

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

### Presenter Script

“Now I will generate an RCA report for P-101 high vibration.

Normally, preparing an RCA requires engineers to manually collect logs, inspection reports, SOPs, and evidence. PlantMind automatically organizes this into a structured RCA.

The report includes the problem statement, observed symptoms, evidence, possible causes, likely root cause, corrective action, preventive action, confidence level, and source documents.

This is especially useful because it converts scattered maintenance knowledge into a decision-ready engineering report.”

### Expected Outcome

The judge should see that PlantMind AI can convert evidence into a structured RCA workflow.

---

## 12. Demo Step 6: Compliance Center

### Screen

`Compliance Center`

### Goal

Show missing evidence detection and compliance gap summary.

### User Action

Open Compliance Center.

Then click:

```text
Generate Compliance Summary
```

### What to Show

Compliance table:

```text
Asset: P-101
Requirement: Weekly vibration inspection
Evidence: P-101_Inspection_Report_IR-008.pdf
Status: Available

Asset: P-101
Requirement: Weekly lubrication check
Evidence: Missing
Status: Missing

Asset: C-201
Requirement: Monthly compressor inspection
Evidence: C-201_Inspection_Report.pdf
Status: Available

Asset: C-201
Requirement: Filter replacement verification
Evidence: C-201_Maintenance_Log_Feb2026.pdf
Status: Delayed

Asset: HX-301
Requirement: Pressure test
Evidence: HX-301_SOP_Pressure_Test.pdf
Status: Available

Asset: HX-301
Requirement: Cleaning and fouling inspection
Evidence: Missing or overdue
Status: Overdue
```

### Expected Compliance Summary

```text
PlantMind found compliance gaps for two assets.

1. P-101 has missing weekly lubrication evidence.
2. HX-301 has overdue cleaning and fouling inspection evidence.
3. C-201 has available monthly inspection evidence, but filter replacement verification is delayed.

Recommended next steps:
- Upload or complete P-101 lubrication record.
- Schedule HX-301 cleaning inspection.
- Verify C-201 filter replacement completion.
```

### Presenter Script

“PlantMind also checks compliance evidence.

Here, the system shows which required checks have supporting evidence and which are missing or overdue.

For P-101, weekly vibration inspection evidence is available, but lubrication evidence is missing.

For HX-301, pressure test evidence is available, but cleaning and fouling inspection evidence is overdue.

This is important because maintenance and compliance are connected. An asset may not only have a technical risk but also an evidence gap.”

### Expected Outcome

The judge should understand that PlantMind AI supports compliance workflows, not just maintenance diagnosis.

---

## 13. Demo Step 7: C-201 Compressor Quick View

### Screen

`Asset 360 View` or `Ask PlantMind`

### Goal

Briefly show that the system supports another asset, but without changing the main story.

### User Action

Ask:

```text
What maintenance should be planned for C-201?
```

### Expected Answer

```text
C-201 should be scheduled for compressor inspection and filter replacement verification because the RUL trend is decreasing, outlet temperature has increased, and pressure ratio instability has been observed.

Recommended action:
Plan inspection within the next maintenance window, verify filter replacement, check outlet temperature trend, and review compressor shutdown SOP before intervention.

Sources:
1. C-201_RUL_Report.pdf
2. C-201_Maintenance_Log_Feb2026.pdf
3. C-201_Inspection_Report.pdf
4. C-201_SOP_Compressor_Shutdown.pdf
```

### Presenter Script

“To show that this is not limited to one asset, we can also ask about C-201 Compressor.

PlantMind uses the RUL report, maintenance log, inspection report, and SOP to recommend maintenance planning.

This shows how the same architecture can support predictive maintenance and planning for rotating equipment.”

### Expected Outcome

The judge should see that PlantMind AI supports multiple frozen assets while keeping the demo focused.

---

## 14. Demo Step 8: HX-301 Quick Compliance Query

### Screen

`Ask PlantMind` or `Compliance Center`

### Goal

Briefly show compliance intelligence for process equipment.

### User Action

Ask:

```text
What evidence is missing for HX-301?
```

### Expected Answer

```text
HX-301 is missing current cleaning and fouling inspection evidence. The inspection report indicates possible fouling because outlet temperature is below target and pressure drop is increasing. The compliance checklist marks the cleaning record as overdue.

Pressure test evidence is available, but cleaning evidence must be updated.

Sources:
1. HX-301_Inspection_Report.pdf
2. HX-301_Cleaning_Record.pdf
3. HX-301_Compliance_Checklist.pdf
4. HX-301_SOP_Pressure_Test.pdf
```

### Presenter Script

“For HX-301, PlantMind identifies a different type of issue. Instead of vibration or RUL, the problem is process performance and compliance evidence.

It detects possible fouling and points out that the cleaning record is overdue or missing.

This shows that the platform can support both rotating equipment and process equipment.”

### Expected Outcome

The judge should see that PlantMind AI can generalize across the three selected asset types.

---

## 15. Closing Script

### Presenter Script

“To summarize, PlantMind AI acts as an Industrial Asset and Operations Brain.

In this demo, we showed how the system identifies P-101 as a high-risk pump, explains the reason using cited evidence, connects symptoms and failures through a knowledge graph, generates a structured RCA report, and detects compliance evidence gaps.

The value is that maintenance teams no longer need to manually search across logs, SOPs, inspection reports, and compliance checklists. PlantMind brings all of that knowledge together into one explainable intelligence layer.

This can help reduce downtime risk, improve maintenance planning, speed up root-cause analysis, and strengthen compliance readiness.”

---

## 16. Primary Demo Questions

The system must be able to answer these questions confidently during the demo.

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

## 17. Backup Questions

Use these only if judges ask follow-up questions.

### Question 1

```text
What documents are linked to P-101?
```

Expected answer:

```text
The documents linked to P-101 are the datasheet, maintenance log, inspection report IR-008, lubrication and bearing check SOP, incident report, compliance checklist, and pump drawing.
```

### Question 2

```text
What is the likely root cause of P-101 vibration?
```

Expected answer:

```text
The likely root cause is bearing wear caused by lubrication degradation or possible shaft misalignment.
```

### Question 3

```text
What compliance gaps exist in the plant?
```

Expected answer:

```text
The main compliance gaps are missing weekly lubrication evidence for P-101 and overdue cleaning or fouling inspection evidence for HX-301. C-201 also has delayed filter replacement verification.
```

### Question 4

```text
How does PlantMind generate recommendations?
```

Expected answer:

```text
PlantMind combines document retrieval, extracted metadata, sensor trends, compliance rules, and asset knowledge graph relationships to generate evidence-backed recommendations.
```

### Question 5

```text
Is this replacing engineers?
```

Expected answer:

```text
No. PlantMind AI is designed as a decision-support system. It helps engineers find evidence faster, understand risk, and prepare RCA or compliance summaries. Final maintenance decisions remain with qualified plant teams.
```

---

## 18. Demo Risk Handling

### If the RAG answer fails

Use the preloaded suggested questions instead of typing free-form queries.

Recommended fallback:

```text
Why is P-101 high risk?
```

### If the graph does not load

Move to Asset 360 and explain:

```text
The graph relationships are also represented here through linked symptoms, documents, failure modes, and recommended actions.
```

### If the RCA generation is slow

Use a pre-generated RCA report stored in the demo data and show it directly.

### If sensor model output is not ready

Use precomputed health scores and trend charts.

### If document upload is not ready

Use preloaded indexed documents in the Document Library.

---

## 19. Judge-Facing Differentiators

During the demo, emphasize these points:

### 1. Evidence-backed AI

PlantMind does not give unsupported answers. It cites source documents.

### 2. Industrial workflow fit

The system supports maintenance, RCA, compliance, and asset risk in one flow.

### 3. Knowledge graph explainability

The graph makes AI reasoning easier to inspect.

### 4. Practical scope

The project is intentionally scoped to three assets, making it realistic and demo-ready.

### 5. Hybrid intelligence

PlantMind combines RAG, rules, graph relationships, and sensor trends instead of relying only on a chatbot.

---

## 20. Final Demo Success Criteria

The demo is successful if the audience understands the following story:

```text
P-101 Pump is high risk.

PlantMind AI explains that the risk is caused by high vibration, abnormal bearing noise, and missing lubrication evidence.

It cites inspection reports, maintenance logs, SOPs, and compliance checklists.

It shows the relationship between the asset, symptom, failure mode, document evidence, and maintenance action.

It generates a root-cause analysis report.

It detects missing compliance evidence.

It recommends corrective and preventive maintenance action.
```

---

## 21. Final Demo Statement

PlantMind AI converts scattered industrial knowledge into actionable maintenance intelligence.

It helps plant teams move from:

```text
Documents → Evidence → Asset Risk → Root Cause → Compliance Gap → Maintenance Action
```

This is the core demo story and should not be changed.
