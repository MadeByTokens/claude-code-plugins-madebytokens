#!/usr/bin/env python3
"""
Sandboxed Python calculator for chess position analysis.

Usage:
    echo "result = sum(1 for r in board for c in r if c == 'P')" | python3 scripts/calculate.py

Or with a file:
    python3 scripts/calculate.py < my_code.py

The code runs with:
    - board: 8x8 list (['r','n','b',...], rank 8 first)
    - our_color: 'white' or 'black'
    - their_color: opposite of our_color
    - math module available

Set 'result' variable to return your answer.
"""

import sys
import json
import signal
import math as math_module
from pathlib import Path

STATE_FILE = Path("state/game.json")
MAX_LINES = 30
TIMEOUT_SECONDS = 0.5

def load_board():
    """Load board from game.json as simple 8x8 list."""
    if not STATE_FILE.exists():
        return None, None, "No game state found"

    with open(STATE_FILE) as f:
        state = json.load(f)

    fen = state.get("fen", "")
    if not fen:
        return None, None, "No FEN in game state"

    # Convert FEN to 8x8 board
    fen_board = fen.split()[0]
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
    return board, our_color, None

def run_sandboxed(code, board, our_color):
    """Run code in sandbox with timeout."""

    # Check line limit
    lines = [l for l in code.strip().split('\n') if l.strip() and not l.strip().startswith('#')]
    if len(lines) > MAX_LINES:
        return None, f"Code too long ({len(lines)} lines, max {MAX_LINES})"

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
            return None, f"Forbidden pattern '{pattern}'"

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
        'print': lambda *args: None,  # Silent print
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
        raise TimeoutError("Timeout")

    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, TIMEOUT_SECONDS)

        exec(code, env)

        signal.setitimer(signal.ITIMER_REAL, 0)

        result = env.get('result')
        if result is None:
            return None, "Code must set 'result' variable"

        result_str = str(result)
        if len(result_str) > 500:
            result_str = result_str[:500] + "..."

        return result_str, None

    except TimeoutError:
        signal.setitimer(signal.ITIMER_REAL, 0)
        return None, f"Timeout ({TIMEOUT_SECONDS}s limit)"
    except Exception as e:
        signal.setitimer(signal.ITIMER_REAL, 0)
        return None, f"{type(e).__name__}: {e}"

def main():
    # Read code from stdin
    code = sys.stdin.read()
    if not code.strip():
        print("Error: No code provided")
        sys.exit(1)

    # Load board
    board, our_color, err = load_board()
    if err:
        print(f"Error: {err}")
        sys.exit(1)

    # Run calculation
    result, err = run_sandboxed(code, board, our_color)
    if err:
        print(f"Error: {err}")
        sys.exit(1)

    print(result)

if __name__ == "__main__":
    main()
