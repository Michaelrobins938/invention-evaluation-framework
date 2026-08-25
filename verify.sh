#!/usr/bin/env bash
set -uo pipefail

# Invention Evaluation Engine — v1.8 install verifier
# Usage: ./verify.sh [--path /path/to/invention-evaluation-engine]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$SCRIPT_DIR"

if [ "${1:-}" = "--path" ]; then
  TARGET="${2:?--path requires a directory argument}"
fi

FAIL=0
check() {
  local desc="$1" file="$2"
  if [ -f "$file" ]; then
    echo "  [PASS] $desc"
  else
    echo "  [FAIL] $desc — missing: $file"
    FAIL=1
  fi
}

echo "Verifying invention-evaluation-engine at: $TARGET"
echo ""

check "engine SKILL.md" "$TARGET/skills/SKILL-Orchestrator.md"
check "sub-skill 01" "$TARGET/skills/skill-01-invention-evaluation-overview/SKILL.md"
check "sub-skill 02" "$TARGET/skills/skill-02-gather-invention-submission/SKILL.md"
check "sub-skill 03" "$TARGET/skills/skill-03-analyze-technology-fundamentals/SKILL.md"
check "sub-skill 04" "$TARGET/skills/skill-04-conduct-patent-landscape/SKILL.md"
check "sub-skill 05" "$TARGET/skills/skill-05-conduct-novelty-search/SKILL.md"
check "sub-skill 06" "$TARGET/skills/skill-06-conduct-literature-search/SKILL.md"
check "sub-skill 07" "$TARGET/skills/skill-07-analyze-market-opportunity/SKILL.md"
check "sub-skill 08" "$TARGET/skills/skill-08-identify-partners/SKILL.md"
check "sub-skill 09" "$TARGET/skills/skill-09-compile-report/SKILL.md"
check "sub-skill 10" "$TARGET/skills/skill-10-render-report/SKILL.md"
check "renderer: render_report.py" "$TARGET/report-renderer/render_report.py"
check "renderer: contract.py" "$TARGET/report-renderer/contract.py"
check "renderer: visual_qa.py" "$TARGET/report-renderer/visual_qa.py"
check "renderer: template.html" "$TARGET/report-renderer/template.html"
check "docs/DIGEST.md" "$TARGET/skills/DIGEST.md"
check "docs/GLOSSARY.md" "$TARGET/skills/GLOSSARY.md"
check "docs/INDEX.md" "$TARGET/skills/INDEX.md"
check "docs/PIPELINE_STATE.md" "$TARGET/skills/PIPELINE_STATE.md"
check "example submission" "$TARGET/examples/tesla-us433700/submission.md"
check "example quickstart prompt" "$TARGET/examples/tesla-us433700/quickstart-prompt.md"
check "example report v1.6" "$TARGET/examples/tesla-us433700/report-tesla-us433700-e2e-v16.md"
check "v1.7 models" "$TARGET/engine_v17/models.py"
check "v1.7 recovery controller" "$TARGET/engine_v17/recovery.py"
check "v1.7 claim graph" "$TARGET/engine_v17/claim_graph.py"
check "v1.7 rights graph" "$TARGET/engine_v17/rights_graph.py"
check "v1.7 constraints" "$TARGET/engine_v17/constraints.py"
check "v1.7 landscape layer" "$TARGET/engine_v17/landscape.py"
check "v1.7 provenance invariants" "$TARGET/engine_v17/provenance.py"
check "v1.7 migration" "$TARGET/engine_v17/migration.py"
check "v1.7 compiler" "$TARGET/engine_v17/compiler.py"
check "v1.8 coverage gates" "$TARGET/engine_v17/coverage.py"
check "v1.8 renderer contract" "$TARGET/report-renderer/contract.py"
check "v1.8 visual QA gate" "$TARGET/report-renderer/visual_qa.py"
check "v1.7 tests" "$TARGET/tests_v17/test_us8527057_acceptance.py"
check "v1.8 state machine tests" "$TARGET/tests_v17/test_state_machine.py"
check "v1.8 coverage tests" "$TARGET/tests_v17/test_coverage.py"
check "renderer contract tests" "$TARGET/report-renderer/tests/test_contract.py"
check "renderer visual QA tests" "$TARGET/report-renderer/tests/test_visual_qa.py"

for f in "$TARGET/skills/skill-*/SKILL.md"; do
  if [ -f "$f" ]; then
    if ! grep -q '^name:' "$f" || ! grep -q '^description:' "$f"; then
      echo "  [FAIL] frontmatter missing name/description in $f"
      FAIL=1
    fi
  fi
