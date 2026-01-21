#!/bin/bash
# Start a PRD session - creates state file and session markdown file

# Get topic from argument or use default
TOPIC="${1:-untitled}"
TOPIC_SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//')
TIMESTAMP=$(date +"%Y%m%d-%H%M")
SESSION_FILE="./prd-${TOPIC_SLUG}-${TIMESTAMP}.md"

# Check for source brainstorm file (optional second argument)
SOURCE_BRAINSTORM="${2:-}"

# Create state file in current directory
STATE_FILE="./.prd-state"

# Define all PRD sections (25 total - includes Taste Layer, Anti-Architecture, and AI Implementation sections)
ALL_SECTIONS="vision_principles,problem_statement,target_users,user_stories,functional_requirements,non_functional_requirements,data_model,ui_ux_specification,api_contract,change_analysis,architecture_decisions,edge_cases,testing_strategy,success_metrics,scope_boundaries,risks_mitigations,dependencies,technical_constraints,evolution_strategy,tech_stack,project_structure,commands,code_style,git_workflow,ai_boundaries"

# Write state
cat > "$STATE_FILE" << EOF
PRD_ACTIVE=1
SESSION_FILE=$SESSION_FILE
SOURCE_BRAINSTORM=$SOURCE_BRAINSTORM
TOPIC=$TOPIC
STARTED=$TIMESTAMP
CURRENT_SECTION=vision_principles
COMPLETED_SECTIONS=
TOTAL_SECTIONS=25
REQUIREMENT_COUNT=0
USER_STORY_COUNT=0
ALL_SECTIONS=$ALL_SECTIONS
EOF

# Create session markdown file with template
cat > "$SESSION_FILE" << EOF
# Product Requirements Document: $TOPIC
Generated: $(date +"%Y-%m-%d %H:%M")
Source Brainstorm: ${SOURCE_BRAINSTORM:-None}

---

## 0. Vision & Principles

*Capturing the soul of the product — taste and judgment that AI cannot infer*

### 0.1 Product Vision
**In one sentence, what is this product and why does it matter?**
[To be filled]

### 0.2 Design Principles (Non-Negotiables)
What principles must NEVER be violated, even if technically convenient?

| Principle | Why It Matters | Example Violation to Avoid |
|-----------|----------------|---------------------------|
| [To be filled] | [Why] | [What would break this] |

### 0.3 What Would Feel Wrong
If the final product had these characteristics, it would be a failure regardless of technical correctness:
- [To be filled]

### 0.4 Aesthetic & UX North Star
- **What should it FEEL like to use this?** [To be filled]
- **What products do you admire that have similar feel?** [To be filled]
- **What's the personality/tone?** [To be filled]

### 0.5 Explicit Taste Decisions
Judgment calls that are subjective but critical:

| Decision | Choice Made | Rationale |
|----------|-------------|-----------|
| [To be filled] | [Choice] | [Why this feels right] |

**Section Status:** NOT STARTED

---

## 1. Problem Statement

### 1.1 Background
[To be filled]

### 1.2 Pain Points
[To be filled]

### 1.3 Impact
[To be filled]

**Section Status:** NOT STARTED

---

## 2. Target Users

### 2.1 Primary Persona
[To be filled]

### 2.2 Secondary Personas
[To be filled]

**Section Status:** NOT STARTED

---

## 3. User Stories

[To be filled]

**Section Status:** NOT STARTED

---

## 4. Functional Requirements

[To be filled]

**Section Status:** NOT STARTED

---

## 5. Non-Functional Requirements

### 5.1 Performance
[To be filled]

### 5.2 Security
[To be filled]

### 5.3 Accessibility
[To be filled]

### 5.4 Scalability
[To be filled]

**Section Status:** NOT STARTED

---

## 6. Data Model

[To be filled]

**Section Status:** NOT STARTED

---

## 7. UI/UX Specification

[To be filled]

**Section Status:** NOT STARTED

---

## 8. API Contract

[To be filled - or N/A if not applicable]

**Section Status:** NOT STARTED

---

## 9. Change Analysis

*Addresses: "What will likely change?"*

### 9.1 Configuration vs Hardcoded Decisions
| Element | Decision | Rationale |
|---------|----------|-----------|
| [To be filled] | Config / Hardcode | [Why] |

### 9.2 Flexibility Requirements
[To be filled - what needs to be easily changeable?]

### 9.3 Feature Flags / Toggle Points
[To be filled - what might need to be turned on/off?]

**Section Status:** NOT STARTED

---

## 10. Architecture Decisions

