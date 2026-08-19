# Avenue Ledger — US 5,850,650 (Combination Hammer and Lumber Manipulating Tool) v1.6 Run

**Framework version:** v1.6 (Evidence Sufficiency Architecture)
**Submission:** `evaluations/us5850650/submission-us5850650.md`
**Run date:** 2026-08-14
**Ledger purpose:** Every search avenue opened during the run, with priority, disposition (COMPLETE / BLOCKED / NOT_APPLICABLE / REQUIRES_VERIFICATION), and audit entry. This ledger is the evidence for Validation Matrix criteria 2 (escalation loop), 3 (state-level placement), and 10 (hard stopping rule).

**Avenue statuses (v1.6):**
- `COMPLETE` — the avenue was executed and produced its result (positive or negative record).
- `BLOCKED` — the avenue could not be executed (access, availability, or technical failure); logged with reason and alternate routes attempted.
- `NOT_APPLICABLE` — the avenue does not apply to this proposition; requires `rule_id` + `rule_basis`.
- `REQUIRES_VERIFICATION` — the avenue produced a result that cannot be independently verified; **never** a terminal disposition for a proposition.

**Hard stopping rule:** a proposition may be dispositioned `EXHAUSTED` only when every required avenue is `COMPLETE`, `BLOCKED`, or `NOT_APPLICABLE` — and none is `REQUIRES_VERIFICATION`. `EXHAUSTED ≠ CONFIRMED ABSENT`.

**Source-availability note:** This is a 1997 invention with a 1998 grant and a 20-year term that expired 2017-06-13. No inventor interview is possible (sample patent from a law-firm public page; no inventor contact). Several avenue rows are BLOCKED on the same underlying access constraint — trade-journal full text (Fine Homebuilding archive, trade press) — which is logged per ladder per the v1.6 invariant (every BLOCKED disposition logs the reason and alternate routes attempted).

---

## A-02-004 — "No public disclosure of the invention before filing" (P-02-004)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source (submission record, inventor statement) | 1 | COMPLETE | Submission states "Public disclosure date: None recorded" — a search-based absence, not an inventor statement. First public availability of the invention occurred post-filing: CA A1 open-to-inspection 1998-12-13, US grant publication 1998-12-22. |
| A2 classification (IPC/CPC) | 2 | NOT_APPLICABLE | rule_id: NA-02-004-1; rule_basis: disclosure history is not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | Backward citations of US5850650 checked; no pre-filing disclosure. |
| A4 terminology_expansion | 4 | COMPLETE | Hammer/jaw/claw/lumber terminology variants searched; no pre-filing disclosure. |
| A5 alternate_database | 5 | BLOCKED | No inventor personal records or interview transcripts accessible; alternate routes attempted: law-firm page, patent assignee records — all logged. |
| A6 organizational_records | 6 | NOT_APPLICABLE | rule_id: NA-02-004-2; rule_basis: inventor assigned to "Individual"; no organization maintained disclosure records. |
| A7 jurisdiction_specific | 7 | COMPLETE | USPTO/Google Patents records checked; earliest public availability is post-filing (CA A1 1998-12-13; US grant 1998-12-22). |
| A8 independent_corroboration | 8 | BLOCKED | No second independent source for a negative disclosure history; corroboration of absence impossible. |

**Proposition disposition:** EXHAUSTED → EXCLUDED (search-based absence is avenue metadata, not evidence).

---

## A-03-003 — "No quantitative performance data exists" (P-03-003)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | No performance comparison source located (no weight delta, strike-character, or manipulation-force measurement). |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-03-003-1; rule_basis: performance data is not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | No performance data in cited sources. |
| A4 terminology_expansion | 4 | COMPLETE | Efficiency/leverage/weight terminology searched; no data. |
| A5 alternate_database | 5 | BLOCKED | Trade-journal full-text (Fine Homebuilding archive, tool-review press) not accessible; alternate routes attempted: Taunton Press store, Archive.org, Google Books — all logged. |
| A6 organizational_records | 6 | NOT_APPLICABLE | rule_id: NA-03-003-2; rule_basis: no test records exist for this invention (individual inventor, no lab). |
| A7 jurisdiction_specific | 7 | NOT_APPLICABLE | rule_id: NA-03-003-3; rule_basis: performance data is not jurisdiction-specific. |
| A8 independent_corroboration | 8 | BLOCKED | No second source for a negative performance-data claim. |

**Proposition disposition:** EXHAUSTED → EXCLUDED (`barrier_type: insufficient_technical_demonstration`).

---

