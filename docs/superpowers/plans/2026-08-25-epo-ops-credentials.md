# EPO OPS Credential Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Feed EPO OPS consumer key/secret from a gitignored `.env` into the existing `engine_v17.epo_ops` client, fix the token request body, add a self-check CLI, tests, and docs.

**Architecture:** A stdlib-only `.env` loader (`config.py`) populates `os.environ` lazily before `EpoOpsAuth` reads its two credential variables (shell exports always win). `auth.py` sends a spec-compliant form-encoded token request and records failures in `last_error`. `__main__.py` provides a masked self-check that fetches a token and runs one biblio query via the existing `retrieve_citations()` path.

**Tech Stack:** Python 3.14 stdlib only (`pathlib`, `urllib`, `dataclasses`), pytest.

## Global Constraints

- Zero third-party dependencies added (stdlib only).
- Real credentials live ONLY in `.env` at repo root (gitignored at `.gitignore:16`). Never written to any tracked file, test, log, or stdout. The executor holds the actual key/secret values from the user conversation; they must NOT appear in this plan, commits, or test fixtures.
- Shell environment variables take precedence over `.env` values.
- Existing graceful-fallback behavior (unauthenticated mode) is preserved.
- No changes to orchestrator flow, cache behavior, or live_adapters.py.
- House style: pytest classes, absolute imports `from engine_v17.epo_ops...`, mocked HTTP in unit tests (no live calls).
- Commit steps assume the user approved committing; if not, leave work uncommitted and say so at the end.

---

### Task 1: `.env` loader — `config.py`

**Files:**
- Create: `engine_v17/epo_ops/config.py`
- Test: `engine_v17/epo_ops/tests/test_config.py`

**Interfaces:**
- Consumes: nothing (stdlib).
- Produces:
  - `load_env(path: str | Path | None = None) -> Path | None` — loads KEY=VALUE pairs into `os.environ` without overriding existing vars; returns loaded path or None.
  - `ensure_loaded() -> None` — auto-loads default `.env` once per process.
  - `_parse_env_line(line: str) -> tuple[str, str] | None`

- [ ] **Step 1: Write the failing tests**

Create `engine_v17/epo_ops/tests/test_config.py`:

```python
"""Tests for .env credential loading."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from engine_v17.epo_ops.config import _parse_env_line, load_env


class TestParseEnvLine:
    def test_basic_pair(self):
        assert _parse_env_line("KEY=value") == ("KEY", "value")

    def test_whitespace_and_quotes(self):
        assert _parse_env_line('  KEY = "quoted value" ') == ("KEY", "quoted value")
        assert _parse_env_line("KEY='single'") == ("KEY", "single")

    def test_comments_and_blanks(self):
        assert _parse_env_line("# comment") is None
        assert _parse_env_line("") is None
        assert _parse_env_line("   ") is None

    def test_malformed(self):
        assert _parse_env_line("NO_EQUALS_SIGN") is None
        assert _parse_env_line("=novalue") is None

    def test_hash_inside_value_kept(self):
        assert _parse_env_line("SECRET=a#b") == ("SECRET", "a#b")


class TestLoadEnv:
    def test_loads_pairs_from_file(self, tmp_path: Path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("EPO_TEST_A=1\n# c\nEPO_TEST_B='two words'\n", encoding="utf-8")
        monkeypatch.delenv("EPO_TEST_A", raising=False)
        monkeypatch.delenv("EPO_TEST_B", raising=False)
        loaded = load_env(env_file)
        assert loaded == env_file
        assert os.environ["EPO_TEST_A"] == "1"
        assert os.environ["EPO_TEST_B"] == "two words"

    def test_never_overrides_existing_env(self, tmp_path: Path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("EPO_TEST_C=file-value\n", encoding="utf-8")
        monkeypatch.setenv("EPO_TEST_C", "shell-value")
        load_env(env_file)
        assert os.environ["EPO_TEST_C"] == "shell-value"

    def test_missing_file_returns_none(self, tmp_path: Path):
        assert load_env(tmp_path / "absent.env") is None

    def test_malformed_lines_skipped(self, tmp_path: Path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "GOOD=1\nBAD LINE NO EQUALS\n\n# note\n=novalue\n", encoding="utf-8"
        )
        monkeypatch.delenv("GOOD", raising=False)
        assert load_env(env_file) == env_file
        assert os.environ["GOOD"] == "1"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest engine_v17/epo_ops/tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine_v17.epo_ops.config'`

