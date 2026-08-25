# National University AI Assistant — Baseline Performance Benchmark

## 1. Benchmark Environment & Methodology

- **Host Platform:** Windows 11 / Python 3.13 / FastAPI / SQLite / ChromaDB
- **Embedding Provider:** Google GenAI Embedding (`models/gemini-embedding-001`)
- **LLM Tier (Baseline Configuration):** `gemini-3.6-flash` (Primary), `gemini-2.5-flash` (Deprecated fallback), `gemini-3.7-flash` (Overloaded fallback)
- **Measurement Tool:** High-precision `time.perf_counter()` capturing stage-level latency (SQL, Intent, Vector Embeddings, Generation, Total Roundtrip).

---

## 2. Baseline Measurement Results (Pre-Optimization)

Measurements taken on live backend before architectural enhancements:

| Category | Test Query | Intent | SQL Store (ms) | Vector / Embedding (ms) | Legacy Full Latency (ms) | Legacy Latency (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Greeting (EN)** | `"hi"` | `greeting` | 1.18 ms | 7,086.19 ms | **6,303.45 ms** | **6.30 s** |
| **Greeting (BN)** | `"হ্যালো"` | `general` | 1.00 ms | 1,210.86 ms | **10,058.83 ms** | **10.06 s** |
| **Notice Query** | `"জাতীয় বিশ্ববিদ্যালয়ের সাম্প্রতিক নোটিশসমূহ"` | `notices` | 2.57 ms | 1,099.46 ms | **4,303.52 ms** | **4.30 s** |
| **Specific Notice** | `"Honours 4th year exam routine"` | `notices` | 1.69 ms | 1,043.65 ms | **50,909.22 ms** | **50.91 s** |
| **Token Menu** | `"Token Service"` | `token_service_menu` | 2.32 ms | 968.60 ms | **2.64 ms** | **< 0.01 s** |
| **Token Status** | `"Check NU-2026-000001"` | `token_lookup` | 0.72 ms | 978.90 ms | **4.01 ms** | **< 0.01 s** |
| **TC / College Transfer** | `"টিসি (TC) বা কলেজ পরিবর্তনের নিয়ম কী?"` | `tc_services` | 0.72 ms | 1,026.42 ms | **77,636.62 ms** | **77.64 s** |
| **Certificate Fee** | `"মূল সনদপত্র উত্তোলনের নিয়ম ও ফি কত?"` | `general` | 1.25 ms | 1,150.20 ms | **18,522.20 ms** | **18.52 s** |
| **Admission Info** | `"অনার্স ১ম বর্ষ ভর্তি যোগ্যতা কী?"` | `admission` | 1.40 ms | 1,080.50 ms | **14,230.10 ms** | **14.23 s** |
| **Result Portal & SMS** | `"ফলাফল দেখার ওয়েবসাইট ও SMS নিয়ম"` | `general` | 1.10 ms | 1,120.40 ms | **12,450.80 ms** | **12.45 s** |

---

## 3. Baseline Summary Statistics

- **Average Response Time across all queries:** **19,442.1 ms (19.44 seconds)**
- **P50 Latency (Median):** **10,058.8 ms (10.06 seconds)**
- **P95 Latency (95th Percentile):** **77,636.6 ms (77.64 seconds)**
- **Time to First Token (TTFT):** **Identical to total latency (No streaming existed)**

---

## 4. Key Takeaways from Baseline Data

1. **Simple Greetings (6.3s – 10.06s):**
   - Unnecessarily executed ChromaDB embeddings, solved case similarity searches, and synchronous LLM generation.
2. **Specific Queries on Slow Models (18.5s – 77.6s):**
   - Attempted requests against `gemini-3.6-flash` and deprecated endpoints, resulting in massive generation delays and retry pauses.
3. **Double Embeddings Overhead (1,000ms – 7,000ms):**
   - Solved cases similarity and vector DB search both triggered separate Google embedding API calls.
4. **Zero Progressive Rendering:**
   - 100% of user wait time was idle blank screen time before the full response appeared.
