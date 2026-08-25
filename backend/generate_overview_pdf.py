"""
National University Bangladesh AI Assistant & Smart Support Platform
Comprehensive Project Overview, Technical Architecture & 0-Level User Documentary PDF Generator
Outputs to: E:/projects/AI_CHAT_BOT/docs/project-overview.pdf
"""

import os
import sys
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group, Circle, Polygon
from reportlab.pdfgen import canvas

# 1. Register Fonts
FONT_PATH = "C:/Windows/Fonts/kalpurush.ttf"
ARIAL_PATH = "C:/Windows/Fonts/ARIALUNI.TTF"

if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("Kalpurush", FONT_PATH))
    MAIN_FONT = "Kalpurush"
    BOLD_FONT = "Kalpurush"
elif os.path.exists(ARIAL_PATH):
    pdfmetrics.registerFont(TTFont("ArialUni", ARIAL_PATH))
    MAIN_FONT = "ArialUni"
    BOLD_FONT = "ArialUni"
else:
    MAIN_FONT = "Helvetica"
    BOLD_FONT = "Helvetica-Bold"

OUTPUT_PDF_PATH = Path("E:/projects/AI_CHAT_BOT/docs/project-overview.pdf")
OUTPUT_PDF_PATH.parent.mkdir(parents=True, exist_ok=True)

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic total page count in footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Header (Only on pages > 1)
        if self._pageNumber > 1:
            self.setFillColor(colors.HexColor("#065f46"))
            self.rect(36, 762, 540, 2, fill=True, stroke=False)
            self.setFont(MAIN_FONT, 8)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(36, 768, "National University Bangladesh • AI Assistant & Support Platform (nu.ac.bd)")
            self.drawRightString(576, 768, "Project Overview & Architecture Documentary")

        # Footer (On all pages)
        self.setFillColor(colors.HexColor("#cbd5e1"))
        self.rect(36, 40, 540, 1, fill=True, stroke=False)
        self.setFont(MAIN_FONT, 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(36, 28, "Confidential • National University Bangladesh AI Academic Project v2.0 • 2026")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 28, page_text)

        self.restoreState()

