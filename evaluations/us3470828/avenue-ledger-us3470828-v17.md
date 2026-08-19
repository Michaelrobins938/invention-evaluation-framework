# Avenue Ledger — US 3,470,828

## Run metadata

- Run ID: us3470828-v17
- Submission: `submission-us3470828.md`
- Primary source: https://patents.google.com/patent/US3470828A/en
- Date of run: 2026-08-16
- Evidence rule: search completion is not evidence; unresolved propositions remain in the work queue.

## Proposition ledger

| Proposition ID | Version | Proposition | State | Evidence state |
|---|---:|---|---|---|
| P-02-001 | 1 | US3470828A identity, inventors, filing date, publication date, and claim count | ESTABLISHED | CONFIRMED PRESENT |
| P-03-001 | 1 | Technical architecture disclosed by the patent | ESTABLISHED | CONFIRMED PRESENT |
| P-03-002 | 1 | Independent experimental proof of performance | ESCALATION_REQUIRED | WORK QUEUE |
| P-04-001 | 1 | Broad pre-filing patent landscape | ESCALATION_REQUIRED | WORK QUEUE |
| P-05-001 | 1 | Claim 1 anticipation | ESCALATION_REQUIRED | WORK QUEUE |
| P-05-002 | 1 | Obviousness bridge and motivation | ESCALATION_REQUIRED | WORK QUEUE |
| P-06-001 | 1 | Independent literature disclosure before 1967-11-21 | ESCALATION_REQUIRED | WORK QUEUE |
| P-07-001 | 1 | Quantified market size and growth | ESCALATION_REQUIRED | WORK QUEUE |
| P-07-002 | 1 | Commercial adoption and readiness | ESCALATION_REQUIRED | WORK QUEUE |
| P-08-001 | 1 | Organization-specific partner fit | ESCALATION_REQUIRED | WORK QUEUE |

## Recovery records

### FR-04-001 — Patent landscape

- Initial failure: no complete family-deduplicated landscape count established from the supplied PDF.
- Diagnosis: terminology, classification, and historical database coverage may differ.
- Troubleshooting: primary patent record classification and citation sections consulted; Google Patents historical search behavior used as the initial retrieval route.
- Strategies executed:
  - R1 terminology: electromagnetic inductive suspension / magnetic levitation / electrodynamic suspension; Google Patents; relevant records US1020943A and US3125964A.
  - R2 classification: B60L13/04, B61B13/08, Y10S505/903; Google Patents; classification records returned.
  - R3 citation lineage: target patent cited references and cited-by records; Google Patents; US1020943A and US3125964A linked.
  - R4 alternate source: USPTO, Espacenet, PatentCenter links identified but not fully retrieved in this run; avenue remains incomplete.
  - R5 entity/jurisdiction: US application and inventor identity captured; family/foreign ownership remains incomplete.
- Assessment: additional avenues remain; state remains `ESCALATION_REQUIRED`.

### FR-05-001 — Claim 1 anticipation

- Initial failure: two retrieved historical patents were related but did not map every claim limitation.
- Diagnosis: related magnetic suspension terminology does not establish the target superconducting passive-loop combination.
- Troubleshooting: expanded terms and classification terms using the primary record; reviewed cited references and claims of US1020943A and US3125964A.
- Strategies executed:
  - R1 terminology expansion: levitating transmitting apparatus, magnetic road, magnetic suspension, electrodynamic suspension.
  - R2 classification traversal: B61B13/08 and B60L13/04.
  - R3 citation lineage: target patent citations and cited-by trail.
  - R4 alternate source: Google Patents full-text and claim pages for US1020943A and US3125964A.
  - R5 temporal/entity: pre-1967 US records and named inventor/reference tracing.
- Assessment: claim mapping remains incomplete; no anticipation finding admitted.

### FR-06-001 — Literature

- Initial failure: cited ASME and *Physica* references were named in the patent but full independent records were not retrieved.
- Diagnosis: citation identity and archival accessibility require separate recovery.
- Troubleshooting: exact titles, authors, venues, dates, and report numbers extracted from the target patent for archive searches.
- Strategies executed:
  - R1 exact-title search for Powell 1963 paper.
  - R2 exact-title search for Van Beelen 1965 paper.
  - R3 exact-report search for ASME 66-WA/RR-5.
  - R4 citation expansion from the target patent and related patent pages.
  - R5 historical terminology search for magnetic road, superconductive transport, and electrodynamic suspension.
- Assessment: independent literature evidence remains unestablished.

### FR-07-001 — Market

- Initial failure: no reconstructable market-size dataset was supplied or retrieved.
- Diagnosis: historical invention market boundary is not the same as a current maglev revenue category.
- Troubleshooting: separated historical technology disclosure from modern market claims and identified the necessary infrastructure, cryogenic, and regulatory proxies.
- Strategies executed:
  - R1 market-boundary reconstruction.
  - R2 transportation-infrastructure proxy search.
  - R3 superconducting-magnet supplier/industry proxy search.
  - R4 regulatory and public-procurement route.
  - R5 commercialization/adoption history route.
- Assessment: no quantitative finding admitted; market proposition remains `ESCALATION_REQUIRED`.

### FR-08-001 — Partners

- Initial failure: no organization-specific fit record with sell/buy/need/mapping fields was established.
- Diagnosis: candidate categories can be identified, but current organization-specific relevance and rights dependencies remain unverified.
- Troubleshooting: separated consortium categories from named partner recommendations.
- Strategies executed:
  - R1 system integrator category.
  - R2 superconducting/cryogenic supplier category.
  - R3 infrastructure contractor category.
  - R4 public transportation research category.
  - R5 university/research collaboration category.
- Assessment: no partner-fit finding admitted.
