"""
National University Bangladesh AI Assistant — Officer Query Entity Extractor
Extracts name, designation, department, phone, email, pagination, and intent with multi-turn support.
"""

import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple

from .normalizer import (
    normalize_text,
    normalize_officer_query,
    normalize_phone,
    normalize_email,
    is_general_knowledge_query
)
from .aliases import (
    DEPARTMENT_ALIASES,
    DESIGNATION_ALIASES,
    RELATIONSHIP_INDICATORS,
    DIRECTORY_STOPWORDS
)

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_REGEX = re.compile(r'(?:\+?880|01)[3-9]\d{8}|02\d{7,9}|(?:\+?৮৮০|০১)[৩-৯][০-৯]{8}')

PAGINATION_NEXT_PATTERNS = [
    re.compile(r'\b(next|next\s+page|next\s+50|more|show\s+more)\b', re.IGNORECASE),
    re.compile(r'(পরবর্তী|পরের\s+পৃষ্ঠা|আরো\s+দেখান|সামনে)', re.IGNORECASE)
]
PAGINATION_PREV_PATTERNS = [
    re.compile(r'\b(prev|previous|previous\s+page|back)\b', re.IGNORECASE),
    re.compile(r'(পূর্ববর্তী|আগের\s+পৃষ্ঠা|পেছনে)', re.IGNORECASE)
]
PAGINATION_PAGE_NUM_REGEX = re.compile(r'\b(?:page|পৃষ্ঠা)\s*([0-9০-৯]+)\b', re.IGNORECASE)


@dataclass
class OfficerQueryEntities:
    raw_query: str
    normalized_query: str
    intent: str
    name: Optional[str] = None
    designation: Optional[str] = None          # Canonical English
    designation_bn: Optional[str] = None       # Canonical Bangla
    department_slug: Optional[str] = None      # Canonical Slug
    department_name: Optional[str] = None      # Canonical Name
    department_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_all_query: bool = False
    is_all_departments_query: bool = False
    is_general_knowledge: bool = False
    confidence: float = 1.0
    match_strategy: str = "exact"
    page: int = 1


def _find_department(text: str) -> Optional[Tuple[Dict[str, Any], str]]:
    """Finds matching department entity by checking longest alias first."""
    t = text.lower()
    # Sort departments by alias length descending
    all_dept_alias_tuples = []
    for dept in DEPARTMENT_ALIASES:
        for alias in dept["aliases"]:
            all_dept_alias_tuples.append((alias.lower(), dept))
    all_dept_alias_tuples.sort(key=lambda x: len(x[0]), reverse=True)

    for alias, dept in all_dept_alias_tuples:
        # Check boundary match or substring match
        pattern = r'(?:\b|\s|^)' + re.escape(alias) + r'(?:\b|\s|$)'
        match = re.search(pattern, t)
        if match:
            return dept, alias
    return None


def _find_designation(text: str) -> Optional[Tuple[Dict[str, Any], str]]:
    """Finds matching designation entity by checking longest alias first."""
    t = text.lower()
    all_desig_alias_tuples = []
    for desig in DESIGNATION_ALIASES:
        for alias in desig["aliases"]:
            all_desig_alias_tuples.append((alias.lower(), desig))
    all_desig_alias_tuples.sort(key=lambda x: len(x[0]), reverse=True)

    for alias, desig in all_desig_alias_tuples:
        pattern = r'(?:\b|\s|^)' + re.escape(alias) + r'(?:\b|\s|$)'
        match = re.search(pattern, t)
        if match:
            return desig, alias
    return None


