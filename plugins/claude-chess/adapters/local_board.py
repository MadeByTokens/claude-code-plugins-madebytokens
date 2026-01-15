"""
Local board adapter for the chess plugin.

Provides a terminal-based chess board display for human vs AI play.
Uses python-chess for board management and move validation.
"""

from typing import Optional

try:
    import chess
except ImportError:
    chess = None

from .interface import ChessAdapter, GameState, GameResult


# Unicode chess pieces for display
UNICODE_PIECES = {
    'K': '\u2654', 'Q': '\u2655', 'R': '\u2656', 'B': '\u2657', 'N': '\u2658', 'P': '\u2659',
    'k': '\u265A', 'q': '\u265B', 'r': '\u265C', 'b': '\u265D', 'n': '\u265E', 'p': '\u265F',
}

# ASCII pieces as fallback
ASCII_PIECES = {
    'K': 'K', 'Q': 'Q', 'R': 'R', 'B': 'B', 'N': 'N', 'P': 'P',
    'k': 'k', 'q': 'q', 'r': 'r', 'b': 'b', 'n': 'n', 'p': 'p',
}


def board_to_ascii(board: 'chess.Board', perspective: str = "white", use_unicode: bool = True) -> str:
    """
    Convert a chess board to ASCII/Unicode representation.

    Args:
        board: The chess.Board to display
        perspective: "white" or "black" - which side is at the bottom
        use_unicode: Whether to use Unicode chess symbols

    Returns:
        Multi-line string representation of the board
    """
    pieces = UNICODE_PIECES if use_unicode else ASCII_PIECES

    lines = []
    lines.append("  +-----------------+")

    # Determine rank order based on perspective
    if perspective == "white":
        ranks = range(7, -1, -1)
        files = range(8)
    else:
        ranks = range(8)
        files = range(7, -1, -1)

    for rank in ranks:
        row = f"{rank + 1} |"
        for file in files:
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            if piece:
                symbol = pieces.get(piece.symbol(), piece.symbol())
            else:
                # Checkered pattern using dots and spaces
                if (rank + file) % 2 == 0:
                    symbol = '\u00B7'  # middle dot
                else:
                    symbol = ' '
            row += f" {symbol}"
        row += " |"
        lines.append(row)

    lines.append("  +-----------------+")

    # File labels
    if perspective == "white":
        lines.append("    a b c d e f g h")
    else:
        lines.append("    h g f e d c b a")

    return "\n".join(lines)


def move_to_san(board: 'chess.Board', uci_move: str) -> str:
    """Convert UCI move to Standard Algebraic Notation (SAN)."""
    try:
        move = chess.Move.from_uci(uci_move)
        return board.san(move)
    except Exception:
        return uci_move


