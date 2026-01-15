# Claude Chess Plugin - Initial Plan

## Project Goal

Create a Claude Code Plugin that plays chess by simulating human-like reasoning rather than brute-force calculation. The focus is on **fun and enjoyable gameplay** at various skill levels, not maximum ELO. Still, we don't want to be embarrassed with something that is so low ELO that people will consider a waste of tokens. It needs to be a good opponent according to the user's choice.

## Core Philosophy

1. **Human-Like Reasoning**: The agent forms high-level plans and checks for tactical refutations, rather than calculating every possible move.
2. **Agent Isolation**: Inspired by the [bon-cop-bad-cop](https://github.com/MadeByTokens/bon-cop-bad-cop) plugin - agents operate with information barriers to get better outcomes.
3. **Persistent Learning**: The agent maintains memory of past games, openings, and mistakes.
4. **Controlled Creativity**: The agent varies its play through structured randomness - different strategic focuses, opening choices, and moods - to remain unpredictable and engaging.
5. **Stockfish for Testing Only**: Not used as a crutch for decision-making, only as an opponent for validation.

---

## Architecture

### Chess Move Standard: UCI Notation

The universal standard for chess move communication:
```
e2e4     # pawn e2 to e4
g1f3     # knight g1 to f3
e7e8q    # pawn promotes to queen
e1g1     # castling (king moves two squares)
```

### Abstraction Layer

```
┌─────────────────────────────────────────┐
│           Chess Plugin Core             │
│  (speaks UCI: "e2e4", "g1f3", etc.)     │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌──────────┐
│Stockfish│  │ Lichess  │  │  Local   │
│Adapter  │  │ Adapter  │  │ Board UI │
└────────┘  └──────────┘  └──────────┘
```

---

## Agent Structure (bon-cop-bad-cop Pattern)

| TDD Plugin Role | Chess Plugin Role |
|-----------------|-------------------|
| Test Writer (creates challenges) | **Devil's Advocate** (imagines opponent's best reply) |
| Code Writer (solves blind) | **Strategist** (proposes candidates without seeing critique) |
| Reviewer (validates all) | **Arbiter** (validates legality, evaluates position) |

### Information Barriers

- **Strategist**: Sees position + memory, proposes candidate moves
- **Devil's Advocate**: Sees position + candidates, tries to refute them
- **Arbiter**: Sees everything, issues final verdict on move selection

---

## Directory Structure

```
chess-grandmaster/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── strategist.md       # Proposes candidate moves (sees position + memory)
│   ├── devils-advocate.md  # Tries to refute moves (sees position + candidates)
│   └── arbiter.md          # Final validator (sees everything, issues verdict)
├── commands/
│   ├── play.md             # Main game loop
│   ├── analyze.md          # Post-game analysis
│   └── status.md           # Show current game state
├── adapters/
│   ├── interface.py        # Abstract base: get_position(), make_move(uci)
│   ├── stockfish.py        # Stockfish adapter (for testing)
│   ├── lichess.py          # Lichess API adapter
│   └── local_board.py      # Simple terminal/GUI board
└── state/
    ├── game.json           # Current game state (FEN, move history, whose turn)
    ├── memory.md           # Long-term learning
    └── game.log            # Detailed reasoning audit trail
```

---

## Skill Levels (Without Stockfish)

Skill is controlled through **reasoning constraints**, not random mistakes:

| Level | Strategist Behavior | Devil's Advocate Behavior |
|-------|---------------------|---------------------------|
| **Beginner** | Only 1 candidate, ignores long-term plans | Disabled (no critique) |
| **Casual** | 2 candidates, sees 1 move ahead | Light critique, misses some tactics |
| **Club** | 3 candidates, positional awareness | Full critique, but limited depth |
| **Expert** | 3+ candidates, deep plans | Aggressive refutation, multiple lines |

Key insight: **weaker play = less deliberation**, not random mistakes.

---

## Creativity System (Preventing Repetitive Play)

### The Problem

