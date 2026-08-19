"""File-based cache for EPO OPS responses."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any


class EpoOpsCache:
    """
    Simple file-based cache for EPO OPS API responses.

    Caches are stored under a configurable directory (default: .epo_ops_cache/)
    and keyed by a hash of the URL + relevant parameters. Entries expire
    after a configurable TTL (default: 24 hours).
    """

    def __init__(self, cache_dir: str | Path | None = None, ttl_seconds: int = 86400):
        self.cache_dir = Path(cache_dir or os.environ.get("EPO_OPS_CACHE_DIR", ".epo_ops_cache"))
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, url: str, params: dict[str, Any] | None = None) -> str:
        """Generate a cache key from URL and optional parameters."""
        raw = url + "|" + json.dumps(params or {}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _path(self, key: str, suffix: str = ".json") -> Path:
        return self.cache_dir / f"{key}{suffix}"

    def get(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Retrieve a cached response if fresh, otherwise None."""
        key = self._key(url, params)
        path = self._path(key)

        if not path.exists():
            return None

        try:
            mtime = path.stat().st_mtime
            if time.time() - mtime > self.ttl_seconds:
                path.unlink(missing_ok=True)
                return None

            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            path.unlink(missing_ok=True)
            return None

    def put(self, url: str, data: dict[str, Any], params: dict[str, Any] | None = None) -> None:
        """Write a response to the cache."""
        key = self._key(url, params)
        path = self._path(key)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except OSError:
            pass  # Cache write failure is non-fatal

    def clear(self) -> None:
        """Remove all cached entries."""
        for path in self.cache_dir.glob("*.json"):
            path.unlink(missing_ok=True)

    def stats(self) -> dict[str, Any]:
        """Return cache statistics."""
        entries = list(self.cache_dir.glob("*.json"))
        total_size = sum(p.stat().st_size for p in entries if p.exists())
        return {
            "cache_dir": str(self.cache_dir),
            "entry_count": len(entries),
            "total_size_bytes": total_size,
            "ttl_seconds": self.ttl_seconds,
        }