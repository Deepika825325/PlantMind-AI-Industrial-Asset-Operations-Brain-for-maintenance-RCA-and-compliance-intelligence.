# PlantMind Nexus Migration Strategy

**Source version:** PlantMind `v0.2.0` Demo Stable
**Target version:** PlantMind Nexus `v1`
**Migration approach:** Additive and backward compatible

## 1. Objective

PlantMind Nexus will evolve the current PlantMind application into a closed-loop industrial reliability platform without rebuilding the existing system.

The current application will remain operational while production-grade storage, telemetry, machine learning, authentication, observability and deployment capabilities are introduced incrementally.

The target reliability workflow is:

```text
Detect → Contextualise → Explain → Act → Verify → Learn
```

## 2. Migration Principles

The migration must follow these rules:

1. Do not rebuild the existing application.
2. Preserve all current frontend routes.
3. Preserve all current public API contracts.
4. Preserve stable demo identifiers.
5. Keep JSON demo mode operational.
6. Introduce production infrastructure incrementally.
7. Prefer additive changes over destructive refactoring.
8. Validate every migration step with automated regression tests.
9. Keep the application demonstrable without external infrastructure.
10. Require explicit approval for breaking changes.

## 3. Stable Domain Identifiers

The following identifiers must remain unchanged:

### Assets

* `P-101`
* `C-201`
* `HX-301`

### RCA

* `RCA-P101-001`

### Evidence

* `P101-EV-001`
* `P101-EV-002`
* `P101-EV-003`
* `P101-EV-004`

Existing work-order IDs, document IDs and compliance-rule IDs must also remain compatible.

These identifiers connect the dashboard, Asset 360, RCA, maintenance, compliance, documents, evidence and P&ID modules.

## 4. Dual Data Modes

PlantMind Nexus will support two runtime modes.

### Demo Mode

```text
PLANTMIND_DATA_MODE=demo
```

Demo mode will use:

* Existing JSON files
* Deterministic seed data
* Demo reset support
* Local historical telemetry replay
* No required external infrastructure
* Fast automated testing
* Offline demonstration support

### Production Mode

```text
PLANTMIND_DATA_MODE=production
```

Production mode will use:

* PostgreSQL
* TimescaleDB
* Qdrant
* Object storage
* Redis
* Background workers
* Authentication
* Audit logging
* Model tracking
* Observability services

Demo mode must remain the default during the early migration stages.

## 5. Repository Migration Pattern

The current data flow is:

```text
Route
  ↓
Service
  ↓
JSON file
```

The target data flow is:

```text
Route
  ↓
Service
  ↓
Repository interface
  ├── JSON repository
  └── PostgreSQL repository
```

Example:

```text
MaintenanceService
  ↓
WorkOrderRepository
  ├── JsonWorkOrderRepository
  └── PostgresWorkOrderRepository
```

The route layer and service behavior should remain stable while the underlying repository implementation changes.

## 6. Recommended Backend Structure

New folders will be introduced gradually:

```text
apps/api/
├── core/
├── routes/
├── services/
├── repositories/
│   ├── base.py
│   ├── json/
│   └── postgres/
├── db/
│   ├── session.py
│   ├── base.py
│   └── migrations/
├── models/
│   ├── database/
│   └── schemas/
├── telemetry/
├── ml/
├── rag/
├── security/
├── workers/
├── audit/
└── integrations/
```

Existing files should not be moved merely to match the target structure.

Folders should be introduced only when the corresponding capability is implemented.

## 7. Configuration Strategy

The target configuration will support:

```text
PLANTMIND_ENV=development
PLANTMIND_DATA_MODE=demo

DATABASE_URL=
REDIS_URL=
QDRANT_URL=
OBJECT_STORAGE_ENDPOINT=

JWT_SECRET=
ACCESS_TOKEN_EXPIRE_MINUTES=30

TELEMETRY_MODE=replay
RAG_MODE=local
MODEL_REGISTRY_MODE=local
```

Configuration values must be loaded through a centralized settings module.

Secrets must not be committed to Git.

## 8. Production Technology Plan

### Existing Stack to Preserve

* Next.js
* React
* TypeScript
* Tailwind CSS
* FastAPI
* Pytest

### Technologies to Introduce

| Requirement                | Technology                 |
| -------------------------- | -------------------------- |
| Transactional storage      | PostgreSQL                 |
| Time-series telemetry      | TimescaleDB                |
| Database migrations        | Alembic                    |
| Vector search              | Qdrant                     |
| Local object storage       | MinIO                      |
| Cloud object storage       | S3-compatible storage      |
| Cache and job coordination | Redis                      |
| Background processing      | Celery or Dramatiq         |
| Authentication             | JWT with OIDC-ready design |
| Model tracking             | MLflow                     |
| Metrics                    | Prometheus                 |
| Dashboards                 | Grafana                    |
| Tracing                    | OpenTelemetry              |
| Containerization           | Docker and Docker Compose  |
| CI/CD                      | GitHub Actions             |

