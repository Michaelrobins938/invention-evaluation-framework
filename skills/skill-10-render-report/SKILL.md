---
name: render-report
description: Renders the compiled invention evaluation report into the branded "inventionevaluator" format — styled HTML plus a print-ready A4 PDF with a clean sample-faithful cover page (wordmark, metadata block, legal text, disclaimer box — no header band, no icon cluster), table of contents with accurate physical page numbers, running footer with page counters, CONFIDENTIAL watermark, gauges, SWOT, section dividers, and search boxes. This is a mandatory pipeline phase: EVERY end-to-end run produces this styled report as its final deliverable. Use after compile-report at the end of every evaluation run, or whenever the user asks for the styled/final PDF deliverable. Do not use this skill to analyze or summarize the invention — it only formats what skill-09 already compiled.
---

# Render Report (Phase 10)

## v1.7 Run Contract

Every phase inherits the active `run_id`, canonical `evaluation_dir`, `phase status`, proposition identity/version, `execution ledger`, `Evidence Sufficiency Gate`, and `Failure Recovery Contract`. Artifact ingestion is not proof that a phase executed. Terminal states require execution-backed records and validated hand-off artifacts.

## When to use
- End of every evaluation run — after skill-09 compile-report has produced the report MD.
- "Generate the branded/PDF report." / "I want the final styled deliverable."

## When NOT to use
- The report MD doesn't exist yet — run compile-report first; never render an unfinished report.

## Execution

**Governing principle:** The renderer is a presentation layer only. It must never invent
metrics, findings, or evidence. Every gauge/bar/chart value comes from the per-run scores
manifest, and each score must carry a `basis` proposition_id from the proposition ledger.
Charts whose data was not established render labeled placeholder frames — never fabricated
series.

1. Confirm the inputs exist:
   - compiled report MD (skill-09 output, e.g. `report-<id>-e2e-v16.md`)
   - avenue ledger MD (`avenue-ledger-<id>-v16.md`)
   - scores manifest JSON (`scores-<id>.json`)
   - submission record MD (Appendix C, optional but recommended)
   - resolved run directory from the artifact-destination gate; rendering to a
     temporary directory or only returning HTML in chat does not satisfy delivery.
2. Run the renderer:
   ```bash
   python3 invention-evaluation-engine/report-renderer/render_report.py \
       --report  evaluations/<id>/report-<id>-e2e-v16.md \
       --ledger  evaluations/<id>/avenue-ledger-<id>-v16.md \
       --scores  evaluations/<id>/scores-<id>.json \
       --submission evaluations/<id>/submission-<id>.md \
       --out evaluations/<id>/report-<id>-e2e-v16.html \
       --pdf
   ```
   `--pdf` triggers the two-pass render: pass 1 embeds invisible `TOCMARK:<sid>`
   markers and prints to PDF; the renderer scans the printed PDF with `pdftotext`
   to learn each section's real physical page; pass 2 fills the TOC page numbers
   and prints the final PDF with markers stripped.
