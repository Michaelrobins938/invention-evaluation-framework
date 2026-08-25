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
