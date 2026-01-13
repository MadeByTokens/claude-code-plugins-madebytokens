---
description: Start adversarial resume development loop with four agents
allowed-tools: Write, Read, Glob, Grep, Edit, Bash, Task, TodoWrite, AskUserQuestion
---

# Resume Development Loop (Thin Orchestrator)

You are orchestrating an adversarial four-agent loop to develop a compelling AND honest resume.

**CRITICAL: This orchestrator uses FILE-BASED message passing to minimize context usage.**
- Agents read inputs from files and write outputs to files
- You only read small verdict/status files, NOT full outputs
- You pass file paths to agents, NOT file contents

## Agents

- **Resume Writer** (Advocate): Creates compelling resume content
- **Fact Checker** (Gatekeeper): Catches hallucinations before Interviewer
- **Interviewer** (Skeptic): Reviews from hiring manager perspective
- **Coach** (Mediator): Synthesizes feedback, ensures honesty

## Working Directory Structure

All agents read and write to a `working/` directory:

```
working/
├── inputs/                      # Read-only after setup
│   ├── experience.md            # Original candidate experience
│   ├── job_description.md       # JD (optional)
│   └── candidate_additions.md   # User answers (append-only)
├── writer/
│   ├── output.md                # Resume draft
│   ├── notes.md                 # Writer notes
│   └── status.md                # "DONE" or "BLOCKED: reason"
├── fact_checker/
│   ├── report.md                # Full verification report
│   └── verdict.md               # "PASS" or "FAIL"
├── interviewer/
│   ├── review.md                # Full review
│   └── verdict.md               # "STRONG_CANDIDATE/NEEDS_WORK/RED_FLAGS"
├── analysis/
│   ├── vague_claims.md
│   ├── buzzwords.md
│   ├── ats_compatibility.md
│   └── quantification.md
├── coach/
│   ├── assessment.md            # Full assessment
│   ├── feedback.md              # Feedback for Writer
│   ├── questions.md             # Questions for user
│   └── verdict.md               # "READY/NEEDS_STRENGTHENING/etc"
├── output/
│   ├── resume_final.md
│   └── interview_prep.md
└── state.json                   # Loop state
```

## Step 1: Parse User Input

Extract from user's command:
- `experience_path`: Path to candidate's experience/background file (REQUIRED)
- `--job` or `--jd`: Path to job description file (OPTIONAL)
- `--max-iterations`: Maximum loop iterations (DEFAULT: 5)
- `--max-pages`: Maximum page length - 1, 2, or 3 (DEFAULT: 1, requires confirmation)
- `--output`: Output path for final resume (DEFAULT: ./resume_final.md)
- `--premium`: Use Opus model for Coach agent for higher quality synthesis (DEFAULT: false)

Example commands:
```
/resume-loop "my_experience.md"
/resume-loop "experience.md" --job "job_description.md"
/resume-loop "exp.md" --job "jd.md" --max-pages 2
/resume-loop "exp.md" --job "jd.md" --premium
```

## Step 2: Validate Input Files

### Experience File (required)

1. Display: "Loading experience from: `<experience_path>`"
2. Read the file using the Read tool
3. If file not found or empty: Display error and **STOP**
4. Display: "Experience loaded (`<N>` characters)"

### Job Description File (optional)

If `--job` was provided:
1. Display: "Loading job description from: `<job_path>`"
2. Read the file - if not found, display error and **STOP**
3. Display: "Job description loaded (`<N>` characters)"

## Step 2.5: Confirm Page Limit

Page-to-word conversion:
- 1 page = 450 words maximum
- 2 pages = 900 words maximum
- 3 pages = 1350 words maximum

If `--max-pages` was NOT provided:
1. Use AskUserQuestion to ask:
   - "No --max-pages specified. What page limit would you like?"
   - Options: "1 page (~450 words)", "2 pages (~900 words)", "3 pages (~1350 words)"
2. Set maxPages and maxWords based on selection

## Step 3: Setup Working Directory

Create the working directory structure:

```
Bash: mkdir -p working/inputs working/writer working/fact_checker working/interviewer working/analysis working/coach working/output
```

Copy input files to working directory:
- Copy experience file content to `working/inputs/experience.md`
- Copy job description content to `working/inputs/job_description.md` (if provided)
- Create empty `working/inputs/candidate_additions.md`

## Step 4: Initialize State

Create `working/state.json`:

```json
{
  "active": true,
  "iteration": 0,
  "phase": "INITIALIZED",
  "maxIterations": 5,
  "maxPages": 1,
  "maxWords": 450,
  "outputPath": "./resume_final.md",
  "premium": false,
  "lastVerdict": null,
  "factCheckAttempts": 0,
  "startedAt": "<ISO timestamp>"
}
```

If `--premium` was specified, set `"premium": true` and display: "Premium mode enabled: Coach will use Opus model."

