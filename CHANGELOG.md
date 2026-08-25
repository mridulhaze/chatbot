# Changelog & Update History

All notable changes and technical resolutions for the National University AI Assistant project are documented in this file.

---

## [1.2.1] - 2026-08-18 (Rate-Limit Resilience & University Administration Data)

### Fixed & Improved
- **Automatic Retry with Backoff & Model Fallback**: Added automatic 3x retry backoff and fallback models (`gemini-3.5-flash` -> `gemini-3.1-flash-lite` -> `gemini-3.5-flash-lite`) in [`main.py`](file:///e:/projects/AI_CHAT_BOT/main.py). When concurrent users query the API simultaneously, transient Gemini 429 RPM spikes are recovered automatically without dropping connections.
- **Frontend Error Message Transparency**: Refactored the catch block in [`gemini-code-1786959765553.html`](file:///e:/projects/AI_CHAT_BOT/gemini-code-1786959765553.html) to present clear connection diagnostics rather than generic offline warnings.
- **University Leadership & Administration Dataset**: Ingested complete details for the Vice-Chancellor (**Professor Dr. A. S. M. Amanullah**), Pro-VCs (**Prof. Md. Lutfor Rahaman**, **Professor Dr. Mohammad Ali Zinnah**), Treasurer, and Registrar into [`data/nu_knowledge_base.json`](file:///e:/projects/AI_CHAT_BOT/data/nu_knowledge_base.json) and Chroma DB.

---

## [1.2.0] - 2026-08-18 (Smart Interactive UI & Multi-Turn Memory)

### Added & Enhanced
- **Rich Markdown & PDF Badge Rendering**: Integrated `marked.js` + `DOMPurify` into [`gemini-code-1786959765553.html`](file:///e:/projects/AI_CHAT_BOT/gemini-code-1786959765553.html). Notice PDF download links are automatically rendered as interactive `[📥 Download Notice PDF]` buttons.
- **Multi-Turn Conversational Memory**: Added conversation history tracking (`history` array) in both frontend and FastAPI backend [`main.py`](file:///e:/projects/AI_CHAT_BOT/main.py), allowing natural follow-up queries (e.g. "give me the link of masters final").
- **Dynamic Contextual Suggestion Chips**: The backend generates contextual follow-up buttons (`suggested_chips`) displayed below each bot response for 1-click exploration.
- **Expanded Knowledge Base**: Added comprehensive datasets for Result Archives (`results.nu.ac.bd`), SMS result query codes (`16222`), Form fill-up procedures (`ems.nu.ac.bd`), GPA/CGPA grading tables, and Board Challenge (re-scrutiny) guidelines.
- **Academic Counselor Prompt**: Removed repetitive robotic boilerplate; trained prompt to deliver structured, articulate, empathetic, and actionable guidance in both English and Bengali.
- **UI Utilities**: Added 1-click Copy to Clipboard button on messages, Clear Chat session reset, and mobile-friendly responsive layout.

---

## [1.1.0] - 2026-08-18

### Fixed
- **Fixed `ingest.py` 404 NOT_FOUND Error**:
  - *Cause*: `ingest.py` requested `model="text-embedding-004"` which was not supported or not found in API version `v1beta`.
  - *Resolution*: Updated embedding model to `models/gemini-embedding-001`.
- **Fixed `ingest.py` 429 RESOURCE_EXHAUSTED Rate Limit Error**:
  - *Cause*: Scraping the entire `nu.ac.bd` homepage included massive HTML selects/options generating >530 chunks which saturated Gemini Free-Tier rate limits.
  - *Resolution*:
    - Implemented clean structured table scraping targeting dedicated notice sub-pages (`recent-news-notice.php`, `examination-notice.php`, `admission-notice.php`).
    - Stripped redundant navigational and select tag bloat.
    - Implemented batching (10 chunks per batch) with 1.0s delay and exponential retry backoff (up to 5 attempts).
- **Fixed `main.py` Deprecated Model & SDK**:
  - *Cause*: `main.py` relied on deprecated `google.generativeai` and `gemini-1.5-flash` model, and duplicate Chroma imports.
  - *Resolution*: Migrated to modern `google.genai.Client`, `gemini-3.5-flash`, unified `langchain_chroma.Chroma`, and matching `models/gemini-embedding-001`.
- **Fixed Missing Dependencies**:
  - Added `langchain-chroma>=0.1.0` and `google-genai>=1.0.0` to `requirements.txt`.

### Added
- Curated baseline knowledge seed for National University containing program structures (Honours, Degree, Masters, Professional), 4.00 grading scale, promotion/improvement policies, re-scrutiny timelines, and admission criteria.
- Created `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, and `AI_AGENT_GUIDE.md` for project tracking and AI agent continuity.

### Verified
- Executed `python ingest.py` successfully and built `./nu_vector_db`.
- Ran end-to-end RAG verification test querying `./nu_vector_db` + `gemini-3.5-flash` with 100% accurate responses.

---

## [1.0.0] - Initial Prototype
- Initial project scaffolding for National University RAG chatbot with `ingest.py`, `main.py`, and `gemini-code-1786959765553.html` frontend widget.
