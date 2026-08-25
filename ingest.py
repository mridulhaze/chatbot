import os
import io
import time
import shutil
import urllib3
import requests
from bs4 import BeautifulSoup
import pdfplumber
from pathlib import Path
from dotenv import load_dotenv

# Suppress InsecureRequestWarning for unverified SSL chains
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Modern LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 1. Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(f"Missing GEMINI_API_KEY in {env_path}")

DB_DIR = "./nu_vector_db"

def scrape_nu_notices(url: str, category_name: str) -> list[dict]:
    """Extract structured notice rows from NU notice pages."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    notices = []
    try:
        response = requests.get(url, headers=headers, timeout=20, verify=False)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for table rows containing notices
        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                row_text = " | ".join([c.get_text(strip=True) for c in cols if c.get_text(strip=True)])
                link = row.find("a")
                href = link.get("href") if link else None
                if href and not href.startswith("http"):
                    href = f"https://www.nu.ac.bd/{href.lstrip('/')}"
                if row_text:
                    notices.append({
                        "category": category_name,
                        "text": row_text,
                        "url": href or url
                    })
    except Exception as e:
        print(f"Skipping notice page {url} (Error: {e})", flush=True)
    return notices

def scrape_nu_webpage_clean(url: str) -> str:
    """Extract concise, clean text from an NU HTML page."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=20, verify=False)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove junk tags
        for tag in soup(["script", "style", "select", "option", "nav", "footer", "header", "noscript", "svg", "iframe"]):
            tag.decompose()
            
        lines = []
        for elem in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "span"]):
            text = elem.get_text(strip=True)
            if len(text) > 10 and text not in lines:
                lines.append(text)
                
        return "\n".join(lines[:100]) # Cap to most relevant content
    except Exception as e:
        print(f"Skipping {url} (Error: {e})", flush=True)
        return ""

def extract_pdf_text_from_url(pdf_url: str) -> str:
    """Download and extract raw text from online PDF notices."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(pdf_url, headers=headers, timeout=25, verify=False)
        response.raise_for_status()
        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages[:3]] # Read first 3 pages
            text = "\n".join(pages_text)
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {pdf_url}: {e}", flush=True)
        return ""

def build_knowledge_base():
    documents = []

    print("1. Scraping National University notice portals...", flush=True)
    target_notice_pages = [
        ("https://www.nu.ac.bd/recent-news-notice.php", "General & Recent Notices"),
        ("https://www.nu.ac.bd/examination-notice.php", "Examination & Routine Notices"),
        ("https://www.nu.ac.bd/admission-notice.php", "Admission Notices")
    ]

    all_pdf_links = []
    for page_url, category in target_notice_pages:
        notices = scrape_nu_notices(page_url, category)
        print(f"  - Scraped {len(notices)} notices from {category}", flush=True)
        
        # Take the top 20 latest notices from each category
        top_notices = notices[:20]
        if top_notices:
            notice_summary = f"# National University Notices - {category}\n"
            for n in top_notices:
                notice_summary += f"- {n['text']} (Link: {n['url']})\n"
                if n["url"].endswith(".pdf") and len(all_pdf_links) < 3:
                    all_pdf_links.append(n["url"])
            documents.append(Document(page_content=notice_summary, metadata={"source": page_url, "category": category}))

    # 2. Extract content from top PDF notices if available
    print("2. Extracting sample PDF notice texts...", flush=True)
    for pdf_url in all_pdf_links:
        pdf_text = extract_pdf_text_from_url(pdf_url)
        if pdf_text and len(pdf_text) > 30:
            print(f"  - Extracted {len(pdf_text)} chars from {pdf_url}", flush=True)
            documents.append(Document(page_content=pdf_text, metadata={"source": pdf_url, "type": "pdf_notice"}))

    # 3. Comprehensive National University Knowledge Seed
    print("3. Adding curated National University baseline knowledge...", flush=True)
    seed_nu_info = """
