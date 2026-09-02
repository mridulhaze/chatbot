"""
National University Bangladesh AI Assistant — Result Query Entity Extractor
Extracts program, year, exam type, session, roll/reg numbers, and sub-intents with multi-turn support.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple

from .aliases import (
    RESULT_TRIGGER_KEYWORDS,
    UNRELATED_RESULT_CONTEXTS,
    PROGRAM_ALIASES,
    YEAR_ALIASES,
    DATE_QUERY_KEYWORDS,
    PUBLICATION_CHECK_KEYWORDS,
    LINK_QUERY_KEYWORDS,
    REVALUATION_KEYWORDS,
    LATEST_NOTICE_KEYWORDS,
    ROLL_REGEX,
    REG_REGEX
)


def normalize_query_text(text: str) -> str:
    """Normalizes Unicode NFKC, converts Bengali digits, and cleans whitespace."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", str(text))
    # Digit translation
    trans = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    text = text.translate(trans)
    # Lowercase & normalize spaces
    text = re.sub(r'[\s\-_]+', ' ', text).strip()
    return text


@dataclass
class ResultQueryEntities:
    raw_query: str
    normalized_query: str
    is_result_query: bool
    sub_intent: str = "RESULT_GENERAL"  # RESULT_GENERAL, RESULT_LINK, RESULT_BY_PROGRAM, RESULT_PUBLICATION, RESULT_LATEST_NOTICE, RESULT_CHECK, RESULT_REVALUATION, RESULT_DATE_QUERY
    program: Optional[str] = None       # HONOURS, DEGREE, MASTERS, PROFESSIONAL, REVALUATION, ALL
    program_bn: Optional[str] = None
    year: Optional[str] = None          # 1ST_YEAR, 2ND_YEAR, 3RD_YEAR, 4TH_YEAR, FINAL_YEAR, PRELIMINARY
    year_bn: Optional[str] = None
    exam_type: Optional[str] = None
    session: Optional[str] = None
    roll_number: Optional[str] = None
    reg_number: Optional[str] = None
    confidence: float = 1.0
    matched_keywords: List[str] = field(default_factory=list)


def _detect_result_trigger(text: str) -> bool:
    """Checks if query contains result-related keywords without being an unrelated administrative query."""
    t_lower = text.lower()
    for unrelated in UNRELATED_RESULT_CONTEXTS:
        if unrelated in t_lower:
            return False

    for kw in RESULT_TRIGGER_KEYWORDS:
        pattern = r'(?:\b|\s|^|[^\w])' + re.escape(kw) + r'(?:ের|র|তে|এ|গুলো|দের)?(?:\b|\s|$|[^\w])'
        if re.search(pattern, t_lower):
            return True
    return False


def _find_program(text: str) -> Optional[Tuple[str, str]]:
    """Finds matching program entity by testing longest alias first."""
    t = text.lower()
    alias_tuples = []
    for key, p_data in PROGRAM_ALIASES.items():
        for alias in p_data["aliases"]:
            alias_tuples.append((alias.lower(), key, p_data["name_bn"]))
    alias_tuples.sort(key=lambda x: len(x[0]), reverse=True)

    for alias, key, name_bn in alias_tuples:
        pattern = r'(?:\b|\s|^|[^\w])' + re.escape(alias) + r'(?:ের|র|তে|এ|গুলো|দের)?(?:\b|\s|$|[^\w])'
        if re.search(pattern, t):
            return key, name_bn
    return None


def _find_year(text: str) -> Optional[Tuple[str, str]]:
    """Finds matching academic year entity by testing longest alias first."""
    t = text.lower()
    alias_tuples = []
    for key, y_data in YEAR_ALIASES.items():
        for alias in y_data["aliases"]:
            alias_tuples.append((alias.lower(), key, y_data["name_bn"]))
    alias_tuples.sort(key=lambda x: len(x[0]), reverse=True)

    for alias, key, name_bn in alias_tuples:
        pattern = r'(?:\b|\s|^|[^\w])' + re.escape(alias) + r'(?:ের|র|তে|এ|গুলো|দের)?(?:\b|\s|$|[^\w])'
        if re.search(pattern, t):
            return key, name_bn
    return None


