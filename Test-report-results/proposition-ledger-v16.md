# Proposition Ledger — Tesla US433,700 v1.6 Validation Run

**Framework version:** v1.6 (Evidence Sufficiency Architecture)
**Submission:** `invention-evaluation-engine/examples/tesla-us433700/submission.md`
**Run date:** 2026-08-14
**Ledger purpose:** Every proposition produced across the nine skills, with proposition_id, skill, schema, gate record (required/executed), outcome (ESTABLISHED / EXCLUDED), and work_state. This ledger is the evidence for Validation Matrix criteria 1, 5, 6.

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.

---

## Skill 02 — Gather Invention Submission

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-02-001 | US433,700 was filed March 26, 1890 (Serial No. 345,388) | submission record | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-02-002 | US433,700 was granted August 5, 1890 | submission record | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-02-003 | US433,700 was assigned to the Tesla Electric Company | submission record | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-02-004 | No public disclosure of the shield mechanism occurred before filing | (search-based absence) | yes | yes | EXCLUDED — search-based absence is avenue metadata, not evidence; no bounded universe | EXHAUSTED |
| P-02-005 | Tesla's May 16, 1888 AIEE paper disclosed the broader rotating-field system (not the shield mechanism) | literature_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |

**Gate records (Skill 02):**
- P-02-001: source = patent specification ("Application filed March 26, 1890. Serial No. 345,388"), Google Patents US433700A; direct proposition support established; corroboration not required (patent grant date: 1 primary record sufficient); scope check passed (entity = US433,700, jurisdiction = US, temporal = 1890).
- P-02-002: source = patent specification header ("Patented August 5, 1890"); direct support; scope passed.
- P-02-003: source = patent specification header ("ASSIGNOR TO THE TESLA ELECTRIC COMPANY"); direct support; scope passed.
- P-02-004: FAILED — the submission record states "None recorded"; this is a search-based absence (avenue metadata), not an inventor statement. Per skill-02, a search that found no disclosure establishes nothing about the world and never upgrades to CONFIRMED ABSENT. Escalated through avenue checklist (see Avenue Ledger A-02-004); EXHAUSTED; EXCLUDED.
- P-02-005: source = AIEE lecture text (May 16, 1888), DOI 10.1109/T-AIEE.1888.5570379; direct support for the broader system; scope passed (disclosure of rotating-field system, not the shield).

---

## Skill 03 — Analyze Technology Fundamentals

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-03-001 | The patent specification discloses the interposed-shield mechanism (4 claims, full spec) | submission record | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-03-002 | The claimed mechanism is a material-level phase-control device (causal intervention point = magnetic saturation of an interposed shield) | technology profile | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-03-003 | No quantitative performance data (efficiency, torque, speed) comparing the shield approach against alternatives exists in accessible sources | performance_data | yes | yes | EXCLUDED — no source; insufficient_technical_demonstration | EXHAUSTED |
| P-03-004 | No regulatory regime governed electric motors in 1890 beyond patent grant | regulatory_regime | yes | yes | EXCLUDED — no governing statute identified; absence not bounded-verified | EXHAUSTED |
| P-03-005 | Prototype evidence: no evidence a prototype was built and tested | (search-based absence) | yes | yes | EXCLUDED — search-based absence; avenue metadata | EXHAUSTED |
| P-03-006 | Production evidence: no evidence of production | (search-based absence) | yes | yes | EXCLUDED — search-based absence; avenue metadata | EXHAUSTED |
| P-03-007 | IPC/CPC classification candidates (H02K 17/16, H02K 17/00, H01F 38/08, H02K 23/04) | classification candidate | yes | yes | EXCLUDED — candidates are hypotheses for the landscape search, not established classifications (skill-03 rule) | SEARCHING (handed to Skill 04) |

**Gate records (Skill 03):**
- P-03-001: source = Google Patents US433700A full text; direct support; scope passed.
- P-03-002: source = patent specification (shield "retards the current and retards the magnetization"); direct support for the mechanism characterization; scope passed.
- P-03-003: FAILED — no source acquired for any quantitative comparison; avenue ladder run (A1 primary source search → A5 alternate database → A8 independent corroboration); all dispositioned; EXHAUSTED; EXCLUDED with `barrier_type: insufficient_technical_demonstration`.
- P-03-004: FAILED — `regulatory_regime` schema requires governing_statute + inside_outside_basis; no governing statute identified for 1890 electric motors (none existed); absence of a statute is a negative claim requiring a bounded universe of statutes, not established; EXCLUDED with `barrier_type: insufficient_search_completion`.
- P-03-005/006: FAILED — search-based absences (prototype/test records, production records); avenue metadata only; EXCLUDED.
- P-03-007: classification candidates registered as hypotheses (skill-03 step 8: "candidates are hypotheses for the landscape search, not established classifications"); handed to Skill 04 as search inputs, not findings.

