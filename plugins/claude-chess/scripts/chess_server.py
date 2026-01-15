#!/usr/bin/env python3
"""
Chess MCP Server for the Claude Chess plugin.

Exposes chess operations as MCP tools that Claude can call.
"""

import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from constants import STOCKFISH_PATHS, SkillLevel

# Try to import chess library
try:
    import chess
    import chess.engine
    import chess.svg
    CHESS_AVAILABLE = True
except ImportError:
    CHESS_AVAILABLE = False

# State paths - relative to current working directory (user's project)
STATE_DIR = Path("state")
GAME_JSON = STATE_DIR / "game.json"
GAME_LOG = STATE_DIR / "game.log"
MEMORY_FILE = STATE_DIR / "memory.md"

# Unicode chess pieces
UNICODE_PIECES = {
    'K': '\u2654', 'Q': '\u2655', 'R': '\u2656', 'B': '\u2657', 'N': '\u2658', 'P': '\u2659',
    'k': '\u265A', 'q': '\u265B', 'r': '\u265C', 'b': '\u265D', 'n': '\u265E', 'p': '\u265F',
}

# Create MCP server
mcp = FastMCP("chess")

# Track the GUI viewer process to close it before opening new one
_viewer_process = None


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


def uci_history_to_san(uci_moves: list) -> str:
    """Convert UCI move history to SAN format with turn tags: '[Turn 1] e4 e5 [Turn 2] Nf3 Nc6'"""
    if not CHESS_AVAILABLE or not uci_moves:
        return ""

    board = chess.Board()
    san_parts = []
    turn_num = 1

    for i, uci in enumerate(uci_moves):
        try:
            move = chess.Move.from_uci(uci)
            san = board.san(move)

            if i % 2 == 0:  # White's move - start new turn
                san_parts.append(f"[Turn {turn_num}] {san}")
            else:  # Black's move - same turn
                san_parts.append(san)
                turn_num += 1

            board.push(move)
        except (ValueError, chess.InvalidMoveError):
            san_parts.append(uci)  # Fallback to UCI if invalid

    return " ".join(san_parts)


# Piece values for material calculation (shared across functions)
PIECE_VALUES = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 0}
# Piece names - uppercase keys for display, lowercase available via .lower()
PIECE_NAMES = {"P": "pawn", "N": "knight", "B": "bishop", "R": "rook", "Q": "queen", "K": "king"}
PIECE_NAMES_LOWER = {k.lower(): v for k, v in PIECE_NAMES.items()}


def _truncate_tactical_lists(info: dict, max_items: int = 5) -> dict:
    """Truncate tactical info lists to avoid clutter."""
    for key in info:
        if len(info[key]) > max_items:
            info[key] = info[key][:max_items] + [f"...and {len(info[key]) - max_items} more"]
    return info


def _find_hanging_pieces(board: 'chess.Board', our_color: chess.Color, opp_color: chess.Color) -> dict:
    """Find hanging pieces and threats for both sides."""
    result = {
        "our_hanging_pieces": [],
        "their_hanging_pieces": [],
        "threats_to_us": [],
        "our_threats": [],
    }

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        square_name = chess.square_name(square)
        piece_symbol = piece.symbol().upper()
        piece_full = PIECE_NAMES[piece_symbol]

        is_attacked_by_us = board.is_attacked_by(our_color, square)
        is_attacked_by_them = board.is_attacked_by(opp_color, square)

        if piece.color == our_color:
            # Our piece - check if it's hanging (attacked and not defended)
            if is_attacked_by_them:
                defenders = sum(
                    1 for sq in chess.SQUARES
                    if board.piece_at(sq)
                    and board.piece_at(sq).color == our_color
                    and sq != square
                    and board.is_attacked_by(our_color, square)
                )
                # High value pieces (Q, R) are always flagged as threatened
                if defenders == 0 or piece_symbol in ['Q', 'R']:
                    result["threats_to_us"].append(f"{piece_full} on {square_name} is attacked")
                    if defenders == 0:
                        result["our_hanging_pieces"].append(f"{piece_full} on {square_name}")
        else:
            # Their piece - check if it's hanging
            if is_attacked_by_us:
                result["our_threats"].append(f"can capture {piece_full} on {square_name}")
                defenders = board.attackers(opp_color, square)
                if len(defenders) == 0:
                    result["their_hanging_pieces"].append(f"{piece_full} on {square_name}")

    return result


