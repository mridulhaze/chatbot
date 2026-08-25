---
name: result
version: 1.0.0
description: Provides guidelines for examination results, CGPA grading scales, withheld results, and re-evaluation applications.
---

# National University Result Skill

## Purpose
Assist students with published exam results, grading systems (CGPA scale), result correction, withheld (WH) outcomes, and board rescrutiny.

## Trigger Conditions
Activate this skill whenever:
1. User inquires about "Result", "রেজাল্ট", "ফলাফল", "CGPA", "GPA", "Withheld", "স্থগিত", "Improvement", "মানোন্নয়ন".
2. User asks how to check results via SMS or web portal (`nu.ac.bd/results`).

## Available MCP Tools
- `search_exam_information`: Queries published result notifications.
- `search_notice`: Finds recent result circulars.
- `get_services`: Provides support service for result correction and withheld queries.

## Conversational Workflow
1. Provide standard result checking methods (SMS format: `NU <space> H1/H2/H3/H4 <space> Roll/Reg`, and `results.nu.ac.bd`).
2. If result is withheld or missing, explain the official procedure to submit application via college to Controller of Examinations.
3. If student needs follow-up assistance, route to **Token Service (Result Correction / Withheld)**.
