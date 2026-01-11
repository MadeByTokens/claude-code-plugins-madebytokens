---
description: Start adversarial resume development loop with three agents
allowed-tools: Write, Read, Glob, Grep, Edit, Bash, Task, TodoWrite, AskUserQuestion
---

# Resume Development Loop

You are orchestrating an adversarial three-agent loop to develop a compelling AND honest resume.

## Agents

- **Resume Writer** (Advocate): Creates compelling resume content
- **Interviewer** (Skeptic): Reviews from hiring manager perspective
- **Coach** (Mediator): Synthesizes feedback, ensures honesty

## Step 1: Parse User Input

Extract from user's command:
- `experience_path`: Path to candidate's experience/background file (REQUIRED)
- `--job` or `--jd`: Path to job description file (OPTIONAL)
- `--max-iterations`: Maximum loop iterations (DEFAULT: 5)
- `--output`: Output path for final resume (DEFAULT: ./resume_final.md)
- `--format`: Resume format - traditional, modern, ats (DEFAULT: ats)

Example commands:
```
/resume-loop "my_experience.md"
/resume-loop "experience.md" --job "job_description.md"
/resume-loop "exp.md" --job "jd.md" --max-iterations 3 --output "./my_resume.md"
```

## Step 2: Validate Input Files

### Experience File (required)

1. Display: "📄 Loading experience from: `<experience_path>`"
2. Attempt to read the file using the Read tool
3. **If the file does not exist or cannot be read:**
   - Display: "❌ Experience file not found: `<experience_path>`"
   - Display: "Please check the path and try again."
   - **STOP** - do not continue
4. **If the file is empty:**
   - Display: "❌ Experience file is empty: `<experience_path>`"
   - **STOP** - do not continue
5. Display: "✅ Experience loaded (`<N>` characters)"

### Job Description File (optional)

If `--job` was provided:

1. Display: "📄 Loading job description from: `<job_path>`"
2. Attempt to read the file using the Read tool
3. **If the file does not exist or cannot be read:**
   - Display: "❌ Job description file not found: `<job_path>`"
   - Display: "Please check the path and try again."
   - **STOP** - do not continue
4. **If the file is empty:**
   - Display: "❌ Job description file is empty: `<job_path>`"
   - **STOP** - do not continue
5. Display: "✅ Job description loaded (`<N>` characters)"

## Step 3: Check for Existing Loop

Read `.resume-state.json` if it exists:
- If `active: true`, inform user and ask if they want to continue or start fresh
- If starting fresh, back up old state file

## Step 4: Initialize State

Create `.resume-state.json`:

```json
{
  "active": true,
  "iteration": 0,
  "phase": "INITIALIZED",
  "candidateInput": {
    "experiencePath": "<path>",
    "experience": "<content>",
    "jobDescriptionPath": "<path or null>",
    "jobDescription": "<content or null>"
  },
  "options": {
    "maxIterations": 5,
    "format": "ats",
    "outputPath": "./resume_final.md"
  },
  "currentResume": null,
  "history": [],
  "lastVerdict": null,
  "interviewQuestions": [],
  "startedAt": "<ISO timestamp>",
  "completedAt": null,
  "stoppedReason": null
}
```

## Step 5: Main Loop

```
while iteration < maxIterations AND lastVerdict != "READY":
    iteration++

    === PHASE 1: WRITING ===
    Update state: phase = "WRITING"

    Invoke Resume Writer agent via Task tool:
    - Provide: candidate experience, job description (if any), coach feedback (if any)
    - DO NOT provide: interviewer's raw feedback
    - Agent type: resume-helper:resume-writer

    Save Writer's output to state.currentResume

    === PHASE 2: REVIEWING ===
    Update state: phase = "REVIEWING"

    Invoke Interviewer agent via Task tool:
    - Provide: current resume only, job description (if any)
    - DO NOT provide: candidate's raw experience, writer's notes
    - Agent type: resume-helper:interviewer

    Save Interviewer's review to state.history[iteration].interviewerReview

    === PHASE 3: COACHING ===
    Update state: phase = "COACHING"

    Invoke Coach agent via Task tool:
    - Provide: EVERYTHING - candidate input, resume, interviewer review, history
    - Agent type: resume-helper:coach

    Parse Coach's verdict and feedback
    Update state.lastVerdict

    If verdict == "READY":
        Break loop

    If verdict == "BLOCKED":
        Ask user for additional information via AskUserQuestion (HIGH priority questions)
        Add their response to candidateInput

    If Coach output contains MEDIUM or HIGH priority questions (even if not BLOCKED):
        Present questions to user via AskUserQuestion
        Frame as: "The Coach has some questions that would strengthen your resume:"
        Add their responses to candidateInput for next iteration
        (User can skip questions they don't want to answer)

    Save iteration to history
```

