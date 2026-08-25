import json
import re
from pathlib import Path

def chunks(text,size=1200,overlap=200):
    text=re.sub(r"\s+"," ",text).strip()
    start=0
    while start < len(text):
        end=min(len(text),start+size)
        yield text[start:end]
        if end==len(text):
            break
        start=max(0,end-overlap)

def export_pages(input_jsonl="data/nu_pages.jsonl",output_jsonl="data/nu_rag_chunks.jsonl",size=1200,overlap=200):
    Path(output_jsonl).parent.mkdir(parents=True,exist_ok=True)
    with open(input_jsonl,encoding="utf-8") as src, open(output_jsonl,"w",encoding="utf-8") as dst:
        for line in src:
            try:
                page=json.loads(line)
            except Exception:
                continue
            for i,chunk in enumerate(chunks(page.get("text",""),size,overlap)):
                dst.write(json.dumps({
                    "id":f'{page.get("content_hash","unknown")}-{i}',
                    "text":chunk,
                    "metadata":{
                        "url":page.get("url"),
                        "title":page.get("title"),
                        "page_type":page.get("page_type"),
                        "language":page.get("language"),
                        "published_date":page.get("published_date")
                    }
                },ensure_ascii=False)+"\n")

if __name__=="__main__":
    export_pages()
