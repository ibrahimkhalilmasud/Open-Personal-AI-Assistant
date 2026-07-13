# SECURITY

## Purpose
Security posture and operational guidance.

## Audience
Users, admins, and contributors.

## Prerequisites
Understand `.env`, API keys, and plugin trust boundaries.

## Step-by-step
1. Keep secrets in `.env`, never commit them.
2. Use API key auth for `/api/v1/*` endpoints.
3. Rotate API keys by generating a new one and deactivating old records.
4. Restrict CORS (`CORS_ALLOWED_ORIGINS`, `CORS_ALLOW_CREDENTIALS`).
5. Treat plugins as trusted code unless audited.

## Security implementation notes
- API keys are stored as PBKDF2-HMAC-SHA256 hashes using `OPA_API_KEY_HASH_PEPPER`.
- Public endpoints are limited to health/docs/root paths.
- Audit/metrics request records are persisted (`api_requests`, `api_audit_log`).

## Examples
```bash
curl -X POST http://127.0.0.1:8000/api/v1/system/api-keys -H "Content-Type: application/json" -d '{"name":"sdk"}'
```

## Troubleshooting
- 401: missing API key header.
- 403: invalid key or inactive key.

## Related documents
- [API_REFERENCE.md](API_REFERENCE.md)
- [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