- [ ] **Step 3: Write minimal implementation**

Create `engine_v17/epo_ops/config.py`:

```python
"""Local credential loading for EPO OPS — stdlib-only .env support."""

from __future__ import annotations

import os
from pathlib import Path

_MAX_WALK_UP = 6

_loaded = False


def _parse_env_line(line: str) -> tuple[str, str] | None:
    """Parse one KEY=VALUE line. Returns None for blanks, comments, malformed lines."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if "=" not in stripped:
        return None
    key, _, value = stripped.partition("=")
    key = key.strip()
    value = value.strip()
    if not key or not all(c.isalnum() or c == "_" for c in key):
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return key, value


def find_env_file() -> Path | None:
    """Locate a .env file: walk up from CWD (max 6 levels), then repo root."""
    cwd = Path.cwd()
    for candidate in [cwd, *list(cwd.parents)[:_MAX_WALK_UP]]:
        env_path = candidate / ".env"
        if env_path.is_file():
            return env_path
    repo_root = Path(__file__).resolve().parents[2]
    env_path = repo_root / ".env"
    return env_path if env_path.is_file() else None


def load_env(path: str | Path | None = None) -> Path | None:
    """Load KEY=VALUE pairs from a .env file into os.environ.

    Existing environment variables always win (never overridden).
    Returns the path of the file loaded, or None when nothing was loaded.
    """
    global _loaded
    env_path = Path(path) if path is not None else find_env_file()
    if env_path is None or not env_path.is_file():
        _loaded = True
        return None
    try:
        text = env_path.read_text(encoding="utf-8")
    except OSError:
        _loaded = True
        return None
    for line in text.splitlines():
        parsed = _parse_env_line(line)
        if parsed is None:
            continue
        key, value = parsed
        if key not in os.environ:
            os.environ[key] = value
    _loaded = True
    return env_path


def ensure_loaded() -> None:
    """Auto-load the default .env once per process."""
    if not _loaded:
        load_env()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest engine_v17/epo_ops/tests/test_config.py -v`
Expected: PASS (all)

- [ ] **Step 5: Commit**

```bash
git add engine_v17/epo_ops/config.py engine_v17/epo_ops/tests/test_config.py
git commit -m "feat(epo_ops): stdlib .env loader for OPS credentials"
```

---

### Task 2: Auth fix — form-encoded token request + `last_error`

**Files:**
- Modify: `engine_v17/epo_ops/auth.py`
- Test: `engine_v17/epo_ops/tests/test_auth.py` (new)

**Interfaces:**
- Consumes: `engine_v17.epo_ops.config.ensure_loaded` (Task 1).
- Produces:
  - `EpoOpsAuth.last_error: str | None` (new attribute, set on token-refresh failure, cleared on success).
  - Token request: POST with `Authorization: Basic base64(client_id:client_secret)`, `Content-Type: application/x-www-form-urlencoded`, body `grant_type=client_credentials`.
  - Module-level `_env(name: str) -> str` used by field defaults.

- [ ] **Step 1: Write the failing tests**

Create `engine_v17/epo_ops/tests/test_auth.py`:

