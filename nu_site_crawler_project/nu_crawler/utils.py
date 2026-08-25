from datetime import datetime, timezone
import hashlib
import re
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()

def normalize_url(url, base_url=None, keep_query=False):
    if base_url:
        url = urljoin(base_url, url)
    url = url.strip()
    p = urlsplit(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        return ""
    host = p.hostname.lower()
    port = p.port
    netloc = host if not port or (p.scheme == "http" and port == 80) or (p.scheme == "https" and port == 443) else f"{host}:{port}"
    path = re.sub(r"/{2,}", "/", p.path or "/")
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    query = p.query if keep_query else ""
    return urlunsplit((p.scheme.lower(), netloc, path, query, ""))

def extension(url):
    path = unquote(urlsplit(url).path).lower()
    m = re.search(r"(\.[a-z0-9]{1,8})$", path)
    return m.group(1) if m else ""

def domain_matches(host, allowed_domains):
    host = host.lower().split(":")[0]
    for d in allowed_domains:
        d = d.lower().strip()
        if d.startswith("*."):
            base = d[2:]
            if host == base or host.endswith("." + base):
                return True
        elif host == d:
            return True
    return False

def language_of(text):
    bangla = len(re.findall(r"[\u0980-\u09FF]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if bangla and latin:
        return "bn-en"
    if bangla:
        return "bn"
    if latin:
        return "en"
    return "unknown"

def clean_text(text):
    text = re.sub(r"\r\n?", "\n", text)
    lines = [re.sub(r"[ \t]+", " ", x).strip() for x in text.split("\n")]
    return "\n".join(x for x in lines if x)

def first_date(text):
    patterns = [
        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
        r"\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b",
        r"\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})\b",
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1)
    return None
