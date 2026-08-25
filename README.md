# NU AI — Smart Academic Assistant for National University Bangladesh (nu.ac.bd)

A production-grade AI Academic Assistant and counselor for **National University Bangladesh (জাতীয় বিশ্ববিদ্যালয়)** built on Google Gemini 2.5/3.5 Flash, ChromaDB vector store, and SQLite structured storage with a **self-enriching RAG (Retrieval-Augmented Generation)** architecture.

---

## 🌟 Key Features

1. **Dual-Tier Retrieval-Augmented Generation (RAG)**:
   - **Tier 1: Live & Structured SQL Cache**: Exact-match queries for latest circulars, admission eligibility, routines, and verified FAQs.
   - **Tier 2: Semantic Vector Search**: ChromaDB semantic search over official notices, PDF circulars, and university guidelines.
2. **Polite Multi-Source Crawlers**:
   - `nu.ac.bd/notices` (`recent-news-notice.php`, `examination-notice.php`, `admission-notice.php`).
   - `app1.nu.edu.bd` (Honours, Degree Pass, Masters, and Professional admission guidelines).
   - `results.nu.ac.bd` (Grading scales, SMS syntax, re-scrutiny instructions — **strictly zero personal student roll scraping**).
   - `ems.nu.ac.bd` (Form fill-up procedures, payment methods, Sonali Seba).
   - Diff-based hashing (`MD5`) so only modified or newly published circulars are embedded.
3. **Support Token Service (সাপোর্ট টোকেন সার্ভিস)**:
   - **Student Problem Submission**: Interactive service categories (Form Fill-up, TC, Rescrutiny, EMS, Certificate, Marksheet, Registration, Admission, Results, Other).
   - **Atomic Sequential Token IDs**: `NU-YYYY-000001` format using database-backed atomic sequences to prevent collisions.
   - **Full Support Lifecycle**: `PENDING` -> `ASSIGNED` -> `PROCESSING` -> `SOLVED` -> `CLOSED` -> `REJECTED` with audit history logging.
   - **Solved Cases as Secondary Knowledge**: When an administrator records a verified solution, it is automatically embedded into ChromaDB with zero PII exposure to serve similar future student queries.
   - **Admin / Solver Management Center**: Filter, assign solvers (ICT Support, Exam Section, Certificate Cell), and resolve student tickets.
4. **Continuous Self-Enrichment Engine**:
   - Automatically detects low-confidence or unanswered student queries and logs them into a **Gap Queue** (`gap_queue` table).
   - Background enrichment worker generates structured candidate answers using Gemini and attaches confidence ratings.
   - 1-Click approval in the Admin Portal to publish candidate answers into the active verified knowledge base.
5. **Bilingual & Empathetic UI**:
   - Automatic language detection for Bengali (বাংলা), English, and Banglish.
   - Official portal quick-links, dynamic follow-up chips, PDF download badges, and markdown tables.
   - Resilient graceful degradation (returns structured facts with official links even if LLM connectivity fluctuates).

---

## 🏛️ System Architecture

```
                    ┌──────────────────────────┐
                    │      NU AI CHATBOT       │
                    └────────────┬─────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             │                   │                   │
             ▼                   ▼                   ▼
       NU Knowledge        Token Service         General AI
          / RAG                  │
             │           ┌───────┼───────┐
             │           ▼       ▼       ▼
             │         Tokens  Solvers History
             │           │
             │           ▼
             │     Solved Problems
             │      (Anonymized)
             │           │
             └───────────┼──────────────────────────┐
                         ▼                          │
                   AI Similarity                    │
                         │                          │
                         └───────────┬──────────────┘
                                     ▼
                                Final Answer
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key ([Google AI Studio](https://aistudio.google.com/))

### 2. Installation
```bash
git clone <repository_url>
cd AI_CHAT_BOT

# Create virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create or verify `.env` in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PRIMARY_MODEL=gemini-3.5-flash
CRAWL_INTERVAL_HOURS=4
ENRICH_INTERVAL_HOURS=8
RATE_LIMIT_PER_MINUTE=45
PORT=8000
HOST=0.0.0.0
```

### 4. Running the Server
```bash
python main.py
```
Open your browser at **[http://localhost:8000](http://localhost:8000)** to interact with the assistant and admin controls.

---

## 🐳 Docker Deployment

Run with Docker Compose:
```bash
docker compose up -d --build
```
Logs can be viewed with:
```bash
docker compose logs -f
```

---

## 📡 API Reference

### Chat & Search
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/chat` | Main conversational RAG endpoint (accepts `message`, `history`, `session_id`) |
| `GET` | `/api/quick-links` | Categorized list of official National University portals and archives |
| `GET` | `/api/health` | Health check and database/crawler status |

### Admin & Self-Enrichment
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/admin/crawl-status` | View recent crawl logs, pages indexed, and crawler state |
| `POST` | `/api/admin/trigger-crawl` | Trigger an immediate polite crawl in the background |
| `GET` | `/api/admin/gap-queue` | List pending, candidate, and resolved gap queries |
| `POST` | `/api/admin/gap-queue/{id}/approve` | Approve a candidate answer into the verified knowledge base |
| `POST` | `/api/admin/gap-queue/{id}/reject` | Reject/dismiss a gap query |
| `POST` | `/api/admin/trigger-enrichment` | Trigger background AI research across all pending gaps |

---

## 🛡️ Privacy & Compliance
- **Zero Personal Data**: The bot does **not** scrape, cache, or expose individual students' roll numbers or registration-specific marks.
- **Polite Crawling**: Scrapers respect host limits, include identify headers (`NU-Academic-AI-Crawler`), implement jitter delays, and verify SSL securely.
- **Accurate Academic Guidance**: Strictly instructed to avoid hallucinating admission dates or pass figures. Provides official URLs when circulars are pending.
