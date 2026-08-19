# Proposition Ledger — US 5,850,650 (Combination Hammer and Lumber Manipulating Tool) v1.6 Run

**Framework version:** v1.6 (Evidence Sufficiency Architecture)
**Submission:** `evaluations/us5850650/submission-us5850650.md`
**Run date:** 2026-08-14
**Ledger purpose:** Every proposition produced across the nine skills, with proposition_id, skill, schema, gate record (required/executed), outcome (ESTABLISHED / EXCLUDED), and work_state. This ledger is the evidence for Validation Matrix criteria 1, 5, 6.

**Governing principle:** Unsupported assertions are errors. Missing evidence is a work queue, not an answer.

---

## Skill 02 — Gather Invention Submission

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-02-001 | US5850650 was filed June 13, 1997 (Appl. No. 08/876,165) | submission record | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-02-002 | US5850650 was granted December 22, 1998 | submission record | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-02-003 | Inventor John J. Karsnia, International Falls, MN; assignee individual | submission record | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-02-004 | No public disclosure of the invention occurred before filing | (search-based absence) | yes | yes | EXCLUDED — search-based absence is avenue metadata, not evidence; no inventor statement available | EXHAUSTED |
| P-02-005 | Canadian family member CA2240576C exists (filed 1998-06-12, priority 1997-06-13, granted 2001-06-05) | submission record | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-02-006 | Legal status: US term expired 2017-06-13 (20 years from filing); CA expired 2018-06-12 | submission record | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |

**Gate records (Skill 02):**
- P-02-001: source = patent front page ("Appl. No.: 876,165 / Filed: Jun. 13, 1997"), Google Patents US5850650A; direct proposition support established; corroboration not required (patent grant date: 1 primary record sufficient); scope check passed (entity = US5850650, jurisdiction = US, temporal = 1997).
- P-02-002: source = patent front page ("Date of Patent: Dec. 22, 1998"); direct support; scope passed.
- P-02-003: source = patent front page ("Inventor: John J. Karsnia, 2729 County Rd. 94, International Falls, Minn. 56649"); assignee = Individual (Google Patents); direct support; scope passed.
- P-02-004: FAILED — the submission record states "Public disclosure date: None recorded"; this is a search-based absence (avenue metadata), not an inventor statement. Per skill-02, a search that found no disclosure establishes nothing about the world and never upgrades to CONFIRMED ABSENT. Escalated through avenue checklist (see Avenue Ledger A-02-004); EXHAUSTED; EXCLUDED.
- P-02-005: source = Google Patents CA2240576C record (filing date 1998-06-12, priority date 1997-06-13, grant 2001-06-05); direct support; scope passed (family member, same invention title).
- P-02-006: source = Google Patents legal-status records (US: "Expired - Lifetime", anticipated expiration 2017-06-13; CA: MKEX expiry event, effective 2018-06-12) + statutory term computation (20 years from filing, post-1995 regime); direct support; scope passed.

---

## Skill 03 — Analyze Technology Fundamentals

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-03-001 | The patent discloses a hammer-head with claw, striking head, socket; jaw non-movably secured to socket opposing claw, spaced finite distance (claims 1–5); alternative: jaw secured to handle (claims 6–13) | submission record | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-03-002 | The claimed mechanism is a fixed-geometry single-tool integration: no moving parts; jaw + claw grip lumber; handle provides leverage to twist lumber straight | technology profile | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-03-003 | No quantitative performance data (weight comparison, strike character, manipulation force) exists in accessible sources | performance_data | yes | yes | EXCLUDED — no source; insufficient_technical_demonstration | EXHAUSTED |
| P-03-004a | OSHA 29 CFR 1910.242 (Hand tools) requires employers to maintain hand tools in safe working condition | regulatory_regime | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-03-004b | No mandatory product-design approval regime (CPSC mandatory standard, FDA, etc.) governs hand hammers in the US | (negative regulatory claim) | yes | yes | EXCLUDED — negative claim; bounded universe of mandatory standards not established | EXHAUSTED |
| P-03-005 | Prototype evidence: no evidence a prototype was built and tested | (search-based absence) | yes | yes | EXCLUDED — search-based absence; avenue metadata | EXHAUSTED |
| P-03-006 | Production evidence: no evidence of production | (search-based absence) | yes | yes | EXCLUDED — search-based absence; avenue metadata | EXHAUSTED |
| P-03-007 | Official classification on the patent: Int. Cl. 6 B25D 1/04; U.S. Cl. 7/146; Field of Search 7/143, 146, 147 | classification candidate | yes | yes | ESTABLISHED (CONFIRMED PRESENT) as the patent's official classification record; candidate set (B25D 1/00, B25D 1/04, USPC 7/146, 7/143, 7/147) handed to Skill 04 as search inputs | SEARCHING (handed to Skill 04) |

