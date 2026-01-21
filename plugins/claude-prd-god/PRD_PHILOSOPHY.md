# PRD Phase Design Philosophy

## My Analysis & Expert Understanding

I've thoroughly analyzed the claude brainstorm plugin. Here's my synthesis of the **design philosophy** and what it means for the PRD phase:

### Core Design Philosophy

The brainstorm plugin solves a fundamental problem: **Claude wants to be helpful by solving problems, but true ideation requires staying in divergent thinking mode**. The solution is elegant:

1. **Hook-enforced behavior** - Rules injected on EVERY prompt via `UserPromptSubmit`, making it impossible for Claude to "forget"
2. **User-controlled exits** - Only explicit `/brainstorm:done` ends the mode
3. **State file sentinel** - `.brainstorm-state` presence determines active session
4. **Silent artifact generation** - Ideas logged without interrupting flow
5. **Structured navigation** - Fork/back enables exploring tangents without losing context
6. **AskUserQuestion for decisions** - Structured UI at critical decision points

### The Analogous Problem for PRD

Just like brainstorming has the problem of "jumping to solutions," the **PRD phase has the problem of jumping to code/implementation without complete requirements**. The result is:
- Incomplete specifications
- Missed edge cases
- Ambiguous acceptance criteria
- Scope creep during development
- Rework when requirements were misunderstood

### The Accidental Architecture Problem