LLMs tend toward predictable patterns because:
- Training data has strong biases (popular openings, common plans)
- Same position + same prompt → very similar candidate moves
- The model "learned" that certain moves are "good" in certain positions

Without intervention: **same FEN + same memory = similar moves 80%+ of the time**

### The Solution: Structured Randomness

At the start of each game, the system randomly selects parameters that influence play style without compromising quality:

#### Strategic Focus (randomly selected per game)

| Focus | Effect on Strategist |
|-------|---------------------|
| **Piece Activity** | Prioritize moves that activate pieces, even if unconventional |
| **King Safety** | Favor solid, defensive setups |
| **Pawn Structure** | Consider long-term pawn health in evaluations |
| **Initiative** | Prefer forcing moves that keep pressure |
| **Space Control** | Value central and territorial expansion |

#### Mood (affects risk tolerance)

| Mood | Risk Tolerance | Typical Behavior |
|------|----------------|------------------|
| **Ambitious** | High | Accept gambits, play for the win |
| **Solid** | Low | Prefer safe, proven lines |
| **Provocative** | Medium-High | Choose offbeat but sound variations |
| **Practical** | Medium | Balance risk vs reward pragmatically |

#### Opening Repertoire Rotation

The system maintains multiple openings per color and rotates to avoid staleness:

```
As White:
  - 1.e4 systems: Italian, Scotch, Vienna
  - 1.d4 systems: London, Queen's Gambit
  - 1.c4/1.Nf3: English, Réti

As Black vs 1.e4:
  - Sicilian, French, Caro-Kann, e5-based

As Black vs 1.d4:
  - King's Indian, Nimzo/Queen's Indian, Slav
```

Anti-repetition rule: "You played the Italian in your last 2 games → try something else"

### Implementation in game.json

```json
{
  "active": true,
  "fen": "...",
  "our_color": "white",
  "skill_level": "club",

  "creativity": {
    "strategic_focus": "piece_activity",
    "mood": "ambitious",
    "opening_choice": "sicilian",
    "recent_openings": ["italian", "italian", "scotch"]
  }
}
```

### How Creativity Parameters Reach the Strategist

The Strategist agent receives these parameters as part of its prompt:

```
# Current Position
FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

# Today's Game Parameters
- Strategic Focus: PIECE ACTIVITY
  → Prioritize moves that develop and activate your pieces
- Mood: AMBITIOUS
  → You're willing to accept gambits and take calculated risks
- Opening Note: You've played the Italian Game in your last 2 games
  → Consider varying your opening choice

# Relevant Memory
[...]

# Your task: Propose 3 candidate moves with reasoning
```

### Creativity vs Skill Level Interaction

| Skill Level | Creativity Behavior |
|-------------|---------------------|
| **Beginner** | Mood always "solid", limited opening repertoire |
| **Casual** | Random mood, basic repertoire rotation |
| **Club** | Full mood range, diverse repertoire |
| **Expert** | Full system + opponent-adaptive creativity |

### Anti-Repetition Memory

Track recent games to ensure variety:

```markdown
# Recent Game Styles (in memory.md)

## Last 5 Games
| Game | Opening | Focus | Mood | Result |
|------|---------|-------|------|--------|
| 5 | Italian | Piece Activity | Ambitious | Win |
| 4 | Italian | King Safety | Solid | Draw |
| 3 | Scotch | Initiative | Provocative | Loss |
| 2 | London | Pawn Structure | Practical | Win |
| 1 | Sicilian (Black) | Space | Ambitious | Win |

→ Avoid: Italian (played 2x recently), Solid mood (too predictable)
→ Suggest: d4 opening, Ambitious/Provocative mood
```

---

## Time Management

LLMs have no intrinsic time sense. Solution: external controller passes time context to agents.

