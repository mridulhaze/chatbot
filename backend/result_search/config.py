"""
National University Bangladesh AI Assistant — Result Links & Portal Configuration
Provides centralized, configurable result URLs and portal routing definitions.
"""

from typing import Dict, Any, List

# Official NU Result Portals
MAIN_RESULT_PORTAL = "https://results.nu.ac.bd/"
RECENT_NOTICE_PAGE_URL = "https://www.nu.ac.bd/recent-news-notice.php"
EXAM_NOTICE_PAGE_URL = "https://www.nu.ac.bd/examination-notice.php"
EMS_PORTAL_URL = "http://ems.nu.ac.bd/"

# In-memory TTL cache duration (seconds)
RESULT_CACHE_TTL_SECONDS = 600

# Configurable Result Links Mapping
RESULT_LINKS: Dict[str, Dict[str, Any]] = {
    "HONOURS": {
        "canonical_name": "HONOURS",
        "bangla_name": "অনার্স",
        "english_name": "Honours",
        "url": "https://results.nu.ac.bd/honours",
        "active": True,
        "priority": 1,
        "aliases": [
            "honours", "hons", "honors", "অনার্স", "সম্মান", "স্নাতক সম্মান",
            "honours 1st", "honours 2nd", "honours 3rd", "honours 4th"
        ],
        "sms_format": "NU <H1/H2/H3/H4> <Roll/Reg_No> send to 16222",
        "description": "১ম, ২য়, ৩য় ও ৪র্থ বর্ষের ফলাফল"
    },
    "DEGREE": {
        "canonical_name": "DEGREE",
        "bangla_name": "ডিগ্রি (পাস)",
        "english_name": "Degree (Pass)",
        "url": "https://results.nu.ac.bd/degree",
        "active": True,
        "priority": 2,
        "aliases": [
            "degree", "degree pass", "pass course", "ডিগ্রি", "ডিগ্রী", "পাস",
            "পাস কোর্স", "স্নাতক পাস", "ডিগ্রি পাস"
        ],
        "sms_format": "NU DEG <Roll/Reg_No> send to 16222",
        "description": "১ম, ২য় ও ৩য় বর্ষের পাস ফলাফল"
    },
    "MASTERS": {
        "canonical_name": "MASTERS",
        "bangla_name": "মাস্টার্স",
        "english_name": "Masters",
        "url": "https://results.nu.ac.bd/masters",
        "active": True,
        "priority": 3,
        "aliases": [
            "masters", "master", "মাস্টার্স", "স্নাতকোত্তর", "m.a", "m.sc", "m.s.s", "m.com", "mba",
            "masters final", "masters preliminary", "masters preli", "প্রিলি", "মাস্টার্স শেষ পর্ব"
        ],
        "sms_format": "NU MF <Roll/Reg_No> send to 16222 (Final) / NU MP (Preli)",
        "description": "প্রিলিমিনারি ও ফাইনাল (শেষ পর্ব) ফলাফল"
    },
    "PROFESSIONAL": {
        "canonical_name": "PROFESSIONAL",
        "bangla_name": "প্রফেশনাল",
        "english_name": "Professional",
        "url": "https://results.nu.ac.bd/professional",
        "active": True,
        "priority": 4,
        "aliases": [
            "professional", "প্রফেশনাল", "পেশাগত", "bba", "cse", "ece", "b.ed", "bed", "b.m.ed",
            "llb", "pgd", "amt", "kmt", "fdt", "tourism", "thm", "aviation", "fashion"
        ],
        "sms_format": "NU PRO <Roll/Reg_No> send to 16222",
        "description": "বিবিএ, সিএসই, ইসিই, বিএড, এলএলবি, পিজিডি কোর্স"
    },
    "REVALUATION": {
        "canonical_name": "REVALUATION",
        "bangla_name": "পুনঃনিরীক্ষণ",
        "english_name": "Re-scrutiny / Revaluation",
        "url": "https://results.nu.ac.bd/revaluation",
        "active": True,
        "priority": 5,
        "aliases": [
            "revaluation", "rescrutiny", "re-scrutiny", "পুনঃনিরীক্ষণ", "পুনঃনিরীক্ষা",
            "খাতা পুনঃনিরীক্ষণ", "পুনর্নিরীক্ষণ", "খাতা চ্যালেঞ্জ", "বোর্ড চ্যালেঞ্জ",
            "board challenge", "challenge", "rescrutiny result", "revaluation result"
        ],
        "sms_format": "পোর্টালে সোনালী সেবার ট্রানজেকশন আইডি দিয়ে চেক করুন",
        "description": "পরীক্ষার খাতা পুনঃনিরীক্ষণের ফলাফল"
    },
    "ALL": {
        "canonical_name": "ALL",
        "bangla_name": "জাতীয় বিশ্ববিদ্যালয়",
        "english_name": "All Results Archive",
        "url": "https://results.nu.ac.bd/",
        "active": True,
        "priority": 6,
        "aliases": [
            "all", "সকল", "সব", "সকল রেজাল্ট", "archive", "আর্কাইভ", "main result", "ফলাফল আর্কাইভ"
        ],
        "sms_format": "NU <COURSE_CODE> <Roll/Reg_No> to 16222",
        "description": "জাতীয় বিশ্ববিদ্যালয়ের সার্বিক ফলাফল আর্কাইভ"
    }
}


def get_active_result_links() -> Dict[str, Dict[str, Any]]:
    """Returns all currently active result links sorted by priority."""
    return {k: v for k, v in sorted(RESULT_LINKS.items(), key=lambda item: item[1].get("priority", 99)) if v.get("active", True)}