> "You're always vibe coding into a system, whether you've designed it intentionally or not."
> — [Vibe Coding Without System Design is a Trap](https://www.focusedchaos.co/p/vibe-coding-without-system-design-is-a-trap)

AI coding tools optimize for **"working right now"** rather than **"evolvable systems."** Without intentional system design in the PRD, you create **accidental architecture** that becomes fragile and expensive to maintain.

**Four Failure Modes AI-Generated Code Exhibits:**

| Problem | Example | Root Cause |
|---------|---------|------------|
| **Hardcoding over abstraction** | Job field options hardcoded instead of globally configurable | AI doesn't ask "should this be flexible?" |
| **Missing testability** | PDF parsing seemed to work until edge cases found | AI doesn't build test infrastructure proactively |
| **Edge cases ignored** | AI resume scoring over-indexed on location with weak inputs | AI focuses on happy paths, not failure modes |
| **Progressive building breaks things** | Adding custom questions broke earlier scoring assumptions | Features added atop fragile foundations |

**The Five Pre-Coding Questions (MANDATORY in PRD):**

These questions MUST be answered in the PRD before any implementation begins:

1. **What will likely change?** → Don't hardcode changeable values. Identify configuration points.
2. **Should this exist once or everywhere?** → Build shared concepts centrally. Avoid duplication.
3. **What's the source of truth?** → Define data ownership clearly. One authoritative source per data type.
4. **What breaks if I change this?** → If you can't answer, the architecture is fragile. Map dependencies.
5. **How would I test this?** → Awkward testing signals design problems. If hard to test, redesign.

These questions prevent accidental architecture by forcing intentional design decisions INTO the PRD document, where they can be reviewed before code hardens them into reality.

### The Taste Layer: Capturing Human Judgment

> **"Taste is judgment compressed by time."**
> — [Personal Taste Is the Moat](https://wangcong.org/2026-01-13-personal-taste-is-the-moat.html)

As AI commoditizes technical correctness, **human judgment becomes the differentiator**. AI can generate code that "works" but cannot answer:

- Should this feature exist at all?
- Does this design age gracefully?
- Are we hiding complexity or creating it?
- What would make this feel cheap or bloated?

These are **judgment calls, not rule violations** — no AI can catch them. A PRD that only captures requirements misses the most important layer: the user's **taste and vision**.

**What Traditional PRDs Capture vs. What's Missing:**

| What PRDs Capture | What's Missing (Taste) |
|-------------------|------------------------|
| What features are needed? | Should this feature exist at all? |
| How should it work? | Does this design feel right? |
| What are the edge cases? | What would make this feel cheap/bloated? |
| What are the requirements? | What's the vision? What's the soul? |
| Technical constraints | Aesthetic constraints — what do we refuse to compromise on? |

**The PRD plugin must capture the user's taste and judgment, not just facts.**

This means:

1. **Vision & Principles come FIRST** — Before any requirements, capture what the product should feel like, what's non-negotiable, what would feel wrong.

2. **Dialogue, not interrogation** — The flow should be: Claude proposes → User reacts with judgment → Claude refines → User approves vision, not just facts.

3. **Taste checks throughout** — At each section, ask: "Does this feel right?", "Is there anything here that feels like bloat?", "What would you refuse to compromise on?"

4. **Design smell detection** — Flag things that are technically correct but may be poor taste: features that add complexity without clear value, designs that address symptoms rather than root causes.

### Writing Specs That AI Agents Can Actually Implement

> "Most agent files fail because they're too vague."
> — [How to Write a Good Spec](https://addyosmani.com/blog/good-spec/)

Research on 2,500+ agent specification files reveals that effective AI specs require **specificity over abstraction**. Say "React 18 with TypeScript 5.3, Vite 5.0, and Tailwind CSS 3.4" — not "React project."

**Six Essential Sections for AI Implementation:**

1. **Tech Stack** — Exact technologies with version numbers
2. **Project Structure** — Explicit folder/file layout
3. **Commands** — Executable commands with full flags (build, test, lint, deploy)
4. **Code Style Examples** — Concrete code snippets showing expected patterns
5. **Git Workflow** — Branch naming, commit conventions, PR process
6. **Boundaries** — Always do / Ask first / Never do

**The "Curse of Instructions":**

Performance degrades as requirements multiply. Solutions:
- Break large PRDs into focused modules (backend, frontend, API)
- Create hierarchical summaries with references to detailed sections
- Use phased implementation (don't give AI everything at once)

**PRD as Living Artifact:**

Effective specs are "living artifacts" that evolve — not static documents. The PRD should:
- Be version-controlled alongside code
- Update as implementation decisions materialize
- Serve as conformance test contract (implementation validates against PRD)

**The Single Most Common Helpful Constraint:**

> "Never commit secrets" was identified as the most valuable boundary across 2,500+ agent files.

Other critical safeguards: protect vendor directories, production configs, and environment files.

### What Makes a PRD "Complete Enough for Any AI Agent"

A truly complete PRD should enable **any competent developer (human or AI) to build the product without asking clarifying questions**. This requires:

| # | Section | Purpose | Completeness Criteria |
|---|---------|---------|----------------------|
| 0 | **Vision & Principles** | What's the soul of this product? | Product vision, non-negotiables, aesthetic principles, what would feel wrong |
| 1 | **Problem Statement** | Why does this need to exist? | Clear pain points, measurable impact |
| 2 | **Target Users** | Who exactly benefits? | Personas with demographics, needs, behaviors |
| 3 | **User Stories** | What can users do? | Given-When-Then format, comprehensive coverage |
| 4 | **Functional Requirements** | What features are needed? | Specific, prioritized (MoSCoW), no ambiguity |
| 5 | **Non-Functional Requirements** | Quality attributes | Performance metrics, security requirements, accessibility |
| 6 | **Data Model** | What data exists? | Entities, relationships, constraints, source of truth |
| 7 | **UI/UX Specification** | What does it look like? | Wireframes, user flows, interaction patterns |
| 8 | **API Contract** | How do systems talk? | Endpoints, request/response schemas, error handling |
| 9 | **Change Analysis** | What will likely change? | Configuration points, flexibility needs, hardcode vs config decisions |
| 10 | **Architecture Decisions** | How do components relate? | Shared vs local concepts, data ownership, dependency map |
| 11 | **Edge Cases & Error Scenarios** | What happens when things fail? | Malformed inputs, missing data, system failures, error handling |
| 12 | **Testing Strategy** | How do we verify correctness? | Test approach per requirement, testability assessment, test data needs |
| 13 | **Success Metrics** | How do we know it works? | KPIs, targets, measurement methods |
| 14 | **Scope Boundaries** | What's IN and OUT? | Explicit v1 boundaries, deferred items |
| 15 | **Risks & Mitigations** | What could go wrong? | Identified risks with concrete mitigations |
| 16 | **Dependencies** | What do we need? | External services, libraries, prerequisites |
| 17 | **Technical Constraints** | What limits exist? | Platform, performance, security boundaries |
| 18 | **Evolution Strategy** | How will this system grow? | Future features, assumption invalidation, migration paths |

**AI Implementation Sections (19-24) — Critical for "Any AI Agent Can Build It":**

| # | Section | Purpose | Completeness Criteria |
|---|---------|---------|----------------------|
| 19 | **Tech Stack** | Exact technologies to use | Specific versions, no ambiguity (e.g., "React 18.2.0, TypeScript 5.3") |
| 20 | **Project Structure** | Folder/file layout | Complete directory tree with explanations |
| 21 | **Commands** | How to build, test, run | Executable commands with full flags |
| 22 | **Code Style & Examples** | How code should look | Concrete snippets showing patterns, naming conventions |
| 23 | **Git Workflow** | Version control process | Branch naming, commit format, PR process |
| 24 | **AI Agent Boundaries** | What AI can/can't do | Always do, Ask first, Never do lists |

**Total: 25 sections (0-24)**

**Sections 9-12 directly address the Five Pre-Coding Questions:**
- **Change Analysis** → "What will likely change?"
- **Architecture Decisions** → "Should this exist once or everywhere?" + "What's the source of truth?" + "What breaks if I change this?"
- **Edge Cases & Error Scenarios** → Prevents AI from focusing only on happy paths
- **Testing Strategy** → "How would I test this?"

---

## Proposed PRD Phase Features

### 1. Phase Transition Flow (Brainstorm → PRD)

```
/brainstorm:done
    ↓
Claude offers: "Generate PRD from these ideas?" (via AskUserQuestion)
    ↓
User selects ideas/themes to develop
    ↓
/prd:start [optional: reference to brainstorm file]
    ↓
PRD_ACTIVE=1, enforcer switches to PRD mode
```

**Key Design Decision**: PRD is a **separate phase** with its own state file (`.prd-state`), enforcer rules, and commands. This mirrors how brainstorm has its own isolated state.

### 2. PRD Commands (Parallel to Brainstorm)

| Command | Purpose |
|---------|---------|
| `/prd:start [topic]` | Initialize PRD session, import from brainstorm if available |
| `/prd:section <name>` | Navigate to specific section for deep-dive |
| `/prd:status` | Show completeness per section, current progress |
| `/prd:review` | Gap analysis - what's missing or incomplete? |
| `/prd:refine` | Iterate on current section with more detail |
| `/prd:done` | Finalize PRD, generate complete document |
| `/prd:help` | Show PRD structure and guidance |

### 3. PRD Enforcer Rules (Injected on Every Prompt)

```
PRD MODE ACTIVE - ENFORCED RULES

You are a requirements analyst, NOT a developer.

NEVER (strictly enforced):
- Write code, create code files, or make implementation decisions
- Skip sections without user approval
- Make unstated assumptions
- Use vague language ("should", "might", "could")
- Accept incomplete acceptance criteria
- Move to next section without user sign-off

ALWAYS:
- Discuss each section interactively before finalizing
- Ask clarifying questions when requirements are ambiguous
- Reference brainstorm ideas where applicable
- Ensure acceptance criteria are testable and specific
- Track completeness per section
- Use precise, unambiguous language
- Include edge cases and error scenarios
```

### 4. Interactive Section Workflow

For each PRD section, the flow is:

```
1. Claude presents section purpose and prompting questions
2. Claude proposes initial content based on brainstorm + discussion
3. User reviews, asks for changes or more detail
4. Claude refines until user approves
5. Section marked complete, move to next
```

This mirrors how brainstorm has fork/back navigation - but instead of threads, we navigate **sections**.

### 5. Brainstorm Import Feature

When starting PRD from a brainstorm session:

```
/prd:start --from brainstorm-checkout-flow-20260119-1530.md

Claude reads brainstorm file, extracts:
- Key themes
- Top ideas (most discussed/excited about)
- Forks explored
- Questions raised

Presents: "I found these themes from your brainstorm. Which should we develop into requirements?"
```

### 6. Completeness Tracking

PRD state includes section completion:

```bash
PRD_ACTIVE=1
SESSION_FILE=./prd-checkout-flow-20260120-0800.md
SOURCE_BRAINSTORM=./brainstorm-checkout-flow-20260119-1530.md
TOPIC=checkout flow improvement
STARTED=20260120-0800
CURRENT_SECTION=user_stories
COMPLETED_SECTIONS=problem_statement,target_users
TOTAL_SECTIONS=18
```

`/prd:status` shows:
```
PRD STATUS

Topic: Checkout flow improvement
Source: brainstorm-checkout-flow-20260119-1530.md

Section Progress:

Foundation (Taste Layer):
✓ Vision & Principles    [COMPLETE] ← Captures human judgment

Core Requirements:
✓ Problem Statement       [COMPLETE]
✓ Target Users           [COMPLETE]
→ User Stories           [IN PROGRESS - 8 stories, 3 need acceptance criteria]
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

AI Implementation (for "Any AI Can Build It"):
○ Tech Stack             [NOT STARTED]
○ Project Structure      [NOT STARTED]
○ Commands               [NOT STARTED]
○ Code Style & Examples  [NOT STARTED]
○ Git Workflow           [NOT STARTED]
○ AI Agent Boundaries    [NOT STARTED]

Overall: 3/25 sections complete (12%)
Taste Layer: 1/1 ✓
Anti-Accidental-Architecture: 0/4 ⚠️
AI Implementation: 0/6 ⚠️
```

### 7. PRD Artifact Format

```markdown
# Product Requirements Document: [Topic]
Generated: [timestamp]
Source Brainstorm: [filename]

## 1. Problem Statement
### 1.1 Background
[context]

### 1.2 Pain Points
- [pain point 1]
- [pain point 2]

### 1.3 Impact
[why this matters]

---
## 2. Target Users

### 2.1 Primary Persona: [Name]
- Demographics: [details]
- Goals: [what they want]
- Frustrations: [current pain]
- Behaviors: [how they work today]

### 2.2 Secondary Persona: [Name]
[...]

---
## 3. User Stories

### US-001: [Title]
**As a** [user type]
**I want** [action]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]

**Priority:** Must Have
**Source Idea:** [reference to brainstorm idea]

[... more user stories ...]

---
## 4. Functional Requirements
[...]

---
## 14. Technical Constraints
[...]

---
## Appendix: Traceability Matrix

| Brainstorm Idea | → User Story | → Requirement | → Acceptance Criteria |
|-----------------|--------------|---------------|----------------------|
| One-click purchase | US-001 | FR-001 | AC-001a, AC-001b |
```

### 8. Review & Gap Analysis

`/prd:review` triggers a comprehensive check:

```
PRD REVIEW

Checking completeness...

ISSUES FOUND:

❌ User Stories:
   - US-003 missing acceptance criteria
   - US-007 has vague "should work quickly" - needs specific metric

❌ Non-Functional Requirements:
   - No performance requirements specified
   - No accessibility requirements

❌ Scope Boundaries:
   - Section empty - what's explicitly OUT of scope?

⚠️ Risks & Mitigations:
   - Only 2 risks identified - consider more edge cases

RECOMMENDATIONS:
1. Add acceptance criteria to US-003 and US-007
2. Define performance targets (e.g., "checkout completes in <2s")
3. Specify WCAG compliance level
4. Explicitly list out-of-scope items
5. Consider: What if payment provider fails? What if user abandons?
```

---

## Architecture Summary

**Note:** The PRD plugin is a **standalone plugin**, separate from the brainstorm plugin. Users can use brainstorm output as input to PRD (via `--from` flag), but the plugins are independent.

```
claude-prd-god/                    # Standalone PRD plugin
├── .claude-plugin/
│   └── plugin.json            # Plugin metadata
├── commands/
│   ├── start.md               # /prd:start - Initialize PRD session
│   ├── section.md             # /prd:section - Navigate to section
│   ├── status.md              # /prd:status - Show completeness
│   ├── review.md              # /prd:review - Gap analysis
│   ├── refine.md              # /prd:refine - Iterate on section
│   ├── done.md                # /prd:done - Finalize PRD
│   └── help.md                # /prd:help - PRD guidance
├── hooks/
│   ├── hooks.json             # PRD hooks only
│   └── prd-enforcer.sh        # PRD mode rules
└── scripts/
    ├── start-prd-session.sh   # Initialize PRD state
    ├── end-prd-session.sh     # Clear PRD state
    ├── approve-prd-write.sh   # Auto-approve prd-*.md
    ├── approve-prd-bash.sh    # Auto-approve session scripts
    └── approve-prd-websearch.sh # Auto-approve web searches
```

---

## Hook Enforcement Mechanism (Critical for No-Code Guarantee)

This section details the **exact hook implementation** that prevents Claude from writing code during the PRD phase. This mirrors the brainstorm plugin's enforcement pattern.

### Why Hooks Are Essential

Telling Claude "don't write code" in a prompt is unreliable - Claude may forget, especially in long sessions. The hook system solves this by:

1. **Injecting rules on EVERY prompt** - Claude literally cannot forget
2. **Auto-approving only PRD files** - Code files require manual user approval
3. **State-based activation** - Hooks only fire when PRD session is active

### Hook Architecture for PRD

```
User types message
       ↓
┌─────────────────────────────────────────────────┐
│ UserPromptSubmit Hook fires                     │
│ → runs prd-enforcer.sh                          │
│ → checks for .prd-state file                    │
│ → if PRD_ACTIVE=1: injects rules into context   │
└─────────────────────────────────────────────────┘
       ↓
Claude processes with PRD rules injected
       ↓
┌─────────────────────────────────────────────────┐
│ If Claude attempts to Write a file:             │
│ → PreToolUse hook fires                         │
│ → runs approve-prd-write.sh                     │
│ → extracts file_path from tool input            │
│                                                 │
│ Decision:                                       │
│ • prd-*.md files → AUTO-APPROVED (silent)       │
│ • Any other file → NO AUTO-APPROVAL             │
│   (requires user permission prompt)             │
└─────────────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────────────┐
│ If Claude attempts Bash command:                │
│ → PreToolUse hook fires                         │
│ → runs approve-prd-bash.sh                      │
│                                                 │
│ Decision:                                       │
│ • start-prd-session.sh → AUTO-APPROVED          │
│ • end-prd-session.sh → AUTO-APPROVED            │
│ • Any other command → NO AUTO-APPROVAL          │
└─────────────────────────────────────────────────┘
```

### 1. PRD Enforcer Script (`hooks/prd-enforcer.sh`)

```bash
#!/bin/bash
# PRD mode enforcer hook
# Outputs plugin path always, and injects rules reminder when PRD session is active

# Get the plugin root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"

STATE_FILE="./.prd-state"

# Always output plugin path so Claude knows where scripts are
echo "<prd-plugin-path>$PLUGIN_ROOT</prd-plugin-path>"

# Exit if no active session
if [ ! -f "$STATE_FILE" ]; then
    exit 0
fi

# Read state
source "$STATE_FILE"

# Only output if PRD is active
if [ "$PRD_ACTIVE" = "1" ]; then
    cat << 'EOF'
<prd-mode-enforced>
PRD MODE ACTIVE - ENFORCED RULES

You are a requirements analyst, NOT a developer.

NEVER (these are strictly enforced):
- Write code files (.py, .js, .ts, .java, .go, .rs, .c, .cpp, .html, .css, etc.)
- Create implementation files or prototypes
- Make architectural or implementation decisions
- Skip sections without explicit user approval
- Use vague language ("should", "might", "could", "probably")
- Accept requirements without testable acceptance criteria
- Exit PRD mode unless user calls /prd:done

ALWAYS:
- Write ONLY to the PRD session file (prd-*.md)
- Discuss each section interactively before finalizing
- Ask clarifying questions when requirements are ambiguous
- Ensure every requirement has specific, testable acceptance criteria
- Reference source brainstorm ideas where applicable
- Use precise, unambiguous language with measurable targets
- Consider edge cases, error scenarios, and failure modes
- Track section completeness

SECTION WORKFLOW:
1. Present section purpose and key questions to answer
2. Discuss with user, gather requirements
3. Draft section content
4. User reviews and requests changes
5. Iterate until user explicitly approves
6. Mark section complete, move to next

Commands available:
- /prd:section <name> - Navigate to specific section
- /prd:status - Show section completeness
- /prd:review - Gap analysis and recommendations
- /prd:refine - Iterate on current section
- /prd:done - Finalize PRD (THE ONLY WAY TO EXIT)

Stay in character. Document requirements. No code. No implementation.
</prd-mode-enforced>
EOF
fi
```

### 2. PRD Write Approval Script (`scripts/approve-prd-write.sh`)

```bash
#!/bin/bash
# Auto-approve Write operations ONLY for PRD session files
# All other files (especially code files) require manual approval

# Read the hook input from stdin
input=$(cat)

# Extract the file_path from the input
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# ONLY approve writes to prd-*.md files
if [[ "$file_path" == *"prd-"*".md" ]]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "PRD session file"
  }
}
EOF
  exit 0
fi

# IMPORTANT: Do NOT auto-approve any other file type
# This means code files (.py, .js, .ts, etc.) will trigger
# the normal permission prompt, giving the user a chance to reject

# Don't interfere with other operations (let normal permission flow handle them)
exit 0
```

### 3. PRD Bash Approval Script (`scripts/approve-prd-bash.sh`)

```bash
#!/bin/bash
# Auto-approve Bash operations for PRD plugin scripts only

# Read the hook input from stdin
input=$(cat)

# Extract the command from the input
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Approve start-prd-session.sh (with any arguments)
if [[ "$command" == *"scripts/start-prd-session.sh"* ]]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "PRD session start"
  }
}
EOF
  exit 0
fi

# Approve end-prd-session.sh
if [[ "$command" == *"scripts/end-prd-session.sh"* ]]; then
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "PRD session end"
  }
}
EOF
  exit 0
fi

# Do NOT auto-approve any other bash commands
# This prevents Claude from running code, installing packages, etc.
exit 0
```

### 4. hooks.json Configuration (PRD Standalone)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/approve-prd-write.sh"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/approve-prd-bash.sh"
          }
        ]
      },
      {
        "matcher": "WebSearch",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/approve-prd-websearch.sh"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/prd-enforcer.sh"
          }
        ]
      }
    ]
  }
}
```

### 5. How Code Writing Is Prevented

The prevention works through **multiple layers**:

| Layer | Mechanism | Effect |
|-------|-----------|--------|
| **1. Rules injection** | `prd-enforcer.sh` injects "NEVER write code files" on every prompt | Claude follows explicit instructions |
| **2. No auto-approval** | `approve-prd-write.sh` only approves `prd-*.md` files | Code files trigger permission prompt |
| **3. User gate** | If Claude tries to write code, user sees permission dialog | User can reject the operation |
| **4. Bash restriction** | `approve-prd-bash.sh` only approves session scripts | No `npm init`, `python`, `git commit`, etc. |

**Example scenario - Claude attempts to write code:**

```
Claude: "Let me create a quick prototype..."
       ↓
