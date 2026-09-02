"""
National University Bangladesh AI Assistant — Officer Query Normalizer
Handles Bangla, English, Banglish, punctuation, plural forms, digit conversion, and general knowledge discrimination.
"""

import re
import unicodedata
from typing import Tuple, List, Set

BN_TO_EN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
EN_TO_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

# General Knowledge question patterns (Should NOT trigger directory search)
GENERAL_KNOWLEDGE_PATTERNS = [
    re.compile(r'\bwhat\s+(is|does|are)\b', re.IGNORECASE),
    re.compile(r'\bhow\s+to\s+(become|apply)\b', re.IGNORECASE),
    re.compile(r'\bmeaning\s+of\b', re.IGNORECASE),
    re.compile(r'\bdefinition\s+of\b', re.IGNORECASE),
    re.compile(r'\bjob\s+(description|role|responsibilities)\b', re.IGNORECASE),
    re.compile(r'(কী\s+কাজ\s+করে|কাজ\s+কী|কাজ\s+কি|ভূমিকা\s+কী|দায়িত্ব\s+কী|যোগ্যতা\s+কী|কাজের\s+বিবরণ|হতে\s+কী\s+লাগে|কীভাবে\s+হওয়া\s+যায়)', re.IGNORECASE),
    re.compile(r'(ki\s+kaj\s+kore|kaj\s+ki|kivabe\s+hoya\s+jay|kajer\s+biboron)', re.IGNORECASE)
]

# Explicit Directory Intent cues (forces directory search even if phrasing is short)
DIRECTORY_INTENT_PATTERNS = [
    re.compile(r'\b(who\s+is|who\s+are|list\s+all|list\s+of|show\s+all|find\s+all|contact\s+info|phone\s+number|email\s+address)\b', re.IGNORECASE),
    re.compile(r'(কে\s+আছেন|কারা\s+আছেন|তালিকা|সকল\s+কর্মকর্তা|ফোন\s+নম্বর|মোবাইল\s+নম্বর|ইমেইল|যোগাযোগ)', re.IGNORECASE),
    re.compile(r'\b(ke\s+ke\s+ache|kara\s+ache|list\s+dao|phone\s+number|email)\b', re.IGNORECASE)
]

# Common English Plurals in designations / roles
PLURAL_SUBSTITUTIONS = [
    (re.compile(r'\bprogrammers\b', re.IGNORECASE), 'programmer'),
    (re.compile(r'\bofficers\b', re.IGNORECASE), 'officer'),
    (re.compile(r'\bemployees\b', re.IGNORECASE), 'employee'),
    (re.compile(r'\bassistants\b', re.IGNORECASE), 'assistant'),
    (re.compile(r'\bdirectors\b', re.IGNORECASE), 'director'),
    (re.compile(r'\bregistrars\b', re.IGNORECASE), 'registrar'),
    (re.compile(r'\bengineers\b', re.IGNORECASE), 'engineer'),
    (re.compile(r'\banalysts\b', re.IGNORECASE), 'analyst'),
    (re.compile(r'\binspectors\b', re.IGNORECASE), 'inspector'),
    (re.compile(r'\bcontrollers\b', re.IGNORECASE), 'controller'),
    (re.compile(r'\bexecutives\b', re.IGNORECASE), 'executive'),
    (re.compile(r'\boperators\b', re.IGNORECASE), 'operator'),
    (re.compile(r'\btypists\b', re.IGNORECASE), 'typist'),
    (re.compile(r'\bguards\b', re.IGNORECASE), 'guard'),
    (re.compile(r'\bdrivers\b', re.IGNORECASE), 'driver'),
    (re.compile(r'\bdepartments\b', re.IGNORECASE), 'department'),
    (re.compile(r'\boffices\b', re.IGNORECASE), 'office'),
    (re.compile(r'\bsections\b', re.IGNORECASE), 'section')
]

# Common Banglish normalizations to canonical terms
BANGLISH_SUBSTITUTIONS = [
    (re.compile(r'\bshohokari\b|\bsohokari\b|\bshohokary\b|\bsohokary\b', re.IGNORECASE), 'assistant'),
    (re.compile(r'\bsinior\b|\bseenior\b', re.IGNORECASE), 'senior'),
    (re.compile(r'\bprokolpi\b|\bengineer\b', re.IGNORECASE), 'engineer'),
    (re.compile(r'\bporichalok\b|\bporicalok\b', re.IGNORECASE), 'director'),
    (re.compile(r'\bupoporichalok\b|\bupo-porichalok\b', re.IGNORECASE), 'deputy director'),
    (re.compile(r'\bkormokorta\b|\bkormokortader\b|\bkormokortara\b', re.IGNORECASE), 'officer'),
    (re.compile(r'\bkormochari\b|\bkormocarider\b|\bkormocarira\b', re.IGNORECASE), 'employee'),
    (re.compile(r'\bdoptor\b|\bdoptorer\b|\bdaptar\b|\bdoptore\b', re.IGNORECASE), 'department'),
    (re.compile(r'\bporikkha\b|\bporiksha\b|\bexam\b', re.IGNORECASE), 'exam'),
    (re.compile(r'\bniyontrok\b|\bcontroller\b', re.IGNORECASE), 'controller'),
    (re.compile(r'\brejistrar\b|\bregistrar\b|\bregistar\b', re.IGNORECASE), 'registrar'),
    (re.compile(r'\bsharirik\s+shikkha\b', re.IGNORECASE), 'physical education'),
    (re.compile(r'\bortho\s+o\s+hishab\b', re.IGNORECASE), 'finance'),
    (re.compile(r'\bgronthagar\b|\blibrary\b', re.IGNORECASE), 'library'),
    (re.compile(r'\bporibohon\b|\btransport\b', re.IGNORECASE), 'transport'),
    (re.compile(r'\bprokoushol\b|\bengineering\b', re.IGNORECASE), 'engineering'),
    (re.compile(r'\bbhorti\b|\badmission\b', re.IGNORECASE), 'admission'),
    (re.compile(r'\bjonosongjog\b|\bpr\b', re.IGNORECASE), 'public relations'),
    (re.compile(r'\bke\s+ke\s+ache\b|\bkara\b|\bke\s+ache\b', re.IGNORECASE), 'list'),
]