# National University of Bangladesh (জাতীয় বিশ্ববিদ্যালয়) - Official Master Guide

## Overview & Official Portals
- Established: 1992 by an Act of Parliament of Bangladesh.
- Type: Affiliating apex university for tertiary education across all 64 districts in Bangladesh.
- Main Campus: Board Bazar, Gazipur-1704, Dhaka Division, Bangladesh.
- Official Website: https://www.nu.ac.bd
- Admissions Portal: http://app1.nu.edu.bd
- Results & Result Archive Portals:
  * http://results.nu.ac.bd/ (Primary Result Archive for Honours, Degree, Masters, Professional)
  * http://www.nu.ac.bd/results/ (Alternative Result Server)
  * http://103.113.200.7/ (Dedicated Archive Server)
- Form Fill-up & EMS Portal: http://ems.nu.ac.bd/
- Student Service Portal: https://nu.edu.bd/

## Results Archive & Result Checking Methods

### 1. Online Result Checking:
- Visit http://results.nu.ac.bd/ or http://www.nu.ac.bd/results/
- Select Course (Honours, Degree, Masters, Professional) and Year.
- Select Individual Result or College-wise Result.
- Enter Roll Number, Registration Number, and Passing / Examination Year.
- Complete security captcha code and click "Search Result" to view detailed marksheet and GPA/CGPA.

### 2. SMS Result Format (Send to 16222 from any Teletalk, Grameenphone, Banglalink, Robi, Airtel SIM):
- **Honours 1st Year**: `NU <space> H1 <space> Roll_Number` -> send to `16222`
- **Honours 2nd Year**: `NU <space> H2 <space> Roll_Number` -> send to `16222`
- **Honours 3rd Year**: `NU <space> H3 <space> Roll_Number` -> send to `16222`
- **Honours 4th Year**: `NU <space> H4 <space> Roll_Number` -> send to `16222`
- **Degree Pass (1st, 2nd, 3rd Year)**: `NU <space> DEG <space> Roll_Number` -> send to `16222`
- **Masters Final Part**: `NU <space> MF <space> Roll_Number` -> send to `16222`
- **Masters Preliminary**: `NU <space> MP <space> Roll_Number` -> send to `16222`
- **Professional Courses (BBA/CSE/ECE)**: `NU <space> HP <space> Roll_Number` -> send to `16222`

### 3. Answer Script Re-scrutiny (খাতা পুনর্নিরীক্ষণ / Challenge):
- Application opens online on http://www.nu.ac.bd/ within 30 days after result publication.
- Pay the specified re-scrutiny fee via Sonali Bank Sonali Seba slip/online gateway.
- Result of re-scrutiny is published on the official notice board within 30-45 days.

## Academic Programs & Degree Structure
1. **Honours (4-Year Integrated Bachelor Degree)**:
   - B.A. (Honours), B.S.S. (Honours), B.B.A. (Honours), B.Sc. (Honours)
2. **Degree Pass Course (3 Years)**:
   - B.A. (Pass), B.S.S. (Pass), B.Sc. (Pass), B.B.S. (Pass)
3. **Masters Degree Programs**:
   - Masters (Regular) - 1 Year duration (for 4-year Honours graduates)
   - Masters (Preliminary & Final) - 2 Years duration (for 3-year Degree Pass graduates)
4. **Professional & Special Programs**:
   - BBA (Professional), CSE, ECE, AMT, FDT, MBA, LL.B, B.Ed, M.Ed, etc.

