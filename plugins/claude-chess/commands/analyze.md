---
description: Perform post-game analysis to identify key moments, mistakes, and improvements
---

# Chess Analyze Command

Perform detailed post-game analysis to identify critical moments, mistakes, missed opportunities, and lessons for improvement.

## Prerequisites

This command works best after a completed game, but can also analyze:
- An ongoing game (analysis of moves so far)
- A position from a FEN string
- A game from PGN notation

## Step 1: Load Game Data

Read the game state and log:
```
Read: state/game.json
Read: state/game.log
```

If analyzing a specific position or PGN provided by user, parse that instead.

## Step 2: Identify Key Moments

Review the game and identify:

### Critical Positions
Positions where the evaluation changed significantly:
- Turning points (advantage shifted)
- Missed wins (we had a winning move but didn't play it)
- Blunders (moves that threw away advantage)
- Brilliant moves (unexpected strong moves)

### Tactical Moments
- Forks, pins, skewers that occurred or were missed
- Sacrifices (sound or unsound)
- Checkmate threats

### Strategic Themes
- Pawn structure evolution
- Piece activity changes
- King safety considerations
- Control of key squares/files

## Step 3: Move-by-Move Review

For each move in the game, provide:

```
Move [N]: [UCI] ([SAN])
Our Assessment: [What we thought]
Actual Quality: [Excellent/Good/OK/Inaccuracy/Mistake/Blunder]
Better Alternative: [if applicable]
Comment: [Brief explanation]
```

Focus on:
- Moves where we went wrong
- Moves where we missed something better
- Moves that were particularly good

Don't analyze every move in detail - focus on the interesting ones.

## Step 4: Phase Analysis

### Opening
- Did we follow opening principles?
- How did our opening choice work out?
- Where did we deviate from theory (if applicable)?
- What was the resulting position?

### Middlegame
- What was our plan?
- Did we execute it well?
- Key tactical moments
- Piece coordination

### Endgame (if reached)
- Technique evaluation
- Missed wins or draws
- Time management (if timed game)

## Step 5: Summary Report

Generate a summary:

```
=== Post-Game Analysis ===

Result: [Win/Loss/Draw] - [Method: Checkmate/Resignation/Stalemate/etc.]

Overall Assessment:
[2-3 sentences on how the game went]

Key Moments:
1. Move [N]: [Description of critical moment]
2. Move [N]: [Description of critical moment]
3. Move [N]: [Description of critical moment]

What Went Well:
- [Positive point]
- [Positive point]

What To Improve:
- [Area for improvement]
- [Area for improvement]

Lessons Learned:
1. [Specific, actionable lesson]
2. [Specific, actionable lesson]

Accuracy Score: [Rough estimate based on move quality]

Recommendation:
[Specific suggestion for next game]
```

## Step 6: Compare to Engine (Optional)

If Stockfish is available, use the `chess_analyze()` MCP tool to get position evaluation. This adds objective evaluation but is not required.

## Output Formatting

### For Terminal
Use clear sections with headers. Keep analysis concise but insightful.

### Move Quality Indicators
- !! = Brilliant
- ! = Good move
- !? = Interesting
- ?! = Dubious
- ? = Mistake
- ?? = Blunder

### Example Output

```
=== Post-Game Analysis ===

Result: Loss - Checkmate (Move 34)

Overall Assessment:
Strong opening play but collapsed in the middlegame after missing a
tactical shot on move 18. The endgame was never reached as opponent
converted their advantage efficiently.

Key Moments:

Move 12: d2d4 (d4)
Our plan to challenge the center was correct, but timing was off.
Better was 12. Be3 first to complete development.
Assessment: Inaccuracy (?!)

Move 18: h2h3? (h3)
We played a prophylactic move but missed 18. Nxe5! winning a pawn
due to the pin on the f-file. This was the turning point.
Assessment: Mistake (?)

Move 25: Qd1??
Allowed the devastating Rxf2! sacrifice. Should have played Rf1
to defend. This lost the game.
Assessment: Blunder (??)

What Went Well:
- Opening preparation was solid (Italian Game)
- Piece development was logical

What To Improve:
- Check ALL forcing moves before playing (missed Nxe5!)
- Be more alert to sacrifices on f2/f7
- When defending, calculate opponent's threats more carefully

Lessons Learned:
1. Before prophylactic moves (h3, a3), first check if there's
   a tactical opportunity available
2. When opponent has heavy pieces on a file, watch for sacrifices

Accuracy Score: ~65% (estimated)

Recommendation:
Practice tactical puzzles focusing on discovered attacks and
piece coordination. The opening was fine; tactics need work.
```

## Integration with Learn Command

After analysis, suggest running `/chess:learn` to extract and store the lessons in memory.md for future games.

## Analyzing External Games

If user provides a PGN or FEN:
- Parse the input
- Apply the same analysis framework
- Note that game.log won't be available for those games
