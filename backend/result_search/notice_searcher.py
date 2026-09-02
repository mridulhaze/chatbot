"""
National University Bangladesh AI Assistant — Result Notice Search & Ranking
Searches recent official NU notices (both from database and official portals) and ranks result publications.
"""

import re
import time
import logging
from typing import Dict, Any, List, Optional, Tuple

from db.sql_store import get_sql_store
from .entity_extractor import ResultQueryEntities
from .config import RECENT_NOTICE_PAGE_URL, RESULT_CACHE_TTL_SECONDS

logger = logging.getLogger("NU_RESULT_NOTICE_SEARCHER")

# In-memory cached result notice lookups
_NOTICE_SEARCH_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}


class ResultNoticeSearcher:
    def __init__(self):
        self.sql_store = get_sql_store()

    def search_result_notices(
        self,
        entities: ResultQueryEntities,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Searches recent official notices and returns deterministic ranked results.
        """
        cache_key = f"{entities.program}_{entities.year}_{entities.sub_intent}"
        now = time.time()
        if cache_key in _NOTICE_SEARCH_CACHE:
            cached_time, cached_data = _NOTICE_SEARCH_CACHE[cache_key]
            if now - cached_time < RESULT_CACHE_TTL_SECONDS:
                return cached_data

        # 1. Build keyword search terms
        search_terms = self._build_search_terms(entities)

        # 2. Query database notices
        candidates = self._fetch_candidate_notices(search_terms)

        # 3. Deterministic scoring and ranking
        ranked_notices = self._rank_notices(candidates, entities)

        final_results = ranked_notices[:limit]
        _NOTICE_SEARCH_CACHE[cache_key] = (now, final_results)
        return final_results

    def _build_search_terms(self, entities: ResultQueryEntities) -> List[str]:
        """Constructs targeted search phrases for SQL/pattern matching."""
        terms = ["ফলাফল", "ফল প্রকাশ", "result", "পুনঃনিরীক্ষণ"]

        if entities.program == "HONOURS":
            terms.extend([
                "অনার্স", "সম্মান", "honours", "অনার্স ফাইনাল", "ফাইনাল ইয়ার", "ফাইনাল ইয়ার",
                "৪র্থ বর্ষ", "চতুর্থ বর্ষ", "১ম বর্ষ", "২য় বর্ষ", "৩য় বর্ষ"
            ])
            if entities.year == "1ST_YEAR":
                terms.extend(["১ম বর্ষ", "প্রথম বর্ষ", "1st year"])
            elif entities.year == "2ND_YEAR":
                terms.extend(["২য় বর্ষ", "২য় বর্ষ", "দ্বিতীয় বর্ষ", "2nd year"])
            elif entities.year == "3RD_YEAR":
                terms.extend(["৩য় বর্ষ", "৩য় বর্ষ", "তৃতীয় বর্ষ", "3rd year"])
            elif entities.year in ["4TH_YEAR", "FINAL_YEAR"]:
                terms.extend(["৪র্থ বর্ষ", "চতুর্থ বর্ষ", "4th year", "ফাইনাল", "অনার্স ফাইনাল", "ফাইনাল ইয়ার"])
        elif entities.program == "DEGREE":
            terms.extend(["ডিগ্রি", "ডিগ্রী", "পাস", "degree", "ডিগ্রি পাস"])
            if entities.year == "1ST_YEAR":
                terms.extend(["১ম বর্ষ", "প্রথম বর্ষ"])
            elif entities.year == "2ND_YEAR":
                terms.extend(["২য় বর্ষ", "২য় বর্ষ", "দ্বিতীয় বর্ষ"])
            elif entities.year == "3RD_YEAR":
                terms.extend(["৩য় বর্ষ", "৩য় বর্ষ", "তৃতীয় বর্ষ"])
        elif entities.program == "MASTERS":
            terms.extend(["মাস্টার্স", "স্নাতকোত্তর", "masters", "শেষ পর্ব", "ফাইনাল", "প্রিলিমিনারি", "প্রিলি"])
        elif entities.program == "PROFESSIONAL":
            terms.extend([
                "প্রফেশনাল", "professional", "বিবিএ", "সিএসই", "বিএড", "এমএড", "এলএলবি",
                "বিপিএড", "এমপিএড", "বিএমএড", "বিএসএড", "এমএসএড", "ট্যুরিজম", "thm",
                "লাইব্রেরি", "তথ্য বিজ্ঞান", "পোস্ট গ্র্যাজুয়েট", "পিজিডি", "bba", "mba", "cse", "llb", "bed"
            ])
        elif entities.program == "REVALUATION":
            terms.extend(["পুনঃনিরীক্ষণ", "পুনঃনিরীক্ষা", "খাতা", "চ্যালেঞ্জ"])

        return list(set(terms))

    def _fetch_candidate_notices(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """Queries the notices table for recent matching records."""
        conn = self.sql_store._get_connection()
        try:
            cursor = conn.cursor()
            conditions = " OR ".join(["title LIKE ?" for _ in search_terms])
            params = [f"%{t}%" for t in search_terms]

            sql = f"""
                SELECT id, title, url, pdf_url, published_date, iso_date
                FROM notices
                WHERE ({conditions})
                ORDER BY NULLIF(iso_date, '') DESC, id DESC
                LIMIT 80
            """
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.warning(f"Error fetching candidate notices: {e}")
            return []
        finally:
            conn.close()

    def _rank_notices(
        self,
        candidates: List[Dict[str, Any]],
        entities: ResultQueryEntities
    ) -> List[Dict[str, Any]]:
        """
        Deterministically scores and ranks candidate notices.
        Prioritizes exact program, exact year, recency, and result publication phrasing.
        """
        scored_list: List[Tuple[float, Dict[str, Any]]] = []

        for item in candidates:
            title = (item.get("title") or "").lower()
            iso_date = item.get("iso_date") or ""
            score = 0.0

            # 1. Result Publication Wording Boost
            if any(w in title for w in ["ফলাফল প্রকাশ", "ফল প্রকাশ", "পরীক্ষার ফলাফল", "চূড়ান্ত ফলাফল", "result publish", "ফলাফল"]):
                score += 40.0

            # 2. Recency Scoring (Favor 2026 notices)
            if iso_date >= "2026-08-30":
                score += 45.0
            elif iso_date >= "2026-08-01":
                score += 25.0
            elif iso_date >= "2026-01-01":
                score += 15.0

            # 3. Penalty for Unrelated notices without result
            if ("ভর্তি" in title or "admission" in title or "বিল প্রাপ্তি" in title or "ভুয়া সময়সূচি" in title) and "ফলাফল" not in title:
                score -= 80.0

            # 4. Program Matching
            if entities.program == "HONOURS":
                if any(w in title for w in ["অনার্স", "সম্মান", "honours"]):
                    score += 40.0
                    # Major boost for Honours Final Year Result notices
                    if any(w in title for w in ["অনার্স ফাইনাল", "অনার্স ৪র্থ বর্ষ", "ফাইনাল ইয়ার", "ফাইনাল ইয়ার"]):
                        score += 30.0
                elif any(w in title for w in ["ডিগ্রি", "মাস্টার্স", "বিএড", "পাস"]):
                    score -= 40.0
            elif entities.program == "DEGREE":
                if any(w in title for w in ["ডিগ্রি", "ডিগ্রী", "পাস", "degree"]):
                    score += 40.0
                elif any(w in title for w in ["অনার্স", "মাস্টার্স"]):
                    score -= 40.0
            elif entities.program == "MASTERS":
                if any(w in title for w in ["মাস্টার্স", "স্নাতকোত্তর", "masters"]):
                    score += 40.0
                elif any(w in title for w in ["অনার্স", "ডিগ্রি"]):
                    score -= 40.0
            elif entities.program == "PROFESSIONAL":
                prof_kw = [
                    "প্রফেশনাল", "professional", "পোস্ট গ্র্যাজুয়েট", "ডিপ্লোমা", "বিএড", "এমএড",
                    "সিএসই", "বিবিএ", "এলএলবি", "বিপিএড", "এমপিএড", "বিএমএড", "বিএসএড", "এমএসএড",
                    "ট্যুরিজম", "thm", "লাইব্রেরি", "তথ্য বিজ্ঞান", "পিজিডি", "bba", "mba", "cse", "llb", "bed"
                ]
                if any(w in title for w in prof_kw):
                    score += 45.0
            elif entities.program == "REVALUATION":
                if any(w in title for w in ["পুনঃনিরীক্ষণ", "পুনঃনিরীক্ষা", "খাতা"]):
                    score += 50.0

            # 5. Year Matching
            if entities.year == "1ST_YEAR":
                if any(w in title for w in ["১ম বর্ষ", "প্রথম বর্ষ", "1st year", "১ম সেমিস্টার", "প্রথম সেমিস্টার"]):
                    score += 35.0
                elif any(w in title for w in ["২য় বর্ষ", "৩য় বর্ষ", "৪র্থ বর্ষ", "2nd", "3rd", "4th"]):
                    score -= 30.0
            elif entities.year == "2ND_YEAR":
                if any(w in title for w in ["২য় বর্ষ", "২য় বর্ষ", "দ্বিতীয় বর্ষ", "2nd year", "২য় সেমিস্টার"]):
                    score += 35.0
                elif any(w in title for w in ["১ম বর্ষ", "৩য় বর্ষ", "৪র্থ বর্ষ"]):
                    score -= 30.0
            elif entities.year == "3RD_YEAR":
                if any(w in title for w in ["৩য় বর্ষ", "৩য় বর্ষ", "তৃতীয় বর্ষ", "3rd year"]):
                    score += 35.0
                elif any(w in title for w in ["১ম বর্ষ", "২য় বর্ষ", "৪র্থ বর্ষ"]):
                    score -= 30.0
            elif entities.year in ["4TH_YEAR", "FINAL_YEAR"]:
                if any(w in title for w in ["৪র্থ বর্ষ", "চতুর্থ বর্ষ", "4th year", "ফাইনাল", "ফাইনাল ইয়ার", "ফাইনাল ইয়ার"]):
                    score += 45.0
                elif any(w in title for w in ["১ম বর্ষ", "২য় বর্ষ", "৩য় বর্ষ"]):
                    score -= 30.0

            # 6. PDF Link bonus
            if item.get("pdf_url") or (item.get("url") and item.get("url").lower().endswith(".pdf")):
                score += 10.0

            if score > 0:
                scored_list.append((score, item))

        # Sort by score descending, then by date descending
        scored_list.sort(key=lambda x: (x[0], x[1].get("iso_date") or ""), reverse=True)
        return [item[1] for item in scored_list]
