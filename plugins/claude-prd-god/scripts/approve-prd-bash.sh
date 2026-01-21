#!/bin/bash
# Auto-approve Bash operations for PRD plugin scripts only

# Read the hook input from stdin
input=$(cat)

# Extract the command from the input
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Approve start-prd-session.sh (with any arguments)
if [[ "$command" == *"scripts/start-prd-session.sh"* ]]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "PRD session start"
  }
}
EOF
  exit 0
fi

# Approve end-prd-session.sh
if [[ "$command" == *"scripts/end-prd-session.sh"* ]]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "PRD session end"
  }
}
EOF
  exit 0
fi

# Approve generate-final-prd.sh
if [[ "$command" == *"scripts/generate-final-prd.sh"* ]]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "PRD final generation"
  }
}
EOF
  exit 0
fi

# Do NOT auto-approve any other bash commands
# This prevents Claude from running code, installing packages, etc.
exit 0