Claude attempts: Write tool → file_path: "checkout.py"
       ↓
PreToolUse hook fires → approve-prd-write.sh
       ↓
"checkout.py" does NOT match "prd-*.md" pattern
       ↓
Script exits without approving (exit 0)
       ↓
Normal permission flow: USER SEES PROMPT
       ↓
"Claude wants to write to checkout.py. Allow?"
       ↓
User can REJECT → Claude cannot write code
```

### 6. State File for PRD (`.prd-state`)

```bash
PRD_ACTIVE=1
SESSION_FILE=./prd-checkout-flow-20260120-0800.md
SOURCE_BRAINSTORM=./brainstorm-checkout-flow-20260119-1530.md
TOPIC=checkout flow improvement
STARTED=20260120-0800
CURRENT_SECTION=user_stories
COMPLETED_SECTIONS=problem_statement,target_users
TOTAL_SECTIONS=14
REQUIREMENT_COUNT=0
USER_STORY_COUNT=0
```

The enforcer checks this file on every prompt. If `PRD_ACTIVE=1`, rules are injected. Deleting this file (via `/prd:done`) exits PRD mode.

### 7. Defense in Depth Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    DEFENSE IN DEPTH                         │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: RULES                                              │
│ • Explicit "NEVER write code" injected on every prompt      │
│ • Claude's training makes it follow explicit instructions   │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: AUTO-APPROVAL RESTRICTION                          │
│ • Only prd-*.md files are auto-approved                     │
│ • Code files (.py, .js, etc.) are NOT auto-approved         │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: USER PERMISSION GATE                               │
│ • Any non-PRD file write triggers permission prompt         │
│ • User has final say on whether to allow                    │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: BASH RESTRICTION                                   │
│ • Only session management scripts auto-approved             │
│ • No package installs, no code execution, no git commits    │
├─────────────────────────────────────────────────────────────┤
│ Layer 5: EXPLICIT EXIT ONLY                                 │
│ • Only /prd:done command exits PRD mode                     │
│ • No accidental or implicit exit possible                   │
└─────────────────────────────────────────────────────────────┘
```

