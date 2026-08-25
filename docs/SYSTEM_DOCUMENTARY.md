# 🎓 National University Bangladesh AI Academic Assistant & Support Platform
## Comprehensive System Documentary, User Manual & Technical Architecture (0-Level to Advanced)

---

## 🌟 Executive Summary: What is this Platform?

The **National University Bangladesh AI Assistant** is a unified, production-grade AI platform developed specifically for the **3+ million students, teachers, and administrative staff** of the National University (NU), Bangladesh (nu.ac.bd).

Historically, students across thousands of affiliated colleges faced difficulties finding accurate notices, exam schedules, admission criteria, and resolving portal login issues (such as EMS accounts and form fill-up errors). 

This platform bridges this gap by combining:
1. **Intelligent Conversational AI (Bilingual Bengali & English)** powered by Google Gemini 3 Flash with sub-millisecond preloaded instant answers.
2. **Retrieval-Augmented Generation (RAG) & ChromaDB Vector Store** that indexes verified official notices, circulars, and regulations.
3. **Official Support Token Service (Ticketing System)** allowing students to open tracked tickets for 10+ specific university services with atomic ID generation (`NU-2026-XXXXXX`).
4. **Service-Specific Encrypted Credential Vault** protecting student portal passwords with AES-128-CBC encryption.
5. **Autonomous 24/7 Knowledge Enrichment Agents** that crawl the web, parse academic circulars, extract dates and rules, synthesize Q&A pairs, and update the knowledge base around the clock.
6. **Model Context Protocol (MCP) Server Architecture** giving AI models direct, tool-based access to databases, search engines, and ticket workflows.
7. **Department Solver & Administrative Support Center** for university staff to assign, process, resolve, and audit support tokens.

---

## 📖 Chapter 1: Complete User Manual for 0-Level Beginners

This section is written for anyone using the platform for the very first time. No technical knowledge is required.

```
+-------------------------------------------------------------------------+
|                NATIONAL UNIVERSITY AI ASSISTANT HOMEPAGE                |
+-------------------------------------------------------------------------+
| [NU Logo] National University AI Assistant           [🎫 Token Service] |
| nu.ac.bd Official Knowledge Base & Token Support     [📋 Check Token]   |
|                                                      [📱 Mobile QR]     |
|                                                      [🔐 Admin Portal]  |
|                                                      [❓ Help Guide]    |
+-------------------------------------------------------------------------+
| [🎓 Admission] [📊 Results] [📝 Form Fill-up] [📄 Official Notices]     |
+-------------------------------------------------------------------------+
|                                                                         |
|  💬 Chat Window: Ask any question in Bengali or English                 |
|                                                                         |
|  [🎫 টোকেন সার্ভিস] [📑 টোকেন স্ট্যাটাস চেক] [📄 সাম্প্রতিক নোটিশ] [🎓 ভর্তি তথ্য] |
|                                                                         |
|  [ Type your question here...                                    ] [➤]  |
+-------------------------------------------------------------------------+
```

### 1.1 How to Chat with the AI Assistant
1. **Type in plain Bengali or English**: You can ask questions such as:
   - *"অনার্স ১ম বর্ষের ভর্তি কবে শুরু হবে?"*
   - *"How can I check my Degree 2nd year results via SMS?"*
   - *"ইএমএস পোর্টালে পাসওয়ার্ড রিসেট করার নিয়ম কী?"*
   - *"সার্টিফিকেট উত্তোলনের জন্য কী কী কাগজপত্র প্রয়োজন?"*
2. **Instant Preloaded Answers (< 0.001s)**:
   - If you send common greetings like `hi`, `hello`, `সালাম`, `ভর্তি`, `রুটিন`, or `রেজাল্ট`, the system responds **instantly** without waiting for network delays, showing you all official links and quick action buttons.
3. **Clickable Official References**:
   - Every official response comes with green verified citation badges linking directly to `nu.ac.bd`, `app1.nu.edu.bd`, `results.nu.ac.bd`, and `ems.nu.ac.bd`.
4. **Suggested Action Chips**:
   - Click the interactive pills at the bottom of the answer (e.g. `🎓 ভর্তি তথ্য`, `🎫 টোকেন সার্ভিস`) to immediately execute related actions.

