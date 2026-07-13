# PlantMind Nexus Security Guide

## Security Controls

PlantMind Nexus includes:

- Environment-based secrets policy
- No committed local environment files
- Rate limiting policy
- Upload-size limits
- Restricted CORS policy
- JWT expiry policy
- Input validation through FastAPI and Pydantic
- Admin-route protection
- Security headers
- Dependency scan in CI
- Secret scan in CI

## Security Endpoint

- GET /admin/security-review

This endpoint requires admin authorization.

## Security Headers

- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Permissions-Policy

## CI Security Checks

- Gitleaks secret scan
- Dependency audit
- Local environment file exclusion check
- Admin-route protection tests