**Gate records (Skill 03):**
- P-03-001: source = Google Patents US5850650A full text (claims 1–13, specification); direct support; scope passed.
- P-03-002: source = patent specification (jaw "non-movably secured"; "does not have any moving parts"; "approximately the same weight as a conventional hammer"; handle manipulation "forcing the lumber 12 to twist into the desired position"); direct support for the mechanism characterization; scope passed.
- P-03-003: FAILED — no source acquired for any quantitative comparison (weight delta, strike-character measurement, manipulation force); avenue ladder run (A1 primary source search → A5 alternate database → A8 independent corroboration); all dispositioned; EXHAUSTED; EXCLUDED with `barrier_type: insufficient_technical_demonstration`.
- P-03-004a: source = OSHA 29 CFR 1910.242 (public regulation text); direct support (general workplace hand-tool safety rule); scope passed. Regulatory burden estimate: LOW (analytical, see report §2).
- P-03-004b: FAILED — `regulatory_regime` schema requires governing_statute + inside_outside_basis; the absence of a mandatory product-design standard is a negative claim requiring a bounded universe of mandatory standards (CPSC 16 CFR product list, FDA device classes), not established; EXCLUDED with `barrier_type: insufficient_search_completion`.
- P-03-005/006: FAILED — search-based absences (prototype/test records, production records); avenue metadata only; EXCLUDED.
- P-03-007: the patent's own classification (Int. Cl. 6 B25D 1/04; U.S. Cl. 7/146) is CONFIRMED PRESENT from the front page; the broader candidate set for the landscape search is registered as hypotheses (skill-03 step 8), handed to Skill 04 as search inputs, not findings.

---

## Skill 04 — Conduct Patent Landscape

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-04-001 | B25D 1/00 (hand hammers) class: ~84 patents (ipqwery index); B25D total US grants 2015–2025 = 1,146 (PlainPatent); top B25D assignees 2015–2025: Makita 175, Hilti 126, Milwaukee 113, Black & Decker 78 (dominated by power percussion tools) | landscape finding | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-04-002 | No international family members beyond US + CA | (negative landscape finding) | yes | yes | EXCLUDED — single-source family record; corroboration avenue BLOCKED; no bounded universe | EXHAUSTED |
| P-04-003 | Forward citations: US5850650 family cited by 22 documents (Stanley B&D demolition utility tool family, Mrugalski US7311293B2, Yung-Shou Chen multipurpose tools, Fiskars demolition tools, Ezy Lifter board removal tool, CN104275681B) | landscape finding | yes | yes | ESTABLISHED (CONFIRMED PRESENT) — neutral historical signals, not patentability evidence | — |
| P-04-004 | Design-space position: Karsnia explored two mounting configurations in one patent (jaw-on-socket claims 1–5; jaw-on-handle claims 6–13); no sibling filings identified | landscape finding | yes | yes | ESTABLISHED (CONFIRMED PRESENT) for the two-configuration fact; sibling-absence EXCLUDED (search-based absence) | EXHAUSTED (sibling-absence) |
| P-04-005 | Post-filing lineage: Stanley Black & Decker demolition utility tool (US8024994B2, priority 2007-06-26) has grasping jaws with teeth + striking head and cites US5850650 | landscape finding | yes | yes | ESTABLISHED (CONFIRMED PRESENT) — neutral historical signal | — |

