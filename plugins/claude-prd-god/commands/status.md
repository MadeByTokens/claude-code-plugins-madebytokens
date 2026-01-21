---
description: Show current PRD session progress including section completion status.
---

# PRD Status

The user wants to see their progress on the PRD.

## Actions

1. **Read `.prd-state`** to get current state
2. **Read session file** to assess section completeness
3. **Display status overview**

## Display Format

```
PRD STATUS

Topic: [topic from state]
Source: [brainstorm file or "None"]
Started: [timestamp]
Current Section: [current section name]

Section Progress:

Foundation (Taste Layer):
✓ Vision & Principles    [COMPLETE] ← Human judgment captured

Core Requirements:
✓ Problem Statement       [COMPLETE]
✓ Target Users           [COMPLETE]
→ User Stories           [IN PROGRESS]
○ Functional Requirements [NOT STARTED]
○ Non-Functional Reqs    [NOT STARTED]
○ Data Model             [NOT STARTED]
○ UI/UX Specification    [NOT STARTED]
○ API Contract           [NOT STARTED]

Anti-Accidental-Architecture (CRITICAL):
○ Change Analysis        [NOT STARTED]
○ Architecture Decisions [NOT STARTED]
○ Edge Cases & Errors    [NOT STARTED]
○ Testing Strategy       [NOT STARTED]

Planning & Constraints:
○ Success Metrics        [NOT STARTED]
○ Scope Boundaries       [NOT STARTED]
○ Risks & Mitigations    [NOT STARTED]
○ Dependencies           [NOT STARTED]
○ Technical Constraints  [NOT STARTED]
○ Evolution Strategy     [NOT STARTED]

AI Implementation ("Any AI Can Build It"):
○ Tech Stack             [NOT STARTED]
○ Project Structure      [NOT STARTED]
○ Commands               [NOT STARTED]
○ Code Style & Examples  [NOT STARTED]
○ Git Workflow           [NOT STARTED]
○ AI Agent Boundaries    [NOT STARTED]

Overall: X/25 sections complete (X%)
Taste: X/1 | Anti-Architecture: X/4 | AI Implementation: X/6

Session file: [path]
```

Legend:
- ✓ = Complete
- → = In Progress (current)
- ○ = Not Started

## After Status

Use AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "How would you like to continue?",
      "header": "Continue",
      "multiSelect": false,
      "options": [
        {"label": "Continue current", "description": "Keep working on [current section]"},
        {"label": "Jump to section", "description": "Go to a different section"},
        {"label": "Review all", "description": "Check for gaps across all sections"},
        {"label": "Wrap up", "description": "Finalize PRD with /prd:done"}
      ]
    }
  ]
}
```

## Important

- This command does NOT exit PRD mode
- Do NOT write code
- Accurate status helps user understand progress
