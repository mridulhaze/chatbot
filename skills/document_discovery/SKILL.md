---
name: document_discovery
description: Discovers, downloads, parses, and extracts text and metadata from official NU documents (PDF, DOCX, XLSX).
---

# Document Discovery & Extraction Skill

## Overview
Automates the retrieval and ingestion of official circulars, examination routines, syllabi, admission guidelines, and administrative forms published in binary document formats.

## Supported Document Formats
- **PDF** (`.pdf`, `application/pdf`): Multi-page text extraction with per-page tracking and notice title mapping.
- **DOCX** (`.docx`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`): Paragraph and table extraction.
- **XLSX** (`.xlsx`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`): Multi-sheet tabular parsing.
- **CSV & TXT**: Direct UTF-8 sanitized string extraction.

## Metadata Extraction
- Preserves `source_url`, `file_name`, `page_count`, `file_size`, `published_date`, and `document_type`.
