"""
National University Bangladesh AI Assistant — Officer & Department Aliases & Canonical Mapping
Contains canonical representations, synonyms, and variations across Bangla, English, and Banglish.
"""

from typing import Dict, List, Any, Optional

# --- All 33 Administrative Departments of National University ---
DEPARTMENT_ALIASES: List[Dict[str, Any]] = [
    # 1. Vice-Chancellor Division
    {
        "slug": "vc-office",
        "name_bn": "উপাচার্য দপ্তর",
        "name_en": "Vice-Chancellor Office",
        "parent": "উপাচার্য দপ্তর (Vice-Chancellor)",
        "url": "https://www.nu.ac.bd/vice-chancellor-office.php",
        "aliases": [
            "vc office", "vc", "vice chancellor", "vice chancellor office", "vice-chancellor",
            "উপাচার্য", "ভিসি", "উপাচার্য দপ্তর", "উপাচার্য অফিস", "ভিসি অফিস", "ভিসির দপ্তর",
            "vc er", "vc doptor", "vc te", "upacharjo", "vice chancelor"
        ]
    },
    {
        "slug": "registrar-office",
        "name_bn": "রেজিস্ট্রার দপ্তর",
        "name_en": "Registrar Office",
        "parent": "উপাচার্য দপ্তর (Vice-Chancellor)",
        "url": "https://www.nu.ac.bd/Registrar-office.php",
        "aliases": [
            "registrar", "registrar office", "registrar dept", "registrar department", "reg office",
            "রেজিস্ট্রার", "রেজিস্টার", "রেজিস্ট্রার দপ্তর", "রেজিস্টার দপ্তর", "রেজিস্ট্রার অফিস", "রেজিস্ট্রারের",
            "registar", "rejistrar", "registrar er", "registrar doptor", "registrar te"
        ]
    },
    {
        "slug": "planning-development",
        "name_bn": "পরিকল্পনা ও উন্নয়ন দপ্তর",
        "name_en": "Planning & Development",
        "parent": "উপাচার্য দপ্তর (Vice-Chancellor)",
        "url": "https://www.nu.ac.bd/planning-development.php",
        "aliases": [
            "planning and development", "planning", "development", "planning development", "p&d",
            "পরিকল্পনা ও উন্নয়ন", "পরিকল্পনা", "উন্নয়ন দপ্তর", "পরিকল্পনা দপ্তর",
            "planning er", "development doptor", "porikolpona"
        ]
    },
    {
        "slug": "public-relations",
        "name_bn": "জনসংযোগ, তথ্য ও পরামর্শ দপ্তর",
        "name_en": "Public Relations",
        "parent": "উপাচার্য দপ্তর (Vice-Chancellor)",
        "url": "https://www.nu.ac.bd/public-relations.php",
        "aliases": [
            "public relations", "pr", "pr office", "public relation", "press", "media",
            "জনসংযোগ", "জনসংযোগ দপ্তর", "জনসংযোগ অফিস", "তথ্য ও পরামর্শ", "পরামর্শ দপ্তর", "প্রেস",
            "jonosongjog", "pr doptor", "pr te"
        ]
    },
    {
        "slug": "international-desk",
        "name_bn": "আন্তর্জাতিক ডেস্ক দপ্তর",
        "name_en": "International Desk",
        "parent": "উপাচার্য দপ্তর (Vice-Chancellor)",
        "url": "https://www.nu.ac.bd/international-desk-department.php",
        "aliases": [
            "international desk", "international desk department", "international", "foreign desk",
            "আন্তর্জাতিক ডেস্ক", "আন্তর্জাতিক ডেস্ক দপ্তর", "আন্তর্জাতিক", "আন্তর্জাতিক শাখা",
            "international desk er", "antorjatik desk"
        ]
    },
    {
        "slug": "discipline-security",
        "name_bn": "শৃঙ্খলা ও নিরাপত্তা দপ্তর",
        "name_en": "Discipline & Security",
        "parent": "উপাচার্য দপ্তর (Vice-Chancellor)",
        "url": "https://www.nu.ac.bd/office-of-the-discipline-and-security.php",
        "aliases": [
            "discipline and security", "discipline & security", "security", "discipline", "security department",
            "শৃঙ্খলা ও নিরাপত্তা", "শৃঙ্খলা ও নিরাপত্তা দপ্তর", "নিরাপত্তা দপ্তর", "শৃঙ্খলা দপ্তর", "সিকিউরিটি",
            "security doptor", "srinkhola", "nirapotta"
        ]
    },
    {
        "slug": "engineering",
        "name_bn": "প্রকৌশল দপ্তর",
        "name_en": "Engineering Department",
        "parent": "উপাচার্য দপ্তর (Vice-Chancellor)",
        "url": "https://www.nu.ac.bd/engineering-department-office.php",
        "aliases": [
            "engineering department", "engineering", "engineer office", "works department",
            "প্রকৌশল দপ্তর", "প্রকৌশল", "ইঞ্জিনিয়ারিং", "ইঞ্জিনিয়ারিং দপ্তর", "পূর্ত শাখা",
            "prokoushol", "engineering doptor", "engineer te"
        ]
    },
    {
        "slug": "college-monitoring",
        "name_bn": "কলেজ মনিটরিং ও মূল্যায়ন দপ্তর",
        "name_en": "College Monitoring & Evaluation",
        "parent": "উপাচার্য দপ্তর (Vice-Chancellor)",
        "url": "https://www.nu.ac.bd/College-Monitoring-and-Evaluation-Department.php",
        "aliases": [
            "college monitoring and evaluation", "college monitoring", "monitoring & evaluation", "evaluation",
            "কলেজ মনিটরিং ও মূল্যায়ন", "কলেজ মনিটরিং", "মূল্যায়ন দপ্তর", "মনিটরিং দপ্তর",
            "college monitoring er", "monitoring doptor"
        ]
    },
    {
        "slug": "law-affairs",
        "name_bn": "আইন বিষয়ক দপ্তর",
        "name_en": "Law Affairs",
        "parent": "উপাচার্য দপ্তর (Vice-Chancellor)",
        "url": "https://www.nu.ac.bd/Law_Department.php",
        "aliases": [
            "law affairs", "law", "legal department", "legal affairs", "law department",
            "আইন বিষয়ক দপ্তর", "আইন দপ্তর", "আইন শাখা", "লিগ্যাল শাখা", "আইনি পরামর্শ",
            "ain bishoyok", "law doptor", "legal te"
        ]
    },

    # 2. Pro-Vice-Chancellor 1 Division
    {
        "slug": "pro-vc-office",
        "name_bn": "উপ-উপাচার্য দপ্তর",
        "name_en": "Pro-Vice-Chancellor Office",
        "parent": "উপ-উপাচার্য দপ্তর ১ (Pro-Vice-Chancellor 1)",
        "url": "https://www.nu.ac.bd/Pro-Vice-Chancellor-Office.php",
        "aliases": [
            "pro vc", "pro-vc", "pro vice chancellor", "pro-vice-chancellor", "pro vc 1", "pro vc 2",
            "উপ-উপাচার্য", "উপ উপাচার্য", "প্রো-ভিসি", "প্রোভিসি", "উপ-উপাচার্য দপ্তর", "প্রো-ভিসি অফিস",
            "pro vc doptor", "provc"
        ]
    },
    {
        "slug": "exam-controller",
        "name_bn": "পরীক্ষা নিয়ন্ত্রক দপ্তর",
        "name_en": "Controller of Examination Office",
        "parent": "উপ-উপাচার্য দপ্তর ১ (Pro-Vice-Chancellor 1)",
        "url": "https://www.nu.ac.bd/exam-controller-office.php",
        "aliases": [
            "controller of examination department", "controller of examination", "exam controller department", "exam controller", "controller office", "coe", "exam department", "examination controller",
            "পরীক্ষা নিয়ন্ত্রক", "পরীক্ষা নিয়ন্ত্রক", "পরীক্ষা নিয়ন্ত্রক দপ্তর", "পরীক্ষা নিয়ন্ত্রক দপ্তর", "পরীক্ষা দপ্তর", "পরীক্ষা অফিস",
            "porikkha niyontrok doptor", "porikkha niyontrok", "poriksha niyontrok", "exam controller er", "coe doptor", "exam controller doptor"
        ]
    },
    {
        "slug": "inspector-of-college",
        "name_bn": "কলেজ পরিদর্শন দপ্তর",
        "name_en": "College Inspection Department",
        "parent": "উপ-উপাচার্য দপ্তর ১ (Pro-Vice-Chancellor 1)",
        "url": "https://www.nu.ac.bd/inspector-of-college.php",
        "aliases": [
            "college inspection", "inspector of college", "college inspector", "college inspection department",
            "কলেজ পরিদর্শন", "কলেজ পরিদর্শন দপ্তর", "কলেজ পরিদর্শক", "কলেজ পরিদর্শক দপ্তর",
            "college poridoroshon", "inspector of college er"
        ]
    },
    {
        "slug": "internal-audit",
        "name_bn": "অভ্যন্তরীণ নিরীক্ষা দপ্তর",
        "name_en": "Internal Audit",
        "parent": "উপ-উপাচার্য দপ্তর ১ (Pro-Vice-Chancellor 1)",
        "url": "https://www.nu.ac.bd/internal-audit-office.php",
        "aliases": [
            "internal audit", "audit", "audit department", "audit office",
            "অভ্যন্তরীণ নিরীক্ষা", "অভ্যন্তরীণ নিরীক্ষা দপ্তর", "নিরীক্ষা দপ্তর", "অডিট দপ্তর", "অডিট শাখা",
            "obhontorin nirikkha", "audit doptor"
        ]
    },
    {
        "slug": "publication-marketing",
        "name_bn": "প্রকাশনা ও বিপণন দপ্তর",
        "name_en": "Publication & Marketing",
        "parent": "উপ-উপাচার্য দপ্তর ১ (Pro-Vice-Chancellor 1)",
        "url": "https://www.nu.ac.bd/publication-section.php",
        "aliases": [
            "publication and marketing", "publication", "marketing", "publication marketing", "publication section",
            "প্রকাশনা ও বিপণন", "প্রকাশনা ও বিপণন দপ্তর", "প্রকাশনা দপ্তর", "বিপণন দপ্তর", "প্রকাশনা শাখা",
            "prokashona", "publication doptor"
        ]
    },
    {
        "slug": "physical-education",
        "name_bn": "শারীরিক শিক্ষা দপ্তর",
        "name_en": "Physical Education & Cultural Affairs",
        "parent": "উপ-উপাচার্য দপ্তর ১ (Pro-Vice-Chancellor 1)",
        "url": "https://www.nu.ac.bd/physical-education.php",
        "aliases": [
            "physical education", "physical education and cultural affairs", "sports", "cultural affairs", "games and sports",
            "শারীরিক শিক্ষা", "শারীরিক শিক্ষা দপ্তর", "শারীরিক শিক্ষা ও সাংস্কৃতিক দপ্তর", "খেলাধুলা দপ্তর", "ক্রীড়া শাখা", "সংস্কৃতি শাখা",
            "sharirik shikkha", "sports doptor"
        ]
    },
    {
        "slug": "estate",
        "name_bn": "এস্টেট দপ্তর",
        "name_en": "Estate Department",
        "parent": "উপ-উপাচার্য দপ্তর ১ (Pro-Vice-Chancellor 1)",
        "url": "https://www.nu.ac.bd/Estate_Department.php",
        "aliases": [
            "estate department", "estate", "estate office",
            "এস্টেট দপ্তর", "এস্টেট", "এস্টেট শাখা", "সম্পত্তি দপ্তর",
            "estate doptor", "estate er"
        ]
    },
    {
        "slug": "hr-development",
        "name_bn": "মানবসম্পদ উন্নয়ন ও শুদ্ধাচার দপ্তর",
        "name_en": "HR Development & Integrity",
        "parent": "উপ-উপাচার্য দপ্তর ১ (Pro-Vice-Chancellor 1)",
        "url": "https://www.nu.ac.bd/Human-Resource-Development-and-Integrity.php",
        "aliases": [
            "hr development", "human resource development", "integrity", "hr", "human resource",
            "মানবসম্পদ উন্নয়ন", "মানবসম্পদ দপ্তর", "মানবসম্পদ ও শুদ্ধাচার", "শুদ্ধাচার দপ্তর", "এইচআর",
            "hr doptor", "manob sompod"
        ]
    },

    # 3. Pro-Vice-Chancellor 2 Division
    {
        "slug": "ict-department",
        "name_bn": "আইসিটি দপ্তর",
        "name_en": "ICT Department",
        "parent": "উপ-উপাচার্য দপ্তর ২ (Pro-Vice-Chancellor 2)",
        "url": "https://www.nu.ac.bd/ict-department.php",
        "aliases": [
            "ict", "ict department", "ict dept", "ict office", "computer cell", "it department", "it dept",
            "আইসিটি", "আইসিটি দপ্তর", "আইসিটি অফিস", "কম্পিউটার দপ্তর", "আইসিটি বিভাগ", "আইটি দপ্তর",
            "ict te", "ict er", "ict doptor", "aicsiti", "ict department er"
        ]
    },
    {
        "slug": "transport-department",
        "name_bn": "পরিবহন শাখা",
        "name_en": "Transport Section",
        "parent": "উপ-উপাচার্য দপ্তর ২ (Pro-Vice-Chancellor 2)",
        "url": "https://www.nu.ac.bd/transport-department.php",
        "aliases": [
            "transport section", "transport department", "transport", "vehicle department", "bus section",
            "পরিবহন শাখা", "পরিবহন দপ্তর", "পরিবহন", "যানবাহন শাখা", "বাস শাখা",
            "poribohon", "transport doptor", "transport er"
        ]
    },
    {
        "slug": "medical-centre",
        "name_bn": "চিকিৎসা কেন্দ্র",
        "name_en": "Medical Centre",
        "parent": "উপ-উপাচার্য দপ্তর ২ (Pro-Vice-Chancellor 2)",
        "url": "https://www.nu.ac.bd/medical-services-department.php",
        "aliases": [
            "medical centre", "medical center", "medical services", "medical", "hospital", "health centre",
            "চিকিৎসা কেন্দ্র", "চিকিৎসা দপ্তর", "চিকিৎসা শাখা", "মেডিকেল সেন্টার", "মেডিকেল", "হাসপাতাল",
            "chikitsa kendro", "medical te", "medical doptor"
        ]
    },
    {
        "slug": "regional-center-coord",
        "name_bn": "আঞ্চলিক কেন্দ্র সমন্বয় দপ্তর",
        "name_en": "Regional Center Coordination",
        "parent": "উপ-উপাচার্য দপ্তর ২ (Pro-Vice-Chancellor 2)",
        "url": "https://www.nu.ac.bd/Regional-Center-Co-ordination.php",
        "aliases": [
            "regional center coordination", "regional center", "regional coordination", "regional centres",
            "আঞ্চলিক কেন্দ্র সমন্বয়", "আঞ্চলিক কেন্দ্র সমন্বয় দপ্তর", "আঞ্চলিক কেন্দ্র", "আঞ্চলিক দপ্তর",
            "ancholik kendro", "regional center er"
        ]
    },
    {
        "slug": "information-services",
        "name_bn": "তথ্য ও সেবা দপ্তর",
        "name_en": "Information & Services",
        "parent": "উপ-উপাচার্য দপ্তর ২ (Pro-Vice-Chancellor 2)",
        "url": "https://www.nu.ac.bd/Information-and-services-department.php",
        "aliases": [
            "information and services", "information services", "helpdesk department", "info and services",
            "তথ্য ও সেবা", "তথ্য ও সেবা দপ্তর", "তথ্য সেবা দপ্তর", "হেল্পডেস্ক দপ্তর",
            "tothyo o seba", "information doptor"
        ]
    },
    {
        "slug": "procurement",
        "name_bn": "ক্রয় দপ্তর",
        "name_en": "Procurement Department",
        "parent": "উপ-উপাচার্য দপ্তর ২ (Pro-Vice-Chancellor 2)",
        "url": "https://www.nu.ac.bd/Procurement_and_Store_Department.php",
        "aliases": [
            "procurement department", "procurement", "purchase department", "purchase",
            "ক্রয় দপ্তর", "ক্রয় শাখা", "ক্রয় দপ্তর", "কেনাকাটা শাখা",
            "kroy doptor", "procurement er"
        ]
    },
    {
        "slug": "central-store",
        "name_bn": "কেন্দ্রীয় ভাণ্ডার দপ্তর",
        "name_en": "Central Store",
        "parent": "উপ-উপাচার্য দপ্তর ২ (Pro-Vice-Chancellor 2)",
        "url": "https://www.nu.ac.bd/department-of-central-store.php",
        "aliases": [
            "central store", "store department", "central store department", "warehouse",
            "কেন্দ্রীয় ভাণ্ডার", "কেন্দ্রীয় ভাণ্ডার দপ্তর", "কেন্দ্রীয় স্টোর", "স্টোর দপ্তর", "ভাণ্ডার শাখা",
            "kendriyo bhandar", "store doptor"
        ]
    },

    # 4. Treasurer Division
    {
        "slug": "treasurer-office",
        "name_bn": "ট্রেজারার দপ্তর",
        "name_en": "Treasurer Office",
        "parent": "কোষাধ্যক্ষ দপ্তর (Treasurer)",
        "url": "https://www.nu.ac.bd/Treasurer-office.php",
        "aliases": [
            "treasurer office", "treasurer", "treasury",
            "ট্রেজারার দপ্তর", "ট্রেজারার", "কোষাধ্যক্ষ দপ্তর", "কোষাধ্যক্ষ",
            "treasurer doptor", "koshaddhokkho"
        ]
    },
    {
        "slug": "online-education",
        "name_bn": "অনলাইন শিক্ষা দপ্তর",
        "name_en": "Online Education",
        "parent": "কোষাধ্যক্ষ দপ্তর (Treasurer)",
        "url": "https://www.nu.ac.bd/Online_Education_Department.php",
        "aliases": [
            "online education department", "online education", "e-learning", "elearning",
            "অনলাইন শিক্ষা দপ্তর", "অনলাইন শিক্ষা", "ই-লার্নিং দপ্তর", "দূরশিক্ষণ শাখা",
            "online education doptor", "online shikkha"
        ]
    },
    {
        "slug": "library-department",
        "name_bn": "গ্রন্থাগার দপ্তর",
        "name_en": "Library Department",
        "parent": "কোষাধ্যক্ষ দপ্তর (Treasurer)",
        "url": "https://www.nu.ac.bd/library-department.php",
        "aliases": [
            "library department", "library", "central library", "nu library",
            "গ্রন্থাগার দপ্তর", "গ্রন্থাগার", "লাইব্রেরি", "লাইব্রেরি দপ্তর", "কেন্দ্রীয় গ্রন্থাগার",
            "gronthagar", "library doptor", "library te"
        ]
    },
    {
        "slug": "finance-accounts",
        "name_bn": "অর্থ ও হিসাব দপ্তর",
        "name_en": "Finance & Accounts",
        "parent": "কোষাধ্যক্ষ দপ্তর (Treasurer)",
        "url": "https://www.nu.ac.bd/finance-account.php",
        "aliases": [
            "finance and accounts", "finance & accounts", "finance", "accounts", "f&a", "accounts department",
            "অর্থ ও হিসাব", "অর্থ ও হিসাব দপ্তর", "অর্থ দপ্তর", "হিসাব দপ্তর", "হিসাব শাখা", "অ্যাকাউন্টস",
            "ortho o hishab", "finance doptor", "accounts te"
        ]
    },
    {
        "slug": "teachers-training",
        "name_bn": "শিক্ষক প্রশিক্ষণ দপ্তর",
        "name_en": "Teachers Training Department",
        "parent": "কোষাধ্যক্ষ দপ্তর (Treasurer)",
        "url": "https://www.nu.ac.bd/teachers-training-information.php",
        "aliases": [
            "teachers training department", "teachers training", "teacher training", "ttis",
            "শিক্ষক প্রশিক্ষণ দপ্তর", "শিক্ষক প্রশিক্ষণ", "শিক্ষক ট্রেনিং শাখা",
            "shikkhok proshikkhon", "teachers training doptor"
        ]
    },
    {
        "slug": "admission-registration",
        "name_bn": "ভর্তি ও রেজিস্ট্রেশন সেল",
        "name_en": "Admission & Registration Cell",
        "parent": "কোষাধ্যক্ষ দপ্তর (Treasurer)",
        "url": "https://www.nu.ac.bd/admission-and-registration-cell.php",
        "aliases": [
            "admission and registration cell", "admission & registration", "admission cell", "registration cell", "admission department",
            "ভর্তি ও রেজিস্ট্রেশন সেল", "ভর্তি ও রেজিস্ট্রেশন", "ভর্তি সেল", "রেজিস্ট্রেশন সেল", "ভর্তি শাখা",
            "bhorti o registration", "admission cell er"
        ]
    },
    {
        "slug": "ilbs",
        "name_bn": "মুক্তিযুদ্ধ ও বাংলাদেশ গবেষণা ইনস্টিটিউট (ILBS)",
        "name_en": "Institute of Liberation War and Bangladesh Studies (ILBS)",
        "parent": "কোষাধ্যক্ষ দপ্তর (Treasurer)",
        "url": "https://www.nu.ac.bd/ILBS.php",
        "aliases": [
            "ilbs", "institute of liberation war", "liberation war institute", "bangladesh studies",
            "মুক্তিযুদ্ধ ও বাংলাদেশ গবেষণা ইনস্টিটিউট", "মুক্তিযুদ্ধ ইনস্টিটিউট", "আইএলবিএস", "গবেষণা ইনস্টিটিউট",
            "ilbs doptor"
        ]
    },
    {
        "slug": "iqac",
        "name_bn": "প্রাতিষ্ঠানিক মান নিশ্চিতকরণ সেল (IQAC)",
        "name_en": "Institutional Quality Assurance Cell (IQAC)",
        "parent": "কোষাধ্যক্ষ দপ্তর (Treasurer)",
        "url": "https://www.nu.ac.bd/IQAC.php",
        "aliases": [
            "iqac", "institutional quality assurance cell", "quality assurance", "quality cell",
            "প্রাতিষ্ঠানিক মান নিশ্চিতকরণ সেল", "আইকিউএসি", "মান নিশ্চিতকরণ সেল", "আই কিউ এ সি",
            "iqac cell"
        ]
    },
    {
        "slug": "ifscs",
        "name_bn": "ফরেনসিক সায়েন্স ও সাইবার সিকিউরিটি ইনস্টিটিউট (IFSCS)",
        "name_en": "Institute of Forensic Science and Cyber Security (IFSCS)",
        "parent": "কোষাধ্যক্ষ দপ্তর (Treasurer)",
        "url": "https://www.nu.ac.bd/IFSCS.php",
        "aliases": [
            "ifscs", "institute of forensic science", "cyber security institute", "forensic science", "cyber security",
            "ফরেনসিক সায়েন্স ও সাইবার সিকিউরিটি ইনস্টিটিউট", "ফরেনসিক ইনস্টিটিউট", "সাইবার সিকিউরিটি ইনস্টিটিউট", "আইএফএসসিএস",
            "ifscs institute"
        ]
    }
]