This multi-layered approach ensures that even if one layer fails (e.g., Claude ignores the rules), the other layers catch the attempt. The user always has final control.

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Separate state files** (`.prd-state` vs `.brainstorm-state`) | Allows having completed brainstorm accessible while PRD is active |
| **Section-based navigation** vs thread-based | PRD is structured; sections have defined content, unlike freeform brainstorm threads |
| **Completeness tracking** | PRD quality depends on thoroughness - tracking motivates completion |
| **Review command** | Automated gap detection prevents incomplete PRDs |
| **Traceability to brainstorm** | Links requirements to original ideas, maintains context |
| **Strict acceptance criteria enforcement** | Key to "any AI agent can build it" - testable criteria are non-negotiable |

---

This design maintains the core philosophy of the brainstorm plugin (user control, hook enforcement, interactive discussion, artifact generation) while adapting it for the structured, completeness-focused nature of PRD creation.

---

## Complete Implementation Reference (Standalone)

This section contains **everything needed to implement the PRD plugin from scratch** without referencing any external codebase.

### 1. Claude Code Plugin System Overview

Claude Code plugins are directory-based. The plugin system recognizes:

- **`.claude-plugin/plugin.json`** - Plugin metadata (name, version, description)
- **`commands/*.md`** - Slash commands (each file = one command)
- **`hooks/hooks.json`** - Hook configuration
- **`hooks/*.sh`** - Hook handler scripts
- **`scripts/*.sh`** - Utility scripts

