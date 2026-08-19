# v1.7 Evidence Recovery Record — US8527057

## Patent-family archaeology

- `US7881799B2` is the parent record for the target divisional.
- Google Patents lists the parent as active with adjusted expiration 2028-03-14.
- The family record shows priority to `US8527057B2` and assignment events from Second
  Sight Medical Products to Vivani Medical in 2022 and Vivani to Cortigent in 2023.
- Target `US8527057B2` is recorded separately as expired for maintenance-fee nonpayment.

Sources:

- https://patents.google.com/patent/US7881799B2/en
- https://patents.google.com/patent/US8527057B2/en

## Close pre-critical-date references

### US20050222624A1 — Retinal prosthesis with side mounted inductive coil

- Priority: 2004-04-06, before the target's 2005-04-28 priority date.
- Subject matter: retinal electrode array, side-mounted secondary inductive coil,
  scleral strap, lateral placement, external inductive coupling, surgical handling
  features, and flexible cable arrangements.
- Status: close technical-lineage reference; no complete claim-1 anticipation finding
  is admitted because the reviewed record does not establish the target's full hermetic
  flip-chip package and all claimed relationships in one qualifying reference.

Source: https://patents.google.com/patent/US20050222624A1/en

### US20030158588A1 — Minimally invasive retinal prosthesis

- Priority: 2002-01-17.
- Subject matter: minimally invasive retinal prosthesis, external electronics/coils,
  flexible ocular geometry, and surgical placement constraints.
- Role: domain-level coverage and technical context; not a complete anticipation mapping.

Source: https://patents.google.com/patent/US20030158588A1/en

### US20030097166A1 — Flexible electrode array for artificial vision

- Priority: 2001-11-16.
- Subject matter: flexible/stretchable retinal electrode arrays, conductive leads,
  polymer substrates, embedded electrodes, manufacturing, and flip-chip attachment.
- Role: product/process-domain coverage; not a complete anticipation mapping.

Source: https://patents.google.com/patent/US20030097166A1/en

## Product and regulatory breadcrumb

FDA HDE H110002 identifies:

- Trade name: ARGUS II RETINAL PROSTHESIS SYSTEM.
- Applicant: Cortigent, Inc.
- Decision date: 2013-02-13.
- Product code: NBF, prosthesis retinal.
- Clinical trial: NCT00407602.
- Indication: adults age 25 or older with severe-to-profound retinitis pigmentosa,
  subject to light-perception, prior useful-vision, lens-status, follow-up, fitting,
  and rehabilitation criteria.

Source: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfHDE/hde.cfm?id=H110002

## Clinical history breadcrumb

ClinicalTrials.gov search results for “Argus II” identify:

| Study | Status | Relevance |
|---|---|---|
| NCT00407602 | COMPLETED | Argus II feasibility protocol |
| NCT01860092 | TERMINATED | New-enrollment post-approval study |
| NCT01490827 | TERMINATED | Argus II post-market surveillance |
| NCT02303288 | COMPLETED | France post-market study |
| NCT04359108 | COMPLETED | Environmental localization mapping for visual-prosthesis users |

Source: https://clinicaltrials.gov/api/v2/studies?query.term=Argus%20II&pageSize=20

## Remaining recovery work

- Map US8527057 claim limitations against the Argus II product and FDA device records.
- Retrieve examiner/applicant citations and prosecution history for the parent/divisional
  family.
- Reconstruct all continuation, divisional, foreign, and surviving family rights.
- Build a bounded patient/procedure/reimbursement model rather than a generic industry
  proxy alone.
- Determine whether commercialization failure, reimbursement, regulatory constraints,
  product economics, or business-model factors drove the post-market outcome.

## Bounded patient-population model

PubMed review PMID 29597005 reports worldwide retinitis-pigmentosa prevalence of
approximately 1:4,000. The model therefore begins with:

```text
Population with RP ≈ reference population ÷ 4,000
Potential severe/profound candidates = RP population × eligibility fraction
Addressable implants = eligible candidates × diagnosis/access/consent fraction
Economic opportunity = addressable implants × device/procedure economics
```

The FDA HDE record supplies the eligibility constraints, but the eligible fraction,
diagnosis/access fraction, device price, procedure reimbursement, and adoption rate are
not established. The model is therefore a recovery scaffold and sensitivity framework,
not a TAM/SAM/SOM claim.

Source: https://pubmed.ncbi.nlm.nih.gov/29597005/
