# PlantMind Nexus Deployment Guide

## Deployment Scope

PlantMind Nexus production deployment includes:

- Frontend
- Backend API
- PostgreSQL
- Redis
- Qdrant
- Object storage
- Background worker
- MLflow-style model registry
- Observability metrics endpoint

## Required Services

| Service | Purpose |
|---|---|
| Frontend | User interface |
| Backend API | PlantMind intelligence APIs |
| PostgreSQL | Persistent relational storage |
| Redis | Queue and cache layer |
| Qdrant | Vector retrieval store |
| Object storage | Documents, artifacts, and reports |
| Worker | Ingestion, extraction, replay, and evaluation jobs |
| Metrics endpoint | Prometheus-compatible monitoring |

## Required Environment Variables

Use environment variables or a secret manager. Do not commit secrets.

- DATABASE_URL
- REDIS_URL
- QDRANT_URL
- OBJECT_STORAGE_ENDPOINT
- OBJECT_STORAGE_BUCKET
- JWT_SECRET_KEY
- PLANTMIND_ALLOWED_ORIGINS
- PLANTMIND_MAX_UPLOAD_BYTES
- PLANTMIND_RATE_LIMIT_PER_MINUTE
- PLANTMIND_JWT_EXPIRY_MINUTES
- PLANTMIND_PRODUCTION_ANOMALY_MODEL_VERSION

## Production-Style Validation

Run:

    docker compose --env-file .env.example config --quiet
    docker compose --env-file .env.example build

## Health Checks

- GET /observability/health
- GET /metrics
- GET /mlops/model-registry/overview
- GET /compliance/audit-packages/assets/P-101

## Final Deployment Checklist

- Backend starts successfully
- Frontend build succeeds
- Database migrations run
- Seed data loads
- Login works
- P-101 replay works
- Anomaly detected
- Incident created
- RCA updated
- Work order completed
- Recovery verified
- Audit package updated
- Evaluation report available
