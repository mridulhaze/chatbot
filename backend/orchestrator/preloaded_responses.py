"""
National University AI Assistant - Preloaded Instant Response Engine
Pre-compiled, rich responses with official links, citations, and interactive chips for zero-latency (<1ms) execution.
"""

from typing import Optional, Dict, Any
from backend.models.schemas import ChatResponse, SourceCitation

# Pre-compiled Citation Cards
CITATIONS_ADMISSION = [
    SourceCitation(title="জাতীয় বিশ্ববিদ্যালয় ভর্তি পোর্টাল", url="http://app11.nu.edu.bd/", date="অফিসিয়াল পোর্টাল"),
    SourceCitation(title="অনলাইন ভর্তি নির্দেশিকা", url="http://app11.nu.edu.bd/notice", date="সার্কুলার")
]

CITATIONS_EMS = [
    SourceCitation(title="EMS স্টুডেন্ট পোর্টাল", url="https://ems.nu.ac.bd/", date="অফিসিয়াল সেবা"),
    SourceCitation(title="ফরম পূরণ নোটিশ বোর্ড", url="https://www.nu.ac.bd/recent-notices.php", date="রুটিন")
]

CITATIONS_ERP_SERVICES = [
    SourceCitation(title="জাতীয় বিশ্ববিদ্যালয় স্টুডেন্ট ERP সার্ভিসেস পোর্টাল", url="http://103.113.200.68/nu-app/", date="ERP অনলাইন সেবা"),
    SourceCitation(title="জাতীয় বিশ্ববিদ্যালয় অনলাইন সার্ভিস পোর্টাল", url="http://103.113.200.68/nu-app/", date="স্টুডেন্ট লগইন"),
    SourceCitation(title="সোনালী সেবা ই-পেমেন্ট গেটওয়ে", url="https://www.nu.ac.bd/", date="অনলাইন পেমেন্ট")
]

CITATIONS_RESULTS = [
    SourceCitation(title="জাতীয় বিশ্ববিদ্যালয় ফলাফল আর্কাইভ", url="https://results.nu.ac.bd/", date="ফলাফল পোর্টাল"),
    SourceCitation(title="রেজাল্ট সার্ভার ২", url="http://103.113.200.68/nu-app/search.php", date="বিকল্প সার্ভার")
]

CITATIONS_GENERAL = [
    SourceCitation(title="জাতীয় বিশ্ববিদ্যালয় মূল ওয়েবসাইট", url="https://www.nu.ac.bd/", date="অফিসিয়াল পোর্টাল"),
    SourceCitation(title="সাম্প্রতিক নোটিশ ও অফিস আদেশ", url="https://www.nu.ac.bd/recent-notices.php", date="সার্কুলার"),
    SourceCitation(title="ভর্তি ও রেজিস্ট্রেশন পোর্টাল", url="http://app11.nu.edu.bd/", date="ভর্তি শাখা"),
    SourceCitation(title="EMS ও ফরম পূরণ পোর্টাল", url="https://ems.nu.ac.bd/", date="পরীক্ষা শাখা")
]