class LocalBoardAdapter(ChessAdapter):
    """
    Adapter for local human vs AI games.

    This adapter manages the board state but doesn't have an opponent -
    moves are made manually (by human or by our AI).
    """

    def __init__(self):
        """Initialize the local board adapter."""
        if chess is None:
            raise RuntimeError("""
## python-chess Library Required

Install the python-chess library:
```bash
pip install chess
```
""")
        self.board: Optional[chess.Board] = None
        self.our_color: Optional[str] = None
        self.move_history: list[str] = []
        self._pending_opponent_move: Optional[str] = None

    def start_game(self, our_color: str = "white") -> GameState:
        """Start a new game."""
        self.board = chess.Board()
        self.our_color = our_color
        self.move_history = []
        self._pending_opponent_move = None

        return self.get_position()

    def get_position(self) -> GameState:
        """Get the current game state."""
        if self.board is None:
            raise RuntimeError("No active game. Call start_game() first.")

        current_turn = "white" if self.board.turn == chess.WHITE else "black"
        is_our_turn = current_turn == self.our_color

        # Determine result
        if self.board.is_checkmate():
            if self.board.turn == chess.WHITE:
                result = GameResult.BLACK_WINS
            else:
                result = GameResult.WHITE_WINS
        elif self.board.is_stalemate() or self.board.is_insufficient_material() or \
             self.board.can_claim_draw() or self.board.is_fifty_moves():
            result = GameResult.DRAW
        else:
            result = GameResult.IN_PROGRESS

        return GameState(
            fen=self.board.fen(),
            move_history=self.move_history.copy(),
            our_color=self.our_color,
            is_our_turn=is_our_turn,
            result=result,
            last_opponent_move=self._pending_opponent_move
        )

    def make_move(self, uci_move: str) -> GameState:
        """Make a move on the board."""
        if self.board is None:
            raise RuntimeError("No active game. Call start_game() first.")

        try:
            move = chess.Move.from_uci(uci_move)
            if move not in self.board.legal_moves:
                raise ValueError(f"Illegal move: {uci_move}")
            self.board.push(move)
            self.move_history.append(uci_move)
        except ValueError as e:
            raise ValueError(f"Invalid UCI move '{uci_move}': {e}")

        return self.get_position()

    def set_opponent_move(self, uci_move: str) -> GameState:
        """
        Set the opponent's move (for human input or external source).

        Args:
            uci_move: Move in UCI format

        Returns:
            Updated game state
        """
        self._pending_opponent_move = uci_move
        return self.make_move(uci_move)

    def wait_for_opponent(self, timeout: Optional[float] = None) -> GameState:
        """
        Wait for opponent move.

        For local board, this just returns current state.
        The actual opponent move should be set via set_opponent_move().
        """
        return self.get_position()

    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        if self.board is None:
            return True
        return self.board.is_game_over()

    def get_legal_moves(self) -> list[str]:
        """Get all legal moves in UCI format."""
        if self.board is None:
            return []
        return [move.uci() for move in self.board.legal_moves]

    def resign(self) -> GameState:
        """Resign the game."""
        if self.board is None:
            raise RuntimeError("No active game. Call start_game() first.")

        if self.our_color == "white":
            result = GameResult.BLACK_WINS
        else:
            result = GameResult.WHITE_WINS

        return GameState(
            fen=self.board.fen(),
            move_history=self.move_history.copy(),
            our_color=self.our_color,
            is_our_turn=False,
            result=result,
            last_opponent_move=self._pending_opponent_move
        )

    def display_board(self, use_unicode: bool = True) -> str:
        """
        Get a string representation of the current board.

        Args:
            use_unicode: Whether to use Unicode chess symbols

        Returns:
            ASCII/Unicode board representation
        """
        if self.board is None:
            return "No active game."

        return board_to_ascii(self.board, self.our_color, use_unicode)

    def get_move_history_san(self) -> list[str]:
        """Get move history in Standard Algebraic Notation."""
        if self.board is None:
            return []

        # Replay moves to get SAN for each
        temp_board = chess.Board()
        san_moves = []
        for uci_move in self.move_history:
            move = chess.Move.from_uci(uci_move)
            san_moves.append(temp_board.san(move))
            temp_board.push(move)

        return san_moves

    def get_pgn(self) -> str:
        """Get the game in PGN format."""
        if self.board is None:
            return ""

        san_moves = self.get_move_history_san()
        pgn_lines = []

        # Build move pairs
        for i in range(0, len(san_moves), 2):
            move_num = i // 2 + 1
            white_move = san_moves[i]
            black_move = san_moves[i + 1] if i + 1 < len(san_moves) else ""
            if black_move:
                pgn_lines.append(f"{move_num}. {white_move} {black_move}")
            else:
                pgn_lines.append(f"{move_num}. {white_move}")

        # Add result
        state = self.get_position()
        if state.result != GameResult.IN_PROGRESS:
            pgn_lines.append(state.result.value)

        return " ".join(pgn_lines)


def load_from_fen(fen: str, our_color: str = "white") -> LocalBoardAdapter:
    """
    Create a LocalBoardAdapter from a FEN position.

    Args:
        fen: FEN string for the position
        our_color: Which color we're playing

    Returns:
        LocalBoardAdapter set to the given position
    """
    adapter = LocalBoardAdapter()
    adapter.board = chess.Board(fen)
    adapter.our_color = our_color
    adapter.move_history = []
    return adapter