*Addresses: "Should this exist once or everywhere?", "What's the source of truth?", "What breaks if I change this?"*

### 10.1 Shared vs Local Concepts
| Concept | Scope | Rationale |
|---------|-------|-----------|
| [To be filled] | Shared / Local | [Why] |

### 10.2 Source of Truth
| Data Type | Owner | Consumers |
|-----------|-------|-----------|
| [To be filled] | [System/Service] | [Who reads it] |

### 10.3 Dependency Map
[To be filled - what breaks if X changes?]

**Section Status:** NOT STARTED

---

## 11. Edge Cases & Error Scenarios

*Prevents AI from focusing only on happy paths*

### 11.1 Malformed Input Handling
| Input Type | Malformed Example | Expected Behavior |
|------------|-------------------|-------------------|
| [To be filled] | [Example] | [What should happen] |

### 11.2 Missing Data Scenarios
[To be filled]

### 11.3 System Failure Modes
[To be filled - what if external services fail?]

### 11.4 Concurrent/Race Conditions
[To be filled - if applicable]

**Section Status:** NOT STARTED

---

## 12. Testing Strategy

*Addresses: "How would I test this?"*

### 12.1 Testability Assessment
| Requirement | Easy to Test? | If No, Why? | Redesign Needed? |
|-------------|---------------|-------------|------------------|
| [To be filled] | Yes/No | [Reason] | [Yes/No] |

### 12.2 Test Approach per Feature
[To be filled]

### 12.3 Test Data Requirements
[To be filled]

### 12.4 Integration Test Scenarios
[To be filled]

**Section Status:** NOT STARTED

---

## 13. Success Metrics

[To be filled]

**Section Status:** NOT STARTED

---

## 14. Scope Boundaries

### 14.1 In Scope (v1)
[To be filled]

### 14.2 Out of Scope (Future)
[To be filled]

**Section Status:** NOT STARTED

---

## 15. Risks & Mitigations

[To be filled]

**Section Status:** NOT STARTED

---

## 16. Dependencies

[To be filled]

**Section Status:** NOT STARTED

---

## 17. Technical Constraints

[To be filled]

**Section Status:** NOT STARTED

---

## 18. Evolution Strategy

*How will this system grow over time?*

### 18.1 Anticipated Future Features
| Feature | Likelihood | Impact on Current Design |
|---------|------------|-------------------------|
| [To be filled] | High/Med/Low | [What would need to change] |

### 18.2 Assumptions That May Become Invalid
[To be filled - what are we assuming that might not hold?]

### 18.3 Migration Paths
[To be filled - if X changes, how do we migrate?]

### 18.4 Extensibility Points
[To be filled - where should the system be designed for extension?]

**Section Status:** NOT STARTED

---

# AI Implementation Specification

*The following sections ensure any AI agent can build this product without asking clarifying questions.*

---

## 19. Tech Stack

*Exact technologies with specific versions — no ambiguity*

### 19.1 Core Technologies
| Category | Technology | Version | Rationale |
|----------|------------|---------|-----------|
| Language | [To be filled] | [x.x.x] | [Why this choice] |
| Framework | [To be filled] | [x.x.x] | [Why this choice] |
| Database | [To be filled] | [x.x.x] | [Why this choice] |
| Styling | [To be filled] | [x.x.x] | [Why this choice] |

### 19.2 Development Tools
| Tool | Version | Purpose |
|------|---------|---------|
| [To be filled] | [x.x.x] | [Purpose] |

### 19.3 External Services
| Service | Purpose | API Version |
|---------|---------|-------------|
| [To be filled] | [Purpose] | [Version] |

**Section Status:** NOT STARTED

---

## 20. Project Structure

*Explicit folder/file layout the AI must follow*