# 1. Welcome & General Overview Message (Exact rich layout from Master UI)
WELCOME_REPLY = """জাতীয় বিশ্ববিদ্যালয়ের (National University of Bangladesh) শিক্ষা বিষয়ক যেকোনো সহায়তার জন্য আপনার নির্দিষ্ট প্রশ্নটি করুন। আপনাকে কীভাবে সহায়তা করা যেতে পারে তার একটি সংক্ষিপ্ত তালিকা নিচে দেওয়া হলো:

### ১. ভর্তি সংক্রান্ত তথ্য (Admissions)
• **কোর্সসমূহ:** অনার্স (সম্মান), ডিগ্রি (পাস), মাস্টার্স ও প্রফেশনাল কোর্স।
• **ভর্তি প্রক্রিয়া:** এসএসসি ও এইচএসসি ফলাফলের ভিত্তিতে সরাসরি অনলাইনে আবেদন সম্পন্ন করতে হয়।
• **অফিসিয়াল লিংক:** [জাতীয় বিশ্ববিদ্যালয় ভর্তি পোর্টাল](http://app11.nu.edu.bd/)

### ২. পরীক্ষা ও ফরম পূরণ (Form Fill-Up & EMS)
• **পরীক্ষার ফরম পূরণ:** অনলাইনে ফরম পূরণ সম্পন্ন করে স্ব-স্ব কলেজে ফি সহ জমা দিতে হয়।
• **ইএমএস অ্যাকাউন্ট সমস্যা:** একাউন্ট ব্লক বা পাসওয়ার্ড ভুলে গেলে [EMS পোর্টালে](https://ems.nu.ac.bd/) শিক্ষার্থী তথ্য যাচাই করে রিসেট সুবিধা পাওয়া যায়।
• **অফিসিয়াল লিংক:** [ফরম পূরণ ও ইএমএস পোর্টাল](https://ems.nu.ac.bd/)

### ৩. পরীক্ষার ফলাফল (Results)
• **সিজিপিএ (CGPA) ও গ্রেডিং:** বছরভিত্তিক ফলাফল জানতে রেজিস্ট্রেশন/রোল নম্বর ব্যবহার করুন।
• **নিরাপদ চেক লিংক:** [ফলাফল পোর্টাল](https://results.nu.ac.bd/) অথবা যেকোনো মোবাইল থেকে SMS করুন:
  `NU <space> DEG/HONS/MAT <space> Roll/Reg No` লিখে পাঠান **16222** নম্বরে।

### ৪. একাডেমিক নোটিশ ও সার্কুলার
• সময়সূচি, সংশোধিত রুটিন ও জরুরি নির্দেশনার জন্য সর্বদা অফিসিয়াল নোটিশ বোর্ড অনুসরণ করুন।
• **অফিসিয়াল লিংক:** [জাতীয় বিশ্ববিদ্যালয় নোটিশ বোর্ড](https://www.nu.ac.bd/recent-notices.php)

### ৫. প্রশাসনিক ও দাপ্তরিক যোগাযোগ
• [রেজিস্ট্রার দপ্তর](https://www.nu.ac.bd/) • [পরীক্ষা নিয়ন্ত্রক দপ্তর](https://www.nu.ac.bd/)
• [আইসিটি দপ্তর](https://www.nu.ac.bd/) • [উপাচার্য দপ্তর](https://www.nu.ac.bd/)

আপনার নির্দিষ্ট কোনো বিষয়, পরীক্ষা বা ভর্তি সম্পর্কিত প্রশ্ন থাকলে বিস্তারিত জানান।"""

# 2. Preloaded Admissions Overview
ADMISSION_REPLY = """### 🎓 জাতীয় বিশ্ববিদ্যালয় ভর্তি নির্দেশিকা ও তথ্য (Admissions)

জাতীয় বিশ্ববিদ্যালয়ের অধীনে সকল স্নাতক (সম্মান), পাস ও স্নাতকোত্তর কোর্সে মেধা তালিকার ভিত্তিতে শিক্ষার্থী ভর্তি করা হয়:

1. **অনার্স ১ম বর্ষ (Honours 1st Year):**
   - **যোগ্যতা:** এসএসসি ও এইচএসসি পরীক্ষায় নির্দিষ্ট ন্যূনতম জিপিএ (মানবিকে মোট ৬.৫, বিজ্ঞান ও ব্যবসায় শিক্ষায় ৭.০)।
   - **আবেদন প্রক্রিয়া:** [ভর্তি পোর্টালে](http://app11.nu.edu.bd/) প্রাথমিক আবেদন ফরম পূরণ করে কলেজ কর্তৃক নির্ধারিত ফি রকেট/বিকাশ/মোবাইল ব্যাংকিংয়ের মাধ্যমে জমা দিতে হয়।
2. **ডিগ্রি (পাস) কোর্স:**
   - ৩ বছর মেয়াদী বিএ/বিএসএস/বিবিএস/বিএসসি কোর্সে আবেদন কার্যক্রম সার্কুলার অনুযায়ী পরিচালিত হয়।
3. **মাস্টার্স ও প্রফেশনাল কোর্স:**
   - প্রিলিমিনারি ও মাস্টার্স ফাইনাল কোর্সে অনলাইনে আবেদন গ্রহণ করা হয়।

👉 **ভর্তি সংক্রান্ত অফিসিয়াল পোর্টাল:** [app11.nu.edu.bd](http://app11.nu.edu.bd/)"""

# 3. Preloaded Examination & Routine
EXAM_REPLY = """### 📝 পরীক্ষা ও রুটিন সংক্রান্ত তথ্য (Examinations & Routines)

জাতীয় বিশ্ববিদ্যালয়ের সকল পরীক্ষার রুটিন, কেন্দ্র তালিকা ও সংশোধিত বিজ্ঞপ্তি সংক্রান্ত জরুরি তথ্য:

1. **পরীক্ষার রুটিন প্রকাশ:** সকল বর্ষের পরীক্ষার রুটিন অফিসিয়াল নোটিশ বোর্ডে পিডিএফ আকারে প্রকাশিত হয়।
2. **প্রবেশপত্র (Admit Card):** পরীক্ষা শুরুর সাধারণত ৩-৭ দিন পূর্বে স্ব-স্ব কলেজ অধ্যক্ষের মাধ্যমে সিল ও স্বাক্ষরযুক্ত প্রবেশপত্র বিতরণ করা হয়।
3. **পরীক্ষার নিয়মাবলী:** প্রবেশপত্র এবং রেজিস্ট্রেশন কার্ড অবশ্যই পরীক্ষার হলে সাথে রাখতে হবে।

👉 **পরীক্ষার সর্বশেষ নোটিশ ও রুটিন দেখুন:** [nu.ac.bd/recent-notices.php](https://www.nu.ac.bd/recent-notices.php)"""

