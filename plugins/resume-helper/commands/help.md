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
    --output <file>       Output path for final resume (default: ./resume_final.md)
    --format <type>       Resume format: traditional, modern, ats (default: ats)

  Examples:
    /resume-helper:resume-loop "experience.md"
    /resume-helper:resume-loop "exp.md" --job "job.md"
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
4. Get resume_final.md and interview_prep.md

────────────────────────────────────────────────────────────────────
```