## 9. Technologies Deferred from Nexus v1

The following technologies should not be introduced during the initial migration unless a demonstrated requirement exists:

* Kafka
* Kubernetes
* Neo4j migration
* SAP integration
* IBM Maximo integration
* Full multi-tenancy
* Live OPC-UA plant connectivity
* Video intelligence
* Complex multi-agent orchestration
* Continuous automatic model retraining

PostgreSQL can initially store graph relationships while the current knowledge-graph interface remains unchanged.

## 10. New Nexus Modules

The following frontend routes will be introduced additively:

```text
/telemetry
/anomalies
/anomalies/[anomalyId]
/incidents
/incidents/[incidentId]
/simulations
/models
/evaluations
/monitoring
/audit
/settings
```

Existing routes must remain available.

## 11. Asset 360 Expansion

The current Asset 360 page will remain the primary asset entry point.

Additional capabilities will be introduced as tabs:

```text
/assets/[assetId]
├── overview
├── telemetry
├── health
├── documents
├── inspections
├── anomalies
├── incidents
├── rca
├── maintenance
└── compliance
```

The existing asset page will become the `overview` experience without requiring an immediate route redesign.

## 12. Nexus v1 Product Scenario

The primary demonstration scenario will use `P-101`.

```text
P-101 begins in a healthy state
        ↓
Bearing-degradation telemetry replay starts
        ↓
Vibration and temperature increase
        ↓
Rule-based and ML anomaly detection activate
        ↓
Anomaly records are created
        ↓
Related anomalies are grouped into an incident
        ↓
Asset health score decreases
        ↓
Failure classifier predicts lubrication degradation
        ↓
Sensor evidence is created
        ↓
RCA-P101-001 receives the new evidence
        ↓
Relevant SOPs and maintenance records are retrieved
        ↓
Probable causes are ranked
        ↓
An engineer reviews and approves the conclusion
        ↓
A maintenance recommendation is generated
        ↓
A work order is approved and completed
        ↓
Post-maintenance telemetry is replayed
        ↓
PlantMind verifies vibration and temperature recovery
        ↓
Compliance evidence is updated
        ↓
The verified outcome becomes labelled model feedback
```

## 13. Initial Nexus Domain Models

The first production models to introduce are:

* Telemetry point
* Sensor
* Component
* Anomaly
* Incident
* Asset health snapshot
* Model prediction
* Verification
* Decision trace
* Model feedback record

These models must reference existing PlantMind assets, RCA cases, evidence records and work orders rather than creating disconnected duplicate entities.

## 14. Migration Phases

### Phase 1 — Baseline Protection

* Freeze the current stable state
* Preserve API contracts
* Record frontend routes
* Capture current test results
* Create regression fixtures
* Tag the baseline release

### Phase 2 — Configuration and Repository Boundary

* Add centralized settings
* Introduce repository interfaces
* Implement JSON repositories
* Keep existing service behavior unchanged
* Add repository contract tests

### Phase 3 — Production Storage

* Add PostgreSQL and TimescaleDB
* Add Alembic migrations
* Implement PostgreSQL repositories
* Add seed and reset tooling
* Validate parity between demo and production modes

### Phase 4 — Telemetry and Reliability Intelligence

* Add telemetry replay
* Add rule-based anomaly detection
* Add ML anomaly detection
* Add incident grouping
* Add health-score calculation
* Connect telemetry evidence to RCA

### Phase 5 — Closed-Loop Maintenance

* Generate recommendations from incidents and RCA
* Connect recommendations to work orders
* Add completion workflow
* Add post-maintenance verification
* Create model feedback records

### Phase 6 — Security and Audit

* Add authentication
* Add role-based authorization
* Add decision traces
* Add audit logging
* Protect administrative endpoints

### Phase 7 — Observability and Deployment

* Add application metrics
* Add distributed tracing
* Add dashboards
* Containerize services
* Add CI/CD pipelines
* Deploy the production beta

## 15. Validation Requirements

After every migration change, verify:

```text
python -m pytest -q
```

From `apps/web`:

```text
npm run lint
npm run build
```

Also verify:

* Existing API endpoints remain available.
* Existing response fields remain compatible.
* Existing frontend routes continue loading.
* Demo reset continues working.
* Readiness validation continues passing.
* Stable demo identifiers remain unchanged.

## 16. Definition of Migration Success

PlantMind Nexus v1 is successful when:

* Demo mode remains fully operational.
* Production mode uses PostgreSQL-backed repositories.
* Telemetry replay creates anomalies and incidents.
* Incidents connect to RCA and maintenance.
* Completed maintenance triggers verification.
* Verification updates asset health and compliance evidence.
* Decision traces record model and human actions.
* Automated tests protect existing behavior.
* The application is deployable using containers and CI/CD.
* The complete workflow can be demonstrated using `P-101`.