# 4. Preloaded Results & SMS System
RESULTS_REPLY = """### 📊 পরীক্ষার ফলাফল ও সিজিপিএ জানার নিয়ম (Results)

জাতীয় বিশ্ববিদ্যালয়ের ফলাফল দ্রুত ও নির্ভুলভাবে জানার দুটি পদ্ধতি রয়েছে:

1. **অনলাইন পোর্টাল (Web Portal):**
   - [results.nu.ac.bd](https://results.nu.ac.bd/) ভিজিট করে আপনার রোল এবং রেজিস্ট্রেশন নম্বর দিয়ে বছর নির্বাচন করুন।
2. **এসএমএস (SMS) এর মাধ্যমে দ্রুত ফলাফল:**
   - মেসেজ অপশনে গিয়ে লিখুন:
     - **অনার্স:** `NU HONS <Roll/Registration No>`
     - **ডিগ্রি:** `NU DEG <Roll/Registration No>`
     - **মাস্টার্স:** `NU MAT <Roll/Registration No>`
   - পাঠিয়ে দিন **16222** নম্বরে (যেকোনো মোবাইল অপারেটর থেকে)।

3. **ফলাফল পুনর্নিরীক্ষণ (Rescrutiny):**
   - ফলাফল প্রকাশের ৩০ দিনের মধ্যে সোনালী সেবার মাধ্যমে অনলাইনে ফি জমা দিয়ে আবেদন করা যায়।"""

# 5. Preloaded Form Fill-Up & EMS
EMS_REPLY = """### 💻 ফরম পূরণ ও ইএমএস পোর্টাল নির্দেশিকা (Form Fill-Up & EMS)

পরীক্ষায় অংশগ্রহণের জন্য অনলাইনে ফরম পূরণ বাধ্যতামূলক:

1. **ফরম পূরণ প্রক্রিয়া:**
   - [ems.nu.ac.bd](https://ems.nu.ac.bd/) এ স্টুডেন্ট লগইন করুন অথবা স্ব-স্ব পরীক্ষার ফরম পূরণ লিংকে যান।
   - বিষয় কোড ও ব্যক্তিগত তথ্য যাচাই করে ফরম সাবমিট করুন এবং প্রিন্ট কপি কলেজে জমা দিন।
2. **পাসওয়ার্ড বা অ্যাকাউন্ট সমস্যা:**
   - যদি EMS পোর্টালে পাসওয়ার্ড ভুলে যান বা অ্যাকাউন্ট ব্লক হয়ে যায়, তাহলে 'Forgot Password' অপশনে রেজিস্ট্রেশন নম্বর দিয়ে রিসেট করুন।
   - সমস্যা সমাধান না হলে আমাদের **টোকেন সার্ভিসে** একটি সাপোর্ট টোকেন খুলুন।"""


