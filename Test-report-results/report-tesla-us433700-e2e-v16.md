# Invention Evaluation Report — Tesla US433,700 (v1.6)

**Framework version:** v1.6 (Evidence Sufficiency Architecture)
**Submission:** `invention-evaluation-engine/examples/tesla-us433700/submission.md`
**Report date:** 2026-08-14
**Report ID:** report-tesla-us433700-e2e-v16

---

## Executive Summary

This report evaluates US Patent 433,700, "Electro-Magnetic Motor," granted to Nikola Tesla on August 5, 1890 (filed March 26, 1890, Serial No. 345,388; assigned to the Tesla Electric Company). The invention is a two-circuit alternating-current motor in which the phase difference between the energizing circuits is produced by the retarding effect of an interposed magnetic shield on one circuit.

**Established findings (evidence-backed):**

1. US433,700 claims a two-circuit AC motor in which an interposed magnetic shield retards the magnetization of one circuit, producing the phase difference required for rotation (Claim 1, limitations (a)–(e)).
2. No single identified prior-art reference anticipates Claim 1. US424,036 (granted March 25, 1890, one day before filing) discloses the retarding-magnetization principle (limitation (e)) but not the two-energizing-circuits arrangement (limitation (b)) nor the interposed-shield structure (limitation (d)). US416,195 discloses the two-energizing-circuits arrangement (limitation (b)) but not the interposed-shield structure (limitation (d)) nor the retarding-magnetization principle (limitation (e)).
3. The component knowledge (two-circuit motors), the principle (magnetic saturation and lag), and the function (phase difference) were all known before 1890. The combination of an interposed saturable shield as the phase-control mechanism, and its application, could not be established from the completed evidence protocol.
4. The motivation proposition for the interposed-shield implementation is only partially grounded (analogous sources only); the obviousness proposition could not be established and is excluded from factual findings.
5. Commercial adoption could not be established from the completed evidence protocol. No manufacturer was identified as embodying the shield mechanism in production motors.
6. Westinghouse Electric & Manufacturing Company is the strongest identified commercialization pathway, holding Tesla's core AC patents via the 1888 licensing deal and selling AC power systems.

**Analytical conclusions (inference from established findings, never evidence):**

- The anticipation gate resolves to NOT ANTICIPATED by any identified reference.
- The mechanism/design-choice distances (C2/D3 vs US424,036; C3/D3 vs US416,195) characterize the invention as a material-dynamics design choice within a known design space, assessed per pathway and never combined.
- The invention sits at the material-dynamics corner of Tesla's phase-control design-space exploration (sibling filings US433,701, US433,702 filed the same day).
- Commercial actionability is Moderate (market size medium × growth high-qualitative × accessibility medium × competitive intensity medium).

**Operational Audit (unestablished propositions, with barrier types):**

The following propositions could not be established from the completed evidence protocol and are excluded from factual findings. Each is recorded with its barrier type:

| Proposition | Barrier type |
|---|---|
| No public disclosure of the shield mechanism before filing | insufficient_search_completion |
| No quantitative performance data exists | insufficient_technical_demonstration |
| No regulatory regime governed electric motors in 1890 | insufficient_search_completion |
| Prototype evidence | insufficient_search_completion |
| Production evidence | insufficient_search_completion |
| No international patent family for US433,700 | insufficient_corroboration |
| No assignees other than Tesla in the pre-1890 phase-control space | insufficient_search_completion |
| Motivation proposition (PARTIALLY GROUNDED, analogous only) | insufficient_search_completion |
| Obviousness proposition | insufficient_search_completion |
| Unexpected-result proposition | insufficient_technical_demonstration |
| No pre-filing non-patent publication discloses the shield mechanism | source_unavailable |
| Commercial adoption | insufficient_search_completion |
| Market sizing (1890 revenue / AC-motor CAGR) | source_unavailable |
| NAICS classification | insufficient_identity |
| Market relevance (government awards) | insufficient_search_completion |
| No other viable commercialization pathway exists | insufficient_identity |

---

## 1. Established Findings

Established findings are propositions that passed the Evidence Sufficiency Gate. Each carries a proposition_id, source identity, and (for absences) a bounded universe.

### 1.1 Submission and chronology

