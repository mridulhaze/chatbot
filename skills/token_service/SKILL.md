---
name: token_service
version: 1.0.0
description: Manages student and user support requests, issue resolution, similar solved case retrieval, and support token tracking for National University.
---

# Token Service Skill

## Purpose
Manage user support requests for National University academic and administrative portals (Form Fill-up, EMS, TC, Rescrutiny, Certificate, Marksheet, Registration, Admission, Results, and others).

## Trigger Conditions
Activate this skill whenever:
1. User mentions or selects "Token Service", "Support Ticket", "সাপোর্ট টোকেন", "টোকেন সেবা".
2. User provides or inquires about a Token ID formatted like `NU-YYYY-XXXXXX` (e.g. `NU-2026-000123`).
3. User describes a personal academic issue or difficulty (e.g. "I cannot login to EMS", "Payment completed but form fill-up pending", "Certificate correction status").
4. User clicks any Service Action Card in the UI (e.g. [ EMS ], [ Form Fill-up ], [ TC ]).

## Available MCP Tools
- `get_services`: Returns active support service types dynamically.
- `create_token`: Atomically creates a support token request.
- `get_token_status`: Returns public status, solver department, and resolution message.
- `get_token_history`: Returns status change timeline.
- `search_similar_solved_problems`: Retrieves anonymized previously solved cases using semantic similarity.

## Conversational Workflow
1. **Detect Intent & Parameters**:
   - If user provided a specific `Token ID`, immediately query `get_token_status(token_id)` and present the formatted status card.
   - If user states a problem without selecting a service, inspect if the problem implies a service (e.g. "EMS login" -> EMS). If ambiguous, call `get_services()` and present the service selection buttons.
2. **Search Similar Solved Knowledge**:
   - Before creating a new token, invoke `search_similar_solved_problems(service_code, problem, limit=3)`.
   - If high-confidence match found (score >= 0.75), display the anonymized common solution clearly marked as **"পূর্ববর্তী সমাধান রেকর্ড (Previous Solved Case)"**.
   - Then offer interactive confirmation:
     - `[ Create Support Token ]` / `[ নতুন টোকেন তৈরি করুন ]`
     - `[ Problem Resolved / Cancel ]` / `[ সমাধান পেয়েছি ]`
3. **Token Creation on User Request**:
   - When the user confirms token creation, call `create_token(service_code, problem, user_name, user_phone, registration_no)`.
   - Return the generated **Token ID** (`NU-YYYY-XXXXXX`), current status (`🟡 PENDING`), and clear instructions on how to track it.
4. **Token Status Inquiry**:
   - When user enters `NU-YYYY-XXXXXX`, call `get_token_status(token_id)`.
   - Present status badge, responsible solver desk, submission date, and if resolved, the official solution.

## Privacy & Security Guardrails
- **NEVER** expose other users' names, phone numbers, emails, or registration numbers.
- **NEVER** expose internal admin notes or private solver communications to regular users or public AI responses.
- All similar solved problems returned by MCP tools MUST be sanitized and anonymized.
- Only return official department names and public resolution instructions.
