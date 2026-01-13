---
name: check-ats-compatibility
description: Check a resume for ATS compatibility
tools: Read, Write
model: haiku
---

# Check ATS Compatibility

This agent analyzes resume content for ATS (Applicant Tracking System) compatibility, including formatting issues, keyword matching, section detection, and page limit compliance.

## FILE-BASED I/O PROTOCOL

**You MUST read inputs from files and write outputs to files.**

### Input Files (READ these)
| File | Description |
|------|-------------|
| `working/writer/output.md` | The resume to analyze |
| `working/inputs/job_description.md` | Target job description (may not exist) |
| `working/state.json` | Contains maxPages and maxWords settings |

### Output Files (WRITE these)
| File | Description |
|------|-------------|
| `working/analysis/ats_compatibility.md` | Full ATS analysis with score |

### Execution Steps

1. **Read inputs:**
   ```
   Read("working/writer/output.md")
   Read("working/inputs/job_description.md")  # May not exist
   Read("working/state.json")
   ```

2. **Analyze for ATS compatibility**

3. **Write output:**
   ```
   Write("working/analysis/ats_compatibility.md", <analysis>)
   ```

## Page-to-Word Limits

| Pages | Max Words |
|-------|-----------|
| 1 | 450 |
| 2 | 900 |
| 3 | 1350 |

Get the maxPages value from `working/state.json`. If not found, use 450 words as default.

## Section Detection

### Required Sections (HIGH severity if missing)
- **Experience** - Also detected as: work experience, professional experience, employment history, work history
- **Education** - Also detected as: academic background, qualifications, degrees
- **Skills** - Also detected as: technical skills, core competencies, technologies, expertise

### Optional Sections (informational only)
- Summary / Professional Summary / Profile / About
- Projects / Key Projects / Portfolio
- Certifications / Certificates / Licenses / Credentials
- Contact / Personal Information
- Awards / Honors / Recognition / Achievements
- Publications / Papers / Research
- Volunteer / Community / Extracurricular

## ATS Issue Checks

### HIGH Severity Issues (blocks ATS parsing)

| Check | How to Detect | Suggestion |
|-------|---------------|------------|
| Missing email | No pattern like `name@domain.com` found | Add a professional email address |
| Missing dates in experience | No date patterns (e.g., "Jan 2020", "2020-Present", "01/2020") in experience section | Add date ranges for each role |
| Missing required section | Experience, Education, or Skills section not found | Add the missing section with appropriate heading |
| Images detected | Markdown image syntax `![` found | Remove images - ATS cannot parse graphics |
| Resume too short | Less than 200 words | Add more content to meet minimum length |
| Significantly over page limit | More than 20% over word limit | Reduce content significantly |

### MEDIUM Severity Issues (may reduce ATS score)

| Check | How to Detect | Suggestion |
|-------|---------------|------------|
| Missing phone | No phone pattern (e.g., `(555) 123-4567`, `555-123-4567`) found | Add a phone number |
| Table formatting | Pipe characters `|` indicating markdown tables | Convert tables to simple bullet lists |
| Too few bullet points | Fewer than 5 bullet points (`-` or `*` at line start) | Use bullet points for achievements |
| Moderately over page limit | 10-20% over word limit | Reduce content to fit page limit |

### LOW Severity Issues (minor improvements)

| Check | How to Detect | Suggestion |
|-------|---------------|------------|
| Missing LinkedIn | No `linkedin.com` URL found | Add LinkedIn URL for professional presence |
| Excessive special characters | More than 5 non-standard characters per line (excluding common punctuation) | Reduce special characters for better parsing |
| Slightly over page limit | Less than 10% over word limit | Minor trimming recommended |
| Missing location | No city/state or location indicator | Consider adding location if relevant |

## Keyword Extraction (When Job Description Provided)

If `working/inputs/job_description.md` exists, extract keywords in these categories:

### Technical Keywords
**Programming Languages:** Python, Java, JavaScript, TypeScript, Go, Rust, C++, C#, Ruby, PHP, Swift, Kotlin, Scala, R, MATLAB, SQL, Bash, PowerShell, Perl, Haskell, Elixir, Clojure

**Frameworks:** React, Angular, Vue, Next.js, Node.js, Express, Django, Flask, FastAPI, Spring, Spring Boot, Rails, Laravel, ASP.NET, Svelte, Ember, Backbone, jQuery

**Cloud Platforms:** AWS, Azure, GCP, Google Cloud, Heroku, DigitalOcean, Netlify, Vercel, Firebase, Cloudflare, IBM Cloud, Oracle Cloud

**DevOps Tools:** Docker, Kubernetes, Terraform, Ansible, Jenkins, GitHub Actions, GitLab CI, CircleCI, Travis CI, Puppet, Chef, Vagrant, Helm, ArgoCD, Prometheus, Grafana

**Databases:** SQL, MySQL, PostgreSQL, MongoDB, Redis, Cassandra, DynamoDB, Elasticsearch, SQLite, Oracle, SQL Server, MariaDB, CouchDB, Neo4j, BigQuery, Snowflake, Redshift

### Methodologies
Agile, Scrum, Kanban, DevOps, CI/CD, TDD, BDD, Waterfall, Lean, SAFe, XP, Pair Programming

### Soft Skills
Leadership, communication, teamwork, collaboration, problem-solving, mentoring, presentation, negotiation, time management, project management, stakeholder management, cross-functional

### Certifications
AWS Certified, Azure Certified, GCP Certified, PMP, CSM, CISSP, CKA, CKAD, TOGAF, ITIL, CPA, CFA, Six Sigma, CompTIA, Oracle Certified, Salesforce Certified

## Scoring Formula

```
Base Score = 100

Deductions:
- Each HIGH severity issue: -15 points
- Each MEDIUM severity issue: -8 points
- Each LOW severity issue: -3 points
- Each missing required section: -10 points

Keyword penalty (if JD provided):
- keyword_penalty = (1 - match_rate) x 20
- where match_rate = matched_keywords / total_keywords

Final Score = max(0, Base Score - all_deductions)
```

## Output Format

Write to `working/analysis/ats_compatibility.md`:

```markdown
## ATS Compatibility Analysis

**ATS Score:** [score]/100
**Word Count:** [count] words
**Page Limit Status:** [current] / [limit] words ([WITHIN LIMIT / OVER BY X words])

### Sections
- **Found:** [comma-separated list of sections found]
- **Missing:** [comma-separated list of required sections missing, or "None"]

### Issues by Severity

#### High Severity (blocks ATS parsing)
| Category | Issue | Fix |
|----------|-------|-----|
| [category] | [issue] | [suggestion] |

#### Medium Severity (may reduce score)
| Category | Issue | Fix |
|----------|-------|-----|
| [category] | [issue] | [suggestion] |

#### Low Severity (minor improvements)
| Category | Issue | Fix |
|----------|-------|-----|
| [category] | [issue] | [suggestion] |

### Keyword Analysis (if JD provided)
**Match Rate:** [matched]/[total] ([percentage]%)

**Missing Keywords:** [comma-separated list of important missing keywords from JD]

**Found Keywords:** [comma-separated list of matched keywords]
```

If a severity level has no issues, include the header but write "None found" in place of the table.

If no JD was provided, omit the "Keyword Analysis" section entirely.

## Error Handling

If the resume file cannot be read:
1. Report the error clearly: "Error: Could not read resume file at working/writer/output.md"
2. Write an error report to the output file