# 7. Services Mega-Menu Breakdown Replies
SERVICES_MENU_REPLY = """### 🏛️ জাতীয় বিশ্ববিদ্যালয় সকল অনলাইন সেবা পোর্টাল তালিকা (Services Menu)

জাতীয় বিশ্ববিদ্যালয়ের অফিসিয়াল ওয়েবসাইট ([nu.ac.bd](https://www.nu.ac.bd/)) অনুযায়ী মূল সেবাসমূহ নিচে দেওয়া হলো:

#### 👥 স্টুডেন্ট ও পরীক্ষা সংক্রান্ত সেবা:
1. 📜 **[স্টুডেন্ট অনলাইন সার্ভিস পোর্টাল (nu-app)](http://103.113.200.68/nu-app/)**: সার্টিফিকেট, মার্কশিট, ট্রান্সক্রিপ্ট, রেজিস্ট্রেশন কার্ড ও টিসি আবেদন।
2. 🔄 **[খাতা পুনর্মূল্যায়ন ও পুনঃনিরীক্ষণ (Re-Evaluation)](https://results.nu.ac.bd/)**: ফলাফল প্রকাশের ৩০ দিনের মধ্যে সোনালী সেবায় আবেদন।
3. 🔍 **[সনদপত্র ও WES ভেরিফিকেশন (Verification Service)](http://103.113.200.68/nu-app/)**: দেশি ও বিদেশি উচ্চশিক্ষার ডকুমেন্ট সত্যায়ন।
4. 🪪 **সংশোধিত ও ডুপ্লিকেট এডমিট কার্ড**: ভুল প্রবেশপত্র সংশোধন ও উত্তোলনের আবেদন।
5. 🏢 **ওয়ান স্টপ সার্ভিস সেন্টার (One Stop Services)**: গাজীপুর ও আঞ্চলিক কেন্দ্র থেকে সরাসরি জরুরি সনদ বিতরণ।

#### 🎓 কলেজ ও প্রতিষ্ঠান সংক্রান্ত সেবা:
1. 🏫 **কলেজ লগইন (College Login)**: টিসি অনুমোদন (e-TC NOC), গভর্নিং বডি ও অ্যাডহক কমিটি, অধিভুক্তি নবায়ন ও শিক্ষক নিয়োগ।
2. 📊 **[সিএমইএস (CMES - College Monitoring & Evaluation)](https://www.nu.ac.bd/)**: কলেজ তদারকি ও একাডেমিক মান নিশ্চিতকরণ।
3. 🗺️ **কলেজ প্রোফাইল ও কলেজ ম্যাপ**: দেশের সকল অধিভুক্ত কলেজের বিস্তারিত তথ্য ও অবস্থান।

#### 👨‍🏫 শিক্ষক ও কর্মকর্তা সেবা:
1. 💻 **[টিএমআইএস (TMIS - Teachers Management Information System)](http://tmis.nu.ac.bd/)**: শিক্ষকদের কেন্দ্রীয় ডাটাবেজ।
2. 📚 **[টিটিআইএস (TTIS - Teachers Training Information System)](http://ttis.nu.ac.bd/)**: শিক্ষক প্রশিক্ষণ ও ওয়ার্কশপ পোর্টাল।
3. 📝 **[মৌখিক ও ব্যবহারিক পরীক্ষার বিল (Viva/Practical Bill)](http://ems.nu.ac.bd/)**: পরীক্ষকদের অনলাইন বিল এন্ট্রি।
4. 📧 **[ওয়েবমেইল (Webmail)](https://mail.nu.ac.bd/)** ও **কর্মচারী সেবা (Employee Services)**।

#### 🌐 অন্যান্য গুরুত্বপূর্ণ পোর্টাল:
• 💳 **সোনালী সেবা (Sonali Seba e-Payment)** • 💼 **চাকরি পোর্টাল (Job Portal)** • 🎥 **[অনলাইন ভিডিও লেকচার গ্যালারি](https://www.nu.ac.bd/)**
"""

CMES_REPLY = """### 📊 কলেজ মনিটরিং অ্যান্ড ইভ্যালুয়েশন সিস্টেম (CMES)

**CMES (College Monitoring and Evaluation System)** হলো জাতীয় বিশ্ববিদ্যালয়ের আওতাধীন সকল কলেজের একাডেমিক ও প্রশাসনিক কার্যক্রম তদারকির ডিজিটাল পোর্টাল:

• **উদ্দেশ্য:** কলেজের পাঠদান মান, শিক্ষক ও শিক্ষার্থী উপস্থিতি এবং ল্যাব/অবকাঠামোগত উন্নয়ন পর্যবেক্ষণ।
• **ব্যবহারকারী:** জাতীয় বিশ্ববিদ্যালয় কলেজ পরিদর্শন শাখা ও কলেজ প্রশাসন।
👉 **বিস্তারিত দেখুন:** [জাতীয় বিশ্ববিদ্যালয় পোর্টাল](https://www.nu.ac.bd/)"""

WES_VERIFICATION_REPLY = """### 🔍 সনদপত্র, নম্বরপত্র ও WES ভেরিফিকেশন নির্দেশিকা (Verification Service)

বিদেশি উচ্চশিক্ষা বা আন্তর্জাতিক স্বীকৃতির জন্য জাতীয় বিশ্ববিদ্যালয় থেকে সার্টিফিকেট ও ট্রান্সক্রিপ্ট সত্যায়ন (WES / ECE / ICAS):

1. **অনলাইন আবেদন:** [জাতীয় বিশ্ববিদ্যালয় স্টুডেন্ট পোর্টাল (http://103.113.200.68/nu-app/)](http://103.113.200.68/nu-app/) এ Student Login করে **'Verification / WES'** অপশনে যান।
2. **ডকুমেন্ট আপলোড:** আপনার সকল বর্ষের একাডেমিক সার্টিফিকেট, মার্কশিট এবং WES Reference Number ফরম আপলোড করুন।
3. **ফি প্রদান:** নির্ধারিত ফি সোনালী সেবার মাধ্যমে পরিশোধ করুন।
4. **সরাসরি প্রেরণ:** বিশ্ববিদ্যালয় পরীক্ষা নিয়ন্ত্রক দপ্তর সরাসরি সিলগালা খামে বা ইলেকট্রনিক মাধ্যমে WES-এ প্রেরণ করে।
"""

