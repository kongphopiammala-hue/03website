# -*- coding: utf-8 -*-
"""
Script to generate a comprehensive, beautifully formatted Word document (.docx)
User Manual for Primal Haven Game Database & Wiki.
"""

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def create_manual():
    doc = Document()

    # Page setup (A4)
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base styles and colors
    COLOR_PRIMARY = RGBColor(217, 119, 6)     # Amber/Orange #D97706
    COLOR_DARK = RGBColor(30, 41, 59)         # Slate Dark #1E293B
    COLOR_SECONDARY = RGBColor(16, 185, 129)  # Emerald #10B981
    COLOR_TEXT = RGBColor(51, 65, 85)         # Slate Text #334155
    COLOR_MUTED = RGBColor(100, 116, 139)     # Slate Muted #64748B

    # Helper: Set font for paragraph or run
    def set_font(run, font_name="TH Sarabun New", size_pt=15, bold=False, italic=False, color=COLOR_TEXT):
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        run.font.color.rgb = color
        
        # XML level font mapping for East Asian / Complex Script
        rPr = run._r.get_or_add_rPr()
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
        rPr.append(rFonts)

    def add_styled_paragraph(doc, text="", style="Normal", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if text:
            r = p.add_run(text)
            set_font(r, font_name="TH Sarabun New", size_pt=15, color=COLOR_TEXT)
        return p

    def add_h1(doc, text, icon=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        full_text = f"{icon} {text}" if icon else text
        r = p.add_run(full_text)
        set_font(r, font_name="TH Sarabun New", size_pt=20, bold=True, color=COLOR_PRIMARY)
        return p

    def add_h2(doc, text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_font(r, font_name="TH Sarabun New", size_pt=17, bold=True, color=COLOR_DARK)
        return p

    def add_callout(doc, title, text, icon="💡"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.27)
        
        # Light warm background & left thick border
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="FFFBEB"/>')
        cell._tc.get_or_add_tcPr().append(shading)
        
        tcBorders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="none"/>
                <w:left w:val="single" w:sz="24" w:space="0" w:color="D97706"/>
                <w:bottom w:val="none"/>
                <w:right w:val="none"/>
            </w:tcBorders>
        ''')
        cell._tc.get_or_add_tcPr().append(tcBorders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        r_title = p.add_run(f"{icon} {title}\n")
        set_font(r_title, font_name="TH Sarabun New", size_pt=15, bold=True, color=COLOR_PRIMARY)
        
        r_text = p.add_run(text)
        set_font(r_text, font_name="TH Sarabun New", size_pt=14, color=COLOR_DARK)
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def style_table(table, header_bg="1E293B", alt_bg="F8FAFC"):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, row in enumerate(table.rows):
            # Prevent row break across pages
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            
            # Header row repeat
            if i == 0:
                trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

            for cell in row.cells:
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                tcPr = cell._tc.get_or_add_tcPr()
                
                # Shading
                if i == 0:
                    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{header_bg}"/>')
                elif i % 2 == 1:
                    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{alt_bg}"/>')
                else:
                    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="FFFFFF"/>')
                tcPr.append(shd)

                # Borders
                borders = parse_xml(f'''
                    <w:tcBorders {nsdecls("w")}>
                        <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                        <w:left w:val="none"/>
                        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                        <w:right w:val="none"/>
                    </w:tcBorders>
                ''')
                tcPr.append(borders)

    # -------------------------------------------------------------
    # 1. COVER PAGE / HEADER
    # -------------------------------------------------------------
    p_badge = add_styled_paragraph(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=12)
    r_badge = p_badge.add_run("🔥 PRIMAL LIFE SIMULATOR DATABASE & WIKI")
    set_font(r_badge, font_name="TH Sarabun New", size_pt=14, bold=True, color=COLOR_PRIMARY)

    p_title = add_styled_paragraph(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=8)
    r_title = p_title.add_run("คู่มือการใช้งานเว็บไซต์ฐานข้อมูลเกม\n\"ไพรวัลย์ บรรพกาล: วิถีชีวิตยุคหิน\"")
    set_font(r_title, font_name="TH Sarabun New", size_pt=28, bold=True, color=COLOR_DARK)

    p_sub = add_styled_paragraph(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=24)
    r_sub = p_sub.add_run("Primal Haven: Echoes of Stone — User Manual & Game Guide\nฉบับสมบูรณ์สำหรับผู้เล่นและผู้ดูแลระบบ")
    set_font(r_sub, font_name="TH Sarabun New", size_pt=16, italic=True, color=COLOR_MUTED)

    # Document Metadata Box
    meta_tbl = doc.add_table(rows=4, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("เวอร์ชันเกม / ระบบ:", "v1.0.4 Early Access"),
        ("แพลตฟอร์มที่รองรับ:", "Web Browser (Desktop & Mobile Responsive)"),
        ("ตำแหน่งไฟล์ในระบบ:", "c:\\งาน01\\ (Local Workspace)"),
        ("วันที่จัดทำเอกสาร:", "พฤศจิกายน 2026")
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        row = meta_tbl.rows[row_idx]
        c1, c2 = row.cells[0], row.cells[1]
        c1.width = Inches(2.2)
        c2.width = Inches(4.0)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(3)
        p1.paragraph_format.space_after = Pt(3)
        r1 = p1.add_run(k)
        set_font(r1, font_name="TH Sarabun New", size_pt=14, bold=True, color=COLOR_DARK)
        
        p2 = c2.paragraphs[0]
        p2.paragraph_format.space_before = Pt(3)
        p2.paragraph_format.space_after = Pt(3)
        r2 = p2.add_run(v)
        set_font(r2, font_name="TH Sarabun New", size_pt=14, color=COLOR_TEXT)
        
    style_table(meta_tbl, header_bg="E2E8F0", alt_bg="F1F5F9")
    doc.add_page_break()

    # -------------------------------------------------------------
    # 2. TABLE OF CONTENTS / SUMMARY
    # -------------------------------------------------------------
    add_h1(doc, "สารบัญเนื้อหา (Table of Contents)", "📑")
    toc_items = [
        ("บทที่ 1: แนะนำเว็บไซต์และวิธีการเข้าใช้งาน", "วิธีการเปิดเว็บผ่าน Localhost และการเปิดไฟล์แบบออฟไลน์"),
        ("บทที่ 2: โครงสร้างและส่วนติดต่อผู้ใช้ (UI Overview)", "แถบนำทาง ช่องค้นหาด่วน และการสลับธีมแสดงผล"),
        ("บทที่ 3: คู่มือหมวดหมู่ข้อมูลเกมทั้ง 5 ด้าน", "การเกษตร, สัตว์โบราณ, คราฟต์สิ่งของ, ชนเผ่า และอาหาร"),
        ("บทที่ 4: การใช้งานเครื่องมือพิเศษ (Interactive Tools)", "เครื่องคำนวณผลผลิต (Crop Calculator) และตัวช่วยค้นหาของขวัญ"),
        ("บทที่ 5: แผนที่ดินแดนบรรพกาล (Interactive Map)", "สำรวจโซนต่างๆ ระดับเลเวล และจุดเก็บเกี่ยวทรัพยากร"),
        ("บทที่ 6: คำแนะนำสำหรับผู้พัฒนาและอัปเดตข้อมูล", "โครงสร้างโค้ดและการเพิ่มข้อมูลไอเทมใหม่ในอนาคต")
    ]

    for title, desc in toc_items:
        p = add_styled_paragraph(doc, space_before=3, space_after=4)
        r1 = p.add_run(f"• {title} — ")
        set_font(r1, font_name="TH Sarabun New", size_pt=15, bold=True, color=COLOR_PRIMARY)
        r2 = p.add_run(desc)
        set_font(r2, font_name="TH Sarabun New", size_pt=15, color=COLOR_TEXT)

    # -------------------------------------------------------------
    # บทที่ 1
    # -------------------------------------------------------------
    add_h1(doc, "บทที่ 1: แนะนำเว็บไซต์และวิธีการเข้าใช้งาน", "🚀")
    
    p = add_styled_paragraph(doc)
    p.add_run(
        "เว็บไซต์ฐานข้อมูลเกม \"ไพรวัลย์ บรรพกาล: วิถีชีวิตยุคหิน\" (Primal Haven Database & Wiki) "
        "ถูกออกแบบขึ้นเพื่อให้ผู้เล่นสามารถค้นหาข้อมูลเชิงลึก วางแผนการทำฟาร์ม คำนวณกำไร และศึกษาอุปนิสัยของชาวเผ่า "
        "โดยระบบถูกสร้างขึ้นด้วยเทคโนโลยีเว็บมาตรฐานที่โหลดเร็ว ไม่พึ่งพาเซิร์ฟเวอร์ภายนอกที่ซับซ้อน และรองรับการเปิดใช้งานได้ทุกอุปกรณ์"
    )

    add_h2(doc, "1.1 วิธีการเปิดเข้าใช้งานเว็บไซต์")
    p = add_styled_paragraph(doc)
    p.add_run("ผู้ใช้งานสามารถเปิดเข้าดูเว็บไซต์ได้ 2 วิธีหลักดังนี้:\n")
    p.add_run("1. เปิดผ่าน Local Web Server (แนะนำ):\n").bold = True
    p.add_run("   • เปิดโปรแกรมเว็บเบราว์เซอร์ เช่น Google Chrome, Microsoft Edge หรือ Safari\n")
    p.add_run("   • พิมพ์ที่อยู่ URL ในแถบที่อยู่: ")
    r_url = p.add_run("http://localhost:8080\n")
    set_font(r_url, font_name="TH Sarabun New", size_pt=15, bold=True, color=COLOR_PRIMARY)
    p.add_run("   • หน้าต่างเว็บไซต์จะพร้อมใช้งานทันทีพร้อมฟังก์ชันการทำงานครบ 100%\n\n")

    p.add_run("2. เปิดไฟล์ HTML โดยตรง (Offline Mode):\n").bold = True
    p.add_run("   • ไปที่โฟลเดอร์โครงการ: ")
    r_path = p.add_run("c:\\งาน01\\\n")
    set_font(r_path, font_name="TH Sarabun New", size_pt=15, bold=True, color=COLOR_DARK)
    p.add_run("   • ดับเบิลคลิกที่ไฟล์ ")
    p.add_run("index.html").bold = True
    p.add_run(" เพื่อเปิดหน้าเว็บได้ทันทีโดยไม่ต้องเชื่อมต่ออินเทอร์เน็ต")

    add_h2(doc, "1.2 โครงสร้างไฟล์ในโฟลเดอร์ระบบ")
    file_tbl = doc.add_table(rows=5, cols=3)
    file_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["ชื่อไฟล์", "ประเภท", "หน้าที่การทำงาน"]
    for idx, h in enumerate(headers):
        cell = file_tbl.cell(0, idx)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        set_font(r, font_name="TH Sarabun New", size_pt=14, bold=True, color=RGBColor(255, 255, 255))

    file_rows = [
        ("index.html", "HTML Document", "โครงสร้างหน้าเว็บหลัก แถบเมนู ป้ายสถิติ หน้าต่าง Modal และป๊อปอัป"),
        ("styles.css", "CSS Stylesheet", "ชุดคำสั่งตกแต่งธีมดึกดำบรรพ์ (Stone-Age) เอฟเฟกต์แสงไฟ และระบบ Responsive"),
        ("data.js", "JavaScript Data", "คลังข้อมูลดิบทั้งหมดของเกม (พืช, สัตว์, คราฟต์, NPC, อาหาร, แผนที่)"),
        ("app.js", "JavaScript Logic", "ตรรกะระบบค้นหา ตัวกรอง การสลับแท็บ เครื่องคำนวณผลผลิต และระบบบันทึก")
    ]
    for row_idx, (fn, ft, fd) in enumerate(file_rows, start=1):
        row = file_tbl.rows[row_idx]
        for col_idx, text in enumerate([fn, ft, fd]):
            p = row.cells[col_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(text)
            set_font(r, font_name="TH Sarabun New", size_pt=13, color=COLOR_TEXT)
            if col_idx == 0:
                r.bold = True

    style_table(file_tbl)

    add_callout(doc, "ข้อแนะนำสำหรับการใช้งานบนสมาร์ตโฟนและแท็บเล็ต", 
                "เว็บไซต์ได้รับการปรับแต่งระบบ Responsive Layout เพื่อให้สามารถเปิดใช้งานบนโทรศัพท์มือถือ "
                "โดยผู้เล่นสามารถเปิดดูข้อมูลควบคู่ไปขณะกำลังเล่นเกมบนคอมพิวเตอร์หรือเครื่องคอนโซลได้อย่างสะดวกสบาย")

    # -------------------------------------------------------------
    # บทที่ 2
    # -------------------------------------------------------------
    add_h1(doc, "บทที่ 2: โครงสร้างและส่วนติดต่อผู้ใช้ (User Interface)", "🖥️")
    
    p = add_styled_paragraph(doc)
    p.add_run("หน้าต่างเว็บไซต์ได้รับการจัดวางอย่างเป็นสัดส่วน โดยแบ่งออกเป็น 5 ส่วนสำคัญ:")

    add_h2(doc, "2.1 แถบส่วนหัวด้านบน (Header Bar)")
    p = add_styled_paragraph(doc)
    p.add_run("• โลโก้และชื่อเกม: ").bold = True
    p.add_run("คลิกเพื่อรีเซ็ตตัวกรองและคำค้นหากลับสู่หน้าแรกทันที\n")
    p.add_run("• ช่องค้นหาด่วน (Live Search): ").bold = True
    p.add_run("พิมพ์เพื่อค้นหาไอเทมใดๆ ได้ทันทีโดยไม่ต้องกด Enter (สามารถกดคีย์ลัด ")
    p.add_run("/").bold = True
    p.add_run(" บนคีย์บอร์ดเพื่อเข้าสู่ช่องค้นหาได้อย่างรวดเร็ว)\n")
    p.add_run("• ปุ่มสลับโหมดแสง (Theme Toggle): ").bold = True
    p.add_run("สลับระหว่างโหมดมืด (Dark Stone Mode) ที่สบายตา และโหมดสว่าง (Warm Sunlight Mode)\n")
    p.add_run("• ปุ่มรายการโปรด (⭐ Favorites Drawer): ").bold = True
    p.add_run("เปิดแถบด้านข้างเพื่อดูรายการไอเทมทั้งหมดที่คุณได้กดบันทึกไว้")

    add_h2(doc, "2.2 ป้ายสถิติและแนะนำภาพรวม (Hero Banner)")
    p = add_styled_paragraph(doc)
    p.add_run("แสดงสถิติจำนวนไอเทมและข้อมูลในเวอร์ชันปัจจุบัน ได้แก่ จำนวนพืชพันธุ์ (8 ชนิด), สัตว์โบราณ (5 ชนิด), "
              "สิ่งประดิษฐ์และเครื่องมือ (6 ชิ้น), ชาวเผ่า (4 ท่าน) และสูตรอาหาร (4 สูตร)")

    add_h2(doc, "2.3 แถบแท็บสลับหมวดหมู่ (Navigation Tabs)")
    p = add_styled_paragraph(doc)
    p.add_run("แถบปุ่มกดแนวนอนที่ช่วยให้ผู้เล่นสลับดูข้อมูลได้อย่างรวดเร็ว ประกอบด้วย 8 แท็บ:\n"
              "1. 🌾 พืชพันธุ์ & การเกษตร\n"
              "2. 🦣 สัตว์ดึกดำบรรพ์ & การฝึก\n"
              "3. 🪓 เครื่องมือ & การคราฟต์\n"
              "4. 🏕️ ชนเผ่า & NPC\n"
              "5. 🍲 อาหาร & บัฟพลัง\n"
              "6. 🗺️ แผนที่ & จุดเก็บเกี่ยว\n"
              "7. 🧮 คำนวณผลผลิต (Crop Calculator)\n"
              "8. 🎁 ค้นหาของขวัญ NPC (Gift Matcher)")

    # -------------------------------------------------------------
    # บทที่ 3
    # -------------------------------------------------------------
    add_h1(doc, "บทที่ 3: คู่มือการใช้งานหมวดหมู่ข้อมูลเกม", "📖")

    add_h2(doc, "3.1 หมวดพืชพันธุ์และการเกษตร (Crops & Farming)")
    p = add_styled_paragraph(doc)
    p.add_run("ระบบแสดงรายการพืชผลโบราณทั้งหมด พร้อมระบบคัดกรองตามฤดูกาล โดยข้อมูลในแต่ละการ์ดประกอบด้วย:")
    p_crop = add_styled_paragraph(doc)
    p_crop.add_run("• ตัวกรองฤดูกาล: สามารถคลิกเลือกเฉพาะ ฤดูใบไม้ผลิ, ฤดูร้อน, ฤดูใบไม้ร่วง หรือ ฤดูหนาว\n"
                   "• ระยะเวลาการเติบโต: ระบุจำนวนวันที่ใช้ในการเติบโตต่อหนึ่งรอบ\n"
                   "• การเก็บเกี่ยวซ้ำ (Regrow): ระบุว่าพืชชนิดนี้เก็บเกี่ยวได้ครั้งเดียว หรือสามารถเก็บเกี่ยวซ้ำได้ต่อเนื่อง\n"
                   "• พลังงานฟื้นฟู (Stamina): ค่าพลังงานที่ได้รับเมื่อรับประทานผลผลิตสด\n"
                   "• ราคาซื้อและราคาขาย: ใช้ประเมินความคุ้มค่าในการลงทุน\n"
                   "• การเปิดหน้าต่างเจาะลึก (Quick Modal): คลิกที่การ์ดเพื่อดูแหล่งที่พบเมล็ดป่า และเคล็ดลับการปลูกระดับสูง")

    add_h2(doc, "3.2 หมวดสัตว์ดึกดำบรรพ์และการฝึกให้เชื่อง (Ancient Beasts)")
    p = add_styled_paragraph(doc)
    p.add_run("รวบรวมสิ่งมีชีวิตและสัตว์ยักษ์แห่งยุคน้ำแข็งและยุคหิน:")
    p_beast = add_styled_paragraph(doc)
    p_beast.add_run("• ช้างแมมมอธแคระ (Mini Mammoth): สัตว์เศรษฐกิจที่ช่วยผลิตขน นม และช่วยพรวนดิน 3x3 แปลง\n"
                    "• นกโดโด้ยักษ์ (Giant Dodo): สัตว์ปีกในเล้า ให้ไข่ฟองยักษ์และขนนกสีรุ้งสำหรับประดิษฐ์สิ่งของ\n"
                    "• ลูกเสือเขี้ยวดาบ (Saber-toothed Cub): สัตว์เลี้ยงคู่หู ช่วยต่อสู้ไล่สัตว์ร้าย และเพิ่มความเร็วเดิน +15%\n"
                    "• กวางยักษ์ไอริชเอลก์ (Irish Elk): สัตว์ขี่ความเร็วสูง สามารถวิ่งข้ามแม่น้ำและภูมิประเทศขรุขระ\n"
                    "• สเตโกซอรัสแคระ (Dwarf Stegosaurus): ช่วยบดหินเป็นดินเพาะปลูก และผลิตเกล็ดกระดูกทำเกราะ\n"
                    "• เคล็ดลับการฝึก: แต่ละชนิดมีวิธีฝึกเฉพาะ เช่น การเป่า 'ขลุ่ยกระดูก' หรือการย่องเงียบ (Stealth) เข้าไปป้อนอาหาร")

    add_h2(doc, "3.3 หมวดเครื่องมือและการคราฟต์ (Crafting & Tools)")
    p = add_styled_paragraph(doc)
    p.add_run("แสดงรายชื่อเครื่องมือพื้นฐาน อุปกรณ์ทำฟาร์ม เครื่องมือล่าสัตว์ และเตาหลอม:")
    p_craft = add_styled_paragraph(doc)
    p_craft.add_run("• ขวานหินเหล็กไฟ (Flint Axe): ใช้ตัดต้นไม้และเก็บฟืน\n"
                    "• จอบกระดูกสัตว์ (Bone Hoe): เครื่องมือขุดเปิดหน้าดินสำหรับแปลงเพาะปลูก\n"
                    "• ฉมวกกระดูกจับปลา (Bone Harpoon): ฉมวกสองเงี่ยงสำหรับล่าปลาในแม่น้ำ\n"
                    "• เตาเผาดินเหนียว (Primitive Clay Kiln): สิ่งก่อสร้างสำหรับเผาหม้อ เครื่องปั้นดินเผา และหลอมแร่\n"
                    "• เครื่องทอเส้นใยโบราณ (Vine Loom): แปรรูปขนสัตว์และเส้นใยพืชเป็นผืนผ้าใบ\n"
                    "• ขลุ่ยกระดูกสื่อสารสัตว์ (Bone Flute): เครื่องดนตรีทำจากกระดูกปีกนกสำหรับฝึกสัตว์ป่า")

    add_h2(doc, "3.4 หมวดชนเผ่าและ NPC (Tribe & Villagers)")
    p = add_styled_paragraph(doc)
    p.add_run("ข้อมูลเพื่อนบ้านและสมาชิกคนสำคัญในเผ่าประกายไฟ:")
    npc_tbl = doc.add_table(rows=5, cols=4)
    npc_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    npc_headers = ["ชื่อ NPC", "บทบาทในเผ่า", "ของขวัญที่ชอบมาก (Loves)", "ของขวัญที่ไม่ชอบ (Dislikes)"]
    for idx, h in enumerate(npc_headers):
        cell = npc_tbl.cell(0, idx)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        set_font(r, font_name="TH Sarabun New", size_pt=14, bold=True, color=RGBColor(255, 255, 255))

    npc_rows = [
        ("ทาฮู (Tahu)", "หัวหน้าเผ่าผู้พิทักษ์ไฟ", "สตูว์เนื้อแมมมอธ, หินอำพัน", "หินกรวด, ปลาเน่า, วัชพืช"),
        ("ไอยา (Aya)", "หมอยาและนักพฤกษศาสตร์", "เห็ดเรืองแสง, ชาสมุนไพรป่า", "กระดูกสัตว์หัก, ขี้เถ้า, เนื้อดิบ"),
        ("โครัก (Khorak)", "ช่างตีหินและประดิษฐ์อาวุธ", "แร่ทองแดงดิบ, หินออบซิเดียน", "ดอกไม้บอบบาง, ขนนกเปียก"),
        ("มิร่า (Mira)", "พรานสาวผู้สื่อสารกับสัตว์", "ขนนกโดโด้สีรุ้ง, ขลุ่ยกระดูก", "กับดักเหล็ก, ซุปขม, เศษหินคม")
    ]
    for row_idx, data_tuple in enumerate(npc_rows, start=1):
        row = npc_tbl.rows[row_idx]
        for col_idx, text in enumerate(data_tuple):
            p = row.cells[col_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(text)
            set_font(r, font_name="TH Sarabun New", size_pt=13, color=COLOR_TEXT)
            if col_idx == 0:
                r.bold = True
    style_table(npc_tbl)

    add_h2(doc, "3.5 หมวดอาหารและสูตรปรุง (Cooking & Recipes)")
    p = add_styled_paragraph(doc)
    p.add_run("อาหารในยุคดึกดำบรรพ์ไม่ได้มีไว้เพียงดับความหิว แต่ยังมอบบัฟพิเศษที่จำเป็นต่อการเอาชีวิตรอด:")
    p_cook = add_styled_paragraph(doc)
    p_cook.add_run("• สตูว์เนื้อแมมมอธสมุนไพร: มอบบัฟ 'ทนความหนาวจัด' นาน 10 นาที และเพิ่มเลือดสูงสุด +50\n"
                    "• ปลาย่างใบตองโบราณ: มอบบัฟ 'ความเร็วเดิน +25%' นาน 6 นาที\n"
                    "• ซุปเห็ดเรืองแสง: มอบบัฟ 'รัศมีส่องสว่างในที่มืด' นาน 8 นาที สำหรับสำรวจถ้ำลึก\n"
                    "• เค้กเมล็ดพืชน้ำผึ้งป่า: มอบบัฟ 'ลดการสูญเสียพลังงานจากการใช้แรงงาน -30%' นาน 5 นาที")

    # -------------------------------------------------------------
    # บทที่ 4
    # -------------------------------------------------------------
    add_h1(doc, "บทที่ 4: การใช้งานเครื่องมือพิเศษ (Interactive Tools)", "🧮")
    
    add_h2(doc, "4.1 เครื่องคำนวณผลผลิตและกำไร (Crop Profit Calculator)")
    p = add_styled_paragraph(doc)
    p.add_run("เครื่องมืออัจฉริยะที่ช่วยให้ผู้เล่นวางแผนการทำฟาร์มในแต่ละฤดูกาลได้อย่างมีกำไรสูงสุด "
              "โดยอิงตามปฏิทินของเกม (1 ฤดู มี 28 วัน)")
    
    add_callout(doc, "ขั้นตอนการใช้งาน Crop Profit Calculator",
                "1. คลิกเลือกแท็บ '🧮 คำนวณผลผลิต' จากแถบเมนูด้านบน\n"
                "2. เลือกชนิดพืชที่ต้องการปลูกจากเมนูดรอปดาวน์\n"
                "3. กรอกจำนวนแปลงที่ปลูก (Plots) เช่น 12 แปลง หรือ 24 แปลง\n"
                "4. กรอกวันที่เริ่มปลูกของฤดูกาล (วันที่ 1 - 28)\n"
                "5. ระบบจะคำนวณจำนวนรอบที่เก็บเกี่ยวได้ทัน ต้นทุนค่าเมล็ดทั้งหมด รายได้รวม และ 'กำไรสุทธิ' ออกมาให้โดยอัตโนมัติ!")

    add_h2(doc, "4.2 ตัวช่วยค้นหาของขวัญ NPC (NPC Gift Matcher)")
    p = add_styled_paragraph(doc)
    p.add_run("เครื่องมือที่ออกแบบมาแก้ปัญหาที่ผู้เล่นมักจำไม่ได้ว่าชาวเผ่าคนไหนชอบหรือไม่ชอบอะไร "
              "เพียงผู้เล่นเลือกไอเทมที่มีอยู่ในกระเป๋า ระบบจะแสดงผลรีแอคชันและบทสนทนาตอบรับของชาวเผ่าทุกคนทันที "
              "ช่วยประหยัดเวลาและป้องกันไม่ให้ผู้เล่นเผลอให้ของขวัญที่ทำให้ค่าความสัมพันธ์ลดลง")

    # -------------------------------------------------------------
    # บทที่ 5
    # -------------------------------------------------------------
    add_h1(doc, "บทที่ 5: แผนที่ดินแดนบรรพกาล (Interactive World Map)", "🗺️")
    p = add_styled_paragraph(doc)
    p.add_run("แผนผังดินแดนถูกจำลองในรูปแบบ 'แผนผังแผ่นหนังสัตว์' (Leather Schematic Map) "
              "ที่ผู้เล่นสามารถคลิกเลือกดินแดนต่างๆ เพื่อตรวจสอบข้อมูลสภาพแวดล้อมได้แบบเรียลไทม์:")

    map_tbl = doc.add_table(rows=6, cols=3)
    map_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    map_headers = ["ดินแดน", "ระดับความยาก", "ทรัพยากรเด่นที่เก็บเกี่ยวได้"]
    for idx, h in enumerate(map_headers):
        cell = map_tbl.cell(0, idx)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        set_font(r, font_name="TH Sarabun New", size_pt=14, bold=True, color=RGBColor(255, 255, 255))

    map_rows = [
        ("หมู่บ้านชนเผ่าประกายไฟ", "เขตปลอดภัย (Lv. 1)", "น้ำสะอาด, ท่อนฟืน, เศษหินแม่น้ำ, ร้านค้าแลกเปลี่ยน"),
        ("ทุ่งหิมะทุนดราแมมมอธ", "เขตหนาวเย็น (Lv. 3)", "หัวมันหิมะ, ก้อนน้ำแข็งถาวร, ขนแมมมอธ, ถิ่นเสือเขี้ยวดาบ"),
        ("ป่าดงดิบใบเฟิร์นยักษ์", "เขตป่าชื้น (Lv. 2)", "หญ้าหวาน, ใบเฟิร์นยักษ์, ยางไม้เหนียว, สมุนไพรรักษาโรค"),
        ("ถ้ำหินย้อยโบราณ", "เขตสำรวจลึก (Lv. 4+)", "หินเหล็กไฟ, แร่ทองแดงดิบ, หินออบซิเดียน, เห็ดเรืองแสง"),
        ("หาดเปลือกหอยและแนวปะการัง", "เขตฟาร์มปลา (Lv. 1)", "ไข่โดโด้, เปลือกหอย, ทรายเนื้อละเอียด, ปลาแซลมอนโบราณ")
    ]
    for row_idx, (zn, zl, zr) in enumerate(map_rows, start=1):
        row = map_tbl.rows[row_idx]
        for col_idx, text in enumerate([zn, zl, zr]):
            p = row.cells[col_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(text)
            set_font(r, font_name="TH Sarabun New", size_pt=13, color=COLOR_TEXT)
            if col_idx == 0:
                r.bold = True
    style_table(map_tbl)

    # -------------------------------------------------------------
    # บทที่ 6
    # -------------------------------------------------------------
    add_h1(doc, "บทที่ 6: คำแนะนำสำหรับผู้พัฒนาและอัปเดตข้อมูล", "🛠️")
    p = add_styled_paragraph(doc)
    p.add_run("เว็บไซต์ถูกออกแบบโดยแยกส่วนข้อมูล (Data Layer) ออกจากส่วนแสดงผล (View Layer) อย่างชัดเจน "
              "ทำให้ผู้ดูแลสามารถเพิ่มเติมเนื้อหาใหม่ๆ ได้อย่างง่ายดายโดยไม่ต้องแก้ไขโค้ดโครงสร้าง:")

    add_h2(doc, "6.1 การเพิ่มไอเทมใหม่ในไฟล์ data.js")
    p = add_styled_paragraph(doc)
    p.add_run("หากในอนาคตเกมมีแพตช์อัปเดตพืชพันธุ์ สัตว์ หรือสูตรอาหารใหม่ สามารถเปิดไฟล์ ")
    p.add_run("data.js").bold = True
    p.add_run(" ด้วยโปรแกรม Text Editor (เช่น VS Code, Notepad) แล้วเพิ่มข้อมูลในรูปแบบ JSON Object เช่น:\n\n")

    code_tbl = doc.add_table(rows=1, cols=1)
    code_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_cell = code_tbl.cell(0, 0)
    c_cell.width = Inches(6.27)
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1E293B"/>')
    c_cell._tc.get_or_add_tcPr().append(shading)
    cp = c_cell.paragraphs[0]
    cr = cp.add_run(
        "{\n"
        "  id: \"crop-new\",\n"
        "  name: \"ผลเบอร์รี่สายฟ้า (Thunderberry)\",\n"
        "  season: \"summer\",\n"
        "  growthDays: 5,\n"
        "  regrow: true,\n"
        "  regrowDays: 2,\n"
        "  seedPrice: 50,\n"
        "  sellPrice: 45,\n"
        "  icon: \"⚡\"\n"
        "}"
    )
    set_font(cr, font_name="Consolas", size_pt=11, color=RGBColor(241, 245, 249))

    add_h2(doc, "6.2 การนำเว็บไซต์ขึ้นระบบออนไลน์ (Publish to Web)")
    p = add_styled_paragraph(doc)
    p.add_run("เนื่องจากเว็บไซต์นี้เป็น Static Web Application (HTML/CSS/JS) จึงสามารถนำขึ้นโฮสต์ฟรีได้ทันที เช่น:\n"
              "• GitHub Pages: เพียงสร้าง Repository แล้วเปิดใช้งาน GitHub Pages ใน Settings\n"
              "• Vercel / Netlify: ลากโฟลเดอร์โครงการไปวางเพื่อเผยแพร่ออนไลน์ได้ภายใน 1 นาที\n"
              "• Cloudflare Pages: เชื่อมต่อและเปิดใช้งานได้ฟรีไม่มีค่าใช้จ่าย")

    # Document End Summary
    doc.add_paragraph().paragraph_format.space_before = Pt(20)
    p_end = add_styled_paragraph(doc, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_end = p_end.add_run("— สิ้นสุดเอกสารคู่มือการใช้งาน —\nไพรวัลย์ บรรพกาล: วิถีชีวิตยุคหิน (Primal Haven)")
    set_font(r_end, font_name="TH Sarabun New", size_pt=14, italic=True, color=COLOR_MUTED)

    # Save document
    output_path = r"c:\งาน01\คู่มือการใช้งาน_Primal_Haven_Wiki.docx"
    doc.save(output_path)
    print(f"Document saved successfully to {output_path}")

if __name__ == "__main__":
    create_manual()