```
┌──────────────────────────────────────┐
│         Time Controller              │
│  (external Python/bash process)      │
│                                      │
│  while time_remaining > threshold:   │
│      iteration = run_deliberation()  │
│      if iteration.has_move:          │
│          break                       │
│      time_remaining -= elapsed       │
│                                      │
│  # Pass time pressure to agent:      │
│  # "You have 30 seconds. Quick!"     │
└──────────────────────────────────────┘
```

The `play.md` command receives time info as context:
```yaml
# Current time situation:
# Your clock: 2:34
# Opponent clock: 4:12
# Time control: 5+3 (5 min + 3 sec increment)
# Pressure level: MODERATE
```

---

## State Persistence (bon-cop-bad-cop Pattern)

### game.json (Current Game State)
```json
{
  "active": true,
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "move_history": ["e2e4", "e7e5", "g1f3"],
  "our_color": "white",
  "skill_level": "club",
  "phase": "STRATEGIST_THINKING",
  "time_remaining": 300,
  "opponent_time": 300,

  "creativity": {
    "strategic_focus": "piece_activity",
    "mood": "ambitious",
    "opening_choice": "italian",
    "recent_openings": ["scotch", "london", "italian"]
  }
}
```

### memory.md (Long-Term Learning)
```markdown
# Chess Memory

## Opening Preferences
- As white: Prefer 1.e4, Italian Game
- As black: Sicilian Defense against 1.e4

## Lessons Learned
- 2024-01-15: Missed bishop skewer on long diagonal. Watch for this.
- 2024-01-14: Opponent "ChessMaster99" always plays Qh5 early. Prepare for it.

## Opponent Notes
- ChessMaster99: Aggressive, prone to overextension
```

### game.log (Audit Trail)
```
[2024-01-15 10:31:17] [TURN 5] [strategist] Candidates: e4, Nf3, c4
[2024-01-15 10:31:18] [TURN 5] [devils-advocate] Refuting e4: allows Bb4+ pin
[2024-01-15 10:31:19] [TURN 5] [arbiter] Selected: Nf3 (safe, develops piece)
[2024-01-15 10:31:20] [TURN 5] Move played: g1f3
```

---

## Context Management (Avoiding Bloat)

A critical design constraint: **each agent call must stay lean**. LLM context is expensive and bloated prompts degrade reasoning quality.

### Core Principle: FEN is the Source of Truth

The current board position (FEN) contains everything needed to make a move. Move history is for logging, not for agent reasoning.

```
GOOD: Agent receives FEN + relevant memory excerpts
BAD:  Agent receives FEN + full move history + full memory + game log
```

### What Each Agent Receives

| Agent | Receives | Does NOT Receive |
|-------|----------|------------------|
| **Strategist** | FEN, creativity params, ~3 relevant memory excerpts | Move history, game.log, opponent's thinking |
| **Devil's Advocate** | FEN, candidate moves (3-5 lines of text) | Memory, creativity params, strategist's full reasoning |
| **Arbiter** | FEN, candidates + critiques (summary form) | Raw game.log, full memory |

### Token Budgets (Approximate)

| Component | Max Tokens | Notes |
|-----------|------------|-------|
| Agent system prompt | ~500 | Static template |
| FEN + board context | ~100 | Position description |
| Memory excerpts | ~300 | 3-5 relevant items max |
| Creativity params | ~50 | One-liner each |
| Candidate moves | ~200 | For Devil's Advocate/Arbiter |
| **Total per agent call** | **~1,200** | Target ceiling |

### game.log: Write-Only During Play

The game.log is an **audit trail**, not an input to agents during play:

```
During game:  Agents ──write──► game.log  (append only, never read)
After game:   Learn Agent ──read──► game.log ──► memory.md
```

This prevents the log from bloating agent context as the game progresses.

### Long Game Handling (40+ moves)

| Data | Strategy |
|------|----------|
| Move history in game.json | Keep full history for record, but don't pass to agents |
| game.log | Grows on disk, not in context |
| Memory | Same retrieval limits regardless of game length |

**Result**: Move 5 and move 50 have roughly the same context size.

### Memory Retrieval Limits