# 6. Preloaded Certificate, Transcript & TC Services
TC_REPLY = """### 📜 জাতীয় বিশ্ববিদ্যালয় কলেজ ছাড়পত্র / টিসি (Transfer Certificate - TC) নির্দেশিকা

জাতীয় বিশ্ববিদ্যালয়ের নিয়মিত শিক্ষার্থীদের কলেজ পরিবর্তনের (e-TC) আবেদন সম্পূর্ণ অনলাইনে **স্টুডেন্ট ERP সার্ভিসেস পোর্টাল**-এর মাধ্যমে সম্পন্ন করতে হয়:

1. **অনলাইন স্টুডেন্ট রেজিস্ট্রেশন ও লগইন:**
   - [জাতীয় বিশ্ববিদ্যালয় স্টুডেন্ট ERP সার্ভিসেস পোর্টাল (http://103.113.200.68/nu-app/)](http://103.113.200.68/nu-app/) অথবা [103.113.200.68/nu-app](http://103.113.200.68/nu-app/) এ যান।
   - রেজিস্ট্রেশন নম্বর ও সেশন দিয়ে **Student Login** করুন (নতুন হলে প্রথমে 'Student Register' করুন)।

2. **টিসি (TC) ফরম পূরণ ও কলেজ নির্বাচন:**
   - ড্যাশবোর্ড থেকে **'Academic Services' -> 'College Transfer / TC'** অপশনে ক্লিক করুন।
   - বর্তমান কলেজের তথ্য স্বয়ংক্রিয়ভাবে প্রদর্শিত হবে। যে কলেজে স্থানান্তর হতে চান (Target College) সেটি নির্বাচন করুন এবং যথাযথ কারণ উল্লেখ করুন।

3. **ফি প্রদান (Sonali Seva e-Payment):**
   - আবেদন সাবমিট করার পর স্বয়ংক্রিয় সোনালী সেবা পে-স্লিপ ডাউনলোড করুন অথবা অনলাইন পেমেন্ট গেটওয়ে দিয়ে নির্ধারিত ফি পরিশোধ করুন।

4. **অনলাইন ছাড়পত্র অনুমোদন ও ট্র্যাকিং:**
   - আবেদনটি প্রথমে বর্তমান কলেজ ও পরে কাঙ্ক্ষিত কলেজের প্রিন্সিপাল প্যানেলে যায়।
   - উভয় কলেজের অনলাইন অনাপত্তি (NOC/Acceptance) সম্পন্ন হলে জাতীয় বিশ্ববিদ্যালয়ের রেজিস্ট্রেশন শাখা চূড়ান্ত অনুমোদন দেয়।
   - শিক্ষার্থী ERP প্রোফাইল থেকেই অনলাইন ট্রান্সফার সার্টিফিকেট (Approved e-TC) ডাউনলোড করতে পারেন।

🔗 **জরুরি অফিসিয়াল লিংক:**
- **স্টুডেন্ট ERP লগইন ও আবেদন:** [http://103.113.200.68/nu-app/](http://103.113.200.68/nu-app/) অথবা [http://103.113.200.68/nu-app/](http://103.113.200.68/nu-app/)
- **নোটিশ বোর্ড:** [সকল নোটিশ (nu.ac.bd)](https://www.nu.ac.bd/recent-news-notice.php)"""

