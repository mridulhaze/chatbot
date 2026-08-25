---
name: scraped_data_analysis
description: Analyzes newly crawled pages, documents, notices, and links from National University Bangladesh, extracting academic entities and synthesizing verified QA pairs.
author: National University AI Team
version: 1.0.0
---

# Scraped Data Analysis Skill

## Purpose
The `scraped_data_analysis` skill processes raw unstructured content harvested by the Deep Crawler and Polite Scraper from `nu.ac.bd` domains. It extracts key academic metadata (dates, deadlines, fees, departments, circular references) and translates raw announcements into structured, queryable knowledge.

## Core Capabilities
1. **Entity Extraction**: Identifies academic faculties, degrees (Honours, Degree Pass, Masters, Professional), session years, application dates, and fee schedules.
2. **Bilingual QA Synthesis**: Formulates natural question-and-answer pairs in both Bengali and English for student search coverage.
3. **Dead Link & Anomaly Detection**: Flags broken circular links or malformed PDF references before ingestion.

## Standard Workflow
1. Fetch un-analyzed records from the SQLite `pages` and `documents` tables.
2. Parse clean text, stripping tracking scripts, navigational boilerplate, and duplicate headers.
3. Pass structured payload to the `ScrapedDataAnalyzerAgent`.
4. Output verified entity dictionaries and QA JSON objects conforming to the National University Knowledge Schema.