def create_architecture_diagram() -> Drawing:
    """Draws a clean, professional vector sketch diagram of the architecture in Bengali & English."""
    d = Drawing(540, 240)
    
    # Outer container
    d.add(Rect(0, 0, 540, 240, rx=10, ry=10, fillColor=colors.HexColor("#f8fafc"), strokeColor=colors.HexColor("#cbd5e1"), strokeWidth=1))
    
    # Title Banner
    d.add(Rect(0, 210, 540, 30, rx=10, ry=10, fillColor=colors.HexColor("#0f172a"), strokeColor=None))
    d.add(String(15, 220, "সিস্টেম আর্কিটেকচার ও ডাটা ফ্লো ডায়াগ্রাম (Architecture & Data Flow)", fontName=BOLD_FONT, fontSize=11, fillColor=colors.white))

    # Box 1: User Interfaces (Top Left)
    d.add(Rect(15, 120, 115, 75, rx=6, ry=6, fillColor=colors.HexColor("#ecfdf5"), strokeColor=colors.HexColor("#059669"), strokeWidth=1.5))
    d.add(String(22, 178, "ইউজার ইন্টারফেস", fontName=BOLD_FONT, fontSize=10, fillColor=colors.HexColor("#065f46")))
    d.add(String(22, 162, "• ওয়েব চ্যাটবট (Web UI)", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(22, 148, "• মোবাইল কিউআর (QR)", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(22, 134, "• টোকেন সার্ভিস পোর্টাল", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))

    # Arrow 1 -> 2
    d.add(Line(130, 157, 155, 157, strokeColor=colors.HexColor("#059669"), strokeWidth=2))
    d.add(Polygon([155, 157, 148, 161, 148, 153], fillColor=colors.HexColor("#059669"), strokeColor=None))

    # Box 2: FastAPI Gateway & Orchestrator (Center Top)
    d.add(Rect(155, 115, 140, 85, rx=6, ry=6, fillColor=colors.HexColor("#eff6ff"), strokeColor=colors.HexColor("#2563eb"), strokeWidth=1.5))
    d.add(String(162, 185, "FastAPI গেটওয়ে ও এজেন্ট", fontName=BOLD_FONT, fontSize=10, fillColor=colors.HexColor("#1e40af")))
    d.add(String(162, 170, "• নন-ব্লকিং অ্যাসিন্ক ইঞ্জিন", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(162, 156, "• ইন্টেন্ট ও স্কিল রাউটার", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(162, 142, "• প্রি-লোডেড ফাস্ট ক্যাশ (<1ms)", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(162, 128, "• জেমিনি ৩ ফ্ল্যাশ LLM", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))

    # Arrow 2 -> 3
    d.add(Line(295, 157, 320, 157, strokeColor=colors.HexColor("#2563eb"), strokeWidth=2))
    d.add(Polygon([320, 157, 313, 161, 313, 153], fillColor=colors.HexColor("#2563eb"), strokeColor=None))

    # Box 3: MCP Tools & Client (Top Right)
    d.add(Rect(320, 120, 105, 75, rx=6, ry=6, fillColor=colors.HexColor("#faf5ff"), strokeColor=colors.HexColor("#9333ea"), strokeWidth=1.5))
    d.add(String(327, 178, "MCP সার্ভার স্যুট", fontName=BOLD_FONT, fontSize=10, fillColor=colors.HexColor("#6b21a8")))
    d.add(String(327, 162, "• token_mcp", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(327, 148, "• knowledge_mcp", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(327, 134, "• document_mcp", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))

    # Arrow 3 -> 4 (Down Right)
    d.add(Line(372, 120, 372, 95, strokeColor=colors.HexColor("#9333ea"), strokeWidth=2))
    d.add(Polygon([372, 95, 368, 102, 376, 102], fillColor=colors.HexColor("#9333ea"), strokeColor=None))

    # Box 4: Vector & Relational Database (Bottom Right)
    d.add(Rect(310, 15, 125, 80, rx=6, ry=6, fillColor=colors.HexColor("#fffbeb"), strokeColor=colors.HexColor("#d97706"), strokeWidth=1.5))
    d.add(String(317, 80, "ডাটাবেস কোর", fontName=BOLD_FONT, fontSize=10, fillColor=colors.HexColor("#92400e")))
    d.add(String(317, 65, "• ChromaDB ভেক্টর স্টোর", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(317, 51, "• SQLite টোকেন ও ক্রেডেনশিয়াল", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(317, 37, "• nu_deep_crawler.sqlite3", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(317, 23, "• AES-128 এনক্রিপ্টেড ভল্ট", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))

    # Box 5: 24/7 Autonomous Agents (Bottom Left)
    d.add(Rect(15, 15, 130, 80, rx=6, ry=6, fillColor=colors.HexColor("#fdf2f8"), strokeColor=colors.HexColor("#db2777"), strokeWidth=1.5))
    d.add(String(22, 80, "২৪/৭ স্বয়ংক্রিয় নলেজ এজেন্ট", fontName=BOLD_FONT, fontSize=10, fillColor=colors.HexColor("#9d174d")))
    d.add(String(22, 65, "• ScrapedDataAnalyzer", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(22, 51, "• KnowledgeEnricher", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(22, 37, "• KnowledgeProvenance", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(22, 23, "• JSONL অডিট স্ট্রিম ও ম্যানিফেস্ট", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))

    # Arrow 5 -> 4 (Connect Agents to DB)
    d.add(Line(145, 55, 310, 55, strokeColor=colors.HexColor("#db2777"), strokeWidth=2, strokeDashArray=[3,3]))
    d.add(Polygon([310, 55, 303, 59, 303, 51], fillColor=colors.HexColor("#db2777"), strokeColor=None))

    # Box 6: Staff Solvers & Admin Portal (Bottom Center)
    d.add(Rect(155, 15, 140, 80, rx=6, ry=6, fillColor=colors.HexColor("#f1f5f9"), strokeColor=colors.HexColor("#475569"), strokeWidth=1.5))
    d.add(String(162, 80, "দাপ্তরিক সলভার ও অ্যাডমিন", fontName=BOLD_FONT, fontSize=10, fillColor=colors.HexColor("#0f172a")))
    d.add(String(162, 65, "• আইসিটি, পরীক্ষা ও রেজিস্ট্রেশন ডেস্ক", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(162, 51, "• টোকেন সমাধান ও রেজোলিউশন", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(162, 37, "• সেলফ-লার্নিং ভেক্টর ফিডব্যাক", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(162, 23, "• RBAC রোল ম্যানেজমেন্ট", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))

    # Box 7: External nu.ac.bd Web Portals (Right Side)
    d.add(Rect(445, 45, 85, 150, rx=6, ry=6, fillColor=colors.HexColor("#f0fdf4"), strokeColor=colors.HexColor("#16a34a"), strokeWidth=1.5))
    d.add(String(450, 180, "জাতীয় বিশ্ববিদ্যালয়", fontName=BOLD_FONT, fontSize=9, fillColor=colors.HexColor("#166534")))
    d.add(String(450, 168, "অফিসিয়াল পোর্টাল", fontName=BOLD_FONT, fontSize=9, fillColor=colors.HexColor("#166534")))
    d.add(String(450, 145, "• nu.ac.bd", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(450, 130, "• app1.nu.edu.bd", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(450, 115, "• results.nu.ac.bd", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(450, 100, "• ems.nu.ac.bd", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(450, 85, "• সোনালী সেবা পেমেন্ট", fontName=MAIN_FONT, fontSize=8, fillColor=colors.HexColor("#1e293b")))
    d.add(String(450, 60, "[ক্রলার ও স্ক্র্যাপার]", fontName=BOLD_FONT, fontSize=8, fillColor=colors.HexColor("#166534")))

    # Connect Portals to Agents
    d.add(Line(445, 100, 435, 100, strokeColor=colors.HexColor("#16a34a"), strokeWidth=1.5))

    return d

def build_pdf_document():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF_PATH),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=44,
        bottomMargin=44
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "CoverTitle",
        fontName=BOLD_FONT,
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#065f46"),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        fontName=MAIN_FONT,
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#334155"),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        "Heading1_BN",
        fontName=BOLD_FONT,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_BN",
        fontName=BOLD_FONT,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#047857"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_BN",
        fontName=MAIN_FONT,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        "Callout_BN",
        fontName=MAIN_FONT,
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#065f46")
    )

    code_style = ParagraphStyle(
        "Code_Style",
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        fontName=BOLD_FONT,
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        fontName=MAIN_FONT,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # ==================== PAGE 1: TITLE & EXECUTIVE SUMMARY ====================
    
    # Top Header Banner
    header_table = Table(
        [
            [
                Paragraph("<b>NATIONAL UNIVERSITY BANGLADESH</b><br/><font size='8' color='#059669'>জাতীয় বিশ্ববিদ্যালয় • শিক্ষা ও তথ্য প্রযুক্তি বিভাগ</font>", ParagraphStyle("HdrLogo", fontName=BOLD_FONT, fontSize=12, leading=16, textColor=colors.HexColor("#065f46"))),
                Paragraph("<b>OFFICIAL DOCUMENTARY</b><br/><font size='8' color='#64748b'>Project Overview & Tech Architecture<br/>Version 2.0 • Production Ready</font>", ParagraphStyle("HdrRight", fontName=BOLD_FONT, fontSize=9, leading=12, textColor=colors.HexColor("#0f172a"), alignment=2))
            ]
        ],
        colWidths=[300, 240]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#059669"), spaceAfter=14))

    story.append(Paragraph("জাতীয় বিশ্ববিদ্যালয় AI অ্যাসিস্ট্যান্ট ও স্মার্ট সাপোর্ট প্ল্যাটফর্ম", title_style))
    story.append(Paragraph("<b>National University AI Academic Assistant, Support Token Service & 24/7 Autonomous Knowledge Ecosystem</b>", subtitle_style))

    # Executive Summary Card
    summary_card = Table(
        [
            [
                Paragraph("<b>🌟 প্রজেক্ট সারসংক্ষেপ (Executive Overview):</b><br/>"
                          "জাতীয় বিশ্ববিদ্যালয় (nu.ac.bd) বাংলাদেশের সর্ববৃহৎ উচ্চশিক্ষা প্রতিষ্ঠান, যার অধীনে ২,২০০+ অধিভুক্ত কলেজে ৩০ লক্ষাধিক শিক্ষার্থী অধ্যয়নরত। শিক্ষার্থীদের ভর্তি, পরীক্ষার সংশোধিত রুটিন, ফরম পূরণ (EMS পোর্টাল), ফলাফল, মার্কশিট ও সনদ উত্তোলনের সময় হাজার হাজার জিজ্ঞাসার সৃষ্টি হয়।<br/><br/>"
                          "এই প্ল্যাটফর্মটি একটি <b>উৎপাদন-মানসম্পন্ন (Production-Grade) AI ইকোসিস্টেম</b>, যা <b>Google Gemini 3 Flash</b>, <b>ChromaDB ভেক্টর স্টোর</b>, <b>MCP (Model Context Protocol) টুলস</b>, <b>AES-128 এনক্রিপ্টেড ক্রেডেনশিয়াল ভল্ট</b> এবং <b>২৪/৭ স্বয়ংক্রিয় নলেজ এনরিচমেন্ট এজেন্টের</b> সমন্বয়ে শিক্ষার্থীদের তাৎক্ষণিক নির্ভুল তথ্য ও সাপোর্ট টিকেট সমাধান প্রদান করে।", callout_style)
            ]
        ],
        colWidths=[540]
    )
    summary_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#ecfdf5")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#a7f3d0")),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(summary_card)
    story.append(Spacer(1, 10))

    # Key Objectives in 3 Cards
    obj_table = Table(
        [
            [
                Paragraph("<b>⚡ সাব-মিলিমিটার রেসপন্স</b><br/><font size='8' color='#475569'>সাধারণ জিজ্ঞাসা (hi, ভর্তি, রুটিন, রেজাল্ট) 0.001 সেকেন্ডের মধ্যে প্রি-লোডেড ক্যাশ থেকে সরাসরি প্রদান।</font>", ParagraphStyle("Obj1", fontName=MAIN_FONT, fontSize=8.5, leading=12, textColor=colors.HexColor("#065f46"))),
                Paragraph("<b>🎫 অটোমিক সাপোর্ট টোকেন</b><br/><font size='8' color='#475569'>EMS, ফরম পূরণ ও সনদের সমস্যার জন্য NU-2026-XXXXXX ট্র্যাকিং নম্বর সহ সমাধান ডেস্ক।</font>", ParagraphStyle("Obj2", fontName=MAIN_FONT, fontSize=8.5, leading=12, textColor=colors.HexColor("#92400e"))),
                Paragraph("<b>🤖 ২৪/৭ স্বয়ংক্রিয় এজেন্ট</b><br/><font size='8' color='#475569'>প্রতি ১০ মিনিটে নতুন নোটিশ ক্রল করে প্রশ্নোত্তর তৈরি ও ভেক্টর ডাটাবেসে রিয়েল-টাইম আপডেট।</font>", ParagraphStyle("Obj3", fontName=MAIN_FONT, fontSize=8.5, leading=12, textColor=colors.HexColor("#1e40af")))
            ]
        ],
        colWidths=[175, 175, 175]
    )
    obj_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (0,0), 1, colors.HexColor("#bbf7d0")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#fffbeb")),
        ('BOX', (1,0), (1,0), 1, colors.HexColor("#fef08a")),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor("#eff6ff")),
        ('BOX', (2,0), (2,0), 1, colors.HexColor("#bfdbfe")),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(obj_table)
    story.append(Spacer(1, 14))

    # Architecture Sketch Diagram
    story.append(Paragraph("১. পূর্ণাঙ্গ সিস্টেম আর্কিটেকচার স্কেচ ডায়াগ্রাম (System Architecture Sketch)", h1_style))
    story.append(Paragraph("নিচের স্কেচ ডায়াগ্রামে শিক্ষার্থী থেকে শুরু করে এআই অর্কেস্ট্রেটর, এমসিপি সার্ভার, ডাটাবেস এবং ২৪/৭ এজেন্টের ডাটা প্রবাহ প্রদর্শিত হলো:", body_style))
    story.append(Spacer(1, 4))
    story.append(create_architecture_diagram())
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # ==================== PAGE 2: TECH STACK & WORKING MECHANISMS ====================
    story.append(Paragraph("২. ব্যবহৃত প্রযুক্তি স্ট্যাক ও তাদের কার্যপ্রণালী (Technology Stack & Working Principles)", h1_style))
    story.append(Paragraph("প্ল্যাটফর্মটির প্রতিটি স্তর আধুনিক, নিরাপদ এবং স্কেলেবল ওপেন স্ট্যান্ডার্ড আর্কিটেকচারের উপর নির্মিত:", body_style))
    story.append(Spacer(1, 4))

    tech_data = [
        [
            Paragraph("টেকনোলজি (Technology)", table_header_style),
            Paragraph("সংস্করণ / উপাদান", table_header_style),
            Paragraph("ভূমিকা ও কার্যপ্রণালী (Role & Technical Mechanism)", table_header_style)
        ],
        [
            Paragraph("<b>FastAPI Backend</b>", table_cell_style),
            Paragraph("v0.115+ (Python 3.13)", table_cell_style),
            Paragraph("নন-ব্লকিং অ্যাসিনক্রোনাস ওয়েব গেটওয়ে। <font color='#047857'>asyncio.to_thread</font> ব্যবহার করে GenAI ও SQLite ডিস্ক I/O পৃথক থ্রেডে প্রসেস করে ইভেন্ট লুপকে সর্বোচ্চ গতিশীল রাখে।", table_cell_style)
        ],
        [
            Paragraph("<b>Google Gemini 3 Flash</b>", table_cell_style),
            Paragraph("gemini-3-flash-preview<br/>gemini-3.1-flash-lite", table_cell_style),
            Paragraph("উন্নত বাইলিঙ্গুয়াল জেনারেটিভ AI কোর। সাব-সেকেন্ডে বাংলা ও ইংরেজি প্রশ্ন বুঝে অফিসিয়াল রেফারেন্স এবং প্রাসঙ্গিক লিংক সহ উত্তর তৈরি করে।", table_cell_style)
        ],
        [
            Paragraph("<b>ChromaDB & Embeddings</b>", table_cell_style),
            Paragraph("Chroma Vector Store<br/>gemini-embedding-001", table_cell_style),
            Paragraph("অফিসিয়াল নোটিশ ও সমাধানের জন্য সেমান্টিক ভেক্টর সার্চ ইঞ্জিন। রেট লিমিট সুরক্ষা হিসেবে তাৎক্ষণিক রেজিলিয়েন্ট সিউডো-ভেক্টর ব্যাকআপ ব্যবস্থা যুক্ত।", table_cell_style)
        ],
        [
            Paragraph("<b>MCP Protocol Suite</b>", table_cell_style),
            Paragraph("Anthropic / Antigravity<br/>5 Dedicated MCP Servers", table_cell_style),
            Paragraph("মডেলের সাথে ডাটাবেস ও টুলের সরাসরি সংযোগ। <font color='#6b21a8'>token_mcp, knowledge_mcp, document_mcp, credential_mcp, enrichment_mcp</font> টুলসেট পরিচালিত করে।", table_cell_style)
        ],
        [
            Paragraph("<b>SQLite Relational Core</b>", table_cell_style),
            Paragraph("WAL Mode Enabled<br/>4 Isolated DBs", table_cell_style),
            Paragraph("সাপোর্ট টোকেন, ক্রেডেনশিয়াল, ক্রলার পেজ এবং অডিট ট্রেইল সংরক্ষণের ACID রিলেশনাল ইঞ্জিন। হাই-থ্রুপুট রাইটিংয়ের জন্য WAL মোডে কার্যকর।", table_cell_style)
        ],
        [
            Paragraph("<b>Fernet AES-128 Encryption</b>", table_cell_style),
            Paragraph("Cryptography Vault<br/>PBKDF2-HMAC-SHA256", table_cell_style),
            Paragraph("EMS এবং স্টুডেন্ট পোর্টালের লগইন পাসওয়ার্ড সুরক্ষায় CBC মোডে AES-128 ও HMAC ইন্টিগ্রিটি হ্যাশিং। ডাটাবেসে বা লগ ফাইলে কখনো প্লেইনটেক্সট সংরক্ষিত হয় না।", table_cell_style)
        ],
        [
            Paragraph("<b>Preloaded Instant Engine</b>", table_cell_style),
            Paragraph("In-Memory Keyword Trie<br/>Latency: 0.018 ms", table_cell_style),
            Paragraph("সাধারণ সম্ভাষণ (Greetings), ভর্তি যোগ্যতা, পরীক্ষার রুটিন এবং রেজাল্ট দেখার এসএমএস কোড মেমোরিতে প্রিলোড করে মাত্র ১৮ মাইক্রোসেকেন্ডে রেসপন্স প্রদান।", table_cell_style)
        ],
        [
            Paragraph("<b>Responsive Web UI</b>", table_cell_style),
            Paragraph("TailwindCSS + Vanilla JS<br/>Mobile-First QR", table_cell_style),
            Paragraph("কোনো ফ্রেমওয়ার্ক ওভারহেড ছাড়াই দ্রুতগতির ডার্ক/লাইট ইন্টারফেস। মোবাইল ক্যামেরা দিয়ে স্ক্যান করলেই তাৎক্ষণিক চ্যাটবট সক্রিয় হয়।", table_cell_style)
        ]
    ]

    tech_table = Table(tech_data, colWidths=[110, 100, 330])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("৩. ২৪/৭ স্বয়ংক্রিয় নলেজ এনরিচমেন্ট মাল্টি-এজেন্ট সিস্টেম", h1_style))
    story.append(Paragraph("প্ল্যাটফর্মটিতে ৩টি বিশেষায়িত স্বায়ত্তশাসিত এজেন্ট সার্বক্ষণিক কাজ করে চলেছে:", body_style))

    agent_data = [
        [
            Paragraph("এজেন্টের নাম (Agent)", table_header_style),
            Paragraph("কাজের ক্ষেত্র (Responsibilities)", table_header_style),
            Paragraph("আউটপুট স্ট্যান্ডার্ড (Output)", table_header_style)
        ],
        [
            Paragraph("<b>ScrapedDataAnalyzerAgent</b>", table_cell_style),
            Paragraph("নতুন ক্রল করা নোটিশ ও পিডিএফ বিশ্লেষণ করে ডিগ্রি, শিক্ষাবর্ষ, আবেদনের সময়সীমা, ফি ও গুরুত্বপূর্ণ লিংক আলাদা করে এবং বাংলা-ইংরেজি প্রশ্নোত্তর তৈরি করে।", table_cell_style),
            Paragraph("JSON Entities & QA Pairs", table_cell_style)
        ],
        [
            Paragraph("<b>KnowledgeEnricherAgent</b>", table_cell_style),
            Paragraph("তৈরিকৃত প্রশ্নোত্তর ও অফিসিয়াল সামারি ChromaDB ভেক্টর ডাটাবেসে ইনজেস্ট করে এবং তাৎক্ষণিক উত্তরের জন্য মেমোরি ক্যাশে যুক্ত করে।", table_cell_style),
            Paragraph("Chroma Vector Ingestion & SQLite Log", table_cell_style)
        ],
        [
            Paragraph("<b>KnowledgeProvenanceAgent</b>", table_cell_style),
            Paragraph("প্রতিটি পরিবর্তনের অডিট রেকর্ড সংরক্ষণ করে, যাতে অন্য যেকোনো AI এজেন্ট (Claude, Codex, Subagents) এই আপডেট পড়ে স্বয়ংক্রিয়ভাবে কাজ চালিয়ে যেতে পারে।", table_cell_style),
            Paragraph("data/knowledge_updates.jsonl & knowledge_manifest.json (RFC 8259)", table_cell_style)
        ]
    ]

    agent_table = Table(agent_data, colWidths=[140, 260, 140])
    agent_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4338ca")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(agent_table)

    story.append(PageBreak())

    # ==================== PAGE 3: 0-LEVEL USER GUIDE & STEP-BY-STEP ====================
    story.append(Paragraph("৪. ০-লেভেল সাধারণ শিক্ষার্থী ও কর্মচারীদের ব্যবহার নির্দেশিকা (0-Level User Guide)", h1_style))
    story.append(Paragraph("যেকোনো সাধারণ ব্যবহারকারী কোনো প্রশিক্ষণ ছাড়াই সহজে প্ল্যাটফর্মটি ব্যবহার করতে পারবেন:", body_style))
    story.append(Spacer(1, 4))

    # User steps in styled boxes
    steps_data = [
        [
            Paragraph("<b>ধাপ ১: এআই চ্যাটবটে প্রশ্ন করা</b><br/>"
                      "• যেকোনো ভাষায় প্রশ্ন লিখুন (যেমন: <i>'অনার্স ভর্তি কবে শুরু হবে?'</i> অথবা <i>'EMS পাসওয়ার্ড ভুলে গেছি'</i>)।<br/>"
                      "• বটের উত্তরে অফিসিয়াল সার্কুলার লিংক ও সবুজ ভেরিফায়েড ব্যাজ প্রদর্শিত হবে।", table_cell_style),
            Paragraph("<b>ধাপ ২: সাপোর্ট টোকেন আবেদন</b><br/>"
                      "• জটিল বা ব্যক্তিগত সমস্যার ক্ষেত্রে <b>'Token Service'</b> বাটনে ক্লিক করুন।<br/>"
                      "• নির্দিষ্ট সেবা নির্বাচন করে নাম, ফোন ও রেজিস্ট্রেশন নম্বর দিয়ে সাবমিট করুন।<br/>"
                      "• সাথে সাথে একটি ট্র্যাকিং নম্বর পাবেন (যেমন: <b>NU-2026-000140</b>)।", table_cell_style)
        ],
        [
            Paragraph("<b>ধাপ ৩: লাইভ স্ট্যাটাস ট্র্যাকিং</b><br/>"
                      "• <b>'Check Token'</b> বাটনে ট্র্যাকিং আইডি লিখে স্ট্যাটাস দেখুন।<br/>"
                      "• স্ট্যাটাস পরিবর্তন: <font color='#d97706'>PENDING</font> ➔ <font color='#2563eb'>PROCESSING</font> ➔ <font color='#059669'>SOLVED</font>।<br/>"
                      "• সমাধান সম্পন্ন হলে অফিসিয়াল পিডিএফ রেজোলিউশন ডাউনলোড করুন।", table_cell_style),
            Paragraph("<b>ধাপ ৪: মোবাইল কিউআর এক্সেস</b><br/>"
                      "• <b>'Mobile QR'</b> বাটনে ক্লিক করলে স্ক্রিনে কিউআর কোড ভেসে উঠবে।<br/>"
                      "• স্মার্টফোন ক্যামেরা দিয়ে স্ক্যান করলেই কোনো অ্যাপ ইন্সটল ছাড়াই মোবাইলে সম্পূর্ণ চ্যাটবট সক্রিয় হবে।", table_cell_style)
        ]
    ]

    steps_table = Table(steps_data, colWidths=[265, 265])
    steps_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (0,0), 1, colors.HexColor("#86efac")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#fffbeb")),
        ('BOX', (1,0), (1,0), 1, colors.HexColor("#fde047")),
        ('BACKGROUND', (0,1), (0,1), colors.HexColor("#faf5ff")),
        ('BOX', (0,1), (0,1), 1, colors.HexColor("#d8b4fe")),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor("#eff6ff")),
        ('BOX', (1,1), (1,1), 1, colors.HexColor("#93c5fd")),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(steps_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("৫. সাপোর্ট টোকেন সেবাসমূহ ও দাপ্তরিক সলভার বিভাগ (Service Categories & Solvers)", h1_style))
    
    service_data = [
        [Paragraph("সার্ভিস কোড", table_header_style), Paragraph("সেবার নাম (Service Name)", table_header_style), Paragraph("দায়িত্বপ্রাপ্ত দপ্তর (Department Desk)", table_header_style), Paragraph("সমাধানের সময়সীমা", table_header_style)],
        [Paragraph("<b>EMS</b>", table_cell_style), Paragraph("ইএমএস স্টুডেন্ট পোর্টাল পাসওয়ার্ড ও অ্যাকাউন্ট সমস্যা", table_cell_style), Paragraph("আইসিটি সাপোর্ট ডেস্ক (ICT Desk)", table_cell_style), Paragraph("২৪-৪৮ ঘণ্টা", table_cell_style)],
        [Paragraph("<b>FORM_FILLUP</b>", table_cell_style), Paragraph("পরীক্ষার ফরম পূরণ ও কলেজ ফি ভেরিফিকেশন", table_cell_style), Paragraph("পরীক্ষা নিয়ন্ত্রণ শাখা", table_cell_style), Paragraph("১২-২৪ ঘণ্টা", table_cell_style)],
        [Paragraph("<b>RESCRUTINY</b>", table_cell_style), Paragraph("ফলাফল পুনর্নিরীক্ষণ / বোর্ড চ্যালেঞ্জ আবেদন ট্র্যাকিং", table_cell_style), Paragraph("ফলাফল ও মূল্যায়ন শাখা", table_cell_style), Paragraph("৩-৭ কার্যদিবস", table_cell_style)],
        [Paragraph("<b>CERTIFICATE</b>", table_cell_style), Paragraph("মূল সনদ ও সাময়িক সনদ উত্তোলন ও যাচাইকরণ", table_cell_style), Paragraph("সনদপত্র শাখা (Certificate Wing)", table_cell_style), Paragraph("২-৫ কার্যদিবস", table_cell_style)],
        [Paragraph("<b>MARKSHEET</b>", table_cell_style), Paragraph("একাডেমিক ট্রান্সক্রিপ্ট ও নম্বরপত্র সংশোধন", table_cell_style), Paragraph("রেজিস্ট্রার দপ্তর", table_cell_style), Paragraph("২-৪ কার্যদিবস", table_cell_style)],
        [Paragraph("<b>TC</b>", table_cell_style), Paragraph("কলেজ ট্রান্সফার ও মাইগ্রেশন ছাড়পত্র", table_cell_style), Paragraph("কলেজ পরিদর্শন দপ্তর", table_cell_style), Paragraph("৩-৫ কার্যদিবস", table_cell_style)],
        [Paragraph("<b>CORRECTION</b>", table_cell_style), Paragraph("নাম, বয়স, রেজিস্ট্রেশন বা বিষয় সংশোধন", table_cell_style), Paragraph("রেজিস্ট্রেশন ও সংশোধন সেল", table_cell_style), Paragraph("৫-১০ কার্যদিবস", table_cell_style)]
    ]

    serv_table = Table(service_data, colWidths=[80, 210, 160, 90])
    serv_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#065f46")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(serv_table)
    story.append(Spacer(1, 14))

    # Future Roadmap
    story.append(Paragraph("৬. ভবিষ্যৎ কৌশলগত রোডম্যাপ (Future Expansion & Strategic Roadmap)", h1_style))

    roadmap_data = [
        [Paragraph("পর্যায় (Phase)", table_header_style), Paragraph("সময়কাল", table_header_style), Paragraph("পরিকল্পিত ফিচার ও সম্প্রসারণ (Features & Capabilities)", table_header_style)],
        [Paragraph("<b>Phase 1 (Completed)</b>", table_cell_style), Paragraph("Q3 2026", table_cell_style), Paragraph("পূর্ণাঙ্গ RAG চ্যাটবট, সাব-মিলিমিটার প্রিলোডিং, টোকেন সার্ভিস, MCP সার্ভার এবং ২৪/৭ নলেজ এনরিচমেন্ট।", table_cell_style)],
        [Paragraph("<b>Phase 2 (Upcoming)</b>", table_cell_style), Paragraph("Q4 2026", table_cell_style), Paragraph("<b>বাংলা ভয়েস এআই অ্যাসিস্ট্যান্ট:</b> গ্রামীণ ও দৃষ্টিপ্রতিবন্ধী শিক্ষার্থীদের জন্য রিয়েল-টাইম বাইডিরেকশনাল ভয়েস চ্যাট।", table_cell_style)],
        [Paragraph("<b>Phase 3</b>", table_cell_style), Paragraph("Q1 2027", table_cell_style), Paragraph("<b>হোয়াটসঅ্যাপ ও এসএমএস গেটওয়ে:</b> টোকেন সমাধান বা জরুরি নোটিশ প্রকাশের সাথে সাথে শিক্ষার্থীর মোবাইলে অটোমেটিক অ্যালার্ট।", table_cell_style)],
        [Paragraph("<b>Phase 4</b>", table_cell_style), Paragraph("Q2 2027", table_cell_style), Paragraph("<b>রোবোটিক ডিজিটাল সনদপত্র সরবরাহ:</b> কেন্দ্রীয় ডাটাবেস ভেরিফিকেশন সহ সরাসরি ডিজিটাল স্বাক্ষরিত ই-সার্টিফিকেট ডাউনলোড।", table_cell_style)],
        [Paragraph("<b>Phase 5</b>", table_cell_style), Paragraph("Q3 2027", table_cell_style), Paragraph("<b>বিভাগীয় ফেডারেটেড সাব-এজেন্ট:</b> ঢাকা, চট্টগ্রাম, রাজশাহী সহ সকল বিভাগীয় আঞ্চলিক কেন্দ্রের জন্য ডেডিকেটেড সাব-এজেন্ট ক্লাস্টার।", table_cell_style)]
    ]

    road_table = Table(roadmap_data, colWidths=[120, 70, 350])
    road_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(road_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] PDF successfully generated at: {OUTPUT_PDF_PATH}")

if __name__ == "__main__":
    build_pdf_document()
