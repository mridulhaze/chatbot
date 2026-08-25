# Security Model & Role-Based Access Control (RBAC)

## User Roles
1. **`USER`**: Can create tokens, view own token status, and search public knowledge.
2. **`SOLVER`**: Can view assigned tokens, update status to PROCESSING, write solutions, and resolve tokens.
3. **`ADMIN`**: Can view all tokens, assign solvers, update services, manage solvers, and inspect audit logs.
4. **`SUPER_ADMIN`**: Full administrative access including user management and system settings.

## PII & Privacy Protection
- Public endpoints and AI responses never expose student phone numbers, emails, or registration numbers.
- `admin_note` fields are strictly restricted to authorized staff and are never provided to public AI contexts.
- Solved knowledge indexing anonymizes all problem descriptions prior to vector embedding.

## SQL Safety
- AI models have **zero direct SQL execution access**.
- All queries are parameterized via SQLAlchemy ORM and prepared SQLite/Postgres statements.