## Step 6: Finalize

When loop completes (READY verdict or max iterations):

1. Update state:
   ```json
   {
     "active": false,
     "phase": "COMPLETE",
     "completedAt": "<ISO timestamp>",
     "stoppedReason": "ready" | "max_iterations"
   }
   ```

2. Write final resume to output path

3. Write interview prep document to `interview_prep.md`

4. Display summary:
   ```
   ═══════════════════════════════════════════════════
   RESUME DEVELOPMENT COMPLETE
   ═══════════════════════════════════════════════════

   Iterations: X
   Final Verdict: [verdict]

   Output Files:
   - Resume: [output path]
   - Interview Prep: interview_prep.md

   Key Improvements Made:
   - [Summary of changes across iterations]

   Interview Questions to Prepare:
   - [Top questions from Interviewer]
   ═══════════════════════════════════════════════════
   ```

## Agent Invocation Templates

### Resume Writer Task

```
You are the Resume Writer agent. Create/improve a resume for this candidate.

## Candidate Experience
<experience content>

## Target Job Description (if provided)
<job description or "Not provided - create a general-purpose resume">

## Previous Coach Feedback (if iterating)
<coach feedback or "This is the first iteration">

## Current Resume (if iterating)
<current resume or "Create initial resume">

Follow your agent instructions to produce an updated resume.
```

### Interviewer Task

```
You are the Interviewer agent. Review this resume as a hiring manager would.

## Resume to Review
<current resume>

## Job Description (if provided)
<job description or "General review - no specific role">

Follow your agent instructions to produce a thorough review.
```

### Coach Task

```
You are the Coach agent. Synthesize the Writer's resume and Interviewer's review.

## Candidate's Original Input
<experience content>

## Target Job Description
<job description or "Not provided">

## Current Resume (from Writer)
<current resume>

## Interviewer's Review
<interviewer review>

## Iteration History
<previous iterations summary>

## Resume File Path (for tools)
<path to the current resume file, e.g., "resume_draft.md">

## Job Description File Path (for tools, if provided)
<path to job description file or "Not provided">

Follow your agent instructions to:
1. **FIRST: Run all helper tools using Bash** to get objective analysis:
   - python tools/detect_vague_claims.py <resume_file_path> --json
   - python tools/detect_buzzwords.py <resume_file_path> --json
   - python tools/ats_compatibility.py <resume_file_path> <jd_file_path> --json (if JD provided)
   - python tools/quantification_helper.py <resume_file_path> --json (if claims need specifics)
2. Incorporate tool findings into your assessment
3. Verify claims against candidate input
4. Translate interviewer concerns into writer guidance
5. **ALWAYS include 2-3+ questions for the candidate** with priority levels (HIGH/MEDIUM/LOW)
   - Even when the resume is improving, there's always something that could be more specific
6. Issue a verdict: READY, NEEDS_STRENGTHENING, NEEDS_GROUNDING, or BLOCKED
   - Do NOT issue READY if high-severity vague claims remain or ATS score < 80
```

## Error Handling

- If any agent fails, save state and inform user
- If candidate input is insufficient, enter BLOCKED state and ask for more info
- If max iterations reached without READY, inform user of remaining concerns

## Important Notes

1. **Information Isolation**: Maintain strict separation - Interviewer never sees raw candidate input
2. **State Persistence**: Always update `.resume-state.json` after each phase
3. **User Communication**: Keep user informed of progress between iterations
4. **Honesty First**: If Coach flags honesty concerns, prioritize those over polish
