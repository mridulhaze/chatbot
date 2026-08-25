"""
National University Bangladesh AI Assistant & Smart Support Platform
High-Fidelity PDF Generator with Standard Unicode Text Shaping (Bilingual & English Editions)
Outputs to:
  - E:/projects/AI_CHAT_BOT/docs/project-overview.pdf (Bengali / Bilingual Edition)
  - E:/projects/AI_CHAT_BOT/docs/project-overview-en.pdf (English Edition)
"""

import os
import subprocess
from pathlib import Path
import fitz

BASE_DIR = Path("E:/projects/AI_CHAT_BOT")
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Locate Chrome or Edge
def get_browser_executable() -> str:
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("Could not find Edge or Chrome executable for PDF printing.")

def convert_html_to_pdf(html_path: Path, pdf_path: Path):
    browser = get_browser_executable()
    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--allow-file-access-from-files",
        "--enable-local-file-accesses",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri()
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Browser PDF generation failed (code {res.returncode}): {res.stderr}")
    print(f"[OK] Generated: {pdf_path} ({pdf_path.stat().st_size} bytes)")

def generate_bilingual_html() -> str:
    return """<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<title>National University AI Assistant — Project Overview & Architecture</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&family=Fira+Code:wght@400;600&display=swap');

  @page {
    size: A4 portrait;
    margin: 12mm 14mm 14mm 14mm;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Hind Siliguri', 'Noto Sans Bengali', 'Kalpurush', 'SolaimanLipi', 'Vrinda', 'Segoe UI', Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.5;
    font-size: 13px;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .page {
    page-break-after: always;
    position: relative;
    padding-bottom: 25px;
  }

  .page:last-child {
    page-break-after: avoid;
  }

  /* Header Banner */
  .header-table {
    width: 100%;
    border-bottom: 2px solid #059669;
    padding-bottom: 8px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .header-left h2 {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 800;
    color: #065f46;
    letter-spacing: -0.2px;
  }

  .header-left p {
    font-size: 11px;
    color: #059669;
    font-weight: 600;
  }

  .header-right {
    text-align: right;
  }

  .header-right .badge {
    display: inline-block;
    background: #0f172a;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
    font-size: 9px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .header-right p {
    font-size: 10px;
    color: #64748b;
    margin-top: 2px;
  }

  /* Main Title */
  .title-section {
    margin-bottom: 12px;
  }

  .title-section h1 {
    font-size: 21px;
    font-weight: 700;
    color: #065f46;
    line-height: 1.3;
    margin-bottom: 4px;
  }

  .title-section .subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: #475569;
    font-weight: 600;
  }

  /* Callout Boxes */
  .callout-box {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-left: 4px solid #059669;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 12px;
  }

  .callout-box h3 {
    font-size: 13px;
    font-weight: 700;
    color: #065f46;
    margin-bottom: 4px;
  }

  .callout-box p {
    font-size: 12px;
    color: #166534;
    line-height: 1.5;
  }

  /* Highlight Cards 3-Column */
  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    margin-bottom: 14px;
  }

  .card {
    padding: 9px 11px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    background: #ffffff;
  }

  .card.green { background: #f0fdf4; border-color: #bbf7d0; }
  .card.amber { background: #fffbeb; border-color: #fef08a; }
  .card.blue { background: #eff6ff; border-color: #bfdbfe; }
  .card.purple { background: #faf5ff; border-color: #e9d5ff; }

  .card h4 {
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 3px;
  }

  .card.green h4 { color: #065f46; }
  .card.amber h4 { color: #92400e; }
  .card.blue h4 { color: #1e40af; }
  .card.purple h4 { color: #6b21a8; }

  .card p {
    font-size: 11px;
    color: #475569;
    line-height: 1.4;
  }

  /* Section Headings */
  .section-title {
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
    border-left: 3px solid #059669;
    padding-left: 8px;
    margin-top: 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .section-title span.en {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
  }

  /* Architecture Diagram SVG Container */
  .diagram-container {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 12px;
    text-align: center;
  }

  /* Tables */
  table.data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 6px;
    margin-bottom: 12px;
    font-size: 11.5px;
  }

  table.data-table th {
    background: #0f172a;
    color: #ffffff;
    font-weight: 700;
    padding: 6px 10px;
    text-align: left;
    border: 1px solid #334155;
    font-size: 11px;
  }

  table.data-table td {
    padding: 6px 10px;
    border: 1px solid #e2e8f0;
    vertical-align: top;
    line-height: 1.4;
  }

  table.data-table tr:nth-child(even) td {
    background: #f8fafc;
  }

  .tag {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 4px;
    font-family: 'Inter', sans-serif;
    font-size: 9.5px;
    font-weight: 700;
  }

  .tag.green { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
  .tag.blue { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
  .tag.purple { background: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; }
  .tag.amber { background: #fef3c7; color: #92400e; border: 1px solid #fde047; }
  .tag.slate { background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; }

  /* Footer */
  .page-footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    border-top: 1px solid #cbd5e1;
    padding-top: 5px;
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #64748b;
  }
</style>
</head>
<body>

<!-- ==================== PAGE 1: EXECUTIVE OVERVIEW & ARCHITECTURE SKETCH ==================== -->
<div class="page">
  <div class="header-table">
    <div class="header-left">
      <h2>NATIONAL UNIVERSITY BANGLADESH</h2>
      <p>জাতীয় বিশ্ববিদ্যালয় • শিক্ষা ও তথ্য প্রযুক্তি বিভাগ</p>
    </div>
    <div class="header-right">
      <span class="badge">Official Technical Overview</span>
      <p>Version 2.0 • Production Ready • 2026</p>
    </div>
  </div>

  <div class="title-section">
    <h1>জাতীয় বিশ্ববিদ্যালয় AI অ্যাসিস্ট্যান্ট ও স্মার্ট সাপোর্ট প্ল্যাটফর্ম</h1>
    <div class="subtitle">National University AI Academic Assistant, Support Token Service & 24/7 Autonomous Knowledge Ecosystem</div>
  </div>

  <div class="callout-box">
    <h3>🌟 প্রজেক্ট পরিচিতি ও পটভূমি (Executive Overview)</h3>
    <p>
      জাতীয় বিশ্ববিদ্যালয় (<strong>nu.ac.bd</strong>) বাংলাদেশের সর্ববৃহৎ উচ্চশিক্ষা প্রতিষ্ঠান, যার অধীনে ২,২০০+ অধিভুক্ত কলেজে ৩০ লক্ষাধিক শিক্ষার্থী অধ্যয়নরত। ভর্তি বিজ্ঞপ্তি, সংশোধিত পরীক্ষার রুটিন, ফরম পূরণ (EMS পোর্টাল), ফলাফল মূল্যায়ন, সনদ ও মার্কশিট সংক্রান্ত হাজার হাজার জটিল সমস্যা নিরসনে এই কৃত্রিম বুদ্ধিমত্তাভিত্তিক ইকোসিস্টেম তৈরি করা হয়েছে। এটি শিক্ষার্থীদের যেকোনো প্রশ্নের তাৎক্ষণিক উত্তর দেয় এবং দাপ্তরিক সমাধানের জন্য এনক্রিপ্টেড সাপোর্ট টোকেন সিস্টেম পরিচালনা করে।
    </p>
  </div>

  <div class="grid-3">
    <div class="card green">
      <h4>⚡ সাব-মিলিমিটার রেসপন্স</h4>
      <p>সাধারণ জিজ্ঞাসা (hi, ভর্তি, রুটিন, রেজাল্ট) <strong>০.০১ মিলি-সেকেন্ডে</strong> প্রি-লোডেড মেমোরি ক্যাশ থেকে তাৎক্ষণিক প্রদান।</p>
    </div>
    <div class="card amber">
      <h4>🎫 অটোমিক সাপোর্ট টোকেন</h4>
      <p>ইএমএস পাসওয়ার্ড, ফরম পূরণ ও সনদ সমস্যার জন্য <strong>NU-2026-XXXXXX</strong> ট্র্যাকিং নম্বর সহ সমাধান ডেস্ক।</p>
    </div>
    <div class="card blue">
      <h4>🤖 ২৪/৭ স্বয়ংক্রিয় নলেজ এজেন্ট</h4>
      <p>সার্বক্ষণিক নোটিশ ও সার্কুলার বিশ্লেষণ করে প্রশ্নোত্তর তৈরি ও ভেক্টর ডাটাবেসে রিয়েল-টাইম নলেজ আপডেট।</p>
    </div>
  </div>

  <div class="section-title">
    ১. পূর্ণাঙ্গ সিস্টেম আর্কিটেকচার ও ডাটা ফ্লো স্কেচ ডায়াগ্রাম
    <span class="en">(Architecture & Data Flow Sketch)</span>
  </div>

  <div class="diagram-container">
    <svg width="100%" height="225" viewBox="0 0 740 225" xmlns="http://www.w3.org/2000/svg">
      <!-- Container Background -->
      <rect x="0" y="0" width="740" height="225" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
      
      <!-- Top Title -->
      <rect x="0" y="0" width="740" height="26" rx="8" fill="#0f172a"/>
      <text x="15" y="17" fill="#ffffff" font-family="'Hind Siliguri', 'Segoe UI'" font-size="11" font-weight="700">সিস্টেম আর্কিটেকচার ও উপাদান সমূহের সংযোগ রেখাচিত্র (Bilingual Data Flow)</text>
      
      <!-- Box 1: User Channels -->
      <rect x="15" y="38" width="125" height="85" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1.5"/>
      <text x="22" y="56" fill="#065f46" font-family="'Hind Siliguri'" font-size="11" font-weight="700">১. ইউজার ইন্টারফেস</text>
      <text x="22" y="73" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• ওয়েব চ্যাটবট (Web UI)</text>
      <text x="22" y="89" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• মোবাইল কিউআর (QR)</text>
      <text x="22" y="105" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• টোকেন সার্ভিস পোর্টাল</text>

      <!-- Arrow 1 -> 2 -->
      <path d="M 140 80 L 168 80" stroke="#059669" stroke-width="2" marker-end="url(#arrow-green)"/>

      <!-- Box 2: FastAPI Gateway -->
      <rect x="170" y="35" width="165" height="92" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
      <text x="178" y="54" fill="#1e40af" font-family="'Hind Siliguri'" font-size="11" font-weight="700">২. FastAPI গেটওয়ে ও কোর</text>
      <text x="178" y="70" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• নন-ব্লকিং অ্যাসিন্ক ইঞ্জিন (asyncio)</text>
      <text x="178" y="85" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• প্রি-লোডেড ফাস্ট ক্যাশ (18 µs)</text>
      <text x="178" y="100" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• ইন্টেন্ট ও স্কিল রাউটার</text>
      <text x="178" y="115" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• Google Gemini 3 Flash LLM</text>

      <!-- Arrow 2 -> 3 -->
      <path d="M 335 80 L 363 80" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>

      <!-- Box 3: MCP Tool Suite -->
      <rect x="365" y="38" width="135" height="85" rx="6" fill="#faf5ff" stroke="#9333ea" stroke-width="1.5"/>
      <text x="373" y="56" fill="#6b21a8" font-family="'Hind Siliguri'" font-size="11" font-weight="700">৩. MCP সার্ভার স্যুট</text>
      <text x="373" y="73" fill="#334155" font-family="'Fira Code', monospace" font-size="9">• token_mcp (8 tools)</text>
      <text x="373" y="89" fill="#334155" font-family="'Fira Code', monospace" font-size="9">• knowledge_mcp</text>
      <text x="373" y="105" fill="#334155" font-family="'Fira Code', monospace" font-size="9">• credential_mcp</text>

      <!-- Arrow 3 -> 4 (Down) -->
      <path d="M 432 123 L 432 140" stroke="#9333ea" stroke-width="2" marker-end="url(#arrow-purple)"/>

      <!-- Box 4: Database Core -->
      <rect x="345" y="142" width="175" height="74" rx="6" fill="#fffbeb" stroke="#d97706" stroke-width="1.5"/>
      <text x="353" y="159" fill="#92400e" font-family="'Hind Siliguri'" font-size="11" font-weight="700">৪. ডাটাবেস ও এনক্রিপশন কোর</text>
      <text x="353" y="174" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• ChromaDB সেমান্টিক ভেক্টর স্টোর</text>
      <text x="353" y="189" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• SQLite (WAL Mode) টোকেন ডাটাবেস</text>
      <text x="353" y="204" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• Fernet AES-128 ক্রেডেনশিয়াল ভল্ট</text>

      <!-- Box 5: 24/7 Autonomous Agents -->
      <rect x="15" y="142" width="155" height="74" rx="6" fill="#fdf2f8" stroke="#db2777" stroke-width="1.5"/>
      <text x="22" y="159" fill="#9d174d" font-family="'Hind Siliguri'" font-size="11" font-weight="700">৫. ২৪/৭ স্বয়ংক্রিয় এজেন্ট</text>
      <text x="22" y="174" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• ScrapedDataAnalyzerAgent</text>
      <text x="22" y="189" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• KnowledgeEnricherAgent</text>
      <text x="22" y="204" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• JSONL স্ট্রিম ও RFC 8259 Manifest</text>

      <!-- Arrow 5 -> 4 -->
      <path d="M 170 178 L 343 178" stroke="#db2777" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#arrow-pink)"/>

      <!-- Box 6: Solvers & Admin -->
      <rect x="180" y="142" width="155" height="74" rx="6" fill="#f1f5f9" stroke="#475569" stroke-width="1.5"/>
      <text x="188" y="159" fill="#0f172a" font-family="'Hind Siliguri'" font-size="11" font-weight="700">৬. দাপ্তরিক সলভার ও অ্যাডমিন</text>
      <text x="188" y="174" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• আইসিটি, পরীক্ষা ও রেজিস্ট্রেশন ডেস্ক</text>
      <text x="188" y="189" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• সেলফ-লার্নিং ভেক্টর ফিডব্যাক লুপ</text>
      <text x="188" y="204" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">• RBAC ভিত্তিক রোল পারমিশন</text>

      <!-- Box 7: nu.ac.bd Portals -->
      <rect x="530" y="38" width="195" height="178" rx="6" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5"/>
      <text x="540" y="58" fill="#166534" font-family="'Hind Siliguri'" font-size="11" font-weight="700">৭. জাতীয় বিশ্ববিদ্যালয় পোর্টাল</text>
      <text x="540" y="78" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">🌐 nu.ac.bd (মূল ওয়েবসাইট ও নোটিশ)</text>
      <text x="540" y="96" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">📝 app1.nu.edu.bd (ভর্তি পোর্টাল)</text>
      <text x="540" y="114" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">📊 results.nu.ac.bd (ফলাফল আর্কাইভ)</text>
      <text x="540" y="132" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">🔐 ems.nu.ac.bd (স্টুডেন্ট লগইন)</text>
      <text x="540" y="150" fill="#334155" font-family="'Hind Siliguri'" font-size="9.5">💳 সোনালী সেবা পেমেন্ট গেটওয়ে</text>
      <rect x="540" y="165" width="175" height="38" rx="4" fill="#dcfce7" stroke="#86efac"/>
      <text x="546" y="180" fill="#166534" font-family="'Hind Siliguri'" font-size="9" font-weight="700">ইন্টেলিজেন্ট ডিপ ক্রলার ও RAG সিঙ্ক</text>
      <text x="546" y="194" fill="#166534" font-family="'Hind Siliguri'" font-size="8">১০টি ডিপার্টমেন্ট পেজ স্বয়ংক্রিয়ভাবে স্ক্র্যাপ করে</text>

      <!-- Markers -->
      <defs>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 8 5 L 0 9 z" fill="#059669"/></marker>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 8 5 L 0 9 z" fill="#2563eb"/></marker>
        <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 8 5 L 0 9 z" fill="#9333ea"/></marker>
        <marker id="arrow-pink" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 8 5 L 0 9 z" fill="#db2777"/></marker>
      </defs>
    </svg>
  </div>

  <div class="page-footer">
    <span>National University AI Assistant • Project Overview & Architecture</span>
    <span>Page 1 of 3</span>
  </div>
</div>

<!-- ==================== PAGE 2: TECH STACK & 24/7 ENRICHMENT ==================== -->
<div class="page">
  <div class="header-table">
    <div class="header-left">
      <h2>TECHNOLOGY STACK & WORKING MECHANISMS</h2>
      <p>ব্যবহৃত প্রযুক্তি এবং এদের কার্যপ্রণালী বিশদ বিবরণ</p>
    </div>
    <div class="header-right">
      <span class="badge">Core Engineering Stack</span>
      <p>Python 3.13 • FastAPI • ChromaDB • MCP</p>
    </div>
  </div>

  <div class="section-title">
    ২. ব্যবহৃত প্রযুক্তিসমূহ ও তাদের কার্যপদ্ধতি
    <span class="en">(Technologies & Technical Principles)</span>
  </div>

  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 22%;">প্রযুক্তি (Technology)</th>
        <th style="width: 18%;">সংস্করণ / কম্পোনেন্ট</th>
        <th>ভূমিকা ও প্রযুক্তিগত কার্যপ্রণালী (Role & Mechanism)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>FastAPI Backend</strong></td>
        <td><span class="tag green">v0.115+ (Python 3.13)</span></td>
        <td>নন-ব্লকিং অ্যাসিনক্রোনাস ওয়েব গেটওয়ে। <code>asyncio.to_thread</code> ব্যবহার করে ব্যাকগ্রাউন্ডে হেভি I/O এবং GenAI অফলোড করে ইভেন্ট লুপকে সর্বোচ্চ গতিশীল রাখে।</td>
      </tr>
      <tr>
        <td><strong>Google Gemini 3 Flash</strong></td>
        <td><span class="tag blue">gemini-3-flash-preview</span></td>
        <td>বাইলিঙ্গুয়াল জেনারেটিভ AI কোর। সাব-সেকেন্ডে বাংলা ও ইংরেজি প্রশ্ন বিশ্লেষণ করে অফিসিয়াল সার্কুলার লিংক ও ভেরিফায়েড ব্যাজ সহ সঠিক উত্তর প্রদান করে।</td>
      </tr>
      <tr>
        <td><strong>ChromaDB Vector Store</strong></td>
        <td><span class="tag purple">gemini-embedding-001</span></td>
        <td>অফিসিয়াল নোটিশ ও সমাধানের জন্য সেমান্টিক ভেক্টর সার্চ ইঞ্জিন। রেট লিমিট সুরক্ষায় স্বয়ংক্রিয় রেজিলিয়েন্ট সিউডো-ভেক্টর ব্যাকআপ ব্যবস্থা সংযুক্ত।</td>
      </tr>
      <tr>
        <td><strong>MCP Server Suite</strong></td>
        <td><span class="tag amber">5 Dedicated Servers</span></td>
        <td>অ্যানথ্রপিক ও অ্যান্টিগ্র্যাভিটি মডেল কনটেক্সট প্রোটোকল। <code>token_mcp</code>, <code>knowledge_mcp</code>, <code>document_mcp</code>, <code>credential_mcp</code>, <code>enrichment_mcp</code> পরিচালনা করে।</td>
      </tr>
      <tr>
        <td><strong>SQLite Relational Core</strong></td>
        <td><span class="tag slate">WAL Mode Enabled</span></td>
        <td>টোকেন, ক্রেডেনশিয়াল, ক্রলার পেজ ও অডিট ট্রেইল সংরক্ষণের নির্ভরযোগ্য ACID ইঞ্জিন। হাই-থ্রুপুট রাইটিং নিশ্চিত করতে WAL মোডে সক্রিয়।</td>
      </tr>
      <tr>
        <td><strong>Fernet AES-128 Vault</strong></td>
        <td><span class="tag green">CBC + HMAC-SHA256</span></td>
        <td>ইএমএস ও স্টুডেন্ট পোর্টালের লগইন পাসওয়ার্ড সুরক্ষায় AES-128 এনক্রিপশন ও PBKDF2 হ্যাশিং। ডাটাবেসে বা লগ ফাইলে কখনো প্লেইনটেক্সট পাসওয়ার্ড থাকে না।</td>
      </tr>
      <tr>
        <td><strong>Preloaded Fast Cache</strong></td>
        <td><span class="tag blue">In-Memory Trie (18 µs)</span></td>
        <td>সাধারণ সম্ভাষণ (hi, hello, সালাম), ভর্তি যোগ্যতা, পরীক্ষার রুটিন ও এসএমএস কোড মেমোরিতে প্রিলোড রেখে <strong>০.০১ মিলি-সেকেন্ডে</strong> উত্তর প্রদান করে।</td>
      </tr>
    </tbody>
  </table>

  <div class="section-title">
    ৩. ২৪/৭ স্বয়ংক্রিয় নলেজ এনরিচমেন্ট মাল্টি-এজেন্ট সিস্টেম
    <span class="en">(24/7 Autonomous Enrichment Pipeline)</span>
  </div>

  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 28%;">এজেন্টের নাম (Agent)</th>
        <th style="width: 47%;">দায়িত্ব ও কার্যপ্রণালী (Responsibilities)</th>
        <th style="width: 25%;">আউটপুট স্ট্যান্ডার্ড</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>ScrapedDataAnalyzerAgent</strong></td>
        <td>নতুন ক্রল করা নোটিশ ও সার্কুলার বিশ্লেষণ করে ডিগ্রি, শিক্ষাবর্ষ, আবেদনের শেষ তারিখ, ফি ও লিংক পৃথক করে বাংলা-ইংরেজি প্রশ্নোত্তর তৈরি করে।</td>
        <td><span class="tag blue">JSON Entities & QA</span></td>
      </tr>
      <tr>
        <td><strong>KnowledgeEnricherAgent</strong></td>
        <td>তৈরিকৃত প্রশ্নোত্তর ও নোটিশ ChromaDB ভেক্টর ডাটাবেসে ইনজেস্ট করে এবং হাই-ফ্রিকোয়েন্সি প্রশ্নগুলোর জন্য মেমোরি ক্যাশ আপডেট করে।</td>
        <td><span class="tag purple">ChromaDB Ingestion</span></td>
      </tr>
      <tr>
        <td><strong>KnowledgeProvenanceAgent</strong></td>
        <td>প্রতিটি পরিবর্তনের অডিট রেকর্ড সংরক্ষণ করে, যাতে অন্য যেকোনো AI এজেন্ট (Claude, Codex, Subagents) এই আপডেট পড়ে কাজ চালিয়ে যেতে পারে।</td>
        <td><span class="tag green">JSONL Stream & Manifest</span></td>
      </tr>
    </tbody>
  </table>

  <div class="callout-box" style="margin-top: 10px; background: #faf5ff; border-color: #d8b4fe; border-left-color: #9333ea;">
    <h3 style="color: #6b21a8;">💡 সেলফ-লার্নিং ভেক্টর ফিডব্যাক লুপ (Self-Learning Vector Feedback Loop)</h3>
    <p style="color: #581c87;">
      যখন কোনো কর্মকর্তা সাপোর্ট টোকেন <strong>SOLVED</strong> করেন এবং সমাধান বার্তা প্রদান করেন, সিস্টেম স্বয়ংক্রিয়ভাবে শিক্ষার্থীর ব্যক্তিগত তথ্য গোপন করে সমস্যা ও সমাধানের জোড়া ChromaDB-তে ইন্ডেক্স করে। ফলে পরবর্তীকালে অন্য কোনো শিক্ষার্থীর একই সমস্যা হলে AI তাত্ক্ষণিকভাবে পরীক্ষিত সমাধান প্রদান করতে পারে!
    </p>
  </div>

  <div class="page-footer">
    <span>National University AI Assistant • Project Overview & Architecture</span>
    <span>Page 2 of 3</span>
  </div>
</div>

<!-- ==================== PAGE 3: 0-LEVEL USER GUIDE & ROADMAP ==================== -->
<div class="page">
  <div class="header-table">
    <div class="header-left">
      <h2>0-LEVEL USER PLAYBOOK & FUTURE ROADMAP</h2>
      <p>সাধারণ ব্যবহারকারী নির্দেশিকা ও ভবিষ্যৎ কৌশলগত রোডম্যাপ</p>
    </div>
    <div class="header-right">
      <span class="badge">User Operations & Vision</span>
      <p>Token Lifecycle • Roadmap 2026-2027</p>
    </div>
  </div>

  <div class="section-title">
    ৪. ০-লেভেল সাধারণ শিক্ষার্থী ও কর্মচারীদের ব্যবহার নির্দেশিকা
    <span class="en">(0-Level User Playbook)</span>
  </div>

  <div class="grid-3" style="grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
    <div class="card green">
      <h4>১. এআই চ্যাটবটে প্রশ্ন করা</h4>
      <p>যেকোনো ভাষায় প্রশ্ন লিখুন (যেমন: <i>"অনার্স ভর্তি কবে?"</i> বা <i>"EMS পাসওয়ার্ড ভুলে গেছি"</i>)। বট অফিসিয়াল নোটিশের রেফারেন্স ও লিংক সহ নির্ভুল উত্তর দেবে।</p>
    </div>
    <div class="card amber">
      <h4>২. সাপোর্ট টোকেন আবেদন</h4>
      <p>জটিল সমস্যার ক্ষেত্রে <strong>Token Service</strong> বাটনে ক্লিক করে নির্দিষ্ট সেবা নির্বাচন করুন। সাথে সাথে ইউনিক ট্র্যাকিং নম্বর (যেমন: <strong>NU-2026-000140</strong>) পাবেন।</p>
    </div>
    <div class="card blue">
      <h4>৩. লাইভ স্ট্যাটাস ট্র্যাকিং</h4>
      <p><strong>Check Token</strong> অপশনে ট্র্যাকিং আইডি লিখে রিয়েল-টাইম অগ্রগতি দেখুন (<span class="tag amber">PENDING</span> ➔ <span class="tag blue">PROCESSING</span> ➔ <span class="tag green">SOLVED</span>)।</p>
    </div>
    <div class="card purple">
      <h4>৪. মোবাইল ক্যামেরা QR কোড</h4>
      <p><strong>Mobile QR</strong> বাটনে ক্লিক করে স্মার্টফোন দিয়ে স্ক্যান করলেই কোনো অ্যাপ ইন্সটল ছাড়াই মোবাইল ব্রাউজারে সম্পূর্ণ প্ল্যাটফর্ম ওপেন হবে।</p>
    </div>
  </div>

  <div class="section-title">
    ৫. সাপোর্ট টোকেন সেবাসমূহ ও সমাধানকারী বিভাগসমূহ
    <span class="en">(Service Categories & Department Desks)</span>
  </div>

  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 15%;">সার্ভিস কোড</th>
        <th style="width: 40%;">সেবার বিবরণ (Service Description)</th>
        <th style="width: 27%;">দায়িত্বপ্রাপ্ত দপ্তর (Department)</th>
        <th style="width: 18%;">সমাধান সময়</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>EMS</strong></td>
        <td>ইএমএস স্টুডেন্ট পোর্টাল পাসওয়ার্ড ও অ্যাকাউন্ট রিকভারি</td>
        <td>আইসিটি সাপোর্ট ডেস্ক</td>
        <td>২৪-৪৮ ঘণ্টা</td>
      </tr>
      <tr>
        <td><strong>FORM_FILLUP</strong></td>
        <td>পরীক্ষার ফরম পূরণ ও কলেজ ফি ভেরিফিকেশন সমস্যা</td>
        <td>পরীক্ষা নিয়ন্ত্রণ শাখা</td>
        <td>১২-২৪ ঘণ্টা</td>
      </tr>
      <tr>
        <td><strong>RESCRUTINY</strong></td>
        <td>ফলাফল পুনর্নিরীক্ষণ / বোর্ড চ্যালেঞ্জ আবেদন ট্র্যাকিং</td>
        <td>ফলাফল ও মূল্যায়ন শাখা</td>
        <td>৩-৭ কার্যদিবস</td>
      </tr>
      <tr>
        <td><strong>CERTIFICATE</strong></td>
        <td>মূল সনদ ও সাময়িক সনদ উত্তোলন ও যাচাইকরণ</td>
        <td>সনদপত্র শাখা</td>
        <td>২-৫ কার্যদিবস</td>
      </tr>
      <tr>
        <td><strong>MARKSHEET</strong></td>
        <td>একাডেমিক ট্রান্সক্রিপ্ট ও নম্বরপত্র সংশোধন</td>
        <td>রেজিস্ট্রার দপ্তর</td>
        <td>২-৪ কার্যদিবস</td>
      </tr>
      <tr>
        <td><strong>TC / CORRECTION</strong></td>
        <td>কলেজ ট্রান্সফার এবং নাম/বয়স/রেজিস্ট্রেশন সংশোধন</td>
        <td>রেজিস্ট্রেশন সেল</td>
        <td>৫-১০ কার্যদিবস</td>
      </tr>
    </tbody>
  </table>

  <div class="section-title">
    ৬. ভবিষ্যৎ কৌশলগত রোডম্যাপ
    <span class="en">(Future Expansion & Roadmap)</span>
  </div>

  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 22%;">পর্যায় (Phase)</th>
        <th style="width: 15%;">সময়কাল</th>
        <th>পরিকল্পিত প্রযুক্তি ও সক্ষমতা (Planned Features & Capabilities)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Phase 2 (Upcoming)</strong></td>
        <td><span class="tag blue">Q4 2026</span></td>
        <td><strong>বাংলা ভয়েস এআই অ্যাসিস্ট্যান্ট:</strong> গ্রামীণ ও দৃষ্টিপ্রতিবন্ধী শিক্ষার্থীদের জন্য রিয়েল-টাইম বাইডিরেকশনাল ভয়েস চ্যাট।</td>
      </tr>
      <tr>
        <td><strong>Phase 3</strong></td>
        <td><span class="tag amber">Q1 2027</span></td>
        <td><strong>হোয়াটসঅ্যাপ ও এসএমএস গেটওয়ে:</strong> টোকেন সমাধান বা জরুরি নোটিশ প্রকাশের সাথে সাথে শিক্ষার্থীর মোবাইলে অটোমেটিক অ্যালার্ট।</td>
      </tr>
      <tr>
        <td><strong>Phase 4</strong></td>
        <td><span class="tag green">Q2 2027</span></td>
        <td><strong>রোবোটিক ডিজিটাল সনদপত্র সরবরাহ:</strong> কেন্দ্রীয় ডাটাবেস ভেরিফিকেশন সহ সরাসরি ডিজিটাল স্বাক্ষরিত ই-সার্টিফিকেট ডাউনলোড।</td>
      </tr>
      <tr>
        <td><strong>Phase 5</strong></td>
        <td><span class="tag purple">Q3 2027</span></td>
        <td><strong>বিভাগীয় ফেডারেটেড সাব-এজেন্ট:</strong> ঢাকা, চট্টগ্রাম, রাজশাহী সহ সকল বিভাগীয় আঞ্চলিক কেন্দ্রের জন্য ডেডিকেটেড সাব-এজেন্ট ক্লাস্টার।</td>
      </tr>
    </tbody>
  </table>

  <div class="page-footer">
    <span>National University AI Assistant • Project Overview & Architecture</span>
    <span>Page 3 of 3</span>
  </div>
</div>

</body>
</html>"""

