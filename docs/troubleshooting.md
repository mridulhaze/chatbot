# Troubleshooting Guide

## 1. Missing Module or Package Errors
Ensure your virtual environment is active and run:
```bash
pip install -r requirements.txt
```

## 2. Token ID Generation Duplicate Protection
Token IDs rely on the `token_sequences` table. If the database file is reset or moved, `init_token_database()` automatically checks and recreates the sequence table.

## 3. Vector Database Loading
Chroma DB is persisted in `nu_vector_db/`. If embeddings need rebuilding, run `python ingest.py`.