def _find_checks_and_captures(board: 'chess.Board') -> dict:
    """Find available checks and captures from legal moves."""
    result = {
        "checks_available": [],
        "captures_available": [],
    }

    for move in board.legal_moves:
        san = board.san(move)

        if board.gives_check(move):
            result["checks_available"].append(san)

        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            moving_piece = board.piece_at(move.from_square)
            if captured_piece and moving_piece:
                captured_val = PIECE_VALUES.get(captured_piece.symbol().lower(), 0)
                moving_val = PIECE_VALUES.get(moving_piece.symbol().lower(), 0)
                diff = captured_val - moving_val

                if diff >= 2:
                    label = "WINNING"
                elif diff >= -1:
                    label = "EQUAL"
                else:
                    label = "SACRIFICE"

                result["captures_available"].append(f"{san} ({label})")

    return result


def compute_tactical_info(board: 'chess.Board', our_color: str) -> dict:
    """Compute tactical features: hanging pieces, threats, checks, captures."""
    if not CHESS_AVAILABLE:
        return {}

    we_are_white = (our_color == "white")
    our_pieces_color = chess.WHITE if we_are_white else chess.BLACK
    opp_pieces_color = chess.BLACK if we_are_white else chess.WHITE

    # Find hanging pieces and threats
    info = _find_hanging_pieces(board, our_pieces_color, opp_pieces_color)

    # Find available checks and captures
    checks_captures = _find_checks_and_captures(board)
    info.update(checks_captures)

    # Truncate lists to avoid clutter
    return _truncate_tactical_lists(info)


def compute_material_info(board: 'chess.Board', move_history: list, our_color: str) -> dict:
    """Compute material balance and track captured pieces."""
    # Count material on board
    white_material = 0
    black_material = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.symbol().lower() != 'k':
            val = PIECE_VALUES.get(piece.symbol().lower(), 0)
            if piece.color == chess.WHITE:
                white_material += val
            else:
                black_material += val

    # Calculate balance from our perspective
    if our_color == "white":
        diff = white_material - black_material
    else:
        diff = black_material - white_material

    if diff > 0:
        balance = f"+{diff}"
    elif diff < 0:
        balance = str(diff)
    else:
        balance = "0"

    # Track captured pieces by replaying move history
    captured_by_us = []
    captured_by_them = []
    replay_board = chess.Board()

    we_are_white = (our_color == "white")

    for i, uci in enumerate(move_history):
        try:
            move = chess.Move.from_uci(uci)
            is_our_move = (i % 2 == 0) == we_are_white

            if replay_board.is_capture(move):
                captured = replay_board.piece_at(move.to_square)
                if captured:
                    name = PIECE_NAMES_LOWER.get(captured.symbol().lower(), "piece")
                    if is_our_move:
                        captured_by_us.append(name)
                    else:
                        captured_by_them.append(name)

            replay_board.push(move)
        except (ValueError, chess.InvalidMoveError):
            pass  # Skip invalid moves in history

    return {
        "balance": balance,
        "captured": {
            "by_us": captured_by_us,
            "by_them": captured_by_them
        }
    }


def compute_promotion_threats(board: 'chess.Board', our_color: str) -> dict:
    """Find pawns close to promotion (on 7th/2nd rank)."""
    threats = {"ours": [], "theirs": []}
    we_are_white = (our_color == "white")

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.symbol().lower() == 'p':
            rank = chess.square_rank(square)
            file_name = chess.square_name(square)[0]

            is_our_pawn = (piece.color == chess.WHITE) == we_are_white

            # White pawns promote on rank 7 (index 7), dangerous on rank 6
            # Black pawns promote on rank 0 (index 0), dangerous on rank 1
            if piece.color == chess.WHITE:
                if rank == 6:  # 7th rank - one move from promotion
                    msg = f"pawn on {chess.square_name(square)} can promote"
                    if is_our_pawn:
                        threats["ours"].append(msg)
                    else:
                        threats["theirs"].append(msg)
            else:
                if rank == 1:  # 2nd rank - one move from promotion
                    msg = f"pawn on {chess.square_name(square)} can promote"
                    if is_our_pawn:
                        threats["ours"].append(msg)
                    else:
                        threats["theirs"].append(msg)

    return threats


