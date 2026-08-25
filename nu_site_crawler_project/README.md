# National University Bangladesh Website Knowledge Crawler

A respectful Python crawler for building an AI/RAG-ready knowledge map of `nu.ac.bd` and allowed NU subdomains.

## Features

- Crawls internal pages and sub-pages.
- Optionally follows `*.nu.ac.bd`.
- Respects `robots.txt` by default.
- Normalizes URLs and removes fragments.
- Avoids duplicate URLs.
- Records parent/child relationships.
- Extracts titles, headings, metadata, visible text and links.
- Classifies pages: notice, examination, admission, office order, press release, form/instruction, regional centre, service, etc.
- Finds and downloads PDF/DOCX/XLSX/CSV/TXT documents.
- Extracts text from supported documents.
- Saves crawl state in SQLite so the crawl can resume.
- Generates JSONL files for RAG/vector databases.
- Generates a hierarchical `nu_site_map.json`.
- Logs failed URLs.

## Install

Python 3.10+ is recommended.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Then:

```bash
pip install -r requirements.txt
```

## First test crawl

Edit `config.yaml`:

```yaml
crawl:
  max_pages: 1000
  delay_seconds: 1.0
```

Then:

```bash
python run_crawler.py
```

## Full crawl

After checking the first run, increase:

```yaml
crawl:
  max_pages: 100000
  max_depth: 50
  delay_seconds: 0.7
```

Run again:

```bash
python crawler.py
```

The SQLite database allows the crawler to resume.

## Output

```text
data/
  nu_pages.jsonl
  nu_documents.jsonl
  nu_links.jsonl
  nu_errors.jsonl
  nu_site_map.json
  nu_crawler.sqlite3
  documents/
```

## RAG

Use `nu_pages.jsonl` and `nu_documents.jsonl` as source data for your embedding/vector database.

Recommended metadata:

- source URL
- parent URL
- title
- page type
- language
- published date
- academic year/session
- document ID
- content hash

## Important

This crawler does not bypass authentication, CAPTCHA, access controls, or robots rules, and it does not submit forms. Use a reasonable delay and obtain institutional authorization if you plan to run it as a production crawler.
