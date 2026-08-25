# National University AI Assistant — Autonomous AI Lab Roadmap

---

## 🎯 Strategic Objectives

Build an autonomous, continuous, self-healing quality assurance and developer loop that systematically tests, investigates, patches, and benchmarks the National University AI Assistant.

---

## 🚀 Execution Phases

### Phase 1: Foundation & Baseline Validation (Initial Controlled Cycle)
- [x] Inspect full system architecture (Chatbot, RAG, ChromaDB, SQLite, Crawler, Token Service, Security).
- [x] Define multi-persona simulation engine (15 distinct student & faculty personas).
- [x] Build 12-metric quantitative evaluation scorecard.
- [x] Establish `/ai_lab/` persistent directory workspace.
- [x] Implement Agent 1 (QA & Human Simulation) and Agent 2 (Developer & Fixer).
- [x] Implement `AI Lab Orchestrator` with `AUTONOMOUS_MODE` state machine (`STOPPED`, `RUNNING`, `PAUSED`).
- [x] Run **Controlled Initial Test Cycle (Cycle #1)** to verify end-to-end multi-agent handoff without regression.

### Phase 2: Autonomous Diagnostic & Remediation Loop
- [x] Deploy task queue manager (`TASK-0001` format) with priority triage (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- [x] Implement automated root cause analyzer (Prompt, Intent Router, Temporal RAG, MCP, Token Desk).
- [x] Connect continuous test suite runner with automated rollback protection.
- [x] Integrate circuit-breaker for stuck issues (`>3 reopens` halts auto-edits and alerts administrator).

### Phase 3: Research Synthesis & Continuous Exploration
- [ ] Agent 1 autonomous research module synthesizes weekly AI/RAG/Bangla NLP advances.
- [ ] Adversarial edge case generation (Colloquial dialect variations, exam center stress simulations).
- [ ] Cross-college scenario simulation across all 64 districts.

### Phase 4: Admin Dashboard Integration & Live Telemetry
- [x] Add **🧪 AI Lab (Autonomous R&D)** tab to the Central Admin Portal (`static/index.html`).
- [x] Live telemetry stream (Active Agent 1 / Agent 2 status, open issue counters, quality score gauges).
- [x] Admin controls: `[ START ]`, `[ PAUSE ]`, `[ STOP ]`, `[ RESUME ]`, `[ RUN TEST CYCLE ]`.
- [x] Real-time cycle report inspector and downloadable artifacts.
