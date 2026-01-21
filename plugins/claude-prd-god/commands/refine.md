---
description: Iterate on the current PRD section with more detail, clarification, or revisions.
---

# Refine Current Section

The user wants to iterate on the current section to improve it.

## Actions

1. **Read `.prd-state`** to get current section
2. **Read session file** to get current content
3. **Present current content**
4. **Ask what to improve**

## Display Format

```
REFINING: [Section Name]

Current content:
───────────────────────────────
[Current section content from file]
───────────────────────────────
```

## Refinement Options

Use AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "What aspect would you like to refine?",
      "header": "Refine",
      "multiSelect": false,
      "options": [
        {"label": "Add detail", "description": "Expand with more specific information"},
        {"label": "Clarify language", "description": "Make requirements more precise"},
        {"label": "Add edge cases", "description": "Consider failure scenarios"},
        {"label": "Revise completely", "description": "Start this section fresh"}
      ]
    }
  ]
}
```

## Refinement Process

Based on selection:

**Add detail:**
- Ask targeted questions about what's missing
- Propose additions
- Update file with approved changes

**Clarify language:**
- Identify vague terms ("should", "might", "fast", "easy")
- Propose specific replacements
- Update file with approved changes

**Add edge cases:**
- Ask "What if X fails?"
- Ask "What happens when Y is empty/null/invalid?"
- Document error scenarios and expected behavior

**Revise completely:**
- Walk through section from scratch
- Ask all relevant questions again
- Replace section content entirely

## Important

- Always show changes before writing to file
- Get explicit approval before updating
- Keep iterating until user is satisfied
- Do NOT write code
- Stay in PRD mode