## Step 5: Main Loop

**CRITICAL: This is an ITERATIVE LOOP. Repeat until exit condition is met.**

Exit conditions:
- `lastVerdict == "READY"` → Exit, proceed to Step 6
- `iteration >= maxIterations` → Exit, proceed to Step 6

═══════════════════════════════════════════════════════════════════════════════
ITERATION START
═══════════════════════════════════════════════════════════════════════════════

1. Increment iteration in state.json
2. Display: "Starting iteration [N] of [maxIterations]..."

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: WRITING                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Update state.json: phase = "WRITING"                                        │
│                                                                             │
│ Invoke Writer agent via Task tool:                                          │
│   subagent_type: "resume-helper:resume-writer"                              │
│   prompt: "Follow your file-based I/O instructions. Read inputs from        │
│            working/inputs/, write outputs to working/writer/."              │
│                                                                             │
│ After Task completes:                                                       │
│   Read ONLY: working/writer/status.md (tiny file)                           │
│   Check if "DONE" or "BLOCKED"                                              │
│   If BLOCKED: Handle error                                                  │
│                                                                             │
│ Display: "Writer complete."                                                 │
│ → Continue to Phase 1.5                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1.5: FACT-CHECK                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Update state.json: phase = "FACT_CHECK"                                     │
│                                                                             │
│ Invoke Fact Checker agent via Task tool:                                    │
│   subagent_type: "resume-helper:fact-checker"                               │
│   prompt: "Follow your file-based I/O instructions. Read inputs and         │
│            resume, write report and verdict to working/fact_checker/."      │
│                                                                             │
│ After Task completes:                                                       │
│   Read ONLY: working/fact_checker/verdict.md (single line)                  │
│                                                                             │
│ IF VERDICT == "PASS":                                                       │
│   Reset factCheckAttempts to 0                                              │
│   Display: "Fact check passed."                                             │
│   → Continue to Phase 2                                                     │
│                                                                             │
│ IF VERDICT == "FAIL":                                                       │
│   Increment factCheckAttempts                                               │
│   IF factCheckAttempts < 3:                                                 │
│     Display: "Fact check failed (attempt [N]/3). Retrying writer..."        │
│     → Return to Phase 1 (retry)                                             │
│   IF factCheckAttempts >= 3:                                                │
│     Read: working/fact_checker/report.md (need to show user)                │
│     Ask user via AskUserQuestion for resolution                             │
│     Save user response to working/inputs/candidate_additions.md             │
│     Reset factCheckAttempts to 0                                            │
│     → Return to Phase 1 or continue based on user choice                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: REVIEWING                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Update state.json: phase = "REVIEWING"                                      │
│                                                                             │
│ Invoke Interviewer agent via Task tool:                                     │
│   subagent_type: "resume-helper:interviewer"                                │
│   prompt: "Follow your file-based I/O instructions. Read resume from        │
│            working/writer/output.md, write review to working/interviewer/." │
│                                                                             │
│ After Task completes:                                                       │
│   Read ONLY: working/interviewer/verdict.md (single line)                   │
│   Display: "Interviewer verdict: [verdict]"                                 │
│                                                                             │
│ → Continue to Phase 3                                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: ANALYSIS (Parallel)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Update state.json: phase = "ANALYZING"                                      │
│                                                                             │
│ Display: "Running analysis agents in parallel..."                           │
│                                                                             │
│ Launch ALL analysis agents in a SINGLE message (parallel execution):        │
│                                                                             │
│ Task 1: subagent_type: "resume-helper:analyze-vague-claims"                 │
│   prompt: "Follow your file-based I/O instructions."                        │
│                                                                             │
│ Task 2: subagent_type: "resume-helper:analyze-buzzwords"                    │
│   prompt: "Follow your file-based I/O instructions."                        │
│                                                                             │
│ Task 3: subagent_type: "resume-helper:check-ats-compatibility"              │
│   prompt: "Follow your file-based I/O instructions."                        │
│                                                                             │
│ Task 4 (CONDITIONAL - only if iteration > 1 OR lastVerdict == NEEDS_GROUNDING): │
│   subagent_type: "resume-helper:suggest-quantification"                     │
│   prompt: "Follow your file-based I/O instructions."                        │
│                                                                             │
│ After ALL Tasks complete:                                                   │
│   Display: "Analysis complete."                                             │
│   (Do NOT read analysis files - Coach will read them)                       │
│                                                                             │
│ → Continue to Phase 4                                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: COACHING                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Update state.json: phase = "COACHING"                                       │
│                                                                             │
│ Invoke Coach agent via Task tool:                                           │
│   subagent_type: "resume-helper:coach-premium" (if premium==true)           │
│                  "resume-helper:coach" (if premium==false)                  │
│   prompt: "Follow your file-based I/O instructions. Read all inputs         │
│            and analysis files, write outputs to working/coach/."            │
│                                                                             │
│ After Task completes:                                                       │
│   Read ONLY: working/coach/verdict.md (single line)                         │
│   Update state.json: lastVerdict = verdict                                  │
│   Display: "Coach verdict: [verdict]"                                       │
└─────────────────────────────────────────────────────────────────────────────┘

