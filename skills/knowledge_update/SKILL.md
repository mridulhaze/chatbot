---
name: knowledge_update
description: Handles incremental RAG synchronization, chunk generation, and vector index invalidation when content changes.
---

# Knowledge Update & RAG Synchronization Skill

## Overview
Ensures that the AI Assistant's ChromaDB Vector Store and SQLite Knowledge Base accurately reflect the live state of National University.

## Lifecycle
1. **Hash Verification**: Compares incoming SHA-256 content hash with existing hash.
2. **If Unchanged**: Updates timestamp, skipping expensive re-embedding.
3. **If Changed / New**:
   - Updates page/document records in SQLite.
   - Chunks text into semantic blocks preserving titles and sections.
   - Indexes chunks into ChromaDB vector knowledge base.
   - Logs change history and triggers notice sync.
4. **Source Attribution**: Retains exact source URLs and publication dates for citation generation.
