# Current PlantMind State

PlantMind is stabilized through Day 10 closure work.

## Completed foundation

- JSON/demo repository mode remains available.
- PostgreSQL repository mode is implemented.
- Docker development stack is available.
- Deterministic database seed is available.
- Reset works in demo and database modes.
- Optional JWT authentication is available.
- Backend RBAC is available.
- Decision audit trail foundation is available.
- API contract fixtures are exported under contracts/api.

## Current branch

feature/nexus-foundation

## Baseline checks

Run these commands before Day 11:

python -m pytest tests/auth tests/audit -q
python -m pytest -q
docker compose --env-file .env.example config --quiet
python scripts/export_api_contracts.py
