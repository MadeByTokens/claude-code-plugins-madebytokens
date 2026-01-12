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
- `--max-pages`: Maximum page length - 1, 2, or 3 (DEFAULT: 1, requires confirmation)
- `--output`: Output path for final resume (DEFAULT: ./resume_final.md)
- `--format`: Resume format - traditional, modern, ats (DEFAULT: ats)

Example commands:
```
/resume-loop "my_experience.md"
/resume-loop "experience.md" --job "job_description.md"
/resume-loop "exp.md" --job "jd.md" --max-pages 2
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

## Step 2.5: Confirm Page Limit

Page-to-word conversion:
- 1 page = 450 words maximum
- 2 pages = 900 words maximum
- 3 pages = 1350 words maximum

### If `--max-pages` was NOT explicitly provided:

1. Display:
   ```
   ════════════════════════════════════════════════════
   PAGE LIMIT CONFIGURATION
   ════════════════════════════════════════════════════

   No --max-pages specified. The default is 1 page (~450 words).

   Recommended page limits:
     1 page  = ~450 words  (recommended for <10 years experience)
     2 pages = ~900 words  (recommended for 10-20 years experience)
     3 pages = ~1350 words (recommended for executives/academics)

   ════════════════════════════════════════════════════
   ```

2. Use AskUserQuestion tool to ask:
   - Question: "Would you like to proceed with the 1-page default, or specify a different limit?"
   - Options: "1 page (default)", "2 pages", "3 pages"

3. Parse response and set:
   - maxPages = 1, 2, or 3 based on selection
   - maxWords = 450, 900, or 1350 respectively

4. Display confirmation:
   ```
   ✅ Using [N]-page limit (~[WORDS] words maximum)
   ```

### If `--max-pages` was explicitly provided:

1. Validate the value is 1, 2, or 3
2. If invalid:
   - Display: "❌ Invalid --max-pages value: `<value>`. Must be 1, 2, or 3."
   - **STOP** - do not continue
3. Set maxWords based on maxPages (450, 900, or 1350)
4. Display: "✅ Page limit set: [N] pages (~[WORDS] words maximum)"

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
    "maxPages": 1,
    "maxWords": 450,
    "format": "ats",
    "outputPath": "./resume_final.md"
  },
  "currentResume": null,
  "history": [],
  "lastVerdict": null,
  "factCheckAttempts": 0,
  "interviewQuestions": [],
  "startedAt": "<ISO timestamp>",
  "completedAt": null,
  "stoppedReason": null
}
```

## Step 4.5: Initialize Supporting Files

### A. Create Candidate Additions File

Create `candidate_additions.md` to store additional information provided by the user during the process:

```markdown
# Candidate Additions

Additional information provided during resume development.
This file is read fresh by the Writer and Fact-Checker alongside the original experience file.

---

```

This file will be appended to each time the user answers Coach questions.

### B. Create Development Log

Create `resume_development_log.md` to track the full development process:

```markdown
# Resume Development Log

**Started:** <ISO timestamp>
**Experience File:** <experiencePath>
**Job Description:** <jobDescriptionPath or "None provided">
**Page Limit:** <maxPages> pages (<maxWords> words)
**Max Iterations:** <maxIterations>

---

## Process Trail

```

This log will be appended to throughout the process, giving the user a complete audit trail.

**Log entry format:**
```markdown
### [TIMESTAMP] Iteration N - Phase Name

**Event:** <what happened>
**Details:** <specifics>
**Outcome:** <result>

---
```

## Step 5: Main Loop

**CRITICAL: This is an ITERATIVE LOOP. You MUST repeat Phases 1→1.5→2→3→4 until exit condition is met.**

Exit conditions (check AFTER each complete iteration):
- `lastVerdict == "READY"` → Exit loop, proceed to Step 6
- `iteration >= maxIterations` → Exit loop, proceed to Step 6

**If neither exit condition is met, you MUST start the next iteration.**