---

### 1.2 How to Apply for an Official Support Token (Ticket Service)
When you have a personal problem that the chatbot cannot resolve directly (e.g., your EMS account is blocked, or your marksheet is delayed), you can open an official support token:

1. Click the **`[ 🎫 Token Service ]`** button at the top header or in the chat chips.
2. Select your specific **Service Category**:
   - `EMS` — EMS Portal & Student Dashboard Login Issues
   - `FORM_FILLUP` — Exam Form Fill-up & Online Fee Verification
   - `RESCRUTINY` — Result Re-check / Board Challenge Follow-up
   - `CERTIFICATE` — Original or Provisional Certificate Dispatch
   - `MARKSHEET` — Tabulation Sheet & Academic Transcript
   - `TC` — College Transfer & Migration Clearance
   - `CORRECTION` — Name, Age, or Subject Correction
   - `ADMISSION` — Online Admission Application & Merit List Support
3. Fill in your details:
   - **Student Name** (e.g., `Rahim Uddin`)
   - **Phone Number** (e.g., `017XXXXXXXX`)
   - **Roll / Registration Number** (e.g., `1920000000`)
   - **Problem Description** (e.g., *'EMS login showing invalid credentials since last Sunday'*).
4. *(Optional)* Provide service-specific login credentials if technical support requires portal verification (credentials are encrypted with AES-128).
5. Click **`[ Confirm & Save Token ]`**.
6. **Save your Token ID** (e.g., `NU-2026-000135`). You can click the copy button or scan the QR code.

---

### 1.3 How to Check Your Live Token Status
1. Click the **`[ 📋 Check Token ]`** button at the top header.
2. Enter your Token ID (e.g., `NU-2026-000135`).
3. Click **`[ Track Token ]`**.
4. The system will display:
   - **Current Status**: `PENDING` 🟡 ➔ `ASSIGNED` 🟣 ➔ `PROCESSING` 🔵 ➔ `SOLVED` 🟢 ➔ `CLOSED` ⚫
   - **Assigned Department**: (e.g. *ICT Support Desk*, *Exam Controller Section*, *Certificate Wing*)
   - **Official Resolution Message**: Step-by-step instructions from the university officer.
   - **Resolution Certificate PDF**: One-click download button for official records.

---

### 1.4 How to Use on Mobile Phones (QR Code)
1. Click the **`[ 📱 Mobile QR ]`** button at the top header.
2. A high-resolution QR code will appear on your computer screen.
3. Open your mobile phone camera or any QR scanner and scan the code.
4. The full National University AI Assistant will open instantly in your mobile web browser with touch-optimized controls.

---

## 🏛️ Chapter 2: Staff, Solver & Administrator Guide

For designated university department officers, solver desk agents, and system administrators.

```
+-------------------------------------------------------------------------+
|                  ADMINISTRATIVE & SOLVER SUPPORT CENTER                 |
+-------------------------------------------------------------------------+
| Tabs: [🎫 Tokens] [🗺️ Website Map] [🚀 Crawler] [🤖 24/7 Agents] [👥 Users]
+-------------------------------------------------------------------------+
| Real-time Filters: [All Services ▼] [All Statuses ▼] [Search Token ID]   |
+-------------------------------------------------------------------------+
| 📌 NU-2026-000135 | EMS Portal Login Issue | PENDING | [⚙️ Manage Token] |
| 📌 NU-2026-000134 | Marksheet Verification  | SOLVED  | [📄 View Cert]   |
+-------------------------------------------------------------------------+
```

### 2.1 Staff Roles & Permissions
The system enforces strict Role-Based Access Control (RBAC):
- **`STUDENT` (Public)**: Can chat with AI, create tokens, check token status, and use mobile QR. No login required.
- **`SOLVER` (Department Staff)**: Can view assigned tickets, change ticket status, record official resolution messages, view website structure maps, and trigger 24/7 AI enrichment.
- **`ADMIN` (Department Lead)**: All Solver capabilities plus creating staff accounts, assigning user roles, configuring crawler schedules, and auditing logs.
- **`SUPER_ADMIN` (Central ICT Division)**: Full system access including API keys, database migrations, and cryptographic key rotations.

