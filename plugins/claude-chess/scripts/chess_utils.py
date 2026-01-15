#!/usr/bin/env python3
"""
Chess utilities for the Claude Chess plugin.

Provides command-line interface for chess operations:
- Board display (text for AI, graphical window for human)
- Move validation
- Legal moves generation
- Game state management
- Stockfish integration

Usage:
    python3 chess_utils.py --verify          # Check dependencies
    python3 chess_utils.py --display         # Show current board (text)
    python3 chess_utils.py --gui             # Open graphical board window
    python3 chess_utils.py --legal-moves     # List legal moves
    python3 chess_utils.py --move e2e4       # Make a move
    python3 chess_utils.py --validate e2e4   # Check if move is legal
    python3 chess_utils.py --opponent-move   # Get Stockfish's move
    python3 chess_utils.py --check-end       # Check if game is over
    python3 chess_utils.py --pgn             # Output game in PGN format
    python3 chess_utils.py --analyze-brief   # Brief position analysis
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Try to import chess library
try:
    import chess
    import chess.engine
    import chess.svg
    CHESS_AVAILABLE = True
except ImportError:
    CHESS_AVAILABLE = False

# Try to import graphics libraries for GUI display
try:
    import cairosvg
    CAIRO_AVAILABLE = True
except ImportError:
    CAIRO_AVAILABLE = False

import subprocess
import tempfile

# Paths relative to this script
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
STATE_DIR = PROJECT_DIR / "state"
GAME_JSON = STATE_DIR / "game.json"
GAME_LOG = STATE_DIR / "game.log"


# Unicode chess pieces
UNICODE_PIECES = {
    'K': '\u2654', 'Q': '\u2655', 'R': '\u2656', 'B': '\u2657', 'N': '\u2658', 'P': '\u2659',
    'k': '\u265A', 'q': '\u265B', 'r': '\u265C', 'b': '\u265D', 'n': '\u265E', 'p': '\u265F',
}


def check_dependencies() -> tuple[bool, str]:
    """Check if all required dependencies are installed."""
    messages = []

    # Check python-chess
    if not CHESS_AVAILABLE:
        messages.append("""
python-chess library is NOT installed.

Install it with:
    pip install chess
""")

    # Check Stockfish
    stockfish_paths = [
        "stockfish",
        "/usr/bin/stockfish",
        "/usr/local/bin/stockfish",
        "/opt/homebrew/bin/stockfish",
        "/usr/games/stockfish",
    ]

    stockfish_found = False
    stockfish_path = None
    for path in stockfish_paths:
        if shutil.which(path):
            stockfish_found = True
            stockfish_path = shutil.which(path)
            break

    if not stockfish_found:
        import platform
        system = platform.system().lower()

        install_cmd = "See https://stockfishchess.org/download/"
        if system == "linux":
            install_cmd = "sudo apt install stockfish  # Debian/Ubuntu"
        elif system == "darwin":
            install_cmd = "brew install stockfish"

        messages.append(f"""
Stockfish is NOT installed.

Install it with:
    {install_cmd}
""")

    if messages:
        return False, "\n".join(messages)

    return True, f"All dependencies OK.\n- python-chess: installed\n- Stockfish: {stockfish_path}"


def load_game_state() -> dict:
    """Load the current game state from game.json."""
    if not GAME_JSON.exists():
        return {
            "active": False,
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "move_history": [],
            "our_color": "white",
            "skill_level": "club",
            "opponent_type": "stockfish",
            "turn_number": 0,
        }

    with open(GAME_JSON, 'r') as f:
        return json.load(f)


def save_game_state(state: dict):
    """Save the game state to game.json."""
    state["last_updated"] = datetime.now().isoformat()
    with open(GAME_JSON, 'w') as f:
        json.dump(state, f, indent=2)


def log_message(turn: int, agent: str, message: str):
    """Append a message to the game log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(GAME_LOG, 'a') as f:
        f.write(f"[{timestamp}] [TURN {turn}] [{agent}] {message}\n")


