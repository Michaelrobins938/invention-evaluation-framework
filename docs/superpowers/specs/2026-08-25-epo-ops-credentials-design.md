# Design: EPO OPS Credential Integration (.env)

**Date:** 2026-08-25
**Status:** Approved
**Goal:** Feed the user's new EPO OPS consumer key/secret (from developers.epo.org) into the existing `engine_v17.epo_ops` client conveniently and safely.

## Background

`engine_v17/epo_ops/` already implements the full OPS client (OAuth2 client-credentials auth, HTTP client, cache, parsers, citation/NPL retrieval). It reads `EPO_OPS_CLIENT_ID` / `EPO_OPS_CLIENT_SECRET` from environment variables. Missing pieces:

1. Nothing loads a `.env` file (`.gitignore:16` already excludes `.env`, `.env.*`).
2. `EpoOpsAuth._refresh_token()` sends a JSON body labeled `application/x-www-form-urlencoded` — non-compliant with the real OPS token endpoint.
3. No way to verify credentials work before running a full evaluation.
4. No setup documentation for live credentials.

## Components

### 1. Env-file loader — `engine_v17/epo_ops/config.py` (new)

- `load_env(path: str | None = None) -> Path | None`
  - Default search: walk up from CWD looking for `.env`, capped at 6 parent levels; fallback to repo root derived from the module location (`engine_v17/`'s parent).
  - Parses flat `KEY=VALUE` lines; ignores blank lines, `#` comments, surrounding single/double quotes; skips malformed lines without raising.
  - **Never overrides variables already set in the shell** (real env wins).
  - Idempotent via module-level loaded flag; safe to call repeatedly.
- Invoked lazily from `EpoOpsAuth` field defaults before `os.environ.get(...)`.
- Stdlib only (`pathlib`, no third-party deps).

### 2. Auth fix — `engine_v17/epo_ops/auth.py`

- `_refresh_token()`: send proper urlencoded body `grant_type=client_credentials` with matching `Content-Type: application/x-www-form-urlencoded` header; Basic auth header unchanged (`base64(key:secret)`).
- Add `last_error: str | None` attribute capturing token-refresh failures (previously swallowed), so diagnostics can distinguish bad credentials from network errors. Existing graceful fallback (return `None` → unauthenticated mode) is preserved.

### 3. Self-check CLI — `engine_v17/epo_ops/__main__.py` (new)

- Invocation: `python -m engine_v17.epo_ops [PUBLICATION_NUMBER]`
- Behavior:
  1. Load `.env`, report which credential vars are found — values masked (first 6 chars + ellipsis).
  2. Fetch an access token; print OK + expiry seconds, or the captured `last_error`.
  3. Run one biblio query (`/published-data/publication/epodoc/<num>/biblio`) against the given publication number (default: `US5215088`).
  4. Print result summary; exit code 0 on success, non-zero on failure.
- Secrets and tokens are never printed in full.

### 4. Template — `.env.example` (new, committed)

```
# EPO Open Patent Services credentials — https://developers.epo.org
# Copy to .env and fill in your consumer key / consumer secret.
EPO_OPS_CLIENT_ID=your-consumer-key-here
EPO_OPS_CLIENT_SECRET=your-consumer-secret-here
```

The user's real `.env` stays untracked (already gitignored).

### 5. Tests

- `engine_v17/epo_ops/tests/test_config.py` (new): parsing cases (quotes, comments, blanks, malformed), precedence (existing env not overridden), idempotency.
- `engine_v17/epo_ops/tests/test_auth.py` (new): token request shape via mocked urlopen (urlencoded body, Basic header), token caching/expiry window, error path sets `last_error`.
- Mocked HTTP only; no live calls in unit tests.

### 6. Documentation — `README.md`

New "Configure EPO OPS credentials" subsection near the existing live-use note:
copy `.env.example` → `.env`, paste key/secret, run the self-check command. Note that `.env` is gitignored and keys never leave the machine except to EPO.

## Error handling

- Malformed `.env` lines are skipped silently; loader never raises on file content issues.
- Token failure keeps the current fallback semantics (client proceeds unauthenticated); `last_error` surfaces cause for the self-check.
- Live adapters' try/except fallback around EPO OPS usage is unchanged.

## Out of scope

- python-dotenv or any third-party dependency.
- Changes to orchestrator flow, caching behavior, or skill instructions.
- Storing secrets anywhere other than local `.env` / environment.

## Acceptance criteria

1. With a valid `.env`, `python -m engine_v17.epo_ops` fetches a token and returns live biblio data (exit 0).
2. Without credentials, self-check reports what's missing and exits non-zero; unit tests all pass hermetically.
3. Shell-exported variables take precedence over `.env` values.
4. No secret material appears in logs, test output, or git history.
