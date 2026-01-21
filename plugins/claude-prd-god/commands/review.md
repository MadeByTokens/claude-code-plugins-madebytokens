---
description: Analyze the PRD for gaps, incomplete sections, vague requirements, and missing acceptance criteria.
---

# PRD Review

The user wants a comprehensive review of their PRD to identify gaps and issues.

## Actions

1. **Read the entire session file**
2. **Analyze each section** for completeness
3. **Check for common issues**
4. **Present findings with recommendations**

## Review Checklist

For each section, check:

### Vision & Principles (CRITICAL - Taste Layer)
- [ ] Product vision clearly articulated in one sentence?
- [ ] Non-negotiable design principles listed?
- [ ] "What would feel wrong" documented?
- [ ] Aesthetic/UX north star defined?
- [ ] Explicit taste decisions recorded with rationale?
- [ ] Products admired for similar feel identified?

### Problem Statement
- [ ] Background context provided?
- [ ] Specific pain points listed?
- [ ] Impact quantified or described?
- [ ] Current state explained?

### Target Users
- [ ] At least one persona defined?
- [ ] Demographics included?
- [ ] Goals and frustrations listed?
- [ ] Behaviors described?

### User Stories
- [ ] Follows "As a... I want... So that..." format?
- [ ] Each story has acceptance criteria?
- [ ] Priority assigned (Must/Should/Could/Won't)?
- [ ] No vague language?

### Functional Requirements
- [ ] Specific and measurable?
- [ ] Prioritized?
- [ ] No implementation details (just WHAT, not HOW)?

### Non-Functional Requirements
- [ ] Performance targets specified?
- [ ] Security requirements listed?
- [ ] Accessibility level defined (WCAG)?
- [ ] Scalability targets?

### Data Model
- [ ] Key entities identified?
- [ ] Relationships described?
- [ ] Data constraints noted?

### UI/UX Specification
- [ ] Key screens/flows identified?
- [ ] User flow described?
- [ ] Interaction patterns noted?

### API Contract (if applicable)
- [ ] Endpoints listed?
- [ ] Request/response formats?
- [ ] Error handling?

### Change Analysis (CRITICAL - Prevents Accidental Architecture)
- [ ] Configuration vs hardcode decisions documented?
- [ ] Flexibility requirements identified?
- [ ] Feature flags/toggle points considered?
- [ ] "What will likely change?" answered for each component?

### Architecture Decisions (CRITICAL - Prevents Accidental Architecture)
- [ ] Shared vs local concepts identified?
- [ ] Source of truth defined for each data type?
- [ ] Dependency map created (what breaks if X changes)?
- [ ] No orphaned data ownership?

### Edge Cases & Error Scenarios (CRITICAL - Prevents Happy Path Bias)
- [ ] Malformed input handling defined?
- [ ] Missing data scenarios covered?
- [ ] External service failure modes addressed?
- [ ] Concurrent/race conditions considered (if applicable)?
- [ ] Error messages and user feedback specified?

### Testing Strategy (CRITICAL - Prevents Untestable Design)
- [ ] Testability assessed for each requirement?
- [ ] Requirements that are hard to test flagged for redesign?
- [ ] Test approach defined per feature?
- [ ] Test data requirements specified?
- [ ] Integration test scenarios documented?

### Success Metrics
- [ ] KPIs defined?
- [ ] Targets specified?
- [ ] Measurement method described?

### Acceptance Criteria
- [ ] Every user story has criteria?
- [ ] Criteria are testable?
- [ ] Given-When-Then format?

### Scope Boundaries
- [ ] In-scope items listed?
- [ ] Out-of-scope explicitly stated?
- [ ] Future considerations noted?

### Risks & Mitigations
- [ ] At least 3-5 risks identified?
- [ ] Each risk has mitigation?
- [ ] Technical risks included?
- [ ] Business risks included?

### Dependencies
- [ ] External services listed?
- [ ] Third-party libraries?
- [ ] Team/resource dependencies?

### Technical Constraints
- [ ] Platform constraints?
- [ ] Performance limits?
- [ ] Security boundaries?

### Evolution Strategy
- [ ] Anticipated future features documented?
- [ ] Impact on current design assessed?
- [ ] Assumptions that may become invalid listed?
- [ ] Migration paths defined for likely changes?
- [ ] Extensibility points identified?

### Tech Stack (AI Implementation - CRITICAL)
- [ ] All technologies listed with exact version numbers?
- [ ] No ambiguous references (e.g., "React" without version)?
- [ ] Development tools specified?
- [ ] External services and API versions documented?

### Project Structure (AI Implementation - CRITICAL)
- [ ] Complete directory tree provided?
- [ ] Key files and their purposes documented?
- [ ] Naming conventions specified for files, folders, components?

### Commands (AI Implementation - CRITICAL)
- [ ] Install/setup commands provided?
- [ ] Development server commands documented?
- [ ] Test commands with coverage options?
- [ ] Build and deploy commands specified?
- [ ] Linting and formatting commands included?

### Code Style & Examples (AI Implementation - CRITICAL)
- [ ] General style rules documented?
- [ ] GOOD code examples provided for key patterns?
- [ ] BAD anti-patterns shown to avoid?
- [ ] Naming conventions table complete?

### Git Workflow (AI Implementation - CRITICAL)
- [ ] Branch naming conventions specified?
- [ ] Commit message format defined?
- [ ] PR process documented?
- [ ] Protected files listed?

### AI Agent Boundaries (AI Implementation - CRITICAL)
- [ ] ALWAYS DO list populated with safe actions?
- [ ] ASK FIRST list includes sensitive operations?
- [ ] NEVER DO list includes "commit secrets" and other hard stops?
- [ ] Security boundaries explicitly defined?

## Display Format

```
PRD REVIEW

Analyzing your PRD for completeness...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL ISSUES (must fix):

❌ [Section]: [Issue description]
   Recommendation: [How to fix]

❌ [Section]: [Issue description]
   Recommendation: [How to fix]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WARNINGS (should address):

⚠️ [Section]: [Issue description]
   Recommendation: [How to fix]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUGGESTIONS (nice to have):

💡 [Section]: [Suggestion]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY:
- Critical issues: X
- Warnings: X
- Sections complete: X/25
- Taste Layer: [COMPLETE/INCOMPLETE]
- Anti-Accidental-Architecture: X/4 complete
- AI Implementation: X/6 complete
- Ready for development: [YES/NO - requires Taste + Anti-Architecture + AI Implementation]
```

## After Review

Use AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "How would you like to address these findings?",
      "header": "Next",
      "multiSelect": false,
      "options": [
        {"label": "Fix critical issues", "description": "Work through critical issues one by one"},
        {"label": "Review specific section", "description": "Deep dive into one section"},
        {"label": "Continue anyway", "description": "Acknowledge gaps and proceed"},
        {"label": "Export as-is", "description": "Finalize with current state"}
      ]
    }
  ]
}
```

## Important

- Be thorough but constructive
- Prioritize issues by severity
- Provide actionable recommendations
- Do NOT write code
- Stay in PRD mode