| proposition_id | Finding | Source identity |
|---|---|---|
| P-02-001 | US433,700 was filed March 26, 1890 (Serial No. 345,388) | Patent specification header, Google Patents US433700A |
| P-02-002 | US433,700 was granted August 5, 1890 | Patent specification header, Google Patents US433700A |
| P-02-003 | US433,700 was assigned to the Tesla Electric Company | Patent specification header ("ASSIGNOR TO THE TESLA ELECTRIC COMPANY") |
| P-02-005 | Tesla's May 16, 1888 AIEE paper disclosed the broader rotating-field system (not the shield mechanism) | AIEE lecture text, DOI 10.1109/T-AIEE.1888.5570379 |
| P-04-004 | US416,195 and US424,036 were filed the same day (1889-05-20) | Patent specification headers, Google Patents |
| P-04-005 | US433,700, US433,701, US433,702 were filed the same day (1890-03-26) | Patent specification headers, Google Patents |

### 1.2 Technology profile

| proposition_id | Finding | Source identity |
|---|---|---|
| P-03-001 | The patent specification discloses the interposed-shield mechanism (4 claims, full spec) | Google Patents US433700A full text |
| P-03-002 | The claimed mechanism is a material-level phase-control device (causal intervention point = magnetic saturation of an interposed shield) | Patent specification (shield "retards the current and retards the magnetization") |

### 1.3 Patent landscape

| proposition_id | Finding | Source identity |
|---|---|---|
| P-04-001 | Tesla's own filings dominated the pre-1890 AC phase-control landscape (8 patents identified) | Google Patents family/citation chains (US381,968; US382,279; US416,195; US424,036; US433,700; US433,701; US433,702; US433,703) |
| P-04-006 | Forward-citation counts: US433,700: 1; US433,702: 11–15; US381,968: 70+; US382,279: 21–28; US416,195: 3; US424,036: 2; US433,703: 1 | Google Patents Cited By sections (neutral historical signals, not patentability evidence) |

### 1.4 Novelty — prior-art disclosure mapping

| proposition_id | Finding | Source identity |
|---|---|---|
| P-05-001 | Claim 1 limitations (a)–(e) as constructed from the patent's actual claims | US433,700 claims, Google Patents |
| P-05-002 | US424,036 discloses limitation (e) "retarding magnetization" | US424,036 Claim 1 ("field-cores... constructed so as to exhibit the magnetic effect imparted to them after the fall or cessation of current impulse") |
| P-05-003 | US424,036 does not disclose limitation (b) "two energizing-circuits" | Bounded universe: US424,036 full text (claims + specification reviewed) |
| P-05-004 | US424,036 does not disclose limitation (d) "interposed magnetic shields" | Bounded universe: US424,036 full text |
| P-05-005 | US416,195 discloses limitation (b) "two energizing-circuits" | US416,195 claims, Google Patents |
| P-05-006 | US416,195 does not disclose limitation (d) "interposed magnetic shields" | Bounded universe: US416,195 full text |
| P-05-007 | US416,195 does not disclose limitation (e) "retarding magnetization" | Bounded universe: US416,195 full text |
| P-05-008 | US381,968 and US382,279 do not disclose limitations (d) or (e) | Bounded universe: each patent's full text |

### 1.5 Novelty — knowledge decomposition

| proposition_id | Finding | Source identity |
|---|---|---|
| P-05-010a | component_known: two-circuit motors known before 1890 | US416,195; US381,968 |
| P-05-010b | principle_known: magnetic saturation known before 1890 | General electromagnetic knowledge (contemporary texts) |
| P-05-010c | principle_known: magnetic lag known before 1890 | US424,036 |
| P-05-010d | function_known: phase difference known before 1890 | US416,195; US424,036 |

### 1.6 Literature

| proposition_id | Finding | Source identity |
|---|---|---|
| P-06-001 | Ferraris, "Electrodynamic rotations produced by means of alternate currents" (1888-03-11, Royal Academy of Sciences, Turin) | Ferraris publication record |
| P-06-002 | Tesla, "A New System of Alternate Current Motors and Transformers" (AIEE lecture 1888-05-16) | AIEE Transactions, DOI 10.1109/T-AIEE.1888.5570379 |
| P-06-003 | Baily (1879) first primitive induction motor; Dolivo-Dobrovolsky (1889) three-phase cage motor | Historical literature |
| P-06-004 | Rotating magnetic field theory was known before 1890 | Ferraris 1885/1888; Tesla 1888 |
| P-06-005 | Magnetic saturation of iron was known before 1890 | General electromagnetic knowledge |
| P-06-006 | Magnetic lag for motor operation was known before 1890 | US424,036 |

