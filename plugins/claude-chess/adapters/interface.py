"""
Abstract interface for chess adapters.

All adapters (Stockfish, Lichess, local board) implement this interface
to provide a consistent way to interact with different chess backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class GameResult(Enum):
    WHITE_WINS = "1-0"
    BLACK_WINS = "0-1"
    DRAW = "1/2-1/2"
    IN_PROGRESS = "*"


@dataclass
class GameState:
    """Represents the current state of a chess game."""
    fen: str
    move_history: list[str]  # UCI format moves
    our_color: str  # "white" or "black"
    is_our_turn: bool
    result: GameResult
    last_opponent_move: Optional[str] = None  # UCI format

    def to_dict(self) -> dict:
        return {
            "fen": self.fen,
            "move_history": self.move_history,
            "our_color": self.our_color,
            "is_our_turn": self.is_our_turn,
            "result": self.result.value,
            "last_opponent_move": self.last_opponent_move
        }


class ChessAdapter(ABC):
    """
    Abstract base class for chess adapters.

    Adapters handle communication with different chess backends
    while the plugin core handles the AI reasoning.
    """

    @abstractmethod
    def start_game(self, our_color: str = "white") -> GameState:
        """
        Start a new game.

        Args:
            our_color: "white" or "black"

        Returns:
            Initial GameState
        """
        pass

    @abstractmethod
    def get_position(self) -> GameState:
        """
        Get the current game state.

        Returns:
            Current GameState with FEN, move history, etc.
        """
        pass

    @abstractmethod
    def make_move(self, uci_move: str) -> GameState:
        """
        Make a move on the board.

        Args:
            uci_move: Move in UCI format (e.g., "e2e4", "g1f3", "e7e8q")

        Returns:
            Updated GameState after move

        Raises:
            ValueError: If move is illegal
        """
        pass

    @abstractmethod
    def wait_for_opponent(self, timeout: Optional[float] = None) -> GameState:
        """
        Wait for opponent to make a move.

        For engine adapters, this triggers the engine to calculate.
        For online adapters, this polls for opponent's move.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            Updated GameState with opponent's move
        """
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        """Check if the game has ended (checkmate, draw, resignation)."""
        pass

    @abstractmethod
    def get_legal_moves(self) -> list[str]:
        """
        Get all legal moves in the current position.

        Returns:
            List of legal moves in UCI format
        """
        pass

    @abstractmethod
    def resign(self) -> GameState:
        """Resign the current game."""
        pass

    def is_move_legal(self, uci_move: str) -> bool:
        """Check if a move is legal in the current position."""
        return uci_move in self.get_legal_moves()
