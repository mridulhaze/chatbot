---
name: admission
version: 1.0.0
description: Delivers official admission eligibility, merit lists, release slip instructions, quota requirements, and circulars for National University.
---

# National University Admission Skill

## Purpose
Provide comprehensive guidance on Honours, Degree Pass, Masters, and Professional admissions, release slip rules, college transfer quotas, and application deadlines.

## Trigger Conditions
Activate this skill whenever:
1. User inquires about "Admission", "ভর্তি", "Merit List", "মেধা তালিকা", "Release Slip", "রিলিজ স্লিপ", "Migration", "মাইগ্রেশন".
2. User asks about GPA requirements, application fees, or college subject choice.

## Available MCP Tools
- `search_admission_information`: Searches verified admission circulars and guidelines.
- `search_notice`: Searches official admission announcements.
- `get_page`: Retrieves app1/admission portal guide details.

## Conversational Workflow
1. Detect admission program (Honours, Degree, Masters, B.Ed, etc.).
2. Query `search_admission_information(query)` to fetch current circular or criteria.
3. Clearly summarize minimum SSC/HSC GPA eligibility, application timeline, and release slip policies.
4. Link directly to the official admission portal (`app1.nu.edu.bd`).
