import re
import logging
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from langchain_core.documents import Document

from db.sql_store import get_sql_store
from .base_scraper import BaseScraper

logger = logging.getLogger("NU_DEPARTMENTS_SCRAPER")

def convert_bn_to_en_digits(text: str) -> str:
    if not text:
        return ""
    trans = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    return str(text).translate(trans)

DESIGNATION_TRANSLATIONS = {
    # Leadership & Executive
    "উপাচার্য": "Vice-Chancellor",
    "উপ-উপাচার্য": "Pro-Vice-Chancellor",
    "ট্রেজারার": "Treasurer",
    "কোষাধ্যক্ষ": "Treasurer",
    "রেজিস্ট্রার": "Registrar",
    "উপ-রেজিস্ট্রার": "Deputy Registrar",
    "সহকারী রেজিস্ট্রার": "Assistant Registrar",
    "অতিরিক্ত রেজিস্ট্রার": "Additional Registrar",
    "অতিরিক্ত রেজিস্ট্রার ও সচিব": "Additional Registrar & Secretary",
    "অতিরিক্ত রেজিস্ট্রার ও সচিব -২": "Additional Registrar & Secretary - 2",
    
    # Directors & Administration
    "পরিচালক": "Director",
    "পরিচালক (ভারপ্রাপ্ত)": "Director (Acting)",
    "অতিরিক্ত পরিচালক": "Additional Director",
    "উপ-পরিচালক": "Deputy Director",
    "উপপরিচালক": "Deputy Director",
    "সহকারী পরিচালক": "Assistant Director",
    "পরীক্ষা নিয়ন্ত্রক": "Controller of Examinations",
    "পরীক্ষা নিয়ন্ত্রক": "Controller of Examinations",
    "উপ-পরীক্ষা নিয়ন্ত্রক": "Deputy Controller of Examinations",
    "উপ-পরীক্ষা নিয়ন্ত্রক": "Deputy Controller of Examinations",
    "সহকারী পরীক্ষা নিয়ন্ত্রক": "Assistant Controller of Examinations",
    "কলেজ পরিদর্শক": "Inspector of Colleges",
    "উপ-কলেজ পরিদর্শক": "Deputy Inspector of Colleges",
    "সহকারী কলেজ পরিদর্শক": "Assistant Inspector of Colleges",
    "গ্রন্থাগারিক": "Librarian",
    
    # ICT & Technical
    "সিস্টেম এনালিস্ট": "System Analyst",
    "সিনিয়র প্রোগ্রামার": "Senior Programmer",
    "সিনিয়র প্রোগ্রামার": "Senior Programmer",
    "প্রোগ্রামার": "Programmer",
    "সহকারী প্রোগ্রামার": "Assistant Programmer",
    "সহকারি প্রোগ্রামার": "Assistant Programmer",
    "নেটওয়ার্ক এডমিনিস্ট্রেটর": "Network Administrator",
    "নেটওয়ার্ক এডমিনিস্ট্রেটর": "Network Administrator",
    "নেটওয়ার্ক ইঞ্জিনিয়ার": "Network Engineer",
    "নেটওয়ার্ক ইঞ্জিনিয়ার": "Network Engineer",
    "সহকারী নেটওয়ার্ক ইঞ্জিনিয়ার": "Assistant Network Engineer",
    "সহকারী নেটওয়ার্ক ইঞ্জিনিয়ার": "Assistant Network Engineer",
    "মেইনটেন্যান্স ইঞ্জিনিয়ার": "Maintenance Engineer",
    "মেইনটেন্যান্স ইঞ্জিঃ": "Maintenance Engineer",
    "সহকারী মেইনটেন্যান্স ইঞ্জিনিয়ার": "Assistant Maintenance Engineer",
    "টেকনিক্যাল অফিসার": "Technical Officer",
    "সাব-টেকনিক্যাল অফিসার": "Sub-Technical Officer",
    "কম্পিউটার অপারেটর": "Computer Operator",
    "ডাটা এন্ট্রি অপারেটর": "Data Entry Operator",
    
    # Engineering, Medical & Accounts
    "প্রধান প্রকৌশলী": "Chief Engineer",
    "নির্বাহী প্রকৌশলী": "Executive Engineer",
    "সহকারী প্রকৌশলী": "Assistant Engineer",
    "উপ-সহকারী প্রকৌশলী": "Sub-Assistant Engineer",
    "ড্রাফটসম্যান": "Draftsman",
    "ইলেকট্রিক্যাল সুপারভাইজার": "Electrical Supervisor",
    "সিনিয়র মেডিকেল অফিসার": "Senior Medical Officer",
    "মেডিকেল অফিসার": "Medical Officer",
    "সহকারী মেডিকেল অফিসার": "Assistant Medical Officer",
    "হিসাব রক্ষণ কর্মকর্তা": "Accounts Officer",
    "অডিট কর্মকর্তা": "Audit Officer",
    "আইন কর্মকর্তা": "Law Officer",
    "জনসংযোগ কর্মকর্তা": "Public Relations Officer",
    "নিরাপত্তা কর্মকর্তা": "Security Officer",
    "এস্টেট কর্মকর্তা": "Estate Officer",
    "স্টোর কর্মকর্তা": "Store Officer",
    "ক্রয় কর্মকর্তা": "Procurement Officer",
    
    # Support Staff & Officers
    "সেকশন অফিসার": "Section Officer",
    "প্রশাসনিক কর্মকর্তা": "Administrative Officer",
    "উচ্চমান সহকারী": "Upper Division Assistant",
    "উচ্চমান সহকার": "Upper Division Assistant",
    "অফিস সহকারী": "Office Assistant",
    "অফিস সহকারী কাম কম্পিউটার মুদ্রাক্ষরিক": "Office Assistant Cum Computer Typist",
    "অফিস সহায়ক": "Office Support Staff",
    "পোর্টার": "Porter / Support Staff",
    "ড্রাইভার": "Driver",
    "সিকিউরিটি গার্ড": "Security Guard",
    "টেলিফোন অপারেটর": "Telephone Operator",
    "ফটোকপি অপারেটর": "Photocopy Operator",
    "প্লাম্বার": "Plumber",
    "ইলেকট্রিশিয়ান": "Electrician"
}