def board_to_string(board: 'chess.Board', perspective: str = "white", last_move: str = None) -> str:
    """Convert board to a large, clear ASCII representation."""
    lines = []

    # Parse last move to highlight squares
    highlight_from = None
    highlight_to = None
    if last_move and len(last_move) >= 4:
        try:
            highlight_from = chess.parse_square(last_move[:2])
            highlight_to = chess.parse_square(last_move[2:4])
        except:
            pass

    # Large board with box drawing characters
    lines.append("")
    lines.append("     a   b   c   d   e   f   g   h")
    lines.append("   +---+---+---+---+---+---+---+---+")

    if perspective == "white":
        ranks = range(7, -1, -1)
        files = range(8)
    else:
        ranks = range(8)
        files = range(7, -1, -1)

    for rank in ranks:
        row = f" {rank + 1} |"
        for file in files:
            square = chess.square(file, rank)
            piece = board.piece_at(square)

            # Determine cell content
            if piece:
                symbol = UNICODE_PIECES.get(piece.symbol(), piece.symbol())
            else:
                # Empty square - use different chars for light/dark
                if (rank + file) % 2 == 0:
                    symbol = ' '
                else:
                    symbol = ' '

            # Highlight last move squares with markers
            if square == highlight_to:
                row += f">{symbol}<|"
            elif square == highlight_from:
                row += f"({symbol})|"
            else:
                row += f" {symbol} |"

        row += f" {rank + 1}"
        lines.append(row)
        lines.append("   +---+---+---+---+---+---+---+---+")

    if perspective == "white":
        lines.append("     a   b   c   d   e   f   g   h")
    else:
        lines.append("     h   g   f   e   d   c   b   a")

    lines.append("")
    return "\n".join(lines)


def display_board(brief=False):
    """Display the current board position.

    Args:
        brief: If True, output minimal text (just FEN and status) for AI context efficiency.
    """
    if not CHESS_AVAILABLE:
        print("Error: python-chess not installed")
        return

    state = load_game_state()
    board = chess.Board(state["fen"])

    # Get last move for highlighting
    move_history = state.get("move_history", [])
    last_move = move_history[-1] if move_history else None

    if brief:
        # Minimal output for AI - just the essential info
        turn = "W" if board.turn == chess.WHITE else "B"
        if board.is_checkmate():
            winner = "Black" if board.turn == chess.WHITE else "White"
            print(f"CHECKMATE - {winner} wins")
        elif board.is_stalemate():
            print("STALEMATE")
        elif board.is_check():
            print(f"{turn} to move (CHECK)")
        else:
            print(f"{turn} to move")
        return

    # Full board display
    print(board_to_string(board, state.get("our_color", "white"), last_move))

    # Compact status line
    turn = "White" if board.turn == chess.WHITE else "Black"
    status = f"{turn} to move"

    if board.is_check():
        status += " | CHECK!"

    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        status = f"CHECKMATE! {winner} wins."
    elif board.is_stalemate():
        status = "STALEMATE - Draw"
    elif board.is_insufficient_material():
        status = "DRAW - Insufficient material"

    print(status)


