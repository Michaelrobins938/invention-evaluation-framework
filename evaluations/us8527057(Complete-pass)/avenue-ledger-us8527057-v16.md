# Avenue Ledger — US8527057 v1.6 Run

**Run date:** 2026-08-15  
**Submission:** `submission-us8527057.md`  
**Rule:** EXHAUSTED is a work-layer termination state, not evidence.

| Proposition | Required avenue coverage | Disposition | Barrier / note |
|---|---|---|---|
| P-02-001 disclosure history | primary record COMPLETE; terminology COMPLETE; jurisdiction COMPLETE; independent corroboration BLOCKED | EXHAUSTED → excluded | No inventor statement or complete personal disclosure records. |
| P-03-001 performance data | patent COMPLETE; citation expansion COMPLETE; terminology COMPLETE; alternate engineering databases BLOCKED; independent corroboration BLOCKED | EXHAUSTED → excluded | No reconstructable comparative performance data. |
| P-03-002 regulatory pathway | FDA primary COMPLETE; classification-specific pathway BLOCKED; independent regulatory confirmation BLOCKED | EXHAUSTED → excluded | Scope-level burden only; product-specific pathway not established. |
| P-04-004 quantitative landscape | Google Patents COMPLETE; USPTO CPC COMPLETE; alternate database BLOCKED; independent corroboration BLOCKED | SEARCHING → analytical work item | Directional counts now established from Google Patents; second-source family/assignee normalization remains. |
| P-05-001 anticipation | target patent COMPLETE; cited references COMPLETE; classification search COMPLETE; alternate database BLOCKED; independent corroboration BLOCKED | EXHAUSTED → excluded | No final anticipation finding from incomplete external search. |
| P-05-002 obviousness bridge | target/sibling records COMPLETE; analogous references COMPLETE; motivation inferred/analogous; independent corroboration BLOCKED | EXHAUSTED → analytical work item | Partially grounded bridge; no ultimate legal conclusion. |
| P-06-001 literature application disclosure | PubMed COMPLETE; adjacent literature COMPLETE; engineering database BLOCKED; independent corroboration BLOCKED | EXHAUSTED → excluded | Background confirmed; complete package application not established. |
| P-07-001 market size | public health sources COMPLETE; market database BLOCKED; independent corroboration BLOCKED | EXHAUSTED → excluded | No reconstructable quantitative figure. |
| P-07-002 commercial adoption | PubMed/NEI COMPLETE; product-identity link BLOCKED; independent corroboration BLOCKED | EXHAUSTED → excluded | Field activity established; embodiment of this patent not established. |
| P-08-001 partner fit | patent assignment COMPLETE; company/clinical need verification BLOCKED | SEARCHING → operational audit | Candidate pathways require current diligence. |

## Landscape & Market Data classification gate

| Subsection | Classification-in | Classification-verified | Query/source | Result | Disposition |
|---|---|---|---|---|---|
| Patent applications by region | Patent front page: A61N 1/18; USPC 607/54 | A61N title checked against USPTO CPC scheme; thematic match; query narrowed to A61N1/0543 + retinal | Google Patents XHR, same query by country: US/WO/EP/CN/JP/AU/CA | 492 / 318 / 261 / 127 / 100 / 105 / 58 publication records | COMPLETE — counts are records, not deduplicated families |
| Patent applications by main applicants | Patent front page: A61N 1/18; USPC 607/54 | Same verified CPC and keyword gate | Google Patents XHR `country=US&q=A61N1/0543 retinal` | 492 results; top returned applicants: Second Sight 160, Nidek 42, Pixium 32, Cochlear 28, USC 25 | COMPLETE — names not merged across corporate variants |
| Patent activity trend | Patent front page: A61N 1/18; USPC 607/54 | Same verified CPC and keyword gate | Same Google Patents XHR summary frequency buckets | 2016–19: 64; 2019–22: 43; 2022–25: 38; 2025–28: 5 | COMPLETE — three-year buckets, not annual deduplicated filings |
| Industry metrics | Patent front page: A61N 1/18; USPC 607/54; candidate NAICS 334510 | CPC match passed; NAICS 334510 selected as electromedical/electrotherapeutic apparatus manufacturing; Census downloadable CBP record used | Census CBP 2022 `https://www2.census.gov/programs-surveys/cbp/datasets/2022/cbp22us.zip`, row `naics=334510,lfo=-` | 923 establishments; 92,285 employees; annual payroll 10,030,531 thousand dollars | COMPLETE — payroll, not revenue or shipment value; no unsupported revenue substitution |
| Employee-size brackets | Candidate NAICS 334510 | Same verified industry code and downloadable CBP source | Same CBP row; n-fields by employee-size bracket | Establishments: <5 299; 5–9 135; 10–19 102; 20–49 120; 50–99 87; 100–249 83; 250–499 50; 500–999 29; 1000+ 18 | COMPLETE |

The renderer must not substitute B25D, NAICS 332216, or any other unrelated class.
