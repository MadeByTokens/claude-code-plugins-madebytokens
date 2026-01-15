"""
Chess adapters for different backends.

Available adapters:
- StockfishAdapter: Play against Stockfish engine
- LocalBoardAdapter: Terminal-based board for human play
"""

from .interface import ChessAdapter, GameState, GameResult
from .stockfish import StockfishAdapter, check_stockfish_installed, verify_installation
from .local_board import LocalBoardAdapter, board_to_ascii, load_from_fen

__all__ = [
    "ChessAdapter",
    "GameState",
    "GameResult",
    "StockfishAdapter",
    "LocalBoardAdapter",
    "check_stockfish_installed",
    "verify_installation",
    "board_to_ascii",
    "load_from_fen",
]