When a user types `/prd:start`, Claude Code:
1. Looks for `commands/start.md` (or `commands/prd/start.md` for namespaced commands)
2. Reads the file and presents its contents to Claude as instructions
3. Claude follows those instructions

### 2. Plugin Metadata (`.claude-plugin/plugin.json`)

```json
{
  "name": "prd",
  "version": "1.0.0",
  "description": "Product Requirements Document generator. Transforms brainstorm ideas into complete, professional PRDs with interactive section-by-section refinement.",
  "author": {
    "name": "Claude PRD"
  }
}
```

### 3. Command File Format

Each command is a Markdown file with **YAML frontmatter** followed by instructions for Claude.

**Structure:**
```markdown
---
description: Short description shown in help
---

# Command Title

Instructions for Claude to follow when this command is invoked.

## Section 1
Details...

## Section 2
Details...
```

**Key concepts:**
- `description` in frontmatter is shown when user types `/prd:help` or asks about commands
- Everything after the frontmatter is instructions Claude receives
- `$ARGUMENTS` is a magic variable containing whatever the user typed after the command

**Example:** If user types `/prd:start checkout flow improvement`, then:
- Command file: `commands/start.md` is loaded
- `$ARGUMENTS` = `"checkout flow improvement"`

### 4. The `<prd-plugin-path>` Tag