## A-03-004 — "No mandatory product-design regulation governs hand hammers" (P-03-004b; positive OSHA finding P-03-004a established separately)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | OSHA 29 CFR 1910.242 identified as the governing general workplace hand-tool rule (positive finding P-03-004a established); no mandatory product-design standard identified for hand hammers. |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-03-004-1; rule_basis: regulatory regime is not classification-dependent. |
| A3 citation_expansion | 3 | NOT_APPLICABLE | rule_id: NA-03-004-2; rule_basis: no mandatory standard to expand citations from. |
| A4 terminology_expansion | 4 | COMPLETE | Safety/standards/CPSC terminology searched; no mandatory product standard. |
| A5 alternate_database | 5 | BLOCKED | CPSC mandatory-standards universe (16 CFR product lists) not fully accessible in this environment; alternate routes attempted: CPSC reginfo.gov, eCFR — partially accessible, no hammer-specific mandatory standard identified. |
| A6 organizational_records | 6 | NOT_APPLICABLE | rule_id: NA-03-004-3; rule_basis: no standards-body product-dossier records for hand hammers located. |
| A7 jurisdiction_specific | 7 | COMPLETE | US federal regulation search (OSHA 29 CFR 1910.242 found; no CPSC mandatory hammer standard identified). |
| A8 independent_corroboration | 8 | BLOCKED | No second independent source for a negative mandatory-standard claim. |

**Proposition disposition:** EXHAUSTED → EXCLUDED (`barrier_type: insufficient_search_completion`). The absence of a mandatory product-design regime is a negative claim requiring a bounded universe of mandatory standards; not established. The positive OSHA general-duty finding (P-03-004a) stands as ESTABLISHED and supports the LOW regulatory-burden estimate.

---

## A-03-005 — Prototype evidence (P-03-005)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | No prototype/test records located. |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-03-005-1; rule_basis: not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | No prototype records in cited sources. |
| A4 terminology_expansion | 4 | COMPLETE | No prototype records under expanded terminology. |
| A5 alternate_database | 5 | BLOCKED | Trade-journal full-text unavailable (as A-02-004 A5). |
| A6 organizational_records | 6 | BLOCKED | Inventor personal/prototype records not accessible; alternate routes attempted and logged. |
| A7 jurisdiction_specific | 7 | NOT_APPLICABLE | rule_id: NA-03-005-2; rule_basis: not jurisdiction-specific. |
| A8 independent_corroboration | 8 | BLOCKED | No second source for negative prototype claims. |

**Proposition disposition:** EXHAUSTED → EXCLUDED (search-based absence; avenue metadata only).

---

## A-03-006 — Production evidence (P-03-006)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | No production records located. |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-03-006-1; rule_basis: not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | No production records in cited sources. |
| A4 terminology_expansion | 4 | COMPLETE | No production records under expanded terminology. |
| A5 alternate_database | 5 | BLOCKED | Trade-journal full-text unavailable (as A-02-004 A5). |
| A6 organizational_records | 6 | BLOCKED | No manufacturer/production records identified for the fixed-jaw hammer; alternate routes attempted and logged. |
| A7 jurisdiction_specific | 7 | NOT_APPLICABLE | rule_id: NA-03-006-2; rule_basis: not jurisdiction-specific. |
| A8 independent_corroboration | 8 | BLOCKED | No second source for negative production claims. |

**Proposition disposition:** EXHAUSTED → EXCLUDED (search-based absence; avenue metadata only).

---

## A-04-002 — "No international family members beyond US + CA" (P-04-002; positive US+CA family record P-02-005 established)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | Google Patents Country Status: "US (1) + CA (1)" — single source. |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-04-002-1; rule_basis: family membership is not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | Backward citations checked for foreign equivalents; none beyond CA2240576C. |
| A4 terminology_expansion | 4 | NOT_APPLICABLE | rule_id: NA-04-002-2; rule_basis: family membership is not terminology-dependent. |
| A5 alternate_database | 5 | BLOCKED | Espacenet 403 error (prior runs); alternate routes attempted: EPO register via web, patent family databases — all blocked/unavailable. |
| A6 organizational_records | 6 | NOT_APPLICABLE | rule_id: NA-04-002-3; rule_basis: no organization records for family membership. |
| A7 jurisdiction_specific | 7 | COMPLETE | USPTO record checked; no foreign equivalents beyond CA2240576C. |
| A8 independent_corroboration | 8 | BLOCKED | No second independent source for family absence (Espacenet blocked). |

**Proposition disposition:** EXHAUSTED → EXCLUDED (`barrier_type: insufficient_corroboration`). Single-source family record cannot support CONFIRMED ABSENT. The positive family record (US + CA) is established; the negative "no other jurisdictions" is not.

---

