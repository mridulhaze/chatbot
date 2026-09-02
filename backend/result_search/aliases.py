"""
National University Bangladesh AI Assistant — Result Aliases & Keyword Dictionaries
Provides comprehensive keyword, program, year, exam-type, and sub-intent mappings.
"""

import re
from typing import Dict, List, Any

# Primary Result Triggers (Bangla, English, Banglish)
RESULT_TRIGGER_KEYWORDS: List[str] = [
    # English
    "result", "results", "cgpa", "gpa", "grading", "marks", "marksheet", "score", "grade",
    # Bangla
    "রেজাল্ট", "ফলাফল", "ফল", "গ্রেড", "গ্রেডিং", "মার্কস", "নম্বরপত্র", "সিজিপিএ", "জিপিএ",
    "পুনঃনিরীক্ষণ", "পুনঃনিরীক্ষা", "পুনর্নিরীক্ষণ", "খাতা চ্যালেঞ্জ", "বোর্ড চ্যালেঞ্জ",
    # Banglish & Transliterations
    "folafol", "fol", "rejalt", "rijalt", "resalt"
]

# Unrelated Contexts (Must not hijack if only these words are present without result inquiry)
UNRELATED_RESULT_CONTEXTS: List[str] = [
    "result processing department", "result branch address", "where is controller of exam office"
]

# Program Mappings
PROGRAM_ALIASES: Dict[str, Dict[str, Any]] = {
    "HONOURS": {
        "canonical": "HONOURS",
        "name_bn": "অনার্স",
        "name_en": "Honours",
        "aliases": [
            "honours", "hons", "honors", "অনার্স", "সম্মান", "স্নাতক সম্মান", "স্নাতক (সম্মান)",
            "honours 1st", "honours 2nd", "honours 3rd", "honours 4th", "hons 1st", "hons 2nd",
            "hons 3rd", "hons 4th", "hons final", "অনার্স ১ম", "অনার্স ২য়", "অনার্স ৩য়", "অনার্স ৪র্থ"
        ]
    },
    "DEGREE": {
        "canonical": "DEGREE",
        "name_bn": "ডিগ্রি (পাস)",
        "name_en": "Degree (Pass)",
        "aliases": [
            "degree", "degree pass", "pass course", "pass", "ডিগ্রি", "ডিগ্রী", "পাস", "পাস কোর্স",
            "স্নাতক পাস", "স্নাতক (পাস)", "ডিগ্রি পাস", "ডিগ্রী পাস", "degree 1st", "degree 2nd",
            "degree 3rd", "ডিগ্রি ১ম", "ডিগ্রি ২য়", "ডিগ্রি ৩য়"
        ]
    },
    "MASTERS": {
        "canonical": "MASTERS",
        "name_bn": "মাস্টার্স",
        "name_en": "Masters",
        "aliases": [
            "masters", "master", "মাস্টার্স", "স্নাতকোত্তর", "m.a", "m.sc", "m.s.s", "m.com", "mba",
            "masters final", "masters preliminary", "masters preli", "preli", "preliminary",
            "প্রিলিমিনারি", "প্রিলি", "মাস্টার্স শেষ পর্ব", "মাস্টার্স ফাইনাল", "মাস্টার্স ১ম পর্ব"
        ]
    },
    "PROFESSIONAL": {
        "canonical": "PROFESSIONAL",
        "name_bn": "প্রফেশনাল",
        "name_en": "Professional",
        "aliases": [
            "professional", "প্রফেশনাল", "পেশাগত", "llb", "ll.b", "law", "আইন", "এলএলবি", "এলএল.বি",
            "b.ed", "bed", "b.ed honours", "b.ed hons", "m.ed", "med", "বিএড", "এমএড",
            "bped", "b.p.ed", "mped", "m.p.ed", "বিপিএড", "এমপিএড", "শারীরিক শিক্ষা",
            "bmed", "b.m.ed", "বিএমএড", "মাদ্রাসা শিক্ষা",
            "bsed", "b.s.ed", "msed", "m.s.ed", "বিএসএড", "এমএসএড", "স্পেশাল এডুকেশন",
            "bba", "mba", "বিবিএ", "এমবিএ", "ব্যবসা প্রশাসন",
            "cse", "computer science", "কম্পিউটার সায়েন্স", "কম্পিউটার বিজ্ঞান",
            "tourism", "hospitality", "thm", "ট্যুরিজম", "হসপিটালিটি",
            "library", "information science", "islm", "lis", "লাইব্রেরি", "তথ্য বিজ্ঞান", "গ্রন্থাগার ও তথ্যবিজ্ঞান",
            "pgd", "পিজিডি", "পোস্ট গ্র্যাজুয়েট ডিপ্লোমা", "amt", "kmt", "fdt", "aviation", "fashion design"
        ]
    },
    "REVALUATION": {
        "canonical": "REVALUATION",
        "name_bn": "পুনঃনিরীক্ষণ",
        "name_en": "Revaluation",
        "aliases": [
            "revaluation", "rescrutiny", "re-scrutiny", "পুনঃনিরীক্ষণ", "পুনঃনিরীক্ষা",
            "খাতা পুনঃনিরীক্ষণ", "পুনর্নিরীক্ষণ", "খাতা চ্যালেঞ্জ", "বোর্ড চ্যালেঞ্জ",
            "board challenge", "challenge", "rescrutiny result", "revaluation result",
            "খাতা দেখা", "নম্বর চ্যালেঞ্জ", "পুনঃনিরীক্ষণের রেজাল্ট"
        ]
    }
}

