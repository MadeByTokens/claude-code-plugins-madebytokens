#!/bin/bash
# Auto-approve Write operations ONLY for PRD session files
# All other files (especially code files) require manual approval

# Read the hook input from stdin
input=$(cat)

# Extract the file_path from the input
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# ONLY approve writes to prd-*.md files
if [[ "$file_path" == *"prd-"*".md" ]]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "PRD session file"
  }
}
EOF
  exit 0
fi

# IMPORTANT: Do NOT auto-approve any other file type
# This means code files (.py, .js, .ts, etc.) will trigger
# the normal permission prompt, giving the user a chance to reject

# Don't interfere with other operations (let normal permission flow handle them)
exit 0
