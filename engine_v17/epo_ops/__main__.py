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