def save_game_state(state: dict):
    """Save the game state to game.json, including computed fields."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()

    if CHESS_AVAILABLE:
        board = chess.Board(state["fen"])
        our_color = state.get("our_color", "white")
        move_history = state.get("move_history", [])

        # Legal moves in both UCI and SAN format
        state["legal_moves"] = [move.uci() for move in board.legal_moves]
        state["legal_moves_san"] = [board.san(move) for move in board.legal_moves]

        # Visual board from player's perspective
        state["board_visual"] = board_to_string(board, perspective=our_color)

        # Move history in SAN format (like chess books: "1. e4 e5 2. Nf3 Nc6")
        state["move_history_san"] = uci_history_to_san(move_history)

        # Detect hanging pieces and tactical features
        state["tactical_info"] = compute_tactical_info(board, our_color)

        # Material balance and captured pieces
        material_info = compute_material_info(board, move_history, our_color)
        state["material_balance"] = material_info["balance"]
        state["captured"] = material_info["captured"]

        # Promotion threats (pawns on 7th/2nd rank)
        state["promotion_threats"] = compute_promotion_threats(board, our_color)

        # Last opponent move in SAN
        if move_history:
            if our_color == "white" and len(move_history) >= 1:
                if len(move_history) % 2 == 0:
                    state["last_opponent_move"] = move_history[-1]
                else:
                    state["last_opponent_move"] = move_history[-2] if len(move_history) >= 2 else None
            elif our_color == "black" and len(move_history) >= 1:
                if len(move_history) % 2 == 1:
                    state["last_opponent_move"] = move_history[-1]
                else:
                    state["last_opponent_move"] = move_history[-2] if len(move_history) >= 2 else None
            else:
                state["last_opponent_move"] = None
        else:
            state["last_opponent_move"] = None
    else:
        state["last_opponent_move"] = None

    with open(GAME_JSON, 'w') as f:
        json.dump(state, f, indent=2)


def board_to_string(board: 'chess.Board', perspective: str = "white", last_move: str = None) -> str:
    """Convert board to ASCII representation."""
    lines = []

    highlight_from = None
    highlight_to = None
    if last_move and len(last_move) >= 4:
        try:
            highlight_from = chess.parse_square(last_move[:2])
            highlight_to = chess.parse_square(last_move[2:4])
        except ValueError:
            pass  # Invalid square notation, skip highlighting

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
            symbol = UNICODE_PIECES.get(piece.symbol(), piece.symbol()) if piece else ' '

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

    return "\n".join(lines)


@mcp.tool()
def chess_verify() -> str:
    """Check if all chess dependencies are installed."""
    messages = []

    if not CHESS_AVAILABLE:
        messages.append("python-chess: NOT installed (pip install chess)")
    else:
        messages.append("python-chess: OK")

    stockfish_path = None
    for path in STOCKFISH_PATHS:
        if shutil.which(path):
            stockfish_path = shutil.which(path)
            break

    if stockfish_path:
        messages.append(f"Stockfish: OK ({stockfish_path})")
    else:
        messages.append("Stockfish: NOT installed")

    return "\n".join(messages)


@mcp.tool()
def chess_display(brief: bool = False) -> str:
    """Display the current chess board position.

    Args:
        brief: If True, return minimal status only. If False, return full board.
    """
    if not CHESS_AVAILABLE:
        return "Error: python-chess not installed"

    state = load_game_state()
    board = chess.Board(state["fen"])
    move_history = state.get("move_history", [])
    last_move = move_history[-1] if move_history else None

    if brief:
        turn = "W" if board.turn == chess.WHITE else "B"
        if board.is_checkmate():
            winner = "Black" if board.turn == chess.WHITE else "White"
            return f"CHECKMATE - {winner} wins"
        elif board.is_stalemate():
            return "STALEMATE"
        elif board.is_check():
            return f"{turn} to move (CHECK)"
        else:
            return f"{turn} to move"

    board_str = board_to_string(board, state.get("our_color", "white"), last_move)

    turn = "White" if board.turn == chess.WHITE else "Black"
    status = f"{turn} to move"
    if board.is_check():
        status += " | CHECK!"
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        status = f"CHECKMATE! {winner} wins."
    elif board.is_stalemate():
        status = "STALEMATE - Draw"

    return f"{board_str}\n{status}"


@mcp.tool()
def chess_gui() -> str:
    """Open a graphical window showing the chess board."""
    if not CHESS_AVAILABLE:
        return "Error: python-chess not installed"

    state = load_game_state()
    board = chess.Board(state["fen"])

    move_history = state.get("move_history", [])
    last_move = None
    if move_history:
        try:
            last_move = chess.Move.from_uci(move_history[-1])
        except (ValueError, chess.InvalidMoveError):
            pass  # Invalid move in history, skip highlighting

    flipped = state.get("our_color", "white") == "black"

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

    global _viewer_process

    # Use fixed path so we overwrite previous board
    svg_path = STATE_DIR / "board.svg"
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(svg_path, 'w') as f:
        f.write(svg_data)

    # Close previous viewer if still running
    if _viewer_process is not None:
        try:
            _viewer_process.terminate()
            _viewer_process.wait(timeout=1)
        except (OSError, subprocess.TimeoutExpired):
            pass  # Process already dead or won't terminate, ignore
        _viewer_process = None

    # Open viewer - prefer ones that can auto-refresh or handle file updates well
    for viewer in ['feh', 'eog', 'display', 'xdg-open', 'open']:
        if shutil.which(viewer):
            try:
                _viewer_process = subprocess.Popen(
                    [viewer, str(svg_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return "Board opened in graphical viewer"
            except (OSError, subprocess.SubprocessError):
                continue  # Viewer failed to start, try next one

    return f"Board saved to: {svg_path}"


@mcp.tool()
def chess_legal_moves() -> str:
    """Get all legal moves in the current position (UCI format)."""
    if not CHESS_AVAILABLE:
        return "Error: python-chess not installed"

    state = load_game_state()
    board = chess.Board(state["fen"])
    moves = [move.uci() for move in board.legal_moves]
    return " ".join(sorted(moves))


@mcp.tool()
def chess_move(uci: str) -> str:
    """Make a chess move.

    Args:
        uci: Move in UCI format (e.g., e2e4, g1f3, e7e8q for promotion)
    """
    if not CHESS_AVAILABLE:
        return "Error: python-chess not installed"

    state = load_game_state()
    board = chess.Board(state["fen"])

    try:
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            return f"ILLEGAL: {uci}"

        san = board.san(move)
        board.push(move)

        state["fen"] = board.fen()
        state["move_history"].append(uci)
        state["turn_number"] = len(state["move_history"]) // 2 + 1

        if board.is_game_over():
            if board.is_checkmate():
                winner = "black" if board.turn == chess.WHITE else "white"
                state["result"] = f"{winner}_wins"
            else:
                state["result"] = "draw"
            state["active"] = False

        save_game_state(state)
        return f"OK: {uci} ({san})"

    except ValueError as e:
        return f"INVALID: {uci} - {e}"


@mcp.tool()
def chess_log_turn(turn: int, candidates: str, refutations: str, decision: str, move: str) -> str:
    """Log a turn's deliberation to game.log for later analysis.

    Args:
        turn: Turn number
        candidates: Strategist's candidates (JSON string or summary)
        refutations: Devil's Advocate refutations (JSON string or summary), or "skipped" at beginner
        decision: Arbiter's decision (JSON string or summary)
        move: The final move played (UCI)
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
[{timestamp}] === TURN {turn} ===
[strategist] Candidates: {candidates}
[devils-advocate] Refutations: {refutations}
[arbiter] Decision: {decision}
[move] {move}
"""

    with open(GAME_LOG, "a") as f:
        f.write(log_entry)

    return f"Logged turn {turn}"


@mcp.tool()
def chess_remember(note: str, category: str = "patterns") -> str:
    """Add a note to game memory for future turns to reference.

    Call this when you notice something worth remembering:
    - Opponent patterns or tendencies
    - Tactical themes in the position
    - Opening recognition
    - Mistakes to avoid

    Args:
        note: What you noticed (e.g., "Opponent loves knight forks on f7")
        category: One of "opponent_patterns", "position_themes", "opening", "lessons"
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    # Get current turn number from game state
    state = load_game_state()
    turn = state.get("turn_number", "?")

    # Validate category
    valid_categories = ["opponent_patterns", "position_themes", "opening", "lessons"]
    if category not in valid_categories:
        category = "patterns"

    # Create memory file if it doesn't exist
    if not MEMORY_FILE.exists():
        with open(MEMORY_FILE, "w") as f:
            f.write("# Game Memory\n\n")
            f.write("## Opponent Patterns\n\n")
            f.write("## Position Themes\n\n")
            f.write("## Opening\n\n")
            f.write("## Lessons\n\n")

    # Read existing content
    with open(MEMORY_FILE, "r") as f:
        content = f.read()

    # Map category to section header
    section_map = {
        "opponent_patterns": "## Opponent Patterns",
        "position_themes": "## Position Themes",
        "opening": "## Opening",
        "lessons": "## Lessons"
    }
    section = section_map.get(category, "## Opponent Patterns")

    # Insert note after the section header
    entry = f"- [Turn {turn}] {note}\n"
    if section in content:
        # Find the section and add after it
        parts = content.split(section)
        if len(parts) == 2:
            # Insert after the section header (and any existing newlines)
            after_header = parts[1]
            # Find where to insert (after the first newline(s))
            insert_pos = 0
            while insert_pos < len(after_header) and after_header[insert_pos] == '\n':
                insert_pos += 1
            new_after = after_header[:insert_pos] + entry + after_header[insert_pos:]
            content = parts[0] + section + new_after

    # Write back
    with open(MEMORY_FILE, "w") as f:
        f.write(content)

    return f"Remembered: {note}"