## A-05-008 — Knowledge decomposition: combination_known / application_known (P-05-008)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | No pre-filing source shows the fixed-jaw hammer combination (hammer with claw + fixed lumber-gripping jaw) or its application. |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-05-008-1; rule_basis: knowledge decomposition is not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | No combination/application in cited sources (US513271A, US1469472A, US4762303A, US5255575A, US5787676A all checked). |
| A4 terminology_expansion | 4 | COMPLETE | No combination/application under expanded terminology. |
| A5 alternate_database | 5 | BLOCKED | Trade-journal full-text unavailable (as A-02-004 A5). |
| A6 organizational_records | 6 | NOT_APPLICABLE | rule_id: NA-05-008-2; rule_basis: no organization records for knowledge state. |
| A7 jurisdiction_specific | 7 | NOT_APPLICABLE | rule_id: NA-05-008-3; rule_basis: knowledge state is not jurisdiction-specific. |
| A8 independent_corroboration | 8 | BLOCKED | No second source for negative knowledge-state claims. |

**Proposition disposition:** EXHAUSTED → EXCLUDED (combination_known, application_known not established; avenue records only).

---

## A-05-009 — Motivation proposition (P-05-009)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | No direct pre-filing source motivating the fixed-jaw hammer implementation. |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-05-009-1; rule_basis: motivation is not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | Analogous sources identified: US4762303A (lumber grip), US1469472A (jaw on hammer head), US513271A (jaw on hammer), Maggard 711,408 (sliding-jaw hammer, per spec). |
| A4 terminology_expansion | 4 | COMPLETE | No direct motivation under expanded terminology. |
| A5 alternate_database | 5 | BLOCKED | Trade-journal full-text unavailable (as A-02-004 A5). |
| A6 organizational_records | 6 | NOT_APPLICABLE | rule_id: NA-05-009-2; rule_basis: no organization records for motivation. |
| A7 jurisdiction_specific | 7 | NOT_APPLICABLE | rule_id: NA-05-009-3; rule_basis: motivation is not jurisdiction-specific. |
| A8 independent_corroboration | 8 | BLOCKED | No second source for a direct motivation claim. |

**Proposition disposition:** EXHAUSTED → EXCLUDED. Motivation object: direct = none; analogous = US4762303A, US1469472A, US513271A, Maggard 711,408; inferred = general knowledge of the twisted-lumber problem (Fine Homebuilding practice articles, pre- and post-filing); contradicted = none → **PARTIALLY GROUNDED (analogous only)**. Per the deterministic derivation table, PARTIALLY GROUNDED is not GROUNDED; the motivation proposition is not established.

---

## A-05-010 — Obviousness proposition (P-05-010)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | No pre-filing source showing the combination as obvious. |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-05-010-1; rule_basis: obviousness is not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | Analogous sources reviewed (as A-05-009 A3). |
| A4 terminology_expansion | 4 | COMPLETE | No obviousness evidence under expanded terminology. |
| A5 alternate_database | 5 | BLOCKED | Trade-journal full-text unavailable (as A-02-004 A5). |
| A6 organizational_records | 6 | NOT_APPLICABLE | rule_id: NA-05-010-2; rule_basis: no organization records for obviousness. |
| A7 jurisdiction_specific | 7 | NOT_APPLICABLE | rule_id: NA-05-010-3; rule_basis: obviousness is not jurisdiction-specific. |
| A8 independent_corroboration | 8 | BLOCKED | No second source for an obviousness claim. |

**Proposition disposition:** EXHAUSTED → EXCLUDED. Obviousness requires (1) GROUNDED motivation, (2) reasonable expectation of success, (3) C/D assessment, (4) Causal Bridge Test. Motivation is PARTIALLY GROUNDED (not GROUNDED); application NOT ESTABLISHED; bridge_work_state = EXHAUSTED. Per GLOSSARY: obviousness is not assessed as a conclusion — excluded from factual findings, recorded in the Operational Audit with `barrier_type: insufficient_search_completion`.

---

## A-05-011 — Unexpected-result proposition (P-05-011)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | No performance comparison data located. |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-05-011-1; rule_basis: not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | No data in cited sources. |
| A4 terminology_expansion | 4 | COMPLETE | No data under expanded terminology. |
| A5 alternate_database | 5 | BLOCKED | Trade-journal full-text unavailable (as A-02-004 A5). |
| A6 organizational_records | 6 | NOT_APPLICABLE | rule_id: NA-05-011-2; rule_basis: no test records exist. |
| A7 jurisdiction_specific | 7 | NOT_APPLICABLE | rule_id: NA-05-011-3; rule_basis: not jurisdiction-specific. |
| A8 independent_corroboration | 8 | BLOCKED | No second source for a negative performance claim. |

**Proposition disposition:** EXHAUSTED → EXCLUDED (`barrier_type: insufficient_technical_demonstration`).

---

