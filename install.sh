#!/usr/bin/env bash
set -euo pipefail

SKILL_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
TARGET_DIR="$SKILL_ROOT/jiaojie"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_SOURCE_DIR="$SCRIPT_DIR/skill"
GITHUB_OWNER="${GITHUB_OWNER:-LCbeijing}"
GITHUB_REPO="${GITHUB_REPO:-jiaojie}"
GITHUB_REF="${GITHUB_REF:-main}"
ARCHIVE_URL="https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/archive/refs/heads/${GITHUB_REF}.tar.gz"

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
python3 "$TARGET_DIR/scripts/regression_readonly.py" --json
