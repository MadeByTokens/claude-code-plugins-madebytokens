---
description: Cancel the active resume development loop
allowed-tools: Read, Write
---

# Cancel Resume Command

Cancel the current resume development loop and preserve state.

## Instructions

1. Read `working/state.json` from the current working directory

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

   All work has been preserved in the working/ directory.

   Files preserved:
   - working/state.json          (loop state)
   - working/writer/output.md    (current resume draft)
   - working/inputs/             (your input files)
   - working/coach/              (coach feedback and questions)
   - working/analysis/           (analysis results)

   To start a new loop:
   1. Optionally backup the working/ directory
   2. Run: /resume-helper:resume-loop "experience.md"

   ═══════════════════════════════════════════════════
   ```

## Notes

- Cancelling preserves all work done so far in the `working/` directory
- The current resume draft is in `working/writer/output.md`
- User can review any agent's output in their respective directories
- Starting a new loop will recreate the working directory
