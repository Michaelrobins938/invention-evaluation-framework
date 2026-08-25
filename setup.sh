#!/usr/bin/env bash
set -uo pipefail

# Invention Evaluation Framework — one-click setup
# Installs Python dependencies, detects installed coding agents,
# installs the run-invention-evaluation skill into each one,
# creates .env from template, and runs a smoke test.
#
# Usage:
#   bash setup.sh                          # auto-detect everything
#   bash setup.sh --agents claude,opencode # force specific agents
#   bash setup.sh --skip-deps              # skip pip install step
#   bash setup.sh --list                   # only show what was detected

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$SCRIPT_DIR/skills/skill-00-run-evaluation/SKILL.md"
SKILL_NAME="run-invention-evaluation"

LIST_ONLY=0
SKIP_DEPS=0
AGENT_ARG=""

while [ $# -gt 0 ]; do
  case "$1" in
    --agents) AGENT_ARG="$2"; shift 2 ;;
    --skip-deps) SKIP_DEPS=1; shift ;;
    --list) LIST_ONLY=1; shift ;;
    -h|--help)
      sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Unknown argument: $1 (see --help)" >&2; exit 1 ;;
  esac
done

banner() { echo ""; echo "== $1 =="; }

# ---------------------------------------------------------------------------
# 1. Preflight
# ---------------------------------------------------------------------------
banner "Preflight"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Install Python 3.10+ first:"
  echo "  https://www.python.org/downloads/"
  exit 1
fi

PY_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PY_OK="$(python3 -c 'import sys; print(1 if sys.version_info >= (3,10) else 0)')"
echo "  python3: $PY_VERSION"

if [ "$PY_OK" != "1" ]; then
  echo "ERROR: Python 3.10+ required, found $PY_VERSION."
  exit 1
fi

if ! python3 -m pip --version >/dev/null 2>&1; then
  echo "ERROR: pip not available (python3 -m pip). Install pip first:"
  echo "  python3 -m ensurepip --upgrade"
  exit 1
fi
echo "  pip: $(python3 -m pip --version | cut -d' ' -f1-2)"

if [ ! -f "$SKILL_SRC" ]; then
  echo "ERROR: skill source not found: $SKILL_SRC"
  echo "Run this script from the framework root directory."
  exit 1
fi

# ---------------------------------------------------------------------------
# 2. Agent detection
# ---------------------------------------------------------------------------
banner "Detecting coding agents"

declare -A AGENT_DIRS=(
  [claude]="$HOME/.claude/skills"
  [opencode]="$HOME/.config/opencode/skills"
  [opencode-alt]="$HOME/.opencode/skills"
  [agents]="$HOME/.agents/skills"
)

DETECTED=()
for name in claude opencode opencode-alt agents; do
  d="${AGENT_DIRS[$name]}"
  if [ -d "$d" ]; then
    DETECTED+=("$name:$d")
    echo "  [FOUND] $name -> $d"
  fi
done

if [ -n "$AGENT_ARG" ]; then
  DETECTED=()
  IFS=',' read -ra WANTED <<< "$AGENT_ARG"
  for w in "${WANTED[@]}"; do
    w="$(echo "$w" | tr '[:upper:]' '[:lower:]' | tr -d ' ')"
    case "$w" in
      claude)      DETECTED+=("claude:${AGENT_DIRS[claude]}") ;;
      opencode)    DETECTED+=("opencode:${AGENT_DIRS[opencode]}")
                   [ -d "${AGENT_DIRS[opencode-alt]}" ] && DETECTED+=("opencode-alt:${AGENT_DIRS[opencode-alt]}") ;;
      agents)      DETECTED+=("agents:${AGENT_DIRS[agents]}") ;;
      *) echo "Unknown agent '$w' (supported: claude, opencode, agents)" >&2; exit 1 ;;
    esac
  done
fi