# Academic Year Mappings
YEAR_ALIASES: Dict[str, Dict[str, Any]] = {
    "1ST_YEAR": {
        "canonical": "1ST_YEAR",
        "name_bn": "১ম বর্ষ",
        "name_en": "1st Year",
        "aliases": [
            "1st year", "1st", "first year", "first", "১ম বর্ষ", "১ম", "1ম বর্ষ", "1ম",
            "প্রথম বর্ষ", "প্রথম", "1st yr", "১ম ইয়ার", "১ম ইয়ার", "1ম ইয়ার", "1ম ইয়ার",
            "1st semester", "১ম সেমিস্টার", "1ম সেমিস্টার"
        ]
    },
    "2ND_YEAR": {
        "canonical": "2ND_YEAR",
        "name_bn": "২য় বর্ষ",
        "name_en": "2nd Year",
        "aliases": [
            "2nd year", "2nd", "second year", "second", "২য় বর্ষ", "২য়", "২য় বর্ষ", "২য়",
            "2য় বর্ষ", "2য়", "2য় বর্ষ", "2য়", "দ্বিতীয় বর্ষ", "দ্বিতীয় বর্ষ", "দ্বিতীয়",
            "দ্বিতীয়", "2nd yr", "২য় ইয়ার", "২য় ইয়ার", "2য় ইয়ার", "2য় ইয়ার"
        ]
    },
    "3RD_YEAR": {
        "canonical": "3RD_YEAR",
        "name_bn": "৩য় বর্ষ",
        "name_en": "3rd Year",
        "aliases": [
            "3rd year", "3rd", "third year", "third", "৩য় বর্ষ", "৩য়", "৩য় বর্ষ", "৩য়",
            "3য় বর্ষ", "3য়", "3য় বর্ষ", "3য়", "তৃতীয় বর্ষ", "তৃতীয় বর্ষ", "তৃতীয়",
            "তৃতীয়", "3rd yr", "৩য় ইয়ার", "৩য় ইয়ার", "3য় ইয়ার", "3য় ইয়ার"
        ]
    },
    "4TH_YEAR": {
        "canonical": "4TH_YEAR",
        "name_bn": "৪র্থ বর্ষ",
        "name_en": "4th Year",
        "aliases": [
            "4th year", "4th", "fourth year", "fourth", "৪র্থ বর্ষ", "৪র্থ", "4র্থ বর্ষ", "4র্থ",
            "চতুর্থ বর্ষ", "চতুর্থ", "4th yr", "৪র্থ ইয়ার", "৪র্থ ইয়ার", "4র্থ ইয়ার", "4র্থ ইয়ার"
        ]
    },
    "FINAL_YEAR": {
        "canonical": "FINAL_YEAR",
        "name_bn": "ফাইনাল (শেষ পর্ব)",
        "name_en": "Final Year",
        "aliases": [
            "final year", "final", "শেষ বর্ষ", "শেষ পর্ব", "চূড়ান্ত বর্ষ", "চূড়ান্ত বর্ষ",
            "ফাইনাল", "ফাইনাল ইয়ার", "ফাইনাল ইয়ার"
        ]
    },
    "PRELIMINARY": {
        "canonical": "PRELIMINARY",
        "name_bn": "প্রিলিমিনারি (১ম পর্ব)",
        "name_en": "Preliminary",
        "aliases": [
            "preliminary", "preli", "প্রিলিমিনারি", "প্রিলি", "১ম পর্ব", "প্রথম পর্ব"
        ]
    }
}

