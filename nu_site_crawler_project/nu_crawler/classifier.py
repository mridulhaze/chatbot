import re

RULES = [
    ("notice", ["notice", "view-notice", "noticeinstruction", "circular", "বিজ্ঞপ্তি", "নোটিশ", "প্রজ্ঞাপন"]),
    ("examination", ["exam", "examination", "পরীক্ষা", "ফরম পূরণ", "form fill", "routine", "admit", "result", "ফলাফল"]),
    ("admission", ["admission", "ভর্তি", "admission-service"]),
    ("office_order", ["office-order", "office order", "অফিস আদেশ"]),
    ("press_release", ["press-release", "news", "সংবাদ", "শোকবার্তা"]),
    ("form_instruction", ["form", "instruction", "download-form", "নির্দেশিকা", "ফরম"]),
    ("regional_centre", ["আঞ্চলিক-কেন্দ্র", "আঞ্চলিক_কেন্দ্র", "regional", "চট্টগ্রাম", "রাজশাহী", "রংপুর", "খুলনা", "সিলেট", "বরিশাল"]),
    ("faculty_department", ["faculty", "department", "school", "বিভাগ", "অনুষদ"]),
    ("service", ["service", "online", "portal", "migration", "certificate", "transcript", "registration", "কলেজ"]),
    ("general_information", ["about", "at-a-glance", "history", "পরিচিতি", "তথ্য"]),
]

def classify(url, title, text):
    blob = (url + " " + title + " " + text[:12000]).lower()
    for page_type, keywords in RULES:
        for keyword in keywords:
            if keyword.lower() in blob:
                return page_type, keyword
    return "general", None

def extract_academic_metadata(text):
    result = {}
    for pattern in [r"\b(20\d{2}\s*[-–]\s*20\d{2})\b", r"\b(20\d{2}-\d{2})\b"]:
        m = re.search(pattern, text)
        if m:
            result["session"] = m.group(1)
            break
    years = list(dict.fromkeys(re.findall(r"\b(20\d{2})\b", text)))
    if years:
        result["years"] = years[:10]
    known = ["Honours", "Honors", "Degree", "Masters", "Master's", "Professional", "CSE", "ECE", "BBA", "MBA", "M.Ed", "MPhil", "PhD"]
    found = [x for x in known if x.lower() in text.lower()]
    if found:
        result["programs"] = found
    return result