3. Verify the output (mandatory, do not skip). Every item below must be checked
   programmatically — "spot-check a few pages" is not sufficient; the bugs this
   checklist exists to catch (see "Known failure modes") are systematic and hit
   every page identically, so a script check on all pages is cheap and a manual
   spot-check on a few pages will reliably miss them:
   - `pdfinfo report-<id>-e2e-v16.pdf` → A4 (≈595×842 pts).
   - **Footer regex, every page, no exceptions:** run `pdftotext -f <n> -l <n>`
     for every physical page and assert the footer line matches
     `^IEAUS \d[\d,]*: .+\. Submitted \d{4}-\d{2}-\d{2}\. Report \d{4}-\d{2}-\d{2}\.$`
     exactly (submitted/report dates as clean 10-character ISO strings, no stray
     digits spliced in) followed by `Page <n>` as a separate token. If any page's
     footer date string is not exactly 10 characters, or contains a digit that
     doesn't belong to the ISO date, the two footer margin boxes are colliding —
     see Known failure modes #1.
   - **Watermark regex, every page:** assert the extracted watermark text is
     exactly `CONFIDENTIAL` (13 characters) on every page, not a truncated
     variant. A watermark missing its first and/or last character indicates a
     clipping ancestor — see Known failure modes #2.
   - TOC page numbers equal the physical pages where each section divider
     actually lands (verify against the printed PDF for every TOC entry, not a
     sample).
   - No `TOCMARK` strings remain in the final PDF or HTML (`pdftotext ... | grep -c TOCMARK` → 0).
   - Gauge/bar labels match the scores manifest tier labels; placeholder frames appear only where the manifest has no data.
   - **Gauge text layer:** gauge scale endpoints are horizontal text runs
     (`Very Limited` / `Strong`); do not rotate per-tier labels onto an arc —
     rotated SVG text scrambles in `pdftotext` extraction and breaks the
     gauge-labels verification.
   - **Chart geometry:** for every `<svg>` containing more than one independent
     data series (e.g. two pie charts), confirm each series has its own `<svg>`/
     viewBox rather than sharing coordinate space with another series. Compute
     each series' painted bounding box and confirm no two series' boxes overlap.
     Two unrelated pies packed into one viewBox will clip each other's labels —
     see Known failure modes #4.
- **Cover fits on exactly one page:** the cover must not spill onto page 2.
     Assert page 2 starts with the first TOC/section content (e.g. `TABLE OF
     CONTENTS` or `EXECUTIVE SUMMARY`), and assert the disclaimer/legal block's
     lowest text baseline sits above the footer band (≈y781pt on A4). The cover
     wordmark and the metadata block occupy separate vertical bands, so no
     wordmark-length-dependent collision is possible — see Known failure modes #3.
4. Deliverables: the styled HTML and the A4 PDF are the final report. Archive both in `evaluations/<id>/`.
   Return their absolute paths and verify both files exist and are non-empty before
   claiming the run is complete.

## Known failure modes (regression list — check these explicitly, they recur)

These four bugs were found together in one production render (v16, US5850650) and
all four are systemic — they reproduce on every page or every instance of the
pattern, not intermittently, and a checklist that says "verify" without saying
*how* will pass a broken render:

1. **Footer margin-box collision.** The CSS `@page { @bottom-left {...} @bottom-right {...} }`
   boxes share the page's content width. If `@bottom-left`'s `max-width` leaves
   less than ~0.5in clearance for `@bottom-right`'s page number, the two boxes'
   painted text collides, and `pdftotext` (reading by physical glyph position)
   linearizes the overlap by splicing the page-number digit into the middle of
   the date string (`2026-08-14` → `2026-08-114`). Fix: keep `@bottom-left`
   `max-width` at least ~1in short of the page content width, and give
   `@bottom-right` explicit `white-space:nowrap` plus a label (`"Page " counter(page)`)
   so a collision is visually obvious even if the regex check is skipped.
2. **Watermark clipped by an ancestor's `overflow-x:clip`/`hidden`.** A
   `position:fixed` decorative element (the CONFIDENTIAL watermark) is centered
   via `top:50%;left:50%;transform:translate(-50%,-50%) rotate(...)`. Its
   *unrotated* footprint (inflated by large `letter-spacing` at a large
   `font-size`) can exceed the page's content width even though the rotated
   visual footprint looks fine. If any ancestor between it and the page root has
   `overflow-x:clip` or `overflow:hidden`, both edges get clipped symmetrically
   — dropping the first and last character on every single page (`CONFIDENTIAL`
   → `ONFIDENTIA`). Fix: scope any horizontal overflow-clipping to the page
*content* wrapper only, never to `html`/`body`, since fixed-position chrome
    (the watermark) is a descendant of `body` and inherits that clip.
   Keep the watermark's raw text run comfortably narrower than the page anyway,
   as a second line of defense.
