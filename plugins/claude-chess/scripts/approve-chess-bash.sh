#!/bin/bash
# Auto-approve only chess-related bash commands

# Read the hook input from stdin
input=$(cat)

# Extract the command from the input
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Approve mkdir for .chess-working directories
if [[ "$command" == *"mkdir"* && "$command" == *".chess-working"* ]]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Chess plugin directory setup"
  }
}
EOF
  exit 0
fi

# Approve rm for state/game.json (clearing game state)
if [[ "$command" == *"rm"* && "$command" == *"state/game.json"* ]]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Chess plugin clearing game state"
  }
}
EOF
  exit 0
fi

# Approve cat/echo writes to .chess-working/ (agent outputs)
if [[ "$command" == *".chess-working/"* ]]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Chess plugin agent output"
  }
}
EOF
  exit 0
fi

# Don't interfere with other bash commands - let normal permission flow handle them
exit 0