# Sub-Intent Keywords
DATE_QUERY_KEYWORDS = [
    "kobe", "kokhon", "kobe dibe", "kobe asbe", "date", "when", "time", "schedule",
    "কবে", "কখন", "কবে দিবে", "কবে দেবে", "কবে প্রকাশ", "তারিখ", "কবে আসবে", "প্রকাশের তারিখ",
    "কবে নাগাদ", "কবে হতে পারে", "kobe hobe"
]

PUBLICATION_CHECK_KEYWORDS = [
    "publish", "published", "ber hoise", "ber hoyeche", "publish hoise", "publish hoyeche",
    "is out", "released", "declared", "প্রকাশ", "প্রকাশিত", "প্রকাশ হয়েছে", "প্রকাশিত হয়েছে",
    "বের হয়েছে", "বের হইছে", "দিয়েছে কি", "দিয়েছে কি", "আউট হয়েছে", "হইছে কি"
]

LINK_QUERY_KEYWORDS = [
    "link", "website", "portal", "url", "site", "address", "where", "how to check", "check link",
    "লিংক", "ওয়েবসাইট", "পোর্টাল", "ইউআরএল", "সাইট", "কোথায় দেখব", "দেখার লিংক", "কীভাবে দেখব",
    "কিভাবে দেখব", "দেখব কিভাবে", "দেখব কীভাবে", "কোথায় পাওয়া যাবে", "দেখব কেমন করে", "where to check",
    "check my result", "দেখার নিয়ম", "দেখার নিয়ম", "পদ্ধতি", "কীভাবে দেখব", "কিভাবে দেখতে হয়"
]

REVALUATION_KEYWORDS = [
    "revaluation", "rescrutiny", "re-scrutiny", "পুনঃনিরীক্ষণ", "পুনঃনিরীক্ষা", "খাতা পুনঃনিরীক্ষণ",
    "পুনর্নিরীক্ষণ", "খাতা চ্যালেঞ্জ", "বোর্ড চ্যালেঞ্জ", "board challenge", "challenge"
]

LATEST_NOTICE_KEYWORDS = [
    "latest", "recent", "new", "last", "latest notice", "recent notice", "current",
    "সর্বশেষ", "সাম্প্রতিক", "নতুন", "শেষ", "সর্বশেষ নোটিশ", "সাম্প্রতিক নোটিশ"
]

ROLL_REGEX = re.compile(r'\b(?:roll|রোল)[\s:\-]*([0-9০-৯]{4,14})\b', re.IGNORECASE)
REG_REGEX = re.compile(r'\b(?:reg|registration|রেজিস্ট্রেশন)[\s:\-]*([0-9০-৯]{4,16})\b', re.IGNORECASE)