**Gate records (Skill 04):**
- P-04-001: source = ipqwery IPC holdings index (B25D 1/00: 84 patents) + PlainPatent/USPTO-derived B25D counts (1,146 US grants 2015–2025; Makita 175, Hilti 126, Milwaukee 113, Black & Decker 78); direct support; scope passed (B25D, US, 2015–2025). Note: B25D includes power percussion tools; hand-hammer-specific counts are a subset.
- P-04-002: FAILED — Google Patents Country Status shows "US (1) + CA (1)" (single source); A5 alternate database (Espacenet) BLOCKED (403 error in prior runs; alternate routes attempted); A8 independent corroboration could not produce a second independent source; no bounded universe defined; EXCLUDED with `barrier_type: insufficient_corroboration`.
- P-04-003: source = Google Patents "Families Citing this family" (22 documents, listed); direct support; scope passed. Labeled neutral historical signals (skill-04 step 4; GLOSSARY forward-citation rule).
- P-04-004: two-configuration fact source = patent claims 1–5 vs 6–13 (jaw on socket vs jaw on handle); direct support. Sibling-absence: search-based absence (no other Karsnia filings identified); EXCLUDED.
- P-04-005: source = Google Patents US8024994B2 record (assignee Stanley Black & Decker, Inc.; cited-by relationship to US5850650); direct support; scope passed. Neutral historical signal.

---

## Skill 05 — Conduct Novelty Search

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-05-001 | Claim 1 limitations (a)–(d) and Claim 6 limitations (a)–(e) as constructed from the patent's actual claims | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-05-002 | US513271A (Matthews 1894, "Wrench"): hammer part + movable jaw sliding on shank with inclined apertures + dowel pin; no socket, no claw, no lumber function; jaw movable, not non-movably secured | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-05-003 | US1469472A (Bangert 1923, "Combination tool"): hammer/wrench combo with stationary serrated jaw face on hammer head + slide jaw; no claw, no socket, no lumber | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-05-004 | US4762303A (Thomas 1988, "Lumber turning tool"): elongated handle + head with two opposed spaced claws, one shorter; claws engage opposing sides of lumber; handle provides leverage; no striking head, no socket | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-05-005 | US5255575A (Williams 1993, "Multi-purpose hand tool"): interchangeable heads; no fixed jaw, no lumber function | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-05-006 | US5787676A (Scharf, filed 1997-03-18, granted 1998-08-04): lumber straightening apparatus — foot-operated lever, not a hammer; pre-filing priority | prior_art_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-05-007 | No single identified reference anticipates Claim 1 or Claim 6 | analytical (anticipation gate) | yes | yes | ESTABLISHED as analytical conclusion (premise map: P-05-002…P-05-006) | — |
| P-05-008 | Knowledge decomposition: component/principle/function known; combination/application NOT ESTABLISHED | knowledge decomposition | yes | yes | ESTABLISHED for component/principle/function (CONFIRMED PRESENT); combination/application EXCLUDED (avenue records) | EXHAUSTED (combination/application) |
| P-05-009 | Motivation proposition: a skilled person in 1997 would have reason to add a fixed lumber-gripping jaw to a hammer | motivation object | yes | yes | EXCLUDED — PARTIALLY GROUNDED (analogous only); not GROUNDED; no direct pre-filing source | EXHAUSTED |
| P-05-010 | Obviousness proposition: the fixed-jaw hammer was obvious to a skilled person in 1997 | analytical (obviousness) | yes | yes | EXCLUDED — motivation not GROUNDED; application NOT ESTABLISHED; bridge not assessable as conclusion | EXHAUSTED |
| P-05-011 | Unexpected-result proposition: the combination produces a demonstrable unexpected technical result | performance_data | yes | yes | EXCLUDED — no performance comparison data | EXHAUSTED |
| P-05-012 | C/D distances: C2/D3 vs US4762303 (closest functional art); C2/D2 vs US1469472 (per pathway, never combined) | analytical (mechanism/design-choice distance) | yes | yes | ESTABLISHED as analytical conclusion (premise map: P-05-002…P-05-008) | — |

