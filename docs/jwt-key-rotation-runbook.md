# JWT Key Rotation Runbook

This API signs access tokens with RS256 and publishes verification keys at `/.well-known/jwks.json`.

The JWKS endpoint is auth-gated in production, so operational checks there must include a valid bearer token.

## One-time Key Generation

Generate a new RSA keypair:

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out jwt-private.pem
openssl rsa -pubout -in jwt-private.pem -out jwt-public.pem
```

## Active Key Configuration

Set these variables for the active signing key:

- `JWT_ACTIVE_KID=<new-key-id>`
- `JWT_ACTIVE_PRIVATE_KEY=<PEM private key>`
- `JWT_ACTIVE_PUBLIC_KEY=<PEM public key>`

Set issuer and audience:

- `JWT_ISSUER`
- `JWT_AUDIENCE`

## Rotation Procedure

1. Generate new keypair and choose new `kid`.
2. Keep current public key in `JWT_ADDITIONAL_PUBLIC_KEYS` while switching active key.
3. Deploy with new active key.
4. Verify `/.well-known/jwks.json` contains both old and new `kid`.
5. Wait for old access tokens to expire.
6. Remove old key from `JWT_ADDITIONAL_PUBLIC_KEYS`.

`JWT_ADDITIONAL_PUBLIC_KEYS` format (JSON object):

```json
{
  "old-kid-1": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
}
```

## Optional Legacy HS256 Transition

If migrating from older HS256 tokens, set a short cutoff:

- `JWT_ACCEPT_LEGACY_HS256_UNTIL=2026-04-01T00:00:00Z`

After cutoff passes, remove this variable.

## Verification Example

```powershell
curl.exe -H "Authorization: Bearer <admin-or-test-token>" http://127.0.0.1:8000/.well-known/jwks.json
```