if [ ${#DETECTED[@]} -eq 0 ]; then
  echo ""
  echo "No coding-agent skill directories found."
  echo "Supported agents: Claude Code (~/.claude), OpenCode (~/.config/opencode or ~/.opencode)"
  echo ""
  echo "The framework still works standalone:"
  echo "  cd $SCRIPT_DIR && ./evaluate /path/to/invention-folder"
  echo ""
  echo "Re-run setup after installing an agent to auto-install the skill."
  if [ "$LIST_ONLY" = "1" ]; then exit 0; fi
fi

if [ "$LIST_ONLY" = "1" ]; then exit 0; fi

# ---------------------------------------------------------------------------
# 3. Python dependencies
# ---------------------------------------------------------------------------
if [ "$SKIP_DEPS" = "0" ]; then
  banner "Installing Python dependencies"
  PIP_OK=0
  if python3 -m pip install -r "$SCRIPT_DIR/requirements.txt" --quiet 2>/dev/null; then
    PIP_OK=1
  elif python3 -m pip install --user -r "$SCRIPT_DIR/requirements.txt" --quiet 2>/dev/null; then
    PIP_OK=1
    echo "  (installed with --user)"
  elif python3 -m pip install --user --break-system-packages -r "$SCRIPT_DIR/requirements.txt" --quiet 2>/dev/null; then
    PIP_OK=1
    echo "  (installed with --user --break-system-packages)"
  fi

  if [ "$PIP_OK" = "1" ]; then
    echo "  [OK] dependencies installed from requirements.txt"
  else
    echo "  [WARN] pip install failed — checking whether deps already exist..."
  fi
else
  banner "Skipping dependency installation (--skip-deps)"
fi

MISSING=""
for mod in pdfplumber yaml jsonschema PIL docx; do
  if ! python3 -c "import $mod" >/dev/null 2>&1; then
    MISSING="$MISSING $mod"
  fi
done
if [ -n "$MISSING" ]; then
  echo "  [WARN] missing modules:$MISSING"
  echo "         patent PDF/docx parsing will degrade until installed:"
  echo "         python3 -m pip install --user -r $SCRIPT_DIR/requirements.txt"
else
  echo "  [OK] all runtime modules importable"
fi

# ---------------------------------------------------------------------------
# 4. Install skill into each detected agent
# ---------------------------------------------------------------------------
banner "Installing skill: $SKILL_NAME"

INSTALLED_TO=()
for entry in "${DETECTED[@]}"; do
  dest="${entry#*:}"
  label="${entry%%:*}"
  target_dir="$dest/$SKILL_NAME"
  mkdir -p "$target_dir"

  if [ "$(uname)" = "Darwin" ]; then
    sed "s|{{FRAMEWORK_ROOT}}|$SCRIPT_DIR|g" "$SKILL_SRC" > "$target_dir/SKILL.md" 2>/dev/null \
      || perl -pe "s|\{\{FRAMEWORK_ROOT\}\}|$SCRIPT_DIR|g" "$SKILL_SRC" > "$target_dir/SKILL.md"
  else
    sed "s|{{FRAMEWORK_ROOT}}|$SCRIPT_DIR|g" "$SKILL_SRC" > "$target_dir/SKILL.md"
  fi

  INSTALLED_TO+=("$target_dir")
  echo "  [OK] $label -> $target_dir/SKILL.md"
done

# ---------------------------------------------------------------------------
# 5. Environment template
# ---------------------------------------------------------------------------
banner "Environment configuration"

if [ -f "$SCRIPT_DIR/.env" ]; then
  echo "  [OK] .env already exists (left untouched)"
else
  if cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env" 2>/dev/null; then
    echo "  [OK] created .env from .env.example"
    echo "       add EPO OPS credentials later for live patent search:"
    echo "       https://developers.epo.org"
  else
    echo "  [WARN] no .env.example found — skipping (framework runs without live APIs)"
  fi
fi

# ---------------------------------------------------------------------------
# 6. Smoke test
# ---------------------------------------------------------------------------
banner "Smoke test"

SMOKE_FAIL=0

if python3 "$SCRIPT_DIR/run.py" --help >/dev/null 2>&1; then
  echo "  [OK] run.py loads and shows help"
else
  echo "  [FAIL] run.py --help errored"
  SMOKE_FAIL=1
fi

TMPDIR_SMOKE="$(mktemp -d)"
printf 'disclosure text\n' > "$TMPDIR_SMOKE/8530-disclosure.pdf" 2>/dev/null || true

cd "$SCRIPT_DIR"
DETECTED_ID="$(python3 -c "
from pathlib import Path
from engine_v17.pdf_parser import detect_id_from_filenames
print(detect_id_from_filenames(Path('$TMPDIR_SMOKE')) or 'NONE')
" 2>/dev/null || echo "ERR")"

if [ "$DETECTED_ID" = "8530" ]; then
  echo "  [OK] ID auto-detection works (8530)"
elif [ "$DETECTED_ID" = "NONE" ]; then
  echo "  [WARN] ID detection returned none (non-fatal)"
else
  echo "  [WARN] ID detection check skipped/errored (non-fatal)"
fi
rm -rf "$TMPDIR_SMOKE"

# Verify installed skill got real paths
for t in "${INSTALLED_TO[@]:-}"; do
  [ -z "$t" ] && continue
  if grep -q '{{FRAMEWORK_ROOT}}' "$t/SKILL.md" 2>/dev/null; then
    echo "  [WARN] path substitution incomplete in $t/SKILL.md"
    SMOKE_FAIL=1
  fi
done

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
banner "Setup complete"

echo ""
echo "  Framework root : $SCRIPT_DIR"
echo "  Skill installed: ${#INSTALLED_TO[@]} agent(s)"
echo ""

if [ ${#INSTALLED_TO[@]} -gt 0 ]; then
  echo "  NEXT: restart your coding agent, then say:"
  echo '        "evaluate this invention folder: /path/to/folder"'
  echo ""
fi
echo "  Or run directly without any agent:"
echo "        cd $SCRIPT_DIR && ./evaluate /path/to/invention-folder"
echo ""

if [ "$SMOKE_FAIL" = "1" ]; then
  echo "  Setup finished WITH WARNINGS — review [WARN]/[FAIL] lines above."
  exit 1
fi
exit 0
