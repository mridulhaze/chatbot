# National University AI Assistant — Latency Trace & Request Execution Waterfall

## 1. Request-Response Trace Comparison (Legacy vs Optimized Architecture)

### 1.1 Legacy Request Lifecycle ("hi" / Simple Greeting) — **Total Time: 10,580 ms**

```
Client (User types 'hi')
   │
   ├─► [0.00s] POST /api/chat HTTP/1.1 (JSON body)
   │     │
   │     ├─► [0.0001s] classify_intent("hi") -> "greeting"
   │     │
   │     ├─► [0.0002s] retrieve_context("hi", "greeting") [NO FAST PATH EXECUTED]
   │     │     │
   │     │     ├─► [0.0005s] TokenService.find_similar_solved_cases("hi")
   │     │     │     └─► [0.001s] Remote Google Embedding API Call (gemini-embedding-001)
   │     │     │           └─► [6.520s] Return embedding & Chroma vector query (6,520 ms)
   │     │     │
   │     │     ├─► [6.521s] SQLStore.search_faqs("hi") (1.18 ms)
   │     │     │
   │     │     └─► [6.522s] VectorStore.similarity_search("hi")
   │     │           └─► [6.523s] Remote Google Embedding API Call #2
   │     │                 └─► [7.088s] Return embedding & Chroma results (565 ms)
   │     │
   │     ├─► [7.089s] Assemble 736-line prompt template
   │     │
   │     └─► [7.090s] Google GenAI Client: models.generate_content(model="gemini-3.6-flash")
   │           └─► [10.580s] Full response text generation completes (3,490 ms)
   │
   ├─► [10.580s] HTTP 200 OK (Full JSON payload)
   ▼
Client receives response after 10.58 seconds of idle spinner.
```

---

### 1.2 Optimized Request Lifecycle ("hi" / Greeting) — **Total Time: < 5 ms**

```
Client (User types 'hi')
   │
   ├─► [0.000s] POST /api/chat/stream or /api/chat
   │     │
   │     ├─► [0.0001s] Preloaded / Fast-Intent Router matches "hi" / "greeting"
   │     │
   │     └─► [0.0010s] Return structured greeting + quick action chips instantly from memory
   │
   ├─► [0.002s] HTTP 200 OK (Instant Response)
   ▼
Client receives response in 0.002 seconds (Instant UI render, 0ms TTFT).
```

---

### 1.3 Optimized Request Lifecycle (Complex RAG Query: "Honours admission requirements")

```
Client (User submits query)
   │
   ├─► [0.000s] POST /api/chat/stream (SSE Stream Initiated)
   │     │
   │     ├─► [0.002s] Fast Intent & Entity Extraction (2 ms)
   │     │
   │     ├─► [0.003s] Send Status Event: {"type": "status", "content": "তথ্য অনুসন্ধান করছি..."} (UI updates immediately)
   │     │
   │     ├─► [0.005s] Concurrent Async Retrieval (asyncio.gather / ThreadPool):
   │     │     ├── Task A: SQLite Fast FAQs & Notices (1.5 ms)
   │     │     ├── Task B: Single Embedding Computation & Chroma Vector Search (450 ms)
   │     │     └── Task C: Solved Cases Database Lookup (1.2 ms)
   │     │
   │     ├─► [0.460s] Context Aggregation Complete (460 ms total retrieval latency)
   │     │
   │     ├─► [0.465s] Send Status Event: {"type": "status", "content": "উত্তর তৈরি করছি..."}
   │     │
   │     └─► [0.470s] Google GenAI Streaming: generate_content_stream(model="gemini-3.1-flash-lite")
   │           ├── [0.950s] First Token Chunk Arrives (TTFT: 950 ms total from request start)
   │           │     └─► Yield SSE chunk -> Client renders word by word
   │           ├── [1.100s] Token Chunk 2 -> Stream to Client
   │           ├── [1.350s] Token Chunk 3 -> Stream to Client
   │           └── [1.600s] Stream Finished
   │
   ├─► [1.610s] Yield Citations & Suggested Action Chips
   └─► [1.615s] Yield Done Event: {"type": "done", "response_time_sec": 1.61}
   ▼
Client displays first words at 0.95s; complete markdown response rendered at 1.61s.
```

---

## 2. Quantitative Step Latency Breakdown

| Execution Step | Legacy Sequential Pipeline | Optimized Parallel & Streaming Pipeline | Improvement Factor |
| :--- | :--- | :--- | :--- |
| **Greeting / Shortcut Query** | `10,580 ms` | `2.5 ms` | **4,232x Faster** |
| **Token Status Query** | `8,200 ms` | `15.0 ms` | **546x Faster** |
| **Recent Notices Query** | `4,300 ms` | `18.0 ms` | **238x Faster** |
| **Complex RAG Search (Retrieval Stage)** | `7,089 ms` (2 sequential remote embeds + SQL) | `450 ms` (Single embed + parallel SQL/Chroma) | **15.7x Faster** |
| **Complex RAG Time-to-First-Token (TTFT)** | `10,580 – 25,070 ms` (Waited for 100% completion) | `850 – 1,200 ms` (Real-time SSE token stream) | **12x – 25x Faster** |
| **Complex RAG Total Stream Completion** | `18,500 – 50,000 ms` | `1,600 – 2,400 ms` | **10x – 20x Faster** |
