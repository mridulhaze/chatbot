import os
import io
import time
import json
import argparse
import logging
import urllib3
import requests
from bs4 import BeautifulSoup
import pdfplumber
from pathlib import Path
from dotenv import load_dotenv

# Modern LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NU_UPDATER")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(f"Missing GEMINI_API_KEY in {env_path}")

DB_DIR = "./nu_vector_db"
DATA_DIR = Path(__file__).resolve().parent / "data"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def load_flexible_dataset() -> list[Document]:
    """Load curated knowledge base and quick links from the data directory."""
    documents = []
    
    # 1. Load Master Knowledge Base JSON
    kb_file = DATA_DIR / "nu_knowledge_base.json"
    if kb_file.exists():
        with open(kb_file, "r", encoding="utf-8") as f:
            kb_data = json.load(f)
            
        u_info = kb_data.get("university_info", {})
        summary = f"# {u_info.get('name', 'National University')} ({u_info.get('name_bn', '')})\n"
        summary += f"- Established: {u_info.get('established')}\n"
        summary += f"- Location: {u_info.get('headquarters')}\n"
        summary += f"- Website: {u_info.get('official_website')}\n"
        summary += f"- Overview: {u_info.get('nature')}\n\n"
        
        for m in kb_data.get("modules", []):
            summary += f"## {m.get('topic')} ({m.get('topic_bn', '')})\n"
            summary += f"{m.get('content')}\n\n"
            
        documents.append(Document(page_content=summary, metadata={"source": "nu_knowledge_base_json", "type": "master_dataset"}))
        logger.info(f"Loaded master knowledge base from {kb_file.name}")

    # 2. Load Quick Links Catalog JSON
    links_file = DATA_DIR / "quick_links.json"
    if links_file.exists():
        with open(links_file, "r", encoding="utf-8") as f:
            links_data = json.load(f)
            
        links_summary = "# National University Official Portals & Quick Links Directory\n"
        for cat in links_data:
            links_summary += f"\n### {cat.get('icon', '')} {cat.get('category')} ({cat.get('category_bn', '')})\n"
            for l in cat.get("links", []):
                links_summary += f"- **{l.get('title')} ({l.get('title_bn', '')})**: {l.get('url')} - {l.get('description')}\n"
                
        documents.append(Document(page_content=links_summary, metadata={"source": "quick_links_json", "type": "portal_directory"}))
        logger.info(f"Loaded portals directory from {links_file.name}")
        
    return documents

def scrape_notices_live() -> tuple[list[Document], list[str]]:
    """Scrape live circulars and notice boards from nu.ac.bd."""
    target_pages = [
        ("https://www.nu.ac.bd/recent-news-notice.php", "General & Breaking Notices"),
        ("https://www.nu.ac.bd/examination-notice.php", "Examination & Routine Circulars"),
        ("https://www.nu.ac.bd/admission-notice.php", "Admission Circulars")
    ]
    
    documents = []
    pdf_links = []
    
    for url, category in target_pages:
        try:
            res = requests.get(url, headers=HEADERS, timeout=20, verify=False)
            res.raise_for_status()
            res.encoding = res.apparent_encoding or "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            
            rows = soup.find_all("tr")
            notices = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    row_text = " | ".join([c.get_text(strip=True) for c in cols if c.get_text(strip=True)])
                    a = row.find("a")
                    href = a.get("href") if a else None
                    if href and not href.startswith("http"):
                        href = f"https://www.nu.ac.bd/{href.lstrip('/')}"
                    if row_text:
                        notices.append({"text": row_text, "url": href or url})
                        if href and href.endswith(".pdf") and len(pdf_links) < 4:
                            pdf_links.append(href)
                            
            if notices:
                summary = f"# Live Notices: {category}\n"
                for n in notices[:25]:
                    summary += f"- {n['text']} (Link: {n['url']})\n"
                documents.append(Document(page_content=summary, metadata={"source": url, "category": category}))
                logger.info(f"Scraped {len(notices)} notices from {category}")
        except Exception as e:
            logger.warning(f"Could not scrape {url}: {e}")
            
    # Extract sample PDF text from top notices
    for pdf_url in pdf_links:
        try:
            r = requests.get(pdf_url, headers=HEADERS, timeout=25, verify=False)
            r.raise_for_status()
            with pdfplumber.open(io.BytesIO(r.content)) as pdf:
                pages_text = [page.extract_text() or "" for page in pdf.pages[:2]]
                text = "\n".join(pages_text).strip()
            if text and len(text) > 30:
                documents.append(Document(page_content=text, metadata={"source": pdf_url, "type": "pdf_circular"}))
                logger.info(f"Parsed PDF circular: {pdf_url}")
        except Exception as err:
            logger.debug(f"Skipping PDF {pdf_url}: {err}")
            
    return documents, pdf_links

def update_vector_database() -> int:
    """Run full knowledge extraction, chunking, and Chroma DB update."""
    logger.info("Starting Knowledge Base Update...")
    
    # 1. Gather curated datasets and live scraped notices
    docs = load_flexible_dataset()
    live_docs, _ = scrape_notices_live()
    docs.extend(live_docs)
    
    # 2. Chunk documents
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    logger.info(f"Total structured knowledge chunks created: {len(chunks)}")
    
    # 3. Embedding model
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key.strip()
    )
    
    # 4. Batch Embed into Chroma DB
    batch_size = 10
    vector_store = None
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        logger.info(f"Embedding batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
        
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
            except Exception as e:
                logger.warning(f"Batch {batch_num} attempt {attempt + 1} failed: {e}")
                if attempt < 4:
                    wait_time = (attempt + 1) * 6
                    time.sleep(wait_time)
                else:
                    raise e
        time.sleep(1.0)
        
    logger.info("Knowledge Base successfully updated and saved to Chroma DB.")
    return len(chunks)

def run_daemon(interval_seconds: int = 3600):
    """Periodically update the knowledge base."""
    logger.info(f"Starting Knowledge Base Daemon (Interval: {interval_seconds} seconds)...")
    while True:
        try:
            update_vector_database()
        except Exception as e:
            logger.error(f"Error during scheduled update: {e}")
        logger.info(f"Sleeping for {interval_seconds} seconds until next update...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="National University Knowledge Base Updater")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in the background")
    parser.add_argument("--interval", type=int, default=3600, help="Update interval in seconds (default: 3600 / 1 hr)")
    args = parser.parse_args()
    
    if args.daemon:
        run_daemon(args.interval)
    else:
        update_vector_database()
