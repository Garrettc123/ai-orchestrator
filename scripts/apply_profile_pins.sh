#!/usr/bin/env bash
set -euo pipefail
# One-system apply. Requires gh auth with user scope (profile pins).
# MCP GitHub connector cannot run this mutation.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
gh api graphql --input "$ROOT/scripts/apply_profile_pins.graphql"
echo "Pinned 6. Verify: https://github.com/Garrettc123"
