# PlantMind API Contracts

**Baseline version:** `v0.2.0`
**Baseline date:** July 8, 2026
**OpenAPI snapshot:** `docs/contracts/openapi-v0.2.json`
**Documented OpenAPI paths:** 45

## Purpose

This document defines the API behavior that must remain backward compatible while PlantMind evolves into PlantMind Nexus.

Internal implementations may migrate from JSON files to repository interfaces, PostgreSQL, TimescaleDB, Qdrant or background workers.

Existing endpoint paths and response structures must not be changed unintentionally.

## System Endpoints

| Method | Endpoint              | Purpose                                      |
| ------ | --------------------- | -------------------------------------------- |
| GET    | `/`                   | API information and service links            |
| GET    | `/health`             | Basic liveness check                         |
| GET    | `/ready`              | Data and service readiness validation        |
| GET    | `/status/files`       | Demo-file inventory and validation status    |
| POST   | `/admin/reload-cache` | Clear data cache and revalidate source files |
| POST   | `/admin/reset-demo`   | Restore deterministic demo state             |

The internal `/admin/test-error` endpoint is excluded from the public OpenAPI schema and is intended only for structured-error testing.

## Dashboard Endpoints

| Method | Endpoint                        |
| ------ | ------------------------------- |
| GET    | `/dashboard/summary`            |
| GET    | `/dashboard/overview`           |
| GET    | `/dashboard/operations-summary` |

## Asset Endpoints

| Method | Endpoint                      |
| ------ | ----------------------------- |
| GET    | `/assets`                     |
| GET    | `/assets/health-scores`       |
| GET    | `/assets/{asset_id}`          |
| GET    | `/assets/{asset_id}/health`   |
| GET    | `/assets/{asset_id}/evidence` |

## Ask PlantMind Endpoints

| Method | Endpoint                   |
| ------ | -------------------------- |
| POST   | `/ask`                     |
| GET    | `/ask/search`              |
| GET    | `/ask/suggested-questions` |

## Document Endpoints

| Method | Endpoint                          |
| ------ | --------------------------------- |
| GET    | `/documents`                      |
| GET    | `/documents/{document_id}`        |
| GET    | `/documents/{document_id}/chunks` |

## Knowledge Graph Endpoints

| Method | Endpoint                                      |
| ------ | --------------------------------------------- |
| GET    | `/knowledge-graph`                            |
| GET    | `/knowledge-graph/nodes`                      |
| GET    | `/knowledge-graph/edges`                      |
| GET    | `/knowledge-graph/assets/{asset_id}/subgraph` |

## Maintenance Endpoints

| Method | Endpoint                                     |
| ------ | -------------------------------------------- |
| GET    | `/maintenance/events`                        |
| GET    | `/maintenance/events/{event_id}`             |
| GET    | `/maintenance/work-orders`                   |
| GET    | `/maintenance/work-orders/statistics`        |
| GET    | `/maintenance/work-orders/{work_order_id}`   |
| GET    | `/maintenance/assets/{asset_id}/work-orders` |
| GET    | `/maintenance/rca/{case_id}/work-orders`     |
| GET    | `/maintenance/recommendations`               |

## Compliance Endpoints

| Method | Endpoint                                      |
| ------ | --------------------------------------------- |
| GET    | `/compliance`                                 |
| GET    | `/compliance/overview`                        |
| GET    | `/compliance/rules`                           |
| GET    | `/compliance/gaps`                            |
| GET    | `/compliance/assets/{asset_id}`               |
| GET    | `/compliance/assets/{asset_id}/audit-package` |

## RCA Endpoints

| Method | Endpoint                                |
| ------ | --------------------------------------- |
| GET    | `/rca`                                  |
| GET    | `/rca/statistics`                       |
| GET    | `/rca/asset/{asset_id}`                 |
| GET    | `/rca/{case_id}`                        |
| GET    | `/rca/{case_id}/evidence/{evidence_id}` |

## P&ID Endpoints

| Method | Endpoint              |
| ------ | --------------------- |
| GET    | `/pid/{pid_id}`       |
| GET    | `/pid/{pid_id}/image` |

## Compatibility Rules

During the Nexus migration:

1. Existing endpoint paths must remain available.
2. Existing HTTP methods must not change.
3. Existing required parameters must not become optional without review.
4. Existing optional parameters must not become required.
5. Existing response fields must not be removed or renamed.
6. New response fields should be additive.
7. Stable asset, RCA, evidence, work-order, document and compliance identifiers must be preserved.
8. Error responses must continue using the centralized structured-error format.
9. Demo mode must continue supporting deterministic API responses.
10. Any intentional breaking change requires a versioned endpoint or explicit migration plan.

## Contract Validation Strategy

The generated OpenAPI file is the machine-readable baseline:

```text
docs/contracts/openapi-v0.2.json
```

Future API changes should be compared against this file before merging.

Recommended future validation:

```text
Current OpenAPI schema
        ↓
Compare against v0.2 baseline
        ↓
Detect removed paths, methods, parameters or response fields
        ↓
Fail CI when an unapproved breaking change is found
```

## Migration Boundary

Routes and services may remain stable while their storage implementation changes:

```text
Route
  ↓
Service
  ↓
Repository interface
  ├── JSON repository
  └── PostgreSQL repository
```

This repository boundary is the primary mechanism for protecting the API contracts during the PlantMind Nexus migration.
