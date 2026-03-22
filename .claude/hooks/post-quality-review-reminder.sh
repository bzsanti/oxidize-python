#!/usr/bin/env bash
# Guardrail: after a quality-agent finishes, inject a mandatory reminder
# to present findings and ask before implementing.
#
# This hook fires on PostToolUse for Agent calls.
# It checks if the agent was a quality-agent by looking at the tool_input.
set -euo pipefail

INPUT=$(cat)

# Check if this was a quality-agent invocation
IS_QUALITY=$(echo "$INPUT" | jq -r '.tool_input.subagent_type // empty' 2>/dev/null)

if [[ "$IS_QUALITY" != "quality-agent" ]]; then
    exit 0
fi

# Remove any stale approval — quality review invalidates previous approvals
rm -f .claude/approved-plan.txt

# Inject mandatory reminder
cat << 'REMINDER'
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "MANDATORY: Quality review completed. You MUST follow this exact sequence:\n1. Present ALL findings in a summary table (critical + recommended + optional)\n2. ASK the user: '¿Quieres que implemente todos estos hallazgos? ¿En qué orden?'\n3. WAIT for the user's explicit response\n4. Only after approval, create .claude/approved-plan.txt with timestamp and implement\n\nDO NOT start implementing without user approval. The approval file has been deleted."
  }
}
REMINDER