When retrieving from memory.md for the Strategist:

| Category | Max Items Retrieved |
|----------|---------------------|
| Opening book (if in opening) | 1-2 relevant lines |
| Tactical warnings | 2-3 most relevant |
| Opponent notes | 1 profile summary |
| Recent lessons | 1-2 if position-relevant |
| **Total memory in prompt** | **≤5 items, ~300 tokens** |

Retrieval is **position-aware**: endgame positions don't load opening theory.

### Inter-Agent Communication Format

Agents pass **summaries**, not full reasoning:

```
STRATEGIST OUTPUT (passed to Devil's Advocate):
Candidates:
1. Nf3 - develops knight, controls center
2. d4 - central pawn push
3. Bc4 - targets f7

NOT THIS:
[500 words of deliberation about piece activity and mood parameters...]
```

```
DEVIL'S ADVOCATE OUTPUT (passed to Arbiter):
Refutations:
1. Nf3 - SOUND, no tactical issues
2. d4 - WARNING: allows Bb4+ pin after exd4
3. Bc4 - SOUND, but allows Nf6 with tempo

NOT THIS:
[300 words analyzing every possible reply...]
```

### Cost Estimation

Assuming ~1,200 tokens per agent call, 3 agents per move:

| Game Length | Agent Calls | Est. Tokens | Est. Cost (Sonnet) |
|-------------|-------------|-------------|-------------------|
| 20 moves (quick) | 60 | ~72K | ~$0.02 |
| 40 moves (normal) | 120 | ~144K | ~$0.04 |
| 60 moves (long) | 180 | ~216K | ~$0.06 |

This is per-game cost for Claude's reasoning, not counting adapter overhead.

---

## Learning System

The plugin learns and improves through a structured memory system. This is what makes it feel "alive" - it remembers past games, recognizes patterns, and adapts.

### What Gets Learned

| Category | Description | Example |
|----------|-------------|---------|
| **Tactical Patterns** | Recurring tactics that caught us off guard | "Bishop skewer on a2-g8 diagonal" |
| **Positional Ideas** | Strategic concepts that worked well | "Minority attack on queenside in QGD" |
| **Opening Repertoire** | Lines we've played and their outcomes | "Italian Game: 6.d3 led to comfortable middlegame" |
| **Opponent Tendencies** | Patterns from specific opponents | "User 'ChessMaster99' always castles queenside" |
| **Blunder Catalogue** | Mistakes to avoid | "Don't play Qh5 when bishop can pin from b4" |
| **Brilliant Moves** | Interesting ideas worth remembering | "Opponent's Rxf7! sacrifice was beautiful - study this" |

### When Learning Happens

```
Game Flow:

  /chess:play ──► Game in progress ──► Game ends
                        │                   │
                        ▼                   ▼
                   game.log            /chess:learn
                 (raw reasoning)            │
                                           ▼
                                   ┌───────────────┐
                                   │ Learn Agent   │
                                   │ analyzes log  │
                                   │ extracts gems │
                                   └───────┬───────┘
                                           │
                                           ▼
                                      memory.md
                                   (permanent storage)
```

### Memory Structure (memory.md)