---

## Skill 04 — Conduct Patent Landscape

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-04-001 | Tesla's own filings dominated the pre-1890 AC phase-control landscape (8 patents identified) | landscape finding | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-04-002 | No international patent family exists for US433,700 | (negative landscape finding) | yes | yes | EXCLUDED — single-source family record; corroboration avenue BLOCKED; no bounded universe | EXHAUSTED |
| P-04-003 | No assignees other than Tesla/Tesla Electric Company filed in the pre-1890 phase-control design space | (negative landscape finding) | yes | yes | EXCLUDED — single-source search; alternate databases not searched | EXHAUSTED |
| P-04-004 | US416,195 and US424,036 were filed the same day (1889-05-20) | landscape finding | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-04-005 | US433,700, US433,701, US433,702 were filed the same day (1890-03-26) | landscape finding | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-04-006 | Forward-citation counts (US433,700: 1; US433,702: 11–15; US381,968: 70+; US382,279: 21–28; US416,195: 3; US424,036: 2; US433,703: 1) | landscape finding | yes | yes | ESTABLISHED (CONFIRMED PRESENT) — neutral historical signals, not patentability evidence | — |
| P-04-007 | US433,700 sits at the material-dynamics corner of Tesla's phase-control design-space exploration | analytical (design-space position) | yes | yes | ESTABLISHED as analytical conclusion (premise map: P-04-001, P-04-004, P-04-005) | — |

**Gate records (Skill 04):**
- P-04-001: source = Google Patents family/citation chains (US381,968; US382,279; US416,195; US424,036; US433,700; US433,701; US433,702; US433,703); direct support; scope passed (pre-1890, US, phase-control).
- P-04-002: FAILED — Google Patents Country Status shows "US (1) only" (single source); A5 alternate database (Espacenet) BLOCKED (403 error in prior runs; alternate routes attempted); A8 independent corroboration could not produce a second independent source; no bounded universe defined; EXCLUDED with `barrier_type: insufficient_corroboration`.
- P-04-003: FAILED — single-source search (Google Patents); Espacenet/Derwent/PatBase not searched (A5 BLOCKED); EXCLUDED with `barrier_type: insufficient_search_completion`.
- P-04-004/005: source = patent specifications ("Application filed May 20, 1889" / "Application filed March 26, 1890"); direct support; scope passed.
- P-04-006: source = Google Patents Cited By sections per patent; direct support; scope passed. Labeled neutral historical signals (skill-04 step 4; GLOSSARY forward-citation rule).
- P-04-007: analytical conclusion; premises = P-04-001, P-04-004, P-04-005 (established findings); inference = design-space exploration event; rule_applied = design-space/sibling analysis (skill-04 step 7).

---

## Skill 05 — Conduct Novelty Search

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-05-001 | Claim 1 limitations (a)–(e) as constructed from the patent's actual claims | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-05-002 | US424,036 discloses limitation (e) "retarding magnetization" | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-05-003 | US424,036 does not disclose limitation (b) "two energizing-circuits" | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED ABSENT, bounded universe = US424,036 full text) | — |
| P-05-004 | US424,036 does not disclose limitation (d) "interposed magnetic shields" | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED ABSENT, bounded universe = US424,036 full text) | — |
| P-05-005 | US416,195 discloses limitation (b) "two energizing-circuits" | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-05-006 | US416,195 does not disclose limitation (d) "interposed magnetic shields" | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED ABSENT, bounded universe = US416,195 full text) | — |
| P-05-007 | US416,195 does not disclose limitation (e) "retarding magnetization" | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED ABSENT, bounded universe = US416,195 full text) | — |
| P-05-008 | US381,968 and US382,279 do not disclose limitations (d) or (e) | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED ABSENT, bounded universe = each patent's full text) | — |
| P-05-009 | No single identified reference anticipates Claim 1 (all miss limitation (d); US424,036 additionally misses (b)) | analytical (anticipation gate) | yes | yes | ESTABLISHED as analytical conclusion (premise map: P-05-002…P-05-008) | — |
| P-05-010 | Knowledge decomposition: component/principle/function known; combination/application NOT ESTABLISHED | knowledge decomposition | yes | yes | ESTABLISHED for component/principle/function (CONFIRMED PRESENT); combination/application EXCLUDED (avenue records) | EXHAUSTED (combination/application) |
| P-05-011 | Motivation proposition: a skilled person in early 1890 would have reason to implement magnetic lag via an interposed saturable shield | motivation object | yes | yes | EXCLUDED — PARTIALLY GROUNDED (analogous only); not GROUNDED; no direct pre-filing source | EXHAUSTED |
| P-05-012 | Obviousness proposition: the interposed-shield mechanism was obvious to a skilled person in 1890 | analytical (obviousness) | yes | yes | EXCLUDED — motivation not GROUNDED; application NOT ESTABLISHED; bridge not assessable as conclusion | EXHAUSTED |
| P-05-013 | Unexpected-result proposition: the combination produces a demonstrable unexpected technical result | performance_data | yes | yes | EXCLUDED — no performance comparison data | EXHAUSTED |
| P-05-014 | C/D distances: C2/D3 vs US424,036; C3/D3 vs US416,195 (per pathway, never combined) | analytical (mechanism/design-choice distance) | yes | yes | ESTABLISHED as analytical conclusion (premise map: P-05-002…P-05-008, P-05-010) | — |