CERTIFICATE_REPLY = """### 📜 সাময়িক/মূল সনদ ও ট্রান্সক্রিপ্ট উত্তোলনের নিয়ম (Certificate & Transcript)

জাতীয় বিশ্ববিদ্যালয় থেকে মূল সনদপত্র (Original Certificate), সাময়িক সনদ (Provisional Certificate) এবং একাডেমিক ট্রান্সক্রিপ্ট (Academic Transcript) উত্তোলনের আবেদন সম্পূর্ণ অনলাইনে **ERP স্টুডেন্ট সার্ভিসেস পোর্টাল**-এর মাধ্যমে করা হয়:

1. **অনলাইন আবেদন (Student ERP Login):**
   - [জাতীয় বিশ্ববিদ্যালয় স্টুডেন্ট সার্ভিসেস পোর্টাল (http://103.113.200.68/nu-app/)](http://103.113.200.68/nu-app/) অথবা [103.113.200.68/nu-app](http://103.113.200.68/nu-app/) এ স্টুডেন্ট একাউন্টে লগইন করুন।
   - **'Academic Services' -> 'Certificate Application' / 'Transcript Application'** মেনু নির্বাচন করুন।

2. **প্রয়োজনীয় তথ্য ও ডকুমেন্ট আপলোড:**
   - রেজিস্ট্রেশন নম্বর, সেশন ও পাশের বছর সিলেক্ট করে প্রবেশপত্র/রেজিস্ট্রেশন কার্ড এবং ফলাফলের কপি সংযুক্ত করুন।

3. **ফি প্রদান (Sonali Seva):**
   - সোনালী সেবা পে-স্লিপের মাধ্যমে সোনালী ব্যাংকে অথবা অনলাইন ব্যাংকিং/মোবাইল ফিনান্সিয়াল সার্ভিসের মাধ্যমে ফি পরিশোধ করুন।

4. **ট্র্যাকিং ও সনদপত্র ডেলিভারি:**
   - আপনার ERP অ্যাকাউন্ট থেকে 'Application Tracking' এ সর্বশেষ অগ্রগতি যাচাই করতে পারবেন। ডেলিভারি প্রস্তুত হলে বিশ্ববিদ্যালয়ের ওয়ান-স্টপ সার্ভিস / সনদপত্র শাখা হতে সংগ্রহ করা যাবে।

🔗 **অফিসিয়াল পোর্টাল লিংক:** [http://103.113.200.68/nu-app/](http://103.113.200.68/nu-app/) | [http://103.113.200.68/nu-app/](http://103.113.200.68/nu-app/)"""

CORRECTION_REPLY = """### ✏️ সনদপত্র, নম্বরপত্র ও তথ্যের ভুল সংশোধন নির্দেশিকা (Document Corrections)

নাম, পিতা-মাতার নাম, রোল, রেজিস্ট্রেশন নম্বর বা ফলাফলের ভুল সংশোধনের আবেদন প্রক্রিয়া:

1. **অনলাইন আবেদন (ERP Portal):**
   - [জাতীয় বিশ্ববিদ্যালয় ERP সার্ভিসেস পোর্টাল (http://103.113.200.68/nu-app/)](http://103.113.200.68/nu-app/) এ Student Login করে **'Document Correction'** অপশন বেছে নিন।
2. **প্রয়োজনীয় কাগজপত্র:**
   - এসএসসি/এইচএসসি মূল সনদ ও নম্বরপত্রের সত্যায়িত কপি, জাতীয় পরিচয়পত্র/জন্মনিবন্ধন, এবং কলেজ প্রত্যয়নপত্র আপলোড করুন।
3. **ফি ও সোনালী সেবা:**
   - সংশোধনের জন্য নির্ধারিত ফি সোনালী সেবার মাধ্যমে পরিশোধ করতে হবে।
4. **যাচাই ও সংশোধিত কপি:**
   - একাডেমিক কাউন্সিল ও সংশ্লিষ্ট পরীক্ষা শাখা যাচাই শেষে সংশোধিত ডকুমেন্ট অনুমোদন করে।

🔗 **সংশোধন পোর্টাল লিংক:** [http://103.113.200.68/nu-app/](http://103.113.200.68/nu-app/)"""

ERP_SERVICES_REPLY = """### 🌐 জাতীয় বিশ্ববিদ্যালয় স্টুডেন্ট ERP সার্ভিসেস ও অনলাইন সেবা পোর্টাল

জাতীয় বিশ্ববিদ্যালয়ের শিক্ষার্থীদের সকল একাডেমিক ও প্রশাসনিক সেবা প্রদানের জন্য কেন্দ্রীয় **Student ERP Services Portal** কার্যকর রয়েছে:

**প্রধান অনলাইন সেবাসমূহ:**
• 📜 **কলেজ ট্রান্সফার / টিসি (College Transfer / e-TC)**
• 🎓 **মূল ও সাময়িক সনদপত্র আবেদন (Original & Provisional Certificate)**
• 📊 **একাডেমিক ট্রান্সক্রিপ্ট ও নম্বরপত্র (Academic Transcript & Marksheet)**
• ✏️ **নাম ও তথ্যের ভুল সংশোধন (Document / Name Correction)**
• 📋 **দ্বৈত সনদ ও মাইগ্রেশন সার্টিফিকেট (Duplicate Certificate & Migration)**
• 💳 **সোনালী সেবা পে-স্লিপ ও অনলাইন ফি ট্র্যাকিং**

👉 **স্টুডেন্ট ERP লগইন লিংক:** [http://103.113.200.68/nu-app/](http://103.113.200.68/nu-app/) অথবা [http://103.113.200.68/nu-app/](http://103.113.200.68/nu-app/)"""



# Direct normalized phrase mapping for instant lookups (< 0.001s)
INSTANT_LOOKUP_MAP: Dict[str, ChatResponse] = {}

