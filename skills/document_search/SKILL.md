---
name: document_search
version: 1.0.0
description: Searches, extracts, and summarizes official National University forms, syllabi, PDF circulars, and DOCX documents.
---

# National University Document Search Skill

## Purpose
Help students, teachers, and administrators discover, read, and summarize official forms, syllabus PDFs, guidelines, and gazettes.

## Trigger Conditions
Activate this skill whenever:
1. User asks for downloadable forms (e.g. "TC Form", "Rescrutiny Form", "Certificate Application Form", "ফরম").
2. User asks for syllabus, curriculum, or regulations document.
3. User specifically asks to search documents or download a PDF.

## Available MCP Tools
- `search_documents`: Locates PDF, DOCX, XLSX, and CSV documents by keyword.
- `get_document_text`: Retrieves extracted text content of a specific document.
- `get_document_metadata`: Provides file size, download link, hash, and published date.

## Conversational Workflow
1. Identify the requested document topic and type (PDF, Form, Syllabus).
2. Execute `search_documents(query=topic)` through Document MCP.
3. If documents found, return clean clickable download links, document titles, and a brief overview.
4. If the user asks for a summary of the document, fetch `get_document_text` and summarize key instructions.
