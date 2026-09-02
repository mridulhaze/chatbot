"""
National University Bangladesh AI Assistant — Result Response Formatter
Builds clean, structured Markdown responses with direct portal links, official notices, and action chips.
"""

from typing import Dict, Any, List, Tuple
from .entity_extractor import ResultQueryEntities
from .config import RESULT_LINKS, RECENT_NOTICE_PAGE_URL, MAIN_RESULT_PORTAL
from backend.models import SourceCitation


def format_result_response(
    entities: ResultQueryEntities,
    notices: List[Dict[str, Any]]
) -> Tuple[str, List[SourceCitation], float, List[str]]:
    """
    Formats the appropriate Markdown response based on entities, sub-intent, and matched notices.
    Returns (reply_markdown, citations_list, confidence_score, action_chips_list).
    """
    prog_key = entities.program or "ALL"
    prog_info = RESULT_LINKS.get(prog_key, RESULT_LINKS["ALL"])
    prog_url = prog_info.get("url", MAIN_RESULT_PORTAL)
    prog_bn = prog_info.get("bangla_name", "জাতীয় বিশ্ববিদ্যালয়")
    prog_en = prog_info.get("english_name", "National University")
    sms_format = prog_info.get("sms_format", "NU <COURSE_CODE> <Roll/Reg_No> send to 16222")

    year_bn = entities.year_bn or ""
    prog_label = "সকল রেজাল্ট" if prog_key == "ALL" else (prog_bn if "রেজাল্ট" in prog_bn else f"{prog_bn} রেজাল্ট")
    header_title = f"{prog_bn} {year_bn}".strip() if year_bn else (prog_label if prog_key == "ALL" else f"{prog_bn}")

    top_notice = notices[0] if notices else None

    # Base Citations
    citations = [
        SourceCitation(
            title=f"জাতীয় বিশ্ববিদ্যালয় রেজাল্ট পোর্টাল — {prog_bn}",
            url=prog_url,
            category="OFFICIAL_RESULT_PORTAL"
        )
    ]
    if top_notice:
        notice_url = top_notice.get("pdf_url") or top_notice.get("url") or RECENT_NOTICE_PAGE_URL
        citations.append(
            SourceCitation(
                title=top_notice.get("title", "ফলাফল সংক্রান্ত অফিসিয়াল বিজ্ঞপ্তি"),
                url=notice_url,
                date=top_notice.get("published_date"),
                category="NU_RESULT_NOTICE"
            )
        )
    else:
        citations.append(
            SourceCitation(
                title="জাতীয় বিশ্ববিদ্যালয় সাম্প্রতিক নোটিশ বোর্ড",
                url=RECENT_NOTICE_PAGE_URL,
                category="NU_OFFICIAL_NOTICE_BOARD"
            )
        )

    # -------------------------------------------------------------
    # 1. RESULT_GENERAL (Menu Format)
    # -------------------------------------------------------------
    if entities.sub_intent == "RESULT_GENERAL":
        reply = (
            "### 🎓 জাতীয় বিশ্ববিদ্যালয়ের রেজাল্ট (NU Results)\n\n"
            "আপনি কোন কোর্সের ফলাফল দেখতে চান? নিচের তালিকা থেকে নির্বাচন করুন বা বিস্তারিত লিখে পাঠান:\n\n"
            "- 🔹 **অনার্স (Honours):** ১ম, ২য়, ৩য় ও ৪র্থ বর্ষের ফলাফল\n"
            "- 🔹 **ডিগ্রি পাস (Degree Pass):** ১ম, ২য় ও ৩য় বর্ষের ফলাফল\n"
            "- 🔹 **মাস্টার্স (Masters):** প্রিলিমিনারি ও শেষ পর্বের ফলাফল\n"
            "- 🔹 **প্রফেশনাল (Professional):** বিবিএ, সিএসই, বিএড, এলএলবি ইত্যাদি\n"
            "- 🔹 **পুনঃনিরীক্ষণ (Re-scrutiny):** পরীক্ষার খাতা পুনর্নিরীক্ষণের ফলাফল\n\n"
            "---\n"
            f"🔗 **সকল ফলাফল আর্কাইভ:** [{MAIN_RESULT_PORTAL}]({MAIN_RESULT_PORTAL})\n\n"
            f"📢 **সর্বশেষ অফিসিয়াল নোটিশ:** [Recent News & Notice]({RECENT_NOTICE_PAGE_URL})\n\n"
            "💡 *নির্দিষ্ট বর্ষের ফলাফল বা প্রকাশের তারিখ জানতে কোর্স ও বর্ষ উল্লেখ করুন (যেমন: 'অনার্স ৪র্থ বর্ষ রেজাল্ট')।*"
        )
        action_chips = [
            "অনার্স রেজাল্ট",
            "ডিগ্রি রেজাল্ট",
            "মাস্টার্স রেজাল্ট",
            "প্রফেশনাল রেজাল্ট",
            "পুনঃনিরীক্ষণ ফলাফল",
            "সর্বশেষ রেজাল্ট নোটিশ"
        ]
        return reply, citations, 1.0, action_chips

    # -------------------------------------------------------------
    # 2. RESULT_LINK & RESULT_CHECK
    # -------------------------------------------------------------
    if entities.sub_intent in ["RESULT_LINK", "RESULT_CHECK"]:
        reply = (
            f"### 🎓 {header_title} রেজাল্ট অনুসন্ধান\n\n"
            "জাতীয় বিশ্ববিদ্যালয়ের অফিসিয়াল রেজাল্ট পোর্টালে আপনার রোল ও রেজিস্ট্রেশন নম্বর দিয়ে সরাসরি ফলাফল অনুসন্ধান করতে পারবেন:\n\n"
            f"🔗 **সরাসরি রেজাল্ট পোর্টাল:** [{prog_bn} রেজাল্ট দেখুন]({prog_url})\n\n"
            "📋 **ফলাফল দেখার সহজ ধাপসমূহ:**\n"
            "1. উপরের লিংকে প্রবেশ করে আপনার পরীক্ষার সাল ও সংশ্লিষ্ট কোর্স নির্বাচন করুন।\n"
            "2. আপনার **রোল (Roll)** ও **রেজিস্ট্রেশন নম্বর (Registration Number)** প্রবেশ করান।\n"
            "3. স্ক্রিনে প্রদর্শিত ক্যাপচা সিকিউরিটি কোডটি লিখে **Search Result** বাটনে ক্লিক করুন।\n\n"
            f"📱 **এসএমএসে ফলাফল পেতে:** `{sms_format}`\n\n"
            "---\n"
            f"📢 **সর্বশেষ পরীক্ষার নোটিশ:** [Recent News & Notice]({RECENT_NOTICE_PAGE_URL})"
        )
        action_chips = [
            f"{prog_bn} রেজাল্ট",
            "সর্বশেষ রেজাল্ট নোটিশ",
            "পুনঃনিরীক্ষণ ফলাফল"
        ]
        return reply, citations, 1.0, action_chips

    # -------------------------------------------------------------
    # 3. RESULT_REVALUATION
    # -------------------------------------------------------------
    if entities.sub_intent == "RESULT_REVALUATION":
        notice_block = ""
        if top_notice:
            n_url = top_notice.get("pdf_url") or top_notice.get("url") or RECENT_NOTICE_PAGE_URL
            n_date = top_notice.get("published_date") or ""
            notice_block = (
                f"\n📢 **সর্বশেষ পুনঃনিরীক্ষণ সংক্রান্ত বিজ্ঞপ্তি:**\n"
                f"- 📄 **বিজ্ঞপ্তি:** {top_notice.get('title')}\n"
                f"- 📅 **প্রকাশের তারিখ:** {n_date}\n"
                f"- 📥 **বিজ্ঞপ্তি লিংক:** [অফিসিয়াল নোটিশ (PDF)]({n_url})\n"
            )

        reply = (
            "### 📝 পরীক্ষার খাতা পুনঃনিরীক্ষণ (Re-scrutiny / Revaluation) ফলাফল ও নিয়মাবলী\n\n"
            "জাতীয় বিশ্ববিদ্যালয়ের যেকোনো পরীক্ষার ফলাফল প্রকাশের পর ফলাফল পুনঃনিরীক্ষণের আবেদন ও ফলাফল দেখার প্রক্রিয়া নিচে দেওয়া হলো:\n\n"
            f"🔗 **পুনঃনিরীক্ষণ রেজাল্ট পোর্টাল:** [results.nu.ac.bd/revaluation]({prog_url})\n\n"
            "📌 **আবেদন ও ফলাফল সংক্রান্ত নিয়মাবলী:**\n"
            "- ফলাফল প্রকাশের সাধারণত ১৫ থেকে ৩০ দিনের মধ্যে অনলাইনে সোনালী সেবার মাধ্যমে নির্ধারিত ফি জমা দিয়ে আবেদন করতে হয়।\n"
            "- পুনঃনিরীক্ষণের ফলাফল প্রস্তুত হলে উপরের পোর্টাল এবং অফিসিয়াল নোটিশ বোর্ডের মাধ্যমে প্রকাশ করা হয়।\n"
            f"{notice_block}\n"
            "---\n"
            f"🌐 **মূল রেজাল্ট আর্কাইভ:** [{MAIN_RESULT_PORTAL}]({MAIN_RESULT_PORTAL}) | 📢 **সর্বশেষ নোটিশ:** [Recent News]({RECENT_NOTICE_PAGE_URL})"
        )
        action_chips = ["পুনঃনিরীক্ষণ ফলাফল", "অনার্স রেজাল্ট", "ডিগ্রি রেজাল্ট", "মাস্টার্স রেজাল্ট"]
        return reply, citations, 1.0, action_chips

    # -------------------------------------------------------------
    # 4. RESULT_DATE_QUERY ("result kobe", "result kobe dibe")
    # -------------------------------------------------------------
    if entities.sub_intent == "RESULT_DATE_QUERY":
        if top_notice:
            n_url = top_notice.get("pdf_url") or top_notice.get("url") or RECENT_NOTICE_PAGE_URL
            n_date = top_notice.get("published_date") or ""
            reply = (
                f"### 📅 {header_title} প্রকাশের সর্বশেষ অফিসিয়াল তথ্য\n\n"
                "জাতীয় বিশ্ববিদ্যালয়ের অফিসিয়াল নোটিশ অনুযায়ী সংশ্লিষ্ট ফলাফল সংক্রান্ত বিজ্ঞপ্তি:\n\n"
                f"📢 **অফিসিয়াল বিজ্ঞপ্তি:** {top_notice.get('title')}\n"
                f"📅 **প্রকাশের তারিখ:** {n_date}\n"
                f"📥 **অফিসিয়াল নোটিশ ডাউনলোড:** [বিজ্ঞপ্তি দেখুন (PDF)]({n_url})\n\n"
                f"🔎 **অনলাইনে ফলাফল দেখতে:** [{prog_bn} রেজাল্ট পোর্টাল]({prog_url})\n\n"
                "---\n"
                f"🌐 **সর্বশেষ নোটিশ বোর্ড:** [Recent News & Notice]({RECENT_NOTICE_PAGE_URL})\n\n"
                "💡 *জাতীয় বিশ্ববিদ্যালয় কর্তৃপক্ষ অফিসিয়াল বিজ্ঞপ্তি প্রকাশের মাধ্যমেই ফলাফল প্রকাশের নিশ্চিত তারিখ জানিয়ে থাকে।*"
            )
        else:
            reply = (
                f"### 📅 {header_title} প্রকাশের তথ্য\n\n"
                "⚠️ **এ বিষয়ে কোনো তথ্য পাওয়া যায়নি।**\n\n"
                "জাতীয় বিশ্ববিদ্যালয়ের সাম্প্রতিক অফিসিয়াল নোটিশ বোর্ডে এই ফলাফল প্রকাশের নির্দিষ্ট তারিখ সম্পর্কিত কোনো বিজ্ঞপ্তি পাওয়া যায়নি।\n\n"
                "💡 *জাতীয় বিশ্ববিদ্যালয় কর্তৃপক্ষ অফিসিয়াল বিজ্ঞপ্তি প্রকাশের মাধ্যমেই কেবল ফলাফল প্রকাশের তারিখ নিশ্চিত করে।*\n\n"
                f"🔎 **ফলাফল পোর্টাল:** [{prog_label} পোর্টাল]({prog_url})\n\n"
                f"📢 **সর্বশেষ নোটিশ পেজ:** [Recent News & Notice]({RECENT_NOTICE_PAGE_URL})"
            )
        action_chips = [prog_label, "সর্বশেষ রেজাল্ট নোটিশ", "পুনঃনিরীক্ষণ ফলাফল"]
        return reply, citations, 1.0, action_chips

    # -------------------------------------------------------------
    # 5. RESULT_PUBLICATION & RESULT_LATEST_NOTICE & RESULT_BY_PROGRAM
    # -------------------------------------------------------------
    if top_notice:
        n_url = top_notice.get("pdf_url") or top_notice.get("url") or RECENT_NOTICE_PAGE_URL
        n_date = top_notice.get("published_date") or ""
        reply = (
            f"🎓 **{header_title}**\n\n"
            "📢 **সর্বশেষ অফিসিয়াল তথ্য ও বিজ্ঞপ্তি:**\n"
            f"- 📄 **বিজ্ঞপ্তি:** {top_notice.get('title')}\n"
            f"- 📅 **প্রকাশের তারিখ:** {n_date}\n"
            f"- 📥 **অফিসিয়াল বিজ্ঞপ্তি লিংক:** [বিজ্ঞপ্তি দেখুন (PDF)]({n_url})\n\n"
            f"🔎 **ফলাফল দেখুন:** [{prog_label} পোর্টাল]({prog_url})\n\n"
            f"🌐 **সর্বশেষ NU নোটিশ বোর্ড:** [Recent News / Notice]({RECENT_NOTICE_PAGE_URL})\n\n"
            f"📱 **এসএমএসে রেজাল্ট পেতে:** `{sms_format}`\n\n"
            "---\n"
            "💡 *সংশ্লিষ্ট পরীক্ষার রোল ও রেজিস্ট্রেশন নম্বর দিয়ে অনলাইনে রেজাল্ট দেখা যাবে।*"
        )
    else:
        reply = (
            f"🎓 **{header_title}**\n\n"
            "⚠️ **এ বিষয়ে কোনো তথ্য পাওয়া যায়নি।**\n\n"
            "জাতীয় বিশ্ববিদ্যালয়ের সাম্প্রতিক অফিসিয়াল নোটিশে এই ফলাফল সম্পর্কিত নির্দিষ্ট কোনো বিজ্ঞপ্তি পাওয়া যায়নি। সর্বশেষ নোটিশ ও রেজাল্ট দেখতে নিচের অফিসিয়াল লিংকে প্রবেশ করুন:\n\n"
            f"🔎 **ফলাফল দেখুন:** [{prog_label} পোর্টাল]({prog_url})\n\n"
            f"📢 **সর্বশেষ NU নোটিশ বোর্ড:** [Recent News / Notice]({RECENT_NOTICE_PAGE_URL})\n\n"
            f"📱 **এসএমএসে রেজাল্ট ফরম্যাট:** `{sms_format}`"
        )

    action_chips = [
        prog_label,
        "সর্বশেষ রেজাল্ট নোটিশ",
        "পুনঃনিরীক্ষণ ফলাফল"
    ]
    return reply, citations, 1.0, action_chips