The enforcer hook outputs this tag on every prompt:
```
<prd-plugin-path>/absolute/path/to/plugin</prd-plugin-path>
```

Claude must extract this path and use it when running scripts:
```bash
PLUGIN_PATH/scripts/start-prd-session.sh "topic here"
```

Replace `PLUGIN_PATH` with the actual path from the tag.

### 5. Session Management Scripts

#### `scripts/start-prd-session.sh`

```bash
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
```
project-root/
├── src/
│   ├── [To be filled]
│   └── ...
├── tests/
│   └── ...
├── docs/
│   └── ...
└── [To be filled]
```

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
```bash
# Install dependencies
[To be filled]

# Start development server
[To be filled]

# Run in watch mode
[To be filled]
```

### 21.2 Testing
```bash
# Run all tests
[To be filled]

# Run tests with coverage
[To be filled]

# Run specific test file
[To be filled]
```

### 21.3 Build & Deploy
```bash
# Build for production
[To be filled]

# Deploy to staging
[To be filled]

# Deploy to production
[To be filled]
```

### 21.4 Utilities
```bash
# Lint code
[To be filled]

# Format code
[To be filled]

# Type check
[To be filled]
```

**Section Status:** NOT STARTED

---

## 22. Code Style & Examples

*Concrete code snippets showing expected patterns*

### 22.1 General Style Rules
- [To be filled - e.g., "Use functional components, not class components"]
- [To be filled]

### 22.2 Example: Component Pattern
```typescript
// GOOD - Follow this pattern
[To be filled with concrete code example]
```

```typescript
// BAD - Avoid this pattern
[To be filled with anti-pattern example]
```

### 22.3 Example: API/Service Pattern
```typescript
// GOOD - Follow this pattern
[To be filled with concrete code example]
```

### 22.4 Example: Error Handling Pattern
```typescript
// GOOD - Follow this pattern
[To be filled with concrete code example]
```

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
```
[type]: [short description]

[optional body]

[optional footer]
```

**Types:** feat, fix, docs, style, refactor, test, chore

**Example:**
```
feat: add user authentication flow

- Implement login/logout functionality
- Add JWT token handling
- Create auth context provider

Closes #123
```

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
```

#### `scripts/end-prd-session.sh`

```bash
#!/bin/bash
# End a PRD session - removes state file

STATE_FILE="./.prd-state"

if [ -f "$STATE_FILE" ]; then
    # Read session file path before deleting state
    SESSION_FILE=$(grep "SESSION_FILE=" "$STATE_FILE" | cut -d'=' -f2)
    COMPLETED=$(grep "COMPLETED_SECTIONS=" "$STATE_FILE" | cut -d'=' -f2)

    # Remove state file
    rm "$STATE_FILE"

    echo "ENDED=1"
    echo "SESSION_FILE=$SESSION_FILE"
    echo "COMPLETED_SECTIONS=$COMPLETED"
else
    echo "ENDED=0"
    echo "ERROR=No active PRD session"
fi
```

#### `scripts/approve-prd-websearch.sh`

```bash
#!/bin/bash
# Auto-approve WebSearch during active PRD sessions

STATE_FILE="./.prd-state"

# Only auto-approve if PRD session is active
if [ -f "$STATE_FILE" ]; then
  source "$STATE_FILE"
  if [ "$PRD_ACTIVE" = "1" ]; then
    cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "PRD session - web search for requirements research"
  }
}
EOF
    exit 0
  fi
fi

# Don't interfere with other operations
exit 0
```

### 6. AskUserQuestion Tool Reference

The `AskUserQuestion` tool presents structured choices to users. Format:

```json
{
  "questions": [
    {
      "question": "The question text?",
      "header": "Short label",
      "multiSelect": false,
      "options": [
        {"label": "Option 1", "description": "What this option means"},
        {"label": "Option 2", "description": "What this option means"},
        {"label": "Option 3", "description": "What this option means"},
        {"label": "Option 4", "description": "What this option means"}
      ]
    }
  ]
}
```

**Constraints:**
- Maximum 4 options per question
- Maximum 4 questions per call
- `multiSelect: true` allows multiple selections
- Users can always type "Other" for custom input

### 7. Complete Command Implementations

#### `commands/start.md`

