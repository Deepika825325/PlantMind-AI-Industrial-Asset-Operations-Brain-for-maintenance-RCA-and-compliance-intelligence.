# PlantMind Nexus Demo Script

## Goal

Show PlantMind Nexus as a closed-loop industrial maintenance intelligence system for P-101.

The demo should prove that PlantMind is not only a prediction dashboard and not only a RAG chatbot. It connects telemetry, anomaly explanation, RCA reasoning, SOP evidence, governed work orders, post-maintenance verification, and audit-ready compliance into one workflow.

## Primary Demo Page

Open this page first:

/demo/p101-closed-loop

## Recommended Judge Walkthrough

### 1. Start with the P-101 closed-loop timeline

Show the seven-step workflow:

1. Telemetry replay
2. Anomaly detection
3. Incident creation
4. RCA hypothesis generation
5. Governed work order
6. Recovery verification
7. Audit-ready compliance package

Explain:

PlantMind starts from abnormal telemetry and moves all the way to governed maintenance action and audit evidence.

### 2. Show anomaly explanation

Use the Day 2 panel.

Highlight:

- Primary driver: vibration
- Secondary driver: bearing temperature
- Model confidence
- Model registry link
- Human review requirement

Explain:

The anomaly is not a black-box alert. PlantMind explains why the asset is abnormal and which signals contributed.

### 3. Show failure hypothesis ranking

Use the Day 3 panel.

Highlight:

- Lubrication degradation ranked first
- Bearing damage ranked second
- Misalignment and cavitation kept as alternatives
- Sensor fault treated as low probability
- Contradictions and missing tests are visible

Explain:

PlantMind does not jump to one answer. It ranks plausible causes, shows evidence, lists contradictions, and recommends the next test.

### 4. Show SOP/RAG evidence

Use the Day 4 panel.

Highlight:

- SOP-P101-001
- SOP-P101-002
- IR-P101-001
- IR-P101-002
- INC-P101-001
- COMP-001

Explain:

The maintenance decision is backed by SOPs, inspection evidence, incident context, and compliance evidence.

### 5. Show evaluation summary

Use the Day 5 panel.

Highlight:

- Overall judge-readiness score
- Closed-loop completion
- Anomaly explanation coverage
- Failure hypothesis quality
- RAG evidence grounding
- Governance and safety controls

Explain:

This panel summarizes why the system is demo-ready and where its honest limitations are.

## Important Frontend Pages

- /demo/p101-closed-loop
- /asset-health
- /incidents
- /rca-orchestration
- /work-order-lifecycle
- /post-maintenance-verification
- /compliance-audit-package
- /model-registry
- /rag-console
- /documents

## Important Backend Endpoints

- POST /demo/p101/run-closed-loop
- POST /demo/p101/reset
- GET /demo/p101/status
- GET /demo/p101/timeline
- GET /demo/p101/anomaly-explanation
- GET /demo/p101/failure-hypotheses
- GET /demo/p101/sop-evidence
- GET /demo/p101/evaluation-summary
- GET /metrics
- GET /observability/health
- GET /mlops/model-registry/overview
- GET /compliance/audit-packages/assets/P-101
- GET /admin/security-review

## Closing Pitch

PlantMind Nexus turns scattered industrial records and sensor signals into traceable maintenance decisions.

For P-101, it shows:

- what changed,
- why it matters,
- which failure causes are most likely,
- which SOPs and evidence support the decision,
- what work order should be governed,
- what verification is required,
- and what audit package proves closure readiness.

## Honest Limitation Statement

This demo uses deterministic demo telemetry and curated industrial evidence. In real deployment, PlantMind would connect to plant historians, CMMS systems, document repositories, and approval workflows.

This is a production-ready demo architecture, not a live connected plant installation.
