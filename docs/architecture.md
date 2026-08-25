# National University AI Assistant Platform — High-Level Architecture

## Overview
The National University (NU) AI Assistant Platform is an enterprise-grade AI architecture that cleanly separates AI behavioral logic (Skills), controlled data access (MCP Servers), official university knowledge retrieval (RAG Engine & Scrapers), and student issue tracking (Token Service).

```text
                         ┌──────────────────────────────┐
                         │       USER / STUDENT         │
                         └───────────────┬──────────────┘
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │       AI CHAT INTERFACE      │
                         │   Web / Mobile / Embed Widget │
                         └───────────────┬──────────────┘
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │        AI ORCHESTRATOR        │
                         │  • Intent & Entity Detection │
                         │  • Skill Selection           │
                         │  • Context & State Tracking  │
                         │  • MCP Tool Execution        │
                         └───────────────┬──────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
             ┌────────────┐      ┌──────────────┐     ┌─────────────┐
             │   SKILLS   │      │ MCP SERVERS  │     │    RAG      │
             └────────────┘      └──────────────┘     └─────────────┘
                    │                    │                    │
          ┌─────────┼─────────┐    ┌─────┼──────┐            │
          │         │         │    │     │      │            │
          ▼         ▼         ▼    ▼     ▼      ▼            ▼
       NU Skill  Token Skill Exam  Token  NU   Document   Vector DB
                                  MCP   MCP    MCP
                                    │
                                    ▼
                             Token Database
```

## Fundamental Architectural Principles
1. **AI Skills (`skills/`)**: Dictates *what the AI should do* (conversational workflows, decisions, prompt templates, privacy guardrails).
2. **MCP Servers (`mcp_servers/`)**: Controls *what tools and data the AI can access* via typed, restricted interfaces with **zero arbitrary SQL queries**.
3. **Token Service**: Provides atomic sequence generation (`NU-YYYY-000001`), state machine validation, solver assignment, and anonymized solved case indexing.
4. **Official NU RAG**: Queries crawled pages, notices, departments, and syllabi from the official website without mingling with support tickets.
5. **Zero PII Exposure**: Private contact details and internal solver notes are strictly isolated and never leaked into public AI prompts.