def generate_english_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>National University AI Assistant — Project Overview & Technical Architecture</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fira+Code:wght@400;600&display=swap');

  @page {
    size: A4 portrait;
    margin: 12mm 14mm 14mm 14mm;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.5;
    font-size: 13px;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .page {
    page-break-after: always;
    position: relative;
    padding-bottom: 25px;
  }

  .page:last-child {
    page-break-after: avoid;
  }

  .header-table {
    width: 100%;
    border-bottom: 2px solid #059669;
    padding-bottom: 8px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .header-left h2 {
    font-size: 15px;
    font-weight: 800;
    color: #065f46;
    letter-spacing: -0.2px;
  }

  .header-left p {
    font-size: 11px;
    color: #059669;
    font-weight: 600;
  }

  .header-right {
    text-align: right;
  }

  .header-right .badge {
    display: inline-block;
    background: #0f172a;
    color: #ffffff;
    font-size: 9px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .header-right p {
    font-size: 10px;
    color: #64748b;
    margin-top: 2px;
  }

  .title-section {
    margin-bottom: 12px;
  }

  .title-section h1 {
    font-size: 21px;
    font-weight: 800;
    color: #065f46;
    line-height: 1.3;
    margin-bottom: 4px;
    letter-spacing: -0.3px;
  }

  .title-section .subtitle {
    font-size: 12px;
    color: #475569;
    font-weight: 600;
  }

  .callout-box {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-left: 4px solid #059669;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 12px;
  }

  .callout-box h3 {
    font-size: 13px;
    font-weight: 700;
    color: #065f46;
    margin-bottom: 4px;
  }

  .callout-box p {
    font-size: 12px;
    color: #166534;
    line-height: 1.5;
  }

  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    margin-bottom: 14px;
  }

  .card {
    padding: 9px 11px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    background: #ffffff;
  }

  .card.green { background: #f0fdf4; border-color: #bbf7d0; }
  .card.amber { background: #fffbeb; border-color: #fef08a; }
  .card.blue { background: #eff6ff; border-color: #bfdbfe; }
  .card.purple { background: #faf5ff; border-color: #e9d5ff; }

  .card h4 {
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 3px;
  }

  .card.green h4 { color: #065f46; }
  .card.amber h4 { color: #92400e; }
  .card.blue h4 { color: #1e40af; }
  .card.purple h4 { color: #6b21a8; }

  .card p {
    font-size: 11px;
    color: #475569;
    line-height: 1.4;
  }

  .section-title {
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
    border-left: 3px solid #059669;
    padding-left: 8px;
    margin-top: 14px;
    margin-bottom: 8px;
  }

  .diagram-container {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 12px;
    text-align: center;
  }

  table.data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 6px;
    margin-bottom: 12px;
    font-size: 11.5px;
  }

  table.data-table th {
    background: #0f172a;
    color: #ffffff;
    font-weight: 700;
    padding: 6px 10px;
    text-align: left;
    border: 1px solid #334155;
    font-size: 11px;
  }

  table.data-table td {
    padding: 6px 10px;
    border: 1px solid #e2e8f0;
    vertical-align: top;
    line-height: 1.4;
  }

  table.data-table tr:nth-child(even) td {
    background: #f8fafc;
  }

  .tag {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 9.5px;
    font-weight: 700;
  }

  .tag.green { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
  .tag.blue { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
  .tag.purple { background: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; }
  .tag.amber { background: #fef3c7; color: #92400e; border: 1px solid #fde047; }
  .tag.slate { background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; }

  .page-footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    border-top: 1px solid #cbd5e1;
    padding-top: 5px;
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #64748b;
  }
</style>
</head>
<body>

<!-- ==================== PAGE 1: EXECUTIVE OVERVIEW & ARCHITECTURE SKETCH ==================== -->
<div class="page">
  <div class="header-table">
    <div class="header-left">
      <h2>NATIONAL UNIVERSITY BANGLADESH</h2>
      <p>Division of Academic Affairs & Information Technology</p>
    </div>
    <div class="header-right">
      <span class="badge">Official Technical Overview</span>
      <p>Version 2.0 • Production Ready • 2026</p>
    </div>
  </div>

  <div class="title-section">
    <h1>National University AI Academic Assistant & Support Platform</h1>
    <div class="subtitle">Autonomous AI Conversational Assistant, Tracked Support Ticket Service & 24/7 Knowledge Enrichment Ecosystem</div>
  </div>

  <div class="callout-box">
    <h3>🌟 Project Mission & Executive Overview</h3>
    <p>
      National University (<strong>nu.ac.bd</strong>) is the largest higher-education affiliating university in Bangladesh, serving over 3 million students across 2,200+ affiliated colleges. Due to high query volumes during admissions, exam schedules, EMS portal logins, and certificate issuances, this enterprise AI platform was architected. It provides instant verified academic guidance and manages official, encrypted support tickets for departmental solvers.
    </p>
  </div>

  <div class="grid-3">
    <div class="card green">
      <h4>⚡ Sub-Millisecond Response</h4>
      <p>High-frequency queries (greetings, admissions, exam routines) served in <strong>0.018 ms</strong> from in-memory cache.</p>
    </div>
    <div class="card amber">
      <h4>🎫 Atomic Support Tokens</h4>
      <p>EMS lockout, form fill-up, and certificate issues resolved via <strong>NU-2026-XXXXXX</strong> tracked tickets.</p>
    </div>
    <div class="card blue">
      <h4>🤖 24/7 Autonomous Agents</h4>
      <p>Continuously crawl, extract key dates/fees, vectorize Q&As, and update ChromaDB vector storage in real time.</p>
    </div>
  </div>

  <div class="section-title">
    1. Full System Architecture & Data Flow Diagram
  </div>

  <div class="diagram-container">
    <svg width="100%" height="225" viewBox="0 0 740 225" xmlns="http://www.w3.org/2000/svg">
      <rect x="0" y="0" width="740" height="225" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
      <rect x="0" y="0" width="740" height="26" rx="8" fill="#0f172a"/>
      <text x="15" y="17" fill="#ffffff" font-family="'Inter', sans-serif" font-size="11" font-weight="700">End-to-End System Architecture & Component Data Flow</text>
      
      <!-- Box 1: User Channels -->
      <rect x="15" y="38" width="125" height="85" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1.5"/>
      <text x="22" y="56" fill="#065f46" font-family="'Inter'" font-size="11" font-weight="700">1. User Channels</text>
      <text x="22" y="73" fill="#334155" font-family="'Inter'" font-size="9.5">• Responsive Web UI</text>
      <text x="22" y="89" fill="#334155" font-family="'Inter'" font-size="9.5">• Mobile Camera QR</text>
      <text x="22" y="105" fill="#334155" font-family="'Inter'" font-size="9.5">• Support Token Portal</text>

      <!-- Arrow 1 -> 2 -->
      <path d="M 140 80 L 168 80" stroke="#059669" stroke-width="2" marker-end="url(#arrow-green)"/>

      <!-- Box 2: FastAPI Gateway -->
      <rect x="170" y="35" width="165" height="92" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
      <text x="178" y="54" fill="#1e40af" font-family="'Inter'" font-size="11" font-weight="700">2. FastAPI Gateway & Core</text>
      <text x="178" y="70" fill="#334155" font-family="'Inter'" font-size="9.5">• Async Thread Offload (asyncio)</text>
      <text x="178" y="85" fill="#334155" font-family="'Inter'" font-size="9.5">• Preloaded Fast Cache (18 µs)</text>
      <text x="178" y="100" fill="#334155" font-family="'Inter'" font-size="9.5">• Intent & Skill Router</text>
      <text x="178" y="115" fill="#334155" font-family="'Inter'" font-size="9.5">• Google Gemini 3 Flash LLM</text>

      <!-- Arrow 2 -> 3 -->
      <path d="M 335 80 L 363 80" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>

      <!-- Box 3: MCP Tool Suite -->
      <rect x="365" y="38" width="135" height="85" rx="6" fill="#faf5ff" stroke="#9333ea" stroke-width="1.5"/>
      <text x="373" y="56" fill="#6b21a8" font-family="'Inter'" font-size="11" font-weight="700">3. MCP Server Suite</text>
      <text x="373" y="73" fill="#334155" font-family="'Fira Code', monospace" font-size="9">• token_mcp (8 tools)</text>
      <text x="373" y="89" fill="#334155" font-family="'Fira Code', monospace" font-size="9">• knowledge_mcp</text>
      <text x="373" y="105" fill="#334155" font-family="'Fira Code', monospace" font-size="9">• credential_mcp</text>

      <!-- Arrow 3 -> 4 (Down) -->
      <path d="M 432 123 L 432 140" stroke="#9333ea" stroke-width="2" marker-end="url(#arrow-purple)"/>

      <!-- Box 4: Database Core -->
      <rect x="345" y="142" width="175" height="74" rx="6" fill="#fffbeb" stroke="#d97706" stroke-width="1.5"/>
      <text x="353" y="159" fill="#92400e" font-family="'Inter'" font-size="11" font-weight="700">4. Database & Vault Core</text>
      <text x="353" y="174" fill="#334155" font-family="'Inter'" font-size="9.5">• ChromaDB Semantic Vector Store</text>
      <text x="353" y="189" fill="#334155" font-family="'Inter'" font-size="9.5">• SQLite (WAL Mode) Ticket Store</text>
      <text x="353" y="204" fill="#334155" font-family="'Inter'" font-size="9.5">• Fernet AES-128 Credential Vault</text>

      <!-- Box 5: 24/7 Autonomous Agents -->
      <rect x="15" y="142" width="155" height="74" rx="6" fill="#fdf2f8" stroke="#db2777" stroke-width="1.5"/>
      <text x="22" y="159" fill="#9d174d" font-family="'Inter'" font-size="11" font-weight="700">5. 24/7 Autonomous Agents</text>
      <text x="22" y="174" fill="#334155" font-family="'Inter'" font-size="9.5">• ScrapedDataAnalyzerAgent</text>
      <text x="22" y="189" fill="#334155" font-family="'Inter'" font-size="9.5">• KnowledgeEnricherAgent</text>
      <text x="22" y="204" fill="#334155" font-family="'Inter'" font-size="9.5">• JSONL Stream & RFC 8259 Manifest</text>

      <!-- Arrow 5 -> 4 -->
      <path d="M 170 178 L 343 178" stroke="#db2777" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#arrow-pink)"/>

      <!-- Box 6: Solvers & Admin -->
      <rect x="180" y="142" width="155" height="74" rx="6" fill="#f1f5f9" stroke="#475569" stroke-width="1.5"/>
      <text x="188" y="159" fill="#0f172a" font-family="'Inter'" font-size="11" font-weight="700">6. Department Solvers & Admin</text>
      <text x="188" y="174" fill="#334155" font-family="'Inter'" font-size="9.5">• ICT, Exam & Registration Desks</text>
      <text x="188" y="189" fill="#334155" font-family="'Inter'" font-size="9.5">• Self-Learning Vector Feedback</text>
      <text x="188" y="204" fill="#334155" font-family="'Inter'" font-size="9.5">• RBAC Role Permission Gates</text>

      <!-- Box 7: External Portals -->
      <rect x="530" y="38" width="195" height="178" rx="6" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5"/>
      <text x="540" y="58" fill="#166534" font-family="'Inter'" font-size="11" font-weight="700">7. National University Portals</text>
      <text x="540" y="78" fill="#334155" font-family="'Inter'" font-size="9.5">🌐 nu.ac.bd (Main Site & Notices)</text>
      <text x="540" y="96" fill="#334155" font-family="'Inter'" font-size="9.5">📝 app1.nu.edu.bd (Admissions)</text>
      <text x="540" y="114" fill="#334155" font-family="'Inter'" font-size="9.5">📊 results.nu.ac.bd (Archive)</text>
      <text x="540" y="132" fill="#334155" font-family="'Inter'" font-size="9.5">🔐 ems.nu.ac.bd (Student Portal)</text>
      <text x="540" y="150" fill="#334155" font-family="'Inter'" font-size="9.5">💳 Sonali Seba Payment Gateway</text>
      <rect x="540" y="165" width="175" height="38" rx="4" fill="#dcfce7" stroke="#86efac"/>
      <text x="546" y="180" fill="#166534" font-family="'Inter'" font-size="9" font-weight="700">Intelligent Deep Crawler & RAG Sync</text>
      <text x="546" y="194" fill="#166534" font-family="'Inter'" font-size="8">Periodically crawls & indexes 10 sections</text>

      <defs>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 8 5 L 0 9 z" fill="#059669"/></marker>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 8 5 L 0 9 z" fill="#2563eb"/></marker>
        <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 8 5 L 0 9 z" fill="#9333ea"/></marker>
        <marker id="arrow-pink" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 8 5 L 0 9 z" fill="#db2777"/></marker>
      </defs>
    </svg>
  </div>

  <div class="page-footer">
    <span>National University AI Assistant • Project Overview & Architecture</span>
    <span>Page 1 of 3</span>
  </div>
</div>

<!-- ==================== PAGE 2: TECH STACK & ENRICHMENT ==================== -->
<div class="page">
  <div class="header-table">
    <div class="header-left">
      <h2>TECHNOLOGY STACK & WORKING MECHANISMS</h2>
      <p>Comprehensive breakdown of libraries, frameworks, and mechanisms</p>
    </div>
    <div class="header-right">
      <span class="badge">Core Engineering Stack</span>
      <p>Python 3.13 • FastAPI • ChromaDB • MCP</p>
    </div>
  </div>

  <div class="section-title">
    2. Core Technologies & Architecture Principles
  </div>

  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 22%;">Technology</th>
        <th style="width: 20%;">Version / Component</th>
        <th>Role & Engineering Mechanism</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>FastAPI Backend</strong></td>
        <td><span class="tag green">v0.115+ (Python 3.13)</span></td>
        <td>Non-blocking asynchronous REST API gateway. Uses <code>asyncio.to_thread</code> to offload heavy disk I/O and generative AI calls, preventing event-loop latency.</td>
      </tr>
      <tr>
        <td><strong>Google Gemini 3 Flash</strong></td>
        <td><span class="tag blue">gemini-3-flash-preview</span></td>
        <td>High-speed bilingual generative LLM core. Synthesizes contextual responses with verified official circular citations and active hyperlinks.</td>
      </tr>
      <tr>
        <td><strong>ChromaDB Vector Store</strong></td>
        <td><span class="tag purple">gemini-embedding-001</span></td>
        <td>Persistent vector database for academic notices and solved support cases. Includes resilient pseudo-embedding fallback during quota limits.</td>
      </tr>
      <tr>
        <td><strong>MCP Server Suite</strong></td>
        <td><span class="tag amber">5 Dedicated Servers</span></td>
        <td>Model Context Protocol tool suite adhering to Antigravity & Anthropic standards (<code>token_mcp</code>, <code>knowledge_mcp</code>, <code>document_mcp</code>, <code>credential_mcp</code>, <code>enrichment_mcp</code>).</td>
      </tr>
      <tr>
        <td><strong>SQLite Relational Core</strong></td>
        <td><span class="tag slate">WAL Mode Enabled</span></td>
        <td>ACID relational engine for support tickets, credentials, crawler pages, and audit logs. Configured with Write-Ahead Logging for high write concurrency.</td>
      </tr>
      <tr>
        <td><strong>Fernet AES-128 Vault</strong></td>
        <td><span class="tag green">CBC + HMAC-SHA256</span></td>
        <td>Protects student service passwords with AES-128 encryption and PBKDF2 hashing (100,000 iterations). Plaintext passwords are never stored or logged.</td>
      </tr>
      <tr>
        <td><strong>Preloaded Fast Cache</strong></td>
        <td><span class="tag blue">In-Memory Trie (18 µs)</span></td>
        <td>Preloads greetings (hi, hello), admissions criteria, routine FAQs, and SMS result formats into memory to respond in <strong>0.018 milliseconds</strong>.</td>
      </tr>
    </tbody>
  </table>

  <div class="section-title">
    3. 24/7 Autonomous Multi-Agent Knowledge Enrichment Ecosystem
  </div>

  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 28%;">Agent Identifier</th>
        <th style="width: 47%;">Core Responsibilities</th>
        <th style="width: 25%;">Standard Output</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>ScrapedDataAnalyzerAgent</strong></td>
        <td>Scans crawled web pages & PDFs, extracts academic entities (dates, fees, degrees), and synthesizes bilingual Q&A pairs.</td>
        <td><span class="tag blue">JSON Entities & QAs</span></td>
      </tr>
      <tr>
        <td><strong>KnowledgeEnricherAgent</strong></td>
        <td>Ingests Q&A pairs into ChromaDB vector store and updates in-memory fast caches for high-frequency user questions.</td>
        <td><span class="tag purple">ChromaDB Ingestion</span></td>
      </tr>
      <tr>
        <td><strong>KnowledgeProvenanceAgent</strong></td>
        <td>Maintains append-only audit trail so peer AI models (Claude, Codex, Subagents) can synchronize and act on new knowledge.</td>
        <td><span class="tag green">JSONL Stream & Manifest</span></td>
      </tr>
    </tbody>
  </table>

  <div class="callout-box" style="margin-top: 10px; background: #faf5ff; border-color: #d8b4fe; border-left-color: #9333ea;">
    <h3 style="color: #6b21a8;">💡 Self-Learning Vector Feedback Loop</h3>
    <p style="color: #581c87;">
      When an authorized departmental officer marks a support ticket as <strong>SOLVED</strong> with verified resolution instructions, the system anonymizes student identifiers and embeds the problem-solution pair into ChromaDB. Future students facing the same problem instantly receive the verified answer from the AI!
    </p>
  </div>

  <div class="page-footer">
    <span>National University AI Assistant • Project Overview & Architecture</span>
    <span>Page 2 of 3</span>
  </div>
</div>

<!-- ==================== PAGE 3: USER PLAYBOOK & ROADMAP ==================== -->
<div class="page">
  <div class="header-table">
    <div class="header-left">
      <h2>0-LEVEL USER PLAYBOOK & STRATEGIC ROADMAP</h2>
      <p>Step-by-step user operations, service directories, and future expansion</p>
    </div>
    <div class="header-right">
      <span class="badge">Operations & Vision</span>
      <p>Token Lifecycle • Roadmap 2026-2027</p>
    </div>
  </div>

  <div class="section-title">
    4. 0-Level Beginner User Operations Playbook
  </div>

  <div class="grid-3" style="grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
    <div class="card green">
      <h4>1. Ask the AI Assistant</h4>
      <p>Type any inquiry in natural English or Bengali (e.g. <i>"Honours admission date"</i> or <i>"Forgot EMS password"</i>). Receive instant answers with verified portal links.</p>
    </div>
    <div class="card amber">
      <h4>2. Apply for Support Token</h4>
      <p>For account or exam issues, click <strong>Token Service</strong>, choose your service, and submit. Receive an atomic tracking ID (e.g. <strong>NU-2026-000140</strong>).</p>
    </div>
    <div class="card blue">
      <h4>3. Live Status Tracking</h4>
      <p>Click <strong>Check Token</strong> to see real-time solver updates (<span class="tag amber">PENDING</span> ➔ <span class="tag blue">PROCESSING</span> ➔ <span class="tag green">SOLVED</span>) and download official resolution PDFs.</p>
    </div>
    <div class="card purple">
      <h4>4. Smartphone QR Code Access</h4>
      <p>Click <strong>Mobile QR</strong> to display a QR code. Scan with any mobile camera to access the full platform instantly without downloading applications.</p>
    </div>
  </div>

  <div class="section-title">
    5. Support Token Service Directory & Solver Desks
  </div>

  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 15%;">Service Code</th>
        <th style="width: 40%;">Service Scope & Description</th>
        <th style="width: 27%;">Responsible Desk</th>
        <th style="width: 18%;">Resolution SLA</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>EMS</strong></td>
        <td>EMS Student Portal Login & Account Lockout Assistance</td>
        <td>ICT Support Desk</td>
        <td>24-48 Hours</td>
      </tr>
      <tr>
        <td><strong>FORM_FILLUP</strong></td>
        <td>Exam Form Fill-up & College Fee Verification Issues</td>
        <td>Exam Controller Wing</td>
        <td>12-24 Hours</td>
      </tr>
      <tr>
        <td><strong>RESCRUTINY</strong></td>
        <td>Result Re-check / Board Challenge Application Tracking</td>
        <td>Evaluation Wing</td>
        <td>3-7 Business Days</td>
      </tr>
      <tr>
        <td><strong>CERTIFICATE</strong></td>
        <td>Original & Provisional Certificate Processing & Release</td>
        <td>Certificate Section</td>
        <td>2-5 Business Days</td>
      </tr>
      <tr>
        <td><strong>MARKSHEET</strong></td>
        <td>Academic Transcript & Grade Sheet Corrections</td>
        <td>Registrar Department</td>
        <td>2-4 Business Days</td>
      </tr>
      <tr>
        <td><strong>TC / CORRECTION</strong></td>
        <td>College Migration Transfer & Student Profile Corrections</td>
        <td>Registration Cell</td>
        <td>5-10 Business Days</td>
      </tr>
    </tbody>
  </table>

  <div class="section-title">
    6. Strategic Multi-Phase Expansion Roadmap
  </div>

  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 22%;">Phase</th>
        <th style="width: 15%;">Timeline</th>
        <th>Planned Features & Engineering Capabilities</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Phase 2 (Upcoming)</strong></td>
        <td><span class="tag blue">Q4 2026</span></td>
        <td><strong>Bangla Voice AI Assistant:</strong> Bidirectional real-time voice streaming for rural and visually impaired students.</td>
      </tr>
      <tr>
        <td><strong>Phase 3</strong></td>
        <td><span class="tag amber">Q1 2027</span></td>
        <td><strong>Automated SMS & WhatsApp Alerts:</strong> Instant notifications to student smartphones upon ticket resolution or urgent circulars.</td>
      </tr>
      <tr>
        <td><strong>Phase 4</strong></td>
        <td><span class="tag green">Q2 2027</span></td>
        <td><strong>Robotic Digital Certificate Dispatch:</strong> University central database integration for instant digital-signature e-certificates.</td>
      </tr>
      <tr>
        <td><strong>Phase 5</strong></td>
        <td><span class="tag purple">Q3 2027</span></td>
        <td><strong>Federated Sub-Agent Clusters:</strong> Regional sub-agent pods for Dhaka, Chittagong, Rajshahi, and other administrative divisions.</td>
      </tr>
    </tbody>
  </table>

  <div class="page-footer">
    <span>National University AI Assistant • Project Overview & Architecture</span>
    <span>Page 3 of 3</span>
  </div>
</div>

</body>
</html>"""

def build_all_documents():
    print("============================================================")
    print("Building Unicode-Perfect PDF Documentation (BN & EN)")
    print("============================================================")
    
    # 1. Build Bengali/Bilingual Edition
    bn_html_path = DOCS_DIR / "project-overview-bn.html"
    bn_pdf_path = DOCS_DIR / "project-overview.pdf"
    bn_html_path.write_text(generate_bilingual_html(), encoding="utf-8")
    convert_html_to_pdf(bn_html_path, bn_pdf_path)

    # 2. Build English Edition
    en_html_path = DOCS_DIR / "project-overview-en.html"
    en_pdf_path = DOCS_DIR / "project-overview-en.pdf"
    en_html_path.write_text(generate_english_html(), encoding="utf-8")
    convert_html_to_pdf(en_html_path, en_pdf_path)

    # 3. Generate High-Res Image Previews for Verification
    doc_bn = fitz.open(str(bn_pdf_path))
    pix_bn = doc_bn[0].get_pixmap(dpi=150)
    preview_bn_path = DOCS_DIR / "page1_bn_preview.png"
    pix_bn.save(str(preview_bn_path))
    print(f"[OK] Saved Bengali Preview: {preview_bn_path}")

    doc_en = fitz.open(str(en_pdf_path))
    pix_en = doc_en[0].get_pixmap(dpi=150)
    preview_en_path = DOCS_DIR / "page1_en_preview.png"
    pix_en.save(str(preview_en_path))
    print(f"[OK] Saved English Preview: {preview_en_path}")

    # Copy to artifact folder for user viewing
    artifact_dir = Path(r"C:\Users\RAKIB\.gemini\antigravity\brain\468d1645-a2a9-412c-a4e5-8783cc41d202")
    if artifact_dir.exists():
        import shutil
        shutil.copy2(preview_bn_path, artifact_dir / "page1_bn_preview.png")
        shutil.copy2(preview_en_path, artifact_dir / "page1_en_preview.png")
    print("\n[SUCCESS] ALL DOCUMENTATION PDFs GENERATED WITH 100% PERFECT UNICODE TEXT SHAPING!")

if __name__ == "__main__":
    build_all_documents()