# --- Canonical Designation Aliases Mapping ---
DESIGNATION_ALIASES: List[Dict[str, Any]] = [
    {
        "canonical_en": "Assistant Programmer",
        "canonical_bn": "সহকারী প্রোগ্রামার",
        "aliases": [
            "assistant programmer", "assistant programmers", "ap", "asst programmer", "asst. programmer", "assistant programer", "assistent programmer",
            "সহকারী প্রোগ্রামার", "সহকারি প্রোগ্রামার", "সহকারী প্রোগ্রামারদের", "সহকারী প্রোগ্রামারগণ", "সহকারী প্রোগ্রামাররা",
            "shohokari programmer", "sohokari programmer", "assistant programer", "asst programmer"
        ]
    },
    {
        "canonical_en": "Senior Programmer",
        "canonical_bn": "সিনিয়র প্রোগ্রামার",
        "aliases": [
            "senior programmer", "senior programmers", "sp", "sr programmer", "sr. programmer", "senior programer",
            "সিনিয়র প্রোগ্রামার", "সিনিয়র প্রোগ্রামার", "সিনিয়র প্রোগ্রামারদের", "সিনিয়র প্রোগ্রামারগণ",
            "sinior programmer", "seenior programmer", "sr programmer"
        ]
    },
    {
        "canonical_en": "Programmer",
        "canonical_bn": "প্রোগ্রামার",
        "aliases": [
            "programmer", "programmers", "software engineer", "coder", "programer", "programmmer",
            "প্রোগ্রামার", "প্রোগ্রামারদের", "প্রোগ্রামারগণ", "প্রোগ্রামাররা",
            "programmer ra", "programmerder"
        ]
    },
    {
        "canonical_en": "System Analyst",
        "canonical_bn": "সিস্টেম এনালিস্ট",
        "aliases": [
            "system analyst", "systems analyst", "system analysts", "systems analyst", "sa",
            "সিস্টেম এনালিস্ট", "সিস্টেম অ্যানালিস্ট", "সিস্টেম এ্যানালিস্ট", "সিস্টেম এনালিস্টদের",
            "system analyst", "system analist"
        ]
    },
    {
        "canonical_en": "Network Administrator",
        "canonical_bn": "নেটওয়ার্ক এডমিনিস্ট্রেটর",
        "aliases": [
            "network administrator", "network admin", "network administrators", "net admin",
            "নেটওয়ার্ক এডমিনিস্ট্রেটর", "নেটওয়ার্ক অ্যাডমিনিস্ট্রেটর", "নেটওয়ার্ক এ্যাডমিনিস্ট্রেটর", "নেটওয়ার্ক এডমিন",
            "network admin", "network administrator"
        ]
    },
    {
        "canonical_en": "Maintenance Engineer",
        "canonical_bn": "মেইনটেন্যান্স ইঞ্জিনিয়ার",
        "aliases": [
            "maintenance engineer", "maintenance engineers", "hardware engineer",
            "মেইনটেন্যান্স ইঞ্জিনিয়ার", "মেইনটেন্যান্স ইঞ্জিনিয়ার", "মেইনটেন্যান্স ইঞ্জিঃ", "রক্ষণাবেক্ষণ প্রকৌশলী",
            "maintenance engineer"
        ]
    },
    {
        "canonical_en": "Director",
        "canonical_bn": "পরিচালক",
        "aliases": [
            "director", "directors", "head", "department head", "director (acting)",
            "পরিচালক", "পরিচালক (ভারপ্রাপ্ত)", "পরিচালকের", "পরিচালকগণ", "বিভাগীয় প্রধান",
            "porichalok", "director"
        ]
    },
    {
        "canonical_en": "Deputy Director",
        "canonical_bn": "উপ-পরিচালক",
        "aliases": [
            "deputy director", "deputy directors", "dd", "deputy director (acting)",
            "উপ-পরিচালক", "উপপরিচালক", "উপ পরিচালক", "উপ-পরিচালকগণ",
            "upo porichalok", "deputy director"
        ]
    },
    {
        "canonical_en": "Assistant Director",
        "canonical_bn": "সহকারী পরিচালক",
        "aliases": [
            "assistant director", "assistant directors", "ad", "asst director", "asst. director",
            "সহকারী পরিচালক", "সহকারি পরিচালক", "সহকারী পরিচালকদের", "সহকারী পরিচালকগণ",
            "shohokari porichalok", "sohokari porichalok", "asst director"
        ]
    },
    {
        "canonical_en": "Additional Director",
        "canonical_bn": "অতিরিক্ত পরিচালক",
        "aliases": [
            "additional director", "addl director", "addl. director",
            "অতিরিক্ত পরিচালক", "অতিরিক্ত পরিচালকদের",
            "otirikto porichalok"
        ]
    },
    {
        "canonical_en": "Registrar",
        "canonical_bn": "রেজিস্ট্রার",
        "aliases": [
            "registrar", "registrars", "reg", "chief registrar",
            "রেজিস্ট্রার", "রেজিস্টার", "রেজিস্ট্রারদের", "রেজিস্টারদের", "রেজিস্ট্রারের",
            "registar", "rejistrar"
        ]
    },
    {
        "canonical_en": "Deputy Registrar",
        "canonical_bn": "উপ-রেজিস্ট্রার",
        "aliases": [
            "deputy registrar", "deputy registrars", "dr", "deputy registar",
            "উপ-রেজিস্ট্রার", "উপরেজিস্ট্রার", "উপ রেজিস্ট্রার", "উপ-রেজিস্টার",
            "upo registrar", "upo registar"
        ]
    },
    {
        "canonical_en": "Assistant Registrar",
        "canonical_bn": "সহকারী রেজিস্ট্রার",
        "aliases": [
            "assistant registrar", "assistant registrars", "asst registrar", "assistant register", "assistant registar",
            "সহকারী রেজিস্ট্রার", "সহকারি রেজিস্ট্রার", "সহকারী রেজিস্টার", "সহকারি রেজিস্টার",
            "shohokari registrar", "sohokari registar"
        ]
    },
    {
        "canonical_en": "Additional Registrar",
        "canonical_bn": "অতিরিক্ত রেজিস্ট্রার",
        "aliases": [
            "additional registrar", "addl registrar",
            "অতিরিক্ত রেজিস্ট্রার", "অতিরিক্ত রেজিস্টার",
            "otirikto registrar"
        ]
    },
    {
        "canonical_en": "Controller of Examinations",
        "canonical_bn": "পরীক্ষা নিয়ন্ত্রক",
        "aliases": [
            "controller of examinations", "controller of examination", "exam controller", "coe",
            "পরীক্ষা নিয়ন্ত্রক", "পরীক্ষা নিয়ন্ত্রক", "পরীক্ষা নিয়ন্ত্রকের", "প্রধান পরীক্ষা নিয়ন্ত্রক",
            "porikkha niyontrok", "exam controller"
        ]
    },
    {
        "canonical_en": "Deputy Controller of Examinations",
        "canonical_bn": "উপ-পরীক্ষা নিয়ন্ত্রক",
        "aliases": [
            "deputy controller of examinations", "deputy exam controller", "deputy controller", "deputy coe",
            "উপ-পরীক্ষা নিয়ন্ত্রক", "উপ-পরীক্ষা নিয়ন্ত্রক", "উপ পরীক্ষা নিয়ন্ত্রক", "উপ পরীক্ষা নিয়ন্ত্রক",
            "upo porikkha niyontrok", "deputy exam controller"
        ]
    },
    {
        "canonical_en": "Assistant Controller of Examinations",
        "canonical_bn": "সহকারী পরীক্ষা নিয়ন্ত্রক",
        "aliases": [
            "assistant controller of examinations", "assistant exam controller", "assistant controller", "asst coe",
            "সহকারী পরীক্ষা নিয়ন্ত্রক", "সহকারী পরীক্ষা নিয়ন্ত্রক", "সহকারি পরীক্ষা নিয়ন্ত্রক", "সহকারী পরীক্ষা নিয়ন্ত্রকদের",
            "shohokari porikkha niyontrok", "asst exam controller"
        ]
    },
    {
        "canonical_en": "Inspector of Colleges",
        "canonical_bn": "কলেজ পরিদর্শক",
        "aliases": [
            "inspector of colleges", "college inspector", "chief inspector",
            "কলেজ পরিদর্শক", "কলেজ পরিদর্শকের", "কলেজ পরিদর্শকগণ",
            "college poridoroshok"
        ]
    },
    {
        "canonical_en": "Deputy Inspector of Colleges",
        "canonical_bn": "উপ-কলেজ পরিদর্শক",
        "aliases": [
            "deputy inspector of colleges", "deputy college inspector",
            "উপ-কলেজ পরিদর্শক", "উপ কলেজ পরিদর্শক",
            "upo college poridoroshok"
        ]
    },
    {
        "canonical_en": "Section Officer",
        "canonical_bn": "সেকশন অফিসার",
        "aliases": [
            "section officer", "section officers", "so", "sec officer",
            "সেকশন অফিসার", "সেকশন অফিসারদের", "শাখা কর্মকর্তা",
            "section officer"
        ]
    },
    {
        "canonical_en": "Administrative Officer",
        "canonical_bn": "প্রশাসনিক কর্মকর্তা",
        "aliases": [
            "administrative officer", "administrative officers", "admin officer", "ao",
            "প্রশাসনিক কর্মকর্তা", "প্রশাসনিক কর্মকর্তাদের", "প্রশাসনিক অফিসার",
            "prosashonik kormokorta", "admin officer"
        ]
    },
    {
        "canonical_en": "Law Officer",
        "canonical_bn": "আইন কর্মকর্তা",
        "aliases": [
            "law officer", "legal officer", "lawyer", "advocate",
            "আইন কর্মকর্তা", "লিগ্যাল অফিসার", "আইন উপদেষ্টা",
            "ain kormokorta", "legal officer"
        ]
    },
    {
        "canonical_en": "Medical Officer",
        "canonical_bn": "মেডিকেল অফিসার",
        "aliases": [
            "medical officer", "doctor", "physician", "health officer",
            "মেডিকেল অফিসার", "চিকিৎসক", "ডাক্তার", "স্বাস্থ্য কর্মকর্তা",
            "doctor", "medical officer"
        ]
    },
    {
        "canonical_en": "Librarian",
        "canonical_bn": "গ্রন্থাগারিক",
        "aliases": [
            "librarian", "chief librarian", "library officer",
            "গ্রন্থাগারিক", "লাইব্রেরিয়ান", "গ্রন্থাগার কর্মকর্তা",
            "gronthagarik", "librarian"
        ]
    },
    {
        "canonical_en": "Chief Engineer",
        "canonical_bn": "প্রধান প্রকৌশলী",
        "aliases": [
            "chief engineer", "head engineer",
            "প্রধান প্রকৌশলী", "চিফ ইঞ্জিনিয়ার",
            "prodhan prokousholi"
        ]
    },
    {
        "canonical_en": "Executive Engineer",
        "canonical_bn": "নির্বাহী প্রকৌশলী",
        "aliases": [
            "executive engineer", "xen",
            "নির্বাহী প্রকৌশলী", "নির্বাহী ইঞ্জিনিয়ার",
            "nirbahi prokousholi"
        ]
    },
    {
        "canonical_en": "Assistant Engineer",
        "canonical_bn": "সহকারী প্রকৌশলী",
        "aliases": [
            "assistant engineer", "assistant engineers", "asst engineer", "ae",
            "সহকারী প্রকৌশলী", "সহকারি প্রকৌশলী", "সহকারী ইঞ্জিনিয়ার",
            "shohokari prokousholi"
        ]
    },
    {
        "canonical_en": "Upper Division Assistant",
        "canonical_bn": "উচ্চমান সহকারী",
        "aliases": [
            "upper division assistant", "uda", "upper divisional assistant", "upper division",
            "উচ্চমান সহকারী", "উচ্চ মান সহকারী",
            "ucchoman shohokari"
        ]
    },
    {
        "canonical_en": "Lower Division Assistant",
        "canonical_bn": "নিম্নমান সহকারী",
        "aliases": [
            "lower division assistant", "lda", "lower divisional assistant", "lower division",
            "নিম্নমান সহকারী", "নিম্মমান সহকারী", "নিম্ন মান সহকারী",
            "nimnoman shohokari"
        ]
    },
    {
        "canonical_en": "Office Assistant",
        "canonical_bn": "অফিস সহকারী",
        "aliases": [
            "office assistant", "office assistant cum computer typist", "clerk", "typist",
            "অফিস সহকারী", "অফিস সহকারী কাম কম্পিউটার মুদ্রাক্ষরিক", "অফিস সহ. কাম কম্পিঃ মুদ্রাক্ষরিক", "মুদ্রাক্ষরিক",
            "office shohokari"
        ]
    },
    {
        "canonical_en": "Office Support Staff",
        "canonical_bn": "অফিস সহায়ক",
        "aliases": [
            "office support staff", "office sohayok", "support staff", "mlss", "peon", "porter",
            "অফিস সহায়ক", "অফিস সহায়ক", "অফিস সহয়ক", "পিয়ন", "সহায়ক", "পোর্টার",
            "office sohayok"
        ]
    },
    {
        "canonical_en": "Data Entry Operator",
        "canonical_bn": "ডাটা এন্ট্রি অপারেটর",
        "aliases": [
            "data entry operator", "data entry", "deo", "computer operator",
            "ডাটা এন্ট্রি অপারেটর", "ডাটা-এন্ট্রি অপারেটর", "ডাটা এন্ট্রি",
            "data entry operator"
        ]
    },
    {
        "canonical_en": "Driver",
        "canonical_bn": "ড্রাইভার",
        "aliases": [
            "driver", "drivers", "chauffeur",
            "ড্রাইভার", "চালক", "গাড়ি চালক",
            "driver"
        ]
    },
    {
        "canonical_en": "Security Guard",
        "canonical_bn": "সিকিউরিটি গার্ড",
        "aliases": [
            "security guard", "guard", "security staff", "watchman",
            "সিকিউরিটি গার্ড", "নিরাপত্তা প্রহরী", "গার্ড",
            "security guard", "guard"
        ]
    },
    {
        "canonical_en": "Technical Officer",
        "canonical_bn": "টেকনিক্যাল অফিসার",
        "aliases": [
            "technical officer", "to",
            "টেকনিক্যাল অফিসার", "কারিগরি কর্মকর্তা",
            "technical officer"
        ]
    },
    {
        "canonical_en": "Sub-Technical Officer",
        "canonical_bn": "সাব-টেকনিক্যাল অফিসার",
        "aliases": [
            "sub-technical officer", "sub technical officer", "sto",
            "সাব-টেকনিক্যাল অফিসার", "সাব টেকনিক্যাল অফিসার",
            "sub technical officer"
        ]
    },
    {
        "canonical_en": "Vice-Chancellor",
        "canonical_bn": "উপাচার্য",
        "aliases": [
            "vice-chancellor", "vice chancellor", "vc",
            "উপাচার্য", "ভিসি", "উপাচার্যের",
            "upacharjo", "vc"
        ]
    },
    {
        "canonical_en": "Pro-Vice-Chancellor",
        "canonical_bn": "উপ-উপাচার্য",
        "aliases": [
            "pro-vice-chancellor", "pro vice chancellor", "pro-vc", "pro vc",
            "উপ-উপাচার্য", "উপ উপাচার্য", "প্রো-ভিসি", "প্রোভিসি",
            "pro-vc", "provc"
        ]
    },
    {
        "canonical_en": "Treasurer",
        "canonical_bn": "ট্রেজারার",
        "aliases": [
            "treasurer", "treasury head",
            "ট্রেজারার", "কোষাধ্যক্ষ",
            "treasurer", "koshaddhokkho"
        ]
    },
    {
        "canonical_en": "Proctor",
        "canonical_bn": "প্রক্টর",
        "aliases": [
            "proctor", "proctor (in charge)", "assistant proctor",
            "প্রক্টর", "প্রক্টর (ভারপ্রাপ্ত)", "সহকারী প্রক্টর",
            "proctor"
        ]
    }
]

