---
description: Extract lessons from completed games and update long-term memory
---

# Chess Learn Command

Extract lessons from the most recent game (or specified game) and update memory.md for improved future play.

## Purpose

The Learn command is the bridge between individual games and long-term improvement. It:
1. Reads the game log with full deliberation records
2. Identifies patterns and lessons
3. Compresses verbose reasoning into actionable nuggets
4. Updates memory.md with new knowledge
5. Prunes outdated information

## Step 1: Load Game Data

Read all relevant files:
```
Read: state/game.json
Read: state/game.log
Read: state/memory.md
```

## Step 2: Parse Game Log

The game.log contains entries like:
```
[timestamp] [TURN N] [strategist] Candidates: e2e4, d2d4, g1f3
[timestamp] [TURN N] [devils-advocate] Refutations: e2e4-SOUND, d2d4-WARNING, g1f3-SOUND
[timestamp] [TURN N] [arbiter] Decision: e2e4 - controls center
```

Extract:
- All candidate moves considered
- All refutations (especially WARNING and REFUTED)
- All decisions made
- Turning points where evaluation changed

## Step 3: Identify Learnable Moments

### Tactical Patterns
Look for:
- Moves marked REFUTED - what was the tactical threat?
- Moves marked WARNING that we played anyway - did it work out?
- Positions where we missed tactics

Extract pattern: "Check for [tactic type] when [situation]"

### Opening Results
- What opening did we play?
- How did it turn out (win/loss/draw)?
- Were there any problems in the opening?

Update opening book with result.

### Opponent-Specific Notes
If playing against a known opponent (Stockfish level, or named human):
- What tendencies did they show?
- What worked against them?
- What didn't work?

### Mistakes Made
For each significant mistake:
- What did we play?
- What should we have played?
- Why did we miss it?

Compress into a lesson: "Before [action], check [what to check]"

### Brilliant Moves
If we or opponent played something clever:
- What was the position?
- What was the idea?
- Why was it good?

Save for future reference.

## Step 4: Apply Compression Rules

### Compression Algorithm

**EXTRACT** the core lesson (1 sentence max):
- What went wrong/right?
- Why?

**GENERALIZE** if possible:
- "Missed Bb4+ pin" → "Check all checks before capturing"
- "Opponent played Qh5" → "Watch for early queen attacks vs 1.e4"

**DEDUPLICATE** against existing memory:
- If similar lesson exists: increment frequency counter
- If contradicts old lesson: evaluate which is more reliable

**DISCARD** if not actionable:
- "The position was complicated" → DISCARD
- "I felt nervous" → DISCARD
- "Knight on e5 was strong" → KEEP if generalizable

### Examples

```
BEFORE (game.log, 200 words):
[TURN 12] [strategist] Considering Qxd4 because it wins a pawn...
[TURN 12] [devils-advocate] REFUTED: Bb4+ pins knight to king
[TURN 12] [arbiter] Rejecting Qxd4, playing Nf3 instead

AFTER (memory.md entry, 15 words):
- **Pin check**: Before capturing material, verify no pin/discovered check
  - Learned: 2024-01-15
```

## Step 5: Update Memory Sections

### Opening Section
Update with:
- Opening name and recognition
- Typical plans and ideas
- Win/Loss/Draw record

### Opponent Patterns Section
Update with:
- Tendencies observed
- What worked against them
- Record against them

### Position Themes Section
Add new patterns with:
- Tactical motif name (forks, pins, etc.)
- Positional themes (weak squares, outposts)
- When first seen

### Lessons Section
Add with:
- Date learned
- Specific lesson (mistakes to avoid)
- Related game reference

## Step 6: Prune Old Data

Apply memory limits:

| Category | Max Entries | Pruning Strategy |
|----------|-------------|------------------|
| Opening | 20 lines | Keep most played |
| Opponent Patterns | 10 | Remove oldest inactive |
| Position Themes | 50 | Remove least frequent |
| Lessons | 30 | Remove if not triggered in 10 games |

If over limit, remove the least relevant entries.

## Step 7: Generate Summary

Output what was learned:

```
=== Learning Complete ===

Game: [Date] vs [Opponent]
Result: [Win/Loss/Draw]

New Lessons Added:
1. [Lesson summary]
2. [Lesson summary]

Opening Updated:
- Italian Game: Now 4W-1L

Position Themes Reinforced:
- Pin awareness (3rd occurrence)

Memory Status:
- Opening: 8/20
- Opponent Patterns: 3/10
- Position Themes: 23/50
- Lessons: 15/30

Next game recommendations:
- [Based on patterns seen]
```

## Step 8: Write Updated Memory

```
Write: state/memory.md
```

Ensure the new memory.md:
- Maintains proper markdown formatting
- Stays within size limits
- Has clear section headers
- Uses consistent formatting

## Automatic Learning (Optional)

If configured, learning can happen automatically after each game.
Check game.json for `"auto_learn": true` setting.

## Manual Learning from Old Games

If the user wants to learn from a specific past game:
1. Load that game's log file
2. Apply the same extraction process
3. Update memory with new lessons

## Memory File Format

The memory.md file should maintain this structure:

```markdown
# Game Memory

## Opening
[opening recognition, typical plans, win/loss records]

## Opponent Patterns
[known opponents with tendencies]

## Position Themes
[tactical and positional patterns]

## Lessons
[specific lessons with dates]
```

Keep each section focused and within token budget (~300 tokens total when retrieved).