```markdown
---
description: Start a new PRD session to transform ideas into a complete Product Requirements Document. Optionally import from a brainstorm session.
---

# Start PRD Session

You are now entering PRD (Product Requirements Document) mode. Your role shifts fundamentally.

## What You Are

- A requirements analyst, NOT a developer
- A clarifier of ambiguity, NOT a decision maker
- A documenter of needs, NOT a solution architect
- A questioner who ensures completeness, NOT someone who rushes to implementation

## Session Start Checklist

1. **FIRST: Check for brainstorm file** (if `$ARGUMENTS` contains `--from`)
   - Parse the filename from arguments
   - Read the brainstorm file to extract themes and ideas
   - Present them to user for selection

2. **Run the start script** to initialize session state:
   ```bash
   PLUGIN_PATH/scripts/start-prd-session.sh "TOPIC_HERE" "BRAINSTORM_FILE_OR_EMPTY"
   ```

   **IMPORTANT**: Replace `PLUGIN_PATH` with the actual path from the `<prd-plugin-path>` tag in your context.

3. **Present the PRD overview** (shown below)

4. **Begin with Problem Statement section**

## PRD Overview (Present at Start)

Display this guide:

```
PRD MODE ACTIVATED

I'll help you create a complete Product Requirements Document through interactive discussion.

We'll work through 25 sections:

Foundation (Taste Layer) - WE START HERE:
0. Vision & Principles    Soul of the product, non-negotiables

Core Requirements (1-8):
1. Problem Statement      5. Non-Functional Reqs
2. Target Users           6. Data Model
3. User Stories           7. UI/UX Specification
4. Functional Reqs        8. API Contract

Anti-Accidental-Architecture (9-12) - CRITICAL:
9. Change Analysis        11. Edge Cases & Errors
10. Architecture Decisions 12. Testing Strategy

Planning & Constraints (13-18):
13. Success Metrics       16. Dependencies
14. Scope Boundaries      17. Technical Constraints
15. Risks & Mitigations   18. Evolution Strategy

AI Implementation (19-24) - "Any AI Can Build It":
19. Tech Stack            22. Code Style & Examples
20. Project Structure     23. Git Workflow
21. Commands              24. AI Agent Boundaries

For each section, I'll:
- Explain what's needed
- Ask clarifying questions
- Draft content for your review
- Refine until you approve

Commands:
- /prd:section <name>  - Jump to a specific section
- /prd:status          - See completion progress
- /prd:review          - Check for gaps and issues
- /prd:refine          - Iterate on current section
- /prd:done            - Finalize and exit
- /prd:help            - Show this help

No code will be written. Only requirements documentation.
```

## If Brainstorm File Provided

If `$ARGUMENTS` contains `--from <filename>`:

1. Read the brainstorm file
2. Extract key themes and top ideas
3. Present to user:

```
IMPORTING FROM BRAINSTORM

I found these themes in your brainstorm session:
- [Theme 1]: [brief description]
- [Theme 2]: [brief description]
- [Theme 3]: [brief description]

Top ideas that emerged:
1. [Idea]
2. [Idea]
3. [Idea]
```

Then use AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "Which themes should we develop into requirements?",
      "header": "Import",
      "multiSelect": true,
      "options": [
        {"label": "Theme 1", "description": "[description]"},
        {"label": "Theme 2", "description": "[description]"},
        {"label": "Theme 3", "description": "[description]"},
        {"label": "All themes", "description": "Include everything from the brainstorm"}
      ]
    }
  ]
}
```

## Beginning with Vision & Principles (Section 0)

After setup, immediately start with the Vision & Principles section — this captures taste BEFORE requirements:

"Before we dive into requirements, let's capture the **soul** of this product. This is Section 0: Vision & Principles.

AI can generate technically correct code, but only you can define what 'feels right.' I need to understand your taste and judgment:

1. **In one sentence**, what is this product and why does it matter?
2. **What are your non-negotiables?** Principles that must NEVER be violated, even if technically convenient?
3. **What would feel WRONG?** If the final product had certain characteristics, it would be a failure regardless of working correctly — what are those?
4. **What should it FEEL like to use?** What's the vibe, personality, or aesthetic?
5. **What products do you admire** that have a similar feel? Why?

Let's start with #1: In one sentence, what is this product and why does it matter?"

**After Vision & Principles is complete, move to Problem Statement.**

## Section Workflow (Dialogue, Not Interrogation)

For each section, follow this taste-aware workflow:

1. **Explain** what the section needs and why it matters
2. **Ask targeted questions** to understand requirements
3. **Propose** initial content based on answers (Claude proposes first)
4. **Taste check** — Ask: "Does this feel right? Is anything here bloat? What would you refuse to compromise on?"
5. **Refine** based on user's judgment reactions (not just facts)
6. **Iterate** until user says "approved" or "looks good"
7. **Update** session file with finalized content
8. **Mark complete** in state tracking
9. **Move** to next section

**Key UX Principle:** The user approves the VISION, not just the facts. Claude defers to human judgment on design decisions.

## Arguments

`$ARGUMENTS` may contain:
- Just a topic: `checkout flow improvement`
- Topic with brainstorm reference: `checkout flow --from brainstorm-checkout-20260119.md`
- Nothing (will prompt for topic)

If no topic provided, ask: "What product or feature are we documenting requirements for?"
```

#### `commands/section.md`

```markdown
---
description: Navigate to a specific PRD section to view or edit it.
---

# Navigate to PRD Section

The user wants to jump to a specific section of the PRD.

## Arguments

`$ARGUMENTS` contains the section name. Valid sections:
- `problem` or `problem_statement`
- `users` or `target_users`
- `stories` or `user_stories`
- `functional` or `functional_requirements`
- `nonfunctional` or `non_functional_requirements`
- `data` or `data_model`
- `ui` or `ux` or `ui_ux_specification`
- `api` or `api_contract`
- `metrics` or `success_metrics`
- `acceptance` or `acceptance_criteria`
- `scope` or `scope_boundaries`
- `risks` or `risks_mitigations`
- `dependencies`
- `constraints` or `technical_constraints`

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
```

#### `commands/status.md`

```markdown
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
```

#### `commands/review.md`

```markdown
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
```

#### `commands/refine.md`

```markdown
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
```

#### `commands/done.md`

```markdown
---
description: Finalize the PRD session, generate final document, and exit PRD mode.
---