```markdown
# Chess Memory

## Tactical Patterns I've Seen

### Pins
- **Long diagonal bishop pin**: Watch for Bb4+ pinning knight to king
  - First seen: 2024-01-15 vs Stockfish
  - Frequency: 3 games

### Forks
- **Knight fork on f7**: Common in Italian Game if king hasn't castled
  - Counter: Castle early or play ...h6 to prevent Ng5

### Skewers
- **Queen-Rook skewer on back rank**: Keep escape square for king

---

## Opening Book

### As White
| Opening | Record | Notes |
|---------|--------|-------|
| Italian Game (1.e4 e5 2.Nf3 Nc6 3.Bc4) | 3W-1L | Comfortable middlegames |
| London System (1.d4 d5 2.Bf4) | 1W-2L | Opponents seem prepared |

### As Black
| Against | Response | Record | Notes |
|---------|----------|--------|-------|
| 1.e4 | Sicilian (1...c5) | 2W-2L | Sharp but fun |
| 1.d4 | King's Indian | 1W-0L | Good counterattack chances |

---

## Opponent Profiles

### ChessMaster99
- **Style**: Aggressive, attacks early
- **Tendencies**:
  - Always plays Qh5 in Italian Game
  - Castles queenside 80% of the time
  - Prone to time trouble in endgames
- **Weaknesses**: Overextends pawns, weak back rank
- **Record**: 2W-3L

### StockfishLevel5
- **Style**: Solid, exploits mistakes
- **Tendencies**: Perfect tactics, positional squeeze
- **Weaknesses**: None (it's an engine)
- **Record**: 0W-5L (but I'm learning!)

---

## Lessons Learned (Mistakes to Remember)

### Critical Blunders
1. **2024-01-15**: Played Qxd4?? missing Bb4+ pin. Lost queen.
   - Lesson: Check ALL checks before capturing

2. **2024-01-14**: Pushed h3?? allowing Ng4-f2 fork
   - Lesson: Don't weaken kingside without reason

### Missed Opportunities
1. **2024-01-15**: Could have played Nxf7! sacrifice but didn't see it
   - Pattern: Undefended f7 + queen can reach h5 = investigate sac

---

## Brilliant Moves Archive

Interesting ideas worth studying (from opponents or self):

1. **Rxf7!! sacrifice** (vs ChessMaster99, 2024-01-15)
   - Position: [FEN string]
   - Idea: Deflects queen from defending back rank
   - Result: Led to mate in 5

2. **Quiet Bc1-a3!** (self, vs Stockfish, 2024-01-14)
   - Idea: Rerouting bishop to dominate dark squares
   - Result: Won the endgame due to bishop superiority
```

### How the Strategist Uses Memory

When the Strategist agent proposes moves, it receives relevant excerpts from memory:

```
# Current Position
FEN: r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4

# Relevant Memory (auto-retrieved)
- Opening: Italian Game - you've played this 4 times (3W-1L)
- Warning: In this position, watch for ...Bb4+ pin if you play d3
- Opponent "ChessMaster99" note: They usually play Qh5 here
- Tactical pattern: f7 is weak - Ng5 ideas may work

# Your task: Propose 3 candidate moves with reasoning
```

### The Learn Agent

A dedicated agent (`/chess:learn`) runs after each game to:

1. **Parse game.log**: Extract all reasoning and decisions
2. **Identify key moments**: Turning points, blunders, brilliancies
3. **Compare to outcome**: Did our plans work? Why/why not?
4. **Compress insights**: Distill verbose reasoning into actionable nuggets
5. **Update memory.md**: Add new patterns, update opponent profiles
6. **Prune old data**: Remove outdated or contradicted lessons

```
Learn Agent Workflow:

  Read game.log ──► Identify moments ──► Compress ──► Categorize
        │                                   │              │
        ▼                                   ▼              ▼
  "Turn 12 was              "Don't capture   ┌─────────────────────────────┐
   critical - we             when pinned"    │ Was it a tactical pattern?  │──► Add to Tactical Patterns
   played Qxd4                               │ Was it an opening issue?    │──► Update Opening Book
   missing Bb4+                              │ Was it opponent-specific?   │──► Update Opponent Profile
   pin because                               │ Was it a recurring mistake? │──► Add to Lessons Learned
   we were focused                           └─────────────────────────────┘
   on material..."
```

### The Compression Step (Critical!)

Raw game logs are verbose and full of redundant reasoning. The compression step ensures memory stays useful and concise:

**Compression Rules:**

