#!/usr/bin/env bash
# Guardrail: blocks edits to src/*.rs unless the user has approved a plan.
#
# How it works:
# - Claude must create .claude/approved-plan.txt ONLY after the user explicitly says "sí/yes/ok/adelante"
# - The file must contain a timestamp less than 2 hours old
# - If the file doesn't exist or is stale, edits to src/*.rs are blocked
set -euo pipefail

FILE=$(jq -r '.tool_input.file_path // .tool_response.filePath // empty' 2>/dev/null)

# Only gate .rs files in src/
if [[ -z "$FILE" ]] || [[ "$FILE" != *.rs ]] || [[ "$FILE" != */src/* ]]; then
    exit 0
fi

APPROVAL_FILE=".claude/approved-plan.txt"

if [[ ! -f "$APPROVAL_FILE" ]]; then
    echo "{\"decision\": \"block\", \"reason\": \"BLOCKED: No plan approved. Present your plan to the user and wait for explicit approval before editing src/*.rs files. Create .claude/approved-plan.txt only after user says yes.\"}"
    exit 0
fi

# Check timestamp freshness (max 2 hours = 7200 seconds)
APPROVAL_TIME=$(head -1 "$APPROVAL_FILE" | grep -oE '[0-9]+' || echo "0")
CURRENT_TIME=$(date +%s)
AGE=$(( CURRENT_TIME - APPROVAL_TIME ))

if [ "$AGE" -gt 7200 ]; then
    echo "{\"decision\": \"block\", \"reason\": \"BLOCKED: Plan approval expired ($(( AGE / 60 )) minutes old). Present updated plan and get fresh approval.\"}"
    exit 0
fi