def _extract_roll_and_reg(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extracts roll and registration numbers from the query if present."""
    roll = None
    reg = None
    m_roll = ROLL_REGEX.search(text)
    if m_roll:
        roll = m_roll.group(1)
    m_reg = REG_REGEX.search(text)
    if m_reg:
        reg = m_reg.group(1)
    return roll, reg


def extract_result_entities(query: str, history: Optional[List[Any]] = None) -> ResultQueryEntities:
    """
    Extracts structured entities and sub-intent from user query, resolving multi-turn context.
    """
    raw_query = query.strip()
    norm_query = normalize_query_text(raw_query)
    q_lower = norm_query.lower()

    is_trigger = _detect_result_trigger(norm_query)

    # Detect Roll / Reg
    roll, reg = _extract_roll_and_reg(norm_query)

    # Detect Program and Year
    program_res = _find_program(norm_query)
    year_res = _find_year(norm_query)

    prog_key = program_res[0] if program_res else None
    prog_bn = program_res[1] if program_res else None
    year_key = year_res[0] if year_res else None
    year_bn = year_res[1] if year_res else None

    # Multi-turn resolution from conversation history
    if history:
        for prev_msg in reversed(history):
            role = ""
            content = ""
            if isinstance(prev_msg, dict):
                role = prev_msg.get("role", "")
                content = prev_msg.get("content", "")
            elif hasattr(prev_msg, "content"):
                role = getattr(prev_msg, "role", "")
                content = prev_msg.content
            
            # Prioritize previous user utterances to avoid noise from bot templates/notices
            if role and role != "user":
                continue

            if content:
                prev_norm = normalize_query_text(content)
                if not prog_key:
                    prev_p = _find_program(prev_norm)
                    if prev_p:
                        prog_key, prog_bn = prev_p
                if not year_key:
                    prev_y = _find_year(prev_norm)
                    if prev_y:
                        year_key, year_bn = prev_y

    if year_key and not prog_key:
        prog_key = "HONOURS"
        prog_bn = "অনার্স"

    if (year_key or prog_key) and not is_trigger and history:
        is_trigger = True

    if not is_trigger:
        return ResultQueryEntities(
            raw_query=raw_query,
            normalized_query=norm_query,
            is_result_query=False
        )

    # Sub-intent Classification
    sub_intent = "RESULT_GENERAL"

    # Helper for checking term presence
    def _has_term(terms_list: List[str]) -> bool:
        for term in terms_list:
            if term.lower() in q_lower:
                return True
        return False

    # 1. Roll / Reg Check
    if roll or reg or _has_term(["check my result", "amar result", "আমার রেজাল্ট", "রোল দিয়ে"]):
        sub_intent = "RESULT_CHECK"
    # 2. Revaluation
    elif prog_key == "REVALUATION" or _has_term(REVALUATION_KEYWORDS):
        sub_intent = "RESULT_REVALUATION"
        prog_key = "REVALUATION"
        prog_bn = "পুনঃনিরীক্ষণ"
    # 3. Direct Link Inquiry ("result link", "where can i check", "দেখব কিভাবে", "কোথায় দেখব")
    elif _has_term(LINK_QUERY_KEYWORDS):
        sub_intent = "RESULT_LINK"
    # 4. Date Query ("result kobe", "result kobe dibe", "কবে দিবে")
    elif _has_term(DATE_QUERY_KEYWORDS):
        sub_intent = "RESULT_DATE_QUERY"
    # 5. Publication Status Check ("result published?", "result ber hoise?", "প্রকাশ হয়েছে?")
    elif _has_term(PUBLICATION_CHECK_KEYWORDS):
        sub_intent = "RESULT_PUBLICATION"
    # 6. Latest Notice ("latest result", "সর্বশেষ রেজাল্ট", "recent result notice")
    elif _has_term(LATEST_NOTICE_KEYWORDS):
        sub_intent = "RESULT_LATEST_NOTICE"
    # 7. Specific Program + Year (e.g. "honours 4th year result") -> Search recent notices & provide portal link
    elif prog_key and year_key:
        sub_intent = "RESULT_PUBLICATION"
    # 8. Specific Program alone (e.g. "honours result", "degree result", "masters result", "professional result")
    elif prog_key:
        sub_intent = "RESULT_BY_PROGRAM"
    # 9. Generic / Menu Query ("result", "রেজাল্ট", "ফলাফল", "NU result")
    else:
        sub_intent = "RESULT_GENERAL"

    return ResultQueryEntities(
        raw_query=raw_query,
        normalized_query=norm_query,
        is_result_query=True,
        sub_intent=sub_intent,
        program=prog_key,
        program_bn=prog_bn,
        year=year_key,
        year_bn=year_bn,
        roll_number=roll,
        reg_number=reg,
        confidence=1.0
    )
