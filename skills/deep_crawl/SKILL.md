---
name: deep_crawl
description: Orchestrates recursive, prioritized deep crawling across the National University (NU) web ecosystem.
---

# Deep Crawl Skill

## Overview
This skill governs autonomous, reliable, and resumable deep crawling of the National University (NU) portal ecosystem (`nu.ac.bd` and approved subdomains).

## Responsibilities
- Decides crawl strategy and parameters (`max_pages`, `max_depth`, `concurrency`, `delay_seconds`).
- Priority-driven URL scheduling (Notices: 100, Admission: 95, Exam: 95, Results: 95, Documents: 85, General: 40).
- Initiates document discovery and text extraction for PDFs, circulars, and syllabi.
- Manages crawl state lifecycle (`running`, `paused`, `completed`, `stopped`, `failed`).
- Employs incremental change detection via SHA-256 hashing to avoid redundant embeddings.

## Tool Invocation (via Crawler MCP)
1. `crawler_start_crawl(start_url, max_pages, max_depth, concurrency)`
2. `crawler_get_status(job_id)`
3. `crawler_get_website_map()`
4. `crawler_retry_failed()`