```python
"""Tests for EPO OPS authentication (mocked HTTP only)."""

from __future__ import annotations

import base64
import io
import json
from urllib.parse import parse_qs

import pytest

import engine_v17.epo_ops.auth as auth_module
from engine_v17.epo_ops.auth import EpoOpsAuth


class _FakeResponse:
    def __init__(self, payload: dict):
        self._body = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def read(self, *args, **kwargs):
        return self._body.read()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


@pytest.fixture
def captured():
    requests = []

    def fake_urlopen(request, timeout=None):
        requests.append(request)
        return _FakeResponse({"access_token": "tok-123", "expires_in": 3600})

    return requests, fake_urlopen


class TestDefaults:
    def test_defaults_read_environment(self, monkeypatch):
        monkeypatch.setenv("EPO_OPS_CLIENT_ID", "env-key")
        monkeypatch.setenv("EPO_OPS_CLIENT_SECRET", "env-secret")
        auth = EpoOpsAuth()
        assert auth.client_id == "env-key"
        assert auth.client_secret == "env-secret"
        assert auth.is_authenticated


class TestTokenRequestShape:
    def test_request_is_form_encoded_with_basic_header(self, monkeypatch, captured):
        requests, fake_urlopen = captured
        monkeypatch.setattr(auth_module, "urlopen", fake_urlopen)
        auth = EpoOpsAuth(client_id="key", client_secret="secret")

        token = auth.get_token()

        assert token == "tok-123"
        request = requests[0]
        expected_basic = "Basic " + base64.b64encode(b"key:secret").decode("ascii")
        assert request.headers["Authorization"] == expected_basic
        assert request.headers.get("Content-type") == "application/x-www-form-urlencoded"
        body = parse_qs(request.data.decode("ascii"))
        assert body == {"grant_type": ["client_credentials"]}
        assert auth.last_error is None

    def test_token_cached_within_expiry(self, monkeypatch, captured):
        requests, fake_urlopen = captured
        monkeypatch.setattr(auth_module, "urlopen", fake_urlopen)
        auth = EpoOpsAuth(client_id="key", client_secret="secret")

        assert auth.get_token() == "tok-123"
        assert auth.get_token() == "tok-123"
        assert len(requests) == 1


class TestErrorPath:
    def test_failure_sets_last_error(self, monkeypatch):
        def failing_urlopen(request, timeout=None):
            raise OSError("network down")

        monkeypatch.setattr(auth_module, "urlopen", failing_urlopen)
        auth = EpoOpsAuth(client_id="key", client_secret="secret")

        assert auth.get_token() is None
        assert auth.last_error is not None
        assert "OSError" in auth.last_error

    def test_unauthenticated_returns_none_without_request(self, monkeypatch, captured):
        requests, fake_urlopen = captured
        monkeypatch.setattr(auth_module, "urlopen", fake_urlopen)
        auth = EpoOpsAuth(client_id="", client_secret="")

        assert auth.get_token() is None
        assert requests == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest engine_v17/epo_ops/tests/test_auth.py -v`
Expected: FAIL — `test_request_is_form_encoded_with_basic_header` fails on body assertion (current code sends JSON bytes); `TestDefaults.test_defaults_read_environment` may pass already.

- [ ] **Step 3: Implement**

Rewrite `engine_v17/epo_ops/auth.py`:

