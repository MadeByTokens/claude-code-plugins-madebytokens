---
description: Display help and reference for PRD commands, sections, and usage.
---

# PRD Help

The user wants help with the PRD plugin.

## Display Format

```
PRD HELP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMMANDS:

  /prd:start [topic]     Start a new PRD session
                         Options: --from <brainstorm-file.md>

  /prd:section <name>    Jump to a specific section
                         Names: problem, users, stories, functional,
                                nonfunctional, data, ui, api, metrics,
                                acceptance, scope, risks, dependencies,
                                constraints

  /prd:status            Show completion progress for all sections

  /prd:review            Analyze PRD for gaps and issues

  /prd:refine            Iterate on current section with more detail

  /prd:done              Finalize PRD, generate final document, and exit

  /prd:help              Show this help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRD SECTIONS (25 total):

  Foundation (Taste Layer) - FIRST:
  0. Vision & Principles   Soul of the product, non-negotiables

  Core Requirements (1-8):
  1. Problem Statement     Why this needs to exist
  2. Target Users          Who benefits from this
  3. User Stories          As a... I want... So that...
  4. Functional Reqs       Features needed (WHAT, not HOW)
  5. Non-Functional Reqs   Performance, security, accessibility
  6. Data Model            Entities, relationships, constraints
  7. UI/UX Specification   Screens, flows, interactions
  8. API Contract          Endpoints, formats

  Anti-Accidental-Architecture (9-12) - CRITICAL:
  9. Change Analysis       What will change? Config vs hardcode
  10. Architecture Decisions Source of truth, dependencies
  11. Edge Cases & Errors   What happens when things fail?
  12. Testing Strategy      How do we test?

  Planning & Constraints (13-18):
  13. Success Metrics       KPIs, targets
  14. Scope Boundaries      What's in/out of v1
  15. Risks & Mitigations   What could go wrong
  16. Dependencies          External services, libraries
  17. Technical Constraints Platform limits
  18. Evolution Strategy    How will it grow?

  AI Implementation (19-24) - "Any AI Can Build It":
  19. Tech Stack            Exact versions (React 18.2, etc.)
  20. Project Structure     Folder/file layout
  21. Commands              Build, test, deploy commands
  22. Code Style & Examples Concrete code patterns
  23. Git Workflow          Branch naming, commits
  24. AI Agent Boundaries   Always/Ask/Never rules

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW IT WORKS:

  1. Start with /prd:start
  2. Work through sections interactively
  3. For each section:
     - I explain what's needed
     - Ask clarifying questions
     - Draft content
     - You review and approve
  4. Use /prd:status to track progress
  5. Use /prd:review to find gaps
  6. Finalize with /prd:done

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SESSION FILES:

  Working document: prd-[topic]-[timestamp].md
  Final PRD:        prd-[topic]-FINAL.md
  Located in: current working directory

  The working document preserves full history and status markers.
  The final PRD is clean, stakeholder-ready, with executive summary.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIPS:

  • Be specific - vague requirements lead to wrong implementations
  • Include edge cases - what happens when things fail?
  • Define acceptance criteria - how do we know it's done?
  • Quantify where possible - "fast" → "responds in <200ms"
```

## After Help

Use AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "What would you like to do?",
      "header": "Next",
      "multiSelect": false,
      "options": [
        {"label": "Start PRD", "description": "Begin a new PRD session"},
        {"label": "Learn about sections", "description": "Get details on a specific section"},
        {"label": "Continue", "description": "Return to current work"}
      ]
    }
  ]
}
```

## If User Wants Section Details

Provide detailed explanation of the selected section, including:
- Purpose of the section
- What questions it answers
- Example content
- Common mistakes to avoid

## Important

- This command works whether or not a PRD session is active
- If session is active, stay in PRD mode after showing help
- Do NOT write code
