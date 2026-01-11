---
description: Generate interview preparation document from a resume
allowed-tools: Read, Write, Glob, Grep, Edit, Bash, Task
---

# Interview Prep Command

Generate an interview preparation document based on a resume.

## Usage

```
/resume-helper:interview-prep "path/to/resume.md"
/resume-helper:interview-prep  # Uses resume from last completed loop
```

## Instructions

### Step 1: Load Resume

1. If path provided, read the resume file
2. If no path provided:
   - Read `.resume-state.json`
   - Extract `currentResume` from state
   - If no state or no resume, ask user for resume path

### Step 2: Analyze Resume

Invoke the Interviewer agent to generate likely interview questions:

```
You are the Interviewer agent. Analyze this resume and generate comprehensive interview questions.

## Resume
<resume content>

## Task
Generate interview questions that a hiring manager would likely ask based on this resume. For each claim or achievement, create questions that would verify or explore it deeper.

Organize questions by category:
1. Experience verification questions
2. Technical deep-dive questions
3. Behavioral/situational questions
4. Questions about gaps or transitions
5. Questions the candidate should ask the interviewer
```

### Step 3: Generate Prep Document

Create `interview_prep.md` with the following structure:

```markdown
# Interview Preparation Guide

Generated: [date]
Resume: [filename]

## Quick Reference

### Your Key Talking Points
- [Top 3-5 achievements to emphasize]

### Numbers to Remember
| Metric | Value | Context |
|--------|-------|---------|
| Team size | X | Project Y |
| Impact | X% | Achievement Z |
| ... | ... | ... |

## Likely Questions & Suggested Responses

### Experience Verification

**Q: [Question about specific role/achievement]**

*Why they're asking:* [What they want to verify]

*Suggested response framework:*
- Situation: [Context to set]
- Your role: [Clarify your specific contribution]
- Actions: [What you did]
- Result: [Quantified outcome]

*Key points to hit:*
- [Specific detail 1]
- [Specific detail 2]

---

### Technical Deep-Dives

**Q: [Technical question based on resume]**

*Why they're asking:* [What they want to assess]

*Suggested approach:*
- [How to structure your answer]
- [Technical details to include]
- [What to avoid]

---

### Behavioral Questions

**Q: "Tell me about a time when..." [scenario from resume]**

*STAR Response:*
- **Situation:** [Set the scene]
- **Task:** [Your responsibility]
- **Action:** [What you did - be specific]
- **Result:** [Quantified outcome]

---

### Questions About Gaps/Transitions

**Q: [Question about career gap or transition]**

*Suggested response:*
- [Honest, positive framing]
- [What you learned/did during that time]
- [How it makes you stronger for this role]

---

## Red Flags to Address Proactively

If these come up, here's how to handle them:

1. **[Potential concern]**
   - Address by: [suggested approach]

2. **[Potential concern]**
   - Address by: [suggested approach]

---

## Questions YOU Should Ask

Demonstrate engagement and evaluate fit:

### About the Role
- "What does success look like in the first 90 days?"
- "What are the biggest challenges facing the team right now?"

### About the Team
- "How is the team structured?"
- "What's the collaboration style?"

### About Growth
- "What opportunities for growth exist?"
- "How do you support professional development?"

### About the Company
- "What's the company's biggest priority this year?"
- "How would you describe the culture?"

---

## Final Checklist

Before the interview:
- [ ] Review all numbers and metrics in your resume
- [ ] Practice STAR responses for top 3 achievements
- [ ] Prepare 3-5 questions to ask
- [ ] Research the company and interviewer
- [ ] Review the job description again
- [ ] Prepare your "Tell me about yourself" (2-min version)

---

*Good luck! Remember: The best interviews feel like conversations, not interrogations.*
```

### Step 4: Save and Report

1. Write `interview_prep.md` to current directory
2. Display summary:

```
═══════════════════════════════════════════════════
INTERVIEW PREP GENERATED
═══════════════════════════════════════════════════

Output: interview_prep.md

Contents:
- X experience verification questions
- X technical deep-dive questions
- X behavioral questions
- X questions for you to ask
- Key numbers reference card
- Red flag mitigation strategies

Top 3 Questions to Practice:
1. [Most likely question]
2. [Second most likely]
3. [Third most likely]

Review interview_prep.md for full preparation guide.
═══════════════════════════════════════════════════
```

## Notes

- This command can be run independently of the resume loop
- Works best with resumes that have specific, quantified achievements
- Generated questions are based on what a skeptical interviewer would ask
