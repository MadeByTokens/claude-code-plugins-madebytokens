---
description: Navigate to a specific PRD section to view or edit it.
---

# Navigate to PRD Section

The user wants to jump to a specific section of the PRD.

## Arguments

`$ARGUMENTS` contains the section name. Valid sections:
- `vision` or `vision_principles`
- `problem` or `problem_statement`
- `users` or `target_users`
- `stories` or `user_stories`
- `functional` or `functional_requirements`
- `nonfunctional` or `non_functional_requirements`
- `data` or `data_model`
- `ui` or `ux` or `ui_ux_specification`
- `api` or `api_contract`
- `change` or `change_analysis`
- `architecture` or `architecture_decisions`
- `edge` or `edge_cases`
- `testing` or `testing_strategy`
- `metrics` or `success_metrics`
- `scope` or `scope_boundaries`
- `risks` or `risks_mitigations`
- `dependencies`
- `constraints` or `technical_constraints`
- `evolution` or `evolution_strategy`
- `tech` or `tech_stack`
- `structure` or `project_structure`
- `commands`
- `style` or `code_style`
- `git` or `git_workflow`
- `boundaries` or `ai_boundaries`

## Actions

1. **Parse the section name** from `$ARGUMENTS`
2. **Read current session file** to see section status
3. **Display section content** and status
4. **Offer to work on it**

## Display Format

```
SECTION: [Section Name]
Status: [COMPLETE / IN PROGRESS / NOT STARTED]

Current Content:
[Show what's in the session file for this section]

---
```

Then use AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "What would you like to do with this section?",
      "header": "Action",
      "multiSelect": false,
      "options": [
        {"label": "Edit", "description": "Revise or add to this section"},
        {"label": "Review", "description": "Check for completeness and issues"},
        {"label": "Approve", "description": "Mark this section as complete"},
        {"label": "Back", "description": "Return to previous section"}
      ]
    }
  ]
}
```

## If No Section Specified

If `$ARGUMENTS` is empty, show section list and ask which one:

```json
{
  "questions": [
    {
      "question": "Which section would you like to work on?",
      "header": "Section",
      "multiSelect": false,
      "options": [
        {"label": "Problem Statement", "description": "Section 1 - Why this exists"},
        {"label": "Target Users", "description": "Section 2 - Who it's for"},
        {"label": "User Stories", "description": "Section 3 - What users can do"},
        {"label": "Other section...", "description": "Type the section name"}
      ]
    }
  ]
}
```

## Important

- Stay in PRD mode
- Do NOT write code
- Update session file when changes are made
- Track section status changes