# Relationship filter indicator words that link name/designation to department
RELATIONSHIP_INDICATORS: List[str] = [
    # English
    "in", "from", "of", "at", "under", "for", "within", "belonging to",
    # Bangla
    "দপ্তরের", "দপ্তরে", "অফিসের", "অফিসে", "শাখার", "শাখায়", "বিভাগের", "বিভাগে",
    "এর", "তে", "এ", "মধ্যে", "থেকে", "অধীনে",
    # Banglish
    "er", "te", "e", "moddhe", "theke", "odhine"
]

# Stopwords to safely remove when parsing names/unrecognized tokens
# MUST NOT remove tokens that match known designations (e.g. "Director", "Assistant")
DIRECTORY_STOPWORDS: List[str] = [
    # English commands & fillers
    "list", "show", "all", "give", "find", "who", "are", "is", "the", "me", "please",
    "details", "information", "info", "contact", "number", "numbers", "names", "tell",
    "employee", "employees", "officer", "officers", "staff", "staffs", "personnel",
    # Bangla commands & fillers
    "তালিকা", "দেখান", "দেখাও", "দিন", "বলুন", "সকল", "সব", "কারা", "কে", "কে কে",
    "তথ্য", "নাম্বার", "নম্বর", "ফোন", "ইমেইল", "যোগাযোগ", "কতজন", "কত জন", "সমূহ",
    "কর্মকর্তা ও কর্মচারী", "কর্মকর্তা ও কর্মচারীবৃন্দ", "কর্মকর্তা ও কর্মচারীবৃন্দের",
    "কর্মকর্তা", "কর্মকর্তাদের", "কর্মকর্তারা", "কর্মকর্তাগণ", "কর্মকর্তাগণের", "কর্মকর্তাবৃন্দ", "কর্মকর্তাবৃন্দের",
    "কর্মচারী", "কর্মচারীদের", "কর্মচারীরা", "কর্মচারীগণ", "কর্মচারীগণের", "কর্মচারীবৃন্দ", "কর্মচারীবৃন্দের",
    "স্টাফ", "বৃন্দ", "বৃন্দের", "গণ", "গণের", "ও", "এবং",
    # Banglish commands
    "list dao", "dekhao", "bolo", "ke ke", "kara", "kotojon", "kormokorta", "kormochari"
]