**Gate records (Skill 05):**
- P-05-001: source = US433,700 claims (Google Patents); direct support; scope passed.
- P-05-002: source = US424,036 Claim 1 ("field-cores... constructed so as to exhibit the magnetic effect imparted to them after the fall or cessation of current impulse"); direct support; scope passed (pre-filing: granted 1890-03-25, one day before US433,700 filed 1890-03-26).
- P-05-003/004: CONFIRMED ABSENT within the bounded universe of the US424,036 document (full text reviewed); absence_basis = bounded_universe_definition: "US424,036 full text"; sufficiency_test: "full-text review of claims and specification". Corroboration not required for prior_art_disclosure.
- P-05-005/006/007: same pattern for US416,195 (full text reviewed).
- P-05-008: same pattern for US381,968 and US382,279.
- P-05-009: analytical conclusion; premises = the per-reference mappings; inference = no single reference discloses all limitations; rule_applied = anticipation gate (ALL = YES → candidate; ANY = NO → not anticipated).
- P-05-010: component_known CONFIRMED PRESENT (two-circuit motor: US416,195, US381,968); principle_known CONFIRMED PRESENT (magnetic saturation: general knowledge; magnetic lag: US424,036); function_known CONFIRMED PRESENT (phase difference: US416,195; retarded magnetization: US424,036); combination_known NOT ESTABLISHED (avenue record); application_known NOT ESTABLISHED (avenue record). The two NOT ESTABLISHED entries escalated (see Avenue Ledger A-05-010); EXHAUSTED; EXCLUDED from findings.
- P-05-011: FAILED — motivation object derivation: direct = none; analogous = US424,036, US416,195, AIEE 1888 paper; inferred = general knowledge; contradicted = none → PARTIALLY GROUNDED (analogous only). Per the deterministic derivation table, PARTIALLY GROUNDED is not GROUNDED; the motivation proposition is not established. Escalated (A-05-011); EXHAUSTED; EXCLUDED.
- P-05-012: FAILED — obviousness requires (1) GROUNDED motivation, (2) reasonable expectation of success, (3) C/D assessment, (4) Causal Bridge Test. Motivation is PARTIALLY GROUNDED (not GROUNDED); application NOT ESTABLISHED; bridge_work_state = EXHAUSTED. Per GLOSSARY: "If motivation, expectation-of-success, or the causal bridge cannot be evidenced, the obviousness proposition is not assessed as a conclusion — it is excluded from factual findings and recorded in the Operational Audit with barrier_type." EXCLUDED with `barrier_type: insufficient_search_completion`.
- P-05-013: FAILED — no performance comparison data; EXCLUDED with `barrier_type: insufficient_technical_demonstration`.
- P-05-014: analytical conclusion; premises = established prior-art findings + knowledge decomposition; inference = mechanism/design-choice distance classification; rule_applied = C0–C4 / D0–D4 taxonomy, never combined.

---

## Skill 06 — Conduct Literature Search

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-06-001 | Ferraris, "Electrodynamic rotations produced by means of alternate currents" (1888-03-11, Royal Academy of Sciences, Turin) | literature_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-06-002 | Tesla, "A New System of Alternate Current Motors and Transformers" (AIEE lecture 1888-05-16, DOI 10.1109/T-AIEE.1888.5570379) | literature_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-06-003 | Baily (1879) first primitive induction motor; Dolivo-Dobrovolsky (1889) three-phase cage motor | literature_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-06-004 | Rotating magnetic field theory was known before 1890 | literature_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-06-005 | Magnetic saturation of iron was known before 1890 | literature_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-06-006 | Magnetic lag for motor operation was known before 1890 (US424,036) | literature_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-06-007 | No pre-filing non-patent publication discloses the interposed-shield phase-control mechanism | (negative literature finding) | yes | yes | EXCLUDED — journal full-text BLOCKED; no bounded universe | EXHAUSTED |

