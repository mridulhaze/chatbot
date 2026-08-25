---
name: examination
version: 1.0.0
description: Provides examination schedules, form fill-up timelines, admit cards, exam centers, and rescrutiny policies for National University.
---

# National University Examination Skill

## Purpose
Guide students through Honours, Degree Pass, Masters, and Professional examination schedules, form fill-up circulars, rescrutiny applications, and exam centers.

## Trigger Conditions
Activate this skill whenever:
1. User mentions "Exam", "Examination", "পরীক্ষা", "রুটিন", "Routine", "Form Fill-up", "ফরম পূরণ", "Rescrutiny", "খাতা পুনঃনিরীক্ষণ".
2. User asks about exam postponement, center lists, or admit card downloads.

## Available MCP Tools
- `search_exam_information`: Searches examination notices, routines, and schedules.
- `search_notice`: Searches recent controller of examination notices.
- `get_services`: Provides form fillup and rescrutiny support services if student faces issues.

## Conversational Workflow
1. Identify course and year (e.g. Honours 1st Year, Degree 2nd Year, Masters Final).
2. Query `search_exam_information(query)` to find active circulars or schedules.
3. If an official notice exists, present the dates, deadlines, and official links.
4. If the student reports an issue with their form fill-up payment or fee slip, guide them to the **Token Service (Form Fill-up)**.
