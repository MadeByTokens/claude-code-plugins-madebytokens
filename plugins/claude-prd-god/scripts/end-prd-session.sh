#!/bin/bash
# End a PRD session - removes state file

STATE_FILE="./.prd-state"

if [ -f "$STATE_FILE" ]; then
    # Read session file path before deleting state
    SESSION_FILE=$(grep "SESSION_FILE=" "$STATE_FILE" | cut -d'=' -f2)
    COMPLETED=$(grep "COMPLETED_SECTIONS=" "$STATE_FILE" | cut -d'=' -f2)

    # Remove state file
    rm "$STATE_FILE"

    echo "ENDED=1"
    echo "SESSION_FILE=$SESSION_FILE"
    echo "COMPLETED_SECTIONS=$COMPLETED"
else
    echo "ENDED=0"
    echo "ERROR=No active PRD session"
fi
