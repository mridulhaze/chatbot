import os
import sys
import time
from pathlib import Path

# Ensure UTF-8 stdout on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.rag_engine import get_rag_engine
from backend.models.schemas import ChatMessage

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

def run_post_optimization_benchmark():
    print("=" * 80, flush=True)
    print("NATIONAL UNIVERSITY AI ASSISTANT — POST-OPTIMIZATION LATENCY BENCHMARK", flush=True)
    print("=" * 80, flush=True)

    rag_engine = get_rag_engine()
    results = []

    for cat, query in BENCHMARK_QUERIES:
        # Measure Non-Streaming response
        t0 = time.perf_counter()
        resp = rag_engine.answer_query(query=query, history=[])
        t_sync = (time.perf_counter() - t0) * 1000

        # Measure Streaming response & Time-to-First-Token (TTFT)
        t0 = time.perf_counter()
        stream = rag_engine.stream_answer_query(query=query, history=[])
        ttft = None
        chunks = 0
        total_len = 0
        for event in stream:
            if "data:" in event:
                if '"type": "token"' in event and ttft is None:
                    ttft = (time.perf_counter() - t0) * 1000
                chunks += 1
                total_len += len(event)
        t_stream = (time.perf_counter() - t0) * 1000
        if ttft is None:
            ttft = t_stream

        print(f"[{cat:15}] Query: '{query[:35]}...'", flush=True)
        print(f"    Sync Total: {t_sync:7.2f} ms | Stream TTFT: {ttft:7.2f} ms | Stream Total: {t_stream:7.2f} ms | Intent: {resp.intent}", flush=True)

        results.append({
            "category": cat,
            "query": query,
            "intent": resp.intent,
            "sync_ms": t_sync,
            "ttft_ms": ttft,
            "stream_ms": t_stream,
            "sources": len(resp.sources) or len(resp.citations)
        })

    print("\n" + "=" * 80, flush=True)
    print("POST-OPTIMIZATION AGGREGATE SUMMARY", flush=True)
    print("=" * 80, flush=True)

    sync_times = [r["sync_ms"] for r in results]
    ttft_times = [r["ttft_ms"] for r in results]
    stream_times = [r["stream_ms"] for r in results]

    avg_sync = sum(sync_times) / len(sync_times)
    avg_ttft = sum(ttft_times) / len(ttft_times)
    avg_stream = sum(stream_times) / len(stream_times)

    print(f"Average Total Sync Latency : {avg_sync:7.2f} ms ({avg_sync/1000:.2f} s)", flush=True)
    print(f"Average Time to First Token: {avg_ttft:7.2f} ms ({avg_ttft/1000:.2f} s)", flush=True)
    print(f"Average Total Stream Time  : {avg_stream:7.2f} ms ({avg_stream/1000:.2f} s)", flush=True)

if __name__ == "__main__":
    run_post_optimization_benchmark()
