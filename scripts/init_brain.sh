#!/usr/bin/env bash
# Scaffold a new project's Obsidian brain from templates/brain/.
# Usage: init_brain.sh "Brand Name" brand-slug [target-dir]
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 \"Brand Name\" brand-slug [target-dir]" >&2
  exit 1
fi

BRAND_NAME="$1"
BRAND_SLUG="$2"
TARGET_DIR="${3:-$HOME/Documents/${BRAND_SLUG}-brain}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates/brain"

if [[ -d "$TARGET_DIR" ]]; then
  echo "Vault already exists at $TARGET_DIR — leaving it untouched. Delete it first if you want a clean re-scaffold." >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"
cp -R "$TEMPLATE_DIR/." "$TARGET_DIR/"

# Substitute placeholders in every markdown file
find "$TARGET_DIR" -type f -name "*.md" -print0 | while IFS= read -r -d '' f; do
  sed -i.bak "s/{{BRAND}}/$BRAND_NAME/g; s/{{BRAND_SLUG}}/$BRAND_SLUG/g" "$f"
  rm -f "$f.bak"
done

echo "Vault scaffolded at $TARGET_DIR"
echo "Fill in wiki/voice/ and wiki/positioning/ before the first blog-pipeline run, or answer the interview gate thoroughly and let it fill them in."
