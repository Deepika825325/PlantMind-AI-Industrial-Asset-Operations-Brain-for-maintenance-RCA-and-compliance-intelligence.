# PlantMind Nexus Migration Notes

## Migration principle

PlantMind Nexus must keep the demo stable while progressively adding production features.

## Protected invariants

- Demo mode must continue to run without PostgreSQL.
- API response shapes must remain stable unless intentionally versioned.
- P-101 RCA relationships must remain intact.
- Reset must be deterministic.
- RBAC must protect actions, not only pages.
- Critical decisions must be auditable.
- Request IDs must be propagated into logs and audit records.

## Completed phases

1. Baseline protection
2. Repository abstraction
3. Docker development stack
4. PostgreSQL foundation
5. Operational repository migration
6. Deterministic seed
7. Production-compatible reset
8. Optional authentication
9. Role-based access control
10. Decision audit trail foundation

## Next phase

Day 11 will start production document ingestion.