### 1.7 Market

| proposition_id | Finding | Source identity |
|---|---|---|
| P-07-005 | AC electrical infrastructure was expanding rapidly in the 1890s (War of the Currents) | Historical record (Westinghouse 1893 World's Fair contract; electrification historiography) |
| P-07-006 | Competitive landscape: Edison GE (DC), Westinghouse (AC, Tesla-licensed), Thomson-Houston | Historical record (company histories) |
| P-07-007 | Westinghouse held Tesla's core AC patents via the 1888 licensing deal | Historical record (Westinghouse business history) |
| P-07-008 | Tesla Electric Company was financially strained | Historical record |

### 1.8 Partners

| proposition_id | Finding | Source identity |
|---|---|---|
| P-08-001 | Westinghouse Electric & Manufacturing Company: sells AC power systems; buys motor improvements; technical need = phase-control improvements within its licensed Tesla system; invention mapping = shield improvement integrates into Westinghouse AC motor line | Historical record (Westinghouse business history; 1888 Tesla licensing deal) |
| P-08-004 | Thomson-Houston Electric: alternative AC system manufacturer; medium fit | Historical record (Thomson-Houston business history) |

---

## 2. Analytical Conclusions

Analytical conclusions are inferences drawn from established findings. They are never evidence. Each carries a premise map.

### 2.1 Anticipation gate

| proposition_id | Conclusion | Premise map | Rule applied |
|---|---|---|---|
| P-05-009 | NOT ANTICIPATED by any identified reference | P-05-002…P-05-008 (per-reference limitation mappings) | Anticipation gate: ALL limitations in a single reference → candidate; ANY missing → not anticipated |

**Reasoning:** Every identified reference misses at least one Claim 1 limitation. US424,036 misses (b) and (d); US416,195 misses (d) and (e); US381,968 and US382,279 miss (d) and (e). No single reference discloses the full combination.

### 2.2 Mechanism/design-choice distances

| proposition_id | Conclusion | Premise map | Rule applied |
|---|---|---|---|
| P-05-014 | C2/D3 vs US424,036; C3/D3 vs US416,195 (per pathway, never combined) | P-05-002…P-05-008, P-05-010 | C0–C4 / D0–D4 taxonomy, per pathway |

**Reasoning:** The interposed-shield mechanism is a material-dynamics design choice (C2/C3) within a known design space (D3). Distances are assessed per pathway and never combined into a single composite.

### 2.3 Design-space position

| proposition_id | Conclusion | Premise map | Rule applied |
|---|---|---|---|
| P-04-007 | US433,700 sits at the material-dynamics corner of Tesla's phase-control design-space exploration | P-04-001, P-04-004, P-04-005 | Design-space/sibling analysis |

**Reasoning:** Tesla filed US433,700/701/702 the same day (1890-03-26), exploring phase-control variants; US433,700 is the material-dynamics (shield) variant.

### 2.4 Commercial actionability

| proposition_id | Conclusion | Premise map | Rule applied |
|---|---|---|---|
| P-07-009 | Commercial actionability: Moderate (market size med × growth high-qualitative × accessibility med × competitive intensity med) | P-07-005…P-07-008 | Size × growth × accessibility × competitive intensity scoring |

**Reasoning:** Market size is medium (qualitative only — sizing could not be established); growth is high (qualitative); accessibility is medium (Westinghouse pathway identified); competitive intensity is medium (Edison GE DC, Thomson-Houston AC). No "low" scores → Moderate.

### 2.5 Partner prioritization

| proposition_id | Conclusion | Premise map | Rule applied |
|---|---|---|---|
| P-08-002 | Westinghouse is the strongest identified commercialization pathway | P-08-001, P-07-007 | Counterfactual-exclusivity audit (reformulated from "only partner") |

**Reasoning:** Westinghouse holds Tesla's core AC patents (1888 licensing), sells AC power systems, and has a technical need for phase-control improvements within its licensed system. The claim is "strongest identified pathway," not "only pathway" (see Operational Audit, P-08-003).

### 2.6 Chronology validator

| proposition_id | Conclusion | Premise map | Rule applied |
|---|---|---|---|
| P-09-001 | All dates consistent; US424,036 (granted 1890-03-25) is prior art; US433,702 (same-day filing) and US433,703 (post-filing) excluded | P-02-001, P-02-002, P-04-004, P-04-005 | Chronology validator |

**Reasoning:** US424,036 was granted one day before US433,700 was filed → prior art. US433,702 was filed the same day → not prior art. US433,703 was filed April 4, 1890 → post-filing, not prior art.

---

## 3. Operational Audit

The following propositions could not be established from the completed evidence protocol. They are excluded from factual findings. Each is recorded with its barrier type and avenue disposition summary. Full avenue ladders are in `avenue-ledger-v16.md`.

| proposition_id | Proposition | Barrier type | Avenue summary |
|---|---|---|---|
| P-02-004 | No public disclosure of the shield mechanism before filing | insufficient_search_completion | A1 COMPLETE (search-based absence); A5 BLOCKED (period full-text); A8 BLOCKED |
| P-03-003 | No quantitative performance data exists | insufficient_technical_demonstration | A1 COMPLETE; A5 BLOCKED; A8 BLOCKED |
| P-03-004 | No regulatory regime governed electric motors in 1890 | insufficient_search_completion | A1 COMPLETE; A5 BLOCKED (legal databases); A8 BLOCKED |
| P-03-005 | Prototype evidence | insufficient_search_completion | A1 COMPLETE; A5 BLOCKED; A6 BLOCKED (company records) |
| P-03-006 | Production evidence | insufficient_search_completion | A1 COMPLETE; A5 BLOCKED; A6 BLOCKED |
| P-04-002 | No international patent family for US433,700 | insufficient_corroboration | A1 COMPLETE (single source); A5 BLOCKED (Espacenet 403); A8 BLOCKED |
| P-04-003 | No assignees other than Tesla in the pre-1890 phase-control space | insufficient_search_completion | A1 COMPLETE; A5 BLOCKED (Espacenet/Derwent/PatBase) |
| P-05-011 | Motivation proposition (PARTIALLY GROUNDED, analogous only) | insufficient_search_completion | A1 COMPLETE (no direct source); A3 COMPLETE (analogous only) |
| P-05-012 | Obviousness proposition | insufficient_search_completion | Motivation not GROUNDED; application NOT ESTABLISHED; bridge EXHAUSTED |
| P-05-013 | Unexpected-result proposition | insufficient_technical_demonstration | A1 COMPLETE (no performance data) |
| P-06-007 | No pre-filing non-patent publication discloses the shield mechanism | source_unavailable | A1 COMPLETE; A5 BLOCKED (1888–1890 journal full-text) |
| P-07-001 | Commercial adoption | insufficient_search_completion | A1 COMPLETE (no product identity link); A6 BLOCKED (Westinghouse records) |
| P-07-002 | Market sizing (1890 revenue / AC-motor CAGR) | source_unavailable | A1 COMPLETE (no dataset); A5 BLOCKED |
| P-07-003 | NAICS classification | insufficient_identity | NAICS did not exist in 1890; no taxonomy record; no code reported |
| P-07-004 | Market relevance (government awards) | insufficient_search_completion | A1 COMPLETE (no award identities) |
| P-08-003 | No other viable commercialization pathway exists | insufficient_identity | Counterfactual-exclusivity; absence of alternatives not evidenced |

**Audit note:** The absence of a regulatory regime, the absence of an international family, and the absence of commercial adoption are negative claims. Under v1.6, negative claims require a bounded evidence universe and (where the schema requires) independent corroboration. None of these could be established from the completed evidence protocol; they are recorded here as unestablished propositions, not as findings.

---

## 4. Report constraints verification

| Constraint | Status |
|---|---|
| Executive Summary ⊆ Established Findings + Analytical Conclusions | PASS |
| No legacy evidence states (the five legacy-state labels) | PASS |
| No prohibited language in factual findings (all such language confined to Operational Audit) | PASS |
| No "Overall patentability" row | PASS |
| No orphan analytical conclusions (every conclusion has a premise map) | PASS |
| No proposition dispositioned EXHAUSTED with a REQUIRES_VERIFICATION avenue | PASS |
| Chronology validator passed | PASS |

---

*Report compiled per skill-09 (compile-report). Proposition and avenue ledgers: `proposition-ledger-v16.md`, `avenue-ledger-v16.md`. Negative-control test: `negative-control-v16.md`. Validation matrix: `validation-matrix-v16.md`.*