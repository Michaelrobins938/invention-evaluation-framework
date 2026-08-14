# Negative-Control Test — Tesla US433,700 v1.6 Validation Run

**Framework version:** v1.6 (Evidence Sufficiency Architecture)
**Run date:** 2026-08-14
**Test purpose:** Inject five malformed propositions into the pipeline. All five MUST fail the Evidence Sufficiency Gate and be dispositioned EXCLUDED. Any injection that passes the gate is a framework defect.

**Test rule:** An injected proposition passes the gate only if it satisfies its schema's required fields, carries source identity, and (for negatives) defines a bounded universe with a sufficiency test. All five injections below are designed to fail at least one of these requirements.

---

## Injection 1 — "Various SBIR awards for spray cooling in military applications"

**Target schema:** `market_relevance_award`

| Gate check | Result |
|---|---|
| Schema required fields: agency, award_id, recipient, award_date, title, url, relevant_passage, independence_lineage_id (min 2) | FAIL — "Various SBIR awards" provides no award_id, no agency, no recipient, no award_date, no title, no url, no relevant_passage, no independence_lineage_id |
| Source identity | FAIL — no source for any specific award |
| Row non-existence | FAIL — no schema row can be constructed |

**Disposition:** EXCLUDED (row non-existence; schema fields absent). The phrase "Various SBIR awards" is a category claim, not an evidence record.

---

## Injection 2 — "NAICS 334419 – inferred"

**Target schema:** `naics_classification`

| Gate check | Result |
|---|---|
| Schema required fields: taxonomy_source, code, official_title, edition_year, basis | FAIL — no taxonomy_source, no official_title, no edition_year; "inferred" is not a valid basis |
| Source identity | FAIL — no taxonomy record |
| Basis validity | FAIL — "inferred" is a legacy analytical label, not an evidence basis |

**Disposition:** EXCLUDED (schema fields absent; invalid basis). No code is reported.

---

## Injection 3 — "Research on spray cooling for UAVs and military applications"

**Target schema:** `literature_disclosure`

| Gate check | Result |
|---|---|
| Schema required fields: authors, title, venue, date, DOI/report no., URL, experimental system, demonstrated result | FAIL — no authors, no title, no venue, no date, no DOI, no URL, no experimental system, no demonstrated result |
| Source identity | FAIL — no publication identity |
| Relevance to invention | FAIL — no link to the interposed-shield mechanism |

**Disposition:** EXCLUDED (row non-existence; no publication identity; no demonstrated result).

---

## Injection 4 — "No international equivalents found."

**Target schema:** (negative landscape finding)

| Gate check | Result |
|---|---|
| Bounded universe | FAIL — no bounded universe defined ("found" implies a search, not a universe) |
| absence_basis | FAIL — no absence_basis recorded |
| Sufficiency test | FAIL — no sufficiency test |
| Corroboration | FAIL — single-source search statement |

**Disposition:** EXCLUDED. This is a search-result statement (avenue metadata), not evidence. Compare with the legitimate treatment in the run: P-04-002 was dispositioned EXCLUDED with `barrier_type: insufficient_corroboration` because the corroboration avenue (Espacenet) was BLOCKED — the injection is even weaker (no bounded universe at all).

---

## Injection 5 — "Commercial adoption not observed."

**Target schema:** `commercial_adoption`

| Gate check | Result |
|---|---|
| Schema required fields: product_identity_link, source, date, independence_lineage_id (min 2) | FAIL — no product_identity_link, no source, no date, no independence_lineage_id |
| Prohibited language | FAIL — "not observed" is legacy evidence-state language (NOT OBSERVED), prohibited in factual findings |
| Negative-claim requirements | FAIL — no bounded universe, no absence_basis |

**Disposition:** EXCLUDED. "Not observed" is a search-result statement, not evidence. The legitimate treatment in the run: P-07-001 was dispositioned EXCLUDED with the report language "Commercial adoption could not be established from the completed evidence protocol."

---

## Test result

| Injection | Gate result | Disposition | Pass/Fail |
|---|---|---|---|
| 1. "Various SBIR awards…" | FAIL (row non-existence) | EXCLUDED | PASS |
| 2. "NAICS 334419 – inferred" | FAIL (schema fields; invalid basis) | EXCLUDED | PASS |
| 3. "Research on spray cooling for UAVs…" | FAIL (no publication identity) | EXCLUDED | PASS |
| 4. "No international equivalents found." | FAIL (no bounded universe) | EXCLUDED | PASS |
| 5. "Commercial adoption not observed." | FAIL (prohibited language; no product identity) | EXCLUDED | PASS |

**All 5 injections FAILED the Evidence Sufficiency Gate and were dispositioned EXCLUDED. No injection became a finding. Negative-control test: PASS.**

**Framework defect check:** None. The gate rejected all five malformed propositions on schema-field, source-identity, bounded-universe, and language grounds — exactly as designed.