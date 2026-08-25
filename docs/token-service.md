# Token Service & Support Ticket System

## Overview
The Token Service provides students and users with a traceable academic support ticketing system for National University services.

## Supported Services
- `FORM_FILLUP`: Examination form fill-up, payment, and submission issues.
- `TC`: College transfer certificate application and approval.
- `RESCRUTINY`: Answer sheet re-scrutiny applications.
- `EMS`: EMS portal login, account credentials, and college access.
- `CERTIFICATE`: Original and provisional certificate processing.
- `MARKSHEET`: Marksheet verification, correction, and duplicates.
- `REGISTRATION`: Student registration card correction.
- `ADMISSION`: Admission release slip, quota, and merit lists.
- `RESULT`: Withheld results, CGPA recalculation, and promotion.
- `OTHER`: General academic or administrative inquiries.

## Atomic ID Generation
Token IDs are generated using an atomic sequence counter:
Format: `NU-YYYY-000001` (e.g. `NU-2026-000075`).

## Strict Lifecycle State Machine
```text
PENDING ───► ASSIGNED ───► PROCESSING ───► SOLVED ───► CLOSED
   │             │             │
   └─────────────┴─────────────┴───► REJECTED
```

## Anonymized Solved Problem Knowledge Base
When an admin/solver solves a token with `solve_token(token_id, solve_message)`:
1. The solver message is saved to the database.
2. The problem and solution are anonymized (all user PII is stripped).
3. The anonymized record is indexed into the Chroma vector database.
4. Future students asking similar questions receive the verified resolution immediately.