def display_board_gui():
    """Open a graphical window showing the current board position."""
    if not CHESS_AVAILABLE:
        print("Error: python-chess not installed")
        return

    state = load_game_state()
    board = chess.Board(state["fen"])

    # Get last move for highlighting
    move_history = state.get("move_history", [])
    last_move = None
    if move_history:
        try:
            last_move = chess.Move.from_uci(move_history[-1])
        except:
            pass

    # Determine orientation based on our color
    flipped = state.get("our_color", "white") == "black"

    # Generate SVG with highlighted last move
    svg_data = chess.svg.board(
        board,
        lastmove=last_move,
        flipped=flipped,
        size=600,
        colors={
            'square light': '#f0d9b5',
            'square dark': '#b58863',
            'square light lastmove': '#cdd16a',
            'square dark lastmove': '#aaa23b',
        }
    )

    # Save to temp file and open with image viewer
    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
        f.write(svg_data.encode('utf-8'))
        svg_path = f.name

    # Try different viewers
    viewers = ['xdg-open', 'open', 'display', 'eog', 'feh']
    for viewer in viewers:
        if shutil.which(viewer):
            try:
                subprocess.Popen([viewer, svg_path],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                print(f"Board opened in graphical viewer")
                return
            except:
                continue

    print(f"Board saved to: {svg_path}")
    print("Could not find a viewer. Install: eog, feh, or imagemagick")


def get_legal_moves():
    """Print all legal moves in UCI format."""
    if not CHESS_AVAILABLE:
        print("Error: python-chess not installed")
        return

    state = load_game_state()
    board = chess.Board(state["fen"])

    moves = [move.uci() for move in board.legal_moves]
    print(" ".join(sorted(moves)))


def make_move(uci_move: str):
    """Make a move and update game state."""
    if not CHESS_AVAILABLE:
        print("Error: python-chess not installed")
        return False

    state = load_game_state()
    board = chess.Board(state["fen"])

    try:
        move = chess.Move.from_uci(uci_move)
        if move not in board.legal_moves:
            print(f"Error: Illegal move {uci_move}")
            return False

        # Get SAN before pushing
        san = board.san(move)

        board.push(move)

        # Update state
        state["fen"] = board.fen()
        state["move_history"].append(uci_move)
        state["turn_number"] = len(state["move_history"]) // 2 + 1

        # Check for game end
        if board.is_game_over():
            if board.is_checkmate():
                winner = "black" if board.turn == chess.WHITE else "white"
                state["result"] = f"{winner}_wins"
            else:
                state["result"] = "draw"
            state["active"] = False

        save_game_state(state)
        print(f"Move played: {uci_move} ({san})")
        return True

    except ValueError as e:
        print(f"Error: Invalid move {uci_move} - {e}")
        return False


def validate_move(uci_move: str):
    """Check if a move is legal."""
    if not CHESS_AVAILABLE:
        print("Error: python-chess not installed")
        return

    state = load_game_state()
    board = chess.Board(state["fen"])

    try:
        move = chess.Move.from_uci(uci_move)
        if move in board.legal_moves:
            san = board.san(move)
            print(f"LEGAL: {uci_move} ({san})")
        else:
            print(f"ILLEGAL: {uci_move}")
    except ValueError:
        print(f"INVALID: {uci_move} (bad format)")


def get_opponent_move():
    """Get Stockfish's move."""
    if not CHESS_AVAILABLE:
        print("Error: python-chess not installed")
        return

    state = load_game_state()

    # Find Stockfish
    stockfish_path = None
    for path in ["stockfish", "/usr/bin/stockfish", "/usr/local/bin/stockfish",
                 "/opt/homebrew/bin/stockfish", "/usr/games/stockfish"]:
        if shutil.which(path):
            stockfish_path = shutil.which(path)
            break

    if not stockfish_path:
        print("Error: Stockfish not found")
        return

    board = chess.Board(state["fen"])

    # Set depth based on skill level
    skill_depths = {
        "beginner": 1,
        "casual": 3,
        "club": 8,
        "expert": 15,
    }
    depth = skill_depths.get(state.get("skill_level", "club"), 8)

    try:
        engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        limit = chess.engine.Limit(depth=depth, time=2.0)
        result = engine.play(board, limit)
        engine.quit()

        if result.move:
            uci_move = result.move.uci()
            san = board.san(result.move)

            # Apply the move
            board.push(result.move)

            # Update state
            state["fen"] = board.fen()
            state["move_history"].append(uci_move)
            state["turn_number"] = len(state["move_history"]) // 2 + 1

            # Check for game end
            if board.is_game_over():
                if board.is_checkmate():
                    winner = "black" if board.turn == chess.WHITE else "white"
                    state["result"] = f"{winner}_wins"
                else:
                    state["result"] = "draw"
                state["active"] = False

            save_game_state(state)
            print(f"Opponent played: {uci_move} ({san})")
        else:
            print("Error: Stockfish returned no move")

    except Exception as e:
        print(f"Error: Stockfish failed - {e}")


def check_game_end():
    """Check if the game has ended."""
    if not CHESS_AVAILABLE:
        print("Error: python-chess not installed")
        return

    state = load_game_state()
    board = chess.Board(state["fen"])

    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        print(f"GAME OVER: Checkmate! {winner} wins.")
    elif board.is_stalemate():
        print("GAME OVER: Stalemate - Draw")
    elif board.is_insufficient_material():
        print("GAME OVER: Draw - Insufficient material")
    elif board.can_claim_fifty_moves():
        print("GAME OVER: Draw claimable - Fifty move rule")
    elif board.can_claim_threefold_repetition():
        print("GAME OVER: Draw claimable - Threefold repetition")
    else:
        print("IN PROGRESS")


def output_pgn():
    """Output the game in PGN format."""
    if not CHESS_AVAILABLE:
        print("Error: python-chess not installed")
        return

    state = load_game_state()

    # Replay moves to get SAN
    board = chess.Board()
    san_moves = []
    for uci_move in state.get("move_history", []):
        try:
            move = chess.Move.from_uci(uci_move)
            san_moves.append(board.san(move))
            board.push(move)
        except ValueError:
            san_moves.append(uci_move)

    # Build PGN
    pgn_parts = []
    for i in range(0, len(san_moves), 2):
        move_num = i // 2 + 1
        white_move = san_moves[i]
        if i + 1 < len(san_moves):
            black_move = san_moves[i + 1]
            pgn_parts.append(f"{move_num}. {white_move} {black_move}")
        else:
            pgn_parts.append(f"{move_num}. {white_move}")

    # Add result if game is over
    result = state.get("result")
    if result:
        if "white" in result:
            pgn_parts.append("1-0")
        elif "black" in result:
            pgn_parts.append("0-1")
        else:
            pgn_parts.append("1/2-1/2")

    print(" ".join(pgn_parts))


def analyze_brief():
    """Provide a brief analysis of the current position."""
    if not CHESS_AVAILABLE:
        print("Error: python-chess not installed")
        return

    state = load_game_state()
    board = chess.Board(state["fen"])

    # Determine phase
    piece_count = len(board.piece_map())
    if piece_count >= 28:
        phase = "Opening"
    elif piece_count >= 14:
        phase = "Middlegame"
    else:
        phase = "Endgame"

    # Count material
    white_material = 0
    black_material = 0
    piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9}

    for piece in board.piece_map().values():
        value = piece_values.get(piece.symbol().upper(), 0)
        if piece.color == chess.WHITE:
            white_material += value
        else:
            black_material += value

    material_diff = white_material - black_material
    if material_diff > 2:
        material = "White ahead"
    elif material_diff < -2:
        material = "Black ahead"
    else:
        material = "Roughly equal"

    # Who to move
    to_move = "White" if board.turn == chess.WHITE else "Black"

    print(f"Phase: {phase}")
    print(f"Material: {material} (W:{white_material} B:{black_material})")
    print(f"{to_move} to move")

    if board.is_check():
        print("IN CHECK")