## Grading System & CGPA Calculation Formula
- 80% to 100%: A+ (Grade Point: 4.00) - Outstanding
- 75% to <80%: A (Grade Point: 3.75) - Excellent
- 70% to <75%: A- (Grade Point: 3.50) - Very Good
- 65% to <70%: B+ (Grade Point: 3.25) - Good
- 60% to <65%: B (Grade Point: 3.00) - Satisfactory
- 55% to <60%: B- (Grade Point: 2.75) - Above Average
- 50% to <55%: C+ (Grade Point: 2.50) - Average
- 45% to <50%: C (Grade Point: 2.25) - Below Average
- 40% to <45%: D (Grade Point: 2.00) - Pass
- Below 40%: F (Grade Point: 0.00) - Fail
- Minimum Passing CGPA for Graduation: 2.00

## Examination, Form Fill-Up & Promotion Regulations
- **Form Fill-Up**: Conducted online via http://ems.nu.ac.bd. Students fill out the form online, submit the printed copy to their college, and pay the board and college fees.
- **Year Promotion Criteria**:
  * Honours 1st to 2nd year: Must pass in at least 3 theoretical courses and achieve minimum GPA of 2.00.
  * Honours 2nd to 3rd year: Must pass in at least 3 theoretical courses and achieve minimum GPA of 2.00.
  * Honours 3rd to 4th year: Must pass in at least 4 theoretical courses and achieve minimum GPA of 2.00.
- **Improvement Exam Policy**:
  * Allowed for grades 'C', 'D', or 'F'.
  * Can be taken only in the immediate subsequent year during the regular exam of that syllabus.
  * Highest improved grade is capped at 'B+' for C and D grades in improvement.

## Admission Process & Release Slips
- **Undergraduate (Honours / Degree) Admission**:
  * Portal: http://app1.nu.edu.bd
  * Selection is 100% GPA-based (SSC GPA 40% + HSC GPA 60%). No separate written test for general courses.
  * Stages: 1st Merit List -> 2nd Merit List & Subject Migration -> 1st Release Slip -> 2nd Release Slip.
  * Release Slip: Eligible candidates who are not selected or canceled admission can apply to 3 to 5 colleges with preferred subjects on the admission portal.

## Certificates, Transcripts & Academic Services
- **Provisional Certificate / Original Certificate / Marksheet Verification**:
  * Applied online through the National University Student Service Portal (http://service.nu.edu.bd/ or https://www.nu.ac.bd).
  * Fees paid via Sonali Seba. Delivery via postal mail or collection at Gazipur main campus.
"""
    documents.append(Document(page_content=seed_nu_info, metadata={"source": "nu_master_knowledge_base", "type": "seed_data"}))

    # 4. Text Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"\nTotal curated chunks created: {len(chunks)}", flush=True)

    # Clean old vector DB directory if needed
    if os.path.exists(DB_DIR):
        print(f"Cleaning previous DB directory '{DB_DIR}'...", flush=True)
        try:
            shutil.rmtree(DB_DIR)
        except Exception as e:
            print(f"Note: Could not completely delete {DB_DIR}: {e}", flush=True)

    # Initialize Embeddings with active Gemini embedding model
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key.strip()
    )

    print("\nBuilding Chroma vector store...", flush=True)
    batch_size = 10
    vector_store = None

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        print(f"  Embedding batch {batch_num}/{total_batches} ({len(batch)} chunks)...", flush=True)
        
        # Retry logic for quota/rate limits
        for attempt in range(5):
            try:
                if vector_store is None:
                    vector_store = Chroma.from_documents(
                        documents=batch,
                        embedding=embeddings,
                        persist_directory=DB_DIR
                    )
                else:
                    vector_store.add_documents(documents=batch)
                break
            except Exception as err:
                print(f"    Attempt {attempt + 1} failed: {err}", flush=True)
                if attempt < 4:
                    wait_time = (attempt + 1) * 6
                    print(f"    Waiting {wait_time}s before retrying...", flush=True)
                    time.sleep(wait_time)
                else:
                    raise err
        
        time.sleep(1.0)

    print(f"\nSUCCESS: Knowledge base successfully created and saved to '{DB_DIR}'.", flush=True)

if __name__ == "__main__":
    build_knowledge_base()