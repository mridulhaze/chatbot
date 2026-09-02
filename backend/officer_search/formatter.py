"""
National University Bangladesh AI Assistant — Officer Response Formatter
Renders single profile cards, tabular directory lists, all-department mega menus, and zero-result suggestions.
"""

from typing import List, Dict, Any, Tuple
from .entity_extractor import OfficerQueryEntities
from .normalizer import convert_bn_to_en_digits, convert_en_to_bn_digits
from .aliases import DEPARTMENT_ALIASES
from backend.models import SourceCitation


def format_officer_response(
    officers: List[Dict[str, Any]],
    entities: OfficerQueryEntities,
    total_count: int,
    page: int = 1,
    page_size: int = 50,
    suggestions: List[str] = None
) -> Tuple[str, List[SourceCitation], List[str]]:
    """
    Renders structured Markdown response for officer directory queries.
    Returns (reply_markdown, citations_list, suggested_chips).
    """
    citations: List[SourceCitation] = []
    chips: List[str] = []

    # --- Case 1: All Departments Mega-Menu Listing ---
    if entities.is_all_departments_query:
        reply = "### 🏛️ জাতীয় বিশ্ববিদ্যালয়ের সকল প্রশাসনিক দপ্তর ও অফিস পরিচিতি (All Offices Directory)\n\n"
        reply += "জাতীয় বিশ্ববিদ্যালয়ের অফিশিয়াল ওয়েবসাইট ([nu.ac.bd](https://www.nu.ac.bd)) অনুযায়ী বিশ্ববিদ্যালয় প্রশাসনের ৪টি প্রধান বিভাগের অধীনে মোট **৩৩টি দপ্তর ও অফিস** রয়েছে:\n\n"

        hierarchy_groups = {}
        for d in DEPARTMENT_ALIASES:
            parent = d.get("parent", "অন্যান্য দপ্তর")
            if parent not in hierarchy_groups:
                hierarchy_groups[parent] = []
            hierarchy_groups[parent].append(d)

        for parent, depts in hierarchy_groups.items():
            reply += f"#### 🔹 {parent}:\n"
            for d in depts:
                reply += f"- **[{d['name_bn']} ({d['name_en']})]({d['url']})**\n"
            reply += "\n"

        reply += "---\n💡 *নির্দিষ্ট কোনো দপ্তরের কর্মকর্তা তালিকা দেখতে দপ্তরের নাম লিখে মেসেজ দিন (যেমন: 'আইসিটি কর্মকর্তা তালিকা' বা 'রেজিস্ট্রার দপ্তর')।*"

        for d in DEPARTMENT_ALIASES[:6]:
            citations.append(SourceCitation(
                title=f"{d['name_bn']} ({d['name_en']})",
                url=d["url"],
                category="Offices & Departments"
            ))

        chips = ["💻 আইসিটি দপ্তর কর্মকর্তা", "🏛️ রেজিস্ট্রার দপ্তর", "🏢 পরীক্ষা নিয়ন্ত্রক দপ্তর", "💰 অর্থ ও হিসাব দপ্তর"]
        return reply, citations, chips

    # --- Case 2: Zero Records Found ---
    if not officers:
        reply = "### ⚠️ কোনো কর্মকর্তা/কর্মচারীর তথ্য পাওয়া যায়নি\n\n"
        reply += "আপনার অনুসন্ধানের সাথে মিল পাওয়া কোনো কর্মকর্তা বা কর্মচারীর তথ্য জাতীয় বিশ্ববিদ্যালয়ের ডাটাবেজে পাওয়া যায়নি।\n\n"

        if suggestions:
            reply += "**আপনি কি নিচের কোনো একটি পদবি বা দপ্তরের তথ্য খুঁজছেন?**\n"
            for s in suggestions:
                reply += f"- {s}\n"
            reply += "\n"

        reply += "💡 *সঠিকভাবে অনুসন্ধানের জন্য কর্মকর্তার পুরো নাম, সঠিক পদবি (যেমন: 'সহকারী প্রোগ্রামার') অথবা দপ্তরের নাম (যেমন: 'আইসিটি দপ্তর') উল্লেখ করুন।*\n\n"
        reply += "---\n🔗 **অফিসিয়াল দপ্তর পোর্টাল:** [জাতীয় বিশ্ববিদ্যালয় পোর্টাল](https://www.nu.ac.bd)"

        chips = ["💻 আইসিটি সহকারী প্রোগ্রামার", "🏛️ রেজিস্ট্রার দপ্তর কর্মকর্তা", "🏢 পরীক্ষা নিয়ন্ত্রক দপ্তর", "🏛️ সকল দপ্তরের তালিকা"]
        return reply, citations, chips

    # --- Case 3: Single Person Direct Profile Card ---
    if len(officers) == 1 and entities.name:
        o = officers[0]
        name = o.get('name') or "কর্মকর্তা"
        desig_bn = o.get('designation_bn') or ""
        desig_en = o.get('designation_en') or ""
        dept_name = o.get('department_name') or "জাতীয় বিশ্ববিদ্যালয়"
        dept_url = o.get('department_url') or "https://www.nu.ac.bd"
        phone = convert_bn_to_en_digits(str(o.get('phone', '')).strip()) if o.get('phone') and str(o['phone']).strip() not in ['-', 'None', ''] else "তথ্য উপলব্ধ নয়"
        email = o.get('email', '').strip() if o.get('email') and str(o['email']).strip() not in ['-', 'None', ''] else "তথ্য উপলব্ধ নয়"

        desig_display = f"{desig_bn} ({desig_en})" if (desig_bn and desig_en and desig_bn != desig_en) else (desig_bn or desig_en or "কর্মকর্তা")

        reply = f"### 👤 কর্মকর্তা/কর্মচারীর বিস্তারিত তথ্য\n\n"
        reply += f"জাতীয় বিশ্ববিদ্যালয়ের অফিশিয়াল ডাটাবেজ অনুযায়ী **{name}**-এর যোগাযোগের তথ্য:\n\n"
        reply += f"- 👤 **নাম (Name):** **{name}**\n"
        reply += f"- 💼 **পদবি (Designation):** {desig_display}\n"
        reply += f"- 🏢 **দপ্তর (Department):** {dept_name}\n"
        reply += f"- 📞 **ফোন/মোবাইল (Phone):** `{phone}`\n"
        if email != "তথ্য উপলব্ধ নয়":
            reply += f"- 📧 **ইমেইল (Email):** [{email}](mailto:{email})\n"
        else:
            reply += f"- 📧 **ইমেইল (Email):** {email}\n"

        reply += f"\n---\n🔗 **অফিসিয়াল পোর্টাল:** [{dept_name}]({dept_url})\n"
        reply += "💡 *দাপ্তরিক প্রয়োজনে উল্লেখিত ফোন নম্বর অথবা ইমেইলে সরাসরি যোগাযোগ করতে পারেন।*"

        citations.append(SourceCitation(
            title=f"{name} — {dept_name}",
            url=dept_url,
            category="Offices & Directory"
        ))

        chips = ["💻 আইসিটি দপ্তর কর্মকর্তা", "🏛️ রেজিস্ট্রার দপ্তর", "🎫 সাপোর্ট টোকেন খুলুন"]
        return reply, citations, chips

    # --- Case 4: Tabular Listing (Department, Designation, or Combined Filter) ---
    # Setup Pagination Slice
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_count)
    page_officers = officers[start_idx:end_idx]

    # Determine Title & Context
    if entities.designation and entities.department_name:
        title = f"{entities.department_name} — {entities.designation_bn or entities.designation} তালিকা"
        subtitle = f"{entities.department_name}-এ কর্মরত **{entities.designation_bn or entities.designation}**"
        dept_url = entities.department_url or "https://www.nu.ac.bd"
    elif entities.designation:
        title = f"জাতীয় বিশ্ববিদ্যালয়ের {entities.designation_bn or entities.designation} তালিকা"
        subtitle = f"জাতীয় বিশ্ববিদ্যালয়ের বিভিন্ন দপ্তরে কর্মরত **{entities.designation_bn or entities.designation}**"
        dept_url = "https://www.nu.ac.bd"
    elif entities.department_name:
        title = f"{entities.department_name} — কর্মকর্তা ও কর্মচারীদের তালিকা"
        subtitle = f"{entities.department_name}-এর সকল কর্মকর্তা ও কর্মচারী"
        dept_url = entities.department_url or "https://www.nu.ac.bd"
    elif entities.name:
        title = f"নামের অনুসন্ধানের ফলাফল: '{entities.name}'"
        subtitle = f"নামের সাথে মিল থাকা কর্মকর্তা ও কর্মচারী"
        dept_url = "https://www.nu.ac.bd"
    else:
        title = "কর্মকর্তা ও কর্মচারী তালিকা"
        subtitle = "জাতীয় বিশ্ববিদ্যালয়ের কর্মকর্তা ও কর্মচারী"
        dept_url = "https://www.nu.ac.bd"

    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
    page_info_bn = f"(মোট {convert_en_to_bn_digits(str(total_count))} জনের মধ্যে {convert_en_to_bn_digits(str(start_idx + 1))}-{convert_en_to_bn_digits(str(end_idx))} প্রদর্শিত, পৃষ্ঠা {convert_en_to_bn_digits(str(page))}/{convert_en_to_bn_digits(str(total_pages))})"

    reply = f"### 👨‍💻 {title}\n\n"
    reply += f"জাতীয় বিশ্ববিদ্যালয়ের অফিশিয়াল ওয়েবসাইট ও ডাটাবেজ অনুযায়ী {subtitle} তথ্য তালিকা নিচে দেওয়া হলো {page_info_bn}:\n\n"

    # Build Markdown Table Rows
    table_rows = []
    # If cross-department search, include Department column
    include_dept_col = not bool(entities.department_slug)

    if include_dept_col:
        reply += "| ক্রমিক (SL) | নাম (Name) | পদবি (Designation) | দপ্তর (Department) | ফোন/মোবাইল (Phone) | ইমেইল (Email) |\n"
        reply += "|---|---|---|---|---|---|\n"
    else:
        reply += "| ক্রমিক (SL) | নাম (Name) | পদবি (Designation) | ফোন/মোবাইল (Phone) | ইমেইল (Email) |\n"
        reply += "|---|---|---|---|---|\n"

    for idx, o in enumerate(page_officers, start=start_idx + 1):
        sl_bn = convert_en_to_bn_digits(str(idx))
        name = o.get('name') or "-"
        desig = o.get('designation_bn') or o.get('designation_en') or "-"
        dept = o.get('department_name') or "-"
        phone = convert_bn_to_en_digits(str(o.get('phone', '')).strip()) if o.get('phone') and str(o['phone']).strip() not in ['-', 'None', ''] else "-"
        email = o.get('email', '').strip() if o.get('email') and str(o['email']).strip() not in ['-', 'None', ''] else "-"

        if include_dept_col:
            # Shorten department name for clean table rendering if long
            dept_short = dept.split("(")[0].strip() if "(" in dept else dept
            reply += f"| {sl_bn} | **{name}** | {desig} | {dept_short} | {phone} | {email} |\n"
        else:
            reply += f"| {sl_bn} | **{name}** | {desig} | {phone} | {email} |\n"

    reply += "\n---\n"
    if dept_url:
        reply += f"🔗 **অফিসিয়াল পোর্টাল লিংক:** [{title.split('—')[0].strip()}]({dept_url})\n"
    reply += "💡 *দাপ্তরিক প্রয়োজনে সংশ্লিষ্ট কর্মকর্তার ফোন নম্বর অথবা ইমেইলে সরাসরি যোগাযোগ করতে পারেন।*"

    citations.append(SourceCitation(
        title=title,
        url=dept_url,
        category="Offices & Directory"
    ))

    # Construct contextual navigation chips
    if page < total_pages:
        chips.append(f"⏩ পরবর্তী ৫০ জন (Page {page + 1})")
    if page > 1:
        chips.append(f"⏪ পূর্ববর্তী ৫০ জন (Page {page - 1})")

    if entities.department_slug == "ict-department":
        chips.extend(["💻 আইসিটি সহকারী প্রোগ্রামার", "🏛️ রেজিস্ট্রার দপ্তর", "🏛️ সকল দপ্তরের তালিকা"])
    elif entities.designation:
        chips.extend(["💻 আইসিটি সহকারী প্রোগ্রামার", "🏛️ সকল দপ্তরের তালিকা", "🎫 সাপোর্ট টোকেন"])
    else:
        chips.extend(["💻 আইসিটি দপ্তর কর্মকর্তা", "🏛️ রেজিস্ট্রার দপ্তর", "🏢 পরীক্ষা নিয়ন্ত্রক দপ্তর", "🏛️ সকল দপ্তরের তালিকা"])

    return reply, citations, chips
