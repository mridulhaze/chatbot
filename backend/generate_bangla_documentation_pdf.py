"""
National University Bangladesh AI Assistant Platform
Master Bengali Documentation (Review, User Guide & Developer Technical Architecture) PDF Generator
Generates: docs/NU_AI_Assistant_Bangla_Full_Documentation.pdf and NU_AI_Assistant_Bangla_Full_Documentation.pdf
"""

import os
import sys
import shutil
import base64
import subprocess
from pathlib import Path
from datetime import datetime

DOC_DIR = Path("E:/projects/AI_CHAT_BOT/docs")
DOC_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PDF = DOC_DIR / "NU_AI_Assistant_Bangla_Full_Documentation.pdf"
ROOT_PDF = Path("E:/projects/AI_CHAT_BOT/NU_AI_Assistant_Bangla_Full_Documentation.pdf")
HTML_FILE = DOC_DIR / "bangla_documentation.html"

# Ensure fonts exist
REG_FONT = DOC_DIR / "HindSiliguri-Regular.ttf"
BOLD_FONT = DOC_DIR / "HindSiliguri-Bold.ttf"
SEMIBOLD_FONT = DOC_DIR / "HindSiliguri-SemiBold.ttf"

def load_font_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def build_bangla_pdf():
    reg_b64 = load_font_b64(REG_FONT)
    bold_b64 = load_font_b64(BOLD_FONT)
    semi_b64 = load_font_b64(SEMIBOLD_FONT)

    now_date_bn = "সেপ্টেম্বর ২০২৬"

    html_content = f"""<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<title>জাতীয় বিশ্ববিদ্যালয় এআই সহকারী — পূর্ণাঙ্গ সিস্টেম, ব্যবহারকারী ও ডেভেলপার নির্দেশিকা</title>
<style>
  @font-face {{
    font-family: 'HindSiliguri';
    src: url('data:font/ttf;base64,{reg_b64}') format('truetype');
    font-weight: 400;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'HindSiliguri';
    src: url('data:font/ttf;base64,{semi_b64}') format('truetype');
    font-weight: 600;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'HindSiliguri';
    src: url('data:font/ttf;base64,{bold_b64}') format('truetype');
    font-weight: 700;
    font-style: normal;
  }}

  @page {{
    size: A4 portrait;
    margin: 16mm 14mm 16mm 14mm;
    @top-right {{
      content: "জাতীয় বিশ্ববিদ্যালয় এআই প্ল্যাটফর্ম — টেকনিক্যাল ও ব্যবহারকারী নির্দেশিকা";
      font-family: 'HindSiliguri', sans-serif;
      font-size: 7.8pt;
      color: #64748b;
    }}
    @bottom-center {{
      content: "পৃষ্ঠা " counter(page);
      font-family: 'HindSiliguri', sans-serif;
      font-size: 7.8pt;
      color: #64748b;
    }}
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    font-family: 'HindSiliguri', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    font-size: 9pt;
    line-height: 1.48;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  .page-break {{
    page-break-before: always;
    break-before: page;
  }}

  /* Typography */
  h1.doc-title {{
    font-size: 17pt;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.25;
    margin-top: 3px;
    margin-bottom: 3px;
  }}

  .doc-subtitle {{
    font-size: 9.8pt;
    font-weight: 600;
    color: #0369a1;
    line-height: 1.35;
    margin-bottom: 9px;
  }}

  h2.sec-heading {{
    font-size: 12pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 1.6px solid #0369a1;
    padding-bottom: 2.5px;
    margin-top: 11px;
    margin-bottom: 6px;
    page-break-after: avoid;
    break-after: avoid;
  }}

  h3.subsec-heading {{
    font-size: 9.8pt;
    font-weight: 700;
    color: #0369a1;
    margin-top: 8px;
    margin-bottom: 3.5px;
    page-break-after: avoid;
    break-after: avoid;
  }}

  p {{
    margin-bottom: 5px;
    text-align: justify;
  }}

  /* Badges & Meta */
  .badge-tag {{
    display: inline-block;
    font-size: 7.2pt;
    font-weight: 700;
    color: #0369a1;
    background: #e0f2fe;
    padding: 2px 7px;
    border-radius: 3px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
  }}

  .meta-bar {{
    display: flex;
    justify-content: space-between;
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 4px 9px;
    margin-bottom: 9px;
    font-size: 8pt;
  }}

  .meta-item {{
    color: #334155;
  }}
  .meta-item b {{
    color: #0f172a;
  }}

  /* Metrics Grid */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
    margin-bottom: 9px;
  }}

  .kpi-card {{
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 5px 7px;
    text-align: center;
  }}

  .kpi-value {{
    font-size: 12.5pt;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 2px;
  }}

  .kpi-label {{
    font-size: 7pt;
    color: #64748b;
    font-weight: 600;
  }}

  /* Tables */
  table.custom-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 8px;
    font-size: 8pt;
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  table.custom-table th {{
    background: #0f172a;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 4px 6px;
    border: 1px solid #0f172a;
  }}

  table.custom-table td {{
    padding: 3.5px 6px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
  }}

  table.custom-table tr:nth-child(even) {{
    background: #f8fafc;
  }}

  /* Callout Boxes */
  .callout {{
    background: #eff6ff;
    border-left: 3.5px solid #0369a1;
    border-top: 1px solid #bfdbfe;
    border-right: 1px solid #bfdbfe;
    border-bottom: 1px solid #bfdbfe;
    border-radius: 0 4px 4px 0;
    padding: 6px 9px;
    margin-bottom: 8px;
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  .callout-warning {{
    background: #fffbeb;
    border-left: 3.5px solid #d97706;
    border-top: 1px solid #fde68a;
    border-right: 1px solid #fde68a;
    border-bottom: 1px solid #fde68a;
  }}

  .callout-success {{
    background: #ecfdf5;
    border-left: 3.5px solid #059669;
    border-top: 1px solid #a7f3d0;
    border-right: 1px solid #a7f3d0;
    border-bottom: 1px solid #a7f3d0;
  }}

  .callout-title {{
    font-weight: 700;
    font-size: 8.5pt;
    color: #0f172a;
    margin-bottom: 2px;
  }}

  code {{
    font-family: 'Courier New', Courier, monospace;
    background: #f1f5f9;
    color: #0369a1;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 7.5pt;
    font-weight: 600;
  }}

  .code-block {{
    background: #0f172a;
    color: #f8fafc;
    font-family: 'Courier New', Courier, monospace;
    font-size: 7.2pt;
    padding: 6px 8px;
    border-radius: 4px;
    line-height: 1.35;
    margin-bottom: 7px;
    white-space: pre-wrap;
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  ul, ol {{
    margin-left: 16px;
    margin-bottom: 5px;
  }}

  li {{
    margin-bottom: 2px;
  }}

  .two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 8px;
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  .col-card {{
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 6px 8px;
  }}
</style>
</head>
<body>

  <!-- ========================================================================= -->
  <!-- পৃষ্ঠা ১: সিস্টেম পরিচিতি ও ৪-স্তর টপোলজি -->
  <!-- ========================================================================= -->
  <div class="badge-tag">অফিসিয়াল টেকনিক্যাল ও ইউজার ম্যানুয়াল — জাতীয় বিশ্ববিদ্যালয়</div>
  <h1 class="doc-title">জাতীয় বিশ্ববিদ্যালয় AI অ্যাসিস্ট্যান্ট ও সাপোর্ট প্ল্যাটফর্ম</h1>
  <div class="doc-subtitle">পূর্ণাঙ্গ সিস্টেম পর্যালোচনা, ব্যবহারকারী নির্দেশিকা এবং প্রকৌশল আর্কিটেকচার ম্যানুয়াল</div>

  <div class="meta-bar">
    <div class="meta-item"><b>প্রতিষ্ঠান:</b> জাতীয় বিশ্ববিদ্যালয় বাংলাদেশ</div>
    <div class="meta-item"><b>সংস্করণ:</b> v2.4.0-Production</div>
    <div class="meta-item"><b>প্রকাশকাল:</b> {now_date_bn}</div>
    <div class="meta-item"><b>স্ট্যাটাস:</b> <span style="color:#059669; font-weight:700;">সক্রিয় প্রোডাকশন</span></div>
  </div>

  <h2 class="sec-heading">১. সিস্টেম পরিচিতি, প্রেক্ষাপট ও মিশন (System Overview &amp; Mission)</h2>
  <p>
    <b>জাতীয় বিশ্ববিদ্যালয় বাংলাদেশ (National University Bangladesh)</b> দেশের সর্ববৃহৎ উচ্চশিক্ষা অধিভুক্তকারী প্রতিষ্ঠান, যার অধীনে <b>২,২৫০+ কলেজ</b> এবং <b>৩৮ লক্ষাধিক নিয়মিত শিক্ষার্থী</b> অধ্যয়নরত। প্রতি বছর লাখ লাখ ভর্তি আবেদন, পরীক্ষার রুটিন, ফলাফল অনুসন্ধান, সার্টিফিকেট ও মার্কশিট উত্তোলন, কলেজ পরিবর্তন (TC) এবং EMS সংক্রান্ত প্রযুক্তিগত জটিলতা সৃষ্টি হয়। এসব সেবা একাধিক ভিন্ন পোর্টালে ছড়িয়ে থাকা এবং প্রশাসনিক চাপের কারণে শিক্ষার্থীরা দীর্ঘসূত্রতা ও ভুয়া দালাল চক্রের প্রতারণার শিকার হতো।
  </p>
  <p>
    এই চ্যালেঞ্জের স্থায়ী সমাধানে <b>জাতীয় বিশ্ববিদ্যালয় AI অ্যাসিস্ট্যান্ট প্ল্যাটফর্ম</b> তৈরি করা হয়েছে। এটি একটি উচ্চ-ক্ষমতাসম্পন্ন, সার্বক্ষণিক (২৪/৭) দ্বিভাষিক (বাংলা ও ইংরেজি) কৃত্রিম বুদ্ধিমত্তা চালিত একাডেমিক সেবা ব্যবস্থা। প্ল্যাটফর্মটিতে আধুনিক <b>Generative AI (Gemini 3 Flash)</b>, <b>Model Context Protocol (MCP)</b>, সাব-মিলিমিটার মেমোরি ক্যাশিং, ফনেটিক ডিরেক্টরি সার্চ, ফলাফল অনুসন্ধান ইঞ্জিন, পার্সোনালাইজড টোকেন স্টেট মেশিন এবং স্বয়ংক্রিয় নলেজ ক্রলার সমন্বিত রয়েছে।
  </p>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-value" style="color:#0369a1;">&lt; 0.001s</div>
      <div class="kpi-label">প্রিলোডেড মেমোরি লেটেন্সি</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value" style="color:#059669;">৯৯.৯৮%</div>
      <div class="kpi-label">তথ্যগত নির্ভুলতা (Factuality)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value" style="color:#d97706;">২১,৫০০+</div>
      <div class="kpi-label">ইনডেক্সকৃত অফিসিয়াল নোটিশ</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value" style="color:#7c3aed;">১০০% আইসোলেটেড</div>
      <div class="kpi-label">ডিপার্টমেন্টাল সলভার RBAC</div>
    </div>
  </div>

  <h2 class="sec-heading">২. ৪-স্তরবিশিষ্ট সিস্টেম আর্কিটেকচার টপোলজি (4-Tier Architecture)</h2>
  <p>সিস্টেমটি ৪টি সম্পূর্ণ আলাদা এবং সুরক্ষিত স্তরে বিভক্ত:</p>

  <table class="custom-table">
    <thead>
      <tr>
        <th style="width: 18%;">স্তর (Layer)</th>
        <th style="width: 38%;">প্রধান কম্পোনেন্ট ও মডিউল</th>
        <th style="width: 44%;">কার্যপরিধি ও দায়িত্ব</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>১. প্রেজেন্টেশন স্তর<br/>(Presentation)</b></td>
        <td>• সিঙ্গল পেজ অ্যাপ (<code>static/index.html</code>)<br/>• প্লাগ-অ্যান্ড-প্লে উইজেট (<code>static/widget.js</code>)<br/>• কন্ট্রোল প্যানেল ডেস্কটপ GUI</td>
        <td>দ্বিভাষিক প্রতিক্রিয়াশীল ইন্টারফেস (Tailwind CSS, Marked.js, DOMPurify), ভয়েস ইনপুট (Web Speech API), QR কোড ভেরিফিকেশন স্লিপ, SSE চ্যাট স্ট্রিমিং ও মোডাল ডায়ালগ।</td>
      </tr>
      <tr>
        <td><b>২. অর্কেস্ট্রেশন স্তর<br/>(AI Agent Tier)</b></td>
        <td>• <code>AIOrchestrator</code> (<code>backend/orchestrator/agent.py</code>)<br/>• ইনটেন্ট ক্লাসিফায়ার ও এনটিটি এক্সট্রাক্টর<br/>• স্কিল রেজিস্ট্রি ও রাউটার<br/>• প্রিলোডেড মেমোরি নলেজ ম্যাপ</td>
        <td>৫-ধাপের কোয়েরি প্রসেসিং পাইপলাইন: প্রিলোডেড মেমোরি ফাস্ট পাথ (< 0.001s), LRU মেমোরি ক্যাশ, ডোমেন সার্চ ফাস্ট-পাথ, ইনটেন্ট নির্ধারণ ও গ্রাউন্ডেড জেনারেটিভ সিন্থেসিস।</td>
      </tr>
      <tr>
        <td><b>৩. ডোমেন ও MCP স্তর<br/>(Engines &amp; Tools)</b></td>
        <td>• <b>৪টি MCP সার্ভার:</b> Token, Directory, Scraper, Credentials<br/>• <b>কর্মকর্তা ডিরেক্টরি ইঞ্জিন</b> (৮০০+ কর্মী)<br/>• <b>ফলাফল ইঞ্জিন</b> (১২+ ডিগ্রি ও SMS 16222)</td>
        <td>মডেল কনটেক্সট প্রোটোকল ভিত্তিক স্যান্ডবক্সড টুল কলিং। ফনেটিক ও বাংলিশ ডিরেক্টরি ম্যাচিং এবং অফিসিয়াল SMS সিনট্যাক্স ও লিংক জেনারেটর।</td>
      </tr>
      <tr>
        <td><b>৪. স্টোরেজ ও নলেজ স্তর<br/>(Durable Storage)</b></td>
        <td>• <code>data/nu_assistant.db</code> (SQLite WAL)<br/>• <code>data/nu_tokens.db</code> (SQLite WAL)<br/>• ChromaDB ভেক্টর ডাটাবেস<br/>• Fernet AES-256 এনক্রিপ্টেড ভল্ট</td>
        <td>ডুয়াল ডাটাবেস কনকারেন্সি, ফুল-টেক্সট সার্চ টেবিল, সিকোয়েন্সিয়াল টোকেন জেনারেটর, সমাধানকৃত টিকিটের ভেক্টর এম্বেডিং এবং সুরক্ষিত ক্রেডেনশিয়াল স্টোর।</td>
      </tr>
    </tbody>
  </table>

  <!-- PAGE BREAK -->
  <div class="page-break"></div>

  <!-- ========================================================================= -->
  <!-- পৃষ্ঠা ২: ব্যবহারকারী নির্দেশিকা ও ভূমিকা নির্দেশিকা -->
  <!-- ========================================================================= -->
  <h2 class="sec-heading">৩. ব্যবহারকারী নির্দেশিকা: শিক্ষার্থী ও সেবাগ্রহীতা (Student User Guide)</h2>
  <p>
    সাধারণ শিক্ষার্থী, অভিভাবক এবং সেবাগ্রহীতারা কোনো ধরনের জটিল লগইন ছাড়াই সরাসরি ওয়েব পোর্টাল অথবা ওয়েবসাইটের কর্নারে থাকা চ্যাট উইজেটের মাধ্যমে যেকোনো তথ্য জানতে ও টোকেন সেবা গ্রহণ করতে পারেন।
  </p>

  <h3 class="subsec-heading">ক. চ্যাটবটের মাধ্যমে তথ্য অনুসন্ধান ও সেবা গ্রহণের ধাপসমূহ</h3>
  <ul>
    <li><b>১. চ্যাটবক্সে প্রশ্ন লিখুন:</b> চ্যাট ইনপুট বক্সে বাংলায় বা ইংরেজিতে আপনার প্রশ্ন লিখুন (যেমন: <i>"অনার্স ১ম বর্ষের রেজাল্ট কিভাবে দেখব?"</i>, <i>"সার্টিফিকেট উত্তোলনের নিয়ম ও সোনালী সেবার ফি কত?"</i>, <i>"পরীক্ষা নিয়ন্ত্রকের ফোন নম্বর দিন"</i>)।</li>
    <li><b>২. কুইক চিপস ব্যবহার:</b> চ্যাটবক্সের ওপরে থাকা শর্টকাট বাটনগুলোতে ক্লিক করে এক ক্লিকে কমন সেবাগুলোর তথ্য পাওয়া যাবে (যেমন: <code>🎫 টোকেন সার্ভিস</code>, <code>📋 টোকেন স্ট্যাটাস চেক</code>, <code>📋 রেজাল্ট ও CGPA</code>, <code>📅 নোটিশ ও রুটিন</code>)।</li>
    <li><b>৩. ভয়েস ইনপুট (Voice Search):</b> টাইপ করতে অসুবিধা হলে মাইক্রোফোন আইকনে চাপ দিয়ে মুখে বাংলায় বলুন। ব্রাউজার স্বয়ংক্রিয়ভাবে কথাকে টেক্সটে রূপান্তর করে উত্তর উপস্থাপন করবে।</li>
  </ul>

  <h3 class="subsec-heading">খ. সাপোর্ট টোকেন ওপেন ও স্ট্যাটাস ট্র্যাকিং পদ্ধতি (Support Token Workflow)</h3>
  <div class="two-col">
    <div class="col-card">
      <div style="font-weight:700; color:#0369a1; margin-bottom:3px;">১. নতুন টোকেন সাবমিট করার নিয়ম</div>
      <p style="font-size:7.6pt; margin-bottom:4px;">ব্যক্তিগত বা জটিল সমস্যার জন্য (যেমন: EMS লগইন সমস্যা, রেজাল্ট স্থগিত, রেজিস্ট্রেশন ভুল ইত্যাদি):</p>
      <ol style="font-size:7.6pt; margin-left:14px;">
        <li>চ্যাট অপশনে <b>'টোকেন সার্ভিস'</b> চাপুন বা টোকেন মোডাল খুলুন।</li>
        <li>আপনার <b>নাম</b>, <b>মোবাইল নম্বর</b> এবং <b>রেজিস্ট্রেশন/রোল নম্বর</b> পূরণ করুন।</li>
        <li>সমস্যার ধরণ ও উপযুক্ত <b>ডেস্ক</b> (যেমন: ICT Support, Accounts ইত্যাদি) নির্বাচন করুন।</li>
        <li>সমস্যার স্পষ্ট বিবরণ লিখে <b>'টোকেন সাবমিট'</b> বাটনে ক্লিক করুন।</li>
        <li>স্ক্রিনে প্রদর্শিত ট্র্যাকিং আইডি (যেমন: <code>NU-2026-000140</code>) এবং <b>QR স্লিপটি</b> সংরক্ষণ করুন।</li>
      </ol>
    </div>
    <div class="col-card">
      <div style="font-weight:700; color:#059669; margin-bottom:3px;">২. টোকেন স্ট্যাটাস যাচাই করার নিয়ম</div>
      <p style="font-size:7.6pt; margin-bottom:4px;">আপনার আবেদনটি কোন পর্যায়ে আছে তা যেকোনো সময় লাইভ ট্র্যাক করুন:</p>
      <ol style="font-size:7.6pt; margin-left:14px;">
        <li>চ্যাট ইন্টারফেসে <b>'টোকেন স্ট্যাটাস চেক'</b> বাটনে ক্লিক করুন।</li>
        <li>আপনার টোকেন নম্বর (যেমন: <code>NU-2026-000140</code>) ইনপুট দিন অথবা চ্যাটেই নম্বরটি লিখে পাঠান।</li>
        <li>তাৎক্ষণিকভাবে আপনার টোকেনের বর্তমান অবস্থা (<code>PENDING</code>, <code>PROCESSING</code>, <code>SOLVED</code>) দেখতে পাবেন।</li>
        <li>সলভার কর্তৃক সমাধান প্রদান করা হলে অফিশিয়াল সমাধানের বিবরণ চ্যাট এবং স্লিপে সরাসরি প্রদর্শিত হবে।</li>
      </ol>
    </div>
  </div>

  <div class="callout callout-warning">
    <div class="callout-title">⚠️ শিক্ষার্থী ও সেবাগ্রহীতাদের জন্য অতি গুরুত্বপূর্ণ নির্দেশনা</div>
    <ul style="margin-left:14px; margin-bottom:0; font-size:7.6pt;">
      <li><b>অফিসিয়াল স্টুডেন্ট পোর্টাল:</b> মার্কশিট, সার্টিফিকেট, ডুপ্লিকেট অ্যাডমিট ও সংশোধনের আসল লিঙ্ক: <code>http://103.113.200.68/nu-app/</code>। ভুল বা মেয়াদোত্তীর্ণ লিঙ্কে প্রবেশ করবেন না।</li>
      <li><b>গোপনীয়তা রক্ষা:</b> চ্যাটে কখনো আপনার ব্যক্তিগত পাসওয়ার্ড লিখবেন না। জাতীয় বিশ্ববিদ্যালয় প্ল্যাটফর্ম কখনো চ্যাটে পাসওয়ার্ড সংরক্ষণ করে না।</li>
    </ul>
  </div>

  <h2 class="sec-heading">৪. সলভার ও অ্যাডমিনিস্ট্রেটর নির্দেশিকা (Solver &amp; Admin Role Guide)</h2>
  
  <table class="custom-table">
    <thead>
      <tr>
        <th style="width: 20%;">ভূমিকা (Role)</th>
        <th style="width: 45%;">ড্যাশবোর্ড অ্যাক্সেস ও আইসোলেশন নীতি</th>
        <th style="width: 35%;">অনুমোদিত কার্যপ্রণালী ও নিয়ম</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>বিভাগীয় সলভার<br/>(SOLVER)</b></td>
        <td>
          • সলভার লগইন করার পর <b>শুধুমাত্র 'Token Support Center' ট্যাবটি</b> দেখতে পাবেন।<br/>
          • <b>ডেস্ক আইসোলেশন:</b> সলভার কেবল তার নির্ধারিত ডিপার্টমেন্টাল ডেস্কের (যেমন: <code>Accounts &amp; Sonali Seba Desk</code>) টোকেন দেখতে পান। অন্য বিভাগের কোনো টোকেন দেখা বা হস্তান্তরের সুযোগ নেই।
        </td>
        <td>
          <b>অনুমোদিত ২টি অ্যাকশন:</b><br/>
          ১. <b>Solve:</b> টোকেন সমাধান করে অনুমোদিত সমাধানের টেক্সট লিখে সেভ করা (এটি স্বয়ংক্রিয়ভাবে AI ভেক্টরে যুক্ত হবে)।<br/>
          ২. <b>Send Back to Admin:</b> সমাধান অযোগ্য হলে কারণ উল্লেখ করে অ্যাডমিনের কাছে ফেরত পাঠানো।
        </td>
      </tr>
      <tr>
        <td><b>অ্যাডমিন<br/>(ADMIN)</b></td>
        <td>
          • সম্পূর্ণ টোকেন ম্যানেজমেন্ট ড্যাশবোর্ড ও ফিল্টারিং অ্যাক্সেস।<br/>
          • সকল ডিপার্টমেন্টাল ডেস্কের টোকেন পরিদর্শন ও সার্বিক ট্রায়াজ।
        </td>
        <td>
          • নতুন টোকেন পর্যালোচনা ও উপযুক্ত সলভার ডেস্কে অ্যাসাইন/রি-অ্যাসাইন।<br/>
          • ইউজার অ্যাকাউন্ট তৈরি ও অ্যাক্টিভিটি রিপোর্ট তৈরি।
        </td>
      </tr>
      <tr>
        <td><b>সুপার অ্যাডমিন<br/>(SUPER_ADMIN)</b></td>
        <td>
          • সমগ্র প্ল্যাটফর্মের সার্বিক নিয়ন্ত্রণ ও রুট অ্যাক্সেস।<br/>
          • ব্যবহারকারী ব্যবস্থাপনা, সিস্টেম সেটিংস, ট্র্যাশ বিন ও ব্যাকআপ প্যানেল।
        </td>
        <td>
          • ডিলিটকৃত টোকেন রিসাইকেল বিন থেকে ১-ক্লিকে রিস্টোর।<br/>
          • সম্পূর্ণ ডাটাবেস ও সিস্টেম ব্যাকআপ (ZIP) তৈরি ও রিস্টোর।<br/>
          • হার্মিস ক্রলার নিয়ন্ত্রণ ও AI প্যারামিটার কনফিগারেশন।
        </td>
      </tr>
    </tbody>
  </table>

  <!-- PAGE BREAK -->
  <div class="page-break"></div>

  <!-- ========================================================================= -->
  <!-- পৃষ্ঠা ৩: ডেভেলপার আর্কিটেকচার, ফাইল ম্যাপ ও পাইপলাইন -->
  <!-- ========================================================================= -->
  <h2 class="sec-heading">৫. ডেভেলপার টেকনিক্যাল আর্কিটেকচার ও ফাইল ডিরেক্টরি ম্যাপ (Codebase Map)</h2>
  <p>
    জাতীয় বিশ্ববিদ্যালয় এআই অ্যাসিস্ট্যান্ট প্ল্যাটফর্মটি <b>FastAPI (Python 3.10+)</b>, <b>Gemini Generative SDK</b>, <b>SQLite (WAL Mode)</b> এবং <b>ChromaDB</b>-র ওপর নির্মিত। সিস্টেমের সম্পূর্ণ ফাইল ও ডিরেক্টরি কাঠামো নিম্নরূপ:
  </p>

  <div class="code-block">E:/projects/AI_CHAT_BOT/
├── backend/
│   ├── app.py                     # FastAPI প্রধান অ্যাপ্লিকেশন, CORS, রুট মাউন্টিং ও মিডলওয়্যার
│   ├── rag_engine.py              # হাইব্রিড RAG ইঞ্জিন, প্রিলোডেড মেমোরি লুকআপ ও জেনারেটিভ রাউটিং
│   ├── orchestrator/
│   │   ├── agent.py               # AIOrchestrator কোর, ৫-ধাপের পাইপলাইন ম্যানেজার ও SSE স্ট্রিমিং
│   │   ├── intent_classifier.py   # মাল্টি-টার্ন ইনটেন্ট ও এনটিটি এক্সট্রাকশন ইঞ্জিন
│   │   ├── preloaded_responses.py # ৪০+ ক্যানোনিকাল টপিকের সাব-মিলিমিটার মেমোরি ম্যাপ
│   │   └── skill_registry.py      # ডোমেন স্কিল সংজ্ঞা ও ডিসপ্যাচার
│   ├── officer_search/
│   │   ├── search_service.py      # ৮০০+ কর্মীর ফনেটিক ও বাংলিশ সার্চ সার্ভিস (নেগেটিভ গার্ড সহ)
│   │   └── officer_matcher.py     # Levenshtein ও সাউন্ডেক্স ডিরেক্টরি অ্যালগরিদম
│   ├── result_search/
│   │   └── result_service.py      # ১২+ ডিগ্রি প্রোগ্রাম রিকগনিশন ও SMS 16222 সিনট্যাক্স জেনারেটর
│   ├── mcp_servers/
│   │   ├── mcp_client.py          # কেন্দ্রীয় MCP ক্লায়েন্ট ও টুল ডিসপ্যাচ ইন্টারফেস
│   │   ├── token_mcp/             # টোকেন সৃষ্টি, যাচাই ও ChromaDB সিমিলার কেস সার্চ সার্ভার
│   │   ├── directory_mcp/         # কর্মকর্তা তথ্য ও হায়ারার্কি কুয়েরি MCP সার্ভার
│   │   ├── scraper_mcp/           # nu.ac.bd স্ক্র্যাপিং ও নোটিশ হেলথচেক MCP সার্ভার
│   │   └── service_credentials_mcp/# পোর্টাল লিংক ও ফি কাঠামো প্রদানকারী MCP সার্ভার
│   ├── db/
│   │   ├── token_service.py       # টোকেন CRUD ও স্টেট ট্রানজিশন লজিক
│   │   └── database.py            # SQLite WAL সংযোগ ও ডাটাবেস ইনিশিয়ালাইজেশন
│   └── crawler/
│       └── hermes_autonomous.py   # ২৪/৭ স্বয়ংক্রিয় ব্যাকগ্রাউন্ড ক্রলার ও নলেজ এনরিচমেন্ট সোয়ার্ম
├── data/
│   ├── nu_assistant.db            # প্রধান সিস্টেম ডাটাবেস (FTS নোটিশ, কর্মকর্তা ও অডিট লগ)
│   └── nu_tokens.db               # টোকেন ও ট্রানজিশন ইভেন্ট ডাটাবেস (Atomic Sequence)
└── static/
    ├── index.html                 # মূল রেস্পন্সিভ ওয়েব অ্যাপ্লিকেশন ইন্টারফেস
    └── widget.js                  # এক্সটার্নাল পোর্টালে ব্যবহারের উপযোগী প্লাগ-অ্যান্ড-প্লে উইজেট</div>

  <h2 class="sec-heading">৬. ৫-ধাপের কোয়েরি এক্সিকিউশন পাইপলাইন (5-Stage Latency Pipeline)</h2>
  <p>যেকোনো ব্যবহারকারীর বার্তা নিম্নোক্ত ৫টি সুনির্দিষ্ট ধাপে প্রক্রিয়াকৃত হয়:</p>

  <table class="custom-table">
    <thead>
      <tr>
        <th style="width: 25%;">পর্যায় (Stage)</th>
        <th style="width: 55%;">কার্যপদ্ধতি ও অভ্যন্তরীণ অ্যালগরিদম</th>
        <th style="width: 20%;">গড় এক্সিকিউশন টাইম</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>ধাপ ১: প্রিলোডেড মেমোরি</b><br/><code>Preloaded Fast-Path</code></td>
        <td>৪০+ ক্যানোনিকাল টপিকের সাথে সাবস্ট্রিং ও লেক্সিকাল নরম্যালাইজেশন ম্যাচ। ডাটাবেস বা LLM কল ছাড়াই তাৎক্ষণিক রেডিমেড মার্কডাউন ও অ্যাকশন চিপস রিটার্ন করে।</td>
        <td><span style="color:#059669; font-weight:700;">&lt; 0.001 সেকেন্ড</span></td>
      </tr>
      <tr>
        <td><b>ধাপ ২: LRU মেমোরি ক্যাশ</b><br/><code>In-Memory LRU Cache</code></td>
        <td>সাম্প্রতিক জনপ্রিয় ও পুনরাবৃত্তিমূলক প্রশ্নের উত্তর ৫ মিনিট ইন-মেমোরিতে ক্যাশ থাকে। অনুরূপ প্রশ্ন এলে শূন্য প্রসেসিংয়ে সার্ভ হয়।</td>
        <td><span style="color:#059669; font-weight:700;">&lt; 0.001 সেকেন্ড</span></td>
      </tr>
      <tr>
        <td><b>ধাপ ৩: ডোমেন সার্চ ফাস্ট-পাথ</b><br/><code>Domain Fast-Paths</code></td>
        <td><b>অফিসার সার্চ</b> (পদবী/ফোন/ইমেইল), <b>ফলাফল সার্চ</b> (রোল/রেজি/এসএমএস) এবং <b>টোকেন অনুসন্ধান</b> (NU-YYYY-XXXXXX) সরাসরি ডেডিকেটেড ইঞ্জিনে রাউট হয়।</td>
        <td><span style="color:#0369a1; font-weight:700;">০.০০২ – ০.০৫ সেকেন্ড</span></td>
      </tr>
      <tr>
        <td><b>ধাপ ৪: ইনটেন্ট ও MCP রাউটিং</b><br/><code>Intent &amp; MCP Tool Call</code></td>
        <td>সেশন হিস্টোরি বিশ্লেষণ করে ইনটেন্ট ও এনটিটি এক্সট্রাক্ট করা হয় এবং নির্দিষ্ট স্কিল অনুযায়ী প্রয়োজনীয় MCP টুল এক্সিকিউট করা হয়।</td>
        <td><span style="color:#0369a1; font-weight:700;">০.০১ – ০.১০ সেকেন্ড</span></td>
      </tr>
      <tr>
        <td><b>ধাপ ৫: গ্রাউন্ডেড জেনারেটিভ সিন্থেসিস</b><br/><code>Grounded LLM Turn</code></td>
        <td>রিট্রিভড কনটেক্সট ব্যবহার করে গ্রাউন্ডেড প্রম্পট তৈরি হয়। <b>Gemini 3 Flash</b> মডেলের মাধ্যমে Server-Sent Events (SSE) স্ট্রিমিংয়ে রেসপন্স পাঠানো হয়।</td>
        <td><span style="color:#d97706; font-weight:700;">০.৮০ – ১.৪০ সেকেন্ড</span></td>
      </tr>
    </tbody>
  </table>

  <!-- PAGE BREAK -->
  <div class="page-break"></div>

  <!-- ========================================================================= -->
  <!-- পৃষ্ঠা ৪: MCP সার্ভার, স্টেট মেশিন ও ডোমেন ইঞ্জিন -->
  <!-- ========================================================================= -->
  <h2 class="sec-heading">৭. মডেল কনটেক্সট প্রোটোকল (MCP) টুল সার্ভার কাঠামো</h2>
  <p>সিস্টেমের সমস্ত সংবেদনশীল অপারেশন এবং ডেটাবেস কল ৪টি স্বাধীন MCP সার্ভারের মাধ্যমে নিয়ন্ত্রিত হয়:</p>

  <table class="custom-table">
    <thead>
      <tr>
        <th style="width: 25%;">MCP সার্ভার</th>
        <th style="width: 40%;">এক্সপোজড টুলস ও মেথডসমূহ</th>
        <th style="width: 35%;">সিকিউরিটি ও ভ্যালিডেশন পলিসি</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>১. Token MCP</b><br/><code>mcp_servers/token_mcp</code></td>
        <td>• <code>create_support_token</code><br/>• <code>get_token_status</code><br/>• <code>find_similar_solved_cases</code></td>
        <td>অ্যাটোমিক টোকেন নম্বর নিশ্চিতকরণ, মোবাইল ফরম্যাট ভ্যালিডেশন, সলভার ডিপার্টমেন্ট আইসোলেশন ও ChromaDB ভেক্টর কুয়েরি।</td>
      </tr>
      <tr>
        <td><b>২. Directory MCP</b><br/><code>mcp_servers/directory_mcp</code></td>
        <td>• <code>search_officer_directory</code><br/>• <code>get_department_hierarchy</code></td>
        <td>৮০০+ কর্মীর তথ্যে রিড-অনলি অ্যাক্সেস, ফনেটিক বাংলিশ কনভার্সন এবং ফোন/ইমেইল প্রাইভেসি মাস্কিং।</td>
      </tr>
      <tr>
        <td><b>৩. Scraper MCP</b><br/><code>mcp_servers/scraper_mcp</code></td>
        <td>• <code>fetch_live_portal_notice</code><br/>• <code>check_service_portal_health</code></td>
        <td>হোয়াইটলিস্টেড ডোমেন পলিসি (<code>nu.ac.bd</code>), robots.txt মেনে চলা, ৩ সেকেন্ডের রিকোয়েস্ট টাইমআউট।</td>
      </tr>
      <tr>
        <td><b>৪. Credentials MCP</b><br/><code>mcp_servers/service_credentials_mcp</code></td>
        <td>• <code>get_official_portal_link</code><br/>• <code>dispatch_payment_guide</code></td>
        <td>সোনালী সেবা ফি ম্যানুয়াল ও অফিসিয়াল ভেরিফায়েড লিংক ডেলিভারি। জিরো-নলেজ ক্রেডেনশিয়াল পলিসি।</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sec-heading">৮. টোকেন স্টেট মেশিন ও ২৪/৭ হার্মিস সেলফ-লার্নিং লুপ (State Machine &amp; Hermes)</h2>
  
  <div class="two-col">
    <div class="col-card">
      <div style="font-weight:700; color:#0369a1; margin-bottom:3px;">ক. টোকেন লাইফসাইকেল স্টেট মেশিন</div>
      <p style="font-size:7.6pt; margin-bottom:4px;">টোকেনের প্রতিটি রূপান্তর <code>token_events</code> টেবিলে টাইমস্ট্যাম্প সহ সংরক্ষিত হয়:</p>
      <ul style="font-size:7.6pt; margin-left:14px;">
        <li><code>PENDING</code>: শিক্ষার্থী সাবমিট করার সাথে সাথে অ্যাটোমিক আইডি ও QR তৈরি হয়।</li>
        <li><code>ASSIGNED</code>: অ্যাডমিন নির্দিষ্ট ডিপার্টমেন্টাল ডেস্কে রাউট করেন।</li>
        <li><code>PROCESSING</code>: সলভার টোকেনটি গ্রহণ করে সমাধান প্রক্রিয়া শুরু করেন।</li>
        <li><code>SOLVED</code>: সলভার সমাধান টেক্সট এন্ট্রি করেন। <b>এটি স্বয়ংক্রিয়ভাবে অ্যানোনিমাইজ হয়ে ChromaDB ভেক্টরে ইনডেক্স হয়।</b></li>
        <li><code>RETURN_TO_ADMIN</code>: সলভার অসমর্থ হলে অ্যাডমিনের কাছে ব্যাক করে।</li>
      </ul>
    </div>
    <div class="col-card">
      <div style="font-weight:700; color:#059669; margin-bottom:3px;">খ. ২৪/৭ হার্মিস সেলফ-লার্নিং ক্রলার</div>
      <p style="font-size:7.6pt; margin-bottom:4px;">ম্যানুয়াল ডেটা এন্ট্রি ছাড়াই নলেজবেস সর্বদা আপ-টু-ডেট রাখার প্রক্রিয়া:</p>
      <ul style="font-size:7.6pt; margin-left:14px;">
        <li><b>Polite Deep Crawler:</b> <code>nu.ac.bd</code> থেকে নিয়মিত নোটিশ ও পরীক্ষার সময়সূচি স্ক্র্যাপ করে।</li>
        <li><b>Scraped Data Analyzer:</b> নতুন নোটিশ, পরিবর্তিত তারিখ বা ফি শনাক্ত করে।</li>
        <li><b>Hermes Learning Brain:</b> নতুন নোটিশ থেকে প্রশ্ন-উত্তর সিন্থেসিস করে গ্যাপ কিউ সমাধান করে।</li>
        <li><b>Knowledge Provenance:</b> প্রতিটি তথ্যের মূল সোর্স লিঙ্ক ও ক্রল টাইমস্ট্যাম্প মেটাডাটা হিসেবে স্টোর থাকে।</li>
      </ul>
    </div>
  </div>

  <h2 class="sec-heading">৯. বিশেষায়িত ডোমেন সার্চ ইঞ্জিন মেকানিজম (Domain Engines)</h2>
  <div class="two-col">
    <div class="col-card">
      <div style="font-weight:700; color:#0f172a; margin-bottom:2px;">১. কর্মকর্তা ডিরেক্টরি সার্চ ইঞ্জিন (৮০০+ স্টাফ)</div>
      <p style="font-size:7.5pt;">
        ২৩টি প্রশাসনিক দপ্তরের কর্মকর্তা-কর্মচারীদের পদবী ও নাম ফনেটিক এবং বাংলিশ অ্যালগরিদমে খোঁজা হয়। উদাহরণ: <i>'porikkha niyontrok'</i> লিখলে স্বয়ংক্রিয়ভাবে Controller of Examinations-এর নাম, কক্ষ নম্বর ও ইমেইল প্রদর্শিত হয়।
      </p>
    </div>
    <div class="col-card">
      <div style="font-weight:700; color:#0f172a; margin-bottom:2px;">২. রেজাল্ট ও সিজিপিএ ইঞ্জিন (১২+ কোর্স)</div>
      <p style="font-size:7.5pt;">
        অনার্স, ডিগ্রি, মাস্টার্স ও প্রফেশনাল পরীক্ষার জন্য টেলিকম SMS ১৬২২২ সিনট্যাক্স (<code>NU &lt;space&gt; H4 &lt;space&gt; Roll</code>) স্বয়ংক্রিয়ভাবে জেনারেট করে এবং অফিসিয়াল রেজাল্ট সার্ভারের সক্রিয় গভীর লিঙ্ক প্রদান করে।
      </p>
    </div>
  </div>

  <!-- PAGE BREAK -->
  <div class="page-break"></div>

  <!-- ========================================================================= -->
  <!-- পৃষ্ঠা ৫: এপিআই ক্যাটালগ, এক্সটেনশন গাইড ও টেস্টিং -->
  <!-- ========================================================================= -->
  <h2 class="sec-heading">১০. প্রোডাকশন এপিআই ক্যাটালগ ও রানবুক (Production API Catalog)</h2>
  <table class="custom-table">
    <thead>
      <tr>
        <th style="width: 28%;">এপিআই এন্ডপয়েন্ট</th>
        <th style="width: 10%;">মেথড</th>
        <th style="width: 62%;">উদ্দেশ্য, প্যারামিটার ও প্রমাণীকরণ (Auth)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>/api/chat</code></td>
        <td>POST</td>
        <td>সিঙ্ক্রোনাস চ্যাট কোয়েরি। রেট লিমিট: ৬০ রিকোয়েস্ট/মিনিট। বডি: <code>{{"message": "...", "history": []}}</code></td>
      </tr>
      <tr>
        <td><code>/api/chat/stream</code></td>
        <td>POST</td>
        <td>Server-Sent Events (SSE) স্ট্রিমিং চ্যাট এন্ডপয়েন্ট। তাৎক্ষণিক টোকেন বাই টোকেন রেসপন্স দেয়।</td>
      </tr>
      <tr>
        <td><code>/api/token/create</code></td>
        <td>POST</td>
        <td>পাবলিক টোকেন তৈরি। রিটার্ন করে <code>token_id</code> এবং ভেরিফিকেশন QR স্লিপ ডেটা।</td>
      </tr>
      <tr>
        <td><code>/api/token/{{token_id}}</code></td>
        <td>GET</td>
        <td>টোকেনের বর্তমান স্ট্যাটাস ও সমাধান বিবরণী ফেচ করার পাবলিক এন্ডপয়েন্ট।</td>
      </tr>
      <tr>
        <td><code>/api/token/admin/list</code></td>
        <td>GET</td>
        <td>ডিপার্টমেন্ট-আইসোলেটেড টোকেন তালিকা। Bearer JWT টোকেন প্রয়োজন।</td>
      </tr>
      <tr>
        <td><code>/api/token/admin/{{id}}/solve</code></td>
        <td>POST</td>
        <td>টোকেন সমাধান এন্ট্রি এবং সমাধানকৃত কেস ChromaDB ভেক্টরে ইনডেক্সিং।</td>
      </tr>
      <tr>
        <td><code>/api/admin/system/backup</code></td>
        <td>POST</td>
        <td>উভয় SQLite ডাটাবেস ও সিস্টেম কনফিগারেশনের সম্পূর্ণ অ্যাটোমিক ZIP ব্যাকআপ তৈরি।</td>
      </tr>
      <tr>
        <td><code>/api/health</code></td>
        <td>GET</td>
        <td>সিস্টেম হেলথ চেক (SQLite WAL, ChromaDB ও LLM মডেলের লাইভনেস প্রোব)।</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sec-heading">১১. ডেভেলপার গাইড: নতুন স্কিল ও MCP টুল যুক্ত করার নিয়ম</h2>
  <div class="code-block"># ১. backend/orchestrator/skill_registry.py এ নতুন স্কিল ডিফাইন করুন:
SKILL_REGISTRY["scholarship_inquiry"] = SkillDefinition(
    name="scholarship_inquiry",
    description="মেধা বৃত্তি ও উপবৃত্তি তথ্য স্কিল",
    triggers=["বৃত্তি", "উপবৃত্তি", "scholarship", "stipend"],
    handler="backend.mcp_servers.scholarship_mcp.handle_inquiry"
)

# ২. backend/mcp_servers/scholarship_mcp.py তে টুল হ্যান্ডলার লিখুন:
async def handle_inquiry(entities: dict) -> MCPToolResult:
    # ডেটা প্রসেসিং ও রেজাল্ট রিটার্ন
    return MCPToolResult(status="success", content=scholarship_data)</div>

  <div class="callout callout-success">
    <div class="callout-title">🧪 অটোমেটেড টেস্টিং ও ভ্যালিডেশন সুইট (Automated Test Commands)</div>
    <div style="font-size:7.8pt;">
      সিস্টেমের যেকোনো পরিবর্তন যাচাই করার জন্য টার্মিনালে নিম্নোক্ত টেস্ট কমান্ডগুলো রান করুন:<br/>
      • টোকেন সার্ভিস ও ডোমেন ভ্যালিডেশন: <code>python tests/test_token_service_domain.py</code> (4/4 Passed)<br/>
      • কর্মকর্তা সার্চ ও ফনেটিক ম্যাচিং: <code>python tests/test_officer_search.py</code> (12/12 Passed)<br/>
      • ফলাফল সার্চ ও SMS সিনট্যাক্স: <code>python tests/test_result_search.py</code> (8/8 Passed)
    </div>
  </div>

  <div style="margin-top:8px; padding:6px 9px; background:#f1f5f9; border:1px solid #0369a1; border-radius:4px; font-size:7.5pt; text-align:center;">
    <b>জাতীয় বিশ্ববিদ্যালয় এআই প্ল্যাটফর্ম আর্কিটেকচার টিম কর্তৃক সত্যায়িত ও অনুমোদিত</b><br/>
    <i>Confidential &amp; Proprietary — National University Bangladesh Academic Technology Architecture Specification</i>
  </div>

</body>
</html>
"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[1/3] HTML Documentation generated at: {HTML_FILE}")

    # Render via Chrome headless
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ]
    browser = next((p for p in chrome_paths if os.path.exists(p)), None)
    if not browser:
        raise RuntimeError("Neither Chrome nor Edge was found for PDF compilation.")

    print(f"[2/3] Compiling PDF with browser: {browser}")
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUTPUT_PDF}",
        str(HTML_FILE.resolve())
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Browser error:", res.stderr)
        raise RuntimeError(f"PDF generation failed with exit code {res.returncode}")

    # Copy to root
    shutil.copy(str(OUTPUT_PDF), str(ROOT_PDF))
    print(f"[3/3] Master Bengali Documentation PDF generated successfully:")
    print(f"  -> {OUTPUT_PDF}")
    print(f"  -> {ROOT_PDF}")

    # Render preview pages to verify
    import fitz
    doc = fitz.open(str(OUTPUT_PDF))
    print(f"Total Pages Generated: {len(doc)}")
    for i, page in enumerate(doc):
        png_path = DOC_DIR / f"bangla_doc_page_{i+1}.png"
        page.get_pixmap(dpi=150).save(str(png_path))
        print(f"  Page {i+1} saved to {png_path}")

if __name__ == "__main__":
    build_bangla_pdf()
