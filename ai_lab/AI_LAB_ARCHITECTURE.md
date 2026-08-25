# National University AI Assistant — Autonomous AI Lab Architecture
**Continuous Multi-Agent Quality Assurance, Research & Development Ecosystem**

---

## 1. System Overview

The **National University AI Lab** is a 24/7 autonomous dual-agent reinforcement and self-improving loop designed to continuously elevate the intelligence, factual accuracy, conversational naturalness, multilingual fluency (Bangla, English, Banglish), and system reliability of the National University AI Assistant.

```
                   ┌─────────────────────────────────────────┐
                   │                 AGENT 1                 │
                   │  AI Researcher + Human Simulator + QA   │
                   └────────────────────┬────────────────────┘
                                        │
                                        ▼  Executes Multi-Turn Scenarios & Edge Cases
                           ┌─────────────────────────┐
                           │      QA REPORT &        │
                           │     ACTIONABLE TASKS    │
                           └────────────┬────────────┘
                                        │
                                        ▼  Prioritizes & Diagnoses Root Causes
                   ┌─────────────────────────────────────────┐
                   │                 AGENT 2                 │
                   │    AI Developer & System Fixer Engine   │
                   └────────────────────┬────────────────────┘
                                        │
                                        ▼  Implements Patches & Automated Unit Tests
                           ┌─────────────────────────┐
                           │    TESTS & DEPLOYS TO   │
                           │    CONTROLLED STAGING   │
                           └────────────┬────────────┘
                                        │
                                        ▼  Re-tests Fixed Scenarios & Checks Regressions
                   ┌─────────────────────────────────────────┐
                   │                 AGENT 1                 │
                   │    Verification & Continuous Discovery  │
                   └────────────────────┬────────────────────┘
                                        │
                                        └───────────► (Loop continues / Cooldown)
```

---

## 2. Core Agents Specification

### 2.1 AGENT 1: Senior AI Researcher & Human Simulator (QA Engine)
* **15 Dynamic User Personas:**
  1. *Normal Student:* Standard inquiries about routine, admission, results.
  2. *Confused Student:* Unclear terms, vague needs, seeking guidance.
  3. *Angry / Frustrated User:* Complaining about exam delays or withheld marks.
  4. *Low NU Knowledge User:* Unfamiliar with Gazipur campus vs affiliated colleges.
  5. *Technically Knowledgeable User:* Asks for API details, server status, security.
  6. *College Administrator:* Asks about EMS portal access, college code batch updates.
  7. *Faculty / Teacher:* Asks about examiner remunerations, practical mark submission.
  8. *Incomplete Question Inquirer:* "ভর্তি কবে?", "result?", "routine?".
  9. *Typo-Prone User:* "admissoin", "formfilup", "reslt", "certifcate".
  10. *Bangla-Native User:* Pure Bengali Unicode queries.
  11. *English-Native User:* Formal English queries.
  12. *Banglish Colloquial User:* "nu te admission kobe?", "result ber hoise?".
  13. *Context Switching User:* Jumps from Admission to Marksheet then back to Admission.
  14. *Deep Multi-Turn Follow-Up User:* Drills down into specific clause of a notice.
  15. *Adversarial / Hallucination Probe:* Tests future dates (e.g. 2035) and unverified rumors.

* **12-Dimensional Scoring Matrix (1 to 10 Scale):**
  - **Accuracy:** Factual correctness against official National University regulations.
  - **Relevance:** Direct response to the query without tangential clutter.
  - **Clarity:** Well-structured, readable layout with bold headers and bullet points.
  - **Completeness:** Provides necessary steps, links, and contact channels.
  - **Context Awareness:** Retains multi-turn conversation memory.
  - **Naturalness:** Avoids robotic repetition, empathetic human-like tone.
  - **Bangla Quality:** Natural Bengali phrasing without transliteration artifacts.
  - **English Quality:** Professional, grammatically sound English.
  - **Source Quality:** Cites official notices (`www.nu.ac.bd`, notice dates, PDF URLs).
  - **Tool & Skill Selection:** Appropriate activation of Token, Credential, or RAG MCP tools.
  - **Safety & Privacy:** Zero leakage of passwords, credentials, or administrative secrets.
  - **Helpfulness:** Offers proactive, actionable next steps for the student.

---

### 2.2 AGENT 2: Senior AI Software & RAG Engineer (Developer Engine)
* **Root Cause Analysis Workflow:**
  - Evaluates whether issues stem from **Prompt Formatting**, **Intent Routing**, **Temporal Retrieval Decay**, **Vector Chunk Slicing**, **Database Constraints**, or **Token Workflow Handlers**.
* **Targeted Implementations:**
  - Patches RAG search queries, expands colloquial synonym registries, sharpens prompt guidelines, and updates skill trigger rules.
* **Regression Safety Guarantee:**
  - Every patch must be accompanied by an automated regression test in `tests/`.
  - Staging validation occurs before any change is promoted to live serving.
* **Anti-Infinite-Damage Safeguard:**
  - If any issue is reopened **> 3 times**, it is automatically locked as `STUCK_ISSUE`, modifications are halted on that subsystem, and an urgent alert is issued for human review.

---

## 3. Persistent Directory Structure

```
/ai_lab/
├── AI_LAB_ARCHITECTURE.md     # Master architecture documentation
├── AI_LAB_ROADMAP.md          # Phased operational roadmap
├── lab_state.json             # Persistent 24/7 execution state & metrics
├── agent1_researcher_qa.py    # Agent 1 engine
├── agent2_developer_fixer.py  # Agent 2 engine
├── orchestrator_loop.py       # Autonomous loop manager & rate limiter
├── research/                  # Synthesized best-practice research papers
├── qa_reports/                # Detailed QA reports from Agent 1
├── tasks/                     # Task queue items (TASK-XXXX)
├── implementations/           # Agent 2 implementation changelogs & diffs
├── test_results/              # Automated test run logs
├── regressions/               # Regression suite tracking
├── cycle_reports/             # Comprehensive executive cycle logs
└── metrics/                   # Historical KPI metrics and score graphs
```

---

## 4. Operational Safety & Resource Governance

1. **Global Control States:**
   - `STOPPED`: System completely idle, no background tasks started.
   - `RUNNING`: Autonomous cycle executes on scheduled cooldown intervals.
   - `PAUSED`: Current task finishes safely, new cycles paused.
2. **Rate Limits & Safeguards:**
   - `MAX_TESTS_PER_CYCLE`: 15 scenarios.
   - `COOLDOWN_BETWEEN_CYCLES`: 120 seconds.
   - `MAX_CONCURRENT_SIMULATIONS`: 4 parallel sessions.
   - `MAX_REOPEN_COUNT`: 3 (triggers `STUCK_ISSUE` circuit breaker).
   - Zero Credential Exposure Policy (AES-256-GCM, no passwords in logs/prompts/RAG).