═══════════════════════════════════════════════════════════════════════════════
ITERATION START: Increment iteration counter, then execute Phases 1, 1.5, 2, 2.5, 3
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1 of 5: WRITING                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Update state: phase = "WRITING"                                             │
│                                                                             │
│ Invoke Resume Writer agent via Task tool:                                   │
│ - Provide: experience FILE PATH (not content!), job description, coach      │
│   feedback, current resume (if iterating), page/word limits                 │
│ - The Writer will READ BOTH files fresh:                                    │
│   1. Original experience file                                               │
│   2. candidate_additions.md (user answers to questions)                     │
│ - DO NOT provide: interviewer's raw feedback, experience content in prompt  │
│ - Agent type: resume-helper:resume-writer                                   │
│                                                                             │
│ Save Writer's output to state.currentResume and to resume_draft.md          │
│                                                                             │
│ **LOG:** Append to resume_development_log.md:                               │
│   "### [TIME] Iteration N - WRITING"                                        │
│   "Writer created/updated resume draft. Word count: X words."               │
│                                                                             │
│ → When complete, IMMEDIATELY CONTINUE to Phase 1.5                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1.5 of 5: FACT-CHECK (Hallucination Detection)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ Update state: phase = "FACT_CHECK"                                          │
│                                                                             │
│ **This phase catches hallucinations before the resume reaches the           │
│ Interviewer. The Fact Checker reads all source files fresh.**               │
└─────────────────────────────────────────────────────────────────────────────┘

**Initialize fact-check attempt counter:** If not set, set `factCheckAttempts = 0`

**Invoke Fact Checker agent via Task tool:**
- Agent type: `resume-helper:fact-checker`
- Prompt:
  ```
  Verify the resume against the candidate's original input.

  Experience file path: [state.candidateInput.experiencePath]
  Candidate additions file: candidate_additions.md
  Resume file path: resume_draft.md

  Read ALL THREE files fresh using the Read tool. Do NOT rely on context.
  Check every specific claim in the resume for a source in EITHER the original
  experience file OR the candidate_additions.md file (user answers to questions).

  Follow your instructions and output a Fact Check Report with verdict PASS or FAIL.
  ```

**Handle Fact Checker verdict:**

┌─────────────────────────────────────────────────────────────────────────────┐
│ IF VERDICT == "PASS":                                                       │
│                                                                             │
│ Display: "✅ Fact check passed. No hallucinations detected."                │
│ Reset: factCheckAttempts = 0                                                │
│                                                                             │
│ **LOG:** Append to resume_development_log.md:                               │
│   "### [TIME] Iteration N - FACT-CHECK"                                     │
│   "**Result:** PASS - All claims verified against original input."          │
│                                                                             │
│ → CONTINUE to Phase 2: REVIEWING                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ IF VERDICT == "FAIL":                                                       │
│                                                                             │
│ Increment: factCheckAttempts += 1                                           │
│ Display: "❌ Fact check failed. Hallucinations detected (attempt           │
│          [factCheckAttempts]/3)"                                            │
│                                                                             │
│ Display the list of hallucinations from the Fact Checker's report.          │
│                                                                             │
│ **LOG:** Append to resume_development_log.md:                               │
│   "### [TIME] Iteration N - FACT-CHECK"                                     │
│   "**Result:** FAIL (attempt [factCheckAttempts]/3)"                        │
│   "**Hallucinations found:**"                                               │
│   - List each hallucinated claim from report                                │
│                                                                             │
│ IF factCheckAttempts < 3:                                                   │
│   - Send hallucination list back to Writer as feedback                      │
│   - **LOG:** "Returning to Writer for correction."                          │
│   - → RETURN to Phase 1: WRITING (retry with feedback)                      │
│                                                                             │
│ IF factCheckAttempts >= 3:                                                  │
│   - Display: "⚠️ Writer failed fact-check 3 times. Escalating to user."    │
│   - **LOG:** "Escalating to user after 3 failed attempts."                  │
│   - Use AskUserQuestion to show hallucinations and ask user:                │
│     "The Writer keeps adding details not in your input. Options:"           │
│     1. "Provide additional details" (user adds info to candidateInput)      │
│     2. "Remove the hallucinated claims" (instruct Writer to use vague       │
│        language)                                                            │
│     3. "Accept current resume anyway" (proceed with warnings)               │
│   - **LOG:** "User chose: [option selected]"                                │
│   - **If user chose option 1 (provide details):**                           │
│     - **SAVE TO FILE:** Append to `candidate_additions.md`:                 │
│       "### [TIMESTAMP] Iteration N - Fact-Check Clarification"              │
│       "[details user provided]"                                             │
│   - Handle user's choice and proceed accordingly                            │
│   - Reset: factCheckAttempts = 0                                            │
│   - → Based on choice: RETURN to Phase 1 or CONTINUE to Phase 2             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2 of 5: REVIEWING                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Update state: phase = "REVIEWING"                                           │
│                                                                             │
│ Invoke Interviewer agent via Task tool:                                     │
│ - Provide: current resume only, job description (if any)                    │
│ - DO NOT provide: candidate's raw experience, writer's notes                │
│ - Agent type: resume-helper:interviewer                                     │
│                                                                             │
│ Save Interviewer's review to state.history[iteration].interviewerReview     │
│                                                                             │
│ **LOG:** Append to resume_development_log.md:                               │
│   "### [TIME] Iteration N - REVIEWING"                                      │
│   "Interviewer reviewed resume."                                            │
│   "**Key concerns raised:** [summarize top 2-3 concerns]"                   │
│                                                                             │
│ → When complete, IMMEDIATELY CONTINUE to Phase 3                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3 of 5: ANALYSIS                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Update state: phase = "ANALYZING"                                           │
│                                                                             │
│ **Run analysis agents IN PARALLEL using Task tool for faster execution.**   │
└─────────────────────────────────────────────────────────────────────────────┘