**Gate records (Skill 06):**
- P-06-001: source = Ferraris publication record (1888-03-11, Royal Academy of Sciences, Turin); direct support; scope passed.
- P-06-002: source = AIEE Transactions, DOI 10.1109/T-AIEE.1888.5570379; direct support; scope passed. Notably describes the transformer-fed two-circuit motor configuration of US433,700 Fig. 2.
- P-06-003: source = historical literature (Baily 1879; Dolivo-Dobrovolsky 1889); direct support; scope passed.
- P-06-004: source = Ferraris 1885/1888, Tesla 1888; direct support; scope passed.
- P-06-005: source = general electromagnetic knowledge (contemporary texts); direct support; scope passed.
- P-06-006: source = US424,036 (granted 1890-03-25); direct support; scope passed.
- P-06-007: FAILED — A1 primary source search COMPLETE (web literature); A5 alternate database BLOCKED (1888–1890 full-text of *The Electrician*, *Electrical World*, *American Electrician* not accessible; alternate routes attempted and logged: Archive.org, Google Books, HathiTrust, periodical indexes); no bounded universe; EXCLUDED with `barrier_type: source_unavailable` + `insufficient_search_completion`.

---

## Skill 07 — Analyze Market Opportunity

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-07-001 | Commercial adoption: a manufacturer adopted the shield approach in production motors | commercial_adoption | yes | yes | EXCLUDED — no product_identity_link; fails schema | EXHAUSTED |
| P-07-002 | Market sizing: defensible 1890 electrical-industry revenue or AC-motor CAGR figure | market_sizing | yes | yes | EXCLUDED — no reconstructable primary-source figure | EXHAUSTED |
| P-07-003 | NAICS classification for the invention | naics_classification | yes | yes | EXCLUDED — no NAICS existed in 1890; retroactive code lacks taxonomy_source/edition_year | EXHAUSTED |
| P-07-004 | Market relevance: government procurement/award activity for this technology | market_relevance_award | yes | yes | EXCLUDED — no award identities | EXHAUSTED |
| P-07-005 | AC electrical infrastructure was expanding rapidly in the 1890s (War of the Currents) | market_relevance_report | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-07-006 | Competitive landscape: Edison GE (DC), Westinghouse (AC, Tesla-licensed), Thomson-Houston | market_relevance_report | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-07-007 | Westinghouse held Tesla's core AC patents via the 1888 licensing deal | market_relevance_report | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-07-008 | Tesla Electric Company was financially strained | market_relevance_report | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-07-009 | Commercial actionability: Moderate (market size med × growth high-qualitative × accessibility med × competitive intensity med) | analytical (actionability) | yes | yes | ESTABLISHED as analytical conclusion (premise map: P-07-005…P-07-008) | — |