```python
"""EPO OPS authentication — OAuth2 client-credentials flow."""

from __future__ import annotations

import base64
import json
import os
import time
from dataclasses import dataclass, field
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def _env(name: str) -> str:
    from .config import ensure_loaded

    ensure_loaded()
    return os.environ.get(name, "")


@dataclass
class EpoOpsAuth:
    """
    Manages EPO OPS authentication tokens.

    EPO OPS uses OAuth2 client-credentials. Credentials are read from
    environment variables (never hardcoded), optionally populated from a
    local `.env` file by engine_v17.epo_ops.config:

        EPO_OPS_CLIENT_ID     consumer key from developers.epo.org
        EPO_OPS_CLIENT_SECRET consumer secret

    Tokens are cached in memory and refreshed before expiry.
    """
    client_id: str = field(default_factory=lambda: _env("EPO_OPS_CLIENT_ID"))
    client_secret: str = field(default_factory=lambda: _env("EPO_OPS_CLIENT_SECRET"))
    token_url: str = "https://ops.epo.org/3.2/auth/accesstoken"
    _token: str | None = field(default=None, repr=False)
    _token_expires_at: float = field(default=0.0, repr=False)
    last_error: str | None = field(default=None, repr=False)

    @property
    def is_authenticated(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def get_token(self, force_refresh: bool = False) -> str | None:
        """
        Return a valid access token, refreshing if necessary.

        Returns None if credentials are not configured (unauthenticated mode).
        """
        if not self.is_authenticated:
            return None

        now = time.time()
        if not force_refresh and self._token and now < self._token_expires_at - 30:
            return self._token

        return self._refresh_token()

    def _refresh_token(self) -> str | None:
        """Request a new token from EPO OPS."""
        payload = urlencode({"grant_type": "client_credentials"}).encode("utf-8")

        request = Request(
            self.token_url,
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": self._basic_auth_header(),
            },
        )

        try:
            with urlopen(request, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
                self._token = body.get("access_token")
                expires_in = body.get("expires_in", 3600)
                self._token_expires_at = time.time() + int(expires_in)
                self.last_error = None
                return self._token
        except Exception as exc:
            # Token refresh failed — preserve fallback semantics, record cause.
            self.last_error = f"{type(exc).__name__}: {exc}"
            return None

    def _basic_auth_header(self) -> str:
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"

    def invalidate(self) -> None:
        """Force token refresh on next get_token() call."""
        self._token = None
        self._token_expires_at = 0.0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest engine_v17/epo_ops/tests/test_auth.py engine_v17/epo_ops/tests/test_config.py -v`
Expected: PASS (all)

- [ ] **Step 5: Commit**

```bash
git add engine_v17/epo_ops/auth.py engine_v17/epo_ops/tests/test_auth.py
git commit -m "fix(epo_ops): spec-compliant token request, capture last_error, .env-aware defaults"
```

---

### Task 3: Self-check CLI — `__main__.py`

**Files:**
- Create: `engine_v17/epo_ops/__main__.py`
- Test: `engine_v17/epo_ops/tests/test_selfcheck.py` (new)

**Interfaces:**
- Consumes: `ensure_loaded` (Task 1), `EpoOpsClient` + `EpoOpsAuth.last_error` (Task 2), `retrieve_citations` (existing `citations.py`).
- Produces:
  - `mask(value: str | None) -> str` — first 6 chars + `…`, `(missing)` when empty.
  - `main(argv: list[str] | None = None) -> int` — exit code 0 on success, 1 on failure.

- [ ] **Step 1: Write the failing tests**

Create `engine_v17/epo_ops/tests/test_selfcheck.py`:

```python
"""Tests for the EPO OPS self-check CLI (no network)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from engine_v17.epo_ops.__main__ import main, mask


class TestMask:
    def test_masks_long_secret(self):
        result = mask("d7vZq3KYqUAmVGYQfQCyEVTSkumSBvnDjDCYTuROAUBzQeXt")
        assert result == "d7vZq3…"
        assert len(result) < 10

    def test_missing_values(self):
        assert mask(None) == "(missing)"
        assert mask("") == "(missing)"

    def test_short_value_fully_masked(self):
        assert mask("abc") == "…"


def _no_autoload(monkeypatch):
    monkeypatch.setattr("engine_v17.epo_ops.__main__.ensure_loaded", lambda: None)


class TestMain:
    def test_missing_credentials_exits_nonzero(self, monkeypatch, capsys):
        _no_autoload(monkeypatch)
        monkeypatch.delenv("EPO_OPS_CLIENT_ID", raising=False)
        monkeypatch.delenv("EPO_OPS_CLIENT_SECRET", raising=False)

        rc = main([])
        out = capsys.readouterr().out

        assert rc == 1
        assert "FAIL" in out
        assert "developers.epo.org" in out

    def test_token_failure_reports_last_error(self, monkeypatch, capsys):
        _no_autoload(monkeypatch)
        stub_auth = SimpleNamespace(
            client_id="stub-key",
            client_secret="stub-secret",
            is_authenticated=True,
            get_token=lambda force_refresh=False: None,
            last_error="OSError: network down",
        )
        stub_client = SimpleNamespace(auth=stub_auth)
        monkeypatch.setattr(
            "engine_v17.epo_ops.__main__.EpoOpsClient", lambda: stub_client
        )

        rc = main([])
        out = capsys.readouterr().out

        assert rc == 1
        assert "network down" in out

    def test_success_path_masks_secrets_and_passes(self, monkeypatch, capsys):
        _no_autoload(monkeypatch)
        stub_auth = SimpleNamespace(
            client_id="stub-key-123456",
            client_secret="stub-secret-654321",
            is_authenticated=True,
            get_token=lambda force_refresh=False: "tok",
            last_error=None,
        )
        bundle = SimpleNamespace(
            patcit=["p1"], nplcit=[], retrieval_metadata={"http_status": 200}
        )
        stub_client = SimpleNamespace(
            auth=stub_auth,
            get=lambda path, **kw: {
                "status": 200,
                "data": "<xml/>" * 25,
                "cached": False,
            },
        )
        monkeypatch.setattr(
            "engine_v17.epo_ops.__main__.EpoOpsClient", lambda: stub_client
        )
        monkeypatch.setattr(
            "engine_v17.epo_ops.__main__.retrieve_citations",
            lambda patent_id, client, use_cache=True: bundle,
        )

        rc = main(["US5215088"])
        out = capsys.readouterr().out

        assert rc == 0
        assert "PASS" in out
        assert "stub-secret" not in out
        assert "d7vZq3" not in out
```

