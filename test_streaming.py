import os
import sys
import time
from google import genai
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

models_to_test = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview"
]

print("STREAMING BENCHMARK & TIME TO FIRST TOKEN (TTFT):")
for m in models_to_test:
    try:
        t0 = time.perf_counter()
        stream = client.models.generate_content_stream(
            model=m,
            contents="জাতীয় বিশ্ববিদ্যালয়ের অনার্স ভর্তি কার্যক্রম সম্পর্কে ৩টি গুরুত্বপূর্ণ তথ্য পয়েন্ট আকারে বাংলায় লিখুন।"
        )
        ttft = None
        chunks = 0
        total_chars = 0
        for chunk in stream:
            if ttft is None:
                ttft = (time.perf_counter() - t0) * 1000
            chunks += 1
            if chunk.text:
                total_chars += len(chunk.text)
        total_time = (time.perf_counter() - t0) * 1000
        print(f"[{m}] TTFT: {ttft:.1f}ms | Total Time: {total_time:.1f}ms | Chunks: {chunks} | Chars: {total_chars}")
    except Exception as e:
        print(f"[{m}] STREAMING FAILED: {e}")