### 20.1 Directory Tree
\`\`\`
project-root/
├── src/
│   ├── [To be filled]
│   └── ...
├── tests/
│   └── ...
├── docs/
│   └── ...
└── [To be filled]
\`\`\`

### 20.2 Key Files and Their Purposes
| File | Purpose |
|------|---------|
| [To be filled] | [What this file does] |

### 20.3 Naming Conventions
- **Files:** [To be filled - e.g., kebab-case.ts]
- **Folders:** [To be filled]
- **Components:** [To be filled]

**Section Status:** NOT STARTED

---

## 21. Commands

*Executable commands with full flags — copy-paste ready*

### 21.1 Development
\`\`\`bash
# Install dependencies
[To be filled]

# Start development server
[To be filled]

# Run in watch mode
[To be filled]
\`\`\`

### 21.2 Testing
\`\`\`bash
# Run all tests
[To be filled]

# Run tests with coverage
[To be filled]

# Run specific test file
[To be filled]
\`\`\`

### 21.3 Build & Deploy
\`\`\`bash
# Build for production
[To be filled]

# Deploy to staging
[To be filled]

# Deploy to production
[To be filled]
\`\`\`

### 21.4 Utilities
\`\`\`bash
# Lint code
[To be filled]

# Format code
[To be filled]

# Type check
[To be filled]
\`\`\`

**Section Status:** NOT STARTED

---

## 22. Code Style & Examples

*Concrete code snippets showing expected patterns*

### 22.1 General Style Rules
- [To be filled - e.g., "Use functional components, not class components"]
- [To be filled]

### 22.2 Example: Component Pattern
\`\`\`typescript
// GOOD - Follow this pattern
[To be filled with concrete code example]
\`\`\`

\`\`\`typescript
// BAD - Avoid this pattern
[To be filled with anti-pattern example]
\`\`\`

### 22.3 Example: API/Service Pattern
\`\`\`typescript
// GOOD - Follow this pattern
[To be filled with concrete code example]
\`\`\`

### 22.4 Example: Error Handling Pattern
\`\`\`typescript
// GOOD - Follow this pattern
[To be filled with concrete code example]
\`\`\`

### 22.5 Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Variables | [To be filled] | [Example] |
| Functions | [To be filled] | [Example] |
| Components | [To be filled] | [Example] |
| Constants | [To be filled] | [Example] |

**Section Status:** NOT STARTED

---

## 23. Git Workflow

*Version control process for AI and human contributors*

### 23.1 Branch Naming
| Branch Type | Pattern | Example |
|-------------|---------|---------|
| Feature | [To be filled] | feature/user-auth |
| Bugfix | [To be filled] | fix/login-redirect |
| Hotfix | [To be filled] | hotfix/security-patch |

### 23.2 Commit Message Format
\`\`\`
[type]: [short description]

[optional body]

[optional footer]
\`\`\`

**Types:** feat, fix, docs, style, refactor, test, chore

**Example:**
\`\`\`
feat: add user authentication flow

- Implement login/logout functionality
- Add JWT token handling
- Create auth context provider

Closes #123
\`\`\`

### 23.3 Pull Request Process
1. [To be filled]
2. [To be filled]
3. [To be filled]

### 23.4 Protected Files (Never Auto-Modify)
- [ ] .env, .env.*
- [ ] [To be filled]

**Section Status:** NOT STARTED

---

## 24. AI Agent Boundaries

*Explicit permissions and restrictions for AI implementation*

### 24.1 ALWAYS DO (Safe to Proceed)
AI agents should always:
- [ ] Follow the code style examples in Section 22
- [ ] Run tests after making changes
- [ ] Use the exact versions specified in Tech Stack
- [ ] Follow the project structure in Section 20
- [ ] Write descriptive commit messages per Section 23
- [ ] [To be filled]

### 24.2 ASK FIRST (Require Human Approval)
AI agents must ask before:
- [ ] Adding new dependencies
- [ ] Changing database schema
- [ ] Modifying authentication/authorization logic
- [ ] Changing API contracts
- [ ] [To be filled]

### 24.3 NEVER DO (Hard Stops)
AI agents must NEVER:
- [ ] Commit secrets, API keys, or credentials
- [ ] Modify .env files or production configs
- [ ] Delete or modify migration files
- [ ] Push directly to main/master branch
- [ ] Bypass tests or linting
- [ ] Modify vendor/node_modules directories
- [ ] [To be filled]

### 24.4 Security Boundaries
- [ ] [To be filled - specific security constraints]

**Section Status:** NOT STARTED

---

## Appendix A: Traceability Matrix

| Source Idea | User Story | Requirement | Acceptance Criteria |
|-------------|------------|-------------|---------------------|
| [To be filled] | | | |

## Appendix B: Five Pre-Coding Questions Checklist

Before implementation begins, verify these are answered:

- [ ] **What will likely change?** → See Section 9 (Change Analysis)
- [ ] **Should this exist once or everywhere?** → See Section 10.1 (Shared vs Local)
- [ ] **What's the source of truth?** → See Section 10.2 (Source of Truth)
- [ ] **What breaks if I change this?** → See Section 10.3 (Dependency Map)
- [ ] **How would I test this?** → See Section 12 (Testing Strategy)

If any question cannot be answered clearly, the PRD is incomplete.

EOF

echo "SESSION_FILE=$SESSION_FILE"
echo "STATE_FILE=$STATE_FILE"
