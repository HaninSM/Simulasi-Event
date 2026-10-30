#!/usr/bin/env python3
"""
Generate 5 Corporate & Executive Light-Theme Cybersecurity Presentations (.pptx)
Aesthetic: Professional, Light Background, Boardroom & Corporate Consulting Style.
Clean typography, soft cards, elegant navy/cobalt/emerald accents, strictly avoiding IT/hacker tropes.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ==================== DESIGN TOKENS (LIGHT CORPORATE THEME) ====================
COLOR_PAGE_BG       = RGBColor(248, 250, 252) # #f8fafc Crisp Light Slate
COLOR_CARD_BG       = RGBColor(255, 255, 255) # #ffffff Pure White Card
COLOR_CARD_ALT      = RGBColor(241, 245, 249) # #f1f5f9 Soft Tinted Container
COLOR_BORDER        = RGBColor(226, 232, 240) # #e2e8f0 Subtle Slate Border
COLOR_NAVY_PRIMARY  = RGBColor(15, 23, 42)    # #0f172a Deep Corporate Navy
COLOR_NAVY_ACCENT   = RGBColor(30, 58, 138)   # #1e3a8a Classic Banking Navy
COLOR_BLUE_ROYAL    = RGBColor(37, 99, 235)   # #2563eb Professional Cobalt Blue
COLOR_TEXT_DARK     = RGBColor(30, 41, 59)    # #1e293b Charcoal Body Text
COLOR_TEXT_MUTED    = RGBColor(100, 116, 139) # #64748b Executive Slate Muted
COLOR_EMERALD_GREEN = RGBColor(4, 120, 87)    # #047857 Corporate Forest Green
COLOR_ROSE_RED      = RGBColor(190, 18, 60)   # #be123c Sophisticated Crimson
COLOR_AMBER_GOLD    = RGBColor(180, 83, 9)    # #b45309 Warm Executive Bronze/Amber
COLOR_PURPLE_SLATE  = RGBColor(109, 40, 217)  # #6d28d9 Refined Purple

def create_base_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs

def render_light_slide_header(slide, title_text, category_pill="STRATEGIC CYBERSECURITY MANAGEMENT", subtitle_text=""):
    # 1. Slide Canvas Background (Off-white / Slate 50)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_PAGE_BG
    bg.line.fill.background()

    # 2. Executive Navy Header Top Stripe
    top_stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.08))
    top_stripe.fill.solid()
    top_stripe.fill.fore_color.rgb = COLOR_NAVY_ACCENT
    top_stripe.line.fill.background()

    # 3. Category Pill Tag
    pill_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.35), Inches(3.6), Inches(0.32))
    pill_shape.fill.solid()
    pill_shape.fill.fore_color.rgb = COLOR_CARD_ALT
    pill_shape.line.color.rgb = COLOR_BORDER
    pill_shape.line.width = Pt(1)

    tf_pill = pill_shape.text_frame
    tf_pill.word_wrap = False
    p_pill = tf_pill.paragraphs[0]
    p_pill.text = category_pill.upper()
    p_pill.font.size = Pt(8.5)
    p_pill.font.bold = True
    p_pill.font.color.rgb = COLOR_NAVY_ACCENT
    p_pill.font.name = "Segoe UI"
    p_pill.alignment = PP_ALIGN.CENTER

    # 4. Slide Title & Subtitle Box
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.8))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY_PRIMARY
    p_title.font.name = "Segoe UI"

    if subtitle_text:
        p_sub = tf_title.add_paragraph()
        p_sub.text = subtitle_text
        p_sub.font.size = Pt(10.5)
        p_sub.font.color.rgb = COLOR_TEXT_MUTED
        p_sub.font.name = "Segoe UI"
        p_sub.space_before = Pt(3)

    # 5. Footer Line & Caption
    footer_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.95), Inches(11.733), Inches(0.02))
    footer_line.fill.solid()
    footer_line.fill.fore_color.rgb = COLOR_BORDER
    footer_line.line.fill.background()

    footer = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.35))
    tf_f = footer.text_frame
    pf = tf_f.paragraphs[0]
    pf.text = "Enterprise Cyber Defense & SIEM Governance  |  Corporate Strategic Operations"
    pf.font.size = Pt(8.5)
    pf.font.color.rgb = COLOR_TEXT_MUTED
    pf.font.name = "Segoe UI"

def render_cover_slide(prs, deck_number_str, deck_title, deck_subtitle, target_audience="Executive Board & Security Leadership"):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_PAGE_BG
    bg.line.fill.background()

    # Main Corporate Presentation Card
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.0), Inches(11.333), Inches(5.5))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD_BG
    card.line.color.rgb = COLOR_BORDER
    card.line.width = Pt(1.5)

    # Left Decorative Accent Column
    left_accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.0), Inches(0.2), Inches(5.5))
    left_accent.fill.solid()
    left_accent.fill.fore_color.rgb = COLOR_NAVY_ACCENT
    left_accent.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(1.8), Inches(1.6), Inches(9.8), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p_badge = tf.paragraphs[0]
    p_badge.text = f"CYBERSECURITY EXECUTIVE SERIES  •  DECK {deck_number_str}"
    p_badge.font.size = Pt(11)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_BLUE_ROYAL
    p_badge.font.name = "Segoe UI"

    p_title = tf.add_paragraph()
    p_title.text = deck_title
    p_title.font.size = Pt(28)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY_PRIMARY
    p_title.font.name = "Segoe UI"
    p_title.space_before = Pt(8)

    p_sub = tf.add_paragraph()
    p_sub.text = deck_subtitle
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = COLOR_TEXT_MUTED
    p_sub.font.name = "Segoe UI"
    p_sub.space_before = Pt(12)

    p_meta = tf.add_paragraph()
    p_meta.text = f"Target Audience: {target_audience}  |  Framework: ISO 27001, NIST SP 800-92, OCSF Governance\nEngineering Team: JadiBegini (Bagus Hanindyo Kusuma, Anand Ferdiansyah, Fitus Yayan Ofnaio Zebua)"
    p_meta.font.size = Pt(10)
    p_meta.font.color.rgb = COLOR_TEXT_DARK
    p_meta.font.name = "Segoe UI"
    p_meta.space_before = Pt(28)

    return slide

# ==================== DECK 1: EXECUTIVE OVERVIEW & GOVERNANCE ====================
def build_deck_1(filepath="01_executive_overview_strategy.pptx"):
    prs = create_base_deck()

    # Slide 1: Cover
    render_cover_slide(
        prs,
        deck_number_str="01 / 05",
        deck_title="Executive Overview, Leadership Team & SIEM Philosophy",
        deck_subtitle="Prinsip Strategis Pusat Komando Operasi Keamanan, Profil Tim JadiBegini, & Nilai Investasi Cyber Defense",
        target_audience="Chief Information Security Officer (CISO), Dewan Direksi, & Stakeholder Bisnis"
    )

    # Slide 2: Profil Tim JadiBegini & Filosofi Gedung Raksasa
    s2 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s2,
        title_text="Profil Tim Pengembang JadiBegini & Filosofi Fundamental SIEM",
        category_pill="STRATEGI & ORGANISASI",
        subtitle_text="Keahlian lintas disiplin pengembang dan pemahaman esensi pusat komando keamanan siber."
    )
    # Team Cards
    team = [
        ("Bagus Hanindyo Kusuma", "Lead / Agile Coach / PM", "Scrum Master & Program Manager dengan pendekatan servant leadership, memandu arsitektur kolaboratif dan tata kelola siklus pengembangan sistem."),
        ("Anand Ferdiansyah", "Security Architecture Lead", "Mahasiswa Universitas Pamulang, berfokus pada normalisasi skema data heterogen, validasi Gatekeeper, dan mitigasi risiko time drift."),
        ("Fitus Yayan Ofnaio Zebua", "Operations Analyst", "Mahasiswa Universitas Pamulang & Pengemudi Grab aktif, berfokus pada verifikasi logika operasional skenario insiden dan penanganan alert fatigue.")
    ]
    for idx, (name, role, bio) in enumerate(team):
        x = Inches(0.8 + idx * 3.95)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(3.75), Inches(2.25))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        tb = s2.shapes.add_textbox(x + Inches(0.2), Inches(1.75), Inches(3.35), Inches(1.95))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = name
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_NAVY_PRIMARY
        
        p2 = tf.add_paragraph()
        p2.text = role.upper()
        p2.font.size = Pt(8.5)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_BLUE_ROYAL
        p2.space_before = Pt(2)

        p3 = tf.add_paragraph()
        p3.text = bio
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = COLOR_TEXT_MUTED
        p3.space_before = Pt(6)

    # Philosophy Cards
    phils = [
        ("🏢 Analogi Gedung Perkantoran Raksasa", "SIEM diibaratkan ruang kendali terpadu gedung bertingkat dengan ratusan pintu dan CCTV. Saat kartu akses 'Budi' digunakan di lobi sementara workstation Budi aktif di lantai 15, SIEM membunyikan alarm korelasi seketika."),
        ("🛡️ Perbedaan Peran: Antivirus vs SIEM & 'SI' vs 'EM'", "Antivirus melindungi satu perangkat lokal secara pasif; SIEM mengawasi seluruh perimeter secara holistik. 'Security Information' mengarsipkan data audit kepatuhan, sedangkan 'Event Management' mengorelasikan anomali real-time.")
    ]
    for idx, (p_title, p_desc) in enumerate(phils):
        x = Inches(0.8 + idx * 5.95)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(4.1), Inches(5.75), Inches(2.6))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        tb = s2.shapes.add_textbox(x + Inches(0.2), Inches(4.25), Inches(5.35), Inches(2.3))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = p_title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY_ACCENT

        p_b = tf.add_paragraph()
        p_b.text = p_desc
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = COLOR_TEXT_DARK
        p_b.space_before = Pt(6)

    # Slide 3: 6 Nilai Strategis Produk
    s3 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s3,
        title_text="Enam Nilai Strategis Mini-SIEM bagi Operasional Bisnis",
        category_pill="NILAI BISNIS",
        subtitle_text="Pondasi kapabilitas pertahanan siber yang andal, akuntabel, dan berorientasi efisiensi biaya."
    )
    values = [
        ("1. Gatekeeper Ingestion", "Normalisasi kontrak data JSON kanonikal dari beragam sumber log. Menolak data cacat dan clock drift via HTTP 422.", COLOR_BLUE_ROYAL),
        ("2. Rule Correlation Brain", "Korelasi sliding window stateful di memori mendeteksi serangan L7, brute force, insider threat, dan anomali jam kantor.", COLOR_NAVY_ACCENT),
        ("3. SOAR Active Containment", "Respons aktif memutus serangan di gerbang masuk: Host Quarantine & User Suspension menolak paket via HTTP 403.", COLOR_EMERALD_GREEN),
        ("4. Hot vs Cold Storage Tiering", "Mengatasi celah temporal blind spot serangan APT puluhan hari menggunakan Persistent Stateful Greylist dan rehidrasi forensik.", COLOR_PURPLE_SLATE),
        ("5. Universal Log Adapter", "Membaca 27 berkas log fisik autentik (Nginx, Syslog RFC 3164, CSV, PGAudit JSONL, MQTT) dengan timestamp shifting dinamis.", COLOR_AMBER_GOLD),
        ("6. Pemantauan Fasilitas Fisik OT", "Memonitor sensor dan kontrol pendingin fasilitas datacenter via MQTT untuk mencegah insiden thermal runaway katastropik.", COLOR_ROSE_RED)
    ]
    for idx, (vtitle, vdesc, vcolor) in enumerate(values):
        col = idx % 3
        row = idx // 3
        x = Inches(0.8 + col * 3.95)
        y = Inches(1.6 + row * 2.5)

        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.75), Inches(2.3))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        # Colored left tag
        tag = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.15), y + Inches(0.18), Inches(0.08), Inches(0.35))
        tag.fill.solid()
        tag.fill.fore_color.rgb = vcolor
        tag.line.fill.background()

        tb = s3.shapes.add_textbox(x + Inches(0.32), y + Inches(0.15), Inches(3.25), Inches(2.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = vtitle
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_NAVY_PRIMARY

        p2 = tf.add_paragraph()
        p2.text = vdesc
        p2.font.size = Pt(10)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(8)

    # Slide 4: Blueprint Arsitektur 5 Layer
    s4 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s4,
        title_text="Blueprint Arsitektur 5 Layer Enterprise Ingestion Pipeline",
        category_pill="ARSITEKTUR ENTERPRISE",
        subtitle_text="Pemrosesan aliran telemetri heterogen dari sensor fisik dan aplikasi hingga konsol analis SOC."
    )
    layers = [
        ("Layer 1: Sumber Telemetri Heterogen", "Menghubungkan Nginx Web Server, Linux Syslog RFC 3164, Turnstile Gate CSV, Database PGAudit, dan Broker MQTT. 27 berkas fisik terintegrasi di sample_logs/.", COLOR_BLUE_ROYAL),
        ("Layer 2: Universal Log Adapter", "Normalisasi parsing multi-format berbasis regex dan dynamic timestamp shifting untuk menyesuaikan jendela waktu korelasi secara otomatis.", COLOR_NAVY_ACCENT),
        ("Layer 3: Gatekeeper Ingestion & Validasi", "Pemeriksaan integritas IPv4, kelengkapan atribut wajib, audit Time Drift (< 24 jam lampau / masa depan), dan penolakan langsung entitas karantina SOAR (HTTP 403).", COLOR_ROSE_RED),
        ("Layer 4: Correlation Engine (The Brain)", "Mesin korelasi berbasis aturan memproses sliding window waktu (10 detik, 60 detik, 1 jam), alert debouncing, dan korelasi sabotase hardware fisik.", COLOR_PURPLE_SLATE),
        ("Layer 5: Storage Tiering & Web SOC Console", "Pemisahan Hot In-Memory Cache untuk korelasi instan dan Cold Storage untuk kepatuhan audit. Dasbor pemantauan real-time dengan audit trail terpadu.", COLOR_EMERALD_GREEN)
    ]
    for idx, (ltitle, ldesc, lcolor) in enumerate(layers):
        y = Inches(1.6 + idx * 1.02)
        bar = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.733), Inches(0.88))
        bar.fill.solid()
        bar.fill.fore_color.rgb = COLOR_CARD_BG
        bar.line.color.rgb = COLOR_BORDER
        bar.line.width = Pt(1)

        side = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.12), Inches(0.88))
        side.fill.solid()
        side.fill.fore_color.rgb = lcolor
        side.line.fill.background()

        tb = s4.shapes.add_textbox(Inches(1.1), y + Inches(0.08), Inches(11.2), Inches(0.72))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = ltitle
        p1.font.size = Pt(11.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_NAVY_PRIMARY

        p2 = tf.add_paragraph()
        p2.text = ldesc
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

    prs.save(filepath)
    print(f"[OK] Generated: {filepath}")

# ==================== DECK 2: DATA CONTRACTS & GATEKEEPER ====================
def build_deck_2(filepath="02_data_contracts_gatekeeper.pptx"):
    prs = create_base_deck()

    render_cover_slide(
        prs,
        deck_number_str="02 / 05",
        deck_title="Data Contracts, Gatekeeper Validation & Integration Syllabus",
        deck_subtitle="Standarisasi Skema Log Kanonikal, Pengujian Negatif RFC, dan Prasyarat Integrasi Infrastruktur Enterprise",
        target_audience="Security Engineers, Data Architects, & IT Operations Leads"
    )

    # Slide 2: Data Contract Kanonikal
    s2 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s2,
        title_text="Spesifikasi Kontrak Data Kanonikal & Schema Enforcement",
        category_pill="KONTRAK DATA & SKEMA",
        subtitle_text="Format JSON terpadu untuk menyelaraskan ribuan sumber telemetri heterogen."
    )
    # Left Card: JSON
    c_l = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    c_l.fill.solid()
    c_l.fill.fore_color.rgb = COLOR_CARD_BG
    c_l.line.color.rgb = COLOR_BORDER
    c_l.line.width = Pt(1)

    tb_l = s2.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p1 = tf_l.paragraphs[0]
    p1.text = "Kontrak Data JSON Kanonikal"
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_NAVY_PRIMARY

    schema_str = (
        "{\n"
        "  \"timestamp\": \"YYYY-MM-DDThh:mm:ssZ\",\n"
        "  \"event_type\": \"login_attempt | web_request |\n"
        "                database_download | recon_probe |\n"
        "                ot_command | mqtt_command\",\n"
        "  \"user_id\": \"string (non-empty)\",\n"
        "  \"ip_address\": \"string (IPv4 Valid)\",\n"
        "  \"location\": \"string (non-empty)\",\n"
        "  \"status\": \"success | failed\",\n\n"
        "  // Komponen Opsional Perangkat Fisik OT:\n"
        "  \"protocol\": \"MQTT | Modbus | BACnet\",\n"
        "  \"device_type\": \"AC_CENTRAL | CHILLER\",\n"
        "  \"target_device\": \"CRAC-AC-CENTRAL-01\",\n"
        "  \"command\": \"POWER_OFF | STATUS_REPORT\"\n"
        "}"
    )
    p_code = tf_l.add_paragraph()
    p_code.text = schema_str
    p_code.font.size = Pt(9.5)
    p_code.font.color.rgb = COLOR_BLUE_ROYAL
    p_code.font.name = "Consolas"
    p_code.space_before = Pt(8)

    # Right Card: Validasi Negatif
    c_r = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    c_r.fill.solid()
    c_r.fill.fore_color.rgb = COLOR_CARD_BG
    c_r.line.color.rgb = COLOR_BORDER
    c_r.line.width = Pt(1)

    tb_r = s2.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    pr = tf_r.paragraphs[0]
    pr.text = "Ketahanan Gatekeeper (Validasi Negatif)"
    pr.font.size = Pt(13)
    pr.font.bold = True
    pr.font.color.rgb = COLOR_ROSE_RED

    validations = [
        ("Integritas Format IPv4", "Menolak alamat string rusak atau bukan format desimal 4 oktet (misal '999.999.999.999')."),
        ("Field Wajib (Non-Empty)", "Menolak paket jika atribut wajib seperti user_id, ip_address, atau location kosong/null."),
        ("Time Drift Lampau (> 24 Jam)", "Menolak log basi lampau (seperti router legacy dengan baterai CMOS reset ke 1970) via HTTP 422."),
        ("Time Drift Masa Depan", "Menolak log dengan stempel waktu > 30 detik di masa depan dari waktu riil sistem."),
        ("SOAR Active Enforcement", "Log dari IP atau pengguna yang berstatus karantina langsung ditolak di gerbang masuk via HTTP 403.")
    ]
    for v_title, v_desc in validations:
        p = tf_r.add_paragraph()
        p.text = f"• {v_title}: {v_desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MUTED
        p.space_before = Pt(8)

    # Slide 3: Silabus Persiapan Integrasi Infrastruktur (4 Pilar)
    s3 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s3,
        title_text="Silabus Persiapan Integrasi Infrastruktur (Universal Ingestion)",
        category_pill="SILABUS OPERASIONAL",
        subtitle_text="Empat pilar kesiapan teknis dan bisnis sebelum menghubungkan perangkat ke sistem SIEM."
    )
    syllabus = [
        ("Tahap 1: Fondasi Bahan Baku Log", COLOR_BLUE_ROYAL,
         "• Anatomi Log: Membedakan Event (kejadian), Payload (isi utama data), dan Metadata (keterangan tambahan).\n• Log Lifecycle: Titik lahir -> Forwarding -> Queueing -> Hot Storage -> Cold Archive.\n• Kalkulasi EPS (Events Per Second): Menghitung beban volume log harian agar mesin korelasi tidak kelebihan kapasitas."),
        ("Tahap 2: Standarisasi Protokol Internasional", COLOR_NAVY_ACCENT,
         "• Protokol RFC 5424: Format pembungkus Syslog standar (Timestamp, Hostname, Severity, Message Payload).\n• Kepatuhan NIST SP 800-92 & ISO 27002: Standar peristiwa wajib catat (kegagalan login & eskalasi privilese).\n• Skema Universal OCSF / CIM: Menyatukan field multi-vendor (SrcIP & Client_Address -> src_endpoint.ip)."),
        ("Tahap 3: Prasyarat Infrastruktur Jaringan", COLOR_AMBER_GOLD,
         "• Sinkronisasi Waktu Sentral (NTP): Syarat mutlak! Seluruh server dan router wajib merujuk waktu atomik UTC yang sama. Deviasi 1 detik merusak korelasi urutan kejadian.\n• Log Forwarder Agregator: Menggunakan Logstash/Fluentd terdistribusi di tiap cabang.\n• Noise Filtering: Membuang ping rutin jaringan pada level forwarder."),
        ("Tahap 4: Prasyarat Bisnis & Konteks Operasional", COLOR_EMERALD_GREEN,
         "• Asset Management: Klasifikasi kekritisan server pembayaran inti vs WiFi publik tamu.\n• Definisi Use Case: Merumuskan skenario ancaman spesifik sebelum sistem dioperasikan.\n• SOP & Eskalasi Bertingkat: Penetapan tim penanggung jawab (Jaringan, Aplikasi, SOC) saat alert kritis terpicu.")
    ]
    for idx, (stitle, scolor, sdesc) in enumerate(syllabus):
        col = idx % 2
        row = idx // 2
        x = Inches(0.8 + col * 5.95)
        y = Inches(1.6 + row * 2.5)

        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.75), Inches(2.35))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        tb = s3.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), Inches(5.35), Inches(2.05))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = stitle
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = scolor

        p2 = tf.add_paragraph()
        p2.text = sdesc
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(6)

    prs.save(filepath)
    print(f"[OK] Generated: {filepath}")

# ==================== DECK 3: THREAT DETECTION & INCIDENT SCENARIOS ====================
def build_deck_3(filepath="03_threat_detection_scenarios.pptx"):
    prs = create_base_deck()

    render_cover_slide(
        prs,
        deck_number_str="03 / 05",
        deck_title="Threat Detection Engine & Cyber Incident Scenarios",
        deck_subtitle="Matriks 7 Aturan Korelasi Inti, Analisis Skenario 1 s/d 7, & Studi Kasus Flash Sale vs DDoS",
        target_audience="Security Operation Center (SOC) Tier-1/2 Analysts & Incident Responders"
    )

    # Slide 2: Matriks Aturan Korelasi
    s2 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s2,
        title_text="Matriks Aturan Mesin Korelasi Berbasis Aturan (The Brain)",
        category_pill="MESIN KORELASI",
        subtitle_text="Kondisi ambang batas deteksi anomali real-time di memori aktif."
    )
    rows = 8
    cols = 4
    table_shape = s2.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.0))
    table = table_shape.table
    table.columns[0].width = Inches(1.8)
    table.columns[1].width = Inches(2.8)
    table.columns[2].width = Inches(1.8)
    table.columns[3].width = Inches(5.333)

    headers = ["ID Aturan", "Nama Insiden", "Severity", "Kondisi Ambang Batas Korelasi"]
    for idx, h in enumerate(headers):
        cell = table.cell(0, idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD_ALT
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_NAVY_PRIMARY

    rule_data = [
        ("Rule 1", "DDoS / Botnet Flood", "TINGGI", "> 10 web_request dari 1 IP dalam rentang 10 detik."),
        ("Rule 2", "Impossible Travel", "KRITIS", "2 login_attempt sukses user sama di lokasi beda selang < 1 jam."),
        ("Rule 3", "Distributed Brute Force", "TINGGI", "> 5 login gagal untuk 1 user dari > 3 IP berbeda dalam 1 menit."),
        ("Rule 4", "Off-Hours Anomaly", "MENENGAH", "Aktivitas sukses user manusia di luar jam kerja resmi (00:00 - 05:00)."),
        ("Rule 5", "Data Exfiltration", "KRITIS", "1 user_id download database > 50 kali dalam rentang 1 menit."),
        ("APT Watchlist", "Low & Slow APT Correlation", "KRITIS", "Korelasi recon di Cold Storage dengan exploit di Hot Storage via Greylist."),
        ("Rule OT Sabotage", "Datacenter AC Shutdown", "KRITIS", "Perintah POWER_OFF / SHUTDOWN hardware pendingin via protokol MQTT.")
    ]
    for row_idx, r in enumerate(rule_data):
        for col_idx, text in enumerate(r):
            cell = table.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(9.5)
            if col_idx == 2:
                p.font.bold = True
                if text == "KRITIS":
                    p.font.color.rgb = COLOR_ROSE_RED
                elif text == "TINGGI":
                    p.font.color.rgb = COLOR_AMBER_GOLD
                else:
                    p.font.color.rgb = COLOR_BLUE_ROYAL
            else:
                p.font.color.rgb = COLOR_NAVY_PRIMARY if col_idx < 2 else COLOR_TEXT_MUTED

    # Slide 3: Studi Kasus Flash Sale vs DDoS
    s3 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s3,
        title_text="Investigasi Kasus: Membedakan Flash Sale Bisnis vs DDoS Layer 7",
        category_pill="STUDI KASUS INVESTIGASI",
        subtitle_text="Lonjakan 1 juta request/menit (CPU 98%): Menghindari False Alarm yang mematikan bisnis."
    )
    cases = [
        ("Pembeli Asli (Flash Sale Sah)", COLOR_EMERALD_GREEN,
         "• Distribusi IP: Tersebar acak dari ratusan ribu IP konsumen unik di berbagai ISP perumahan/seluler.\n• Pola Inter-Arrival: Jeda waktu natural bervariasi (membaca spesifikasi, memilih alamat, beralih ke payment gateway).\n• Nilai Bisnis: Transaksi sah menghasilkan konversi penjualan; memblokir trafik ini berdampak pada pemadaman mandiri (self-inflicted DoS)."),
        ("Serangan DDoS (Botnet HTTP Flood)", COLOR_ROSE_RED,
         "• Distribusi IP: Terkonsentrasi dari rentang IP sempit atau klaster proxy anonim.\n• Pola Inter-Arrival: Interval request seragam (< 2 milidetik) tanpa alur navigasi web wajar.\n• Tindakan Respons: SIEM memvalidasi anomali otomasi ini dan menginstruksikan WAF menerapkan challenge CAPTCHA atau rate-limiting pada cluster penyerang.")
    ]
    for idx, (ctitle, ccolor, cdesc) in enumerate(cases):
        x = Inches(0.8 + idx * 5.95)
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(5.75), Inches(5.0))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        top_line = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.6), Inches(5.75), Inches(0.1))
        top_line.fill.solid()
        top_line.fill.fore_color.rgb = ccolor
        top_line.line.fill.background()

        tb = s3.shapes.add_textbox(x + Inches(0.2), Inches(1.85), Inches(5.35), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = ctitle
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = ccolor

        p_b = tf.add_paragraph()
        p_b.text = cdesc
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = COLOR_TEXT_DARK
        p_b.space_before = Pt(10)

    # Slide 4: Skenario 1 s/d 3
    s4 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s4,
        title_text="Bedah Skenario 1 s/d 3: Trafik Normal, DDoS Attack & Impossible Travel",
        category_pill="DEMO SKENARIO (BAGIAN I)",
        subtitle_text="Evaluasi baseline operasional sah, serangan volumetrik, dan anomali identitas fisik vs remote."
    )
    sc13 = [
        ("SKENARIO 1: TRAFIK NORMAL", "Baseline Operasional Sah",
         "• Sumber: sample_logs/web_access_normal_[1..3].log\n• Aktivitas: Karyawan mengakses portal HR & support desk pada jam kerja wajar.\n• Target Verifikasi: Membuktikan SIEM tidak menghasilkan alarm palsu (False Positive Zero).\n• Hasil: 0 Alarm (Trafik Lolos Normal).",
         COLOR_EMERALD_GREEN),
        ("SKENARIO 2: DDOS ATTACK", "Memicu Rule 1 (Severity: TINGGI)",
         "• Sumber: sample_logs/nginx_ddos_flood_[1..3].log\n• Serangan: IP penyerang membombardir endpoint API > 10 request dalam 10 detik.\n• Respons SIEM: Memicu alarm 'DDoS / Botnet' TINGGI.\n• Tindakan: Playbook SOAR Isolate Host memutus trafik.",
         COLOR_AMBER_GOLD),
        ("SKENARIO 3: IMPOSSIBLE TRAVEL", "Memicu Rule 2 (Severity: KRITIS)",
         "• Sumber: sample_logs/vpn_and_gate_access_[1..3].csv\n• Anomali: Login fisik di Jakarta, lalu 1 detik kemudian login VPN dari Frankfurt DE.\n• Kecepatan Fisik: Mustahil berpindah ribuan km dalam 1 detik (pencurian kredensial).\n• Tindakan: Memicu alarm KRITIS & Suspend User.",
         COLOR_ROSE_RED)
    ]
    for idx, (stitle, ssub, sbody, scolor) in enumerate(sc13):
        x = Inches(0.8 + idx * 3.95)
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(3.75), Inches(5.0))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        side = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.6), Inches(0.1), Inches(5.0))
        side.fill.solid()
        side.fill.fore_color.rgb = scolor
        side.line.fill.background()

        tb = s4.shapes.add_textbox(x + Inches(0.2), Inches(1.8), Inches(3.35), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = stitle
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = scolor

        p_s = tf.add_paragraph()
        p_s.text = ssub
        p_s.font.size = Pt(9.5)
        p_s.font.italic = True
        p_s.font.color.rgb = COLOR_TEXT_MUTED

        p_b = tf.add_paragraph()
        p_b.text = sbody
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = COLOR_TEXT_DARK
        p_b.space_before = Pt(8)

    # Slide 5: Skenario 4 s/d 6
    s5 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s5,
        title_text="Bedah Skenario 4 s/d 6: Brute Force, Exfiltration & Whitelisting Blind Spot",
        category_pill="DEMO SKENARIO (BAGIAN II)",
        subtitle_text="Deteksi serangan kredensial multi-sumber, pencurian data orang dalam, dan bahaya kelalaian whitelist."
    )
    sc46 = [
        ("SKENARIO 4: BRUTE FORCE", "Memicu Rule 3 (Severity: TINGGI)",
         "• Sumber: sample_logs/auth_sshd_bruteforce_[1..3].log\n• Taktik: Serangan tebak password SSH terdistribusi melalui 4 node Tor / VPS.\n• Kriteria: > 5 gagal untuk 1 user dari > 3 IP berbeda dalam 1 menit.\n• Hasil: Alarm 'Distributed Brute Force' dibunyikan.",
         COLOR_AMBER_GOLD),
        ("SKENARIO 5: DATA EXFILTRATION", "Memicu Rule 5 (Severity: KRITIS)",
         "• Sumber: sample_logs/postgres_audit_exfiltration_[1..3].jsonl\n• Ancaman: Oknum developer mendownload data PII nasabah > 50 kali dalam 1 menit.\n• Respons SIEM: Deteksi lonjakan volume unduhan dan membunyikan alarm KRITIS.\n• Mitigasi: Pembatasan akses database & suspend kredensial.",
         COLOR_ROSE_RED),
        ("SKENARIO 6: BLIND SPOT WHITELIST", "Demonstrasi Fatal Error & Kelalaian",
         "• Konsep: Admin memasukkan IP penyerang ke daftar Whitelist (/api/whitelist).\n• Dampak: Korelasi engine otomatis MENGABAIKAN log penyerang (Zero Alert).\n• Pembuktian: Menunjukkan bahaya kelalaian whitelisting tanpa review bertingkat.",
         COLOR_PURPLE_SLATE)
    ]
    for idx, (stitle, ssub, sbody, scolor) in enumerate(sc46):
        x = Inches(0.8 + idx * 3.95)
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(3.75), Inches(5.0))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        side = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.6), Inches(0.1), Inches(5.0))
        side.fill.solid()
        side.fill.fore_color.rgb = scolor
        side.line.fill.background()

        tb = s5.shapes.add_textbox(x + Inches(0.2), Inches(1.8), Inches(3.35), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = stitle
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = scolor

        p_s = tf.add_paragraph()
        p_s.text = ssub
        p_s.font.size = Pt(9.5)
        p_s.font.italic = True
        p_s.font.color.rgb = COLOR_TEXT_MUTED

        p_b = tf.add_paragraph()
        p_b.text = sbody
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = COLOR_TEXT_DARK
        p_b.space_before = Pt(8)

    prs.save(filepath)
    print(f"[OK] Generated: {filepath}")

# ==================== DECK 4: ADVANCED APT & OT SABOTAGE ====================
def build_deck_4(filepath="04_advanced_apt_ot_sabotage.pptx"):
    prs = create_base_deck()

    render_cover_slide(
        prs,
        deck_number_str="04 / 05",
        deck_title="Advanced Threats (APT) & OT Physical Infrastructure Sabotage",
        deck_subtitle="Tantangan Hot vs Cold Storage, Solusi Stateful Greylist, dan Deteksi Sabotase Pendingin Datacenter (MQTT)",
        target_audience="Infrastructure Security Leads, OT/BMS Engineers, & Senior Forensics Analysts"
    )

    # Slide 2: Skenario 8 - The Low & Slow APT
    s2 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s2,
        title_text="Skenario 8: The Low & Slow APT (Jebakan Hot vs Cold Storage)",
        category_pill="APT & TEMPORAL BLIND SPOT",
        subtitle_text="Studi kasus serangan lintas retensi (Hari ke-1 vs Hari ke-20) dan mitigasi Stateful Watchlist."
    )
    cards = [
        ("Problem: The Temporal Blind Spot", COLOR_ROSE_RED,
         "• Retensi Hot Storage dibatasi (14 hari) demi efisiensi biaya infrastruktur.\n• Hari ke-1: Penyerang melancarkan Reconnaissance Probe memetakan kerentanan sistem.\n• Log Hari ke-1 dipindahkan ke Cold Storage setelah siklus 14 hari berakhir.\n• Hari ke-20: Penyerang meluncurkan exploit. Mesin korelasi gagal menghubungkan titik karena data recon telah menjadi arsip beku."),
        ("Solusi: Stateful Watchlist & Rehidrasi Forensik", COLOR_EMERALD_GREEN,
         "• Saat probe terdeteksi di Hari ke-1, IP dicatat ke tabel persisten Stateful Watchlist (Greylist).\n• Hari ke-20: Saat IP tersebut aktif kembali, alarm kritis 'APT Low & Slow' terpicu secara instan.\n• On-Demand Rehydration: Log beku Hari ke-1 ditarik kembali secara terarah untuk penyusunan linimasa forensik (Kill Chain Reconstruction).")
    ]
    for idx, (ctitle, ccolor, cdesc) in enumerate(cards):
        x = Inches(0.8 + idx * 5.95)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(5.75), Inches(5.0))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        side = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.6), Inches(0.12), Inches(5.0))
        side.fill.solid()
        side.fill.fore_color.rgb = ccolor
        side.line.fill.background()

        tb = s2.shapes.add_textbox(x + Inches(0.25), Inches(1.85), Inches(5.3), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = ctitle
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = ccolor

        p_b = tf.add_paragraph()
        p_b.text = cdesc
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = COLOR_TEXT_DARK
        p_b.space_before = Pt(10)

    # Slide 3: Arsitektur Storage Bertingkat & The Brute-Force Fallacy
    s3 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s3,
        title_text="Arsitektur Storage Bertingkat: Hot Storage vs Cold Storage",
        category_pill="ARSITEKTUR STORAGE TIERING",
        subtitle_text="Optimalisasi siklus data: Menghindari pemborosan anggaran media penyimpanan tier cepat."
    )
    c_bf = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    c_bf.fill.solid()
    c_bf.fill.fore_color.rgb = COLOR_CARD_BG
    c_bf.line.color.rgb = COLOR_BORDER
    c_bf.line.width = Pt(1)

    tb_bf = s3.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.6))
    tf_bf = tb_bf.text_frame
    tf_bf.word_wrap = True
    p = tf_bf.paragraphs[0]
    p.text = "⚠️ The Brute-Force Fallacy"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ROSE_RED

    bf_text = (
        "Asumsi konvensional: 'Jika penyerang menyerang di Hari ke-20, perbesar Hot Storage menjadi 30 atau 90 hari.'\n\n"
        "Tiga Alasan Kegagalan Pendekatan Ini:\n\n"
        "1. Biaya Eksponensial: Menyimpan petabyte log mentah di tier RAM/NVMe SSD menaikkan biaya infrastruktur data secara tidak proporsional.\n\n"
        "2. Degradasi Latensi Kueri: Indeks pencarian yang membengkak memperlambat evaluasi aturan korelasi (dari < 10ms menjadi detik/menit).\n\n"
        "3. Noise-to-Signal Tinggi: 98% data adalah telemetri rutin; mengalokasikan tier premium untuk data non-kritis memboroskan anggaran."
    )
    p_b = tf_bf.add_paragraph()
    p_b.text = bf_text
    p_b.font.size = Pt(9.5)
    p_b.font.color.rgb = COLOR_TEXT_DARK
    p_b.space_before = Pt(8)

    # Right: Solusi Mini-SIEM
    c_sol = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    c_sol.fill.solid()
    c_sol.fill.fore_color.rgb = COLOR_CARD_BG
    c_sol.line.color.rgb = COLOR_BORDER
    c_sol.line.width = Pt(1)

    tb_sol = s3.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.6))
    tf_sol = tb_sol.text_frame
    tf_sol.word_wrap = True
    p = tf_sol.paragraphs[0]
    p.text = "✔ Solusi Arsitektural Mini-SIEM"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_EMERALD_GREEN

    sol_text = (
        "1. Stateful Entity Tracking (Lightweight Memory):\n"
        "• Alih-alih menahan puluhan gigabyte data mentah, SIEM menyimpan satu baris JSON status di tabel persisten:\n"
        "  {\"ip\": \"198.51.100.77\", \"risk\": \"HIGH\", \"score\": 85, \"reason\": \"recon_day_1\"}\n"
        "• Jejak memori minimal ini dipertahankan lintas siklus retensi untuk dicocokkan saat entitas aktif kembali di Hari ke-20.\n\n"
        "2. Cold Log Rehydration (On-Demand Forensic):\n"
        "• Saat ancaman terverifikasi di Hari ke-20, sistem secara terarah mengekstraksi paket log historis dari arsip dingin:\n"
        "  cold_s3://logs/{yyyy}/{mm}/{dd}/{ip_hash}/\n"
        "• Log ditarik kembali ke memori aktif analis untuk rekonstruksi linimasa serangan (Kill Chain) tanpa full-table scan."
    )
    p_s = tf_sol.add_paragraph()
    p_s.text = sol_text
    p_s.font.size = Pt(9.5)
    p_s.font.color.rgb = COLOR_TEXT_DARK
    p_s.space_before = Pt(8)

    # Slide 4: Skenario 9 - OT Hardware Sabotage via MQTT
    s4 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s4,
        title_text="Bedah Skenario 9: Sabotase Pendingin Datacenter (AC Central via MQTT)",
        category_pill="KEAMANAN SIBER-FISIK (OT/IOT)",
        subtitle_text="Mencegah insiden thermal runaway dan kerusakan hardware fasilitas datacenter bernilai miliaran."
    )
    sc9 = [
        ("1. Konteks Fisik Fasilitas", COLOR_BLUE_ROYAL,
         "• Target Fisik: Unit CRAC-AC-CENTRAL-01, Chiller Plant, atau PAC In-Row Cooling.\n• Protokol Komunikasi: MQTT via broker terhubung ke sensor BMS/SCADA.\n• Dampak Kegagalan: Jika AC mati mendadak, suhu rak server melonjak drastis memicu thermal runaway (server overheat, mati massal, & kerusakan hardware bernilai miliaran rupiah)."),
        ("2. Alur Replay 2 Tahap", COLOR_AMBER_GOLD,
         "• Mirip Skenario 3 (Akses Fisik vs Remote):\n• Event 1 (Status Monitoring):\n  Sensor membaca suhu 18.5°C & status normal via topik telemetry -> Lolos normal (False Positive Zero).\n• Event 2 (Perintah Sabotase):\n  Oknum ilegal mengirim perintah POWER_OFF via topik power."),
        ("3. Deteksi & Respons SOAR", COLOR_ROSE_RED,
         "• Deteksi Mesin SIEM:\n  SIEM mengenali protokol MQTT dan jenis hardware pendingin OT, langsung memicu alarm KRITIS: 'OT Sabotage: Datacenter AC Central Shutdown (MQTT)'.\n• Respons Aktif SOAR:\n  Analis mengisolasi IP penyerang via SOAR Host Quarantine. Perintah MQTT lanjutan langsung di-drop di Gatekeeper (HTTP 403)!")
    ]
    for idx, (ctitle, ccolor, cdesc) in enumerate(sc9):
        x = Inches(0.8 + idx * 3.95)
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(3.75), Inches(5.0))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        side = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.6), Inches(0.1), Inches(5.0))
        side.fill.solid()
        side.fill.fore_color.rgb = ccolor
        side.line.fill.background()

        tb = s4.shapes.add_textbox(x + Inches(0.2), Inches(1.8), Inches(3.35), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = ctitle
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ccolor

        p_b = tf.add_paragraph()
        p_b.text = cdesc
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = COLOR_TEXT_DARK
        p_b.space_before = Pt(8)

    prs.save(filepath)
    print(f"[OK] Generated: {filepath}")

# ==================== DECK 5: SOAR DEFENSE & AI GOVERNANCE ====================
def build_deck_5(filepath="05_soar_defense_ai_governance.pptx"):
    prs = create_base_deck()

    render_cover_slide(
        prs,
        deck_number_str="05 / 05",
        deck_title="SOAR Active Defense, AI Governance & Product Roadmap",
        deck_subtitle="Otomasi Respons Insiden di Gatekeeper, Tata Kelola Human-Supervised AI, & Matriks 13 Fitur Roadmap",
        target_audience="Security Executives, Risk & Compliance Officers, & SOC Managers"
    )

    # Slide 2: SOAR Active Defense Playbook
    s2 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s2,
        title_text="SOAR Active Defense: Network Quarantine & Identity Containment",
        category_pill="OTOMASI RESPONS INSIDEN",
        subtitle_text="Memutus rantai serangan seketika di gerbang masuk Gatekeeper tanpa perlu restart sistem."
    )
    soar_items = [
        ("1. Network Quarantine (Isolate Host)", "POST /api/soar/isolate",
         "Analis mengisolasi IP penyerang langsung dari kartu alert dashboard atau API. Status alert bertransisi menjadi [CONTAINED] dan buffer korelasi aktif dibersihkan untuk mencegah ghost alerts. Seluruh log lanjutan dari IP tersebut ditolak otomatis di Gatekeeper (HTTP 403 HOST_ISOLATED).", COLOR_ROSE_RED),
        ("2. Identity Containment (Suspend User)", "POST /api/soar/suspend-user",
         "Untuk insiden kredensial terkompromi (seperti Impossible Travel), akun user dibekukan seketika. Setiap percobaan autentikasi atau aktivitas lanjutan yang mengatasnamakan user tersebut ditolak di gerbang Gatekeeper (HTTP 403 USER_SUSPENDED).", COLOR_PURPLE_SLATE),
        ("3. Access Restoration (Release Playbook)", "POST /api/soar/release & unsuspend",
         "Setelah ancaman dinetralisir dan investigasi forensik selesai, analis dapat melepas status karantina host atau mengaktifkan kembali akun pengguna dengan satu klik tanpa perlu merestart sistem.", COLOR_EMERALD_GREEN),
        ("4. Immutable Audit Trail", "GET /api/soar/audit",
         "Setiap aksi karantina, pembekuan user, dan pemulihan dicatat secara kronologis dalam jejak audit SOAR (mencakup action, target, alasan analis, dan stempel waktu ISO UTC) untuk akuntabilitas operasional.", COLOR_BLUE_ROYAL)
    ]
    for idx, (title, endpoint, desc, color) in enumerate(soar_items):
        y = Inches(1.6 + idx * 1.25)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.733), Inches(1.1))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        side = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.1), Inches(1.1))
        side.fill.solid()
        side.fill.fore_color.rgb = color
        side.line.fill.background()

        tb = s2.shapes.add_textbox(Inches(1.05), y + Inches(0.12), Inches(11.3), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"{title} — [{endpoint}]"
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(4)

    # Slide 3: Tata Kelola AI & Human-in-the-Loop
    s3 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s3,
        title_text="Tata Kelola AI: Arsitektur Human-Supervised Adaptation (HITL)",
        category_pill="TATA KELOLA & KESELAMATAN AI",
        subtitle_text="Mengeliminasi risiko black-box decision dan self-inflicted DoS melalui supervisi analis berwenang."
    )
    # 3 Risks
    risks = [
        ("Concept Drift Poisoning", "Penyerang APT menyuntikkan deviasi bertahap frekuensi rendah. AI tanpa supervisi menganggap tren pencurian ini sebagai operasional sah.", COLOR_ROSE_RED),
        ("Self-Inflicted DoS", "Aturan adaptif salah mengklasifikasikan lonjakan checkout promo diskon (Flash Sale) sebagai DDoS, melumpuhkan transaksi pelanggan sah.", COLOR_AMBER_GOLD),
        ("Pelanggaran Audit Kepatuhan", "ISO 27001 & PCI-DSS melarang keputusan 'Black-Box' tanpa tiket persetujuan formal dan verifikator penanggung jawab yang jelas.", COLOR_PURPLE_SLATE)
    ]
    for idx, (rtitle, rdesc, rcolor) in enumerate(risks):
        x = Inches(0.8 + idx * 3.95)
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(3.75), Inches(2.1))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        tb = s3.shapes.add_textbox(x + Inches(0.18), Inches(1.75), Inches(3.4), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = rtitle
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = rcolor

        p_d = tf.add_paragraph()
        p_d.text = rdesc
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = COLOR_TEXT_MUTED
        p_d.space_before = Pt(6)

    # 5-step box
    c_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.9), Inches(11.733), Inches(2.8))
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = COLOR_CARD_BG
    c_box.line.color.rgb = COLOR_BORDER
    c_box.line.width = Pt(1)

    tb_c = s3.shapes.add_textbox(Inches(1.0), Inches(4.05), Inches(11.3), Inches(2.5))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    p.text = "🏛️ Blueprint Siklus Aman: Dari Deteksi Kasus Baru hingga Implementasi Produksi"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_PRIMARY

    steps_text = (
        "1. Gatekeeper Ingest: Validasi skema deterministik (Tolak HTTP 422 jika data rusak)\n"
        "2. Dead-Letter Queue (DLQ): Payload anomali baru diisolasi ke antrean karantina terpisah tanpa mengganggu pipeline utama\n"
        "3. AI Suggestion Engine: Sintesis pola klaster anomali dan perumusan 'Candidate Rule' secara terprogram\n"
        "4. Canary Replay Test: Pengujian regresi aturan pada 30 hari data historis; auto-rollback seketika jika rasio False Positive > 2%\n"
        "5. HITL Approval (Shadow Mode): Aturan beroperasi dalam mode bayangan hingga Lead Analis SOC mengotorisasi promosi ke produksi"
    )
    p_s = tf_c.add_paragraph()
    p_s.text = steps_text
    p_s.font.size = Pt(9.5)
    p_s.font.color.rgb = COLOR_TEXT_DARK
    p_s.space_before = Pt(6)

    # Slide 4: Roadmap PM 13 Fitur
    s4 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s4,
        title_text="Roadmap Ekosistem SIEM & Matriks PM 13 Fitur",
        category_pill="ROADMAP PRODUK",
        subtitle_text="Peta jalan pengembangan fitur berbasis dependensi teknis dan logika operasional."
    )
    phases = [
        ("MVP v1: Foundation (Fitur 1 - 6)", COLOR_BLUE_ROYAL,
         "• 1. Log Ingestion Engine (Critical)\n• 2. Data Parsing & Normalization (Critical)\n• 3. Hot Storage & Indexing (Critical)\n• 4. Search & Query Interface (High)\n• 5. Rule-Based Alerting (High)\n• 6. Basic Dashboard & Reporting (Medium)"),
        ("Phase 2: Intelligence (Fitur 7 - 10)", COLOR_PURPLE_SLATE,
         "• 7. Correlation Engine (High - Stateful)\n• 8. Threat Intel Integration (High - IoC)\n• 9. Incident & Case Management (Medium)\n• 10. Cold Storage / Archiving (Medium - Retensi 1-7 Tahun)"),
        ("Phase 3: Advanced (Fitur 11 - 13)", COLOR_AMBER_GOLD,
         "• 11. UEBA (High - Behavioral ML Model)\n• 12. SOAR (High - Automated Playbook)\n• 13. AI Adaptive Rule Generator (High - DLQ, Canary Replay, & HITL Approval)")
    ]
    for idx, (pname, pcolor, plist) in enumerate(phases):
        x = Inches(0.8 + idx * 3.95)
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(3.75), Inches(2.7))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        side = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.6), Inches(0.08), Inches(2.7))
        side.fill.solid()
        side.fill.fore_color.rgb = pcolor
        side.line.fill.background()

        tb = s4.shapes.add_textbox(x + Inches(0.18), Inches(1.75), Inches(3.4), Inches(2.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = pname
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = pcolor

        p_l = tf.add_paragraph()
        p_l.text = plist
        p_l.font.size = Pt(9.5)
        p_l.font.color.rgb = COLOR_TEXT_DARK
        p_l.space_before = Pt(6)

    # Bottom Dependency Logic
    dep_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.5), Inches(11.733), Inches(2.2))
    dep_box.fill.solid()
    dep_box.fill.fore_color.rgb = COLOR_CARD_BG
    dep_box.line.color.rgb = COLOR_BORDER
    dep_box.line.width = Pt(1)

    tb_dep = s4.shapes.add_textbox(Inches(1.0), Inches(4.65), Inches(11.3), Inches(1.9))
    tf_dep = tb_dep.text_frame
    tf_dep.word_wrap = True
    p = tf_dep.paragraphs[0]
    p.text = "💡 Tiga Prinsip Rantai Dependensi Manajemen Produk (PM Logic)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_EMERALD_GREEN

    dep_points = (
        "1. Fondasi Data Sebelum Analitik Lanjut: Ingestion, Normalisasi, dan Penyimpanan Hot Storage harus stabil sebelum mengaktifkan UEBA. Tanpa data historis terstandarisasi, model perilaku tidak memiliki baseline yang andal.\n\n"
        "2. Pengendalian Risiko Sebelum Otomasi Penuh: SOAR diimplementasikan pada Phase 3 setelah Case Management dan Threat Intel matang. Mitigasi otomatis tanpa akurasi tinggi berisiko memblokir trafik operasional yang sah.\n\n"
        "3. Keseimbangan Performa & Efisiensi Biaya: Pemisahan Hot Storage (Phase 1) dan Cold Archive (Phase 2) menjaga performa korelasi real-time tetap optimal sekaligus mengendalikan biaya penyimpanan jangka panjang."
    )
    p_pts = tf_dep.add_paragraph()
    p_pts.text = dep_points
    p_pts.font.size = Pt(9.5)
    p_pts.font.color.rgb = COLOR_TEXT_MUTED
    p_pts.space_before = Pt(6)

    # Slide 5: QA & Kesimpulan
    s5 = prs.slides.add_slide(prs.slide_layouts[6])
    render_light_slide_header(
        s5,
        title_text="Verifikasi Kualitas (29 Tests Passed) & Rekomendasi Eksekutif",
        category_pill="KESIMPULAN & PENJAMINAN MUTU",
        subtitle_text="Hasil pengujian otomatis dan rekomendasi kesiapan menuju lingkungan produksi perbankan/militer."
    )
    # Badge
    b_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.733), Inches(1.1))
    b_card.fill.solid()
    b_card.fill.fore_color.rgb = COLOR_CARD_BG
    b_card.line.color.rgb = COLOR_EMERALD_GREEN
    b_card.line.width = Pt(1.5)

    tb_b = s5.shapes.add_textbox(Inches(1.0), Inches(1.72), Inches(11.3), Inches(0.9))
    tf_b = tb_b.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "✔ PYTEST STATUS: 29 PASSED (100% SUCCESS RATE IN 2.06s)"
    p_b.font.size = Pt(15)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_EMERALD_GREEN

    p_b2 = tf_b.add_paragraph()
    p_b2.text = "Rangkaian pengujian otomatis end-to-end mencakup validasi skema negatif, korelasi memori sliding window, siklus hidup SOAR, dan skenario OT MQTT."
    p_b2.font.size = Pt(10.5)
    p_b2.font.color.rgb = COLOR_TEXT_MUTED
    p_b2.space_before = Pt(4)

    # 4 Conclusion Points
    conclusions = [
        ("Keandalan Gatekeeper Terbukti", "Validasi ketat kontrak skema data dan audit time drift mencegah polusi data telemetri sebelum masuk ke mesin korelasi.", COLOR_BLUE_ROYAL),
        ("Deteksi Multi-Vektor Lengkap", "Mencakup spektrum serangan siber modern: DDoS L7, anomali identitas fisik vs remote, eksfiltrasi database, ancaman APT lintas waktu, hingga sabotase fisik OT/IoT.", COLOR_NAVY_ACCENT),
        ("SOAR Active Defense Menghentikan Serangan", "SOC tidak hanya pasif memantau grafik melainkan mampu melakukan Network Quarantine dan User Suspension secara real-time di level Gatekeeper.", COLOR_EMERALD_GREEN),
        ("Rekomendasi Skalabilitas Produksi", "Migrasi in-memory stateful store ke Redis/Kafka untuk ingestion jutaan event per detik, integrasi LLM Agent untuk playbook auto-remediation, dan ekspansi protokol OT (Modbus, BACnet).", COLOR_PURPLE_SLATE)
    ]
    for idx, (ctitle, cdesc, ccolor) in enumerate(conclusions):
        y = Inches(2.9 + idx * 0.98)
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.733), Inches(0.85))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1)

        side = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.1), Inches(0.85))
        side.fill.solid()
        side.fill.fore_color.rgb = ccolor
        side.line.fill.background()

        tb = s5.shapes.add_textbox(Inches(1.05), y + Inches(0.08), Inches(11.3), Inches(0.68))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"{idx+1}. {ctitle}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY_PRIMARY

        p2 = tf.add_paragraph()
        p2.text = cdesc
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(2)

    prs.save(filepath)
    print(f"[OK] Generated: {filepath}")

def build_all_5_decks():
    print("Building 5 Corporate Light-Theme Cybersecurity Presentations...")
    build_deck_1("01_executive_overview_strategy.pptx")
    build_deck_2("02_data_contracts_gatekeeper.pptx")
    build_deck_3("03_threat_detection_scenarios.pptx")
    build_deck_4("04_advanced_apt_ot_sabotage.pptx")
    build_deck_5("05_soar_defense_ai_governance.pptx")
    print("All 5 decks generated successfully!")

if __name__ == "__main__":
    build_all_5_decks()
