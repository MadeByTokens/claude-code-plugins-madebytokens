#!/bin/bash
# Auto-approve WebSearch during active PRD sessions

STATE_FILE="./.prd-state"

# Only auto-approve if PRD session is active
if [ -f "$STATE_FILE" ]; then
  source "$STATE_FILE"
  if [ "$PRD_ACTIVE" = "1" ]; then
    cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "PRD session - web search for requirements research"
  }
}
EOF
    exit 0
  fi
fi

# Don't interfere with other operations
exit 0
