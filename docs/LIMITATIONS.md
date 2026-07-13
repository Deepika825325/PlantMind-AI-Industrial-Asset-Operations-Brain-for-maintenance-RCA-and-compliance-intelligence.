# PlantMind Nexus Limitations

## Current Limitations

- Demo data is deterministic and not connected to a live plant.
- Model registry is MLflow-style metadata, not a full external MLflow server.
- Post-maintenance verification uses deterministic replay scenarios.
- Vector database and object storage require environment-specific deployment configuration.
- CI dependency scan is non-blocking to avoid false positives during demo development.
- Real deployment requires plant-specific cybersecurity, safety, and compliance review.

## Production Requirements

Before real plant use:

- Validate against real sensor data.
- Calibrate thresholds.
- Add human approval gates.
- Add role-specific authorization policies.
- Add audit log persistence.
- Add backup and restore procedures.
- Add production monitoring dashboards.
- Conduct security testing.