# End PRD Session

The user is ready to finalize their PRD and exit PRD mode.

## Actions

1. **Run quick review** to check completeness
2. **Add final summary** to session file
3. **Run end script** to clear state
4. **Display completion summary**
5. **Offer next steps**

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

2. **Run end script:**
```bash
PLUGIN_PATH/scripts/end-prd-session.sh
```

3. **Display completion:**

```
PRD SESSION COMPLETE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your PRD has been saved to:
[session file path]

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
```

#### `commands/help.md`

```markdown
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

  /prd:done              Finalize PRD and exit

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

  PRD saved to: prd-[topic]-[timestamp].md
  Located in: current working directory

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
```

### 8. Complete File Structure (Standalone PRD Plugin)

```
claude-prd-god/                        # Plugin directory name
├── .claude-plugin/
│   └── plugin.json                # Plugin metadata
├── commands/
│   ├── start.md                   # /prd:start
│   ├── section.md                 # /prd:section
│   ├── status.md                  # /prd:status
│   ├── review.md                  # /prd:review
│   ├── refine.md                  # /prd:refine
│   ├── done.md                    # /prd:done
│   └── help.md                    # /prd:help
├── hooks/
│   ├── hooks.json                 # Hook configuration
│   └── prd-enforcer.sh            # UserPromptSubmit hook
└── scripts/
    ├── start-prd-session.sh       # Creates .prd-state and prd-*.md
    ├── end-prd-session.sh         # Removes .prd-state
    ├── approve-prd-write.sh       # Auto-approves prd-*.md writes
    ├── approve-prd-bash.sh        # Auto-approves session scripts
    └── approve-prd-websearch.sh   # Auto-approves web searches

Total: 12 files
```

**Note:** This plugin is completely independent from the brainstorm plugin. Users can optionally import brainstorm session files using `/prd:start topic --from brainstorm-file.md`, but the brainstorm plugin is NOT required.

### 9. Installation

To install the PRD plugin:

**Option A: CLI flag**
```bash
claude --plugin-dir /path/to/prd-plugin
```

**Option B: User settings** (`~/.claude/settings.json`):
```json
{
  "pluginDirs": ["/path/to/prd-plugin"]
}
```

**Option C: Project settings** (`.claude/settings.json` in project):
```json
{
  "pluginDirs": ["/path/to/prd-plugin"]
}
```

### 10. Making Scripts Executable

After creating all files, make scripts executable:

```bash
chmod +x hooks/prd-enforcer.sh
chmod +x scripts/start-prd-session.sh
chmod +x scripts/end-prd-session.sh
chmod +x scripts/approve-prd-write.sh
chmod +x scripts/approve-prd-bash.sh
chmod +x scripts/approve-prd-websearch.sh
```

---

---

## Standalone Implementation Summary

This document is **fully self-contained**. A fresh Claude session can implement the complete PRD plugin from scratch using ONLY this document.

### What This Document Contains

| Component | Location in Document |
|-----------|---------------------|
| **Design Philosophy** | Sections: Taste Layer, Accidental Architecture, AI Specs |
| **All 25 PRD Sections** | Table with purposes and completeness criteria |
| **Plugin Metadata** | `plugin.json` in Section 2 |
| **Hook Enforcement** | `prd-enforcer.sh` in Section 1 |
| **Approval Scripts** | `approve-prd-*.sh` in Sections 2-3 |
| **Session Scripts** | `start-prd-session.sh`, `end-prd-session.sh` in Section 5 |
| **hooks.json** | Section 4 (PRD-only, no brainstorm references) |
| **All 7 Commands** | Complete `.md` files in Section 7 |
| **Session Template** | Full 25-section markdown template in Section 5 |
| **File Structure** | Section 8 (12 files total) |
| **Installation** | Section 9 |

### Implementation Checklist for Fresh Session

A new Claude session should:

1. ✅ Create directory structure: `claude-prd-god/`
2. ✅ Create `.claude-plugin/plugin.json`
3. ✅ Create `hooks/hooks.json` (PRD-only config)
4. ✅ Create `hooks/prd-enforcer.sh`
5. ✅ Create all 5 scripts in `scripts/`
6. ✅ Create all 7 command files in `commands/`
7. ✅ Run `chmod +x` on all `.sh` files
8. ✅ Test with `/prd:help`

### Relationship to Brainstorm Plugin

| Aspect | Status |
|--------|--------|
| **Dependency** | NONE — PRD is fully standalone |
| **Shared code** | NONE — separate plugin directory |
| **Optional integration** | `/prd:start --from brainstorm-file.md` can import brainstorm output |
| **Required to use PRD** | NO — user can start fresh with `/prd:start topic` |

### Key Design Decisions Captured

1. **Taste Layer** — Captures human judgment before requirements
2. **Anti-Accidental-Architecture** — Prevents fragile systems
3. **AI Implementation Sections** — Ensures "any AI agent can build it"
4. **Hook Enforcement** — Prevents code writing during PRD mode
5. **25 Sections** — Comprehensive coverage for complete PRDs

---

**An implementer can create the complete PRD plugin from scratch using only this document, without referencing the brainstorm plugin or any external codebase.**