### 2.2 Processing & Solving a Student Token
1. Open **`[ 🔐 Admin & Solvers ]`** and log in with your university credentials.
2. In the **`🎫 Token Support Center`** tab, locate the ticket by filtering by service or status.
3. Click **`[ ⚙️ Manage Token ]`**:
   - **Assign Solver Desk**: Select your department (e.g., *ICT Support Desk Officer*, *Registration Wing*).
   - **Update Status**: Set status to `PROCESSING` or `SOLVED`.
   - **Record Official Resolution**: Type the verified solution in Bengali/English.
4. **Automatic Vector Knowledge Capture**: When a ticket is marked `SOLVED`, the system anonymizes the resolution and automatically indexes it into ChromaDB so the AI Assistant learns the solution for future students!

---

## 💻 Chapter 3: Deep Technical Architecture

```
                                 ┌─────────────────────────────────┐
                                 │   Browser UI & Mobile Client    │
                                 │    (HTML5, TailwindCSS, JS)     │
                                 └───────────────┬─────────────────┘
                                                 │ REST & JSON / WebSockets
                                 ┌───────────────▼─────────────────┐
                                 │      FastAPI Async Backend      │
                                 │   (Non-blocking Event Loop)     │
                                 └───────┬───────────────┬─────────┘
                                         │               │
                 ┌───────────────────────┴──────┐ ┌──────┴────────────────────────┐
                 │    AI Orchestrator Pipeline  │ │       MCP Client Layer         │
                 │   • Fast Greetings (< 1ms)   │ │  • Token MCP Server            │
                 │   • LRU Cache (300s TTL)     │ │  • Knowledge MCP Server        │
                 │   • Intent & Skill Classifier│ │  • Document MCP Server         │
                 │   • Gemini 3 Flash LLM       │ │  • Credential MCP Server       │
                 └───────────────┬──────────────┘ │  • 24/7 Enrichment MCP Server │
                                 │                └──────────────┬─────────────────┘
                 ┌───────────────┴──────────────┐                │
                 │   ChromaDB Vector Database   │                │
                 │   (Google GenAI Embeddings)  │                │
                 └───────────────┬──────────────┘                │
                                 │                               │
                 ┌───────────────┴───────────────────────────────┴─┐
                 │       SQLite Relational & Audit Data Core       │
                 │  • nu_tokens.sqlite3    • nu_credentials.sqlite3│
                 │  • nu_deep_crawler.db   • knowledge_updates.json│
                 └─────────────────────────────────────────────────┘
```

