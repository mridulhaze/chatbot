# REST API & MCP Endpoints Reference

## 1. Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register`: Register new user account.
- `POST /api/v1/auth/login`: Authenticate and receive JWT Bearer token.
- `GET /api/v1/auth/me`: Get current authenticated user profile.

## 2. AI Orchestrator & Skills Chat (`/api/v1/chat` & `/api/chat`)
- `POST /api/v1/chat`: Multi-turn conversational endpoint powered by Skills & MCP tools.

## 3. Public Token Endpoints (`/api/v1/tokens`)
- `GET /api/v1/tokens/services`: List active dynamic support services.
- `POST /api/v1/tokens/create`: Create a support ticket.
- `GET /api/v1/tokens/status/{token_id}`: Query public token status badge.
- `GET /api/v1/tokens/similar-solved`: Query anonymized similar solved cases.

## 4. Admin & Solver Endpoints (`/api/v1/admin`)
- `GET /api/v1/admin/dashboard-stats`: Real-time token metrics.
- `GET /api/v1/admin/tokens`: Filter tokens by status, service, solver.
- `GET /api/v1/admin/tokens/{token_id}`: Detailed token view.
- `POST /api/v1/admin/tokens/{token_id}/assign`: Assign token to department solver.
- `POST /api/v1/admin/tokens/{token_id}/status`: Transition token status.
- `POST /api/v1/admin/tokens/{token_id}/solve`: Submit verified solution.
- `GET /api/v1/admin/audit-logs`: Inspect immutable system audit logs.

## 5. Model Context Protocol (`/api/v1/mcp`)
- `POST /api/v1/mcp/invoke`: Direct execution of typed MCP tools.
