# Evaluations Directory

One folder per evaluated invention. Two kinds of content live here:

## 1. Live runs (produced by the pipeline)

| Path pattern | Produced by | Contents |
|---|---|---|
| `<id>/` | intake + phase workers | `submission-<id>.md`, phase artifacts, `source/` originals |
| `<id>-output/` | full pipeline run | ~29 structured artifacts: report `.md/.html/.pdf`, execution ledger, proposition ledger, epistemic gate report, combined status, scores manifest |

## 2. Validation fixtures (checked into the repo deliberately)

Named after the patent they validate, with outcome in the name where relevant:

- `us8527057/` — primary validation case (9 lanes, 5/5 proposition reviews)
- `us8527057(Complete-pass)/`, `us8905955(Incomplete-fail)/` — deliberate pass/fail fixtures used by the regression suites
- Numeric dirs (`7149534/`, `7153242/`, …) — additional real evaluation cases

**Do not rename fixture directories**: tests and README links reference exact paths.

## Conventions

- Source documents are preserved under `<id>/source/` with hashes recorded per-run; never edited.
- Raw scraped artifacts (`raw-*.{html,bin}`) inside live runs are gitignored.
- New client-specified market reports follow the GenIP pipeline — see
  [`market-report-generator/`](../market-report-generator/) — and land in
  `<id>-market-only-run<N>/` together with their acceptance report.
