#!/usr/bin/env python3
"""
Detect vague claims in resumes that need quantification or specifics.

Usage:
    python detect_vague_claims.py resume.md [--json]

Requirements:
    Python 3.8+
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Pattern, Tuple

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# Scoring thresholds - adjust these to tune sensitivity
LINES_PER_EXPECTED_ISSUE = 3  # Expect roughly 1 issue per N content lines
AVERAGE_SEVERITY_WEIGHT = 2   # Baseline severity for normalization (medium)
MAX_FILE_SIZE_MB = 10         # Maximum file size to process
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
class VagueClaim:
    """Represents a detected vague claim."""
    line_number: int
    text: str
    pattern_matched: str
    issues: List[str]
    suggestion: str
    severity: str  # high, medium, low


@dataclass
class CompiledPattern:
    """Pre-compiled pattern with metadata."""
    regex: Pattern
    issue: str
    suggestion: str
    severity: str
    unless_regex: Optional[Pattern] = None
    priority: int = 0  # Higher priority patterns are checked first


# =============================================================================
# VAGUE CLAIM PATTERNS
# =============================================================================

# Raw pattern definitions
VAGUE_PATTERN_DEFINITIONS: List[Dict] = [
    {
        "pattern": r"\b(led|managed)\s+(a\s+)?team\b",
        "issue": "Team size not specified",
        "suggestion": "Specify team size: 'Led team of [N] engineers'",
        "severity": "high",
        "unless_followed_by": r"\s+of\s+\d+",
        "priority": 10
    },
    {
        "pattern": r"\b(improved|increased|enhanced|boosted|optimized)\s+\w+",
        "issue": "Improvement not quantified",
        "suggestion": "Add percentage or metric: 'Improved [X] by [N]%'",
        "severity": "high",
        "unless_followed_by": r"\s+by\s+\d+",
        "priority": 10
    },
    {
        "pattern": r"\b(reduced|decreased|cut|lowered)\s+\w+",
        "issue": "Reduction not quantified",
        "suggestion": "Add percentage or amount: 'Reduced [X] by [N]%'",
        "severity": "high",
        "unless_followed_by": r"\s+by\s+\d+",
        "priority": 10
    },
    {
        "pattern": r"\bresponsible\s+for\b",
        "issue": "'Responsible for' is passive - what did you DO?",
        "suggestion": "Replace with action verb: 'Managed', 'Developed', 'Led'",
        "severity": "medium",
        "priority": 5
    },
    {
        "pattern": r"\bhelped\s+(with|to)\b",
        "issue": "'Helped' understates contribution",
        "suggestion": "Specify your role: 'Collaborated with X to achieve Y'",
        "severity": "medium",
        "priority": 5
    },
    {
        "pattern": r"\bworked\s+on\b",
        "issue": "'Worked on' is vague - what was your specific role?",
        "suggestion": "Use specific verb: 'Designed', 'Built', 'Implemented'",
        "severity": "medium",
        "priority": 5
    },
    {
        "pattern": r"\bvarious\s+\w+",
        "issue": "'Various' is vague",
        "suggestion": "List specific items or use a number",
        "severity": "low",
        "priority": 1
    },
    {
        "pattern": r"\bmultiple\s+\w+",
        "issue": "'Multiple' is vague - how many?",
        "suggestion": "Specify the number: '5 projects' instead of 'multiple projects'",
        "severity": "low",
        "priority": 1
    },
    {
        "pattern": r"\b(significant|significantly|substantial|substantially)\b",
        "issue": "Vague intensifier - quantify instead",
        "suggestion": "Replace with specific number: '40% improvement' not 'significant improvement'",
        "severity": "medium",
        "priority": 3
    },
    {
        "pattern": r"\b(greatly|major|majorly)\b",
        "issue": "Vague intensifier - quantify instead",
        "suggestion": "Replace with metrics",
        "severity": "medium",
        "priority": 3
    },
    {
        "pattern": r"\bstakeholders\b",
        "issue": "'Stakeholders' is generic",
        "suggestion": "Specify who: 'executives', 'product managers', 'customers'",
        "severity": "low",
        "priority": 1
    },
    {
        "pattern": r"\b(some|several|many|few)\s+\w+",
        "issue": "Vague quantity",
        "suggestion": "Use specific number",
        "severity": "low",
        "priority": 1
    },
    {
        "pattern": r"\betc\.?\b",
        "issue": "'etc.' suggests incomplete thought",
        "suggestion": "Either list all items or remove",
        "severity": "low",
        "priority": 1
    },
    {
        "pattern": r"\b(assisted|assisted with|assisted in)\b",
        "issue": "'Assisted' understates contribution",
        "suggestion": "Clarify your specific contribution",
        "severity": "medium",
        "priority": 4
    },
    {
        "pattern": r"\b(involved in|involved with)\b",
        "issue": "'Involved in' doesn't specify your role",
        "suggestion": "Describe your specific contribution",
        "severity": "medium",
        "priority": 4
    },
    {
        "pattern": r"\b(handled|dealt with)\b",
        "issue": "Generic action verb",
        "suggestion": "Use more specific verb: 'Resolved', 'Processed', 'Managed'",
        "severity": "low",
        "priority": 2
    },
    {
        "pattern": r"\b(things|stuff)\b",
        "issue": "Informal and vague",
        "suggestion": "Be specific about what",
        "severity": "high",
        "priority": 10
    },
    {
        "pattern": r"\b(good|great|excellent)\s+(results|performance|outcomes)\b",
        "issue": "Subjective assessment without evidence",
        "suggestion": "Quantify the results with metrics",
        "severity": "medium",
        "priority": 5
    },
]


def compile_patterns() -> List[CompiledPattern]:
    """Pre-compile all regex patterns for performance."""
    compiled = []
    for p in VAGUE_PATTERN_DEFINITIONS:
        unless_regex = None
        if "unless_followed_by" in p:
            unless_regex = re.compile(p["unless_followed_by"], re.IGNORECASE)

        compiled.append(CompiledPattern(
            regex=re.compile(p["pattern"], re.IGNORECASE),
            issue=p["issue"],
            suggestion=p["suggestion"],
            severity=p["severity"],
            unless_regex=unless_regex,
            priority=p.get("priority", 0)
        ))

    # Sort by priority (higher first) for consistent matching
    compiled.sort(key=lambda x: -x.priority)
    return compiled


# Pre-compile patterns at module load time
COMPILED_PATTERNS: List[CompiledPattern] = compile_patterns()


# =============================================================================
# DETECTION LOGIC
# =============================================================================

def detect_vague_claims(content: str) -> List[VagueClaim]:
    """
    Scan content for vague claims and return findings.

    Uses deduplication to report only one issue per line (highest priority).
    """
    claims = []
    lines = content.split('\n')
    lines_with_issues = set()  # Track which lines already have issues

    for line_num, line in enumerate(lines, 1):
        # Skip headers and empty lines
        stripped = line.strip()
        if stripped.startswith('#') or not stripped:
            continue

        # Find the highest priority match for this line
        best_match = None
        best_priority = -1

        for pattern in COMPILED_PATTERNS:
            match = pattern.regex.search(line)

            if match:
                # Check if there's an exception pattern
                if pattern.unless_regex:
                    remaining = line[match.end():]
                    if pattern.unless_regex.match(remaining):
                        continue  # Skip this match

                # Keep highest priority match
                if pattern.priority > best_priority:
                    best_match = (match, pattern)
                    best_priority = pattern.priority

        # Add the best match for this line (deduplication)
        if best_match and line_num not in lines_with_issues:
            match, pattern = best_match
            claims.append(VagueClaim(
                line_number=line_num,
                text=stripped,
                pattern_matched=match.group(),
                issues=[pattern.issue],
                suggestion=pattern.suggestion,
                severity=pattern.severity
            ))
            lines_with_issues.add(line_num)

    return claims


def calculate_score(claims: List[VagueClaim], total_lines: int) -> float:
    """
    Calculate a vagueness score (0 = very vague, 1 = very specific).

    The score is based on:
    - Number of issues found
    - Severity of issues (high=3, medium=2, low=1)
    - Normalized against expected issues for resume length
    """
    if total_lines == 0:
        return 1.0

    # Weight by severity
    weighted_issues = sum(SEVERITY_WEIGHTS.get(c.severity, 2) for c in claims)

    # Normalize: expect roughly 1 issue per LINES_PER_EXPECTED_ISSUE content lines
    # with average severity of AVERAGE_SEVERITY_WEIGHT
    max_expected_issues = (total_lines / LINES_PER_EXPECTED_ISSUE) * AVERAGE_SEVERITY_WEIGHT
    score = max(0.0, 1.0 - (weighted_issues / max(max_expected_issues, 1)))

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
    # Check file exists
    if not os.path.exists(file_path):
        return "", f"File not found: {file_path}"

    # Check it's a file, not a directory
    if not os.path.isfile(file_path):
        return "", f"Path is not a file: {file_path}"

    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE_BYTES:
        return "", f"File too large: {file_size / 1024 / 1024:.1f}MB (max {MAX_FILE_SIZE_MB}MB)"

    if file_size == 0:
        return "", f"File is empty: {file_path}"

    # Try to read with multiple encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            # Basic validation - check it looks like text
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
        description="Detect vague claims in resumes that need quantification",
        epilog="Example: python detect_vague_claims.py resume.md --json"
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
    claims = detect_vague_claims(content)
    total_lines = len([l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')])
    score = calculate_score(claims, total_lines)

    # Output
    if args.json:
        output = {
            "file": args.file,
            "score": score,
            "total_vague_claims": len(claims),
            "by_severity": {
                "high": len([c for c in claims if c.severity == "high"]),
                "medium": len([c for c in claims if c.severity == "medium"]),
                "low": len([c for c in claims if c.severity == "low"])
            },
            "claims": [
                {
                    "line": c.line_number,
                    "text": c.text,
                    "matched": c.pattern_matched,
                    "issues": c.issues,
                    "suggestion": c.suggestion,
                    "severity": c.severity
                }
                for c in claims
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Vague Claims Analysis: {args.file}")
        print(f"{'=' * 50}")
        print(f"Specificity Score: {score:.0%} (higher is better)")
        print(f"Total Issues Found: {len(claims)}")
        print(f"  - High severity: {len([c for c in claims if c.severity == 'high'])}")
        print(f"  - Medium severity: {len([c for c in claims if c.severity == 'medium'])}")
        print(f"  - Low severity: {len([c for c in claims if c.severity == 'low'])}")
        print()

        if claims:
            print("Details:")
            print("-" * 50)
            # Sort by severity first, then line number
            for claim in sorted(claims, key=lambda x: (SEVERITY_WEIGHTS.get(x.severity, 0) * -1, x.line_number)):
                print(f"\n[{claim.severity.upper()}] Line {claim.line_number}")
                print(f"  Text: \"{claim.text[:70]}{'...' if len(claim.text) > 70 else ''}\"")
                print(f"  Issue: {claim.issues[0]}")
                print(f"  Suggestion: {claim.suggestion}")
        else:
            print("No vague claims detected! Resume language is specific and clear.")


if __name__ == "__main__":
    main()
