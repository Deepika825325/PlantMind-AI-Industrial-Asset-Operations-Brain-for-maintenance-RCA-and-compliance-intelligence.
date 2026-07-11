# PlantMind API Contracts

API contract fixtures are stored in:

contracts/api/

The manifest file is:

contracts/api/manifest.json

Generate fixtures with:

python scripts/export_api_contracts.py

Each fixture records:

- HTTP method
- API path
- Status code
- Request ID
- Normalized response body

Purpose:

These fixtures protect PlantMind from accidental API response-shape regressions during the Nexus migration.