# Name Transliteration Map (English <-> Bengali phonetics)
NAME_TRANSLITERATION_MAP: Dict[str, List[str]] = {
    "mridul": ["মুদুল", "মৃদুল", "mri_roy", "মৃদুল রায়", "মুদুল রায়"],
    "mri": ["মুদুল", "মৃদুল", "mri_roy"],
    "roy": ["রায়", "রায়"],
    "rakib": ["রাকিব"],
    "rakibul": ["রাকিবুল"],
    "shahnewaz": ["শাহনেওয়াজ", "শাহনেওয়াজ"],
    "biplab": ["বিপ্লব"],
    "mobarak": ["মোবারক"],
    "hayder": ["হায়দার", "হায়দার"],
    "nazimul": ["নাজিমুল"],
    "faruk": ["ফারুক"],
    "azharul": ["আজহারুল"],
    "mahfuz": ["মাহফুজ"],
    "shofiqul": ["শফিকুল", "শফিক"],
    "hasan": ["হাসান"],
    "hossain": ["হোসেন"],
    "alam": ["আলম"],
    "islam": ["ইসলাম"],
    "rahman": ["রহমান"],
    "ahmed": ["আহমেদ", "আহমদ"],
    "ali": ["আলী", "আলি"],
    "khan": ["খান"],
    "sarkar": ["সরকার"],
    "shakil": ["শাকিল"],
    "sikder": ["শিকদার"],
    "farzana": ["ফারজানা"],
    "subel": ["সুবেল"],
    "sajib": ["সজিব", "সজীব"],
    "mondal": ["মন্ডল", "মণ্ডল"],
    "narjis": ["নার্জিস"]
}


