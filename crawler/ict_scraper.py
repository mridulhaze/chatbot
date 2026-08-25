import logging
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict, Any
from langchain_core.documents import Document

from .base_scraper import BaseScraper
from db.sql_store import get_sql_store

logger = logging.getLogger("NU_ICT_SCRAPER")

ICT_URL = "https://www.nu.ac.bd/ict-department.php"

class ICTScraper(BaseScraper):
    def scrape_ict_info(self) -> Tuple[List[Document], int, int]:
        """
        Scrapes ICT Department overview, employee & officer profiles, phone, email, and running activities.
        """
        sql_store = get_sql_store()
        documents = []
        pages_scraped = 0
        new_items_count = 0

        html = self.fetch_url(ICT_URL)
        if not html:
            logger.warning(f"Could not fetch ICT Department page: {ICT_URL}")
            return documents, 0, 0

        pages_scraped += 1
        soup = BeautifulSoup(html, "html.parser")

        # 1. Extract Overview & Activities
        dept_text = """# National University ICT Department (তথ্য প্রযুক্তি দপ্তর)

### Overview & Location:
- **Location**: 12th and 13th floor of Academic Building, Gazipur Campus.
- **Role**: Started journey in 1999 as Computer Center. Manages admission portal, registration, online form fill-up, examination results processing, university websites (nu.ac.bd, nubd.info, app1.nu.edu.bd, ems.nu.ac.bd), Sonali Seba integration, network infrastructure, data center, and 225 Mbps fiber optic campus connectivity.
- **Head of Department**: Director (In-Charge): Md. Shahnewaz
- **Total Employees**: Over 86 ICT professionals, officers, and staff.

### Key Running Services & Portals:
- Online Admission Application: http://app1.nu.edu.bd/
- Results & Result Archive: https://results.nu.ac.bd/ and http://www.nu.ac.bd/results/
- Form Fill-up & EMS Portal: http://ems.nu.ac.bd/ and http://www.nubd.info/form_fillup/
- Online Re-Evaluation: http://103.113.200.36/PAMS/ICTUnit/Re-Evaluation.aspx
- Teachers Management Information System (TMIS): tmis.nu.ac.bd
- College Monitoring and Evaluation System (CMES): cmes.nu.ac.bd
- Sonali Seba Online Payment Gateway: Sonali Bank online slip integration.
"""

        # 2. Extract Officer and Employee Cards
        cards = soup.find_all("article", class_="nu-ict-officer-card")
        employees = []

        for c in cards:
            name_el = c.find("div", class_="nu-ict-name-line")
            name = name_el.find("strong").get_text(strip=True) if name_el and name_el.find("strong") else ""
            if not name:
                continue

            info_lines = c.find_all("div", class_="nu-ict-info-line")
            desig, phone, email = "", "", ""
            for line in info_lines:
                lbl = line.find("span", class_="nu-ict-info-label")
                lbl_text = lbl.get_text(strip=True).lower() if lbl else ""
                val_text = line.get_text(strip=True)
                
                if "designation" in lbl_text:
                    desig = val_text.replace("Designation", "").strip()
                elif "phone" in lbl_text:
                    phone = val_text.replace("Phone", "").strip()
                elif "email" in lbl_text:
                    a_tag = line.find("a")
                    email = a_tag.get("href", "").replace("mailto:", "").strip() if a_tag else val_text.replace("Email", "").strip()
                    if email == "...":
                        email = ""

            p_type = c.get("data-person-type", "officer/staff")
            employees.append({
                "name": name,
                "designation": desig,
                "phone": phone,
                "email": email,
                "type": p_type
            })

        # Format employee directory into searchable markdown chunks
        emp_text = f"# National University ICT Department — Officers & Employee Directory (কর্মকর্তা ও কর্মচারী তালিকা)\n\n"
        emp_text += f"**Source**: {ICT_URL}\n**Total Staff Listed**: {len(employees)}\n\n"
        
        from .departments_scraper import translate_designation

        for e in employees:
            bn_d, en_d, bi_d = translate_designation(e['designation'])
            e['designation_bn'] = bn_d
            e['designation_en'] = en_d
            e['designation_bilingual'] = bi_d

            sql_store.upsert_officer(
                department_slug="ict-department",
                department_name="আইসিটি দপ্তর (ICT Department)",
                department_url=ICT_URL,
                name=e['name'],
                designation_bn=bn_d,
                designation_en=en_d,
                phone=e['phone'],
                email=e['email'],
                raw_details=f"Phone: {e['phone']} | Email: {e['email']}"
            )

            emp_text += f"### {e['name']}\n"
            emp_text += f"- **পদবি (Designation)**: {bi_d}\n"
            if e['phone'] and e['phone'] != "...":
                emp_text += f"- **ফোন নম্বর (Phone)**: {e['phone']}\n"
            if e['email'] and e['email'] != "...":
                emp_text += f"- **ইমেইল (Email)**: {e['email']}\n"
            emp_text += f"- **দপ্তর**: তথ্য প্রযুক্তি (আইসিটি) দপ্তর, জাতীয় বিশ্ববিদ্যালয়, গাজীপুর ক্যাম্পাস (১২ ও ১৩ তলা, একাডেমিক ভবন)\n\n"

        # Ingest structured FAQs for quick search
        sql_store.insert_faq_entry(
            question="জাতীয় বিশ্ববিদ্যালয়ের আইসিটি (ICT) দপ্তরের অবস্থান ও পরিচালকের তথ্য কী?",
            answer="জাতীয় বিশ্ববিদ্যালয়ের আইসিটি দপ্তর গাজীপুর মূল ক্যাম্পাসের একাডেমিক ভবনের ১২ ও ১৩ তলায় অবস্থিত। আইসিটি দপ্তরের পরিচালক (ভারপ্রাপ্ত) হলেন মোঃ শাহনেওয়াজ। দপ্তরের ওয়েবসাইট: https://www.nu.ac.bd/ict-department.php",
            source_url=ICT_URL,
            language="bn",
            category="ICT Department",
            confidence=1.0,
            verified_by_admin=1
        )
        sql_store.insert_faq_entry(
            question="Who is the Director of National University ICT Department?",
            answer="The Director (In-Charge) of the National University ICT Department is Md. Shahnewaz. The department is located on the 12th & 13th floors of the Academic Building, Gazipur Campus. Source: https://www.nu.ac.bd/ict-department.php",
            source_url=ICT_URL,
            language="en",
            category="ICT Department",
            confidence=1.0,
            verified_by_admin=1
        )
        new_items_count += len(employees)

        # Create Documents
        doc_overview = Document(
            page_content=dept_text,
            metadata={"source": ICT_URL, "category": "ICT Department", "type": "ict_overview"}
        )
        doc_directory = Document(
            page_content=emp_text,
            metadata={"source": ICT_URL, "category": "ICT Officers & Employees", "type": "employee_directory"}
        )

        documents.append(doc_overview)
        documents.append(doc_directory)

        logger.info(f"Scraped ICT Department info with {len(employees)} officers/employees.")
        return documents, pages_scraped, new_items_count
