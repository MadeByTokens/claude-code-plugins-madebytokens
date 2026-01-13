---
description: Check the status of the current resume development loop
allowed-tools: Read
---

# Resume Status Command

Display the current status of the resume development loop.

## Instructions

1. Read `working/state.json` from the current working directory

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
Phase: [WRITING | FACT_CHECK | REVIEWING | ANALYZING | COACHING]
Iteration: [X] of [maxIterations]

Started: [timestamp]
Experience File: working/inputs/experience.md
Job Description: [working/inputs/job_description.md or "Not provided"]

Last Verdict: [verdict or "N/A"]

Working Directory:
  working/
  ├── inputs/              # Your input files
  ├── writer/              # Current resume in output.md
  ├── fact_checker/        # Verification reports
  ├── interviewer/         # Review feedback
  ├── analysis/            # Analysis results
  └── coach/               # Coach assessment and questions

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
- Interview Prep: working/output/interview_prep.md
- Coach Assessment: working/coach/assessment.md

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

The Coach has requested additional information.
See: working/coach/questions.md

Please provide this information, then the loop will continue.
═══════════════════════════════════════════════════
```

## State File Reference

Key fields in `working/state.json`:
- `active`: Whether loop is running
- `phase`: Current phase (INITIALIZED, WRITING, FACT_CHECK, REVIEWING, ANALYZING, COACHING, COMPLETE)
- `iteration`: Current iteration number
- `maxIterations`: Maximum iterations allowed
- `maxPages`: Page limit (1, 2, or 3)
- `maxWords`: Word limit (450, 900, or 1350)
- `lastVerdict`: Most recent coach verdict
- `factCheckAttempts`: Current fact-check retry count
- `startedAt`: When loop started

## Working Directory Files

For more details, check these files:
- `working/writer/output.md` - Current resume draft
- `working/writer/status.md` - Writer status (DONE/BLOCKED)
- `working/fact_checker/verdict.md` - Fact check result (PASS/FAIL)
- `working/interviewer/verdict.md` - Interviewer verdict
- `working/coach/verdict.md` - Coach verdict
- `working/coach/questions.md` - Outstanding questions for user
