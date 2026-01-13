#!/bin/bash
# Generate premium agent variants from base agents
# Run this script after modifying coach.md to regenerate coach-premium.md

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$SCRIPT_DIR/../agents"

# Generate coach-premium.md from coach.md
sed -e 's/^name: coach$/name: coach-premium/' \
    -e 's/^model: sonnet$/model: opus/' \
    "$AGENTS_DIR/coach.md" > "$AGENTS_DIR/coach-premium.md"

echo "Generated: agents/coach-premium.md (model: opus)"
