"""Tests for EPO OPS client configuration."""

from __future__ import annotations

from engine_v17.epo_ops.client import EpoOpsClient


class TestBaseUrl:
    def test_default_base_url_includes_rest_services(self):
        """OPS v3.2 data endpoints live under /3.2/rest-services (ops.yaml basePath)."""
        client = EpoOpsClient()
        assert client.base_url == "https://ops.epo.org/3.2/rest-services"

    def test_env_overrides_base_url(self, monkeypatch):
        monkeypatch.setenv("EPO_OPS_BASE_URL", "https://example.test/ops")
        client = EpoOpsClient()
        assert client.base_url == "https://example.test/ops"

    def test_url_builder_joins_path(self):
        client = EpoOpsClient(base_url="https://ops.epo.org/3.2/rest-services")
        url = client._url("/published-data/publication/epodoc/US5215088A/biblio")
        assert url == (
            "https://ops.epo.org/3.2/rest-services"
            "/published-data/publication/epodoc/US5215088A/biblio"
        )