def extract_directory_entities(query: str, history: Optional[List[Any]] = None) -> OfficerQueryEntities:
    """
    Extracts structured entities (Name, Designation, Department, Phone, Email)
    from a user query with multi-turn awareness and general knowledge isolation.
    """
    raw_query = query.strip()
    norm_query = normalize_officer_query(raw_query)
    norm_lower = norm_query.lower()

    # 1. Check if General Knowledge question (e.g. "What is an assistant programmer?")
    if is_general_knowledge_query(raw_query):
        return OfficerQueryEntities(
            raw_query=raw_query,
            normalized_query=norm_query,
            intent="GENERAL_KNOWLEDGE",
            is_general_knowledge=True,
            confidence=0.9
        )

    # 2. Check for Pagination commands (next / prev / page X)
    page_num = 1
    for p in PAGINATION_NEXT_PATTERNS:
        if p.search(norm_lower):
            page_num = 2  # Handled in multi-turn
    for p in PAGINATION_PREV_PATTERNS:
        if p.search(norm_lower):
            page_num = 1
    page_match = PAGINATION_PAGE_NUM_REGEX.search(raw_query)
    if page_match:
        try:
            page_num = int(normalize_text(page_match.group(1)))
        except Exception:
            pass

    # 3. Check for ALL Departments mega-menu query
    all_dept_triggers = [
        "সকল দপ্তর", "সব দপ্তর", "সকল অফিস", "দপ্তরের তালিকা", "দপ্তর সমূহ", "দপ্তরসমূহ",
        "অফিস সমুহ", "সকল শাখা", "all department", "all departments", "all offices", "office list",
        "department list", "mega menu", "offices directory"
    ]
    if any(trig in norm_lower for trig in all_dept_triggers) and not any(k in norm_lower for k in ["employee", "officer", "কর্মকর্তা", "কর্মচারী", "staff"]):
        return OfficerQueryEntities(
            raw_query=raw_query,
            normalized_query=norm_query,
            intent="OFFICE_DIRECTORY",
            is_all_departments_query=True,
            confidence=1.0
        )

    # 4. Check for ALL Employees across NU query
    all_emp_triggers = [
        "সকল কর্মকর্তা", "সব কর্মকর্তা", "সকল কর্মচারী", "সব কর্মচারী", "সকল কর্মকর্তা কর্মচারী",
        "সকল স্টাফ", "all employees", "all employee", "all staff", "all officers", "all officer",
        "complete employee list", "everyone in nu", "nu employees"
    ]
    if any(trig in norm_lower for trig in all_emp_triggers) and not _find_department(norm_lower) and not _find_designation(norm_lower):
        return OfficerQueryEntities(
            raw_query=raw_query,
            normalized_query=norm_query,
            intent="ALL_OFFICERS",
            is_all_query=True,
            confidence=1.0,
            page=page_num
        )

    # 5. Extract Email
    email_match = EMAIL_REGEX.search(raw_query)
    extracted_email = normalize_email(email_match.group(0)) if email_match else None

    # 6. Extract Phone / Mobile
    phone_match = PHONE_REGEX.search(raw_query)
    extracted_phone = normalize_phone(phone_match.group(0)) if phone_match else None

    # Working string to strip matched entities from
    remaining_text = norm_query

    # 7. Extract Department Entity
    dept_res = _find_department(remaining_text)
    extracted_dept_slug = None
    extracted_dept_name = None
    extracted_dept_url = None
    if dept_res:
        dept_data, dept_alias = dept_res
        extracted_dept_slug = dept_data["slug"]
        extracted_dept_name = f"{dept_data['name_bn']} ({dept_data['name_en']})"
        extracted_dept_url = dept_data["url"]
        # Remove matched department alias from remaining text
        remaining_text = re.sub(r'(?:\b|\s|^)' + re.escape(dept_alias) + r'(?:\b|\s|$)', ' ', remaining_text, flags=re.IGNORECASE)

    # 8. Extract Designation Entity
    desig_res = _find_designation(remaining_text)
    extracted_desig_en = None
    extracted_desig_bn = None
    if desig_res:
        desig_data, desig_alias = desig_res
        extracted_desig_en = desig_data["canonical_en"]
        extracted_desig_bn = desig_data["canonical_bn"]
        # Remove matched designation alias from remaining text
        remaining_text = re.sub(r'(?:\b|\s|^)' + re.escape(desig_alias) + r'(?:\b|\s|$)', ' ', remaining_text, flags=re.IGNORECASE)

    # 9. Clean relationship indicators, possessive suffixes, and directory stopwords from remaining text
    # Run multiple passes to handle stacked tokens (e.g. "দপ্তরের সকল কর্মকর্তা")
    for _ in range(3):
        for rel in sorted(RELATIONSHIP_INDICATORS, key=len, reverse=True):
            remaining_text = re.sub(r'(?:\b|\s|^)' + re.escape(rel) + r'(?:\b|\s|$)', ' ', remaining_text, flags=re.IGNORECASE)
            # Also clean if attached as suffix (e.g. "দপ্তরের" -> "")
            if rel.startswith("দপ্ত") or rel.startswith("অফিস"):
                remaining_text = re.sub(re.escape(rel), ' ', remaining_text, flags=re.IGNORECASE)

        for stop in sorted(DIRECTORY_STOPWORDS, key=len, reverse=True):
            remaining_text = re.sub(r'(?:\b|\s|^)' + re.escape(stop) + r'(?:\b|\s|$)', ' ', remaining_text, flags=re.IGNORECASE)

    if extracted_email:
        remaining_text = remaining_text.replace(extracted_email, ' ')
    if phone_match:
        remaining_text = remaining_text.replace(phone_match.group(0), ' ')

    # Strip leftover trailing/leading Bengali possessive markers like 'ের', 'র', 'তে', 'এ'
    remaining_text = re.sub(r'\b(ের|র|তে|এ|এর)\b', ' ', remaining_text)
    remaining_text = re.sub(r'\s+', ' ', remaining_text).strip()

    # 10. Candidate Name
    extracted_name = None
    # If remaining text has meaningful name tokens (e.g. "Mridul Roy", "মোঃ শাহনেওয়াজ", "মৃদুল")
    # Must not be a generic leftover filler word
    generic_fillers = {
        "te", "er", "in", "at", "nu", "of", "to", "for", "the", "and", "or", "from",
        "employee", "employees", "officer", "officers", "staff", "staffs", "list", "show",
        "কর্মকর্তা", "কর্মচারী", "অফিসার", "স্টাফ", "তালিকা", "তথ্য", "সকল", "সব", "কারা",
        "কর্মকর্তাদের", "কর্মচারীদের", "কর্মকর্তারা", "কর্মচারীরা", "কর্মকর্তাগণ", "কর্মচারীগণ",
        "কর্মকর্তাবৃন্দ", "কর্মচারীবৃন্দ", "কর্মকর্তাবৃন্দের", "কর্মচারীবৃন্দের",
        "বৃন্দ", "বৃন্দের", "গণ", "গণের", "ও", "এবং", "দেখান", "দেখাও", "দিন", "বলুন"
    }
    # Check if remaining_text still has non-filler meaningful words
    clean_tokens = [w for w in remaining_text.split() if w.lower() not in generic_fillers and len(w) > 1]
    cleaned_name_candidate = " ".join(clean_tokens).strip()

    if (
        len(cleaned_name_candidate) >= 2
        and not cleaned_name_candidate.isdigit()
        and cleaned_name_candidate.lower() not in generic_fillers
        and not any(cleaned_name_candidate.lower() == f for f in generic_fillers)
    ):
        extracted_name = cleaned_name_candidate

    # 11. Multi-Turn Context Resolution
    if history:
        # Check previous turn context if current query is a refinement (e.g. "only assistant programmers", "in ICT")
        prev_entities = _extract_previous_turn_entities(history)
        if prev_entities:
            # Inherit department if current query only has designation
            if not extracted_dept_slug and extracted_desig_en and prev_entities.get("department_slug"):
                extracted_dept_slug = prev_entities["department_slug"]
                extracted_dept_name = prev_entities.get("department_name")
                extracted_dept_url = prev_entities.get("department_url")
            # Inherit designation if current query only has department
            elif not extracted_desig_en and extracted_dept_slug and prev_entities.get("designation"):
                extracted_desig_en = prev_entities["designation"]
                extracted_desig_bn = prev_entities.get("designation_bn")
            # Handle relative pagination
            if any(p.search(norm_lower) for p in PAGINATION_NEXT_PATTERNS):
                page_num = (prev_entities.get("page", 1) or 1) + 1
                extracted_dept_slug = extracted_dept_slug or prev_entities.get("department_slug")
                extracted_dept_name = extracted_dept_name or prev_entities.get("department_name")
                extracted_dept_url = extracted_dept_url or prev_entities.get("department_url")
                extracted_desig_en = extracted_desig_en or prev_entities.get("designation")
                extracted_desig_bn = extracted_desig_bn or prev_entities.get("designation_bn")
                extracted_name = extracted_name or prev_entities.get("name")

    # 12. Derive Specific Intent
    if extracted_email:
        intent = "OFFICER_BY_EMAIL"
    elif extracted_phone:
        intent = "OFFICER_BY_PHONE"
    elif extracted_name and extracted_desig_en and extracted_dept_slug:
        intent = "OFFICER_BY_NAME_AND_DESIGNATION_AND_DEPARTMENT"
    elif extracted_name and extracted_dept_slug:
        intent = "OFFICER_BY_NAME_AND_DEPARTMENT"
    elif extracted_name and extracted_desig_en:
        intent = "OFFICER_BY_NAME_AND_DESIGNATION"
    elif extracted_desig_en and extracted_dept_slug:
        intent = "OFFICER_BY_DESIGNATION_AND_DEPARTMENT"
    elif extracted_desig_en:
        intent = "OFFICER_BY_DESIGNATION"
    elif extracted_dept_slug:
        intent = "OFFICER_BY_DEPARTMENT"
    elif extracted_name:
        intent = "OFFICER_BY_NAME"
    else:
        intent = "OFFICER_DIRECTORY_SEARCH"

    return OfficerQueryEntities(
        raw_query=raw_query,
        normalized_query=norm_query,
        intent=intent,
        name=extracted_name,
        designation=extracted_desig_en,
        designation_bn=extracted_desig_bn,
        department_slug=extracted_dept_slug,
        department_name=extracted_dept_name,
        department_url=extracted_dept_url,
        phone=extracted_phone,
        email=extracted_email,
        page=page_num,
        confidence=1.0 if (extracted_dept_slug or extracted_desig_en or extracted_name or extracted_phone or extracted_email) else 0.7
    )


def _extract_previous_turn_entities(history: List[Any]) -> Dict[str, Any]:
    """Helper to inspect the most recent user and assistant turns for directory entities."""
    if not history:
        return {}
    # Scan backward for the most recent directory query
    for item in reversed(history):
        content = getattr(item, 'content', None) or (item.get('content') if isinstance(item, dict) else str(item))
        if not content:
            continue
        dept_res = _find_department(content)
        desig_res = _find_designation(content)
        res = {}
        if dept_res:
            dept_data, _ = dept_res
            res["department_slug"] = dept_data["slug"]
            res["department_name"] = f"{dept_data['name_bn']} ({dept_data['name_en']})"
            res["department_url"] = dept_data["url"]
        if desig_res:
            desig_data, _ = desig_res
            res["designation"] = desig_data["canonical_en"]
            res["designation_bn"] = desig_data["canonical_bn"]
        if res:
            return res
    return {}
