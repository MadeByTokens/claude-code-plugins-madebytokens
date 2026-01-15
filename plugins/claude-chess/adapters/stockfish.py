"""
Stockfish adapter for the chess plugin.

Uses Stockfish as an opponent for testing and practice.
Requires Stockfish binary to be installed on the system.
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import chess
    import chess.engine
except ImportError:
    chess = None

from .interface import ChessAdapter, GameState, GameResult

# Import shared constants
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from constants import STOCKFISH_PATHS, SkillLevel, SKILL_DEPTHS, SKILL_TIMES


def check_stockfish_installed() -> tuple[bool, str]:
    """
    Check if Stockfish is installed and accessible.

    Returns:
        Tuple of (is_installed, path_or_error_message)
    """
    for path in STOCKFISH_PATHS:
        if shutil.which(path):
            return True, shutil.which(path)

    return False, "Stockfish not found"


def get_install_instructions() -> str:
    """Get platform-specific installation instructions for Stockfish."""
    import platform

    system = platform.system().lower()

    instructions = """
## Stockfish Installation Required

Stockfish is a free, open-source chess engine needed for testing.

"""

    if system == "linux":
        instructions += """### Linux (Debian/Ubuntu)
```bash
sudo apt update && sudo apt install stockfish
```

### Linux (Fedora)
```bash
sudo dnf install stockfish
```

### Linux (Arch)
```bash
sudo pacman -S stockfish
```
"""
    elif system == "darwin":
        instructions += """### macOS
```bash
brew install stockfish
```

If you don't have Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install stockfish
```
"""
    elif system == "windows":
        instructions += """### Windows
1. Download from: https://stockfishchess.org/download/
2. Extract the ZIP file
3. Add the folder containing stockfish.exe to your PATH

Or using Chocolatey:
```powershell
choco install stockfish
```
"""
    else:
        instructions += """### Manual Installation
Download from: https://stockfishchess.org/download/
"""

    instructions += """
After installation, verify with:
```bash
stockfish --version
```
"""
    return instructions


def check_python_chess_installed() -> tuple[bool, str]:
    """Check if python-chess library is installed."""
    if chess is None:
        return False, """
## python-chess Library Required

Install the python-chess library:
```bash
pip install chess
```
"""
    return True, ""


class StockfishAdapter(ChessAdapter):
    """
    Adapter for playing against Stockfish engine.

    Stockfish difficulty is controlled by limiting its search depth and time,
    NOT by its internal skill level setting (which makes random mistakes).
    This provides more natural play at different strengths.
    """

    def __init__(self, skill_level: str = "club", stockfish_path: Optional[str] = None):
        """
        Initialize Stockfish adapter.

        Args:
            skill_level: One of "beginner", "casual", "club", "expert"
            stockfish_path: Optional path to Stockfish binary

        Raises:
            RuntimeError: If Stockfish or python-chess is not available
        """
        # Check dependencies
        chess_ok, chess_msg = check_python_chess_installed()
        if not chess_ok:
            raise RuntimeError(chess_msg)

        if stockfish_path:
            self.stockfish_path = stockfish_path
        else:
            installed, path_or_msg = check_stockfish_installed()
            if not installed:
                raise RuntimeError(get_install_instructions())
            self.stockfish_path = path_or_msg

        self.skill_level = SkillLevel.from_string(skill_level)
        self.depth = SKILL_DEPTHS.get(self.skill_level, 8)
        self.time_limit = SKILL_TIMES.get(self.skill_level, 1.0)

        self.board: Optional[chess.Board] = None
        self.engine: Optional[chess.engine.SimpleEngine] = None
        self.our_color: Optional[str] = None
        self.move_history: list[str] = []

    def _ensure_engine(self):
        """Ensure the engine is running."""
        if self.engine is None:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)

    def _close_engine(self):
        """Close the engine if running."""
        if self.engine is not None:
            self.engine.quit()
            self.engine = None

    def start_game(self, our_color: str = "white") -> GameState:
        """Start a new game against Stockfish."""
        self._close_engine()  # Close any existing game
        self._ensure_engine()

        self.board = chess.Board()
        self.our_color = our_color
        self.move_history = []

        return self.get_position()

    def get_position(self) -> GameState:
        """Get the current game state."""
        if self.board is None:
            raise RuntimeError("No active game. Call start_game() first.")

        # Determine if it's our turn
        current_turn = "white" if self.board.turn == chess.WHITE else "black"
        is_our_turn = current_turn == self.our_color

        # Determine game result
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

        # Get last opponent move
        last_opponent_move = None
        if self.move_history and not is_our_turn:
            last_opponent_move = self.move_history[-1] if self.move_history else None

        return GameState(
            fen=self.board.fen(),
            move_history=self.move_history.copy(),
            our_color=self.our_color,
            is_our_turn=is_our_turn,
            result=result,
            last_opponent_move=last_opponent_move
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

    def wait_for_opponent(self, timeout: Optional[float] = None) -> GameState:
        """
        Let Stockfish make its move.

        The engine's strength is controlled by depth and time limits.
        """
        if self.board is None:
            raise RuntimeError("No active game. Call start_game() first.")

        if self.is_game_over():
            return self.get_position()

        self._ensure_engine()

        # Calculate with depth and time limits
        limit = chess.engine.Limit(
            depth=self.depth,
            time=timeout if timeout else self.time_limit
        )

        result = self.engine.play(self.board, limit)
        if result.move:
            self.board.push(result.move)
            self.move_history.append(result.move.uci())

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

        # Set result based on our color
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
            last_opponent_move=self.move_history[-1] if self.move_history else None
        )

    def __del__(self):
        """Cleanup when adapter is destroyed."""
        self._close_engine()


def verify_installation() -> tuple[bool, str]:
    """
    Verify all dependencies are installed and working.

    Returns:
        Tuple of (all_ok, message)
    """
    messages = []

    # Check python-chess
    chess_ok, chess_msg = check_python_chess_installed()
    if not chess_ok:
        messages.append(chess_msg)

    # Check Stockfish
    sf_ok, sf_msg = check_stockfish_installed()
    if not sf_ok:
        messages.append(get_install_instructions())

    if messages:
        return False, "\n".join(messages)

    # Try to actually run Stockfish
    try:
        adapter = StockfishAdapter(skill_level="beginner")
        state = adapter.start_game()
        del adapter
        return True, f"All dependencies OK. Stockfish found at: {sf_msg}"
    except Exception as e:
        return False, f"Stockfish test failed: {e}\n{get_install_instructions()}"
