# Frontend Route Smoke Test List

These routes must load without crashing in demo mode.

| Route | Purpose |
|---|---|
| `/` | Executive dashboard |
| `/ask` | Ask PlantMind |
| `/assets` | Asset registry |
| `/compliance` | Compliance dashboard |
| `/maintenance` | Maintenance command center |
| `/rca` | RCA command center |
| `/documents` | Document intelligence |
| `/knowledge-graph` | Knowledge graph |
| `/pid` | P&ID viewer |
| `/rbac` | Frontend RBAC action visibility |

## Smoke acceptance

- Page loads
- No unhandled frontend error
- Backend unavailable states render cleanly
- Navigation remains visible
- Demo mode banner remains visible