# SECURITY

- Never commit secrets.
- Use `.env` for keys.
- Report vulnerabilities via private security advisory.
- API keys are stored as PBKDF2-HMAC-SHA256 hashes using `OPA_API_KEY_HASH_PEPPER`.
- CORS defaults are restricted to localhost origins and credentials are disabled by default.
- Plugin sandbox policy limits permissions but is not a true process-level sandbox; plugins execute Python code in-process.
