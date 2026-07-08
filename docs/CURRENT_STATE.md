# PlantMind Current State

**Baseline date:** July 8, 2026
**Baseline version:** PlantMind v0.2 Demo Stable
**Git branch:** `main`
**Baseline commit:** `d57fd39`
**Commit description:** `Normalize Day 5 test file ending`

## Repository Status

* Local branch is synchronized with `origin/main`.
* Git working tree was clean before baseline documentation.
* Existing application functionality is preserved.
* JSON-based deterministic demo mode is operational.

## Backend Validation

Command:

```bash
python -m pytest -q
```

Result:

* 18 tests passed.
* 1 non-blocking Starlette deprecation warning.
* Test execution time: 4.12 seconds.

Known warning:

```text
StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.
```

The warning does not currently affect application functionality or test results.

## Frontend Validation

Application:

* Next.js 16.2.9
* React
* TypeScript
* Tailwind CSS

Production build command:

```bash
npm run build
```

Result:

* Production compilation passed.
* TypeScript validation passed.
* Page-data collection passed.
* Static-page generation passed.
* Page optimization passed.

Lint command:

```bash
npm run lint
```

Result:

* ESLint passed.
* No lint errors reported.
* No lint warnings reported.

## Verified Frontend Routes

* `/`
* `/ask`
* `/assets`
* `/assets/[assetId]`
* `/compliance`
* `/documents`
* `/documents/[documentId]`
* `/knowledge-graph`
* `/maintenance`
* `/pid`
* `/rca`

The internal Next.js `/_not-found` route was also generated successfully.

## Current Core Capabilities

* Operations dashboard
* Asset 360
* Structured root-cause analysis
* Maintenance work-order management
* Compliance intelligence
* Evidence traceability
* Document intelligence pages
* Knowledge-graph visualization
* P&ID viewer
* Ask PlantMind interface
* Centralized error handling
* Readiness validation
* Demo-data reset
* Cache reload
* Shared frontend loading, empty and error states

## Stable Demo Entities

The following identifiers must remain backward compatible during the PlantMind Nexus migration:

### Assets

* `P-101`
* `C-201`
* `HX-301`

### RCA case

* `RCA-P101-001`

### Evidence

* `P101-EV-001`
* `P101-EV-002`
* `P101-EV-003`
* `P101-EV-004`

Existing work-order IDs, document IDs and compliance-rule IDs must also be preserved.

## Migration Principle

PlantMind Nexus will be implemented as an additive evolution of the existing application.

The existing application will remain functional as deterministic demo mode while production repositories, databases, telemetry, machine learning, authentication, observability and deployment capabilities are introduced incrementally.

The target workflow is:

```text
Detect → Contextualise → Explain → Act → Verify → Learn
```

Existing routes, API contracts and stable domain identifiers must not be broken without an explicit versioned migration.
