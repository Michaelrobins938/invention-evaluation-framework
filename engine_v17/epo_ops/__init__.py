"""EPO OPS integration module for the Invention Evaluation Framework.

Provides structured access to EPO Open Patent Services for:
- Patent citation retrieval (patcit + nplcit)
- NPL/XP document resolution via citing-patent strategy
- Layered acquisition with provenance tracking

Usage:
    from engine_v17.epo_ops import EpoOpsClient, retrieve_citations, build_npl_evidence_records

    client = EpoOpsClient()
    bundle = retrieve_citations("US5215088", client)
    records = build_npl_evidence_records("XP000123456", client)

Environment variables:
    EPO_OPS_CLIENT_ID: OAuth2 client ID (optional — unauthenticated mode available)
    EPO_OPS_CLIENT_SECRET: OAuth2 client secret
    EPO_OPS_CACHE_DIR: Response cache directory (default: .epo_ops_cache)
    EPO_OPS_BASE_URL: API base URL (default: https://ops.epo.org/3.2)
"""

from .auth import EpoOpsAuth
from .client import EpoOpsClient
from .citations import retrieve_citations, retrieve_npl_citations
from .models import (
    CitationBundle,
    CitationCategory,
    CitedBy,
    CitedPhase,
    EvidenceStatus,
    MetadataCompleteness,
    NplCitation,
    NplEvidenceRecord,
    PatentCitation,
)
from .npl import (
    XpResolutionResult,
    build_npl_evidence_records,
    resolve_xp_via_citing_patents,
)
from .parser import parse_bibliographic_xml, parse_search_xml

__all__ = [
    # Client
    "EpoOpsClient",
    "EpoOpsAuth",
    # Citation retrieval
    "retrieve_citations",
    "retrieve_npl_citations",
    "retrieve_citations_for_patent",
    # NPL resolution
    "build_npl_evidence_records",
    "resolve_xp_via_citing_patents",
    # Parsers
    "parse_bibliographic_xml",
    "parse_search_xml",
    # Models
    "CitationBundle",
    "CitationCategory",
    "CitedBy",
    "CitedPhase",
    "EvidenceStatus",
    "MetadataCompleteness",
    "NplCitation",
    "NplEvidenceRecord",
    "PatentCitation",
    "XpResolutionResult",
]