### 3.1 Fast-Path & Non-Blocking Async Pipeline
- **FastAPI Thread Isolation**: Handled via `await asyncio.to_thread(orchestrator.process_chat, payload)` in [`backend/api/chat_routes.py`](file:///E:/projects/AI_CHAT_BOT/backend/api/chat_routes.py). Network calls to Google GenAI or SQLite disk I/O do not block the HTTP event loop.
- **Sub-Millisecond Preloaded Engine**: Configured in [`backend/orchestrator/preloaded_responses.py`](file:///E:/projects/AI_CHAT_BOT/backend/orchestrator/preloaded_responses.py). Direct keyword hashes for greetings, admissions, routines, and results return complete, formatted layouts with citations in **18 microseconds (0.018 ms)**.
- **Model Upgrades**: Active models configured to `gemini-3-flash-preview` and `gemini-3.1-flash-lite` with low latency constraints (`max_output_tokens=600`, `temperature=0.2`).

### 3.2 Model Context Protocol (MCP) Integration
The system implements the **Anthropic & Antigravity Model Context Protocol (MCP)** specification:
- **`TokenMCPServer`**: Exposes 8 structured tools for ticket creation, status checks, assignment, and similarity search.
- **`KnowledgeMCPServer`**: Exposes vector search, notices filtering, and section lookup tools.
- **`DocumentMCPServer`**: Exposes PDF document parsing, page extraction, and metadata queries.
- **`CredentialMCPServer`**: Exposes secure credential status and encrypted storage tools.
- **`EnrichmentMCPServer`**: Exposes 24/7 agent telemetry, JSON manifest exports, and batch enrichment triggers.

---

## 🤖 Chapter 4: 24/7 Autonomous Knowledge Enrichment Agents

```
[ 🕷️ Deep Crawler & Scrapers ] ──> [ 💾 Raw Pages & Documents in SQLite ]
                                                │
                                                ▼
                                [ 🤖 Agent 1: ScrapedDataAnalyzerAgent ]
                                (Extracts Dates, Deadlines, Rules & QA)
                                                │
                                                ▼
                                [ 🧠 Agent 2: KnowledgeEnricherAgent ]
                                (Ingests into ChromaDB & Updates Cache)
                                                │
                                                ▼
                                [ 📜 Agent 3: KnowledgeProvenanceAgent ]
                                (Appends to JSONL & Knowledge Manifest)
                                                │
                                                ▼
                                [ 🤝 Standard MCP & REST APIs for Other AIs ]
```

### 4.1 How Autonomous Learning Works:
1. **Continuous Scraped Data Analysis**: `ScrapedDataAnalyzerAgent` runs every 10 minutes, extracting academic rules, dates, deadlines, and generating bilingual Q&A pairs.
2. **Multi-Tier Knowledge Ingestion**: `KnowledgeEnricherAgent` chunks and embeds new QA pairs into ChromaDB, and updates `INSTANT_LOOKUP_MAP` for high-frequency queries.
3. **Traceability & Open Standards**: `KnowledgeProvenanceAgent` appends all updates to [`data/knowledge_updates.jsonl`](file:///E:/projects/AI_CHAT_BOT/data/knowledge_updates.jsonl), compiles the RFC 8259 [`data/knowledge_manifest.json`](file:///E:/projects/AI_CHAT_BOT/data/knowledge_manifest.json), and writes [`data/KNOWLEDGE_CHANGELOG.md`](file:///E:/projects/AI_CHAT_BOT/data/KNOWLEDGE_CHANGELOG.md).
4. **Inter-Agent Collaboration**: Any other AI agent (OpenAI Codex, Claude Code, Antigravity subagent) can read the manifest and know exactly what changed.

---

## 🔒 Chapter 5: Security, Cryptography & Privacy

1. **User Password Hashing**: Passwords stored using PBKDF2-HMAC-SHA256 with 100,000 iterations and unique cryptographic salts.
2. **Service Credential Encryption**: Student passwords for EMS / Form Fill-up portals are encrypted using **Fernet AES-128 in CBC mode** with HMAC-SHA256 authentication. Plaintext passwords are never logged or returned in API responses.
3. **Stateless JWT Authentication**: Secure JWT tokens with configurable expiration (24h) and role claims (`Role.STUDENT`, `Role.SOLVER`, `Role.ADMIN`, `Role.SUPER_ADMIN`).
4. **Comprehensive Audit Logs**: Every administrative action, token creation, status change, and credential submission is written to `nu_audit_log` with IP addresses and timestamps.

---

## 🚀 Chapter 6: Future Roadmap & Next Horizon

| Milestone | Target Horizon | Feature Overview |
| :--- | :--- | :--- |
| **Phase 1 (Completed)** | Q3 2026 | Full RAG Chatbot, Sub-Millisecond Preloading, Token Support Service, MCP Servers, 24/7 Autonomous Enrichment Agents. |
| **Phase 2 (Upcoming)** | Q4 2026 | **Bangla Voice AI Assistant**: Real-time voice interaction using bidirectional WebSocket streaming for rural students. |
| **Phase 3** | Q1 2027 | **Automated WhatsApp & SMS Gateway**: Real-time notifications sent directly to students' mobile phones upon token resolution. |
| **Phase 4** | Q2 2027 | **Automated Digital Certificate Dispatch**: Integration with National University Central Database for instant e-certificate verification and digital signatures. |
| **Phase 5** | Q3 2027 | **Multi-Campus Federated Clustering**: Dedicated sub-agents deployed for regional divisional centers across Bangladesh. |

---

*Authored by the National University AI Engineering Team | Version 2.0.0*
