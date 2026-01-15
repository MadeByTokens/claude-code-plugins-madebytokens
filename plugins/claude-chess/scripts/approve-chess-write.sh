#!/bin/bash
# Auto-approve Write/Edit operations for chess-related files

# Read the hook input from stdin
input=$(cat)

# Extract the file_path from the input
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Approve writes to .chess-working/ directory
if [[ "$file_path" == *".chess-working/"* ]]; then
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

# Don't interfere with other operations
exit 0