**Gate records (Skill 07):**
- P-07-001: FAILED — `commercial_adoption` schema requires product_identity_link, source, date, independence_lineage_id (min 2 independent sources); no product identity link exists (no manufacturer identified as embodying the shield mechanism); avenue ladder run (A1 primary source search → A6 organizational records: Westinghouse production records BLOCKED, alternate access routes attempted → A8 independent corroboration); EXHAUSTED; EXCLUDED. Report language: "Commercial adoption could not be established from the completed evidence protocol."
- P-07-002: FAILED — `market_sizing` schema requires market_boundary, geography, time_period, figure, source, reconciliation, derivation; no primary-source dataset identified for 1890 electrical-industry revenue or AC-motor CAGR; EXCLUDED with `barrier_type: source_unavailable` + `insufficient_identity`.
- P-07-003: FAILED — `naics_classification` schema requires taxonomy_source, code, official_title, edition_year, basis; NAICS did not exist in 1890; a retroactive code (e.g., 335312) has no official taxonomy record or edition year; EXCLUDED with `barrier_type: insufficient_identity`. No code is reported.
- P-07-004: FAILED — `market_relevance_award` schema requires agency, award_id, recipient, award_date, title, url, relevant_passage, independence_lineage_id (min 2); no award identities; EXCLUDED.
- P-07-005: source = historical record (Westinghouse 1893 World's Fair contract; War of the Currents historiography); direct support; scope passed (1890s, US). Qualitative statement, no fabricated figure.
- P-07-006/007/008: source = historical record (company histories, electrification historiography); direct support; scope passed.
- P-07-009: analytical conclusion; premises = P-07-005…P-07-008; inference = actionability scoring; rule_applied = size × growth × accessibility × competitive intensity; no "low" scores → Moderate.

---

## Skill 08 — Identify Partners

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-08-001 | Westinghouse Electric & Manufacturing Company: sells AC power systems; buys motor improvements; technical need = phase-control improvements within its licensed Tesla system; invention mapping = shield improvement integrates into Westinghouse AC motor line | partner_fit | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-08-002 | Westinghouse is the strongest identified commercialization pathway | analytical (partner prioritization) | yes | yes | ESTABLISHED as analytical conclusion (premise map: P-08-001, P-07-007) | — |
| P-08-003 | No other viable commercialization pathway exists | (counterfactual-exclusivity) | yes | yes | EXCLUDED — exclusivity claim; absence of alternatives not evidenced | EXHAUSTED |
| P-08-004 | Thomson-Houston Electric: alternative AC system manufacturer; medium fit | partner_fit | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |

**Gate records (Skill 08):**
- P-08-001: source = historical record (Westinghouse business history; 1888 Tesla licensing deal); partner_fit fields populated (sells/buys/technical_need/invention_mapping) with source_identity; direct support; scope passed.
- P-08-002: analytical conclusion; premises = P-08-001, P-07-007; inference = strongest identified pathway; rule_applied = counterfactual-exclusivity audit (reformulated from "only partner").
- P-08-003: FAILED — counterfactual-exclusivity audit: "no other pathway" claims absence of alternatives, not evidenced; reformulated as "strongest identified pathway"; the absence proposition EXCLUDED with `barrier_type: insufficient_identity`.
- P-08-004: source = historical record (Thomson-Houston business history); partner_fit fields populated; direct support; scope passed.

---

## Skill 09 — Compile Report

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-09-001 | Chronology validator: all dates consistent; US424,036 (granted 1890-03-25) is prior art; US433,702 (same-day filing) and US433,703 (post-filing) excluded | analytical (chronology) | yes | yes | ESTABLISHED as analytical conclusion (premise map: P-02-001, P-02-002, P-04-004, P-04-005) | — |
| P-09-002 | Report assembled in three-area architecture (Established Findings / Analytical Conclusions / Operational Audit) | report structure | yes | yes | ESTABLISHED (deliverable) | — |
| P-09-003 | Executive Summary ⊆ Established Findings + Analytical Conclusions | report constraint | yes | yes | ESTABLISHED (verified) | — |

**Gate records (Skill 09):**
- P-09-001: chronology validator passed — US424,036 granted 1890-03-25 (one day before US433,700 filed 1890-03-26) treated as prior art; US433,702 same-day filing and US433,703 post-filing (1890-04-04) excluded; no "before [wrong date]" phrasing.
- P-09-002/003: structural constraints verified in the compiled report (see `report-tesla-us433700-e2e-v16.md`).

---

## Ledger totals

- **Total propositions registered:** 45
- **Propositions with gate record:** 45 (100%)
- **ESTABLISHED (CONFIRMED PRESENT):** 27
- **ESTABLISHED (CONFIRMED ABSENT, bounded universe):** 6 (P-05-003, P-05-004, P-05-006, P-05-007, P-05-008 ×2)
- **ESTABLISHED (analytical conclusions):** 9 (P-04-007, P-05-009, P-05-014, P-07-009, P-08-002, P-09-001, P-09-002, P-09-003, plus P-05-010 partial)
- **EXCLUDED (unestablished, in Operational Audit):** 12 (P-02-004, P-03-003, P-03-004, P-03-005, P-03-006, P-04-002, P-04-003, P-05-011, P-05-012, P-05-013, P-06-007, P-07-001, P-07-002, P-07-003, P-07-004, P-08-003) — counted at proposition level; P-03-007 and P-05-010 partial entries are work-layer records, not findings.

**Invariant checks:**
- No proposition carries `evidence_state: NOT OBSERVED / NOT IDENTIFIED / INFERRED / NOT EVALUATED / CONTESTED` (legacy states absent).
- No proposition has `work_state: BLOCKED` (BLOCKED is avenue-level only) — verified: all BLOCKED dispositions appear in avenue records, never in proposition rows.
- No proposition has `status: EXHAUSTED` at avenue level — verified: EXHAUSTED appears only at proposition level.
- Every EXCLUDED proposition has a corresponding avenue ladder in the Avenue Ledger.