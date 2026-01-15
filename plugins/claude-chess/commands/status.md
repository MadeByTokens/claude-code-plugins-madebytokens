---
description: Display the current chess game status, board position, and move history
---

# Chess Status Command

Display the current state of the chess game including the board position, move history, and game parameters.

## Available MCP Tools

- `chess_get_state()` - Get game state as JSON
- `chess_display(brief=False)` - Get board as text
- `chess_gui()` - Open graphical board window
- `chess_analyze()` - Brief position analysis

## Execution Steps

### Step 1: Check for Active Game

Call `chess_get_state()` to check if there's an active game.

If no game exists or `"active": false`:
```
No active game. Start a new game with /chess:play
```

### Step 2: Display Game Information

If a game is active, display:

#### Game Header
```
=== Chess Game Status ===
Opponent: [Stockfish/Human]
Our Color: [White/Black]
Skill Level: [Beginner/Casual/Club/Expert]
Turn: [N]
Status: [In Progress/Game Over]
```

#### Current Position

Display the board by calling `chess_display()` or `chess_gui()` for graphical view.

#### Move History

Format moves in pairs (White/Black):
```
Move History:
1. e2e4 e7e5
2. g1f3 b8c6
3. f1b5 ...
```

If the game has PGN, format it from the move_history in the game state.

#### Game Parameters

```
Game Style:
- Strategic Focus: [focus]
- Mood: [mood]
- Opening: [opening choice]
```

#### Current Situation

Analyze and report:
- Whose turn it is
- If in check
- Material count (if significantly imbalanced)
- Game phase (opening/middlegame/endgame)

Call `chess_analyze()` for a brief position assessment.

### Step 3: Suggestions

Based on the situation, suggest:

- If it's our turn: "Use /chess:play to continue and make your next move"
- If waiting for opponent: "Waiting for opponent's move. Use /chess:play to check for updates"
- If game is over: "Game ended. Use /chess:analyze for post-game analysis or /chess:learn to extract lessons"

## Output Format

```
=== Chess Game Status ===

Opponent: Stockfish (Club level)
Our Color: White
Turn: 5
Status: In Progress - Your Move

  +-----------------+
8 | r . b q k b n r |
7 | p p p p . p p p |
6 | . . n . . . . . |
5 | . . . . p . . . |
4 | . . B . P . . . |
3 | . . . . . N . . |
2 | P P P P . P P P |
1 | R N B Q K . . R |
  +-----------------+
    a b c d e f g h

Move History:
1. e2e4 e7e5
2. g1f3 b8c6
3. f1c4 g8f6
4. d2d3 f8e7

PGN: 1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. d3 Be7

Game Style:
- Strategic Focus: Piece Activity
- Mood: Ambitious
- Opening: Italian Game

Position Assessment:
- Phase: Opening
- Material: Equal
- White to move

→ Use /chess:play to continue
```

## No Active Game Output

```
=== Chess Game Status ===

No active game found.

To start a new game:
  /chess:play

This will guide you through:
- Choosing an opponent (Stockfish or Human)
- Selecting your color
- Setting skill level and play style
```

## Minimal Mode

If the user just wants a quick board view, they can say "just the board" and you should call `chess_gui()` to show the graphical board, or `chess_display()` for text output, without the full status header.
