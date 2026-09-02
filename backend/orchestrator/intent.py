"""
National University AI Assistant — Intent Classification Engine
Supports 40+ granular student intents, multi-modal query normalization (Bangla, English, Banglish, Typos),
confidence scoring, entity extraction (Token ID, Service Code, Course, Year), and anti-hallucination routing.
"""

import re
from typing import Tuple, Optional, Dict, Any, List

TOKEN_ID_PATTERN = re.compile(r'\b(NU-\d{4}-\d{6})\b', re.IGNORECASE)

SERVICE_KEYWORDS = {
    "FORM_FILLUP": ["form fillup", "form fill up", "form fill-up", "ফরম পূরণ", "ফরম ফিলাপ", "formfilup", "ফরমফি"],
    "TC": ["tc", "transfer certificate", "ছাড়পত্র", "টিসি", "কলেজ পরিবর্তন", "college change", "college transfer"],
    "RESCRUTINY": ["rescrutiny", "re-check", "খাতা পুনঃনিরীক্ষণ", "পুনঃনিরীক্ষণ", "খাতা চ্যালেঞ্জ", "board challenge", "re-evaluation"],
    "EMS": ["ems", "ইএমএস", "ems portal", "ems লগইন", "ems পাসওয়ার্ড", "ems dashboard"],
    "CERTIFICATE": ["certificate", "সনদপত্র", "মূল সনদ", "সাময়িক সনদ", "সার্টিফিকেট", "provisional certificate", "duplicate certificate"],
    "MARKSHEET": ["marksheet", "transcript", "নম্বরপত্র", "ট্রান্সক্রিপ্ট", "মার্কশিট", "একাডেমিক ট্রান্সক্রিপ্ট", "wes verification"],
    "REGISTRATION": ["registration", "রেজিস্ট্রেশন", "রেজিস্ট্রেশন কার্ড", "দ্বৈত ভর্তি", "re-registration", "reg card"],
    "ADMISSION": ["admission", "ভর্তি", "app11", "app1", "মেধা তালিকা", "রিলিজ স্লিপ", "release slip", "কোটা", "merit list"],
    "RESULT": ["result", "রেজাল্ট", "ফলাফল", "withheld", "স্থগিত", "cgpa", "gpa", "গ্রেড", "fail", "reslt"]
}

