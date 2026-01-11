---
description: Cancel the active resume development loop
allowed-tools: Read, Write
allowed-file-patterns:
  - ".resume-state.json:*"
---

# Cancel Resume Command

Cancel the current resume development loop and preserve state.

## Instructions

1. Read `.resume-state.json` from the current working directory

2. If file doesn't exist or `active: false`:
   ```
   No active resume development loop to cancel.
   ```

3. If active loop exists:

   a. Update the state file:
   ```json
   {
     "active": false,
     "phase": "CANCELLED",
     "completedAt": "<current ISO timestamp>",
     "stoppedReason": "cancelled_by_user"
   }
   ```

   b. Display confirmation:
   ```
   ═══════════════════════════════════════════════════
   RESUME DEVELOPMENT CANCELLED
   ═══════════════════════════════════════════════════

   Loop cancelled at iteration [X].

   State has been preserved in .resume-state.json
   Current resume draft saved.

   To resume later, you can:
   1. Review .resume-state.json for the last state
   2. Start a new loop: /resume-helper:resume-loop "experience.md"

   Files preserved:
   - .resume-state.json (full state)
   - Current resume draft (in state file)
   ═══════════════════════════════════════════════════
   ```

## Notes

- Cancelling preserves all work done so far
- The current resume draft is stored in the state file
- User can manually extract the resume from `.resume-state.json` if needed
- Starting a new loop will prompt to backup or overwrite existing state
