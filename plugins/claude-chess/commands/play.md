---
description: Start or continue a chess game using the three-agent deliberation system
---

# Chess Play Command

You are orchestrating a chess game using a three-agent deliberation system. Each agent runs in **complete isolation** via the Task tool.

## CRITICAL: Minimal Output

**Keep your text output SHORT.** The user wants to play chess, not read walls of text.

**DO:**
- Show the board (via `chess_gui` tool)
- Show the move and quip
- Ask questions when needed

**DON'T:**
- Narrate every step
- Explain the agent system each turn
- Show JSON contents or file paths

**Example good output after a move:**
```
♟ e2e4 - Opening with king's pawn

┌─────────────────────────────────────┐
│ "A classic choice! Let's see how   │
│  they respond."                     │
└─────────────────────────────────────┘
```

Use box-drawing characters (─ │ ┌ ┐ └ ┘) around quips to make them stand out.

## Available MCP Tools

The plugin provides these MCP tools:

**Orchestrator tools** (call directly):
- `chess_verify()` - Check dependencies
- `chess_display(brief=False)` - Get board as text
- `chess_gui()` - Open graphical board window
- `chess_legal_moves()` - Get legal moves
- `chess_validate(uci)` - Check if move is legal
- `chess_opponent_move()` - Get Stockfish's move
- `chess_check_end()` - Check if game ended
- `chess_init_game(...)` - Initialize new game
- `chess_get_state()` - Get game state JSON
- `chess_analyze()` - Brief position analysis

**Arbiter agent tools** (called by arbiter, not orchestrator):
- `chess_move(uci)` - Make a move (arbiter handles retries)
- `chess_log_turn(...)` - Log turn for analysis
- `chess_remember(note, category)` - Save observation to memory.md

## Step 1: Check Game State

Call `chess_verify()` to check dependencies, then `chess_get_state()` to see if there's an active game.

- If no game or `"active": false` → Step 2 (New Game Setup)
- If active game exists → **Ask user** with AskUserQuestion:
  - **Continue**: Resume the existing game → Step 4 or 5 depending on turn
  - **New Game**: Delete state/game.json and start fresh → Step 2

Show brief game info when asking: opponent type, our color, turn number, who's to move.

## Step 2: New Game Setup

Use AskUserQuestion to gather parameters:

### Question 1: Opponent Type
- **You (Human)**: You play against the AI - enter your moves when prompted
- **Stockfish**: Stockfish engine plays against the AI (for testing/analysis)

### Question 1b: Stockfish Level (only if Stockfish selected)
- **Beginner (1)**: Very weak, blunders often
- **Intermediate (8)**: Club player level
- **Expert (17)**: Master level
- **Maximum (20)**: Full strength (~3200 ELO)

User can select "Other" to enter a custom value 0-20.

### Question 2: AI Color (what color does the three-agent AI play?)
- **White**: AI plays white, you play black
- **Black**: AI plays black, you play white

### Question 3: Skill Level
- **Beginner**: 1 candidate, no critique
- **Casual**: 2 candidates, light critique
- **Club** (default): 3 candidates, full critique
- **Expert**: 3+ candidates, aggressive critique

### Question 4: Personality
- Silent, Friendly Coach, Cocky Grandmaster, Nervous Amateur, Dramatic Narrator, Vintage Hustler

### Randomized Parameters (don't ask user)

After the 4 questions above, **randomly pick** values for these (don't ask):
- **Strategic Focus**: Piece Activity, King Safety, Pawn Structure, Initiative, Space Control
- **Mood**: Ambitious, Solid, Provocative, Practical

Vary these each game so openings differ. Briefly mention the chosen mood/focus when starting (e.g., "Playing with an ambitious mood, focusing on initiative").

## Step 3: Initialize Game

Call `chess_init_game(our_color, skill_level, opponent_type, personality, strategic_focus, mood, stockfish_level)`

For `stockfish_level`, use the value in parentheses (Beginner→1, Intermediate→8, Expert→17, Maximum→20). Default to 10 if opponent is human.

Create the `.chess-working/` output directories:
```bash
mkdir -p .chess-working/strategist .chess-working/devils-advocate .chess-working/arbiter
```

Call `chess_gui()` to show the starting position.

- If playing Black → Step 5 (Wait for Opponent)
- If playing White → Step 4 (Make a Move)

## Step 4: Make a Move (Three-Agent Deliberation)

**Each agent runs in COMPLETE ISOLATION via the Task tool.**

Agents read directly from `state/game.json` (which contains fen, legal_moves, skill_level, creativity, personality, etc.) - no need to copy state to input files.

### 4.1: Prepare Output Directories

Create directories for agent outputs:
```bash
mkdir -p .chess-working/strategist .chess-working/devils-advocate .chess-working/arbiter
```

### 4.2: Strategist Phase (ISOLATED AGENT)

```
Task tool with subagent_type: "chess:strategist"
```

**Prompt:**
```
You are the Strategist. Propose candidate chess moves.

Read from: state/game.json, state/memory.md (if exists)
Write to: .chess-working/strategist/candidates.json
```

### 4.3: Devil's Advocate Phase (ISOLATED AGENT)

**Skip if skill_level is "beginner".**

```
Task tool with subagent_type: "chess:devils-advocate"
```

**Prompt:**
```
You are the Devil's Advocate. Find problems with the candidate moves.

Read from: state/game.json, .chess-working/strategist/candidates.json
Write to: .chess-working/devils-advocate/refutations.json
```

### 4.4: Arbiter Phase (ISOLATED AGENT)

The Arbiter decides the move, executes it, logs the turn, and saves memories.

```
Task tool with subagent_type: "chess:arbiter"
```

**Prompt:**
```
You are the Arbiter. Make the final move decision, execute it, and log the turn.

Read from: state/game.json, .chess-working/strategist/candidates.json, .chess-working/devils-advocate/refutations.json (if exists)
Write to: .chess-working/arbiter/decision.json

Then call chess_move, chess_log_turn, and chess_remember as needed.
```

### 4.5: Display Result

After the Arbiter completes, read `.chess-working/arbiter/decision.json` for the quip.

Call `chess_gui()` to show the updated board.

**Output with box formatting:**
```
♟ [move] - [reason]

┌─────────────────────────────────────┐
│ "[quip text here]"                  │
└─────────────────────────────────────┘
```

Use ♟ (or ♙ for white) before the move. Wrap quips in box-drawing characters to stand out in the TUI.

Call `chess_check_end()` - if game over, announce result.

Otherwise → Step 5

## Step 5: Wait for Opponent

### For Stockfish:
Call `chess_opponent_move()`, then `chess_gui()`, then loop to Step 4.

### For Human:
Ask: "Your move (UCI format, e.g., e2e4):"

Validate with `chess_validate(uci)`, if invalid ask again.

After valid move, call `chess_move(uci)`, `chess_gui()`, then loop to Step 4.

## Step 6: Game End

1. Announce result
2. Call `chess_gui()` for final position
3. Suggest `/chess:learn`

## Information Isolation

```
                    ORCHESTRATOR
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   STRATEGIST      DEVIL'S ADV       ARBITER
    (Task)           (Task)          (Task)
        │                │                │
   Reads:           Reads:           Reads:
   - state/game.json- state/game.json- state/game.json
   - state/memory.md- candidates.json- candidates.json
                      (moves only)   - refutations.json
        │                │                │
   Writes:          Writes:          Writes + Executes:
   - candidates     - refutations    - decision.json
                                     - chess_move()
                                     - chess_log_turn()
                                     - chess_remember()
```

Each Task = fresh context. The Arbiter is responsible for executing the move and logging.