def translate_designation(desig: str) -> Tuple[str, str, str]:
    """
    Returns (bn_title, en_title, bilingual_display)
    Accurately preserves compound titles without truncating.
    """
    if not desig:
        return "কর্মকর্তা / কর্মচারী", "Officer / Employee", "কর্মকর্তা / কর্মচারী"
        
    desig_clean = desig.strip()
    
    # Check if desig looks like a phone number or pure numeric string
    if re.search(r"^[\d\+\-\s০-৯]{6,}$", desig_clean) or desig_clean.isdigit():
        return "কর্মকর্তা / কর্মচারী", "Officer / Employee", "কর্মকর্তা / কর্মচারী"
    
    # 1. Exact match check
    for bn, en in DESIGNATION_TRANSLATIONS.items():
        if bn.lower() == desig_clean.lower() or en.lower() == desig_clean.lower():
            bilingual = f"{bn} ({en})" if bn != en else bn
            return bn, en, bilingual
            
    # 2. Sort translations by length descending to match compound titles before base titles
    sorted_translations = sorted(
        DESIGNATION_TRANSLATIONS.items(), 
        key=lambda x: max(len(x[0]), len(x[1])), 
        reverse=True
    )
    for bn, en in sorted_translations:
        if bn in desig_clean or (len(en) > 3 and en.lower() in desig_clean.lower()):
            bilingual = f"{bn} ({en})" if bn != en else bn
            return bn, en, bilingual

    # 3. Fallback heuristic rules
    desig_lower = desig_clean.lower()
    if "additional director" in desig_lower or "অতিরিক্ত পরিচালক" in desig_clean:
        return "অতিরিক্ত পরিচালক", "Additional Director", "অতিরিক্ত পরিচালক (Additional Director)"
    elif "programmer" in desig_lower or "প্রোগ্রামার" in desig_clean:
        if any(w in desig_lower or w in desig_clean for w in ["senior", "সিনিয়র", "সিনিয়র"]):
            return "সিনিয়র প্রোগ্রামার", "Senior Programmer", "সিনিয়র প্রোগ্রামার (Senior Programmer)"
        elif any(w in desig_lower or w in desig_clean for w in ["assistant", "সহকারী", "সহকারি"]):
            return "সহকারী প্রোগ্রামার", "Assistant Programmer", "সহকারী প্রোগ্রামার (Assistant Programmer)"
        else:
            return "প্রোগ্রামার", "Programmer", "প্রোগ্রামার (Programmer)"
    elif "analyst" in desig_lower or "এনালিস্ট" in desig_clean:
        return "সিস্টেম এনালিস্ট", "System Analyst", "সিস্টেম এনালিস্ট (System Analyst)"
    elif "director" in desig_lower or "পরিচালক" in desig_clean:
        if any(w in desig_lower or w in desig_clean for w in ["deputy", "উপ-পরিচালক", "উপপরিচালক"]):
            return "উপ-পরিচালক", "Deputy Director", "উপ-পরিচালক (Deputy Director)"
        elif any(w in desig_lower or w in desig_clean for w in ["assistant", "সহকারী"]):
            return "সহকারী পরিচালক", "Assistant Director", "সহকারী পরিচালক (Assistant Director)"
        elif any(w in desig_lower or w in desig_clean for w in ["acting", "ভারপ্রাপ্ত"]):
            return "পরিচালক (ভারপ্রাপ্ত)", "Director (Acting)", "পরিচালক (ভারপ্রাপ্ত) (Director (Acting))"
        else:
            return "পরিচালক", "Director", "পরিচালক (Director)"
    elif "registrar" in desig_lower or "রেজিস্ট্রার" in desig_clean:
        if any(w in desig_lower or w in desig_clean for w in ["deputy", "উপ-রেজিস্ট্রার"]):
            return "উপ-রেজিস্ট্রার", "Deputy Registrar", "উপ-রেজিস্ট্রার (Deputy Registrar)"
        elif any(w in desig_lower or w in desig_clean for w in ["assistant", "সহকারী"]):
            return "সহকারী রেজিস্ট্রার", "Assistant Registrar", "সহকারী রেজিস্ট্রার (Assistant Registrar)"
        else:
            return "রেজিস্ট্রার", "Registrar", "রেজিস্ট্রার (Registrar)"
    elif "controller" in desig_lower or "নিয়ন্ত্রক" in desig_clean or "নিয়ন্ত্রক" in desig_clean:
        if any(w in desig_lower or w in desig_clean for w in ["deputy", "উপ-পরীক্ষা"]):
            return "উপ-পরীক্ষা নিয়ন্ত্রক", "Deputy Controller of Examinations", "উপ-পরীক্ষা নিয়ন্ত্রক (Deputy Controller of Examinations)"
        elif any(w in desig_lower or w in desig_clean for w in ["assistant", "সহকারী"]):
            return "সহকারী পরীক্ষা নিয়ন্ত্রক", "Assistant Controller of Examinations", "সহকারী পরীক্ষা নিয়ন্ত্রক (Assistant Controller of Examinations)"
        else:
            return "পরীক্ষা নিয়ন্ত্রক", "Controller of Examinations", "পরীক্ষা নিয়ন্ত্রক (Controller of Examinations)"

    return desig_clean, desig_clean, desig_clean

