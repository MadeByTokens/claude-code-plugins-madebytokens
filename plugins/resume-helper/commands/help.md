---
description: Show available Resume Helper commands and options
allowed-tools:
---

# Resume Helper - Help

Display the following help information:

```
╔══════════════════════════════════════════════════════════════════╗
║                      RESUME HELPER PLUGIN                        ║
║     Adversarial multi-agent resume development for Claude Code   ║
╚══════════════════════════════════════════════════════════════════╝

COMMANDS
────────────────────────────────────────────────────────────────────

/resume-helper:resume-loop <experience_file> [options]

  Start the adversarial resume development loop.

  Arguments:
    <experience_file>     Path to your experience/background file (required)

  Options:
    --job <file>          Path to job description for targeting
    --max-iterations <n>  Maximum improvement cycles (default: 5)
    --max-pages <n>       Maximum pages: 1, 2, or 3 (default: 1, prompts for confirmation)
    --output <file>       Output path for final resume (default: ./resume_final.md)
    --format <type>       Resume format: traditional, modern, ats (default: ats)

  Examples:
    /resume-helper:resume-loop "experience.md"
    /resume-helper:resume-loop "exp.md" --job "job.md"
    /resume-helper:resume-loop "exp.md" --job "jd.md" --max-pages 2
    /resume-helper:resume-loop "exp.md" --job "jd.md" --max-iterations 3

────────────────────────────────────────────────────────────────────

/resume-helper:resume-status

  Check status of active or completed loop.
  Shows current phase, iteration, and outstanding concerns.

────────────────────────────────────────────────────────────────────

/resume-helper:cancel-resume

  Cancel an active loop. Progress is preserved in .resume-state.json.

────────────────────────────────────────────────────────────────────

/resume-helper:interview-prep [resume_file]

  Generate interview preparation document.

  Arguments:
    [resume_file]         Path to resume (optional - uses last loop result if omitted)

  Output:
    interview_prep.md     Contains likely questions and suggested responses

────────────────────────────────────────────────────────────────────

QUICK START
────────────────────────────────────────────────────────────────────

1. Create experience.md with your raw experience
2. Run: /resume-helper:resume-loop "experience.md"
3. Answer the Coach's clarifying questions
4. Get your output files:
   - resume_final.md           (your polished resume)
   - interview_prep.md         (preparation guide)
   - resume_development_log.md (full audit trail)
   - candidate_additions.md    (your answers to Coach questions)

NOTE: Default is 1-page resume. Use --max-pages 2 or --max-pages 3 for longer resumes.
      Recommended: 1 page (<10 yrs exp), 2 pages (10-20 yrs), 3 pages (executives/academics)

────────────────────────────────────────────────────────────────────

HOW IT WORKS
────────────────────────────────────────────────────────────────────

The loop uses 4 agents with different roles:

  Writer        → Creates/improves the resume (advocates for you)
  Fact-Checker  → Verifies claims against your input (catches hallucinations)
  Interviewer   → Reviews like a hiring manager (finds weaknesses)
  Coach         → Synthesizes feedback and asks clarifying questions

Flow per iteration:
  1. Writer creates resume draft
  2. Fact-Checker verifies all claims (blocks hallucinations)
  3. Interviewer reviews skeptically
  4. Analysis agents check for issues (parallel)
  5. Coach synthesizes and provides guidance

The Fact-Checker ensures every claim in your resume can be traced back
to your original input. If the Writer invents details, they're caught
before reaching the Interviewer.

IMPORTANT: The Writer and Fact-Checker read your original experience
file fresh from disk each time (not from memory). This prevents
context corruption in long conversations.

────────────────────────────────────────────────────────────────────
```
