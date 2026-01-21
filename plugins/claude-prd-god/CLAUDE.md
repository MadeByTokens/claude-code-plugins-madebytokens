# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin that transforms brainstorm ideas into Product Requirements Documents (PRDs) through interactive, section-by-section refinement. The plugin enforces "requirements analyst" mode—preventing code generation until requirements are complete.

## Architecture

### Plugin System
- **`.claude-plugin/plugin.json`** - Plugin metadata (name: `prd`, version, description)
- **`commands/*.md`** - 7 slash commands with YAML frontmatter + Claude instructions
- **`hooks/hooks.json`** - Hook configuration binding tools to approval scripts
- **`hooks/prd-enforcer.sh`** - UserPromptSubmit hook that injects rules on every prompt when `.prd-state` exists

### Hook Enforcement Flow
1. User runs `/prd:start` → `start-prd-session.sh` creates `.prd-state` + `prd-*.md`
2. `prd-enforcer.sh` fires on every prompt, checks for `.prd-state`
3. If active, outputs `<prd-mode-enforced>` rules blocking code generation
4. PreToolUse hooks validate Write/Bash/WebSearch operations
5. `/prd:done` → `generate-final-prd.sh` creates clean final PRD, then `end-prd-session.sh` removes `.prd-state`

### Auto-Approval Scripts (`scripts/`)
- **`approve-prd-write.sh`** - Only auto-approves `prd-*.md` files
- **`approve-prd-bash.sh`** - Only auto-approves session scripts (`start-prd-session.sh`, `end-prd-session.sh`, `generate-final-prd.sh`)
- **`approve-prd-websearch.sh`** - Allows web searches when PRD session is active

### State Management
- **`.prd-state`** - Bash-sourceable file with session variables (`PRD_ACTIVE`, `SESSION_FILE`, `CURRENT_SECTION`, `COMPLETED_SECTIONS`, etc.)
- **`prd-[topic]-[timestamp].md`** - Working PRD document with 25-section template and status markers
- **`prd-[topic]-FINAL.md`** - Clean, stakeholder-ready PRD with executive summary (generated on `/prd:done`)

## 25 PRD Sections

Grouped by purpose:
- **0**: Vision & Principles (Taste Layer—captures human judgment before specs)
- **1-8**: Core Requirements (problem, users, stories, functional, non-functional, data, UI/UX, API)
- **9-12**: Anti-Accidental-Architecture (change analysis, architecture decisions, edge cases, testing strategy)
- **13-18**: Planning (metrics, scope, risks, dependencies, constraints, evolution)
- **19-24**: AI Implementation (tech stack, project structure, commands, code style, git workflow, AI boundaries)

## Key Design Decisions

1. **Hook-enforced behavior** - Rules injected on EVERY prompt prevent Claude from "forgetting" it's in requirements mode
2. **Taste Layer first (Section 0)** - Captures subjective product vision before diving into specs
3. **Anti-Accidental-Architecture mandatory** - Forces answers to 5 pre-coding questions to prevent fragile systems
4. **Defense in depth** - 5 layers prevent code generation: rules injection, file approval restriction, user permission gates, bash restriction, explicit exit only
5. **Separate state from output** - `.prd-state` is deleted on exit; `prd-*.md` document is preserved

## Command Reference

| Command | Purpose |
|---------|---------|
| `/prd:start [topic] --from file.md` | Initialize session, optionally import brainstorm |
| `/prd:section <name>` | Navigate to specific section (25 sections with aliases) |
| `/prd:status` | Show completion progress |
| `/prd:review` | Gap analysis with ~100 checklist items |
| `/prd:refine` | Iterate on current section |
| `/prd:done` | Generate final PRD and exit mode |
| `/prd:help` | Show help |

## Git Conventions

- Commit messages are always one line
- No Co-Authored-By or other AI attribution in commits

## Philosophy

See `PRD_PHILOSOPHY.md` for the complete rationale. Key concepts:
- **The "vibe coding" problem** - AI generates code without intentional system design, leading to fragile architectures
- **Five pre-coding questions** every PRD must answer: What will change? Shared or local? Source of truth? What breaks if X changes? How to test?
- **AI Implementation Spec** - Ensures any AI agent can build without asking questions (exact versions, file structure, commands, code examples)
