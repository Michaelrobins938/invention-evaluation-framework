# Report Renderer Sample-Fidelity Upgrade

**Status:** Approved design; implementation pending.
**Baseline:** `invention-evaluation-engine/report-renderer/template.html` and `render_report.py`.
**Reference:** `Sample Invention Evaluator Report (1).pdf`.

## 1. Goal

Bring the generated HTML and PDF report template to faithful visual and pagination
quality with the supplied Invention Evaluator sample. This is a presentation-layer
upgrade. The report markdown remains the source of truth, and the existing scoring,
evidence, and placeholder-chart contracts remain unchanged.

## 2. Scope

### In scope

- Reproduce the sample's blue-gray visual system, typography hierarchy, margins, and spacing.
- Recreate the repeating gray chevron header band and running footer.
- Restore the branded cover composition, metadata, legal text, disclaimer, and visual mark.
- Match the table-of-contents hierarchy and dotted leaders.
- Match executive-summary gauges, grouped bar charts, summary blocks, and continuation flow.
- Match section divider pages and large blue section headings.
- Improve table sizing, alternating fills, border treatment, repeated headers, and row flow.
- Preserve landscape and market sidebar layouts where represented by the sample.
- Control page breaks for charts, tables, searches, SWOT, original submission, and appendices.
- Eliminate blank or nearly blank pages caused by layout rules.
- Make only the smallest renderer changes needed to provide stable semantic hooks for the template.

### Out of scope

- Changing report findings, scores, evidence states, or section semantics.
- Adding unsupported metrics or chart data.
- Replacing the renderer with a static PDF background or rasterized document.
- Rewriting the report-generation pipeline outside the Phase 10 renderer.
- Modernizing the brand beyond what is needed for sample fidelity.

## 3. Design

### 3.1 Visual system

Use the sample's restrained palette: navy and medium blue for headings and structure,
gray for the repeating header field, pale blue for table/chart fills, dark gray for
body copy, and low-opacity gray for the diagonal `CONFIDENTIAL` watermark.

The wordmark and cover visual should be implemented as crisp HTML/CSS/SVG-compatible
elements so Chromium PDF output remains sharp without requiring an external asset.
The existing footer data remains dynamic and must continue to include the invention ID,
submitter, invention name, submitted date, report date, and physical page number.

### 3.2 Page architecture

The document will follow the sample's high-level sequence:

1. Cover page.
2. Table of contents.
3. Executive summary.
4. Section divider and analysis content pages.
5. Search and evidence tables.
6. Market and opportunity pages.
7. SWOT and partner pages.
8. Original submission.
9. Appendices.

Fixed header/footer elements must not overlap content. Page-level blocks should use
print-safe break rules and avoid combining excessive minimum heights with forced breaks.
Long sections may continue naturally, but headings, chart frames, search metadata, and
critical table structures should remain with the content they introduce.

### 3.3 Content components

- Cover: angled gray/white/blue composition, title, metadata, legal copy, and disclaimer.
- TOC: level-one and level-two entries with dotted leaders and aligned page numbers.
- Gauge panel: three evenly sized domains with six-tier visual scale and readable labels.
- Bar panel: three grouped bar charts with consistent axis, legend, and caption treatment.
- Summary block: pale-gray or pale-blue container with comfortable line length and bullet spacing.
- Tables: blue rules, pale-blue alternating rows, stable column widths, repeated headers, and controlled row splitting.
- Search blocks: bordered query/result summary followed by result tables or references.
- SWOT: four-quadrant visual with the centered commercial-opportunity label.
- Section dividers: large blue headings and controlled whitespace consistent with the sample.

All generated text remains escaped and all links remain functional in the HTML output.

### 3.4 Renderer boundary

Prefer CSS and template changes. If the existing renderer lacks a reliable hook for a
specific page component or break, add a minimal semantic class or wrapper in
`render_report.py`. Do not move report interpretation or scoring logic into the template.

## 4. Verification

Render a representative report in both HTML and PDF formats. Compare at minimum:

- Cover and table of contents.
- Executive summary.
- Technology analysis and tables.
- Landscape charts and patent activity pages.
- Search-result pages.
- Market analysis and SWOT.
- Potential partners.
- Original submission and appendices.

Verify that:

- No blank or nearly blank pages are introduced.
- Header and footer do not clip or overlap body content.
- Page counters remain accurate.
- Cover elements, watermark, charts, tables, and section headings are present.
- Long tables and paragraphs wrap without clipping or unusable narrow columns.
- Placeholder charts remain explicitly labeled and contain no invented data.
- Existing renderer tests and repository verification commands pass.

## 5. Acceptance criteria

The upgrade is complete when the generated report is recognizably the same document
family as the supplied sample in cover composition, typography, palette, recurring
chrome, component styling, section rhythm, and print pagination, while preserving the
existing report data and evidence contracts.
