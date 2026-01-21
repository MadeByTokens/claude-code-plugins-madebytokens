#!/bin/bash
# Generate a clean, stakeholder-ready final PRD from the working document

set -e

# Get session file from argument or state file
if [ -n "$1" ]; then
    SESSION_FILE="$1"
elif [ -f "./.prd-state" ]; then
    SESSION_FILE=$(grep "SESSION_FILE=" "./.prd-state" | cut -d'=' -f2)
else
    echo "ERROR=No session file specified and no active PRD session"
    exit 1
fi

if [ ! -f "$SESSION_FILE" ]; then
    echo "ERROR=Session file not found: $SESSION_FILE"
    exit 1
fi

# Generate output filename (replace timestamp with FINAL)
FINAL_FILE=$(echo "$SESSION_FILE" | sed 's/-[0-9]\{8\}-[0-9]\{4\}\.md$/-FINAL.md/')

# If the pattern didn't match, just append -FINAL before .md
if [ "$FINAL_FILE" = "$SESSION_FILE" ]; then
    FINAL_FILE="${SESSION_FILE%.md}-FINAL.md"
fi

# Process the file:
# 1. Remove "**Section Status:** ..." lines
# 2. Remove lines that are only "[To be filled]" or "[To be filled - ...]"
# 3. Remove italic helper text lines (lines starting with *)
# 4. Remove empty table rows with only placeholders
# 5. Clean up multiple consecutive blank lines

cat "$SESSION_FILE" | \
    # Remove Section Status lines
    grep -v '^\*\*Section Status:\*\*' | \
    # Remove standalone placeholder lines
    sed '/^\[To be filled.*\]$/d' | \
    # Remove placeholder table cells but keep the row structure for now
    sed 's/| \[To be filled[^|]*\] /| - /g' | \
    # Remove italic helper/instruction lines (but keep italic content that's actual text)
    sed '/^\*[A-Z][^*]*\*$/d' | \
    # Remove "Generated:" and "Source Brainstorm:" metadata lines
    sed '/^Generated: /d' | \
    sed '/^Source Brainstorm: /d' | \
    # Clean up multiple blank lines (reduce to max 2)
    cat -s \
    > "$FINAL_FILE"

# Count completed vs total sections by checking for actual content
TOTAL_SECTIONS=25
COMPLETED=0

# Check each section for real content (not just placeholders)
for section_num in $(seq 0 24); do
    # Look for section header and check if there's content after it
    if grep -q "^## $section_num\." "$SESSION_FILE"; then
        # Check if section has content beyond placeholders
        section_content=$(sed -n "/^## $section_num\./,/^## [0-9]/p" "$SESSION_FILE" | grep -v "^\[To be filled" | grep -v "^\*\*Section Status:" | grep -v "^## " | grep -v "^$" | grep -v "^\*[A-Z]" | head -5)
        if [ -n "$section_content" ]; then
            COMPLETED=$((COMPLETED + 1))
        fi
    fi
done

echo "FINAL_FILE=$FINAL_FILE"
echo "SOURCE_FILE=$SESSION_FILE"
echo "SECTIONS_WITH_CONTENT=$COMPLETED"
echo "TOTAL_SECTIONS=$TOTAL_SECTIONS"