3. **Cover vertical overflow.** Cover content (metadata block, legal text,
   disclaimer) that runs too deep pushes the disclaimer onto page 2, turning
   a one-page cover into a two-page one and offsetting every TOC page number.
   Fix: keep the cover's vertical rhythm compact — metadata block at ≈4.75in
   from the page top (16pt rows, slim margins), legal + disclaimer as plain
   compact text (no box) ending above the footer band (≈y781pt on A4). Verify
   page 2 begins with TOC/section content, never cover content.
4. **Two data series sharing one SVG viewBox.** A second, smaller pie chart
   (e.g. a competitive sub-breakdown) drawn inside the same `<svg>` as an
   unrelated larger pie chart, positioned in a corner "to save space," will
   clip whichever labels of the first chart fall in that corner. Two distinct
   questions (e.g. "top assignees across the whole class" vs. "share among
   framing-hammer-specific brands") are also usually different, non-additive
   denominators and should not be visually implied to be one chart's subset.
   Fix: give each independent series its own `chart-frame`/`<svg>`, sized to
   the page's normal chart width, not squeezed into a corner of another chart.

## Typographic reference (sample-faithful scale)

The branded template reproduces the reference sample's typography:
- Section headings: ~28pt display font, bold, left-aligned, no forced
  uppercase (render the report's own heading case; strip any auto number prefix).
- Sub-headings: ~15pt; body text: ~11.5pt; tables: ~10.5pt.
- TOC entries: ~12pt with dotted leaders and right-aligned page numbers.
- Cover metadata: ~16-18pt, rows ~22pt apart, block starting ≈y540 on A4.
- Cover legal + demo disclaimer: small plain text (~7pt), no box, ending above
  the footer band.

## Quality checklist (all must pass before delivery)
- [ ] PDF is A4 with correct physical page numbers in the footer on every page (cover = 1).
- [ ] Footer date strings are clean 10-character ISO dates on every page — no digits spliced in from the page-number box (Known failure mode #1).
- [ ] Watermark reads exactly "CONFIDENTIAL" (not truncated) on every page (Known failure mode #2).
- [ ] Cover fits on exactly one page — page 2 begins with TOC/section content, and cover content (metadata, legal, disclaimer) ends above the footer band (Known failure mode #3).
- [ ] Every multi-series chart uses one `<svg>`/viewBox per series; no two series' bounding boxes overlap (Known failure mode #4).
- [ ] TOC page numbers match actual section pages (verified against the printed PDF for every entry, not guessed).
- [ ] No renderer-invented metrics: every displayed score exists in the scores manifest with a basis proposition_id.
- [ ] Charts with unestablished data show labeled placeholder frames, never fabricated series.
- [ ] No TOCMARK artifacts in the final HTML/PDF.
- [ ] No legacy evidence states (NOT OBSERVED / INFERRED / UNRESOLVED / NOT IDENTIFIED / CONTESTED) introduced in rendering.
- [ ] The report carries the "not legal advice" disclaimer from the compiled report.

## Boundary
- Formats only — generates no new analysis, no new scores, no new findings.
- If a scores manifest value is missing, the renderer falls back to a labeled placeholder; do not hand-edit the HTML to add numbers that are not in the manifest.
- Layout/CSS fixes (footer spacing, clip scoping, chart placement) are presentation-layer and are fair game to hand-edit or patch in `render_report.py`'s template — that's different from hand-editing in a *number* that isn't in the manifest.
## Landscape & Market Data integrity gate

Before delivery, compare every CPC/NAICS code appearing in the rendered Landscape &
Market Data section with the classification recorded on the patent front page and in
Appendix C. Any mismatch blocks delivery. A placeholder is valid only when the avenue
ledger shows the exact query, source, result count, and rejection reason for an attempted
pull; an unattempted subsection is a pipeline defect. The renderer must never contain a
domain-specific fallback number or classification.
