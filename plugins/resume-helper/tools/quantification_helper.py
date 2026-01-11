#!/usr/bin/env python3
"""
Interactive tool to help candidates quantify their achievements.

Features:
- Detects claims that could benefit from quantification
- Provides targeted questions to elicit specific numbers
- Suggests templates for well-quantified bullet points
- Supports single claim analysis

Usage:
    python quantification_helper.py resume.md [--json]
    python quantification_helper.py --claim "Improved team productivity"

Requirements:
    Python 3.8+
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern, Tuple

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class UnquantifiedClaim:
    """Represents a claim that needs quantification."""
    line_number: int
    original_text: str
    claim_type: str
    questions: List[str]
    template: str


@dataclass
class ClaimPattern:
    """Pre-compiled pattern for claim detection."""
    regex: Pattern
    claim_type: str
    questions: List[str]
    template: str
    priority: int = 0


# =============================================================================
# CLAIM PATTERNS
# =============================================================================

CLAIM_PATTERN_DEFINITIONS: List[Dict] = [
    {
        "pattern": r"(led|managed|supervised|directed)\s+(a\s+)?team",
        "type": "team_leadership",
        "questions": [
            "How many people were on the team?",
            "What were their roles/levels (engineers, designers, etc.)?",
            "How long did you lead them?",
            "What was the team's main deliverable or achievement?",
        ],
        "template": "Led team of {size} {roles} to deliver {deliverable}, achieving {outcome}",
        "priority": 10
    },
    {
        "pattern": r"(improved|increased|enhanced|boosted)\s+(\w+\s+)?(performance|efficiency|productivity|speed|throughput)",
        "type": "performance_improvement",
        "questions": [
            "What specific metric improved (latency, throughput, response time)?",
            "What was the before state/baseline?",
            "What was the after state?",
            "What percentage improvement does this represent?",
            "Over what time period?",
            "How did you measure this?",
        ],
        "template": "Improved {metric} by {percentage}% (from {before} to {after}) by implementing {action}",
        "priority": 10
    },
    {
        "pattern": r"(reduced|decreased|cut|lowered|minimized)\s+(\w+\s+)?(costs?|expenses?|spending|time|latency|errors?|bugs?|incidents?)",
        "type": "reduction",
        "questions": [
            "What exactly was reduced (cost, time, errors)?",
            "What was the original amount/level?",
            "What was the final amount/level?",
            "What's the percentage or absolute reduction?",
            "Over what time period?",
            "What was the business impact (cost savings, time saved)?",
        ],
        "template": "Reduced {what} by {percentage}% (from {before} to {after}), saving {impact} annually",
        "priority": 10
    },
    {
        "pattern": r"(built|developed|created|designed|implemented|architected)\s+(\w+\s+)?(system|platform|tool|application|feature|service|api|infrastructure)",
        "type": "building",
        "questions": [
            "What technologies/stack did you use?",
            "How many users/customers use it now?",
            "What problem does it solve?",
            "What was the scale (requests/day, data volume, transactions)?",
            "How long did it take to build (timeline)?",
            "Is it still in use today? How long has it been running?",
        ],
        "template": "Built {what} using {tech}, serving {users} users and handling {scale} daily",
        "priority": 8
    },
    {
        "pattern": r"(migrated|transitioned|upgraded|converted|ported)\s+",
        "type": "migration",
        "questions": [
            "What did you migrate from and to (legacy system to modern stack)?",
            "How much data/how many systems were involved?",
            "How many users were affected?",
            "What was the downtime (zero-downtime? minimal?)?",
            "How long did the migration take?",
            "What improvement resulted (performance, cost, maintainability)?",
        ],
        "template": "Migrated {what} from {from_tech} to {to_tech}, affecting {users} users with {downtime} downtime, improving {result} by {percentage}%",
        "priority": 7
    },
    {
        "pattern": r"(mentored|coached|trained|onboarded|guided)\s+",
        "type": "mentorship",
        "questions": [
            "How many people did you mentor/train?",
            "Over what time period?",
            "What skills did you help them develop?",
            "What outcomes resulted (promotions, certifications, improved performance)?",
            "What was their level (junior, intern, new hire)?",
        ],
        "template": "Mentored {count} {level} {who} in {skills}, resulting in {outcome}",
        "priority": 6
    },
    {
        "pattern": r"(launched|shipped|released|deployed|delivered)\s+",
        "type": "launch",
        "questions": [
            "What did you launch (feature, product, service)?",
            "How many users adopted it in the first month/quarter?",
            "What was the timeline (on time? ahead of schedule?)?",
            "What was the business impact (revenue, engagement, retention)?",
            "Were there any notable metrics (downloads, signups, conversion rate)?",
        ],
        "template": "Launched {what} to {users} users, achieving {metric} within {timeframe}",
        "priority": 8
    },
    {
        "pattern": r"(automated|streamlined|optimized|simplified)\s+",
        "type": "automation",
        "questions": [
            "What process did you automate/streamline?",
            "How much time did it save per occurrence?",
            "How often was the process run (daily, weekly)?",
            "What was the total time/cost savings (annually)?",
            "What tools/technologies did you use?",
            "How many people benefited from this automation?",
        ],
        "template": "Automated {process}, reducing time from {before} to {after}, saving {hours} hours/{period} across {team_size} team members",
        "priority": 7
    },
    {
        "pattern": r"(generated|drove|increased|grew)\s+(\$|\d|revenue|sales|growth|arr|mrr)",
        "type": "revenue",
        "questions": [
            "What was the revenue/growth amount or percentage?",
            "Over what time period?",
            "What was your specific contribution to this result?",
            "How was this measured/attributed to your work?",
            "What was the starting baseline?",
        ],
        "template": "Generated ${amount} in {metric} by {action}, representing {percentage}% growth",
        "priority": 9
    },
    {
        "pattern": r"(resolved|fixed|debugged|troubleshot|diagnosed)\s+",
        "type": "problem_solving",
        "questions": [
            "What was the problem/issue?",
            "How long had it existed or how critical was it?",
            "What was the impact before fixing (downtime, user complaints, cost)?",
            "How did you solve it (root cause analysis, specific fix)?",
            "What was the result after fixing?",
        ],
        "template": "Resolved {issue} that was causing {impact}, reducing {metric} by {percentage}%",
        "priority": 6
    },
    {
        "pattern": r"(won|awarded|received|earned|recognized)\s+",
        "type": "recognition",
        "questions": [
            "What was the award/recognition?",
            "What was it for (specific achievement)?",
            "How competitive was it (out of how many candidates/teams)?",
            "When did you receive it?",
            "Who gave the award (company, industry body)?",
        ],
        "template": "Received {award} for {reason}, selected from {pool} candidates",
        "priority": 5
    },
    {
        "pattern": r"(collaborated|partnered|worked)\s+with\s+(\w+\s+)?(teams?|departments?|stakeholders?)",
        "type": "collaboration",
        "questions": [
            "How many teams/departments did you collaborate with?",
            "What was the shared goal or project?",
            "What was your specific role in the collaboration?",
            "What was the outcome of the collaboration?",
        ],
        "template": "Collaborated with {count} {teams} to deliver {project}, achieving {outcome}",
        "priority": 4
    },
    {
        "pattern": r"(wrote|authored|documented|created)\s+(\w+\s+)?(documentation|docs|specs|rfcs?|proposals?)",
        "type": "documentation",
        "questions": [
            "What type of documentation did you create?",
            "How many documents or pages?",
            "Who was the audience?",
            "What was the impact (reduced onboarding time, fewer questions)?",
        ],
        "template": "Authored {count} {doc_type} documents, reducing {metric} by {percentage}%",
        "priority": 3
    },
]


def compile_claim_patterns() -> List[ClaimPattern]:
    """Pre-compile all claim patterns."""
    compiled = []
    for p in CLAIM_PATTERN_DEFINITIONS:
        compiled.append(ClaimPattern(
            regex=re.compile(p["pattern"], re.IGNORECASE),
            claim_type=p["type"],
            questions=p["questions"],
            template=p["template"],
            priority=p.get("priority", 0)
        ))
    # Sort by priority (higher first)
    compiled.sort(key=lambda x: -x.priority)
    return compiled


COMPILED_CLAIM_PATTERNS: List[ClaimPattern] = compile_claim_patterns()


# Default questions for claims that don't match specific patterns
DEFAULT_QUESTIONS: List[str] = [
    "What specific metric or outcome resulted from this?",
    "Can you put a number on the impact (percentage, count, dollars)?",
    "What was the scale (users, transactions, data volume)?",
    "What was the timeframe?",
    "How did you measure success?",
]

DEFAULT_TEMPLATE = "{action}, resulting in {quantified_outcome}"


# =============================================================================
# DETECTION LOGIC
# =============================================================================

def find_unquantified_claims(content: str) -> List[UnquantifiedClaim]:
    """Find claims in resume that could benefit from quantification."""
    claims: List[UnquantifiedClaim] = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        # Skip headers and empty lines
        stripped = line.strip()
        if stripped.startswith('#') or not stripped:
            continue

        for pattern in COMPILED_CLAIM_PATTERNS:
            match = pattern.regex.search(line)
            if match:
                # Check if it already has adequate quantification
                has_numbers = bool(re.search(r'\d+', line))
                has_percentage = bool(re.search(r'\d+\s*%', line))
                has_dollar = bool(re.search(r'\$[\d,]+', line))
                has_multiplier = bool(re.search(r'\d+x\b', line, re.IGNORECASE))

                # Consider it quantified if it has numbers AND (percentage OR dollar OR multiplier)
                if has_numbers and (has_percentage or has_dollar or has_multiplier):
                    continue

                claims.append(UnquantifiedClaim(
                    line_number=line_num,
                    original_text=stripped,
                    claim_type=pattern.claim_type,
                    questions=pattern.questions,
                    template=pattern.template
                ))
                break  # Only match one pattern per line

    return claims


def analyze_single_claim(claim_text: str) -> Dict:
    """Analyze a single claim and return questions to quantify it."""
    for pattern in COMPILED_CLAIM_PATTERNS:
        if pattern.regex.search(claim_text):
            return {
                "claim": claim_text,
                "type": pattern.claim_type,
                "questions": pattern.questions,
                "template": pattern.template
            }

    # Generic questions if no specific pattern matched
    return {
        "claim": claim_text,
        "type": "general",
        "questions": DEFAULT_QUESTIONS,
        "template": DEFAULT_TEMPLATE
    }


# =============================================================================
# FILE HANDLING
# =============================================================================

def validate_and_read_file(file_path: str) -> Tuple[str, Optional[str]]:
    """Validate and read file with comprehensive error handling."""
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
        description="Help quantify resume achievements with specific numbers",
        epilog="Example: python quantification_helper.py resume.md --json"
    )
    parser.add_argument("file", nargs="?", help="Path to resume file")
    parser.add_argument("--claim", help="Single claim to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.claim:
        # Analyze single claim
        result = analyze_single_claim(args.claim)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Claim: \"{args.claim}\"")
            print(f"Type: {result['type'].replace('_', ' ').title()}")
            print()
            print("Questions to quantify:")
            for i, q in enumerate(result['questions'], 1):
                print(f"  {i}. {q}")
            print()
            print(f"Template: {result['template']}")
        return

    if not args.file:
        print("Error: Please provide a resume file or use --claim", file=sys.stderr)
        sys.exit(1)

    # Read and validate file
    content, error = validate_and_read_file(args.file)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    claims = find_unquantified_claims(content)

    if args.json:
        output = {
            "file": args.file,
            "total_claims_found": len(claims),
            "claims": [
                {
                    "line": c.line_number,
                    "text": c.original_text,
                    "type": c.claim_type,
                    "questions": c.questions,
                    "template": c.template
                }
                for c in claims
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Quantification Helper: {args.file}")
        print(f"{'=' * 60}")
        print(f"Found {len(claims)} claims that could be quantified better")
        print()

        if not claims:
            print("All claims appear to have quantification.")
            print("Review manually to ensure numbers are specific and defensible.")
            return

        for i, claim in enumerate(claims, 1):
            print(f"{'─' * 60}")
            print(f"Claim #{i} (Line {claim.line_number})")
            print(f"Type: {claim.claim_type.replace('_', ' ').title()}")
            print()
            print(f"Original: \"{claim.original_text[:80]}{'...' if len(claim.original_text) > 80 else ''}\"")
            print()
            print("Questions to answer:")
            for j, q in enumerate(claim.questions, 1):
                print(f"  {j}. {q}")
            print()
            print(f"Suggested template: {claim.template}")
            print()

        print(f"{'=' * 60}")
        print("Tips for quantification:")
        print("  - If you don't know exact numbers, use ranges or estimates")
        print("  - Even rough numbers ('~50%', '10+') are better than none")
        print("  - Use percentages when absolute numbers aren't impressive")
        print("  - Include timeframes for context ('in 3 months', 'annually')")
        print("  - Every number should be defensible in an interview")


if __name__ == "__main__":
    main()