**Gate records (Skill 05):**
- P-05-001: source = US5850650 claims (Google Patents); direct support; scope passed. Claim 1 limitations: (a) hammer-head having a claw, a striking head and a socket for receiving a handle; (b) jaw non-movably secured to said socket opposing said claw; (c) spaced from said claw a finite distance; (d) piece of lumber positionable between jaw and claw. Claim 6 limitations: (a) hammer having hammer-head and handle attached; (b) hammer-head includes claw and striking head; (c) jaw non-movably secured to handle opposing claw; (d) spaced finite distance; (e) lumber positionable between.
- P-05-002: source = US513271A (Google Patents; spec description in US5850650 col. 1: "shank with inclined apertures along its front side in combination with a movable jaw and an inclined dowel pin"); direct support; scope passed (pre-filing: granted 1894).
- P-05-003: source = US1469472A (Google Patents; combination tool with hammer head and wrench jaws); direct support; scope passed (pre-filing: granted 1923).
- P-05-004: source = US4762303A (Google Patents; spec description in US5850650 col. 1: "elongated handle and a head having two opposed and spaced apart claws with one substantially shorter in length than the other"); direct support; scope passed (pre-filing: granted 1988). Closest functional prior art for the lumber-manipulation function.
- P-05-005: source = US5255575A (Google Patents); direct support; scope passed (pre-filing: granted 1993).
- P-05-006: source = US5787676A (Google Patents; filed 1997-03-18, before US5850650's 1997-06-13 filing); direct support; scope passed (pre-filing priority).
- P-05-007: analytical conclusion; premises = the per-reference mappings; inference = no single reference discloses all limitations; rule_applied = anticipation gate (ALL = YES → candidate; ANY = NO → not anticipated).
- P-05-008: component_known CONFIRMED PRESENT (claw hammers: ubiquitous; lumber-gripping claws: US4762303); principle_known CONFIRMED PRESENT (opposed-grip leverage: US4762303); function_known CONFIRMED PRESENT (lumber manipulation: US4762303; carpenter practice literature); combination_known NOT ESTABLISHED (avenue record); application_known NOT ESTABLISHED (avenue record). The two NOT ESTABLISHED entries escalated (see Avenue Ledger A-05-008); EXHAUSTED; EXCLUDED from findings.
- P-05-009: FAILED — motivation object derivation: direct = none; analogous = US4762303 (lumber grip), US1469472 (jaw on hammer head), US513271 (jaw on hammer), Maggard 711,408 (sliding-jaw hammer, per spec); inferred = general knowledge of twisted-lumber problem (Fine Homebuilding practice articles); contradicted = none → PARTIALLY GROUNDED (analogous only). Per the deterministic derivation table, PARTIALLY GROUNDED is not GROUNDED; the motivation proposition is not established. Escalated (A-05-009); EXHAUSTED; EXCLUDED.
- P-05-010: FAILED — obviousness requires (1) GROUNDED motivation, (2) reasonable expectation of success, (3) C/D assessment, (4) Causal Bridge Test. Motivation is PARTIALLY GROUNDED (not GROUNDED); application NOT ESTABLISHED; bridge_work_state = EXHAUSTED. Per GLOSSARY: obviousness is not assessed as a conclusion — excluded from factual findings, recorded in the Operational Audit with `barrier_type: insufficient_search_completion`.
- P-05-011: FAILED — no performance comparison data; EXCLUDED with `barrier_type: insufficient_technical_demonstration`.
- P-05-012: analytical conclusion; premises = established prior-art findings + knowledge decomposition; inference = mechanism/design-choice distance classification; rule_applied = C0–C4 / D0–D4 taxonomy, never combined. Vs US4762303: C2 (same underlying principle — opposed-grip leverage — different configuration: hammer-integrated) / D3 (cross-application leap: recognizing a hammer's claw can serve as one gripping element of a lumber manipulator). Vs US1469472: C2 / D2 (jaw-on-hammer-head known for wrenching; lumber application is the leap).

---

## Skill 06 — Conduct Literature Search

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-06-001 | Fine Homebuilding (1991-11-01) "How to Straighten Crooked Boards, Built-Up Beams, and Headers": hammer + 16d nail used as lever to align framing members (pre-filing; lumber-straightening practice known; does NOT disclose a fixed jaw on a hammer) | literature_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-06-002 | Fine Homebuilding (1999-07-01) "Tweak a twisted stud": bar clamp used as lever to straighten twisted stud (post-filing; background) | literature_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-06-003 | Fine Homebuilding (2000-09-01) "Straightening Framed Walls": strong-backing, planing, shimming techniques (post-filing; background) | literature_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-06-004 | Audel's Carpenters and Builders Guide (1923) documents balloon-framing practice (background; pre-filing) | literature_disclosure | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-06-005 | No pre-filing non-patent publication discloses the specific fixed-jaw hammer combination | (negative literature finding) | yes | yes | EXCLUDED — journal full-text BLOCKED; no bounded universe | EXHAUSTED |

**Gate records (Skill 06):**
- P-06-001: source = Fine Homebuilding article (1991-11-01, "How to Straighten Crooked Boards, Built-Up Beams, and Headers"); direct support for the practice (hammer claw + 16d nail as lever); scope passed (pre-filing: 1991 < 1997). Relevance: establishes the lumber-straightening problem and a hammer-adjacent practice as known before filing; does not disclose the claimed fixed-jaw device.
- P-06-002: source = Fine Homebuilding article (1999-07-01, "Tweak a twisted stud"); direct support; scope passed (post-filing; background only).
- P-06-003: source = Fine Homebuilding article (2000-09-01, "Straightening Framed Walls"); direct support; scope passed (post-filing; background only).
- P-06-004: source = Audel's Carpenters and Builders Guide (1923 edition, referenced in Fine Homebuilding 2024-05-08 balloon-framing article); direct support for framing practice; scope passed (pre-filing; background).
- P-06-005: FAILED — A1 primary source search COMPLETE (web literature); A5 alternate database BLOCKED (full-text of trade journals not accessible; alternate routes attempted and logged); no bounded universe; EXCLUDED with `barrier_type: source_unavailable` + `insufficient_search_completion`.

---

## Skill 07 — Analyze Market Opportunity

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-07-001 | Commercial adoption: a manufacturer adopted the fixed-jaw hammer in production | commercial_adoption | yes | yes | EXCLUDED — no product_identity_link; fails schema | EXHAUSTED |
| P-07-002 | Market sizing: US hand tools market ≈ USD 6.1B (2024), CAGR ≈ 3.4% to 2032 (PS Market Research); US hammer market CAGR 3.0–4.5% (2026–2035) (IndexBox) — reconciled: hammer ⊂ hand tools, both mature low-growth | market_sizing | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-07-003 | NAICS classification: 332216 Saw Blade and Handtool Manufacturing (2022 ed., US Census), includes "Hammers, handtools, manufacturing" | naics_classification | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-07-004 | Competitive landscape: Stanley Black & Decker, Estwing, Vaughan & Bushnell, Stiletto, Milwaukee (TTI), Tekton, private labels (Husky/Kobalt/Hart); premium tier ~45–55% of category revenue; private label 25–35% of units | market_relevance_report | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-07-005 | Commercial actionability: Moderate (market size med-high × growth low × accessibility med × competitive intensity high) — with patent-expiry caveat | analytical (actionability) | yes | yes | ESTABLISHED as analytical conclusion (premise map: P-07-002, P-07-004, P-02-006) | — |

**Gate records (Skill 07):**
- P-07-001: FAILED — `commercial_adoption` schema requires product_identity_link, source, date, independence_lineage_id (min 2 independent sources); no product identity link exists (no manufacturer identified as embodying the fixed-jaw hammer; "Karsnia" product search returned only the patent record); avenue ladder run (A1 primary source search → A6 organizational records → A8 independent corroboration); EXHAUSTED; EXCLUDED. Report language: "Commercial adoption could not be established from the completed evidence protocol."
- P-07-002: source = PS Market Research (US hand tools market, USD 6.1B 2024 → USD 7.8B 2032, CAGR 3.4%) + IndexBox (US hammer market, CAGR 3.0–4.5% 2026–2035); two independent publishers; reconciliation: hammer is a subsegment of hand tools; both mature, low-single-digit growth; derivation: report figures, boundaries stated; scope passed (US, 2024–2035).
- P-07-003: source = US Census NAICS 2022 documentation (332216 "Saw Blade and Handtool Manufacturing"; includes "Hammers, handtools, manufacturing"); basis = product-manufacturing match; scope passed.
- P-07-004: source = IndexBox (US hammer market competitive structure), Valuates (framing hammer manufacturers: Estwing, Vaughan & Bushnell, STILETTO, Milwaukee, TEKTON, STANLEY), Strategic Market Research (striking tools), HTF Market Intelligence (claw hammer), Freedonia (US hand tools leaders); multiple independent publishers; direct support; scope passed.
- P-07-005: analytical conclusion; premises = P-07-002, P-07-004, P-02-006; inference = actionability scoring; rule_applied = size × growth × accessibility × competitive intensity; one "low" (growth) + high competitive intensity → Moderate with risk flags; patent-expiry caveat (no IP to license; concept in public domain).

---

## Skill 08 — Identify Partners

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-08-001 | Stanley Black & Decker: sells hammers (Stanley/DeWalt); buys/absorbs designs; technical need = differentiated professional hand tools; mapping = fixed-jaw framing hammer concept fits Stanley/DeWalt pro lines | partner_fit | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-08-002 | Estwing Manufacturing: sells premium one-piece steel hammers; technical need = new professional features; mapping = fixed-jaw feature differentiates in premium tier | partner_fit | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-08-003 | Vaughan & Bushnell: sells framing hammers (California Framer); niche loyalty; mapping = framing-focused line | partner_fit | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-08-004 | Milwaukee Tool (TTI): sells professional hand tools; mapping = pro framing line | partner_fit | yes | yes | ESTABLISHED (CONFIRMED PRESENT) | — |
| P-08-005 | No other viable commercialization pathway exists | (counterfactual-exclusivity) | yes | yes | EXCLUDED — exclusivity claim; absence of alternatives not evidenced | EXHAUSTED |
| P-08-006 | Estwing and Vaughan & Bushnell are the strongest identified product-fit pathways (framing-focused premium makers); partnership value limited to design/feature licensing given patent expiry | analytical (partner prioritization) | yes | yes | ESTABLISHED as analytical conclusion (premise map: P-08-001…P-08-004, P-02-006) | — |

**Gate records (Skill 08):**
- P-08-001: source = IndexBox / Strategic Market Research / HTF (Stanley Black & Decker as category leader across DIY and trade segments, Stanley/DeWalt brands); partner_fit fields populated (sells/buys/technical_need/invention_mapping) with source_identity; direct support; scope passed.
- P-08-002: source = IndexBox / Strategic Market Research (Estwing: premium one-piece steel construction, made-in-America, professional loyalty); partner_fit fields populated; direct support; scope passed.
- P-08-003: source = IndexBox / Valuates / Strategic Market Research (Vaughan & Bushnell: heritage US framing-tool maker, California Framer); partner_fit fields populated; direct support; scope passed.
- P-08-004: source = IndexBox / Valuates (Milwaukee Tool: professional tier, framing hammers); partner_fit fields populated; direct support; scope passed.
- P-08-005: FAILED — counterfactual-exclusivity audit: "no other pathway" claims absence of alternatives, not evidenced; reformulated as "strongest identified pathways" (P-08-006); the absence proposition EXCLUDED with `barrier_type: insufficient_identity`.
- P-08-006: analytical conclusion; premises = P-08-001…P-08-004, P-02-006; inference = strongest identified pathways; rule_applied = counterfactual-exclusivity audit (reformulated from "only partner"); patent-expiry caveat stated.

---

## Skill 09 — Compile Report

| proposition_id | Proposition | Schema | Gate required | Gate executed | Outcome | work_state |
|---|---|---|---|---|---|---|
| P-09-001 | Chronology validator: all dates consistent; US filed 1997-06-13, granted 1998-12-22; CA filed 1998-06-12 (priority 1997-06-13), granted 2001-06-05; US term expired 2017-06-13; CA expired 2018-06-12; all prior art pre-dates filing | analytical (chronology) | yes | yes | ESTABLISHED as analytical conclusion (premise map: P-02-001, P-02-002, P-02-005, P-02-006, P-05-002…P-05-006) | — |
| P-09-002 | Report assembled in three-area architecture (Established Findings / Analytical Conclusions / Operational Audit) | report structure | yes | yes | ESTABLISHED (deliverable) | — |
| P-09-003 | Executive Summary ⊆ Established Findings + Analytical Conclusions | report constraint | yes | yes | ESTABLISHED (verified) | — |

**Gate records (Skill 09):**
- P-09-001: chronology validator passed — US filed 1997-06-13, granted 1998-12-22; CA filed 1998-06-12 (within 12-month Convention window of US priority 1997-06-13), granted 2001-06-05; US term expired 2017-06-13 (20 years from filing, post-1995 regime); CA expired 2018-06-12 (20 years from CA filing); all prior-art references pre-date the 1997-06-13 filing (US513271 1894; US1469472 1923; US4762303 1988; US5255575 1993; US5787676 filed 1997-03-18); no "before [wrong date]" phrasing.
- P-09-002/003: structural constraints verified in the compiled report (see `report-us5850650-e2e-v16.md`).

---

## Ledger totals

- **Total propositions registered:** 46
- **Propositions with gate record:** 46 (100%)
- **ESTABLISHED (CONFIRMED PRESENT):** 27
- **ESTABLISHED (analytical conclusions):** 7 (P-05-007, P-05-012, P-07-005, P-08-006, P-09-001, P-09-002, P-09-003)
- **EXCLUDED (unestablished, in Operational Audit):** 12 (P-02-004, P-03-003, P-03-004b, P-03-005, P-03-006, P-04-002, P-05-009, P-05-010, P-05-011, P-06-005, P-07-001, P-08-005) — counted at proposition level; P-03-007 candidate set and P-05-008 partial entries are work-layer records, not findings.

**Invariant checks:**
- No proposition carries legacy evidence states (NOT OBSERVED / NOT IDENTIFIED / INFERRED / NOT EVALUATED / CONTESTED / UNRESOLVED).
- No proposition has `work_state: BLOCKED` (BLOCKED is avenue-level only) — verified: all BLOCKED dispositions appear in avenue records, never in proposition rows.
- No proposition has `status: EXHAUSTED` at avenue level — verified: EXHAUSTED appears only at proposition level.
- Every EXCLUDED proposition has a corresponding avenue ladder in the Avenue Ledger.