Note: the `"d7vZq3"` assertion guards against real credentials ever leaking through `mask()` output ordering; it passes because no real creds are configured in this hermetic test.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest engine_v17/epo_ops/tests/test_selfcheck.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine_v17.epo_ops.__main__'`

- [ ] **Step 3: Implement**

Create `engine_v17/epo_ops/__main__.py`:

```python
"""Self-check CLI for EPO OPS connectivity.

Usage:
    python -m engine_v17.epo_ops [PUBLICATION_NUMBER]

Loads credentials (.env or shell environment), fetches an access token,
runs one biblio query, and prints a masked report. Exit code 0 on success.
Secrets are never printed in full.
"""

from __future__ import annotations

import sys

from .citations import retrieve_citations
from .client import EpoOpsClient
from .config import ensure_loaded

DEFAULT_PUBLICATION = "US5215088"


def mask(value: str | None) -> str:
    """Mask a secret for display: first 6 chars plus ellipsis."""
    if not value:
        return "(missing)"
    if len(value) <= 6:
        return "…"
    return value[:6] + "…"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    publication = args[0].upper() if args else DEFAULT_PUBLICATION

    ensure_loaded()
    client = EpoOpsClient()
    auth = client.auth

    print("EPO OPS self-check")
    print(f"  consumer key:     {mask(auth.client_id)}")
    print(f"  consumer secret:  {mask(auth.client_secret)}")

    if not auth.is_authenticated:
        print(
            "FAIL: no credentials found.\n"
            "  Create a .env at the repository root (see .env.example) with\n"
            "  EPO_OPS_CLIENT_ID and EPO_OPS_CLIENT_SECRET from https://developers.epo.org"
        )
        return 1

    token = auth.get_token()
    if not token:
        print(f"FAIL: token request failed ({auth.last_error})")
        return 1
    print("  access token:     acquired OK")

    bundle = retrieve_citations(publication, client, use_cache=True)
    metadata = bundle.retrieval_metadata
    if metadata.get("http_status") != 200:
        print(
            f"FAIL: biblio query for {publication} returned status "
            f"{metadata.get('http_status')}: {metadata.get('error', '')}"
        )
        return 1

    citations = metadata.get("patcit_count", 0) + metadata.get("nplcit_count", 0)
    cached = "cached" if metadata.get("cached") else "live"
    print(f"  biblio query:     {publication} OK ({cached}, {citations} citations)")
    print("PASS: EPO OPS credentials are working.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest engine_v17/epo_ops/tests -v`
Expected: PASS (all — parser, models, config, auth, selfcheck)

- [ ] **Step 5: Commit**

