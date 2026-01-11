---
description: Check the status of the current resume development loop
allowed-tools: Read
allowed-file-patterns:
  - ".resume-state.json:*"
---

# Resume Status Command

Display the current status of the resume development loop.

## Instructions

1. Read `.resume-state.json` from the current working directory

2. If file doesn't exist:
   ```
   No active resume development loop found.

   Start one with: /resume-helper:resume-loop "experience.md"
   ```

3. If file exists, display status based on state:

### Active Loop Display

```
═══════════════════════════════════════════════════
RESUME DEVELOPMENT STATUS
═══════════════════════════════════════════════════

Status: ACTIVE
Phase: [WRITING | REVIEWING | COACHING]
Iteration: [X] of [maxIterations]

Started: [timestamp]
Experience File: [path]
Job Description: [path or "Not provided"]

Last Verdict: [verdict or "N/A"]

Progress:
┌──────────┬─────────────────┬────────────────────┐
│ Iteration│ Verdict         │ Key Changes        │
├──────────┼─────────────────┼────────────────────┤
│ 1        │ NEEDS_GROUNDING │ Initial draft      │
│ 2        │ NEEDS_WORK      │ Added metrics      │
│ ...      │ ...             │ ...                │
└──────────┴─────────────────┴────────────────────┘

Outstanding Concerns:
- [From last interviewer review]
- [...]

Commands:
- Continue: The loop will auto-resume
- Cancel: /resume-helper:cancel-resume
═══════════════════════════════════════════════════
```

### Completed Loop Display

```
═══════════════════════════════════════════════════
RESUME DEVELOPMENT STATUS
═══════════════════════════════════════════════════

Status: COMPLETE
Final Verdict: [READY | MAX_ITERATIONS]
Total Iterations: [X]

Started: [timestamp]
Completed: [timestamp]

Output Files:
- Resume: [output path]
- Interview Prep: interview_prep.md

Summary:
[Brief description of the final state]

To start a new loop: /resume-helper:resume-loop "experience.md"
═══════════════════════════════════════════════════
```

### Blocked Loop Display

```
═══════════════════════════════════════════════════
RESUME DEVELOPMENT STATUS
═══════════════════════════════════════════════════

Status: BLOCKED - Waiting for User Input
Iteration: [X]

The Coach has requested additional information:

[Questions from coach]

Please provide this information, then the loop will continue.
═══════════════════════════════════════════════════
```

## State File Reference

Key fields to display:
- `active`: Whether loop is running
- `phase`: Current phase (WRITING, REVIEWING, COACHING, COMPLETE)
- `iteration`: Current iteration number
- `options.maxIterations`: Maximum iterations allowed
- `lastVerdict`: Most recent coach verdict
- `history`: Array of past iterations with verdicts
- `startedAt`: When loop started
- `completedAt`: When loop finished (if complete)
- `stoppedReason`: Why loop stopped (ready, max_iterations, cancelled, error)
