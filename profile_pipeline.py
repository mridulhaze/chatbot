import os
import sys
import time
from pathlib import Path

# Ensure UTF-8 stdout on Windows and flush immediately
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent))

from db.sql_store import get_sql_store
from db.vector_store import get_vector_store
from token_service.service import get_token_service
from backend.rag_engine import get_rag_engine
from backend.orchestrator.agent import get_ai_orchestrator
from backend.models.schemas import ChatRequest

BENCHMARK_QUERIES = [
    # 1. Greeting
    ("Greeting", "hi"),
    ("Greeting (BN)", "হ্যালো"),
    # 2. Notice
    ("Notice Query", "জাতীয় বিশ্ববিদ্যালয়ের সাম্প্রতিক নোটিশসমূহ"),
    ("Specific Notice", "Honours 4th year exam routine"),
    # 3. Token Service
    ("Token Menu", "Token Service"),
    ("Token Status", "Check NU-2026-000001"),
    # 4. Student ERP / TC
    ("TC Service", "টিসি (TC) বা কলেজ পরিবর্তনের নিয়ম কী?"),
    ("Certificate", "মূল সনদপত্র উত্তোলনের নিয়ম ও ফি কত?"),
    # 5. Admission
    ("Admission", "অনার্স ১ম বর্ষ ভর্তি যোগ্যতা কী?"),
    # 6. Results
    ("Result & SMS", "ফলাফল দেখার ওয়েবসাইট ও SMS নিয়ম")
]

def run_full_audit():
    print("=" * 80, flush=True)
    print("NATIONAL UNIVERSITY AI ASSISTANT — COMPLETE PIPELINE PERFORMANCE AUDIT", flush=True)
    print("=" * 80, flush=True)

    sql_store = get_sql_store()
    vec_store = get_vector_store()
    token_svc = get_token_service()
    rag_engine = get_rag_engine()
    orchestrator = get_ai_orchestrator()

    results = []

    for cat, query in BENCHMARK_QUERIES:
        print(f"\n>>> [{cat}] Query: '{query}'", flush=True)

        # Stage 1: SQL latency
        t0 = time.perf_counter()
        sql_faqs = sql_store.search_faqs(query, limit=3)
        sql_notices = sql_store.get_recent_notices(limit=5)
        t_sql = (time.perf_counter() - t0) * 1000

        # Stage 2: Intent detection latency
        t0 = time.perf_counter()
        intent = rag_engine.classify_intent(query)
        t_intent = (time.perf_counter() - t0) * 1000

        # Stage 3: Token Service similar cases (vector embedding)
        t0 = time.perf_counter()
        similar_cases = token_svc.find_similar_solved_cases(query, top_k=2)
        t_token_sim = (time.perf_counter() - t0) * 1000

        # Stage 4: Vector Store semantic search (Google Embedding + ChromaDB)
        t0 = time.perf_counter()
        vec_matches = vec_store.similarity_search(query, k=5)
        t_vec = (time.perf_counter() - t0) * 1000

        # Stage 5: Full RAG Engine answer_query
        t0 = time.perf_counter()
        rag_resp = rag_engine.answer_query(query=query, history=[])
        t_rag = (time.perf_counter() - t0) * 1000

        # Stage 6: Orchestrator process_chat
        t0 = time.perf_counter()
        orch_req = ChatRequest(message=query, history=[])
        orch_resp = orchestrator.process_chat(orch_req)
        t_orch = (time.perf_counter() - t0) * 1000

        print(f"    Intent: {intent} ({t_intent:.2f}ms)", flush=True)
        print(f"    SQL Store: {t_sql:.2f}ms", flush=True)
        print(f"    Token Sim Embedding: {t_token_sim:.2f}ms", flush=True)
        print(f"    Chroma Vector Search: {t_vec:.2f}ms", flush=True)
        print(f"    RAGEngine Total: {t_rag:.2f}ms ({t_rag/1000:.2f}s)", flush=True)
        print(f"    Orchestrator Total: {t_orch:.2f}ms ({t_orch/1000:.2f}s)", flush=True)

        results.append({
            "category": cat,
            "query": query,
            "intent": intent,
            "sql_ms": t_sql,
            "intent_ms": t_intent,
            "token_sim_ms": t_token_sim,
            "vector_ms": t_vec,
            "rag_total_ms": t_rag,
            "orch_total_ms": t_orch
        })

    # Summary Statistics
    print("\n" + "=" * 80, flush=True)
    print("SUMMARY LATENCY REPORT ACROSS ALL CATEGORIES", flush=True)
    print("=" * 80, flush=True)
    rag_times = [r["rag_total_ms"] for r in results]
    orch_times = [r["orch_total_ms"] for r in results]
    rag_times.sort()
    orch_times.sort()

    p50_rag = rag_times[len(rag_times) // 2]
    p95_rag = rag_times[int(len(rag_times) * 0.95)]
    p50_orch = orch_times[len(orch_times) // 2]
    p95_orch = orch_times[int(len(orch_times) * 0.95)]

    print(f"RAG Engine (Current /api/chat):  Avg={sum(rag_times)/len(rag_times):.1f}ms | P50={p50_rag:.1f}ms | P95={p95_rag:.1f}ms", flush=True)
    print(f"AI Orchestrator (/api/v1/chat): Avg={sum(orch_times)/len(orch_times):.1f}ms | P50={p50_orch:.1f}ms | P95={p95_orch:.1f}ms", flush=True)

if __name__ == "__main__":
    run_full_audit()
