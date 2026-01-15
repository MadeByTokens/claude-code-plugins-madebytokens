#!/bin/bash
# Auto-approve all chess MCP tools

cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Chess plugin tool"
  }
}
EOF
