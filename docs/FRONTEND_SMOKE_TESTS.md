# PlantMind Frontend Smoke-Test Checklist

**Baseline version:** PlantMind `v0.2.0` Demo Stable
**Baseline date:** July 8, 2026
**Frontend:** Next.js 16.2.9

## Purpose

This checklist records the frontend routes and essential behaviors that must remain operational throughout the PlantMind Nexus migration.

Run this checklist before major refactoring, before tagging a release and before merging changes that affect routing, shared components, API clients or application state.

## Test Environment

Record the environment used for each execution:

* Git commit:
* Branch:
* Frontend URL:
* Backend URL:
* Browser:
* Test date:
* Tester:

## Global Application Checks

Verify the following on every major page:

* The page loads without an unhandled application error.
* The browser console contains no unexpected errors.
* The main navigation is visible.
* Navigation links open the correct pages.
* Loading states render correctly.
* Empty states render correctly where applicable.
* API error states are readable and do not break the page.
* Page layout remains usable at desktop width.
* No broken images or missing static assets are visible.
* Refreshing the browser does not break the route.

## Route Checklist

### Operations Dashboard — `/`

Verify:

* Dashboard loads successfully.
* Operations summary cards are visible.
* Asset information is displayed.
* Maintenance information is displayed.
* Compliance information is displayed.
* RCA information is displayed.
* Dashboard links navigate to the relevant modules.

Status: Not yet manually verified for baseline capture.

### Asset List — `/assets`

Verify:

* Asset list loads successfully.
* `P-101` is displayed.
* `C-201` is displayed.
* `HX-301` is displayed.
* Asset health information is displayed.
* Selecting an asset opens its Asset 360 page.

Status: Not yet manually verified for baseline capture.

### Asset 360 — `/assets/P-101`

Verify:

* The `P-101` detail page loads successfully.
* Asset identity and metadata are displayed.
* Health information is displayed.
* Evidence information is accessible.
* Related maintenance, RCA or compliance links work.
* Existing stable identifiers remain unchanged.

Status: Not yet manually verified for baseline capture.

### Documents — `/documents`

Verify:

* Document list loads successfully.
* Document metadata is displayed.
* Selecting a document opens the document detail route.
* Empty, loading and error states remain functional.

Status: Not yet manually verified for baseline capture.

### Document Detail — `/documents/[documentId]`

Verify using a valid existing document ID:

* Document detail page loads.
* Document metadata is displayed.
* Extracted content or chunks are visible.
* Related assets or evidence are displayed where applicable.
* Invalid document IDs show a controlled error or not-found state.

Status: Not yet manually verified for baseline capture.

### Ask PlantMind — `/ask`

Verify:

* Ask PlantMind page loads successfully.
* Suggested questions are displayed.
* A valid question can be submitted.
* The answer renders without breaking the page.
* Evidence or source references are displayed when available.
* Invalid or failed requests show a controlled error state.

Status: Not yet manually verified for baseline capture.

### Knowledge Graph — `/knowledge-graph`

Verify:

* Knowledge graph page loads successfully.
* Nodes are displayed.
* Edges are displayed.
* Asset relationships are visible.
* Graph interactions do not trigger browser errors.

Status: Not yet manually verified for baseline capture.

### Maintenance — `/maintenance`

Verify:

* Maintenance page loads successfully.
* Work-order list is displayed.
* Work-order statistics are displayed.
* Recommendations are visible.
* Existing work-order IDs remain unchanged.
* Work-order details can be inspected.

Status: Not yet manually verified for baseline capture.

### Compliance — `/compliance`

Verify:

* Compliance page loads successfully.
* Compliance overview is displayed.
* Rules are displayed.
* Gaps are displayed.
* Asset compliance information can be accessed.
* Audit-package information is available where implemented.

Status: Not yet manually verified for baseline capture.

### Root Cause Analysis — `/rca`

Verify:

* RCA page loads successfully.
* `RCA-P101-001` is displayed.
* Probable causes are displayed.
* Evidence records are displayed.
* `P101-EV-001` through `P101-EV-004` remain available.
* Evidence details can be opened without errors.

Status: Not yet manually verified for baseline capture.

### P&ID Viewer — `/pid`

Verify:

* P&ID page loads successfully.
* The diagram or image is displayed.
* Asset references are visible.
* P&ID interactions work without browser errors.
* Missing-image handling does not break the page.

Status: Not yet manually verified for baseline capture.

## Dynamic Route Validation

Use at least one known valid ID for every dynamic route:

| Route                     | Baseline test value                                 |
| ------------------------- | --------------------------------------------------- |
| `/assets/[assetId]`       | `/assets/P-101`                                     |
| `/documents/[documentId]` | Record the existing document ID used during testing |

The document ID must be copied from the current demo dataset rather than invented.

## Production Build Baseline

Command:

```text
npm run build
```

Baseline result:

* Compilation passed.
* TypeScript validation passed.
* Page-data collection passed.
* Static-page generation passed.
* Page optimization passed.
* All expected frontend routes were generated.

## Lint Baseline

Command:

```text
npm run lint
```

Baseline result:

* ESLint passed.
* No lint errors were reported.
* No lint warnings were reported.

## Completion Requirement

The baseline smoke test is complete when:

* Every listed route has been opened manually.
* Each route status is changed from `Not yet manually verified` to `Passed`.
* The valid document ID used for testing is recorded.
* Major-page screenshots are stored under `docs/screenshots/v0.2/`.
* Any known visual or functional limitation is documented.
* No existing route is silently removed during the Nexus migration.