# Bengali specific role plural inflections (safe patterns targeting role words)
BN_ROLE_INFLECTION_PATTERNS = [
    (re.compile(r'(প্রোগ্রামার|কর্মকর্তা|কর্মচারী|পরিচালক|রেজিস্ট্রার|প্রকৌশলী|অফিসার|সহকারী)দের\s+তালিকা\b'), r'\1 তালিকা'),
    (re.compile(r'(প্রোগ্রামার|কর্মকর্তা|কর্মচারী|পরিচালক|রেজিস্ট্রার|প্রকৌশলী|অফিসার|সহকারী)দেরকে\b'), r'\1'),
    (re.compile(r'(প্রোগ্রামার|কর্মকর্তা|কর্মচারী|পরিচালক|রেজিস্ট্রার|প্রকৌশলী|অফিসার|সহকারী)দের\b'), r'\1'),
    (re.compile(r'(প্রোগ্রামার|কর্মকর্তা|কর্মচারী|পরিচালক|রেজিস্ট্রার|প্রকৌশলী|অফিসার|সহকারী)গণের\b'), r'\1'),
    (re.compile(r'(প্রোগ্রামার|কর্মকর্তা|কর্মচারী|পরিচালক|রেজিস্ট্রার|প্রকৌশলী|অফিসার|সহকারী)গণ\b'), r'\1'),
    (re.compile(r'(প্রোগ্রামার|কর্মকর্তা|কর্মচারী|পরিচালক|রেজিস্ট্রার|প্রকৌশলী|অফিসার|সহকারী)রা\b'), r'\1'),
    (re.compile(r'(প্রোগ্রামার|কর্মকর্তা|কর্মচারী|পরিচালক|রেজিস্ট্রার|প্রকৌশলী|অফিসার|সহকারী)বর্গ\b'), r'\1'),
    (re.compile(r'(প্রোগ্রামার|কর্মকর্তা|কর্মচারী|পরিচালক|রেজিস্ট্রার|প্রকৌশলী|অফিসার|সহকারী)সমূহ\b'), r'\1'),
]


def convert_bn_to_en_digits(text: str) -> str:
    """Converts Bengali numerals (০-৯) to English numerals (0-9)."""
    if not text:
        return ""
    return str(text).translate(BN_TO_EN_DIGITS)


def convert_en_to_bn_digits(text: str) -> str:
    """Converts English numerals (0-9) to Bengali numerals (০-৯)."""
    if not text:
        return ""
    return str(text).translate(EN_TO_BN_DIGITS)


def normalize_text(text: str) -> str:
    """Basic text normalization: Unicode NFKC, whitespace & digit cleanup."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFKC", str(text))
    norm = convert_bn_to_en_digits(norm)
    norm = norm.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    norm = norm.replace("–", "-").replace("—", "-")
    # Normalize decomposed Bengali nukta forms
    norm = norm.replace("\u09a1\u09bc", "ড়").replace("\u09a2\u09bc", "ঢ়").replace("\u09af\u09bc", "য়")
    norm = norm.replace("পরীক্ষা নিয়ন্ত্রক", "পরীক্ষা নিয়ন্ত্রক")
    norm = re.sub(r'[\r\n\t]+', ' ', norm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    return norm


def is_general_knowledge_query(query: str) -> bool:
    """
    Checks if a query is asking conceptual/informational questions about a role or department
    rather than looking up people in the directory.
    """
    q_norm = normalize_text(query).lower()
    for p in DIRECTORY_INTENT_PATTERNS:
        if p.search(q_norm):
            return False
    for p in GENERAL_KNOWLEDGE_PATTERNS:
        if p.search(q_norm):
            return True
    return False


def normalize_officer_query(query: str) -> str:
    """
    Deep normalization specifically for officer directory queries.
    Cleans punctuation, normalizes plurals, inflections, Banglish and returns a clean search string.
    """
    norm = normalize_text(query)
    for pat, rep in BN_ROLE_INFLECTION_PATTERNS:
        norm = pat.sub(rep, norm)
    for pat, rep in PLURAL_SUBSTITUTIONS:
        norm = pat.sub(rep, norm)
    for pat, rep in BANGLISH_SUBSTITUTIONS:
        norm = pat.sub(rep, norm)
    norm = re.sub(r'[?!,;:\(\)\[\]\{\}\<\>#@\$%\^&\*~`_+=|\\]', ' ', norm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    return norm


def normalize_phone(phone: str) -> str:
    """Standardizes phone and mobile numbers to clean numeric strings."""
    if not phone:
        return ""
    p = convert_bn_to_en_digits(phone.strip())
    p = re.sub(r'[^\d]', '', p)
    if p.startswith("880"):
        p = "0" + p[3:]
    elif p.startswith("88"):
        p = p[2:]
    return p


def normalize_email(email: str) -> str:
    """Standardizes email addresses."""
    if not email:
        return ""
    return email.strip().lower()
