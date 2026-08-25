# Agent Instructions & Project Memory (National University Bangladesh AI Assistant)

Welcome AI Assistant (OpenAI, Claude, Antigravity).

## Critical Context & Architecture
Please read [`AGENTIC_ARCHITECTURE.md`](file:///e:/projects/AI_CHAT_BOT/AGENTIC_ARCHITECTURE.md) for the exhaustive system architecture, database schemas, role hierarchies, and official portal URLs.

### Essential Rules:
1. **Official URLs:**
   - Student Services (TC, Certificate, Marksheet, Transcript, Correction): `http://103.113.200.68/nu-app/`
   - Admission Portal: `http://app11.nu.edu.bd/`
   - EMS Portal: `http://ems.nu.ac.bd/`
   - Never provide deprecated links (`services.nu.edu.bd` or `103.113.200.36`).

2. **Solver Role Access Control:**
   - Solvers only see the `Token Support Center` tab.
   - Solvers only see tokens assigned to their specific department desk (`Accounts & Sonali Seba Desk`, `ICT Support Team`, etc.).
   - Solvers have 2 actions: `Solve` or `Send Back to Admin (Not Solved)`. Solvers CANNOT reassign tokens.

3. **Super Admin Controls:**
   - Full access across all departments, user creation, system backup/restore, and soft-delete/restore tokens from Trash.

4. **Testing Suite:**
   - Run `python tests/test_token_service_domain.py` to verify domain compliance.
