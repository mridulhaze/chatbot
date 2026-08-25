---
name: continuous_knowledge_enrichment
description: 24/7 autonomous knowledge ingestion, vector store synchronization, deduplication, and dynamic preloaded cache updates.
author: National University AI Team
version: 1.0.0
---

# Continuous Knowledge Enrichment Skill

## Purpose
The `continuous_knowledge_enrichment` skill orchestrates continuous 24/7 background learning. It ingests analyzed QA pairs and summaries into ChromaDB, prevents semantic drift, and injects fresh information into the zero-latency instant response engine.

## Core Capabilities
1. **Deduplicated Vector Ingestion**: Checks existing chunks in ChromaDB before embedding to prevent redundant or stale vector representations.
2. **Instant Preloaded Cache Refresh**: Dynamically adds high-frequency synthesized FAQs into `_CHAT_CACHE` and `INSTANT_LOOKUP_MAP` for sub-millisecond student responses.
3. **Multi-tier Synchronization**: Synchronizes across ChromaDB vector store, SQLite relational tables, and filesystem manifests.

## Execution Rules
- Run automatically every 10–15 minutes via `Autonomous24x7Worker`.
- Ensure all vector chunks retain source citations (`url`, `title`, `section`, `synthesized_at`).
