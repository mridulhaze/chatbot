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
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview"
]

print("BENCHMARKING VALID GEMINI MODELS:")
for m in models_to_test:
    try:
        t0 = time.perf_counter()
        resp = client.models.generate_content(
            model=m,
            contents="তুমি জাতীয় বিশ্ববিদ্যালয়ের সহকারী। সংক্ষেপে ১ বাক্যে সালাম দাও।"
        )
        elapsed = (time.perf_counter() - t0) * 1000
        print(f"[{m}] SUCCESS in {elapsed:.1f}ms: {resp.text.strip()}")
    except Exception as e:
        print(f"[{m}] FAILED: {e}")