done

echo ""
echo "--- v1.6 legacy-terminology semantic scan (active schema files) ---"
# Active files: engine SKILL + sub-skills + docs. Historical artifacts
# (Test-report-results/, examples/, docs/superpowers/) are exempt.
ACTIVE_FILES=(
  "$TARGET/skills/SKILL-Orchestrator.md"
  "$TARGET/skills"/skill-*/SKILL.md
  "$TARGET/skills/DIGEST.md"
  "$TARGET/skills/GLOSSARY.md"
  "$TARGET/skills/INDEX.md"
  "$TARGET/skills/PIPELINE_STATE.md"
)

# Anti-patterns: legacy states used as ACTIVE semantics (not in the
# GLOSSARY legacy-mapping table, which is delimited by markers).
LEGACY_ANTIPATTERNS=(
  'evidence_state: NOT OBSERVED'
  'evidence_state: NOT IDENTIFIED'
  'evidence_state: INFERRED'
  'evidence_state: NOT EVALUATED'
  'evidence_state: CONTESTED'
  'Evidence Status: INFERRED'
  'bridge_status: .*UNRESOLVED'
  'final_assessment: .*UNRESOLVED'
  'status: INFERRED'
  'completeness: MEDIUM'
  'Negative Evidence Coverage Rule'
  'Overall patentability:'
  '\| Overall patentability \|'
)

for f in "${ACTIVE_FILES[@]}"; do
  [ -f "$f" ] || continue
  # Migration documentation is exempt from the scan:
  # - GLOSSARY: the delimited legacy-mapping table
  # - PIPELINE_STATE: the historical changelog + validation-run sections
  if [[ "$f" == *GLOSSARY.md ]]; then
    awk '/<!-- v1.6-legacy-mapping -->/{skip=1} /<!-- \/v1.6-legacy-mapping -->/{skip=0; next} !skip' "$f" > /tmp/v16-glossary-scan.txt
    SCAN_FILE=/tmp/v16-glossary-scan.txt
  elif [[ "$f" == *PIPELINE_STATE.md ]]; then
    awk '/<!-- v1.6-history -->/{skip=1} /<!-- \/v1.6-history -->/{skip=0; next} !skip' "$f" > /tmp/v16-pipeline-scan.txt
    SCAN_FILE=/tmp/v16-pipeline-scan.txt
  else
    SCAN_FILE="$f"
  fi
  for pat in "${LEGACY_ANTIPATTERNS[@]}"; do
    if grep -qE "$pat" "$SCAN_FILE"; then
      echo "  [FAIL] LEGACY_STATE_IN_ACTIVE_SCHEMA: '$pat' in $f"
      FAIL=1
    fi
  done
done
echo "  (legacy terms in historical reports / migration docs are permitted)"

echo ""
echo "--- v1.7 engine tests ---"
if command -v pytest >/dev/null 2>&1; then
  if PYTHONPATH="$TARGET" pytest "$TARGET/tests_v17" -q; then
    echo "  [PASS] v1.7 engine test suite"
  else
    echo "  [FAIL] v1.7 engine test suite"
    FAIL=1
  fi
else
  echo "  [FAIL] pytest is not installed"
  FAIL=1
fi

echo ""
echo "--- v1.8 renderer contract + visual QA tests ---"
if command -v pytest >/dev/null 2>&1; then
  if pytest "$TARGET/report-renderer/tests" -q; then
    echo "  [PASS] renderer contract + visual QA test suite"
  else
    echo "  [FAIL] renderer contract + visual QA test suite"
    FAIL=1
  fi
else
  echo "  [FAIL] pytest is not installed"
  FAIL=1
fi

echo ""
echo "--- v1.8 semantic scans ---"
# The renderer must never silently drop semantic content. A report whose
# rendered HTML accounts for every source semantic node is structurally
# sound; one that does not is a contract failure. The delivered PDF must
# also pass the structural + visual QA gate.
PAGES=$(pdfinfo "$TARGET/evaluations/us8527057-v17(Complete-pass)/report-us8527057-v17.pdf" 2>/dev/null | awk '/^Pages:/{print $2}')
PAGES=${PAGES:-1}
PYTHONPATH="$TARGET:$TARGET/report-renderer" python3 "$TARGET/report-renderer/verify_semantics.py" "$TARGET"
if [ $? -ne 0 ]; then FAIL=1; fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "SOME CHECKS FAILED"
  exit 1
fi