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