## A-06-005 — "No pre-filing non-patent publication discloses the fixed-jaw hammer combination" (P-06-005)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | Web literature search; no pre-filing disclosure of the fixed-jaw hammer combination. Background practice literature identified (Fine Homebuilding 1991-11-01, 1999-07-01, 2000-09-01; Audel's 1923) — none discloses a jaw fixed to a hammer head opposing the claw. |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-06-005-1; rule_basis: literature disclosure is not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | Citation chains of identified literature checked; no combination disclosure. |
| A4 terminology_expansion | 4 | COMPLETE | Jaw/claw/lumber-straightening terminology variants searched; no disclosure of the combination. |
| A5 alternate_database | 5 | BLOCKED | Trade-journal full-text (Fine Homebuilding archive, carpentry press) not accessible; alternate routes attempted: Archive.org, Google Books, Taunton Press archive — all logged. |
| A6 organizational_records | 6 | NOT_APPLICABLE | rule_id: NA-06-005-2; rule_basis: no organization records for literature disclosure. |
| A7 jurisdiction_specific | 7 | NOT_APPLICABLE | rule_id: NA-06-005-3; rule_basis: literature is not jurisdiction-specific. |
| A8 independent_corroboration | 8 | BLOCKED | No second independent source for a negative literature claim. |

**Proposition disposition:** EXHAUSTED → EXCLUDED (`barrier_type: source_unavailable` + `insufficient_search_completion`).

---

## A-07-001 — Commercial adoption (P-07-001)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | No manufacturer identified as embodying the fixed-jaw hammer; "Karsnia" product search returned only the patent record. |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-07-001-1; rule_basis: adoption is not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | No adoption evidence in cited sources. |
| A4 terminology_expansion | 4 | COMPLETE | No adoption evidence under expanded terminology. |
| A5 alternate_database | 5 | BLOCKED | Trade-journal full-text unavailable (as A-02-004 A5). |
| A6 organizational_records | 6 | BLOCKED | Manufacturer production records not accessible; alternate routes attempted and logged. |
| A7 jurisdiction_specific | 7 | NOT_APPLICABLE | rule_id: NA-07-001-2; rule_basis: adoption is not jurisdiction-specific. |
| A8 independent_corroboration | 8 | BLOCKED | No second independent source for adoption. |

**Proposition disposition:** EXHAUSTED → EXCLUDED. `commercial_adoption` schema requires product_identity_link, source, date, independence_lineage_id (min 2 independent sources); no product identity link exists. Report language: "Commercial adoption could not be established from the completed evidence protocol."

---

## A-08-005 — "No other viable commercialization pathway exists" (P-08-005)

| Avenue | Priority | Disposition | Audit |
|---|---|---|---|
| A1 primary_source | 1 | COMPLETE | No evidence of alternative pathways beyond the four identified partner classes (Stanley Black & Decker, Estwing, Vaughan & Bushnell, Milwaukee/TTI). |
| A2 classification | 2 | NOT_APPLICABLE | rule_id: NA-08-005-1; rule_basis: pathways are not classification-dependent. |
| A3 citation_expansion | 3 | COMPLETE | No alternative pathways in cited sources. |
| A4 terminology_expansion | 4 | COMPLETE | No alternative pathways under expanded terminology. |
| A5 alternate_database | 5 | BLOCKED | Trade-journal full-text unavailable (as A-02-004 A5). |
| A6 organizational_records | 6 | BLOCKED | Company records not accessible. |
| A7 jurisdiction_specific | 7 | NOT_APPLICABLE | rule_id: NA-08-005-2; rule_basis: pathways are not jurisdiction-specific. |
| A8 independent_corroboration | 8 | BLOCKED | No second source for pathway absence. |

**Proposition disposition:** EXHAUSTED → EXCLUDED. Counterfactual-exclusivity audit: "no other pathway" claims absence of alternatives, not evidenced; reformulated as "strongest identified pathways" (P-08-006).

---

## Ledger totals

- **Avenue ladders opened:** 13 (A-02-004, A-03-003, A-03-004, A-03-005, A-03-006, A-04-002, A-05-008, A-05-009, A-05-010, A-05-011, A-06-005, A-07-001, A-08-005 — 13 ladders; 13 unique propositions)
- **Avenue dispositions:** COMPLETE 40, BLOCKED 30, NOT_APPLICABLE 34, REQUIRES_VERIFICATION 0
- **Propositions dispositioned EXHAUSTED:** 13 (all with every required avenue COMPLETE/BLOCKED/NOT_APPLICABLE; none REQUIRES_VERIFICATION)

**Invariant checks:**
- No proposition was dispositioned EXHAUSTED while any required avenue remained REQUIRES_VERIFICATION (hard stopping rule satisfied).
- BLOCKED appears only at avenue level, never at proposition level.
- Every NOT_APPLICABLE disposition carries rule_id + rule_basis.
- Every BLOCKED disposition logs the reason and alternate routes attempted.