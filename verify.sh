#!/usr/bin/env bash
set -uo pipefail

# Invention Evaluation Engine — v1.6 install verifier
# Usage: ./verify.sh [--path /path/to/invention-evaluation-engine]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$SCRIPT_DIR/invention-evaluation-engine"

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

check "engine SKILL.md" "$TARGET/SKILL.md"
check "sub-skill 01" "$TARGET/skills/skill-01-invention-evaluation-overview/SKILL.md"
check "sub-skill 02" "$TARGET/skills/skill-02-gather-invention-submission/SKILL.md"
check "sub-skill 03" "$TARGET/skills/skill-03-analyze-technology-fundamentals/SKILL.md"
check "sub-skill 04" "$TARGET/skills/skill-04-conduct-patent-landscape/SKILL.md"
check "sub-skill 05" "$TARGET/skills/skill-05-conduct-novelty-search/SKILL.md"
check "sub-skill 06" "$TARGET/skills/skill-06-conduct-literature-search/SKILL.md"
check "sub-skill 07" "$TARGET/skills/skill-07-analyze-market-opportunity/SKILL.md"
check "sub-skill 08" "$TARGET/skills/skill-08-identify-partners/SKILL.md"
check "sub-skill 09" "$TARGET/skills/skill-09-compile-report/SKILL.md"
check "docs/DIGEST.md" "$TARGET/docs/DIGEST.md"
check "docs/GLOSSARY.md" "$TARGET/docs/GLOSSARY.md"
check "docs/INDEX.md" "$TARGET/docs/INDEX.md"
check "docs/PIPELINE_STATE.md" "$TARGET/docs/PIPELINE_STATE.md"
check "example submission" "$TARGET/examples/tesla-us433700/submission.md"
check "example quickstart prompt" "$TARGET/examples/tesla-us433700/quickstart-prompt.md"
check "example report v1.6" "$TARGET/examples/tesla-us433700/report-tesla-us433700-e2e-v16.md"

for f in "$TARGET/SKILL.md" "$TARGET"/skills/skill-*/SKILL.md; do
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
  "$TARGET/SKILL.md"
  "$TARGET"/skills/skill-*/SKILL.md
  "$TARGET/docs/DIGEST.md"
  "$TARGET/docs/GLOSSARY.md"
  "$TARGET/docs/INDEX.md"
  "$TARGET/docs/PIPELINE_STATE.md"
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
echo "--- v1.6 root/package parity check ---"
# root path | package path. Root holds docs at top level and skills in
# skill-XX/ dirs; the package holds them under docs/ and skills/. The engine
# SKILL.md is package-only (no root counterpart) and is not parity-checked.
ROOT_DIR="$SCRIPT_DIR"
PARITY_PAIRS=(
  "DIGEST.md|docs/DIGEST.md"
  "GLOSSARY.md|docs/GLOSSARY.md"
  "INDEX.md|docs/INDEX.md"
  "PIPELINE_STATE.md|docs/PIPELINE_STATE.md"
  "skill-01-invention-evaluation-overview/SKILL.md|skills/skill-01-invention-evaluation-overview/SKILL.md"
  "skill-02-gather-invention-submission/SKILL.md|skills/skill-02-gather-invention-submission/SKILL.md"
  "skill-03-analyze-technology-fundamentals/SKILL.md|skills/skill-03-analyze-technology-fundamentals/SKILL.md"
  "skill-04-conduct-patent-landscape/SKILL.md|skills/skill-04-conduct-patent-landscape/SKILL.md"
  "skill-05-conduct-novelty-search/SKILL.md|skills/skill-05-conduct-novelty-search/SKILL.md"
  "skill-06-conduct-literature-search/SKILL.md|skills/skill-06-conduct-literature-search/SKILL.md"
  "skill-07-analyze-market-opportunity/SKILL.md|skills/skill-07-analyze-market-opportunity/SKILL.md"
  "skill-08-identify-partners/SKILL.md|skills/skill-08-identify-partners/SKILL.md"
  "skill-09-compile-report/SKILL.md|skills/skill-09-compile-report/SKILL.md"
)
for pair in "${PARITY_PAIRS[@]}"; do
  root_rel="${pair%%|*}"
  pkg_rel="${pair##*|}"
  root_file="$ROOT_DIR/$root_rel"
  pkg_file="$TARGET/$pkg_rel"
  if [ -f "$root_file" ] && [ -f "$pkg_file" ]; then
    if [ "$(sha256sum "$root_file" | cut -d' ' -f1)" = "$(sha256sum "$pkg_file" | cut -d' ' -f1)" ]; then
      echo "  [PASS] parity: $root_rel ↔ $pkg_rel"
    else
      echo "  [FAIL] parity mismatch: $root_rel ↔ $pkg_rel (root ≠ package)"
      FAIL=1
    fi
  else
    echo "  [FAIL] parity: missing file for $root_rel ↔ $pkg_rel (root=$root_file pkg=$pkg_file)"
    FAIL=1
  fi
done

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "SOME CHECKS FAILED"
  exit 1
fi