| Input (Verbose) | Output (Compressed) |
|-----------------|---------------------|
| "I considered Qxd4 because it wins a pawn and centralizes the queen, but I didn't notice that after Bb4+ my knight on c3 would be pinned to the king..." | "Check for pins before capturing material" |
| "The opponent played Qh5 again like they did in our last 3 games, threatening mate on f7..." | "ChessMaster99: Always plays Qh5 early" |
| "I played the Italian Game with 1.e4 e5 2.Nf3 Nc6 3.Bc4 and got a good position..." | "Italian Game: +1W (comfortable middlegame)" |

**Compression Algorithm:**

```
For each identified key moment:

1. EXTRACT the core lesson (1 sentence max)
   - What went wrong/right?
   - Why?

2. GENERALIZE if possible
   - "Missed Bb4+ pin" → "Check all checks before capturing"
   - "Opponent played Qh5" → Pattern recognition, not move-by-move

3. DEDUPLICATE against existing memory
   - If similar lesson exists: increment frequency counter
   - If contradicts old lesson: evaluate which is more reliable

4. DISCARD if not actionable
   - "The position was complicated" → DISCARD (not useful)
   - "I felt nervous" → DISCARD (not chess knowledge)
   - "Knight on e5 was strong" → KEEP if generalizable
```

**Memory Size Limits:**

| Category | Max Entries | Pruning Strategy |
|----------|-------------|------------------|
| Tactical Patterns | 50 | Remove least frequent |
| Opening Book | 20 lines | Keep most played |
| Opponent Profiles | 10 | Remove oldest inactive |
| Lessons Learned | 30 | Remove if not triggered in 10 games |
| Brilliant Moves | 20 | Keep most instructive |

**Example Compression:**

```
BEFORE (game.log excerpt, 500 words):
[TURN 12] [strategist] Looking at the position, I see several candidate moves.
Qxd4 looks tempting because it wins a central pawn and activates my queen.
Nf3 is solid, developing another piece. I could also consider castling...
After deep thought, I'll go with Qxd4 because material advantage is important.

[TURN 12] [devils-advocate] Analyzing Qxd4... wait, after Qxd4 Black has Bb4+!
This pins the knight on c3 to the king. The queen on d4 cannot help...

[TURN 12] [arbiter] REJECTED: Qxd4 loses to Bb4+ pin. Selecting Nf3 instead.

AFTER (memory.md entry, 15 words):
- **Pin check before capture**: Always verify no discovered/pin checks after taking material
  - Learned: Game vs Stockfish, 2024-01-15
```

### Memory Retrieval Strategy

Not all memory is relevant to every position. The system uses smart retrieval:

| Position Phase | Memory Retrieved |
|----------------|------------------|
| Opening (moves 1-10) | Opening book, opponent's opening tendencies |
| Middlegame | Tactical patterns, opponent's style |
| Endgame | Endgame techniques, opponent's time management |
| Any phase | Recent lessons learned, similar positions |

---

## Design Decisions (Resolved)

1. **Agent loop depth**: Single pass for Devil's Advocate (simpler, faster, fits context budget)

2. **Adapter priority**: Stockfish first, then local terminal board. Lichess deferred (OAuth complexity).

3. **Creativity parameter selection**: Interactive via AskQuestion tool at game start - user chooses mood, focus, opening.

4. **Agent model**: Sonnet for all three agents (Strategist, Devil's Advocate, Arbiter)

5. **Stockfish**: Check if installed, guide user through installation if missing

6. **Default skill level**: Club (3 candidates, full critique)

7. **Agent system**: Standalone implementation (not using Task subagent system)

8. **Plugin location**: Current directory (claude-chess/)

---

## Usage Examples (Planned)

```bash
# Start a new game
/chess:play --skill club --adapter stockfish

# Check current game status
/chess:status

# Post-game analysis
/chess:analyze

# Learn from the game (update memory)
/chess:learn
```

---

## Technical Notes

- **FEN (Forsyth-Edwards Notation)**: Standard for representing board positions
- **UCI (Universal Chess Interface)**: Standard for move communication
- **Lichess API**: `lichess.org/api/board/game/stream/{gameId}` for real-time game state
- **python-chess**: Library for move validation and board manipulation
