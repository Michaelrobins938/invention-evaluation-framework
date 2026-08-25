# Acceptance-Contract Pattern

**Turn a client/researcher specification into an executable quality boundary.**

This is a reusable framework pattern, not a one-off. First exercised by the
GenIP market-only specification (see `market-report-generator/`); any future
deliverable class with an external specification should follow the same path.

## Principle

A specification that lives only as prose is enforced by whoever remembers it.
A specification encoded as an acceptance contract is enforced by the pipeline,
against **generated artifacts**, before anything ships.

> The LLM can generate the content. The contract determines whether the
> content survives.

## Procedure

1. **Inventory the specification.** Extract every requirement as a FAIL-if
   statement ("FAIL if: literal `**` remains in DOCX text"). Prose adjectives
   ("professional", "readable") become measurable thresholds (body ≥10.5 pt)
   or are explicitly deferred to visual QA with a checklist item.
2. **Build the validator against artifacts, not intent.** The validator reads
   what generation *produced* (DOCX XML, tables, sidecar files, manifest) —
   never the generator's own claims about itself. A correct generator with a
   broken renderer must fail.
3. **Gate the pipeline.** Validator exit code decides ship/regenerate. The
   per-criterion verdict is written into the run directory as evidence
   (`acceptance-report-*.json`) so acceptance is auditable without trusting
   the developer.
4. **Mutation-test the contract.** For every known defect class, inject it
   deliberately and prove the validator rejects it. Negative tests are the
   specification-to-enforcement traceability record; a contract without them
   is untested belief.
5. **Freeze the source specification.** Keep the client's original text dated
   and immutable (e.g., in the run ledger); living documents may restate it,
   history must not be rewritten.

## Rules

- Validate artifacts → not source data, not generator return values.
- Every check has an id, pass/fail, and a human-readable detail line.
- Aggregate verdict + per-criterion records both persist with the run.
- Restricted mission profiles (e.g., market-only) enforce their boundaries
  mechanically via prohibited-language/entity scans — a restricted deliverable
  cannot silently inherit conclusions from the general pipeline.
- Dated client specifications are contracts: version increments require a new
  contract version, never silent edits.

## Reference implementation

| Component | Location |
|---|---|
| Contract (~34 checks, 10 domains) | `market-report-generator/validate_acceptance.py` |
| Mutation/negative tests | `tests/test_market_acceptance.py` |
| Pipeline wiring (ship gate) | `market-report-generator/run-regeneration.ps1` |
| Frozen client specification | `market-report-generator/execution-ledger-8530-market-only-run4.md` |
