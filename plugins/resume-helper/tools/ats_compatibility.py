#!/usr/bin/env python3
"""
Check resume for ATS (Applicant Tracking System) compatibility.

Features:
- Expanded keyword extraction (tech, soft skills, certifications, industries)
- Section detection for standard resume sections
- Contact info validation
- Format compatibility checks
- Keyword matching with job description

Usage:
    python ats_compatibility.py resume.md [job_description.md] [--json]

Requirements:
    Python 3.8+
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Pattern, Set, Tuple

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Scoring deductions by severity
SEVERITY_DEDUCTIONS: Dict[str, int] = {
    "high": 15,
    "medium": 8,
    "low": 3
}

# Section missing deduction
MISSING_SECTION_DEDUCTION = 10

# Keyword mismatch max deduction
KEYWORD_MISMATCH_MAX_DEDUCTION = 20

# Word count thresholds
MIN_WORDS = 200
MAX_WORDS = 1000
IDEAL_MIN_WORDS = 400
IDEAL_MAX_WORDS = 800

# Minimum bullet points expected
MIN_BULLET_POINTS = 5


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ATSIssue:
    """Represents an ATS compatibility issue."""
    category: str
    issue: str
    suggestion: str
    severity: str  # high, medium, low
    line_number: Optional[int] = None


@dataclass
class KeywordMatch:
    """Represents a keyword match between resume and job description."""
    keyword: str
    found_in_resume: bool
    context: Optional[str] = None
    category: str = "general"


@dataclass
class ATSReport:
    """Full ATS compatibility report."""
    score: float
    issues: List[ATSIssue] = field(default_factory=list)
    keyword_matches: List[KeywordMatch] = field(default_factory=list)
    sections_found: List[str] = field(default_factory=list)
    sections_missing: List[str] = field(default_factory=list)


# =============================================================================
# SECTION PATTERNS (Pre-compiled)
# =============================================================================

SECTION_PATTERNS: List[Tuple[Pattern, str]] = [
    (re.compile(r"^#+\s*(experience|work\s+experience|professional\s+experience|employment)", re.IGNORECASE), "experience"),
    (re.compile(r"^#+\s*(education|academic|qualifications)", re.IGNORECASE), "education"),
    (re.compile(r"^#+\s*(skills|technical\s+skills|core\s+competencies|technologies)", re.IGNORECASE), "skills"),
    (re.compile(r"^#+\s*(summary|professional\s+summary|profile|about)", re.IGNORECASE), "summary"),
    (re.compile(r"^#+\s*(projects|key\s+projects|portfolio)", re.IGNORECASE), "projects"),
    (re.compile(r"^#+\s*(certifications?|certificates?|licenses?|credentials)", re.IGNORECASE), "certifications"),
    (re.compile(r"^#+\s*(contact|personal\s+info|contact\s+info)", re.IGNORECASE), "contact"),
    (re.compile(r"^#+\s*(awards?|honors?|recognition|achievements)", re.IGNORECASE), "awards"),
    (re.compile(r"^#+\s*(publications?|papers?|research)", re.IGNORECASE), "publications"),
    (re.compile(r"^#+\s*(volunteer|community|extracurricular)", re.IGNORECASE), "volunteer"),
]

REQUIRED_SECTIONS: Set[str] = {"experience", "education", "skills"}


# =============================================================================
# KEYWORD EXTRACTION PATTERNS (Expanded)
# =============================================================================

# Pre-compiled patterns for keyword extraction
KEYWORD_PATTERNS: Dict[str, List[Pattern]] = {
    "programming_languages": [
        re.compile(r'\b(Python|Java|JavaScript|TypeScript|Go|Golang|Rust|C\+\+|C#|Ruby|PHP|Swift|Kotlin|Scala|R|MATLAB|Perl|Haskell|Elixir|Clojure|F#|Objective-C|Dart|Julia|Lua|Groovy|VB\.NET|COBOL|Fortran|Assembly)\b', re.IGNORECASE),
    ],
    "frameworks": [
        re.compile(r'\b(React|Angular|Vue|Svelte|Next\.?js|Nuxt|Node\.?js|Express|Django|Flask|FastAPI|Spring|Spring Boot|Rails|Ruby on Rails|Laravel|Symfony|ASP\.NET|\.NET Core|Hibernate|Struts)\b', re.IGNORECASE),
    ],
    "cloud_platforms": [
        re.compile(r'\b(AWS|Amazon Web Services|Azure|Microsoft Azure|GCP|Google Cloud|Google Cloud Platform|Heroku|DigitalOcean|Linode|Cloudflare|Vercel|Netlify|Firebase)\b', re.IGNORECASE),
    ],
    "devops_tools": [
        re.compile(r'\b(Docker|Kubernetes|K8s|Terraform|Ansible|Puppet|Chef|Jenkins|CircleCI|Travis CI|GitHub Actions|GitLab CI|ArgoCD|Helm|Prometheus|Grafana|Datadog|New Relic|Splunk|ELK|Elasticsearch|Logstash|Kibana)\b', re.IGNORECASE),
    ],
    "databases": [
        re.compile(r'\b(SQL|MySQL|PostgreSQL|Postgres|MongoDB|Redis|Cassandra|DynamoDB|Oracle|SQL Server|MariaDB|SQLite|Neo4j|CouchDB|Firestore|Supabase|PlanetScale|Snowflake|BigQuery|Redshift)\b', re.IGNORECASE),
    ],
    "methodologies": [
        re.compile(r'\b(Agile|Scrum|Kanban|XP|Extreme Programming|Waterfall|DevOps|DevSecOps|CI/CD|TDD|BDD|Lean|Six Sigma|SAFe|Scaled Agile)\b', re.IGNORECASE),
    ],
    "tools": [
        re.compile(r'\b(Git|GitHub|GitLab|Bitbucket|JIRA|Confluence|Trello|Asana|Slack|Notion|Figma|Sketch|Adobe XD|InVision|Postman|Swagger|VS Code|IntelliJ|Eclipse|Vim|Emacs)\b', re.IGNORECASE),
    ],
    "data_ml": [
        re.compile(r'\b(Machine Learning|ML|Deep Learning|DL|AI|Artificial Intelligence|NLP|Natural Language Processing|Computer Vision|TensorFlow|PyTorch|scikit-learn|Keras|Pandas|NumPy|Spark|Hadoop|Tableau|Power BI|Looker|dbt|Airflow|MLflow)\b', re.IGNORECASE),
    ],
    "soft_skills": [
        re.compile(r'\b(leadership|communication|teamwork|collaboration|problem.solving|critical thinking|time management|project management|stakeholder management|mentoring|coaching|presentation|negotiation|conflict resolution|decision.making|adaptability|creativity|innovation)\b', re.IGNORECASE),
    ],
    "certifications": [
        re.compile(r'\b(AWS Certified|Azure Certified|Google Cloud Certified|PMP|Scrum Master|CSM|PSM|CISSP|CISM|CompTIA|CKA|CKAD|CKS|TOGAF|ITIL|Six Sigma|Green Belt|Black Belt|PE|CPA|CFA|Series 7|Series 63)\b', re.IGNORECASE),
    ],
    "degrees": [
        re.compile(r"\b(bachelor'?s?|master'?s?|phd|ph\.d|doctorate|mba|bs|ms|ba|ma|bsc|msc|b\.s\.|m\.s\.|associate'?s?|jd|md|dds)\b", re.IGNORECASE),
    ],
    "industries": [
        re.compile(r'\b(fintech|healthtech|edtech|e-?commerce|saas|b2b|b2c|enterprise|startup|fortune 500|consulting|banking|insurance|healthcare|pharmaceutical|manufacturing|retail|logistics|telecommunications|media|gaming|cybersecurity)\b', re.IGNORECASE),
    ],
    "security": [
        re.compile(r'\b(OWASP|penetration testing|vulnerability|encryption|SSL|TLS|OAuth|SAML|SSO|IAM|RBAC|SOC 2|HIPAA|GDPR|PCI.DSS|ISO 27001|security audit|threat modeling)\b', re.IGNORECASE),
    ],
}


def extract_keywords_from_jd(jd_content: str) -> List[KeywordMatch]:
    """
    Extract important keywords from job description using expanded patterns.

    Returns list of KeywordMatch objects (without resume context yet).
    """
    keywords: Dict[str, str] = {}  # keyword -> category

    # Extract using pattern categories
    for category, patterns in KEYWORD_PATTERNS.items():
        for pattern in patterns:
            matches = pattern.findall(jd_content)
            for match in matches:
                keyword = match.lower() if isinstance(match, str) else match[0].lower()
                keywords[keyword] = category

    # Extract capitalized acronyms (likely technologies not in our patterns)
    acronyms = re.findall(r'\b[A-Z]{2,6}\b', jd_content)
    for acronym in acronyms:
        if acronym.lower() not in keywords:
            keywords[acronym.lower()] = "acronym"

    # Extract years of experience requirements
    exp_matches = re.findall(r'(\d+)\+?\s*years?', jd_content, re.IGNORECASE)
    if exp_matches:
        max_years = max(int(y) for y in exp_matches)
        keywords[f"{max_years}+ years"] = "experience_level"

    # Create KeywordMatch objects (found_in_resume will be set later)
    return [
        KeywordMatch(keyword=kw, found_in_resume=False, category=cat)
        for kw, cat in sorted(keywords.items())
    ]


def check_sections(content: str) -> Tuple[List[str], List[str]]:
    """Check which standard sections are present."""
    found: Set[str] = set()
    lines = content.split('\n')

    for line in lines:
        for pattern, section_name in SECTION_PATTERNS:
            if pattern.match(line):
                found.add(section_name)
                break

    missing = REQUIRED_SECTIONS - found
    return sorted(found), sorted(missing)


def check_ats_issues(content: str) -> List[ATSIssue]:
    """Check for common ATS compatibility issues."""
    issues: List[ATSIssue] = []
    lines = content.split('\n')

    # Track if we've already flagged certain issues (to avoid duplicates)
    flagged_table = False
    special_char_lines: List[int] = []

    for i, line in enumerate(lines, 1):
        # Tables (ATS often can't parse these)
        if not flagged_table and '|' in line and line.count('|') >= 2:
            issues.append(ATSIssue(
                category="formatting",
                issue="Table formatting detected",
                suggestion="Convert tables to simple lists - ATS may not parse tables correctly",
                severity="medium",
                line_number=i
            ))
            flagged_table = True

        # Excessive special characters (limit to first 3 occurrences)
        special_chars = re.findall(r'[^\w\s.,;:\'\"()\-/@#&]', line)
        if len(special_chars) > 5 and len(special_char_lines) < 3:
            issues.append(ATSIssue(
                category="formatting",
                issue=f"Excessive special characters",
                suggestion="Reduce special characters - ATS may misparse them",
                severity="low",
                line_number=i
            ))
            special_char_lines.append(i)

    # Check for images/graphics references
    if re.search(r'!\[.*\]\(.*\)', content):
        issues.append(ATSIssue(
            category="formatting",
            issue="Image references detected",
            suggestion="Remove images - ATS cannot read graphics",
            severity="high"
        ))

    # Check for contact info
    has_email = bool(re.search(r'[\w.-]+@[\w.-]+\.\w+', content))
    has_phone = bool(re.search(r'[\(]?\d{3}[\).\-\s]?\d{3}[\-.\s]?\d{4}', content))
    has_linkedin = bool(re.search(r'linkedin\.com/in/', content, re.IGNORECASE))

    if not has_email:
        issues.append(ATSIssue(
            category="contact",
            issue="No email address found",
            suggestion="Add a professional email address",
            severity="high"
        ))

    if not has_phone:
        issues.append(ATSIssue(
            category="contact",
            issue="No phone number found",
            suggestion="Add a phone number",
            severity="medium"
        ))

    if not has_linkedin:
        issues.append(ATSIssue(
            category="contact",
            issue="No LinkedIn profile found",
            suggestion="Add LinkedIn URL for professional presence",
            severity="low"
        ))

    # Check for dates in experience
    date_patterns = [
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}',
        r'\b\d{1,2}/\d{4}\b',
        r'\b\d{4}\s*[-–—]\s*(Present|Current|\d{4})\b',
        r'\b(19|20)\d{2}\s*[-–—]\s*(Present|Current|(19|20)\d{2})\b',
    ]
    has_dates = any(re.search(p, content, re.IGNORECASE) for p in date_patterns)

    if not has_dates:
        issues.append(ATSIssue(
            category="content",
            issue="No date ranges found in experience",
            suggestion="Add dates to all positions (e.g., 'Jan 2020 - Present')",
            severity="high"
        ))

    # Check resume length (word count)
    words = len(re.findall(r'\b\w+\b', content))
    if words < MIN_WORDS:
        issues.append(ATSIssue(
            category="content",
            issue=f"Resume too short ({words} words)",
            suggestion=f"Add more detail - aim for {IDEAL_MIN_WORDS}-{IDEAL_MAX_WORDS} words",
            severity="medium"
        ))
    elif words > MAX_WORDS:
        issues.append(ATSIssue(
            category="content",
            issue=f"Resume may be too long ({words} words)",
            suggestion=f"Consider condensing - aim for {IDEAL_MIN_WORDS}-{IDEAL_MAX_WORDS} words for most roles",
            severity="low"
        ))

    # Check for bullet points (ATS prefers them)
    bullet_count = len(re.findall(r'^[\s]*[-•*]\s', content, re.MULTILINE))
    if bullet_count < MIN_BULLET_POINTS:
        issues.append(ATSIssue(
            category="formatting",
            issue=f"Few bullet points detected ({bullet_count})",
            suggestion="Use bullet points for achievements - easier for ATS and humans to parse",
            severity="medium"
        ))

    return issues


def match_keywords(resume: str, keyword_matches: List[KeywordMatch]) -> List[KeywordMatch]:
    """Check which job description keywords appear in resume."""
    resume_lower = resume.lower()

    for km in keyword_matches:
        keyword_lower = km.keyword.lower()
        # Use word boundary for accurate matching
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
        found = bool(re.search(pattern, resume_lower, re.IGNORECASE))

        km.found_in_resume = found

        if found:
            # Find the line containing the keyword for context
            for line in resume.split('\n'):
                if re.search(pattern, line, re.IGNORECASE):
                    km.context = line.strip()[:100]
                    break

    return keyword_matches


def calculate_score(issues: List[ATSIssue], keyword_matches: List[KeywordMatch],
                    sections_missing: List[str]) -> float:
    """Calculate overall ATS compatibility score (0.0 - 1.0)."""
    score = 100.0

    # Deduct for issues by severity
    for issue in issues:
        score -= SEVERITY_DEDUCTIONS.get(issue.severity, 5)

    # Deduct for missing sections
    score -= len(sections_missing) * MISSING_SECTION_DEDUCTION

    # Deduct for missing keywords (if JD provided)
    if keyword_matches:
        matched = sum(1 for m in keyword_matches if m.found_in_resume)
        match_rate = matched / len(keyword_matches)
        score -= (1 - match_rate) * KEYWORD_MISMATCH_MAX_DEDUCTION

    return max(0.0, min(100.0, score)) / 100.0


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
        description="Check ATS (Applicant Tracking System) compatibility of resume",
        epilog="Example: python ats_compatibility.py resume.md job_description.md --json"
    )
    parser.add_argument("resume", help="Path to resume file")
    parser.add_argument("job_description", nargs="?", help="Path to job description file (optional)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Read resume
    resume_content, error = validate_and_read_file(args.resume)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    # Read job description if provided
    keyword_matches: List[KeywordMatch] = []
    if args.job_description:
        jd_content, jd_error = validate_and_read_file(args.job_description)
        if jd_error:
            print(f"Warning: {jd_error}", file=sys.stderr)
        else:
            keyword_matches = extract_keywords_from_jd(jd_content)
            keyword_matches = match_keywords(resume_content, keyword_matches)

    # Run checks
    issues = check_ats_issues(resume_content)
    sections_found, sections_missing = check_sections(resume_content)

    # Add missing section issues
    for section in sections_missing:
        issues.append(ATSIssue(
            category="sections",
            issue=f"Missing '{section}' section",
            suggestion=f"Add a {section} section - ATS systems look for standard sections",
            severity="high"
        ))

    score = calculate_score(issues, keyword_matches, sections_missing)

    # Output
    if args.json:
        output = {
            "file": args.resume,
            "score": round(score, 2),
            "sections_found": sections_found,
            "sections_missing": sections_missing,
            "issues": [
                {
                    "category": i.category,
                    "issue": i.issue,
                    "suggestion": i.suggestion,
                    "severity": i.severity,
                    "line": i.line_number
                }
                for i in issues
            ],
            "keyword_analysis": {
                "total_keywords": len(keyword_matches),
                "matched": sum(1 for m in keyword_matches if m.found_in_resume),
                "match_rate": round(sum(1 for m in keyword_matches if m.found_in_resume) / len(keyword_matches), 2) if keyword_matches else None,
                "by_category": {},
                "missing": [m.keyword for m in keyword_matches if not m.found_in_resume],
                "found": [
                    {"keyword": m.keyword, "category": m.category, "context": m.context}
                    for m in keyword_matches if m.found_in_resume
                ]
            } if keyword_matches else None
        }

        # Add by_category breakdown
        if keyword_matches:
            by_cat: Dict[str, Dict[str, int]] = {}
            for m in keyword_matches:
                if m.category not in by_cat:
                    by_cat[m.category] = {"total": 0, "matched": 0}
                by_cat[m.category]["total"] += 1
                if m.found_in_resume:
                    by_cat[m.category]["matched"] += 1
            output["keyword_analysis"]["by_category"] = by_cat

        print(json.dumps(output, indent=2))
    else:
        print(f"ATS Compatibility Analysis: {args.resume}")
        print(f"{'=' * 50}")
        print(f"ATS Score: {score:.0%}")
        print()

        print(f"Sections Found: {', '.join(sections_found) if sections_found else 'None detected'}")
        if sections_missing:
            print(f"Sections Missing: {', '.join(sections_missing)}")
        print()

        if issues:
            print("Issues Found:")
            print("-" * 50)
            # Sort by severity
            severity_order = {"high": 0, "medium": 1, "low": 2}
            for issue in sorted(issues, key=lambda x: severity_order.get(x.severity, 3)):
                line_info = f" (line {issue.line_number})" if issue.line_number else ""
                print(f"\n[{issue.severity.upper()}] {issue.category.title()}{line_info}")
                print(f"  Issue: {issue.issue}")
                print(f"  Fix: {issue.suggestion}")

        if keyword_matches:
            print()
            print("Keyword Analysis (from Job Description):")
            print("-" * 50)
            matched = [m for m in keyword_matches if m.found_in_resume]
            missing = [m for m in keyword_matches if not m.found_in_resume]

            match_rate = len(matched) / len(keyword_matches) if keyword_matches else 0
            print(f"Match Rate: {len(matched)}/{len(keyword_matches)} ({match_rate:.0%})")

            if matched:
                print(f"\nFound ({len(matched)}): {', '.join(m.keyword for m in matched[:15])}")
                if len(matched) > 15:
                    print(f"  ... and {len(matched) - 15} more")

            if missing:
                print(f"\nMissing ({len(missing)}): {', '.join(m.keyword for m in missing[:15])}")
                if len(missing) > 15:
                    print(f"  ... and {len(missing) - 15} more")
                print("\nConsider adding these keywords if you have the relevant experience.")


if __name__ == "__main__":
    main()
