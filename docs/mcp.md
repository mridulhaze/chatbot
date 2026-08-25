# Model Context Protocol (MCP) Architecture

## Overview
The National University AI Assistant exposes controlled, typed tools via modular MCP Servers under `mcp_servers/`:
1. `mcp_servers/token_mcp/server.py`: Token database operations, status changes, solver assignments.
2. `mcp_servers/knowledge_mcp/server.py`: Official NU website knowledge, notices, examination schedules.
3. `mcp_servers/document_mcp/server.py`: Official forms, syllabi, PDF document text retrieval.

## MCP Standard Tool Response Format
Every MCP tool returns a structured JSON dictionary:
```json
{
  "success": true,
  "data": {
    "token_id": "NU-2026-000123",
    "status": "PENDING"
  },
  "error": null
}
```

Error format:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "TOKEN_NOT_FOUND",
    "message": "Token was not found in database."
  }
}
```

## Security Rules
- **Zero Arbitrary SQL**: No `execute_sql()` or AI-generated SQL execution is permitted.
- **Input Validation**: All arguments are strictly validated using Pydantic schemas.
- **Auditing**: All tool calls are automatically logged with timestamp and arguments in `audit_logs`.