@mcp.tool()
def chess_calculate(code: str) -> str:
    """Run a small Python calculation to help analyze the position.

    Use this as a "clutch" when you need to verify something specific:
    - Count attackers on a square
    - Check pawn structure
    - Calculate king safety
    - Verify piece mobility

    The code runs in a sandbox with:
    - `board`: 8x8 list of pieces ('P'=white pawn, 'p'=black pawn, '.'=empty)
    - `our_color`: 'white' or 'black'
    - `math` module available
    - 30 line limit, 500ms timeout

    Example:
        # Count white pieces attacking e5 (file=4, rank=4 in 0-indexed)
        count = 0
        for r in range(8):
            for f in range(8):
                if board[r][f].isupper():  # white piece
                    # ... check if it attacks e5
                    pass
        result = count

    Set `result` variable to return your answer.

    Args:
        code: Python code (max 30 lines, must set `result` variable)
    """
    import signal
    import math as math_module

    # Check line limit
    lines = [l for l in code.strip().split('\n') if l.strip() and not l.strip().startswith('#')]
    if len(lines) > 30:
        return f"Error: Code too long ({len(lines)} lines, max 30)"

    # Forbidden patterns
    forbidden = [
        'import ', 'from ', '__', 'exec', 'eval', 'compile',
        'open(', 'file(', 'input(', 'subprocess', 'os.', 'sys.',
        'globals', 'locals', 'vars(', 'dir(', 'getattr', 'setattr',
        'delattr', 'hasattr', 'type(', 'isinstance', 'issubclass',
        'breakpoint', 'help(', 'exit', 'quit'
    ]
    code_lower = code.lower()
    for pattern in forbidden:
        if pattern.lower() in code_lower:
            return f"Error: Forbidden pattern '{pattern}' in code"

    # Load current position
    state = load_game_state()
    if not state.get("fen"):
        return "Error: No active game"

    # Convert FEN to simple 8x8 board
    fen_board = state["fen"].split()[0]
    board = []
    for rank in fen_board.split('/'):
        row = []
        for c in rank:
            if c.isdigit():
                row.extend(['.'] * int(c))
            else:
                row.append(c)
        board.append(row)

    our_color = state.get("our_color", "white")

    # Restricted builtins
    safe_builtins = {
        'abs': abs, 'min': min, 'max': max, 'sum': sum,
        'len': len, 'range': range, 'enumerate': enumerate,
        'zip': zip, 'map': map, 'filter': filter,
        'sorted': sorted, 'reversed': reversed,
        'all': all, 'any': any, 'round': round,
        'int': int, 'float': float, 'str': str, 'bool': bool,
        'list': list, 'dict': dict, 'set': set, 'tuple': tuple,
        'True': True, 'False': False, 'None': None,
    }

    # Execution environment
    env = {
        '__builtins__': safe_builtins,
        'board': board,
        'our_color': our_color,
        'their_color': 'black' if our_color == 'white' else 'white',
        'math': math_module,
        'result': None,
    }

    # Timeout handler
    def timeout_handler(signum, frame):
        raise TimeoutError("Calculation took too long")

    try:
        # Set timeout (500ms)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, 0.5)

        exec(code, env)

        # Cancel timeout
        signal.setitimer(signal.ITIMER_REAL, 0)

        result = env.get('result')
        if result is None:
            return "Error: Code must set 'result' variable"

        # Limit output size
        result_str = str(result)
        if len(result_str) > 500:
            result_str = result_str[:500] + "... (truncated)"

        return f"Result: {result_str}"

    except TimeoutError:
        signal.setitimer(signal.ITIMER_REAL, 0)
        return "Error: Timeout (500ms limit)"
    except Exception as e:
        signal.setitimer(signal.ITIMER_REAL, 0)
        return f"Error: {type(e).__name__}: {e}"