def main():
    parser = argparse.ArgumentParser(description="Chess utilities for Claude Chess plugin")
    parser.add_argument("--verify", action="store_true", help="Check dependencies")
    parser.add_argument("--display", action="store_true", help="Display current board (text)")
    parser.add_argument("--brief", action="store_true", help="Minimal text output (for AI context)")
    parser.add_argument("--gui", action="store_true", help="Open graphical board window")
    parser.add_argument("--legal-moves", action="store_true", help="List legal moves")
    parser.add_argument("--move", type=str, help="Make a move (UCI format)")
    parser.add_argument("--validate", type=str, help="Validate a move (UCI format)")
    parser.add_argument("--opponent-move", action="store_true", help="Get Stockfish's move")
    parser.add_argument("--check-end", action="store_true", help="Check if game is over")
    parser.add_argument("--pgn", action="store_true", help="Output game in PGN")
    parser.add_argument("--analyze-brief", action="store_true", help="Brief position analysis")

    args = parser.parse_args()

    if args.verify:
        ok, msg = check_dependencies()
        print(msg)
        sys.exit(0 if ok else 1)

    if args.display:
        display_board(brief=args.brief)
    elif args.gui:
        display_board_gui()
    elif args.legal_moves:
        get_legal_moves()
    elif args.move:
        make_move(args.move)
    elif args.validate:
        validate_move(args.validate)
    elif args.opponent_move:
        get_opponent_move()
    elif args.check_end:
        check_game_end()
    elif args.pgn:
        output_pgn()
    elif args.analyze_brief:
        analyze_brief()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
