---
name: interview-prep
description: 'Generate interview questions for a given role and experience level. Use when preparing for a technical interview, creating interview question sets, or practicing interview skills. Accepts role and years of experience as parameters. Produces 5 technical and 5 behavioural questions tailored to the role and seniority.'
argument-hint: '<role> <years of experience>'
---

# Interview Prep

## When to Use
- Preparing technical interview questions for a specific role
- Practising behavioural interview responses
- Creating question sets matched to a acandidate's seniority level

## Parameters
- **Role**: The job title or position (e.g. Frontend Developer, Data Scientist, DevOps Engineer)
- **Years of experience**: Number of years of relevant professional experience

## Procedure

Given the `role` and `years of experience` provided by the user:

1. Determine the seniority level from experience:
   - 0–2 years → Junior
   - 3–5 years → Mid-level
   - 6–9 years → Senior
   - 10+ years → Principal / Staff / Lead

2. Generate **5 technical interview questions** that:
   - Are specific to the technologies, tools, and concepts core to the `role`
   - Match the depth and complexity expected at the determined seniority level
   - Progress from foundational to advanced where appropriate

3. Generate **5 behavioural interview questions** that:
   - Use the STAR-method format (Situation, Task, Action, Result)
   - Reflect the scope of responsibility expected at the seniority level
   - Cover themes such as collaboration, conflict resolution, ownership, and growth

## Output Format

Return **only** the questions in the following numbered format — no preamble, no explanations:

**Technical Questions**
1. ...
2. ...
3. ...
4. ...
5. ...

**Behavioural Questions**
1. ...
2. ...
3. ...
4. ...
5. ...
