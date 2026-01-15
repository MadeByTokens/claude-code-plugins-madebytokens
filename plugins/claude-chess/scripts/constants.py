"""
Shared constants for the chess plugin.
"""

from enum import Enum
from typing import List

# Common paths where Stockfish might be installed
STOCKFISH_PATHS: List[str] = [
    "stockfish",
    "/usr/bin/stockfish",
    "/usr/local/bin/stockfish",
    "/opt/homebrew/bin/stockfish",  # macOS Homebrew ARM
    "/usr/games/stockfish",  # Debian/Ubuntu
]


class SkillLevel(str, Enum):
    """Chess skill levels for the AI."""
    BEGINNER = "beginner"
    CASUAL = "casual"
    CLUB = "club"
    EXPERT = "expert"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a string is a valid skill level."""
        return value.lower() in [level.value for level in cls]

    @classmethod
    def from_string(cls, value: str) -> "SkillLevel":
        """Convert string to SkillLevel, defaulting to CLUB if invalid."""
        value = value.lower().strip() if value else "club"
        try:
            return cls(value)
        except ValueError:
            return cls.CLUB


# Stockfish search depth limits for different skill levels
SKILL_DEPTHS = {
    SkillLevel.BEGINNER: 1,
    SkillLevel.CASUAL: 3,
    SkillLevel.CLUB: 8,
    SkillLevel.EXPERT: 15,
}

# Stockfish time limits per move in seconds
SKILL_TIMES = {
    SkillLevel.BEGINNER: 0.1,
    SkillLevel.CASUAL: 0.3,
    SkillLevel.CLUB: 1.0,
    SkillLevel.EXPERT: 3.0,
}
