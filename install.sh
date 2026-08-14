#!/usr/bin/env bash
set -euo pipefail

# Invention Evaluation Engine — installer
# Usage:
#   ./install.sh                          # auto-detect target tool
#   ./install.sh --tool claude            # force Claude Code
#   ./install.sh --tool opencode          # force OpenCode
#   ./install.sh --tool copilot           # install into .github/skills/ (run from project root)
#   ./install.sh --tool custom --path /some/dir
#   ./install.sh --force                  # overwrite existing install without backup prompt

PKG_DIR="invention-evaluation-engine"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/$PKG_DIR"

detect_tool() {
  if [ -d "$HOME/.claude/skills" ]; then echo "claude"; return 0; fi
  if [ -d "$HOME/.opencode/skills" ]; then echo "opencode"; return 0; fi
  echo "unknown"
}

TOOL=""
PATH_ARG=""
FORCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --tool) TOOL="$2"; shift 2 ;;
    --path) PATH_ARG="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [ -z "$TOOL" ]; then
  TOOL="$(detect_tool)"
fi

case "$TOOL" in
  claude)   DEST="$HOME/.claude/skills" ;;
  opencode) DEST="$HOME/.opencode/skills" ;;
  copilot)  DEST="$(pwd)/.github/skills" ;;
  custom)   DEST="${PATH_ARG:?--path is required with --tool custom}" ;;
  unknown)  echo "No supported tool detected. Use --tool claude|opencode|copilot|custom (with --path)." >&2; exit 1 ;;
  *) echo "Unknown tool: $TOOL (expected claude|opencode|copilot|custom)" >&2; exit 1 ;;
esac

if [ ! -d "$SRC" ]; then
  echo "ERROR: $SRC not found. Run this script from the package root." >&2
  exit 1
fi

mkdir -p "$DEST"
TARGET="$DEST/$PKG_DIR"

if [ -d "$TARGET" ]; then
  if [ "$FORCE" -eq 1 ]; then
    rm -rf "$TARGET"
    echo "Removed existing install at $TARGET (--force)."
  else
    BAK="$TARGET.bak-$(date +%Y%m%d-%H%M%S)"
    mv "$TARGET" "$BAK"
    echo "Existing install backed up to $BAK"
  fi
fi

cp -R "$SRC" "$TARGET"
echo ""
echo "Installed invention-evaluation-engine to: $TARGET"
echo ""
echo "Next steps:"
echo "  1. Restart your agent tool (or reload skills)."
echo "  2. Run the sample: paste the prompt from"
echo "     $PKG_DIR/examples/tesla-us433700/quickstart-prompt.md"
echo "  3. Compare the output with"
echo "     $PKG_DIR/examples/tesla-us433700/report-tesla-us433700-e2e-v16.md"