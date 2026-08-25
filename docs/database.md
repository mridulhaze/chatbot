# Database Architecture & Pluggable Engine

## Relational Database
The platform uses environment-driven database configuration via SQLAlchemy:
- **Default / Development**: SQLite (`data/nu_tokens.db`, `data/nu_assistant.db`)
- **Production**: PostgreSQL (`postgresql+psycopg2://user:pass@host:5432/nu_assistant`)

To connect PostgreSQL:
```env
DATABASE_URL=postgresql+psycopg2://nu_admin:secret@localhost:5432/nu_assistant
```

## Tables
1. `token_service_types`: Dynamic service categories.
2. `token_solvers`: Responsible departments and solver contacts.
3. `token_requests`: Core support tokens with status and priority.
4. `token_history`: Chronological audit trail of all status transitions.
5. `token_attachments`: Uploaded documents and evidence.
6. `token_sequences`: Concurrency-safe atomic counter per calendar year.
7. `users`: System users, solvers, and administrators.
8. `audit_logs`: Immutable audit trails for all operations.

## Vector Database
The vector storage layer is pluggable:
- `chroma`: Local ChromaDB vector storage (`nu_vector_db/`)
- `pgvector`: PostgreSQL vector extension
- `qdrant`: Distributed vector database