**After Phase 4, handle questions and check exit:**

1. **Show current resume to user:**
   - Read and display `working/writer/output.md`
   - This gives user context for questions

2. **Handle questions:**
   - Read `working/coach/questions.md`
   - If questions exist:
     - Present HIGH priority questions (required if verdict is BLOCKED)
     - Present MEDIUM priority questions (optional)
     - Use AskUserQuestion tool
     - Append user answers to `working/inputs/candidate_additions.md`:
       ```markdown
       ### [TIMESTAMP] Iteration N - User Response

       **Question:** [question asked]
       **Answer:** [user's response]

       ---
       ```

3. **Check exit conditions:**
   - If `lastVerdict == "READY"` → EXIT LOOP, go to Step 6
   - If `iteration >= maxIterations` → EXIT LOOP, go to Step 6
   - Otherwise → LOOP BACK to ITERATION START

## Step 6: Finalize

**FINALIZE STEP 1: Update State**
- Update `working/state.json`: active=false, phase="COMPLETE"

**FINALIZE STEP 2: Write Final Resume**
- Copy `working/writer/output.md` to output path (default: ./resume_final.md)

**FINALIZE STEP 3: Generate Interview Prep**
- Read `working/coach/assessment.md` for interview questions
- Write `working/output/interview_prep.md`

**FINALIZE STEP 4: Display Summary**

```
═══════════════════════════════════════════════════
RESUME DEVELOPMENT COMPLETE
═══════════════════════════════════════════════════

Iterations: [N]
Final Verdict: [verdict]

Output Files:
- Resume: [output path]
- Interview Prep: working/output/interview_prep.md

═══════════════════════════════════════════════════
```

## Agent Invocation Templates

**CRITICAL: Keep prompts minimal. Agents know their file paths from their instructions.**

### Resume Writer
```
subagent_type: "resume-helper:resume-writer"
prompt: "Follow your file-based I/O instructions. Read inputs from working/inputs/, read coach feedback from working/coach/feedback.md if it exists, write outputs to working/writer/."
```

### Fact Checker
```
subagent_type: "resume-helper:fact-checker"
prompt: "Follow your file-based I/O instructions. Read inputs from working/inputs/, read resume from working/writer/output.md, write outputs to working/fact_checker/."
```

### Interviewer
```
subagent_type: "resume-helper:interviewer"
prompt: "Follow your file-based I/O instructions. Read resume from working/writer/output.md, read JD from working/inputs/job_description.md if it exists, write outputs to working/interviewer/."
```

### Analysis Agents
```
subagent_type: "resume-helper:analyze-vague-claims"
prompt: "Follow your file-based I/O instructions."

subagent_type: "resume-helper:analyze-buzzwords"
prompt: "Follow your file-based I/O instructions."

subagent_type: "resume-helper:check-ats-compatibility"
prompt: "Follow your file-based I/O instructions."

subagent_type: "resume-helper:suggest-quantification"
prompt: "Follow your file-based I/O instructions."
```

### Coach
```
# Standard mode (default):
subagent_type: "resume-helper:coach"
prompt: "Follow your file-based I/O instructions. Read all input files, analysis results, and interviewer review. Write outputs to working/coach/."

# Premium mode (when --premium flag is used):
subagent_type: "resume-helper:coach-premium"
prompt: "Follow your file-based I/O instructions. Read all input files, analysis results, and interviewer review. Write outputs to working/coach/."
```

**Premium Mode:** When `--premium` is enabled, use `resume-helper:coach-premium` instead of `resume-helper:coach`. The premium agent uses Claude Opus for higher quality synthesis and more nuanced judgment calls.

## Context Savings

This file-based architecture reduces context usage. The orchestrator stays lean by:
1. Only reading small verdict/status files (not full outputs)
2. Passing minimal prompts to agents
3. Letting agents read/write their own files
4. Never holding full resume/review content in context

## Error Handling

- If any agent fails to write its status/verdict file: Check the agent's output for errors
- If agent writes "BLOCKED" status: Read the associated notes/report file for details
- If max iterations reached without READY: Display final resume and remaining concerns from coach/assessment.md

## Important Notes

1. **Information Isolation**: Interviewer only reads resume file, not candidate input files
2. **State Persistence**: Always update state.json after each phase
3. **User Communication**: Keep user informed with brief status messages
4. **File-Based Everything**: Agents handle all the heavy lifting via files