# Granular Keyword & Pattern Rules for 40+ Intents
INTENT_PATTERNS: List[Dict[str, Any]] = [
    # --- Admission Family ---
    {
        "intent": "ADMISSION_ELIGIBILITY",
        "keywords": ["যোগ্যতা", "eligibility", "point", "পয়েন্ট", "gpa কত লাগে", "minimum gpa", "যোগ্যতা কী", "requirements"],
        "context_keywords": ["admission", "ভর্তি", "অনার্স", "ডিগ্রি", "মাস্টার্স"]
    },
    {
        "intent": "ADMISSION_FEE",
        "keywords": ["ভর্তি ফি", "ভর্তির টাকা", "admission fee", "প্রাথমিক আবেদন ফি", "কত টাকা লাগবে ভর্তিতে", "bhorti fee"],
        "context_keywords": ["ভর্তি", "admission", "ফি", "fee"]
    },
    {
        "intent": "RELEASE_SLIP",
        "keywords": ["রিলিজ স্লিপ", "release slip", "রিলিজ স্লিপে আবেদন", "কয়টি কলেজ", "release slip result", "রিলিজ স্লিপ কি"],
        "context_keywords": ["রিলিজ", "release", "slip"]
    },
    {
        "intent": "MERIT_LIST",
        "keywords": ["মেধা তালিকা", "merit list", "১ম মেধা তালিকা", "২য় মেধা তালিকা", "প্রথম মেধা তালিকা", "দ্বিতীয় মেধা তালিকা", "মেধা তালিকায় নাম", "chance paici kina"],
        "context_keywords": ["মেধা", "merit"]
    },
    {
        "intent": "ADMISSION_CONFIRMATION",
        "keywords": ["ভর্তি নিশ্চিত", "ভর্তি নিশ্চায়ন", "admission confirmation", "ভর্তি বাতিল", "cancel admission", "চূড়ান্ত ভর্তি", "final admission form"],
        "context_keywords": ["নিশ্চায়ন", "confirm", "বাতিল", "cancel"]
    },
    {
        "intent": "COLLEGE_SELECTION",
        "keywords": ["কলেজ পছন্দ", "কলেজ চয়েস", "college selection", "college choice", "পছন্দের কলেজ", "চান্স পাব কীভাবে"],
        "context_keywords": ["পছন্দ", "choice", "college", "কলেজ"]
    },
    {
        "intent": "SUBJECT_CHANGE",
        "keywords": ["বিষয় পরিবর্তন", "সাবজেক্ট চেঞ্জ", "subject change", "auto migration", "অটো মাইগ্রেশন", "সাবজেক্ট মাইগ্রেশন"],
        "context_keywords": ["বিষয়", "subject", "পরিবর্তন", "change"]
    },
    {
        "intent": "ADMISSION_RESULT",
        "keywords": ["ভর্তি ফলাফল", "admission result", "ভর্তি রেজাল্ট", "athn", "ভর্তির রেজাল্ট দেখার নিয়ম"],
        "context_keywords": ["admission", "ভর্তি", "result", "ফলাফল"]
    },
    {
        "intent": "ADMISSION_APPLICATION",
        "keywords": ["ভর্তি আবেদন", "ভর্তির ওয়েবসাইট", "ভর্তি আবেদন করব কীভাবে", "ভর্তি পিন", "admission pin", "admission form download", "app11.nu.edu.bd"],
        "context_keywords": ["ভর্তি", "admission", "আবেদন", "apply"]
    },
    {
        "intent": "ADMISSION_GENERAL",
        "keywords": ["ভর্তি কবে", "ভর্তি শুরু", "ভর্তি শেষ", "admission start", "admission deadline", "ডিগ্রি ভর্তি", "মাস্টার্স ভর্তি", "প্রফেশনাল কোর্স", "প্রিলিমিনারি টু মাস্টার্স"],
        "context_keywords": ["ভর্তি", "admission"]
    },

    # --- Registration Family ---
    {
        "intent": "REGISTRATION_CARD",
        "keywords": ["রেজিস্ট্রেশন কার্ড", "registration card", "রেজিস্ট্রেশন কার্ড হারিয়ে", "নামের বানান ভুল", "বাবার নাম ভুল", "জন্মতারিখ ভুল", "ডুপ্লিকেট রেজিস্ট্রেশন কার্ড", "name correction", "father name correction", "dob correction"],
        "context_keywords": ["রেজিস্ট্রেশন কার্ড", "reg card", "correction"]
    },
    {
        "intent": "REGISTRATION",
        "keywords": ["রেজিস্ট্রেশন নম্বর", "registration number", "নতুন রেজিস্ট্রেশন", "re-registration", "রেজিস্ট্রেশন মেয়াদ"],
        "context_keywords": ["রেজিস্ট্রেশন", "registration"]
    },

    # --- Examination Family ---
    {
        "intent": "EXAM_ROUTINE",
        "keywords": ["রুটিন", "routine", "সময়সূচি", "schedule", "পরীক্ষা কবে", "পরীক্ষা স্থগিত", "সংশোধিত রুটিন", "revised routine", "postponed", "exam date"],
        "context_keywords": ["পরীক্ষা", "exam", "রুটিন", "routine"]
    },
    {
        "intent": "EXAM_CENTER",
        "keywords": ["পরীক্ষার কেন্দ্র", "পরীক্ষার সেন্টার", "exam center", "center list", "কেন্দ্র তালিকা", "আমার কেন্দ্র কোথায়"],
        "context_keywords": ["কেন্দ্র", "center", "venue"]
    },
    {
        "intent": "DUPLICATE_ADMIT_CARD",
        "keywords": ["প্রবেশপত্র হারিয়ে", "lost admit card", "ডুপ্লিকেট প্রবেশপত্র", "ডুপ্লিকেট এডমিট কার্ড", "duplicate admit card"],
        "context_keywords": ["হারিয়ে", "lost", "duplicate", "ডুপ্লিকেট"]
    },
    {
        "intent": "ADMIT_CARD",
        "keywords": ["প্রবেশপত্র", "admit card", "এডমিট কার্ড ডাউনলোড", "প্রবেশপত্রে ভুল", "admit card mistake"],
        "context_keywords": ["প্রবেশপত্র", "admit"]
    },
    {
        "intent": "EXAM_ABSENT",
        "keywords": ["অনুপস্থিত", "absent in exam", "পরীক্ষা না দিলে", "পরীক্ষায় অনুপস্থিত", "absent"],
        "context_keywords": ["অনুপস্থিত", "absent"]
    },
    {
        "intent": "EXAM_IMPROVEMENT",
        "keywords": ["মানোন্নয়ন", "improvement", "মানোন্নয়ন পরীক্ষা", "grade improvement", "মানোন্নয়ন নিয়ম"],
        "context_keywords": ["মানোন্নয়ন", "improvement"]
    },
    {
        "intent": "EXAM_FEE",
        "keywords": ["ফরম পূরণের ফি", "form fill up fee", "পরীক্ষার ফি কত", "ফরম ফিলাপের টাকা", "fee koto"],
        "context_keywords": ["ফরম", "form", "ফি", "fee"]
    },
    {
        "intent": "EXAM_FORM_FILLUP",
        "keywords": ["ফরম পূরণ", "ফরম ফিলাপ", "form fillup", "form fill up", "ফরম পূরণের তারিখ", "ফরম পূরণ ভুল", "ems.nu.ac.bd", "nubd.info"],
        "context_keywords": ["ফরম", "form", "fillup", "ফিলাপ"]
    },

    # --- Result Family ---
    {
        "intent": "RESULT_PUBLICATION",
        "keywords": ["রেজাল্ট কবে", "রেজাল্ট প্রকাশ", "result kobe", "result date", "when will result be published", "ফলাফল কবে দিবে"],
        "context_keywords": ["রেজাল্ট", "result", "কবে", "date", "প্রকাশ"]
    },
    {
        "intent": "RESULT_ERROR",
        "keywords": ["রেজাল্ট দেখাচ্ছে না", "withheld", "স্থগিত", "রেজাল্টে ভুল", "result not found", "result error", "মার্ক আসেনি"],
        "context_keywords": ["ভুল", "error", "withheld", "স্থগিত", "দেখাচ্ছে না"]
    },
    {
        "intent": "CGPA",
        "keywords": ["cgpa", "সিজিপিএ", "আমার cgpa কত", "consolidated result", "সম্মিলিত ফলাফল", "মোট সিজিপিএ"],
        "context_keywords": ["cgpa", "সিজিপিএ"]
    },
    {
        "intent": "GPA",
        "keywords": ["gpa", "জিপিএ", "গ্রেডিং সিস্টেম", "grading system", "৪.০০ স্কেল", "gpa হিসাব", "grading scale"],
        "context_keywords": ["gpa", "জিপিএ", "grading", "গ্রেডিং"]
    },
    {
        "intent": "FAIL_RESULT",
        "keywords": ["ফেল", "fail", "f গ্রেড", "f grade", "এক বিষয়ে ফেল", "f আসলে কি করব", "একটি বিষয়ে অকৃতকার্য"],
        "context_keywords": ["fail", "ফেল", "f grade", "f গ্রেড"]
    },
    {
        "intent": "REVALUATION",
        "keywords": ["পুনঃনিরীক্ষণ", "rescrutiny", "খাতা চ্যালেঞ্জ", "বোর্ড চ্যালেঞ্জ", "re-evaluation", "খাতা পুনর্নিরীক্ষণ", "rescrutiny deadline"],
        "context_keywords": ["পুনঃনিরীক্ষণ", "rescrutiny", "চ্যালেঞ্জ", "challenge"]
    },
    {
        "intent": "RESULT_CHECK",
        "keywords": ["রেজাল্ট দেখব কীভাবে", "check result", "results.nu.ac.bd", "ফলাফল দেখার নিয়ম", "sms রেজাল্ট", "16222", "রেজাল্ট ওয়েবসাইট"],
        "context_keywords": ["রেজাল্ট", "result", "ফলাফল"]
    },

    # --- Certificate / Marksheet / Transcript Family ---
    {
        "intent": "CERTIFICATE",
        "keywords": ["মূল সার্টিফিকেট", "original certificate", "সাময়িক সার্টিফিকেট", "provisional certificate", "সনদপত্র", "সার্টিফিকেট হারিয়ে", "duplicate certificate", "সার্টিফিকেট আবেদন"],
        "context_keywords": ["সার্টিফিকেট", "certificate", "সনদ"]
    },
    {
        "intent": "TRANSCRIPT",
        "keywords": ["ট্রান্সক্রিপ্ট", "transcript", "academic transcript", "wes", "wes verification", "বিদেশে উচ্চশিক্ষা"],
        "context_keywords": ["ট্রান্সক্রিপ্ট", "transcript", "wes"]
    },
    {
        "intent": "MARKSHEET",
        "keywords": ["মার্কশিট", "marksheet", "নম্বরপত্র", "অফিসিয়াল মার্কশিট", "marksheet সংগ্রহ"],
        "context_keywords": ["মার্কশিট", "marksheet", "নম্বরপত্র"]
    },
    {
        "intent": "MIGRATION",
        "keywords": ["মাইগ্রেশন সার্টিফিকেট", "migration certificate", "বিশ্ববিদ্যালয় মাইগ্রেশন"],
        "context_keywords": ["মাইগ্রেশন", "migration"]
    },

    # --- College Change / TC Family ---
    {
        "intent": "TC",
        "keywords": ["টিসি", "tc", "transfer certificate", "ছাড়পত্র", "কলেজ পরিবর্তন", "কলেজ ট্রান্সফার", "tc এর নিয়ম", "tc ডকুমেন্টস"],
        "context_keywords": ["tc", "টিসি", "ছাড়পত্র", "transfer"]
    },

    # --- Support / Notices / Contact Family ---
    {
        "intent": "SONALI_SEBA",
        "keywords": ["সোনালী সেবা", "sonali seba", "ই-পেমেন্ট", "sonali seva pay slip", "ব্যাংক ড্রাফট"],
        "context_keywords": ["সোনালী", "sonali", "সেবা", "seba", "পেমেন্ট"]
    },
    {
        "intent": "STUDENT_LOGIN",
        "keywords": ["স্টুডেন্ট লগইন", "student login", "ems লগইন", "applicant login", "প্রোফাইল দেখার নিয়ম"],
        "context_keywords": ["login", "লগইন", "profile"]
    },
    {
        "intent": "NOTICE",
        "keywords": ["নোটিশ", "notice", "সার্কুলার", "circular", "recent notices", "অফিসিয়াল নোটিশ"],
        "context_keywords": ["নোটিশ", "notice", "বিজ্ঞপ্তি"]
    },
    {
        "intent": "CONTACT",
        "keywords": ["যোগাযোগ", "contact", "ফোন নম্বর", "helpline", "ইমেইল", "email", "ঠিকানা", "গাজীপুর ক্যাম্পাস", "রেজিস্ট্রার দপ্তর ফোন"],
        "context_keywords": ["যোগাযোগ", "contact", "helpline", "phone", "email"]
    },
    {
        "intent": "GENERAL_SUPPORT",
        "keywords": ["অফিসিয়াল ওয়েবসাইট", "official website", "nu.ac.bd", "সহায়তা", "সমস্যার সমাধান", "ওয়ান-স্টপ সার্ভিস", "one-stop desk"],
        "context_keywords": ["সহায়তা", "help", "support", "website"]
    }
]

