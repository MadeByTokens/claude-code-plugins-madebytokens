#!/usr/bin/env python3
"""
Detect overused buzzwords in resumes and suggest alternatives.

Features:
- Context-aware detection (avoids false positives in technical contexts)
- Pre-compiled regex patterns for performance
- Configurable severity levels
- JSON output option

Usage:
    python detect_buzzwords.py resume.md [--json]

Requirements:
    Python 3.8+
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern, Set, Tuple

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# Scoring thresholds
BUZZWORD_TOLERANCE_FACTOR = 1.5  # Allow this many weighted buzzwords per line
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Severity weights for scoring
SEVERITY_WEIGHTS: Dict[str, int] = {
    "high": 3,
    "medium": 2,
    "low": 1
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class BuzzwordMatch:
    """Represents a detected buzzword."""
    line_number: int
    text: str
    buzzword: str
    category: str
    suggestion: str
    severity: str


@dataclass
class BuzzwordDefinition:
    """Pre-compiled buzzword with metadata."""
    pattern: Pattern
    word: str
    suggestion: str
    category: str
    severity: str
    # Context patterns that make this buzzword acceptable (false positive prevention)
    allowed_contexts: List[Pattern]


# =============================================================================
# BUZZWORD DEFINITIONS WITH CONTEXT AWARENESS
# =============================================================================

# Words that should NOT be flagged when appearing in certain contexts
CONTEXT_EXCEPTIONS: Dict[str, List[str]] = {
    # "bandwidth" is okay in technical contexts
    "bandwidth": [
        r"network\s+bandwidth",
        r"bandwidth\s+(usage|consumption|limit|cap|throttl)",
        r"(increase|optimize|reduce)\s+bandwidth",
        r"bandwidth\s+(of|for)\s+(the\s+)?(network|connection|server)",
        r"MB/s|Mbps|Gbps",
    ],
    # "leverage" might be okay in finance
    "leverage": [
        r"financial\s+leverage",
        r"leverage\s+ratio",
        r"debt.{0,20}leverage",
    ],
    # "scalable" is okay when describing actual scaling
    "scalable": [
        r"scalable\s+(to|from)\s+\d+",
        r"horizontally\s+scalable",
        r"vertically\s+scalable",
        r"scalable\s+(architecture|infrastructure|system)",
    ],
    # "robust" is okay in technical contexts
    "robust": [
        r"robust\s+(testing|test|error.handling)",
        r"robust\s+(against|to)\s+",
    ],
    # "ecosystem" is okay for actual tech ecosystems
    "ecosystem": [
        r"(AWS|Azure|Google|Apple|Android|React|Node|Python)\s+ecosystem",
        r"ecosystem\s+(of\s+)?(tools|libraries|packages)",
    ],
}


# Buzzword definitions by category
BUZZWORD_CATEGORIES: Dict[str, Dict] = {
    # Corporate jargon - usually meaningless
    "corporate_jargon": {
        "severity": "high",
        "words": {
            "synergy": "collaboration, coordination",
            "synergize": "collaborate, coordinate",
            "leverage": "use, apply, utilize",
            "leveraged": "used, applied",
            "paradigm": "model, approach, framework",
            "paradigm shift": "major change, transformation",
            "bandwidth": "capacity, availability (unless technical context)",
            "circle back": "follow up, revisit",
            "move the needle": "make measurable impact, improve metrics",
            "low-hanging fruit": "quick wins, easy improvements",
            "boil the ocean": "be specific about scope instead",
            "value-add": "benefit, contribution",
            "value proposition": "benefit, offering",
            "core competency": "key skill, primary strength",
            "best-in-class": "leading, top-performing (with evidence)",
            "world-class": "specify what makes it exceptional",
            "cutting-edge": "specify the technology or approach",
            "bleeding-edge": "specify the innovation",
            "game-changer": "describe the actual impact",
            "disruptive": "describe the innovation specifically",
            "innovative": "describe what was new",
            "revolutionary": "describe the change specifically",
            "transformational": "describe what transformed",
            "holistic": "comprehensive, integrated",
            "robust": "reliable, well-tested, strong",
            "scalable": "specify how it scales",
            "seamless": "smooth, integrated, automatic",
            "streamlined": "simplified, efficient (quantify if possible)",
            "ecosystem": "environment, system, platform",
            "empower": "enable, support, give authority to",
            "empowered": "enabled, gave authority to",
        }
    },
    # Self-descriptive buzzwords - show don't tell
    "self_descriptive": {
        "severity": "medium",
        "words": {
            "passionate": "[show through achievements, don't claim]",
            "driven": "[demonstrate through results]",
            "motivated": "[demonstrate through results]",
            "self-motivated": "[demonstrate through results]",
            "detail-oriented": "[show through specific examples]",
            "results-oriented": "[show the results instead]",
            "results-driven": "[show the results instead]",
            "team player": "[show collaboration examples]",
            "go-getter": "[show initiative examples]",
            "self-starter": "[show initiative examples]",
            "proactive": "[show examples of anticipating needs]",
            "dynamic": "[describe specific adaptability]",
            "hardworking": "[show through accomplishments]",
            "dedicated": "[show through tenure or achievements]",
            "enthusiastic": "[show through engagement or results]",
            "creative": "[show creative solutions or projects]",
            "strategic thinker": "[show strategic decisions made]",
            "thought leader": "[cite publications, talks, or influence]",
            "visionary": "[describe the vision and its implementation]",
            "guru": "[list specific expertise and credentials]",
            "ninja": "[remove - describe actual skills]",
            "rockstar": "[remove - describe actual achievements]",
            "wizard": "[remove - describe actual skills]",
            "expert": "[specify expertise area and evidence]",
        }
    },
    # Action verb buzzwords - often overused but lower severity
    "action_verbs": {
        "severity": "low",
        "words": {
            "spearheaded": "led, initiated, started",
            "championed": "advocated for, promoted, led",
            "orchestrated": "coordinated, organized, managed",
            "quarterbacked": "led, managed, directed",
            "drove": "led, managed, increased (be specific)",
            "evangelized": "promoted, advocated for",
            "socialized": "shared, presented, communicated",
        }
    },
    # Vague achievements
    "vague_achievements": {
        "severity": "medium",
        "words": {
            "exceeded expectations": "specify by how much",
            "consistently exceeded": "specify metrics and percentages",
            "top performer": "specify ranking or metrics",
            "high performer": "specify metrics",
            "outstanding results": "quantify the results",
            "exceptional results": "quantify the results",
            "proven track record": "cite specific achievements",
            "demonstrated ability": "describe specific instances",
            "strong background": "list specific experience",
            "extensive experience": "specify years and areas",
            "vast experience": "specify years and areas",
        }
    }
}


def compile_buzzwords() -> List[BuzzwordDefinition]:
    """Pre-compile all buzzword patterns with context awareness."""
    compiled = []

    for category, category_info in BUZZWORD_CATEGORIES.items():
        severity = category_info["severity"]
        words = category_info["words"]

        for word, suggestion in words.items():
            # Compile the main pattern
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)

            # Compile context exception patterns
            allowed_contexts = []
            if word in CONTEXT_EXCEPTIONS:
                for ctx_pattern in CONTEXT_EXCEPTIONS[word]:
                    allowed_contexts.append(re.compile(ctx_pattern, re.IGNORECASE))

            compiled.append(BuzzwordDefinition(
                pattern=pattern,
                word=word,
                suggestion=suggestion,
                category=category,
                severity=severity,
                allowed_contexts=allowed_contexts
            ))

    return compiled


# Pre-compile at module load time
COMPILED_BUZZWORDS: List[BuzzwordDefinition] = compile_buzzwords()


# =============================================================================
# DETECTION LOGIC
# =============================================================================

def detect_buzzwords(content: str) -> List[BuzzwordMatch]:
    """
    Scan content for buzzwords with context awareness.

    Returns list of matches, excluding those in acceptable contexts.
    """
    matches = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()

        for buzzword_def in COMPILED_BUZZWORDS:
            if buzzword_def.pattern.search(line_lower):
                # Check if any allowed context applies
                context_allowed = False
                for ctx_pattern in buzzword_def.allowed_contexts:
                    if ctx_pattern.search(line_lower):
                        context_allowed = True
                        break

                if not context_allowed:
                    matches.append(BuzzwordMatch(
                        line_number=line_num,
                        text=line.strip(),
                        buzzword=buzzword_def.word,
                        category=buzzword_def.category,
                        suggestion=buzzword_def.suggestion,
                        severity=buzzword_def.severity
                    ))

    return matches


def calculate_score(matches: List[BuzzwordMatch], total_lines: int) -> float:
    """
    Calculate a buzzword score (0 = buzzword heavy, 1 = clean).

    Higher tolerance than vague claims since some buzzwords are acceptable.
    """
    if total_lines == 0:
        return 1.0

    # Weight by severity
    weighted_issues = sum(SEVERITY_WEIGHTS.get(m.severity, 2) for m in matches)

    # Normalize with tolerance factor
    max_expected = total_lines * BUZZWORD_TOLERANCE_FACTOR
    score = max(0.0, 1.0 - (weighted_issues / max(max_expected, 1)))

    return round(score, 2)


# =============================================================================
# FILE HANDLING
# =============================================================================

def validate_and_read_file(file_path: str) -> Tuple[str, Optional[str]]:
    """
    Validate and read file with comprehensive error handling.

    Returns:
        Tuple of (content, error_message). If error_message is not None, content is empty.
    """
    if not os.path.exists(file_path):
        return "", f"File not found: {file_path}"

    if not os.path.isfile(file_path):
        return "", f"Path is not a file: {file_path}"

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE_BYTES:
        return "", f"File too large: {file_size / 1024 / 1024:.1f}MB (max {MAX_FILE_SIZE_MB}MB)"

    if file_size == 0:
        return "", f"File is empty: {file_path}"

    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            if '\x00' in content:
                return "", f"File appears to be binary, not text: {file_path}"

            return content, None

        except UnicodeDecodeError:
            continue
        except PermissionError:
            return "", f"Permission denied reading file: {file_path}"
        except IOError as e:
            return "", f"Error reading file: {e}"

    return "", f"Could not decode file with any supported encoding: {file_path}"


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Detect buzzwords in resumes and suggest clearer alternatives",
        epilog="Example: python detect_buzzwords.py resume.md --json"
    )
    parser.add_argument("file", help="Path to resume file (markdown or text)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Read and validate file
    content, error = validate_and_read_file(args.file)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    # Analyze
    matches = detect_buzzwords(content)
    total_lines = len([l for l in content.split('\n') if l.strip()])
    score = calculate_score(matches, total_lines)

    # Group by category
    by_category: Dict[str, List[BuzzwordMatch]] = {}
    for match in matches:
        if match.category not in by_category:
            by_category[match.category] = []
        by_category[match.category].append(match)

    # Output
    if args.json:
        output = {
            "file": args.file,
            "score": score,
            "total_buzzwords": len(matches),
            "by_severity": {
                "high": len([m for m in matches if m.severity == "high"]),
                "medium": len([m for m in matches if m.severity == "medium"]),
                "low": len([m for m in matches if m.severity == "low"])
            },
            "by_category": {
                cat: len(items) for cat, items in by_category.items()
            },
            "matches": [
                {
                    "line": m.line_number,
                    "text": m.text,
                    "buzzword": m.buzzword,
                    "category": m.category,
                    "suggestion": m.suggestion,
                    "severity": m.severity
                }
                for m in matches
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Buzzword Analysis: {args.file}")
        print(f"{'=' * 50}")
        print(f"Clarity Score: {score:.0%} (higher is better)")
        print(f"Total Buzzwords Found: {len(matches)}")
        print()

        if by_category:
            print("By Category:")
            for cat, items in sorted(by_category.items()):
                cat_display = cat.replace('_', ' ').title()
                print(f"  - {cat_display}: {len(items)}")
            print()

            print("Details:")
            print("-" * 50)

            # Sort by severity (highest first), then line number
            sorted_matches = sorted(
                matches,
                key=lambda x: (SEVERITY_WEIGHTS.get(x.severity, 0) * -1, x.line_number)
            )

            for match in sorted_matches:
                print(f"\n[{match.severity.upper()}] Line {match.line_number}: \"{match.buzzword}\"")
                print(f"  Category: {match.category.replace('_', ' ').title()}")
                print(f"  Suggestion: {match.suggestion}")
        else:
            print("No buzzwords detected! Resume language is clear and specific.")


if __name__ == "__main__":
    main()