**DISPLAY THIS MESSAGE TO USER:** "🔄 ANALYSIS PHASE: Running analysis agents in parallel..."

**CRITICAL: Launch ALL applicable Task agents in a SINGLE message (parallel execution).**

Determine which agents to run:
- **ALWAYS run:** analyze-vague-claims, analyze-buzzwords, check-ats-compatibility
- **CONDITIONALLY run:** suggest-quantification (ONLY if iteration > 1 OR lastVerdict == NEEDS_GROUNDING)

**IMPORTANT: Use these values from state for all prompts:**
- Resume file: Always use `resume_draft.md` (the file Writer saves to)
- Job description CONTENT: Use `state.candidateInput.jobDescription` (already loaded)
- Max pages: Use `state.options.maxPages`

**Launch these Task agents in parallel (single message, multiple Task tool calls):**

**[AGENT 1]** Task with subagent_type: `resume-helper:analyze-vague-claims`
- Prompt: "Analyze the resume at resume_draft.md for vague claims. Follow your instructions and output the analysis."
- Save output to: vague_claims_results

**[AGENT 2]** Task with subagent_type: `resume-helper:analyze-buzzwords`
- Prompt: "Analyze the resume at resume_draft.md for buzzwords. Follow your instructions and output the analysis."
- Save output to: buzzwords_results

**[AGENT 3]** Task with subagent_type: `resume-helper:check-ats-compatibility`
- Prompt: Include the following in your prompt:
  ```
  Check ATS compatibility for the resume at resume_draft.md.
  Max pages: [maxPages from state.options.maxPages]

  Job Description (for keyword matching):
  [Paste the CONTENT from state.candidateInput.jobDescription here, or "No job description provided" if null]

  Follow your instructions and output the analysis.
  ```
- Save output to: ats_results

**[AGENT 4 - CONDITIONAL]** Task with subagent_type: `resume-helper:suggest-quantification`
- Only include this Task if: iteration > 1 OR lastVerdict == NEEDS_GROUNDING
- Prompt: "Suggest quantification improvements for the resume at resume_draft.md. Follow your instructions and output the suggestions."
- Save output to: quantification_results

If suggest-quantification was not run, set: quantification_results = "Not run this iteration (first iteration)"

**After all parallel Tasks complete, display:** "✅ All analysis complete. Proceeding to coaching phase..."

Combine all results into analysis_results string for Coach.

**LOG:** Append to resume_development_log.md:
```
### [TIME] Iteration N - ANALYSIS

**Vague Claims:** [score]/100 ([high] high, [medium] medium, [low] low severity)
**Buzzwords:** Clarity score [score]/100
**ATS Compatibility:** [score]/100, [X] words ([within/over] limit)
**Quantification:** [run/skipped]
```

→ When ALL Tasks complete, IMMEDIATELY CONTINUE to Phase 4

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4 of 5: COACHING                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Update state: phase = "COACHING"                                            │
│                                                                             │
│ Invoke Coach agent via Task tool:                                           │
│ - Provide: candidate input (already verified by Fact-Checker), resume,      │
│   interviewer review, history, AND analysis_results                         │
│ - Agent type: resume-helper:coach                                           │
│                                                                             │
│ Parse Coach's verdict and feedback                                          │
│ Update state.lastVerdict                                                    │
│ Save iteration to history                                                   │
│                                                                             │
│ **LOG:** Append to resume_development_log.md:                               │
│   "### [TIME] Iteration N - COACHING"                                       │
│   "**Verdict:** [READY/NEEDS_STRENGTHENING/NEEDS_GROUNDING/BLOCKED]"        │
│   "**Summary:** [Coach's 2-3 sentence summary]"                             │
│   "**Questions for candidate:** [count] questions asked"                    │
└─────────────────────────────────────────────────────────────────────────────┘