class DepartmentsScraper(BaseScraper):
    """
    Comprehensive Scraper for all National University offices & departments from the official 'Office' menu (33+ departments):
    Grouped by University Governance Hierarchy (VC, Pro-VC 1, Pro-VC 2, Treasurer).
    """

    DEPARTMENTS = [
        # --- Under Vice-Chancellor ---
        {"name": "উপাচার্য দপ্তর (Vice-Chancellor Office)", "slug": "vc-office", "parent": "Vice-Chancellor", "url": "https://www.nu.ac.bd/vice-chancellor-office.php"},
        {"name": "রেজিস্ট্রার দপ্তর (Registrar Office)", "slug": "registrar-office", "parent": "Vice-Chancellor", "url": "https://www.nu.ac.bd/Registrar-office.php"},
        {"name": "পরিকল্পনা ও উন্নয়ন দপ্তর (Planning & Development)", "slug": "planning-development", "parent": "Vice-Chancellor", "url": "https://www.nu.ac.bd/planning-development.php"},
        {"name": "জনসংযোগ, তথ্য ও পরামর্শ দপ্তর (Public Relations)", "slug": "public-relations", "parent": "Vice-Chancellor", "url": "https://www.nu.ac.bd/public-relations.php"},
        {"name": "আন্তর্জাতিক ডেস্ক দপ্তর (International Desk)", "slug": "international-desk", "parent": "Vice-Chancellor", "url": "https://www.nu.ac.bd/international-desk-department.php"},
        {"name": "শৃঙ্খলা ও নিরাপত্তা দপ্তর (Discipline & Security)", "slug": "discipline-security", "parent": "Vice-Chancellor", "url": "https://www.nu.ac.bd/office-of-the-discipline-and-security.php"},
        {"name": "প্রকৌশল দপ্তর (Engineering Department)", "slug": "engineering", "parent": "Vice-Chancellor", "url": "https://www.nu.ac.bd/engineering-department-office.php"},
        {"name": "কলেজ মনিটরিং ও মূল্যায়ন দপ্তর (College Monitoring & Evaluation)", "slug": "college-monitoring", "parent": "Vice-Chancellor", "url": "https://www.nu.ac.bd/College-Monitoring-and-Evaluation-Department.php"},
        {"name": "আইন বিষয়ক দপ্তর (Law Affairs)", "slug": "law-affairs", "parent": "Vice-Chancellor", "url": "https://www.nu.ac.bd/Law_Department.php"},

        # --- Under Pro Vice-Chancellor 1 ---
        {"name": "উপ-উপাচার্য দপ্তর (Pro-Vice-Chancellor Office)", "slug": "pro-vc-office", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/Pro-Vice-Chancellor-Office.php"},
        {"name": "পরীক্ষা নিয়ন্ত্রক দপ্তর (Controller of Examination Office)", "slug": "exam-controller", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/exam-controller-office.php"},
        {"name": "কলেজ পরিদর্শন দপ্তর (College Inspection Department)", "slug": "inspector-of-college", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/inspector-of-college.php"},
        {"name": "অভ্যন্তরীণ নিরীক্ষা দপ্তর (Internal Audit)", "slug": "internal-audit", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/internal-audit-office.php"},
        {"name": "প্রকাশনা ও বিপণন দপ্তর (Publication & Marketing)", "slug": "publication-marketing", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/publication-section.php"},
        {"name": "শারীরিক শিক্ষা দপ্তর (Physical Education & Cultural Affairs)", "slug": "physical-education", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/physical-education.php"},
        {"name": "এস্টেট দপ্তর (Estate Department)", "slug": "estate", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/Estate_Department.php"},
        {"name": "মানবসম্পদ উন্নয়ন ও শুদ্ধাচার দপ্তর (HR Development)", "slug": "hr-development", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/Human-Resource-Development-and-Integrity.php"},

        # --- Under Pro Vice-Chancellor 2 ---
        {"name": "আইসিটি দপ্তর (ICT Department)", "slug": "ict-department", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/ict-department.php"},
        {"name": "পরিবহন শাখা (Transport Section)", "slug": "transport-department", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/transport-department.php"},
        {"name": "চিকিৎসা কেন্দ্র (Medical Centre)", "slug": "medical-centre", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/medical-services-department.php"},
        {"name": "আঞ্চলিক কেন্দ্র সমন্বয় দপ্তর (Regional Center Coordination)", "slug": "regional-center-coord", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/Regional-Center-Co-ordination.php"},
        {"name": "তথ্য ও সেবা দপ্তর (Information & Services)", "slug": "information-services", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/Information-and-services-department.php"},
        {"name": "ক্রয় দপ্তর (Procurement Department)", "slug": "procurement", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/Procurement_and_Store_Department.php"},
        {"name": "কেন্দ্রীয় ভাণ্ডার দপ্তর (Central Store)", "slug": "central-store", "parent": "Pro-Vice-Chancellor", "url": "https://www.nu.ac.bd/department-of-central-store.php"},

        # --- Under Treasurer ---
        {"name": "ট্রেজারার দপ্তর (Treasurer Office)", "slug": "treasurer-office", "parent": "Treasurer", "url": "https://www.nu.ac.bd/Treasurer-office.php"},
        {"name": "অনলাইন শিক্ষা দপ্তর (Online Education)", "slug": "online-education", "parent": "Treasurer", "url": "https://www.nu.ac.bd/Online_Education_Department.php"},
        {"name": "গ্রন্থাগার দপ্তর (Library Department)", "slug": "library-department", "parent": "Treasurer", "url": "https://www.nu.ac.bd/library-department.php"},
        {"name": "অর্থ ও হিসাব দপ্তর (Finance & Accounts)", "slug": "finance-accounts", "parent": "Treasurer", "url": "https://www.nu.ac.bd/finance-account.php"},
        {"name": "শিক্ষক প্রশিক্ষণ দপ্তর (Teachers Training Department)", "slug": "teachers-training", "parent": "Treasurer", "url": "https://www.nu.ac.bd/teachers-training-information.php"},
        {"name": "ভর্তি ও রেজিস্ট্রেশন সেল (Admission & Registration Cell)", "slug": "admission-registration", "parent": "Treasurer", "url": "https://www.nu.ac.bd/admission-and-registration-cell.php"},
        {"name": "মুক্তিযুদ্ধ ও বাংলাদেশ গবেষণা ইনস্টিটিউট (ILBS)", "slug": "ilbs", "parent": "Treasurer", "url": "https://www.nu.ac.bd/ILBS.php"},
        {"name": "আইকিউএসি (IQAC)", "slug": "iqac", "parent": "Treasurer", "url": "https://www.nu.ac.bd/IQAC.php"},
        {"name": "ফরেনসিক সায়েন্স ও সাইবার সিকিউরিটি ইনস্টিটিউট (IFSCS)", "slug": "ifscs", "parent": "Treasurer", "url": "https://www.nu.ac.bd/IFSCS.php"}
    ]

    def scrape(self) -> Tuple[List[Document], Dict[str, Any]]:
        all_docs: List[Document] = []
        sql_store = get_sql_store()
        stats = {
            "departments_scraped": 0,
            "total_employees_extracted": 0,
            "total_documents_built": 0
        }

        for dept in self.DEPARTMENTS:
            url = dept["url"]
            name = dept["name"]
            slug = dept["slug"]
            logger.info(f"Scraping department: {name} ({url})...")

            html = self.fetch_url(url)
            if not html:
                logger.warning(f"Could not fetch department page: {url}")
                continue

            try:
                dept_docs, employees = self._parse_department_page(dept, html)
                all_docs.extend(dept_docs)
                stats["departments_scraped"] += 1
                stats["total_employees_extracted"] += len(employees)
                stats["total_documents_built"] += len(dept_docs)
                
                # Save each officer into SQLite officers_directory
                for emp in employees:
                    sql_store.upsert_officer(
                        department_slug=slug,
                        department_name=name,
                        department_url=url,
                        name=emp["name"],
                        designation_bn=emp["designation_bn"],
                        designation_en=emp["designation_en"],
                        phone=emp.get("phone", ""),
                        email=emp.get("email", ""),
                        raw_details=emp.get("contact", "")
                    )

                logger.info(f"Successfully processed {name}: {len(employees)} officers/employees, {len(dept_docs)} RAG chunks.")
            except Exception as e:
                logger.error(f"Error parsing department {name}: {e}", exc_info=True)

        return all_docs, stats

    def _parse_department_page(self, dept: Dict[str, str], html: str) -> Tuple[List[Document], List[Dict[str, Any]]]:
        soup = BeautifulSoup(html, "html.parser")
        dept_name = dept["name"]
        dept_url = dept["url"]
        
        # Remove noisy tags
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()

        # 1. Extract Overview Text
        intro_parts = []
        for p in soup.find_all(["p", "h3", "h4", "div"]):
            txt = p.get_text(" ", strip=True)
            if len(txt) > 40 and not any(k in txt.lower() for k in ["copyright", "all rights reserved", "visitor count"]):
                if txt not in intro_parts:
                    intro_parts.append(txt)
        overview_text = "\n\n".join(intro_parts[:5])

        # 2. Extract Officer/Employee Cards
        employees = []

        # Method 0: Head/Leadership Profile Hero Card (e.g. Vice-Chancellor, Registrar, Dean Hero Cards)
        head_section = soup.find(class_=lambda c: c and any(k in str(c).lower() for k in ["head-profile", "head-info", "head-card", "dean-profile", "nu-vc-head", "nu-registrar-head"]))
        if head_section:
            h_name_el = head_section.find(class_=lambda c: c and any(k in str(c).lower() for k in ["head-name", "name"])) or head_section.find(["h2", "h3", "h4", "strong"])
            h_desig_el = head_section.find(class_=lambda c: c and any(k in str(c).lower() for k in ["head-designation", "designation"])) or head_section.find("p")
            
            h_name = h_name_el.get_text(strip=True) if h_name_el else ""
            h_desig = h_desig_el.get_text(strip=True) if h_desig_el else ""
            
            h_email = ""
            h_phone = ""
            mail_a = head_section.find("a", href=lambda h: h and "mailto:" in h)
            if mail_a:
                h_email = mail_a.get("href", "").replace("mailto:", "").strip()
            tel_a = head_section.find("a", href=lambda h: h and "tel:" in h)
            if tel_a:
                h_phone = tel_a.get("href", "").replace("tel:", "").strip()
                
            if h_name and len(h_name) > 2:
                h_phone_en = convert_bn_to_en_digits(h_phone)
                bn_d, en_d, bi_d = translate_designation(h_desig or dept_name)
                employees.append({
                    "name": h_name,
                    "designation_raw": h_desig,
                    "designation_bn": bn_d,
                    "designation_en": en_d,
                    "designation": bi_d,
                    "phone": h_phone_en or "দপ্তরে যোগাযোগযোগ্য",
                    "email": h_email or "",
                    "contact": f"Phone: {h_phone_en} | Email: {h_email}" if (h_phone_en or h_email) else ""
                })
        
        # Method A: Structured NU Officer Profile Cards (<article class="*officer-card*">)
        cards = soup.find_all(["article", "div"], class_=lambda c: c and any(k in str(c).lower() for k in ["officer-card", "member-card", "staff-card", "profile-card"]))
        for c in cards:
            name = ""
            name_line = c.find(class_=lambda x: x and "name-line" in str(x))
            if name_line and name_line.find("strong"):
                name = name_line.find("strong").get_text(strip=True)
            elif c.find("img") and c.find("img").get("alt"):
                name = c.find("img").get("alt").strip()
            elif c.find("strong"):
                name = c.find("strong").get_text(strip=True)
                
            desig_raw = ""
            phone = ""
            email = ""
            
            for line in c.find_all(class_=lambda x: x and ("info-line" in str(x) or "row" in str(x))):
                lbl_el = line.find(class_=lambda x: x and "info-label" in str(x))
                lbl = lbl_el.get_text(strip=True).lower() if lbl_el else ""
                
                val = line.get_text(" ", strip=True)
                if lbl_el:
                    val = val.replace(lbl_el.get_text(strip=True), "").strip()
                    
                if "designation" in lbl or "পদবী" in lbl:
                    desig_raw = val
                elif "phone" in lbl or "মোবাইল" in lbl or "ফোন" in lbl or "tel" in lbl:
                    phone = val
                elif "email" in lbl or "ইমেইল" in lbl or "ই-মেইল" in lbl:
                    mail_a = line.find("a", href=lambda h: h and "mailto:" in h)
                    email = mail_a.get_text(strip=True) if mail_a else val

            if name and len(name) > 2:
                phone_en = convert_bn_to_en_digits(phone)
                bn_desig, en_desig, bilingual_desig = translate_designation(desig_raw)
                employees.append({
                    "name": name,
                    "designation_raw": desig_raw,
                    "designation_bn": bn_desig,
                    "designation_en": en_desig,
                    "designation": bilingual_desig,
                    "phone": phone_en,
                    "email": email,
                    "contact": f"Phone: {phone_en} | Email: {email}" if (phone_en or email) else ""
                })

        # Method B: Tables fallback
        if not employees:
            for table in soup.find_all("table"):
                for r in table.find_all("tr"):
                    tds = r.find_all(["td", "th"])
                    cols = [td.get_text(strip=True) for td in tds]
                    if len(cols) >= 3 and not any(h in " ".join(cols).lower() for h in ["sl.", "picture", "designation", "email", "profile", "ক্রমিক", "পদবী"]):
                        # Detect email and phone
                        email = ""
                        phone = ""
                        mail_a = r.find("a", href=lambda h: h and "mailto:" in h)
                        if mail_a:
                            email = mail_a.get("href", "").replace("mailto:", "").strip()
                        tel_a = r.find("a", href=lambda h: h and "tel:" in h)
                        if tel_a:
                            phone = tel_a.get("href", "").replace("tel:", "").strip()

                        for c_text in cols:
                            if "@" in c_text and not email:
                                email = c_text
                            elif re.search(r"[\d০-৯]{8,}", c_text) and not phone:
                                phone = c_text

                        # Column detection for 7-8 column NU table: [SL, Pic, Name, PF, Designation, Phone, Email, View]
                        name_cand = ""
                        desig_cand = ""
                        if len(cols) >= 6:
                            name_cand = cols[2] if len(cols) > 2 and cols[2] and not cols[2].isdigit() and "@" not in cols[2] else cols[1]
                            for idx in [4, 3, 5]:
                                if idx < len(cols) and cols[idx] and "@" not in cols[idx] and not re.search(r"[\d০-৯]{8,}", cols[idx]) and cols[idx] != "০০০০":
                                    desig_cand = cols[idx]
                                    break
                        elif len(cols) >= 3:
                            name_cand = cols[1] if cols[0].isdigit() else cols[0]
                            desig_cand = cols[2] if cols[0].isdigit() else cols[1]

                        if name_cand and len(name_cand) > 2:
                            # Sanitize designation vs phone
                            if re.search(r"[\d০-৯]{7,}", desig_cand) or desig_cand.isdigit():
                                if not phone:
                                    phone = desig_cand
                                desig_cand = "কর্মকর্তা / কর্মচারী"

                            phone_en = convert_bn_to_en_digits(phone)
                            bn_d, en_d, bi_d = translate_designation(desig_cand or "কর্মকর্তা / কর্মচারী")
                            employees.append({
                                "name": name_cand,
                                "designation_raw": desig_cand,
                                "designation_bn": bn_d,
                                "designation_en": en_d,
                                "designation": bi_d,
                                "phone": phone_en,
                                "email": email,
                                "contact": f"Phone: {phone_en} | Email: {email}" if (phone_en or email) else ""
                            })

        # Deduplicate employees by name
        unique_emps = []
        seen_names = set()
        for e in employees:
            n = e.get("name", "").strip()
            if n and n not in seen_names and len(n) > 2:
                seen_names.add(n)
                unique_emps.append(e)

        # Build Rich Bilingual RAG Documents
        docs: List[Document] = []

        # Doc 1: Department Overview & Executive Summary
        overview_doc = f"# জাতীয় বিশ্ববিদ্যালয় — {dept_name}\n"
        overview_doc += f"অফিসিয়াল ওয়েব পোর্টাল: {dept_url}\n\n"
        if overview_text:
            overview_doc += f"### দপ্তরের ভূমিকা ও বিবরণ:\n{overview_text[:1200]}\n\n"
        overview_doc += f"### মোট কর্মকর্তা ও কর্মচারীর সংখ্যা: {len(unique_emps)} জন\n"

        docs.append(Document(
            page_content=overview_doc,
            metadata={
                "source": dept_url,
                "title": dept_name,
                "category": "Office & Department Overview",
                "type": "department_overview"
            }
        ))

        # Doc 2: Structured Employee & Officer Directory Lists (in chunks of 15 employees)
        chunk_size = 15
        for i in range(0, max(len(unique_emps), 1), chunk_size):
            chunk_emps = unique_emps[i : i + chunk_size]
            if not chunk_emps:
                break
            
            chunk_text = f"# {dept_name} — কর্মকর্তা ও কর্মচারীবৃন্দের তালিকা (অংশ {i//chunk_size + 1})\n"
            chunk_text += f"Official Portal: {dept_url}\n\n"
            chunk_text += "| ক্রমিক (SL) | কর্মকর্তা/কর্মচারীর নাম (Officer Name) | পদবী ও শাখা (Designation) | যোগাযোগের তথ্য (Contact & Email) |\n"
            chunk_text += "|---|---|---|---|\n"
            for idx, emp in enumerate(chunk_emps, start=i + 1):
                c_info = emp.get('phone', '') or ''
                if emp.get('email'):
                    c_info += f" | {emp['email']}" if c_info else emp['email']
                if not c_info:
                    c_info = emp.get('contact', 'দপ্তরে যোগাযোগযোগ্য')
                    
                chunk_text += f"| {idx} | **{emp['name']}** | {emp['designation']} | {c_info} |\n"
            
            docs.append(Document(
                page_content=chunk_text,
                metadata={
                    "source": dept_url,
                    "title": f"{dept_name} - কর্মকর্তা ও কর্মচারীবৃন্দের তালিকা",
                    "category": "Department Officers & Employee Directory",
                    "type": "employee_directory"
                }
            ))

        return docs, unique_emps

