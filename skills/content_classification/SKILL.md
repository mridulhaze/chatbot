---
name: content_classification
description: Categorizes discovered web pages and documents into official NU academic domains and assigns crawl priorities.
---

# Content Classification Skill

## Overview
Classifies incoming content streams using multi-signal heuristics (URL structure, title, header tags, and body content keywords).

## Categories & Priorities
1. **NOTICE** (Priority 100): Urgent official announcements, office orders, general circulars.
2. **ADMISSION** (Priority 95): Undergraduate, postgraduate, and professional intake guidelines.
3. **EXAMINATION** (Priority 95): Exam dates, form fill-up deadlines, admit card instructions, center lists.
4. **RESULT** (Priority 95): Published GPA/CGPA results, grade sheets, re-scrutiny windows.
5. **FORM_FILLUP** (Priority 90): Online application instructions, fee payment slips, registration forms.
6. **DOCUMENT** (Priority 85): Official downloadable PDF and document files.
7. **ACADEMIC** (Priority 70): Course curricula, syllabi, academic calendars.
8. **ADMINISTRATION** (Priority 60): Officer directories, contact numbers, departmental desks.
9. **COLLEGE** (Priority 50): Affiliated college affiliation and management info.
10. **GENERAL** (Priority 40): General informational pages.