**After Phase 4 completes, handle verdict and questions:**

**FIRST: Show the current resume draft to the user** (so they have context for questions):

Display:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CURRENT RESUME DRAFT (Iteration [N])                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

Then read and display the contents of `resume_draft.md` to the user.

**THEN: Handle questions based on verdict:**

1. **If verdict == "BLOCKED":**
   - Ask user for additional information via AskUserQuestion (HIGH priority questions)
   - Include the resume quote from the Coach's question table so user knows what's being asked
   - Add their response to candidateInput
   - **SAVE TO FILE:** Append to `candidate_additions.md`:
     ```markdown
     ### [TIMESTAMP] Iteration N - User Response (BLOCKED)

     **Question:** [the question asked]
     **Answer:** [user's response]

     ---
     ```
   - **LOG:** "**User provided additional info:** [summary of what user provided]"
   - → Then continue to EXIT CHECK below

2. **If Coach output contains MEDIUM or HIGH priority questions (even if not BLOCKED):**
   - Present questions to user via AskUserQuestion
   - Frame as: "The Coach has some questions that would strengthen your resume:"
   - Include the resume quote from the Coach's question table so user knows what's being asked
   - Add their responses to candidateInput for next iteration
   - (User can skip questions they don't want to answer)
   - **SAVE TO FILE:** For each answered question, append to `candidate_additions.md`:
     ```markdown
     ### [TIMESTAMP] Iteration N - User Response

     **Question:** [the question asked]
     **Answer:** [user's response]

     ---
     ```
   - **LOG:** "**User answered [X] questions:** [brief summary of answers]"
   - → Then continue to EXIT CHECK below

3. **If no questions to ask:**
   - **LOG:** "No questions asked this iteration."
   - → Continue directly to EXIT CHECK below

═══════════════════════════════════════════════════════════════════════════════
EXIT CHECK: Evaluate whether to continue looping or finalize
═══════════════════════════════════════════════════════════════════════════════

Check these conditions IN ORDER:

┌─────────────────────────────────────────────────────────────────────────────┐
│ CONDITION 1: Is verdict "READY"?                                            │
│                                                                             │
│ If YES → EXIT LOOP, proceed to Step 6: Finalize                             │
│ If NO  → Continue to Condition 2                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ CONDITION 2: Has iteration reached maxIterations?                           │
│                                                                             │
│ If YES → EXIT LOOP, proceed to Step 6: Finalize                             │
│ If NO  → Continue to NEXT ITERATION                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ NEXT ITERATION: Neither exit condition met                                  │
│                                                                             │
│ **You MUST loop back to PHASE 1: WRITING to start the next iteration.**     │
│                                                                             │
│ → LOOP BACK to "ITERATION START" above and repeat Phases 1→1.5→2→3→4        │
└─────────────────────────────────────────────────────────────────────────────┘

## Step 6: Finalize

**You have exited the loop. Now complete ALL 4 finalization steps in sequence.**

┌─────────────────────────────────────────────────────────────────────────────┐
│ FINALIZE STEP 1 of 4: Update State                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Update .resume-state.json with:                                             │
│   {                                                                         │
│     "active": false,                                                        │
│     "phase": "COMPLETE",                                                    │
│     "completedAt": "<ISO timestamp>",                                       │
│     "stoppedReason": "ready" | "max_iterations"                             │
│   }                                                                         │
│                                                                             │
│ → When complete, CONTINUE to Finalize Step 2                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ FINALIZE STEP 2 of 4: Write Final Resume                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Write the final resume to the output path (default: ./resume_final.md)      │
│                                                                             │
│ → When complete, CONTINUE to Finalize Step 3                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ FINALIZE STEP 3 of 4: Write Interview Prep                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ Write interview prep document to `interview_prep.md`                        │
│                                                                             │
│ → When complete, CONTINUE to Finalize Step 4                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ FINALIZE STEP 4 of 4: Complete Log and Display Summary                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ **First, append final summary to resume_development_log.md:**               │
│                                                                             │
│ ```markdown                                                                 │
│ ---                                                                         │
│                                                                             │
│ ## Final Summary                                                            │
│                                                                             │
│ **Completed:** <ISO timestamp>                                              │
│ **Total Iterations:** X                                                     │
│ **Final Verdict:** [READY / MAX_ITERATIONS_REACHED]                         │
│ **Exit Reason:** [ready / max_iterations]                                   │
│                                                                             │
│ ### Output Files                                                            │
│ - Resume: [output path]                                                     │
│ - Interview Prep: interview_prep.md                                         │
│ - Development Log: resume_development_log.md                                │
│ - Candidate Additions: candidate_additions.md                               │
│                                                                             │
│ ### Key Improvements Made                                                   │
│ [Summary of main changes across all iterations]                             │
│                                                                             │
│ ### Fact-Check Summary                                                      │
│ - Total fact-check attempts: [count]                                        │
│ - Hallucinations caught and corrected: [count]                              │
│                                                                             │
│ ### Final Scores                                                            │
│ - Vague Claims: [score]/100                                                 │
│ - Buzzwords: [score]/100                                                    │
│ - ATS Compatibility: [score]/100                                            │
│ - Word Count: [X] / [limit] words                                           │
│ ```                                                                         │
│                                                                             │
│ **Then display the completion summary to the user:**                                 │
│                                                                             │
│   ═══════════════════════════════════════════════════                       │
│   RESUME DEVELOPMENT COMPLETE                                               │
│   ═══════════════════════════════════════════════════                       │
│                                                                             │
│   Iterations: X                                                             │
│   Final Verdict: [verdict]                                                  │
│                                                                             │
│   Output Files:                                                             │
│   - Resume: [output path]                                                   │
│   - Interview Prep: interview_prep.md                                       │
│   - Development Log: resume_development_log.md                              │
│   - Candidate Additions: candidate_additions.md                             │
│                                                                             │
│   Key Improvements Made:                                                    │
│   - [Summary of changes across iterations]                                  │
│                                                                             │
│   Interview Questions to Prepare:                                           │
│   - [Top questions from Interviewer]                                        │
│   ═══════════════════════════════════════════════════                       │
│                                                                             │
│ → DONE. Resume development loop complete.                                   │
└─────────────────────────────────────────────────────────────────────────────┘

## Agent Invocation Templates

### Resume Writer Task

```
You are the Resume Writer agent. Create/improve a resume for this candidate.

## IMPORTANT: Read Experience Files Fresh

You MUST read the candidate's files using the Read tool before writing anything.
Do NOT use any experience content from context - read the files fresh.

Experience file path: [state.candidateInput.experiencePath]
Candidate additions file: candidate_additions.md

## Target Job Description (if provided)
<job description or "Not provided - create a general-purpose resume">

## Previous Coach Feedback (if iterating)
<coach feedback or "This is the first iteration">

## Current Resume (if iterating)
<current resume or "Create initial resume">

## Page/Word Limit
Maximum: [maxPages] pages ([maxWords] words)

Follow your agent instructions:
1. FIRST: Read the experience file using Read tool
2. SECOND: Read candidate_additions.md (contains user answers to Coach questions)
3. THEN: Create/update the resume using ONLY what you read from BOTH files
4. Save the resume to resume_draft.md
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

## Candidate's Original Input (verified by Fact-Checker)
<experience content from state.candidateInput.experience>

## Target Job Description
<job description or "Not provided">

## Current Resume (from Writer)
<current resume>

## Interviewer's Review
<interviewer review>

## Iteration History
<previous iterations summary>

## Page/Word Limit
Maximum: [maxPages] pages ([maxWords] words)

## Analysis Results

The following analysis was performed on the current resume:

### Vague Claims Analysis
<vague_claims_results>

### Buzzwords Analysis
<buzzwords_results>

### ATS Compatibility
<ats_results>

### Quantification Suggestions (if available)
<quantification_results or "Not run this iteration">

---

Follow your agent instructions to:
1. Incorporate the analysis results above into your Tool Analysis Results table
2. Verify claims against candidate input
3. Translate interviewer concerns into writer guidance
4. **ALWAYS include 2-3+ questions for the candidate** with priority levels (HIGH/MEDIUM/LOW)
   - Even when the resume is improving, there's always something that could be more specific
5. Issue a verdict: READY, NEEDS_STRENGTHENING, NEEDS_GROUNDING, or BLOCKED
   - Do NOT issue READY if high-severity vague claims remain, ATS score < 80, or resume exceeds page limit
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