def _init_instant_lookups():
    # Greetings & Salutations
    greeting_triggers = [
        "hi", "hello", "hey", "start", "menu", "help", "hlo", "helo", "hy",
        "হাই", "হ্যালো", "শুরু", "মেনু", "সাহায্য", "আসসালামু আলাইকুম", "সালাম",
        "assalamu alaikum", "assalamualaikum", "kemon acho", "kemon achen",
        "কেমন আছেন", "কে আছো", "জাতীয় বিশ্ববিদ্যালয়", "জাতীয় বিশ্ববিদ্যালয়",
        "nu", "national university", "info"
    ]
    for trig in greeting_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=WELCOME_REPLY,
            citations=CITATIONS_GENERAL,
            intent="GREETING",
            skill_used="nu_general",
            suggested_chips=["🎫 টোকেন সার্ভিস (Token Service)", "📑 টোকেন স্ট্যাটাস চেক", "📄 সাম্প্রতিক নোটিশ", "🎓 ভর্তি তথ্য"]
        )

    # Admissions
    admission_triggers = [
        "admission", "admissions", "apply", "how to apply", "admission procedure",
        "ভর্তি", "ভর্তি তথ্য", "ভর্তি প্রক্রিয়া", "অনার্স ভর্তি", "ডিগ্রি ভর্তি", "মাস্টার্স ভর্তি", "ভর্তি পোর্টাল"
    ]
    for trig in admission_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=ADMISSION_REPLY,
            citations=CITATIONS_ADMISSION,
            intent="ADMISSION_INFO",
            skill_used="admission",
            suggested_chips=["🎓 অনার্স ১ম বর্ষ ভর্তি", "📄 ভর্তি সার্কুলার", "🎫 ভর্তি সহায়তা টোকেন", "🏠 মূল মেনু"]
        )

    # Exam & Routines
    exam_triggers = [
        "exam", "examination", "routine", "exam routine", "admit card",
        "পরীক্ষা", "পরীক্ষার রুটিন", "রুটিন", "এডমিট কার্ড", "প্রবেশপত্র", "পরীক্ষার সময়সূচি"
    ]
    for trig in exam_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=EXAM_REPLY,
            citations=CITATIONS_EMS,
            intent="EXAM_ROUTINE",
            skill_used="examination",
            suggested_chips=["📝 পরীক্ষার রুটিন দেখুন", "🎫 পরীক্ষার টোকেন খুলুন", "📊 ফলাফল চেক", "🏠 মূল মেনু"]
        )

    # Results & CGPA
    result_triggers = [
        "result", "results", "cgpa", "gpa", "marksheet", "rescrutiny",
        "ফলাফল", "রেজাল্ট", "সিজিপিএ", "মার্কশিট", "পুনর্নিরীক্ষণ", "বোর্ড চ্যালেঞ্জ"
    ]
    for trig in result_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=RESULTS_REPLY,
            citations=CITATIONS_RESULTS,
            intent="RESULT_INFO",
            skill_used="result",
            suggested_chips=["📊 ফলাফল পোর্টাল লিংক", "📱 SMS রেজাল্ট নিয়ম", "🎫 ফলাফল সংক্রান্ত টোকেন", "🏠 মূল মেনু"]
        )

    # Form Fill-Up & EMS
    ems_triggers = [
        "form fillup", "form fill up", "ems", "ems login", "password reset", "student portal",
        "ফরম পূরণ", "ইএমএস", "ইএমএস লগইন", "পাসওয়ার্ড ভুলে গেছি", "ফরম ফিলাপ"
    ]
    for trig in ems_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=EMS_REPLY,
            citations=CITATIONS_EMS,
            intent="EMS_INFO",
            skill_used="service_credentials",
            suggested_chips=["💻 EMS লগইন পোর্টাল", "🔐 ইএমএস পাসওয়ার্ড রিসেট", "🎫 ফরম পূরণ সাপোর্ট টোকেন", "🏠 মূল মেনু"]
        )


    # Services Mega Menu & Specialized Modules
    menu_triggers = [
        "services", "service menu", "all services", "সেবা", "সার্ভিস মেনু", "সকল সেবা", "সার্ভিস"
    ]
    for trig in menu_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=SERVICES_MENU_REPLY,
            citations=CITATIONS_GENERAL,
            intent="SERVICES_MENU_INFO",
            skill_used="nu_general",
            suggested_chips=["📜 স্টুডেন্ট nu-app পোর্টাল", "🔍 WES ভেরিফিকেশন", "📊 CMES কলেজ মনিটরিং", "🏠 মূল মেনু"]
        )

    cmes_triggers = ["cmes", "college monitoring", "কলেজ মনিটরিং", "সিএমইএস"]
    for trig in cmes_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=CMES_REPLY,
            citations=CITATIONS_GENERAL,
            intent="CMES_INFO",
            skill_used="nu_general",
            suggested_chips=["📊 CMES পোর্টাল", "🏛️ কলেজ পরিদর্শন দপ্তর", "🏠 মূল মেনু"]
        )

    wes_triggers = ["wes", "wes verification", "verification service", "ডকুমেন্ট ভেরিফিকেশন", "সত্যায়ন", "ইসিএ"]
    for trig in wes_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=WES_VERIFICATION_REPLY,
            citations=CITATIONS_ERP_SERVICES,
            intent="WES_VERIFICATION_INFO",
            skill_used="service_credentials",
            suggested_chips=["🔍 WES আবেদন লিংক", "💳 সোনালী সেবা ফি", "🎫 ভেরিফিকেশন টোকেন", "🏠 মূল মেনু"]
        )

    # College Transfer / TC (ছাড়পত্র)
    tc_triggers = [
        "tc", "transfer certificate", "college transfer", "tc form", "tc application",
        "টিসি", "ছাড়পত্র", "কলেজ পরিবর্তন", "কলেজ ট্রান্সফার", "টিসি ফরম", "টিসি আবেদন", "ছাড়পত্র"
    ]
    for trig in tc_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=TC_REPLY,
            citations=CITATIONS_ERP_SERVICES,
            intent="TC_INFO",
            skill_used="service_credentials",
            suggested_chips=["📜 স্টুডেন্ট ERP পোর্টাল লিংক", "💳 সোনালী সেবা ফি", "🎫 টিসি সহায়তা টোকেন", "🏠 মূল মেনু"]
        )

    # Document Corrections (ভুল সংশোধন)
    correction_triggers = [
        "correction", "name correction", "marksheet correction", "certificate correction", "spelling mistake",
        "সংশোধন", "নাম সংশোধন", "ভুল সংশোধন", "মার্কশিট সংশোধন", "সনদপত্র সংশোধন", "তথ্য সংশোধন"
    ]
    for trig in correction_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=CORRECTION_REPLY,
            citations=CITATIONS_ERP_SERVICES,
            intent="CORRECTION_INFO",
            skill_used="service_credentials",
            suggested_chips=["✏️ ERP সংশোধন পোর্টাল", "💳 সোনালী সেবা পে-স্লিপ", "🎫 সংশোধন সাপোর্ট টোকেন", "🏠 মূল মেনু"]
        )

    # Student ERP Services Portal
    erp_triggers = [
        "erp", "student login", "erp services", "103.113.200.68/nu-app", "103.113.200.68/nu-app", "nu-app", "nu app", "103.113.200.68", "student portal",
        "ইআরপি", "স্টুডেন্ট লগইন", "অনলাইন সার্ভিস", "ইআরপি সার্ভিস", "ছাত্র পোর্টাল"
    ]
    for trig in erp_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=ERP_SERVICES_REPLY,
            citations=CITATIONS_ERP_SERVICES,
            intent="ERP_SERVICES_INFO",
            skill_used="service_credentials",
            suggested_chips=["🌐 ERP লগইন পোর্টাল", "📜 টিসি (TC) আবেদন", "🎓 সার্টিফিকেট আবেদন", "🏠 মূল মেনু"]
        )

    # Certificates & Marksheets
    cert_triggers = [
        "certificate", "transcript", "original certificate", "provisional certificate",
        "সার্টিফিকেট", "নম্বরপত্র", "ট্রান্সক্রিপ্ট", "মূল সনদ", "সাময়িক সনদ"
    ]
    for trig in cert_triggers:
        INSTANT_LOOKUP_MAP[trig] = ChatResponse(
            reply=CERTIFICATE_REPLY,
            citations=CITATIONS_GENERAL,
            intent="CERTIFICATE_INFO",
            skill_used="document_search",
            suggested_chips=["📜 সার্টিফিকেট আবেদনের নিয়ম", "🎫 সার্টিফিকেট সহায়তা টোকেন", "🏠 মূল মেনু"]
        )

_init_instant_lookups()

def get_preloaded_response(query: str) -> Optional[ChatResponse]:
    """
    Checks if a normalized query has a preloaded instant response (< 0.001s execution).
    """
    normalized = query.lower().strip(" \t\n\r.?!,;:-_~`@#$%^&*()+=/\\|")
    if normalized in INSTANT_LOOKUP_MAP:
        return INSTANT_LOOKUP_MAP[normalized]
    
    # Check word-level match for short 1-2 word queries
    words = normalized.split()
    if len(words) <= 2:
        for w in words:
            if w in INSTANT_LOOKUP_MAP:
                return INSTANT_LOOKUP_MAP[w]
                
    return None
