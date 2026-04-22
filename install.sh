#!/usr/bin/env bash
set -euo pipefail

RAW_CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
if command -v cygpath >/dev/null 2>&1; then
  case "$RAW_CODEX_HOME" in
    [A-Za-z]:\\*|[A-Za-z]:/*)
      RAW_CODEX_HOME="$(cygpath -u "$RAW_CODEX_HOME")"
      ;;
  esac
fi

SKILL_ROOT="${RAW_CODEX_HOME}/skills"
TARGET_DIR="$SKILL_ROOT/jiaojie"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_SOURCE_DIR="$SCRIPT_DIR/skill"
GITHUB_OWNER="${GITHUB_OWNER:-LCbeijing}"
GITHUB_REPO="${GITHUB_REPO:-jiaojie}"
GITHUB_REF="${GITHUB_REF:-main}"
ARCHIVE_URL="https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/archive/refs/heads/${GITHUB_REF}.tar.gz"

PYTHON_CMD=()
if command -v python >/dev/null 2>&1; then
  PYTHON_CMD=(python)
elif command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
  PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1; then
  PYTHON_CMD=(py -3)
else
  echo "Python 3 not found. Please install Python before running install.sh." >&2
  exit 1
fi

mkdir -p "$SKILL_ROOT"
rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"

if [[ -d "$LOCAL_SOURCE_DIR" ]]; then
  cp -R "$LOCAL_SOURCE_DIR"/. "$TARGET_DIR"/
else
  TMP_DIR="$(mktemp -d)"
  trap 'rm -rf "$TMP_DIR"' EXIT
  curl -fsSL "$ARCHIVE_URL" | tar -xz -C "$TMP_DIR"
  cp -R "$TMP_DIR"/"${GITHUB_REPO}-${GITHUB_REF}"/skill/. "$TARGET_DIR"/
fi

chmod +x "$TARGET_DIR"/scripts/*.py || true

echo "Installed jiaojie to: $TARGET_DIR"
echo "Running read-only regression..."
"${PYTHON_CMD[@]}" "$TARGET_DIR/scripts/regression_readonly.py" --json
