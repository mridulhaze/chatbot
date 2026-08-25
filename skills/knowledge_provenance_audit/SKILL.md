---
name: knowledge_provenance_audit
description: Maintains machine-readable JSONL audit trails, versioned knowledge manifests, and human-readable Markdown changelogs for inter-agent AI collaboration.
author: National University AI Team
version: 1.0.0
---

# Knowledge Provenance & Audit Skill

## Purpose
The `knowledge_provenance_audit` skill ensures that all autonomous learning and knowledge updates are fully auditable, traceable, and interoperable so secondary AI agents (OpenAI Codex, Claude Code, Antigravity subagents, or external systems) can inspect what was learned and proceed with confidence.

## Standard Artifacts Maintained
1. `data/knowledge_updates.jsonl` — Append-only chronological JSON Lines stream of every knowledge enrichment turn.
2. `data/knowledge_manifest.json` — Machine-readable RFC 8259 JSON manifest detailing database state, version, and statistics.
3. `data/KNOWLEDGE_CHANGELOG.md` — Human- and AI-readable Markdown changelog of recent updates.

## Inter-Agent Integration Standard
Any peer agent or external system can read the latest updates via:
- Reading `data/knowledge_manifest.json`
- Polling MCP Tool: `enrichment_mcp -> get_recent_knowledge_updates(since_timestamp)`
- Calling REST API: `GET /api/v1/enrichment/manifest`
