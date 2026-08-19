"""EPO OPS authentication — OAuth2 client-credentials flow."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.request import Request, urlopen


@dataclass
class EpoOpsAuth:
    """
    Manages EPO OPS authentication tokens.

    EPO OPS uses OAuth2 client-credentials. Credentials are read from
    environment variables (never hardcoded):

        EPO_OPS_CLIENT_ID
        EPO_OPS_CLIENT_SECRET

    Tokens are cached in memory and refreshed before expiry.
    """
    client_id: str = field(default_factory=lambda: os.environ.get("EPO_OPS_CLIENT_ID", ""))
    client_secret: str = field(default_factory=lambda: os.environ.get("EPO_OPS_CLIENT_SECRET", ""))
    token_url: str = "https://ops.epo.org/3.2/auth/accesstoken"
    _token: str | None = field(default=None, repr=False)
    _token_expires_at: float = field(default=0.0, repr=False)

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
        payload = json.dumps({
            "grant_type": "client_credentials",
        }).encode("utf-8")

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
                return self._token
        except Exception as exc:
            # Token refresh failed — return None to signal unauthenticated fallback
            return None

    def _basic_auth_header(self) -> str:
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"

    def invalidate(self) -> None:
        """Force token refresh on next get_token() call."""
        self._token = None
        self._token_expires_at = 0.0