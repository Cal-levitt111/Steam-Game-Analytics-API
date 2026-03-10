# Production Security Checklist

Use this checklist before deploying the application.

In production, the runtime is default-private: all backend routes except register/login require auth, the frontend redirects unauthenticated users to `/auth`, and interactive runtime docs are disabled.

## Required Runtime Settings

- `ENVIRONMENT=production`
- `FORCE_HTTPS=true`
- `ALLOWED_HOSTS=<public-hostnames>`
- `SECRET_KEY=<non-placeholder secret>`
- `JWT_ACTIVE_KID=<current signing key id>`
- `JWT_ACTIVE_PRIVATE_KEY=<PEM private key or escaped \\n form>`
- `JWT_ACTIVE_PUBLIC_KEY=<PEM public key or escaped \\n form>`

The app now fails startup in production if `FORCE_HTTPS`, `ALLOWED_HOSTS`, `SECRET_KEY`, `JWT_ACTIVE_PRIVATE_KEY`, or `JWT_ACTIVE_PUBLIC_KEY` are missing or unsafe.

## Deployment Checks

- Terminate TLS at the reverse proxy or load balancer.
- Forward `X-Forwarded-Proto` only from trusted proxy CIDRs.
- Keep `ENABLE_MCP_SERVER=false` unless MCP exposure is explicitly required.
- Confirm only `POST /api/v1/auth/register` and `POST /api/v1/auth/login` remain public.
- Confirm hosted runtime docs are not exposed; generate and host API docs separately if needed.
- Keep `ACCESS_TOKEN_EXPIRE_MINUTES` short. The example default is `30`.

## Operational Checks

- Rotate JWT signing keys on a fixed cadence and keep the previous public key in `JWT_ADDITIONAL_PUBLIC_KEYS` during overlap.
- Remove `JWT_ACCEPT_LEGACY_HS256_UNTIL` after migration windows expire.
- Review auth rate-limit thresholds for your real traffic profile.
- Verify frontend session cookies are marked `Secure` in production.
- Verify `/.well-known/jwks.json` and `/api/v1/health` are only reachable with auth.
- Run the CI security checks (`bandit`, `pip-audit`, `gitleaks`) on each pull request.
