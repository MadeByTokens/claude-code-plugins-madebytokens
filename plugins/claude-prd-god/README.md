<img width="1024" height="339" alt="image" src="https://github.com/user-attachments/assets/00200a4f-480b-493b-bd8a-8e87f27d4741" />

# claude-prd-god

A Claude Code plugin for creating Product Requirements Documents through interactive, section-by-section refinement.

AI makes it dangerously easy to skip straight to code. You describe something, it builds something, and two weeks later you're ripping it apart because nobody asked "what happens when the database is down?" or "should this config live in one place or twenty?" This plugin locks Claude into requirements-analyst mode—no code allowed—until you've answered the questions that matter. It captures your taste and judgment (things AI can't infer), forces you through Anti-Accidental-Architecture checkpoints, and produces a spec detailed enough that any AI agent can build from it without asking clarifying questions.

## Installation

Add to `~/.claude/settings.json`:

```json
{
  "pluginDirs": ["/path/to/claude-prd-god"]
}
```

Or use the CLI flag:

```bash
claude --plugin-dir /path/to/claude-prd-god
```

## Commands

| Command | Description |
|---------|-------------|
| `/prd:start [topic]` | Start a new PRD session |
| `/prd:section <name>` | Jump to a specific section |
| `/prd:status` | Show completion progress |
| `/prd:review` | Analyze PRD for gaps |
| `/prd:refine` | Iterate on current section |
| `/prd:done` | Finalize, generate final document, and exit PRD mode |
| `/prd:help` | Show help |

### Starting a session

```
/prd:start checkout flow redesign
```

Import from a brainstorm session:

```
/prd:start checkout flow --from brainstorm-checkout-20260120.md
```

## PRD Sections (25 total)

**Foundation (Taste Layer)**
- 0: Vision & Principles

**Core Requirements (1-8)**
- 1: Problem Statement
- 2: Target Users
- 3: User Stories
- 4: Functional Requirements
- 5: Non-Functional Requirements
- 6: Data Model
- 7: UI/UX Specification
- 8: API Contract

**Anti-Accidental-Architecture (9-12)**
- 9: Change Analysis
- 10: Architecture Decisions
- 11: Edge Cases & Error Scenarios
- 12: Testing Strategy

**Planning & Constraints (13-18)**
- 13: Success Metrics
- 14: Scope Boundaries
- 15: Risks & Mitigations
- 16: Dependencies
- 17: Technical Constraints
- 18: Evolution Strategy

**AI Implementation (19-24)**
- 19: Tech Stack
- 20: Project Structure
- 21: Commands
- 22: Code Style & Examples
- 23: Git Workflow
- 24: AI Agent Boundaries

## How it works

1. `/prd:start` creates a `.prd-state` file and a `prd-[topic]-[timestamp].md` session file
2. The `prd-enforcer.sh` hook injects rules on every prompt while PRD mode is active
3. Claude works through sections interactively, asking questions and drafting content
4. You review and approve each section before moving on
5. `/prd:done` generates a clean final PRD with executive summary and removes the state file

## Hook enforcement

While PRD mode is active, Claude:
- Cannot write code files (only `prd-*.md` files are auto-approved)
- Cannot run arbitrary bash commands (only session scripts are approved)
- Must follow the section workflow
- Cannot exit PRD mode except via `/prd:done`

## Files generated

- `.prd-state` - Session state (deleted on `/prd:done`)
- `prd-[topic]-[timestamp].md` - Working document with full history (preserved)
- `prd-[topic]-FINAL.md` - Clean, stakeholder-ready PRD with executive summary (generated on `/prd:done`)

## Project structure

```
claude-prd-god/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── start.md
│   ├── section.md
│   ├── status.md
│   ├── review.md
│   ├── refine.md
│   ├── done.md
│   └── help.md
├── hooks/
│   ├── hooks.json
│   └── prd-enforcer.sh
└── scripts/
    ├── start-prd-session.sh
    ├── end-prd-session.sh
    ├── generate-final-prd.sh
    ├── approve-prd-write.sh
    ├── approve-prd-bash.sh
    └── approve-prd-websearch.sh
```

## License

MIT
