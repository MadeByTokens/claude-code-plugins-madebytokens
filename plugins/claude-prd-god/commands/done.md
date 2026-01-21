---
description: Finalize the PRD session, generate final document, and exit PRD mode.
---

# End PRD Session

The user is ready to finalize their PRD and exit PRD mode.

## Actions

1. **Run quick review** to check completeness
2. **Add final summary** to working session file
3. **Generate clean final PRD** (stakeholder-ready document)
4. **Add executive summary** to final PRD
5. **Run end script** to clear state
6. **Display completion summary**
7. **Offer next steps**

## Pre-Exit Review

Before finalizing, do a quick completeness check:

```
FINALIZING PRD

Quick completeness check...

Sections complete: X/25
Taste Layer: [COMPLETE/INCOMPLETE]
Anti-Accidental-Architecture: X/4
AI Implementation: X/6
Critical gaps: [list any empty required sections]
```

If critical sections are empty (Vision & Principles, Problem Statement, User Stories, Functional Requirements, Anti-Accidental-Architecture sections, OR AI Implementation sections), warn:

```
⚠️ WARNING: Some critical sections are incomplete:
- [Section name]: [status]

Proceeding will create an incomplete PRD.
```

Use AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "How would you like to proceed?",
      "header": "Finalize",
      "multiSelect": false,
      "options": [
        {"label": "Finalize anyway", "description": "Export PRD with current state"},
        {"label": "Complete gaps first", "description": "Go back and fill missing sections"},
        {"label": "Cancel", "description": "Stay in PRD mode"}
      ]
    }
  ]
}
```

## Finalizing

If user confirms:

1. **Add Final Summary section** to session file:

```markdown
---

## Final Summary

**PRD Completion Date:** [timestamp]

**Sections Completed:** X/25

**Taste Layer:** Vision & Principles [COMPLETE/INCOMPLETE]

**Anti-Accidental-Architecture:** X/4 (Change Analysis, Architecture Decisions, Edge Cases, Testing Strategy)

**AI Implementation:** X/6 (Tech Stack, Project Structure, Commands, Code Style, Git Workflow, AI Boundaries)

**Key Requirements:**
- [Most important requirement 1]
- [Most important requirement 2]
- [Most important requirement 3]

**Primary User Stories:**
- [US-001]: [title]
- [US-002]: [title]
- [US-003]: [title]

**Known Gaps:**
- [Any incomplete sections or acknowledged limitations]

**Next Steps:**
1. Review with stakeholders
2. Prioritize requirements for v1
3. Begin technical design
4. Implementation planning
```

2. **Generate clean final PRD:**
```bash
PLUGIN_PATH/scripts/generate-final-prd.sh
```

This creates a stakeholder-ready document that:
- Removes all "[To be filled]" placeholders
- Removes "Section Status" markers
- Removes template helper text
- Cleans up empty sections

3. **Add Executive Summary to final PRD:**

Read the generated final PRD file and prepend an Executive Summary section immediately after the title. Write this using the Edit tool:

```markdown
## Executive Summary

**Product:** [Product name from title]

**Vision:** [One sentence from Section 0.1]

**Problem:** [One sentence summary from Section 1]

**Target Users:** [Primary persona from Section 2]

**Key Capabilities:**
- [Top 3-5 functional requirements from Section 4]

**Success Metrics:** [2-3 key metrics from Section 13]

**Scope:** [v1 scope summary from Section 14]

**Technical Approach:** [Framework/stack from Section 19]

---
```

4. **Run end script:**
```bash
PLUGIN_PATH/scripts/end-prd-session.sh
```

5. **Display completion:**

```
PRD SESSION COMPLETE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generated files:

  Working document (full history):
  [session file path]

  Final PRD (stakeholder-ready):
  [final file path]

Summary:
- Sections completed: X/25
- Taste Layer: ✓ (Vision & Principles captured)
- Anti-Accidental-Architecture: X/4 ✓
- AI Implementation: X/6 ✓
- User stories documented: X
- Requirements captured: X

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You have exited PRD mode. Normal Claude behavior resumed.
```

## Next Steps

Use AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "What would you like to do next?",
      "header": "Next",
      "multiSelect": false,
      "options": [
        {"label": "Technical design", "description": "Start planning the architecture"},
        {"label": "Share PRD", "description": "Get the file path to share with team"},
        {"label": "Start implementation", "description": "Begin building based on this PRD"},
        {"label": "Done for now", "description": "Exit and come back later"}
      ]
    }
  ]
}
```

## Important

- This is the ONLY way to exit PRD mode
- Session file is preserved after exit
- State file is deleted (session ends)
- Claude returns to normal behavior after this command
