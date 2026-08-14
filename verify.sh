#!/usr/bin/env bash
set -uo pipefail

# Invention Evaluation Engine — install verifier
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
check "example report" "$TARGET/examples/tesla-us433700/report-tesla-us433700-e2e-v15.md"

for f in "$TARGET/SKILL.md" "$TARGET"/skills/skill-*/SKILL.md; do
  if [ -f "$f" ]; then
    if ! grep -q '^name:' "$f" || ! grep -q '^description:' "$f"; then
      echo "  [FAIL] frontmatter missing name/description in $f"
      FAIL=1
    fi
  fi
done

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  echo ""
  echo "Quickstart: paste the prompt from"
  echo "  $TARGET/examples/tesla-us433700/quickstart-prompt.md"
  exit 0
else
  echo "SOME CHECKS FAILED"
  exit 1
fi