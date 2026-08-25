# National University AI Assistant — High-Impact Performance Optimization Plan

## 1. Objectives & Key Target Metrics

| Metric | Baseline (Current) | Target (Optimized) | Strategy |
| :--- | :--- | :--- | :--- |
| **Greeting / Static Query Latency** | `6,300 ms – 10,060 ms` | **< 10 ms** | Fast Preloaded Knowledge Engine & Memory Router |
| **Token Lookup / Notice Lookup** | `4,300 ms` | **< 30 ms** | Direct SQLite/Token MCP Shortcut routing |
| **Time to First Token (TTFT)** | `10,000 ms – 77,000 ms` | **< 1,200 ms** | Fast Gemini Flash-Lite tier + Server-Sent Events (SSE) Streaming |
| **Complex RAG Total Time** | `18,000 ms – 50,000 ms` | **< 2,200 ms** | Concurrent Data Retrieval + Optimized Model Config |
| **API Failure Rate / Retries** | Frequent 404/503 fallback pauses | **0% Fallback Cascades** | Standardized verified Google GenAI models (`gemini-3.1-flash-lite`, `gemini-3.5-flash-lite`) |

---

## 2. Architectural Transformations

### Phase 1: Fast Intent Routing & Instant Short-Circuit Engine
1. **Greetings & Welcome Flows:**
   - Detect greeting intents ("hi", "hello", "সালাম", "নমস্কার", "শুভ সকাল") in `< 0.1ms`.
   - Return welcoming message with official quick-action buttons directly from memory. Zero RAG, zero embeddings, zero LLM calls.
2. **Token Management & Status Queries:**
   - Detect `NU-YYYY-XXXXXX` token IDs and "check token status" queries.
   - Fetch directly from Token SQLite database in `< 5ms`.
   - Return structured status cards immediately.
3. **Recent Official Notices:**
   - Queries requesting "latest notices", "recent circulars" fetch top 5 notices directly from SQLite in `< 3ms` without LLM invocation.

### Phase 2: High-Performance Concurrent Data Retrieval (RAG Parallelization)
When a generative answer is genuinely required (e.g. syllabus guidelines, complex exam rules, grading systems):
1. **Single Embedding Generation:**
   - Generate embedding once per query and reuse across both Chroma DB search and Solved Cases vector similarity.
2. **Asynchronous Parallel Execution (`asyncio.gather` / `ThreadPoolExecutor`):**
   - Execute SQLite FAQ lookup, Chroma Vector similarity search, and Solved Cases lookup concurrently.
   - Reduces context retrieval time from `7,000ms+` down to `~400ms`.
3. **In-Memory Embedding & Query Cache (TTL + LRU):**
   - Cache common query embeddings and identical queries for 5–15 minutes.

### Phase 3: Model Tier Tuning & Verified Configuration
1. Update `backend/config.py` and `backend/core/config.py`:
   - Primary: `gemini-3.1-flash-lite` (Measured generation: **~1.1s**, TTFT: **~1.2s**).
   - Fallback 1: `gemini-3.5-flash-lite` (Measured generation: **~980ms**).
   - Fallback 2: `gemini-3-flash-preview`.
   - Remove obsolete/deprecated models (`gemini-2.5-flash`, `gemini-3.6-flash`).

### Phase 4: Server-Sent Events (SSE) Token Streaming Pipeline
1. **Backend Streaming Endpoint (`/api/chat/stream` & `/api/v1/chat/stream`):**
   - Implemented via `fastapi.responses.StreamingResponse(media_type="text/event-stream")`.
   - Generates stream events:
     - `event: status` (Immediate acknowledgment, e.g. "তথ্য যাচাই করা হচ্ছে...")
     - `event: token` (Word-by-word streaming from `client.models.generate_content_stream`)
     - `event: citations` (Official portal links and verified sources)
     - `event: chips` (Contextual quick buttons)
     - `event: done` (Execution duration, token count, timestamp)
2. **Frontend Progressive Rendering (`static/index.html` & `static/widget.js`):**
   - Consume SSE stream using `fetch()` with `ReadableStream` / `TextDecoder`.
   - Render markdown progressively as tokens stream in.
   - Display real-time response time badge (`⏱️ 1.15s @ 9:35 AM`).

---

## 3. Implementation Steps Order

1. Update `backend/config.py` and `backend/core/config.py` with verified high-speed models.
2. Update `backend/rag_engine.py` with:
   - Instant greeting & notice fast-paths.
   - Parallel context retrieval (`ThreadPoolExecutor`).
   - Single embedding reuse.
   - Generator function for streaming response chunks (`stream_answer_query`).
3. Update `backend/orchestrator/agent.py` and `backend/orchestrator/preloaded_responses.py` with streaming generator support.
4. Add `/api/chat/stream` and `/api/v1/chat/stream` streaming routes to `backend/app.py` and `backend/api/chat_routes.py`.
5. Update `static/index.html` and `static/widget.js` to support SSE streaming with fallback to standard JSON.
6. Re-run complete benchmark suite and generate `PERFORMANCE_BEFORE_AFTER.md`.