```bash
git add engine_v17/epo_ops/__main__.py engine_v17/epo_ops/tests/test_selfcheck.py
git commit -m "feat(epo_ops): masked self-check CLI (python -m engine_v17.epo_ops)"
```

---

### Task 4: `.env.example`, real `.env`, README, end-to-end verification

**Files:**
- Create: `.env.example` (committed template, placeholders only)
- Create: `.env` (real credentials — NEVER committed; verify ignored first)
- Modify: `README.md` (insert subsection after Known Limitations table, before the following `---`)

**Interfaces:**
- Consumes: everything above.
- Produces: working documented setup; acceptance criteria from spec met.

- [ ] **Step 1: Verify `.env` is ignored BEFORE writing secrets**

Run: `git check-ignore -v .env`
Expected: matches rule `.env` from `.gitignore`. If it does NOT match, STOP and fix `.gitignore` first.

- [ ] **Step 2: Write `.env.example` (tracked)**

```
# EPO Open Patent Services credentials — https://developers.epo.org
# Copy this file to .env and fill in your consumer key / consumer secret.
# .env is gitignored and never committed.
EPO_OPS_CLIENT_ID=your-consumer-key-here
EPO_OPS_CLIENT_SECRET=your-consumer-secret-here
```

- [ ] **Step 3: Write real `.env` (untracked)**

Executor writes `.env` at repo root using the exact consumer key and consumer secret supplied by the user in conversation (do NOT copy them into any other file, the plan, or commit messages):

```
EPO_OPS_CLIENT_ID=<consumer key from user>
EPO_OPS_CLIENT_SECRET=<consumer secret from user>
```

- [ ] **Step 4: Confirm git status is clean of `.env`**

Run: `git status --porcelain`
Expected: `.env` does NOT appear; `.env.example` does.

- [ ] **Step 5: README documentation**

In `README.md`, immediately after the Known Limitations table row ending `(hermetic \`hermetic_fetcher.py\` covers testing) |` and before the next `\n---\n`, insert:

```markdown

### Configure EPO OPS credentials

Live patent searches use the EPO Open Patent Services API. Register at
[developers.epo.org](https://developers.epo.org), then store your consumer
key/secret locally (never committed):

    cp .env.example .env   # then paste your key/secret into .env
    python -m engine_v17.epo_ops          # self-check: token + live biblio query

`.env` is gitignored; credentials never appear in logs, reports, or git history.
Shell-exported `EPO_OPS_CLIENT_ID` / `EPO_OPS_CLIENT_SECRET` override `.env`.
```

(Use an indented code block as shown, matching README's existing style.)

- [ ] **Step 6: Full regression run**

Run: `python3 -m pytest engine_v17/epo_ops/tests tests -q`
Expected: PASS, no regressions.

- [ ] **Step 7: Live self-check (acceptance criterion 1)**

Run: `python3 -m engine_v17.epo_ops US5215088`
Expected output ends with `PASS: EPO OPS credentials are working.` and shows masked keys only. If EPO returns 403/rate-limit errors, record the exact status and report to user — credentials may still need EPO-side activation (new accounts sometimes lag).

- [ ] **Step 8: Commit**

```bash
git add .env.example README.md
git commit -m "docs: EPO OPS credential setup (.env.example + README guide)"
```

---

## Self-Review Notes

- Spec coverage: loader (Task 1), auth fix + last_error (Task 2), self-check CLI (Task 3), .env.example + README + real .env + live verification (Task 4). Acceptance criteria map: AC1→Task 4 Step 7, AC2→Task 3 Step 1 + Task 4 Step 6, AC3→test_config precedence test, AC4→masked output tests + Task 4 Steps 1/4.
- No placeholders: all code shown verbatim; real secret values intentionally excluded from this tracked plan and held only in conversation → `.env`.
- Type consistency: `last_error` set/cleared in Task 2, consumed in Task 3; `retrieval_metadata` keys (`http_status`, `patcit_count`, `nplcit_count`, `cached`) match existing `citations.py:72-89`.