@mcp.tool()
def chess_validate(uci: str) -> str:
    """Check if a move is legal without making it.

    Args:
        uci: Move in UCI format
    """
    if not CHESS_AVAILABLE:
        return "Error: python-chess not installed"

    state = load_game_state()
    board = chess.Board(state["fen"])

    try:
        move = chess.Move.from_uci(uci)
        if move in board.legal_moves:
            return f"LEGAL: {uci} ({board.san(move)})"
        else:
            return f"ILLEGAL: {uci}"
    except ValueError:
        return f"INVALID: {uci} (bad format)"


@mcp.tool()
def chess_opponent_move() -> str:
    """Get and play Stockfish's move."""
    if not CHESS_AVAILABLE:
        return "Error: python-chess not installed"

    state = load_game_state()

    stockfish_path = None
    for path in STOCKFISH_PATHS:
        if shutil.which(path):
            stockfish_path = shutil.which(path)
            break

    if not stockfish_path:
        return "Error: Stockfish not found"

    board = chess.Board(state["fen"])

    # Use Stockfish's built-in Skill Level (0-20)
    skill_level = state.get("stockfish_level", 10)

    try:
        engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        # Set Stockfish skill level (0=weak, 20=full strength)
        engine.configure({"Skill Level": skill_level})
        # Depth scales with skill: weak players don't calculate as deep
        depth = max(1, skill_level // 2 + 3)
        limit = chess.engine.Limit(depth=depth, time=2.0)
        result = engine.play(board, limit)
        engine.quit()

        if result.move:
            uci_move = result.move.uci()
            san = board.san(result.move)
            board.push(result.move)

            state["fen"] = board.fen()
            state["move_history"].append(uci_move)
            state["turn_number"] = len(state["move_history"]) // 2 + 1

            if board.is_game_over():
                if board.is_checkmate():
                    winner = "black" if board.turn == chess.WHITE else "white"
                    state["result"] = f"{winner}_wins"
                else:
                    state["result"] = "draw"
                state["active"] = False

            save_game_state(state)
            return f"Opponent: {uci_move} ({san})"
        else:
            return "Error: Stockfish returned no move"

    except Exception as e:
        return f"Error: Stockfish failed - {e}"


@mcp.tool()
def chess_check_end() -> str:
    """Check if the game has ended."""
    if not CHESS_AVAILABLE:
        return "Error: python-chess not installed"

    state = load_game_state()
    board = chess.Board(state["fen"])

    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        return f"CHECKMATE: {winner} wins"
    elif board.is_stalemate():
        return "STALEMATE: Draw"
    elif board.is_insufficient_material():
        return "DRAW: Insufficient material"
    elif board.can_claim_fifty_moves():
        return "DRAW: Fifty move rule"
    elif board.can_claim_threefold_repetition():
        return "DRAW: Threefold repetition"
    else:
        return "IN_PROGRESS"


@mcp.tool()
def chess_init_game(our_color: str, skill_level: str, opponent_type: str,
                    personality: str, strategic_focus: str, mood: str,
                    stockfish_level: int = 10) -> str:
    """Initialize a new chess game.

    Args:
        our_color: "white" or "black"
        skill_level: "beginner", "casual", "club", or "expert"
        opponent_type: "stockfish" or "human"
        personality: Player personality for commentary
        strategic_focus: Strategic focus for this game
        mood: Playing mood for this game
        stockfish_level: Stockfish skill level 0-20 (only used if opponent is stockfish)
    """
    # Input sanitization
    our_color = our_color.lower().strip() if our_color else "white"
    if our_color not in ("white", "black"):
        our_color = "white"

    skill_level = SkillLevel.from_string(skill_level).value

    opponent_type = opponent_type.lower().strip() if opponent_type else "human"
    if opponent_type not in ("stockfish", "human"):
        opponent_type = "human"

    # Sanitize stockfish_level - handle strings, floats, out-of-range
    try:
        stockfish_level = int(stockfish_level)
    except (ValueError, TypeError):
        stockfish_level = 10
    stockfish_level = max(0, min(20, stockfish_level))

    # Sanitize strings (prevent injection, limit length)
    personality = str(personality or "silent")[:50]
    strategic_focus = str(strategic_focus or "piece_activity")[:50]
    mood = str(mood or "practical")[:50]

    STATE_DIR.mkdir(parents=True, exist_ok=True)

    # Create fresh memory.md for new game
    with open(MEMORY_FILE, "w") as f:
        f.write("# Game Memory\n\n")
        f.write("## Opening\n\n")
        f.write("## Opponent Patterns\n\n")
        f.write("## Position Themes\n\n")
        f.write("## Lessons\n\n")

    # Clear game log for new game
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(GAME_LOG, "w") as f:
        f.write(f"[{timestamp}] === NEW GAME ===\n")
        f.write(f"Color: {our_color} | Skill: {skill_level} | Opponent: {opponent_type}\n")
        f.write(f"Focus: {strategic_focus} | Mood: {mood} | Personality: {personality}\n")
        if opponent_type == "stockfish":
            f.write(f"Stockfish Level: {stockfish_level}\n")
        f.write("\n")

    state = {
        "active": True,
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "move_history": [],
        "our_color": our_color,
        "skill_level": skill_level,
        "opponent_type": opponent_type,
        "stockfish_level": stockfish_level,
        "turn_number": 1,
        "personality": personality,
        "creativity": {
            "strategic_focus": strategic_focus,
            "mood": mood
        },
        "result": "in_progress"
    }

    save_game_state(state)
    sf_info = f" (Stockfish level {stockfish_level})" if opponent_type == "stockfish" else ""
    return f"Game initialized. Playing as {our_color} against {opponent_type}{sf_info}."


@mcp.tool()
def chess_get_state() -> str:
    """Get the current game state as JSON."""
    state = load_game_state()
    return json.dumps(state, indent=2)


@mcp.tool()
def chess_analyze() -> str:
    """Brief analysis of the current position."""
    if not CHESS_AVAILABLE:
        return "Error: python-chess not installed"

    state = load_game_state()
    board = chess.Board(state["fen"])

    piece_count = len(board.piece_map())
    if piece_count >= 28:
        phase = "Opening"
    elif piece_count >= 14:
        phase = "Middlegame"
    else:
        phase = "Endgame"

    white_material = 0
    black_material = 0

    for piece in board.piece_map().values():
        value = PIECE_VALUES.get(piece.symbol().lower(), 0)
        if piece.color == chess.WHITE:
            white_material += value
        else:
            black_material += value

    diff = white_material - black_material
    if diff > 2:
        material = "White ahead"
    elif diff < -2:
        material = "Black ahead"
    else:
        material = "Equal"

    to_move = "White" if board.turn == chess.WHITE else "Black"
    check = " (CHECK)" if board.is_check() else ""

    return f"Phase: {phase} | Material: {material} (W:{white_material} B:{black_material}) | {to_move} to move{check}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
