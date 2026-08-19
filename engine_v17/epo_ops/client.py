"""Base HTTP client for EPO OPS with authentication and caching."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .auth import EpoOpsAuth
from .cache import EpoOpsCache


Fetcher = Callable[[str], bytes]


@dataclass
class EpoOpsClient:
    """
    HTTP client for EPO OPS (Open Patent Services) API.

    Handles:
    - OAuth2 authentication (client-credentials flow)
    - Request signing with Bearer tokens
    - Rate-limit awareness
    - File-based response caching
    - Error handling with structured error records

    Environment variables:
        EPO_OPS_CLIENT_ID: OAuth2 client ID
        EPO_OPS_CLIENT_SECRET: OAuth2 client secret
        EPO_OPS_CACHE_DIR: Cache directory (default: .epo_ops_cache)
        EPO_OPS_BASE_URL: API base URL (default: https://ops.epo.org/3.2)
    """
    base_url: str = field(default_factory=lambda: os.environ.get("EPO_OPS_BASE_URL", "https://ops.epo.org/3.2"))
    auth: EpoOpsAuth = field(default_factory=EpoOpsAuth)
    cache: EpoOpsCache = field(default_factory=EpoOpsCache)
    fetcher: Fetcher | None = field(default=None, repr=False)
    _rate_limit_remaining: int = field(default=0, repr=False)
    _rate_limit_reset: float = field(default=0.0, repr=False)

    def __post_init__(self) -> None:
        if self.fetcher is None:
            self.fetcher = _default_fetcher

    def _url(self, path: str, params: dict[str, Any] | None = None) -> str:
        """Build a full API URL with optional query parameters."""
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        return url

    def _headers(self, accept: str = "application/xml") -> dict[str, str]:
        """Build request headers with authentication."""
        headers: dict[str, str] = {
            "Accept": accept,
            "User-Agent": "invention-evaluation-engine/1.7",
        }
        token = self.auth.get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _respect_rate_limit(self) -> None:
        """Sleep if we're approaching the rate limit."""
        if self._rate_limit_remaining <= 1 and time.time() < self._rate_limit_reset:
            sleep_time = self._rate_limit_reset - time.time() + 1
            if sleep_time > 0:
                time.sleep(min(sleep_time, 5))

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        accept: str = "application/xml",
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Perform a GET request and return parsed JSON response.

        Returns a dict with:
            - "data": parsed response body
            - "status": HTTP status code
            - "cached": whether result came from cache
            - "error": error description if status != 200
        """
        url = self._url(path, params)
        cache_key_params = {"path": path, "params": params}

        # Check cache first
        if use_cache:
            cached = self.cache.get(url, cache_key_params)
            if cached is not None:
                return {**cached, "cached": True}

        self._respect_rate_limit()

        try:
            body = self.fetcher(url, self._headers(accept))
            response = body.decode("utf-8", errors="replace")

            result: dict[str, Any] = {
                "data": response,
                "status": 200,
                "cached": False,
                "url": url,
            }

            # Cache successful responses
            if use_cache:
                self.cache.put(url, result, cache_key_params)

            return result

        except HTTPError as exc:
            return {
                "data": exc.read().decode("utf-8", errors="replace") if exc.fp else "",
                "status": exc.code,
                "cached": False,
                "error": str(exc),
                "url": url,
            }
        except (URLError, OSError) as exc:
            return {
                "data": "",
                "status": 0,
                "cached": False,
                "error": str(exc),
                "url": url,
            }

    def get_bytes(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """Perform a GET request returning raw bytes (for PDF/images)."""
        url = self._url(path, params)
        cache_key_params = {"path": path, "params": params}

        if use_cache:
            cached = self.cache.get(url, cache_key_params)
            if cached is not None:
                return {**cached, "cached": True}

        self._respect_rate_limit()

        try:
            body = self.fetcher(url, self._headers(accept="*/*"))
            import base64
            result: dict[str, Any] = {
                "data": base64.b64encode(body).decode("ascii"),
                "status": 200,
                "cached": False,
                "url": url,
                "encoding": "base64",
            }
            if use_cache:
                self.cache.put(url, result, cache_key_params)
            return result
        except HTTPError as exc:
            return {
                "data": exc.read().decode("utf-8", errors="replace") if exc.fp else "",
                "status": exc.code,
                "cached": False,
                "error": str(exc),
                "url": url,
            }
        except (URLError, OSError) as exc:
            return {
                "data": "",
                "status": 0,
                "cached": False,
                "error": str(exc),
                "url": url,
            }


def _default_fetcher(url: str, headers: dict[str, str]) -> bytes:
    """Default HTTP fetcher using urllib."""
    request = Request(url, headers=headers)
    with urlopen(request, timeout=60) as response:
        return response.read()