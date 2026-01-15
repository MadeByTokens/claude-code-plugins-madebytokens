---
description: Display help information for the chess plugin
---

# Chess Help

Display available commands and how to use the chess plugin.

## Output

```
=== Claude Chess ===

A chess opponent using three-agent deliberation (Strategist → Devil's Advocate → Arbiter executes).

COMMANDS:
  /chess:play      Start a new game or continue current one
  /chess:status    Show current board and game state
  /chess:analyze   Post-game analysis of moves
  /chess:learn     Extract lessons to memory
  /chess:help      This help message

QUICK START:
  1. Run /chess:play
  2. Select opponent type:
     - "You (Human)" to play against the AI yourself
     - "Stockfish" to watch AI vs engine
  3. Choose AI's color, skill level, personality
  4. Play! Enter your moves in UCI format when prompted (e.g., e2e4)

  Mood and strategic focus are randomized each game for variety.

SKILL LEVELS (AI):
  Beginner   - 1 candidate, no critique (easy)
  Casual     - 2 candidates, light critique
  Club       - 3 candidates, full critique (default)
  Expert     - 3+ candidates, aggressive critique (hard)

STOCKFISH LEVELS (when playing vs Stockfish):
  Beginner (1)     - Very weak, blunders often
  Intermediate (8) - Club player level
  Expert (17)      - Master level
  Maximum (20)     - Full strength (~3200 ELO)
  Custom           - Enter any value 0-20

PERSONALITIES:
  Silent            - No commentary
  Friendly Coach    - Encouraging, explains ideas
  Cocky Grandmaster - Confident, "I saw that 10 moves ago"
  Nervous Amateur   - Self-deprecating, panics when behind
  Dramatic Narrator - Treats every move like an epic battle
  Vintage Hustler   - Street chess vibes, casual smack talk

MOVE FORMAT:
  Moves use UCI notation: e2e4, g1f3, e7e8q (promotion)
  Not algebraic: e4, Nf3, e8=Q

DEPENDENCIES:
  pip install chess mcp
  apt install stockfish  (or brew install stockfish)

MCP TOOLS:
  The MCP server (scripts/chess_server.py) exposes:
  - chess_verify, chess_display, chess_gui, chess_move
  - chess_legal_moves, chess_validate, chess_opponent_move
  - chess_init_game, chess_get_state, chess_analyze, chess_check_end
  - chess_log_turn (logs deliberation for /chess:analyze and /chess:learn)
  - chess_remember (saves agent observations to memory.md)
  - chess_calculate (sandboxed Python for position analysis)

CALCULATION TOOL:
  The Strategist can run small Python snippets to verify analysis:
  - Sandboxed: no imports, 30 line limit, 500ms timeout
  - Board provided as 8x8 list
  - Used as a "clutch" for specific checks, not the main tool

  All tools auto-approved via hooks/hooks.json

FILES:
  state/game.json           - Current game state (in your working directory)
  state/memory.md           - Long-term learning
  state/game.log            - Deliberation audit trail
  .chess-working/           - Agent outputs (candidates, refutations, decision)

For more details, see README.md
```
