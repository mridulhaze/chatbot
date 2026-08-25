import json
import logging
import mimetypes
import time
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .classifier import classify, extract_academic_metadata
from .db import CrawlDB
from .extractors import extract_html, extract_document
from .utils import clean_text, domain_matches, extension, normalize_url, sha256_bytes, utc_now

class NUCrawler:
    def __init__(self, config):
        self.config = config
        self.site = config["site"]
        self.crawl = config["crawl"]
        self.filters = config["filters"]
        self.output = config["output"]

        self.out_dir = Path(self.output["directory"])
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir = self.out_dir / self.output["downloaded_documents"]
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        self.db = CrawlDB(str(self.out_dir / self.output["sqlite_db"]))
        self.pages_fp = open(self.out_dir / self.output["pages_jsonl"], "a", encoding="utf-8")
        self.docs_fp = open(self.out_dir / self.output["documents_jsonl"], "a", encoding="utf-8")
        self.links_fp = open(self.out_dir / self.output["links_jsonl"], "a", encoding="utf-8")
        self.errors_fp = open(self.out_dir / self.output["errors_jsonl"], "a", encoding="utf-8")

        retry = Retry(
            total=self.crawl.get("retries",3),
            connect=self.crawl.get("retries",3),
            read=self.crawl.get("retries",3),
            backoff_factor=1,
            status_forcelist=[429,500,502,503,504],
            allowed_methods=frozenset(["GET","HEAD"]),
            respect_retry_after_header=True
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({
            "User-Agent": self.crawl.get("user_agent","NU-Knowledge-Crawler/1.0"),
            "Accept-Language": "bn,en;q=0.8"
        })

        self.robot_cache = {}
        self.last_request = 0.0
        self.logger = logging.getLogger("nu_crawler")
        logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    def throttle(self):
        delay = float(self.crawl.get("delay_seconds",0.7))
        elapsed = time.monotonic() - self.last_request
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self.last_request = time.monotonic()

    def allowed_url(self, url):
        if not url:
            return False
        p = urlsplit(url)
        if p.scheme not in ("http","https"):
            return False
        if not domain_matches(p.hostname or "", self.site.get("allowed_domains",[])):
            return False
        if extension(url) in set(self.filters.get("skip_extensions",[])):
            return False
        low = url.lower()
        return not any(x.lower() in low for x in self.filters.get("skip_url_patterns",[]))

    def can_fetch(self, url):
        if not self.crawl.get("respect_robots", True):
            return True
        p = urlsplit(url)
        origin = f"{p.scheme}://{p.netloc}"
        if origin not in self.robot_cache:
            rp = RobotFileParser()
            try:
                self.throttle()
                res = self.session.get(origin + "/robots.txt", timeout=10, verify=False)
                if res.status_code == 200:
                    rp.parse(res.text.splitlines())
                else:
                    self.robot_cache[origin] = None
                    return True
            except Exception:
                self.logger.warning("robots.txt unavailable or ignored for: %s", origin)
                self.robot_cache[origin] = None
                return True
            self.robot_cache[origin] = rp
        if self.robot_cache[origin] is None:
            return True
        return self.robot_cache[origin].can_fetch(self.crawl.get("user_agent", "NU-Knowledge-Crawler/1.0"), url)

    def fetch(self, url):
        if not self.can_fetch(url):
            raise RuntimeError("Blocked by robots.txt")
        self.throttle()
        r = self.session.get(url, timeout=self.crawl.get("timeout_seconds", 30), allow_redirects=True, verify=False)
        r.raise_for_status()
        final = normalize_url(r.url, keep_query=self.crawl.get("include_query_strings", False))
        ct = (r.headers.get("Content-Type") or "").split(";")[0].lower()
        max_bytes = int(float(self.crawl.get("max_document_mb", 50)) * 1024 * 1024)
        if len(r.content) > max_bytes:
            raise RuntimeError("Response exceeds configured size limit")
        return r, final, ct, r.content

    def is_document(self, url, content_type):
        if extension(url) in set(self.filters.get("document_extensions",[])):
            return True
        return any(x in (content_type or "") for x in [
            "application/pdf","application/msword","wordprocessingml",
            "application/vnd.ms-excel","spreadsheetml","text/csv","text/plain"
        ])

    def save_document(self, url, parent_url, content_type, data, depth):
        ext = extension(url) or mimetypes.guess_extension(content_type or "") or ".bin"
        digest = sha256_bytes(data)
        path = self.docs_dir / f"{digest[:24]}{ext}"
        if not path.exists():
            path.write_bytes(data)

        try:
            extracted = extract_document(data,content_type,ext)
        except Exception as e:
            extracted = {"text":"","language":"unknown","extraction_error":str(e)}

        record = {
            "document_id": f"NU-DOC-{digest[:16]}",
            "url": url,
            "parent_url": parent_url,
            "depth": depth,
            "content_type": content_type,
            "extension": ext,
            "local_path": str(path),
            "sha256": digest,
            "size_bytes": len(data),
            "title": Path(urlsplit(url).path).name,
            "language": extracted.get("language","unknown"),
            "text": clean_text(extracted.get("text","")),
            "extracted": bool(extracted.get("text")),
            "metadata": {k:v for k,v in extracted.items() if k not in ("text","language")},
            "crawled_at": utc_now()
        }
        self.docs_fp.write(json.dumps(record,ensure_ascii=False)+"\n")
        self.docs_fp.flush()
        self.db.add_document(record)

    def discover(self, source_url, html, depth):
        parsed = extract_html(html,source_url)
        discovered = []
        source_host = (urlsplit(source_url).hostname or "").lower()

        for item in parsed["links"]:
            target = normalize_url(item["href"], source_url, self.crawl.get("include_query_strings",False))
            if not target or not self.allowed_url(target):
                continue

            target_host = (urlsplit(target).hostname or "").lower()
            if target_host != source_host:
                relation = "subdomain" if domain_matches(target_host,self.site.get("allowed_domains",[])) else "external"
            else:
                relation = "internal"

            self.db.add_link(source_url,target,item["text"],relation)
            self.links_fp.write(json.dumps({
                "source_url":source_url,"target_url":target,
                "label":item["text"],"relation":relation
            },ensure_ascii=False)+"\n")

            if relation == "external" and not self.crawl.get("crawl_external_links",False):
                continue
            if relation == "subdomain" and not self.site.get("follow_subdomains",True):
                continue
            discovered.append((target,depth+1,source_url,source_url))

        self.links_fp.flush()
        return parsed, discovered

    def crawl_one(self,url,depth,parent_url):
        self.db.mark_started(url)
        try:
            r,final,ct,data = self.fetch(url)

            if self.is_document(final,ct):
                if self.crawl.get("download_documents",True):
                    self.save_document(final,parent_url,ct,data,depth)
                self.db.mark_done(url,r.status_code,ct,Path(urlsplit(final).path).name,utc_now())
                return []

            if "html" not in ct and not ct.startswith("text/"):
                self.db.mark_done(url,r.status_code,ct,"",utc_now())
                return []

            parsed,discovered = self.discover(final,data,depth)
            page_type,keyword = classify(final,parsed["title"],parsed["text"])
            record = {
                "url":final,
                "canonical_url":final,
                "parent_url":parent_url,
                "depth":depth,
                "http_status":r.status_code,
                "content_type":ct,
                "title":parsed["title"],
                "page_type":page_type,
                "classification_keyword":keyword,
                "language":parsed["language"],
                "published_date":parsed["published_date"],
                "academic_metadata":extract_academic_metadata(parsed["text"]),
                "headings":parsed["headings"],
                "meta":parsed["meta"],
                "links":parsed["links"],
                "text":parsed["text"],
                "content_hash":sha256_bytes(data),
                "crawled_at":utc_now()
            }
            self.pages_fp.write(json.dumps(record,ensure_ascii=False)+"\n")
            self.pages_fp.flush()
            self.db.mark_done(url,r.status_code,ct,record["title"],record["crawled_at"])
            return discovered

        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            self.db.mark_error(url,msg,crawled_at=utc_now())
            self.errors_fp.write(json.dumps({
                "url":url,"parent_url":parent_url,"depth":depth,
                "error":msg,"time":utc_now()
            },ensure_ascii=False)+"\n")
            self.errors_fp.flush()
            self.logger.error("%s -> %s",url,msg)
            return []

    def seed(self):
        root = normalize_url(self.site["root_url"],keep_query=self.crawl.get("include_query_strings",False))
        self.db.add_url(root,0,None,None)

    def build_site_map(self):
        path = self.out_dir / self.output["pages_jsonl"]
        records = []
        if path.exists():
            for line in path.read_text(encoding="utf-8",errors="ignore").splitlines():
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

        nodes = {
            p["url"]:{
                "url":p["url"],"title":p.get("title",""),
                "page_type":p.get("page_type","general"),
                "language":p.get("language","unknown"),
                "depth":p.get("depth",0),"children":[]
            } for p in records
        }
        roots = []
        for p in records:
            url = p["url"]
            parent = p.get("parent_url")
            if parent and parent in nodes and parent != url:
                nodes[parent]["children"].append(nodes[url])
            else:
                roots.append(nodes[url])

        def clean(node):
            seen=set()
            unique=[]
            for c in node["children"]:
                if c["url"] not in seen:
                    seen.add(c["url"]); unique.append(c)
            node["children"]=sorted(unique,key=lambda x:x["url"])
            for c in node["children"]:
                clean(c)
            return node

        roots = [clean(x) for x in roots]
        self.out_dir.joinpath(self.output["site_map_json"]).write_text(
            json.dumps({
                "site":self.site,
                "generated_at":utc_now(),
                "page_count":len(nodes),
                "roots":roots
            },ensure_ascii=False,indent=2),encoding="utf-8"
        )

    def run(self):
        self.seed()
        max_pages=int(self.crawl.get("max_pages",100000))
        count=0
        while count < max_pages:
            item=self.db.get_next()
            if not item:
                break
            url,depth,parent=item
            count+=1
            self.logger.info("[%s/%s] depth=%s %s",count,max_pages,depth,url)
            found=self.crawl_one(url,depth,parent)
            valid=[x for x in found if x[1] <= int(self.crawl.get("max_depth",50))]
            self.db.add_urls(valid)
        self.build_site_map()
        self.logger.info("Finished: %s",self.db.stats())

    def close(self):
        for fp in (self.pages_fp,self.docs_fp,self.links_fp,self.errors_fp):
            fp.close()
        self.db.close()