class IntentClassifier:
    @staticmethod
    def classify(message: str, session_context: Optional[Any] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Extracts intent, entities, and confidence score.
        """
        text = message.strip()
        text_lower = text.lower()
        entities: Dict[str, Any] = {
            "raw_query": text,
            "confidence": 1.0,
            "confidence_level": "HIGH"  # HIGH (90-100%), MEDIUM (70-89%), LOW (<70%)
        }

        # 1. Check for Token ID pattern (Priority 1)
        token_match = TOKEN_ID_PATTERN.search(text)
        if token_match:
            entities["token_id"] = token_match.group(1).upper()
            entities["confidence"] = 1.0
            entities["confidence_level"] = "HIGH"
            return "TOKEN_STATUS", entities

        # 2. Token confirmation / cancel / menu
        if text_lower in ["create token", "create support token", "টোকেন তৈরি করুন", "হ্যাঁ টোকেন তৈরি করুন", "yes create token", "confirm"]:
            return "TOKEN_CONFIRM_CREATE", entities

        if text_lower in ["cancel", "সমস্যা সমাধান পেয়েছি", "no cancel", "বাতিল", "সমাধান হয়েছে"]:
            return "TOKEN_CANCEL", entities

        if any(w in text_lower for w in ["token service", "support token", "টোকেন সেবা", "সাপোর্ট টোকেন", "টিকিট", "সমস্যার সমাধান চাই", "support ticket"]):
            return "TOKEN_SERVICE_MENU", entities

        # 3. Detect Service Code
        for code, keywords in SERVICE_KEYWORDS.items():
            if any(k in text_lower for k in keywords):
                entities["service_code"] = code
                break

        # 4. Check for Problem/Complaint submission
        if any(w in text_lower for w in ["লগইন হচ্ছে না", "ভুল দেখাচ্ছে", "সমস্যা সমাধান চাই", "cannot login", "failed to submit", "পেন্ডিং আছে"]):
            entities["confidence"] = 0.95
            entities["confidence_level"] = "HIGH"
            return "TOKEN_PROBLEM_SUBMISSION", entities

        # 5. Evaluate Granular Intents by keyword matching score
        best_intent = None
        best_score = 0

        for rule in INTENT_PATTERNS:
            score = 0
            # Direct keyword match
            for kw in rule["keywords"]:
                if kw in text_lower:
                    score += 2
            # Contextual keyword match
            for ckw in rule.get("context_keywords", []):
                if ckw in text_lower:
                    score += 1

            if score > best_score:
                best_score = score
                best_intent = rule["intent"]

        if best_intent and best_score >= 2:
            entities["confidence"] = min(1.0, 0.70 + (best_score * 0.1))
            entities["confidence_level"] = "HIGH" if entities["confidence"] >= 0.90 else "MEDIUM"
            return best_intent, entities

        # Fallback to broader category checks
        if any(w in text_lower for w in ["routine", "রুটিন", "exam schedule", "পরীক্ষার সময়সূচী", "পরীক্ষা কেন্দ্র", "admit card"]):
            entities["confidence"] = 0.85
            entities["confidence_level"] = "MEDIUM"
            return "EXAM_ROUTINE", entities

        if any(w in text_lower for w in ["admission", "ভর্তি", "মেধা তালিকা", "release slip", "রিলিজ স্লিপ"]):
            entities["confidence"] = 0.85
            entities["confidence_level"] = "MEDIUM"
            return "ADMISSION_GENERAL", entities

        if any(w in text_lower for w in ["cgpa", "gpa", "marksheet", "রেজাল্ট", "withheld", "স্থগিত"]):
            entities["confidence"] = 0.85
            entities["confidence_level"] = "MEDIUM"
            return "RESULT_CHECK", entities

        # Unidentified query (LOW confidence)
        entities["confidence"] = 0.50
        entities["confidence_level"] = "LOW"
        return "GENERAL_NU_QUERY", entities

_intent_classifier_instance: Optional[IntentClassifier] = None

def get_intent_classifier() -> IntentClassifier:
    global _intent_classifier_instance
    if _intent_classifier_instance is None:
        _intent_classifier_instance = IntentClassifier()
    return _intent_classifier_instance
