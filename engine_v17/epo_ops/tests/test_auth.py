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
