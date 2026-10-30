#!/usr/bin/env python3
"""
Quick Generate Script for Mini-SIEM Presentation
Generates 15 native, checker-valid SVG slides into:
projects/mini_siem_quick_ppt169_20261030/svg_output/
With strict bounds conformity (zero text overflow).
"""

import os
import html

PROJECT_DIR = r"projects/mini_siem_quick_ppt169_20261030"
SVG_DIR = os.path.join(PROJECT_DIR, "svg_output")
os.makedirs(SVG_DIR, exist_ok=True)

def wrap_text(text, max_chars=48):
    words = text.split()
    lines = []
    curr = []
    curr_len = 0
    for w in words:
        if curr_len + len(w) + 1 <= max_chars:
            curr.append(w)
            curr_len += len(w) + 1
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
    if curr:
        lines.append(" ".join(curr))
    return lines

def create_svg_wrapper(page_role, content_xml):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" lang="id-ID" font-family="Segoe UI, Arial, sans-serif" data-pptx-page-role="{page_role}">
  <!-- Canvas Background -->
  <rect id="page-bg" x="0" y="0" width="1280" height="720" fill="#F8FAFC" data-pptx-role="background"/>
  <!-- Top Accent Bar -->
  <rect id="top-bar" x="0" y="0" width="1280" height="6" fill="#1E3A8A" data-pptx-role="decoration"/>
{content_xml}
  <!-- Footer -->
  <g id="footer-group" data-pptx-bounds="72 685 1136 30">
    <line x1="72" y1="685" x2="1208" y2="685" stroke="#E2E8F0" stroke-width="1"/>
    <text x="72" y="704" font-size="12" fill="#64748B">Mini-SIEM Command Center | Tim 'JadiBegini' | Enterprise Cybersecurity Architecture</text>
  </g>
</svg>"""

def render_header(category, title, subtitle=""):
    sub_xml = f'<text x="72" y="108" font-size="14" fill="#64748B">{html.escape(subtitle)}</text>' if subtitle else ""
    return f"""
  <!-- Slide Header -->
  <g id="header-group" data-pptx-bounds="72 32 1136 80">
    <rect id="tag-bg" x="72" y="32" width="340" height="26" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1"/>
    <text x="82" y="49" font-size="11" font-weight="bold" fill="#1E3A8A">{html.escape(category.upper())}</text>
    <text x="72" y="86" font-size="24" font-weight="bold" fill="#0F172A">{html.escape(title)}</text>
    {sub_xml}
  </g>"""

# ==================== SLIDE 01: COVER ====================
def slide_01():
    content = """
  <!-- Cover Hero Card -->
  <g id="hero-card" data-pptx-bounds="72 60 1136 600">
    <rect x="72" y="60" width="1136" height="600" rx="12" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>
    <rect x="72" y="60" width="12" height="600" rx="4" fill="#1E3A8A"/>
    
    <g id="cover-text" transform="translate(120 110)">
      <rect x="0" y="0" width="360" height="30" rx="4" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1"/>
      <text x="14" y="20" font-size="12" font-weight="bold" fill="#1D4ED8">ENTERPRISE CYBERSECURITY SIMULATION</text>
      
      <text x="0" y="80" font-size="44" font-weight="bold" fill="#0F172A">Mini-SIEM Command Center</text>
      
      <text x="0" y="125" font-size="20" font-weight="600" fill="#334155">Security Information &amp; Event Management Simulator</text>
      
      <text x="0" y="170" font-size="15" fill="#64748B">Platform Telemetri Heterogen Real-Time, Gatekeeper RFC Validation, SOAR Active Defense,</text>
      <text x="0" y="195" font-size="15" fill="#64748B">Human-Supervised AI Adaptation &amp; Korelasi 9 Skenario Insiden Siber dan OT Hardware.</text>
      
      <!-- Meta Card Box -->
      <g id="meta-box" transform="translate(0 240)">
        <rect x="0" y="0" width="980" height="150" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1"/>
        
        <text x="24" y="34" font-size="13" font-weight="bold" fill="#1E3A8A">DOKUMEN INDUK &amp; TIM PENGEMBANG</text>
        <text x="24" y="60" font-size="13" fill="#334155">• Dokumen Sumber: mini_siem_product_requirements_document.md (V2.2 Enterprise SOC Edition)</text>
        <text x="24" y="84" font-size="13" fill="#334155">• Tim Pengembang: JadiBegini (Bagus Hanindyo Kusuma, Anand Ferdiansyah, Fitus Yayan Ofnaio Zebua)</text>
        <text x="24" y="108" font-size="13" fill="#334155">• Standard Compliance: ISO 27001, NIST SP 800-92, RFC 5424, OCSF Universal Taxonomy</text>
        <text x="24" y="130" font-size="13" fill="#334155">• Arsitektur Stack: Python 3.11, FastAPI, Pydantic V2, MQTT Broker, SOAR Dynamic Isolation</text>
      </g>
    </g>
  </g>
"""
    return create_svg_wrapper("cover", content)

# ==================== SLIDE 02: PRODUCT OVERVIEW ====================
def slide_02():
    header = render_header("01 / RINGKASAN PRODUK (PRD §1.1)", "6 Nilai Strategis & Solusi Ekosistem Mini-SIEM", "Arsitektur pertahanan aktif hulu-ke-hilir untuk keamanan perimeter, identitas, dan fasilitas.")
    cards = [
        ("1. Gatekeeper Ingestion", "Normalisasi kontrak JSON kanonikal dari beragam sumber log mentah. Menolak data cacat dan clock drift via HTTP 422.", "#0284C7"),
        ("2. Rule Correlation Engine", "Mesin korelasi sliding window stateful di memori mendeteksi serangan L7, brute force, insider threat, dan anomali jam kerja.", "#2563EB"),
        ("3. SOAR Active Defense", "Respons insiden aktif memutus serangan di gerbang: Host Quarantine & User Suspension menolak paket via HTTP 403.", "#059669"),
        ("4. Hot vs Cold Storage (APT)", "Mengatasi temporal blind spot serangan berjarak puluhan hari menggunakan Persistent Stateful Greylist dan rehidrasi forensik.", "#7C3AED"),
        ("5. Universal Log Adapter", "Membaca 27 berkas log fisik autentik (Nginx, Syslog, CSV, PGAudit JSONL, MQTT) dengan timestamp shifting dinamis.", "#D97706"),
        ("6. OT Hardware Monitoring", "Memonitor telemetri sensor dan kontrol hardware fasilitas datacenter via protokol MQTT untuk mencegah sabotase thermal.", "#DC2626")
    ]
    cards_xml = []
    for idx, (title, desc, color) in enumerate(cards):
        col = idx % 3
        row = idx // 3
        x = 72 + col * 390
        y = 135 + row * 260
        lines = wrap_text(desc, max_chars=40)
        lines_xml = "".join([f'<text x="{x+22}" y="{y+100 + i*24}" font-size="13" fill="#475569">{html.escape(l)}</text>' for i, l in enumerate(lines)])
        cards_xml.append(f"""
    <g id="card-{idx+1}" data-pptx-bounds="{x} {y} 365 235">
      <rect x="{x}" y="{y}" width="365" height="235" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
      <rect x="{x}" y="{y}" width="6" height="235" rx="3" fill="{color}"/>
      <text x="{x+22}" y="{y+36}" font-size="16" font-weight="bold" fill="#0F172A">{html.escape(title)}</text>
      <text x="{x+22}" y="{y+64}" font-size="12" font-weight="bold" fill="{color}">ENTERPRISE CAPABILITY</text>
      {lines_xml}
    </g>""")
    return create_svg_wrapper("content", header + "".join(cards_xml))

# ==================== SLIDE 03: ARCHITECTURE ====================
def slide_03():
    header = render_header("02 / ARSITEKTUR SISTEM (PRD §3 & §5)", "Arsitektur 5-Layer Pipeline End-to-End", "Alur telemetri heterogen dari sensor fisik, normalisasi data, korelasi stateful, hingga respons aktif.")
    layers = [
        ("Layer 1: Telemetri Heterogen", "Web Servers (Nginx), SSH Auth (Syslog RFC 3164), Access Gate (CSV), DB Audit (PGAudit JSONL), & Hardware OT (MQTT Broker). 27 berkas log autentik di sample_logs/.", "#2563EB"),
        ("Layer 2: Universal Log Adapter", "app/log_adapter.py: Regex parser multi-format mengonversi log mentah ke kontrak kanonikal LogEvent secara dinamis relatif terhadap waktu nyata NOW().", "#7C3AED"),
        ("Layer 3: Gatekeeper & Schema Validation", "app/main.py: Pydantic V2 schema validation, IPv4 format check, Time Drift verification (<24h). SOAR check: isolated host & suspended user -> HTTP 403 Forbidden.", "#DC2626"),
        ("Layer 4: Correlation Engine (The Brain)", "app/engine.py: Stateful in-memory sliding windows (10s, 60s, 1h), debouncing alert cooldown, Stateful Watchlist APT, dan korelasi sabotase OT.", "#0284C7"),
        ("Layer 5: Storage & SOC Active Console", "Hot In-Memory Cache (5000 logs, 1000 alerts) + Cold Storage Archive. Dashboard web cyberpunk real-time (polling 2 detik) + SOAR Active Defense Panel.", "#059669")
    ]
    layers_xml = []
    for idx, (title, desc, color) in enumerate(layers):
        y = 135 + idx * 105
        layers_xml.append(f"""
    <g id="layer-{idx+1}" data-pptx-bounds="72 {y} 1136 92">
      <rect x="72" y="{y}" width="1136" height="92" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
      <rect x="72" y="{y}" width="8" height="92" rx="4" fill="{color}"/>
      <text x="96" y="{y+30}" font-size="15" font-weight="bold" fill="#0F172A">{html.escape(title)}</text>
      <text x="96" y="{y+56}" font-size="13" fill="#475569">{html.escape(desc)}</text>
    </g>""")
    return create_svg_wrapper("content", header + "".join(layers_xml))

# ==================== SLIDE 04: DATA CONTRACT & GATEKEEPER ====================
def slide_04():
    header = render_header("03 / KONTRAK DATA & GATEKEEPER (PRD §2 & §3A)", "Spesifikasi Kontrak Kanonikal & Ketahanan Validasi", "Standarisasi payload log dan 5 pemeriksaan ketat untuk menolak data cacat di gerbang ingestion.")
    content = header + """
    <!-- Left Column: JSON Schema -->
    <g id="contract-card" data-pptx-bounds="72 135 550 520">
      <rect x="72" y="135" width="550" height="520" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
      <rect x="72" y="135" width="550" height="42" rx="8" fill="#F1F5F9"/>
      <text x="92" y="162" font-size="15" font-weight="bold" fill="#1E3A8A">Canonical JSON Schema (Contract)</text>
      
      <g id="code-block" transform="translate(92 195)" font-family="Consolas, monospace" font-size="12" fill="#0F172A">
        <text y="20">{</text>
        <text y="40" fill="#2563EB">  "timestamp": "2026-10-30T10:15:00Z",</text>
        <text y="60" fill="#2563EB">  "event_type": "login_attempt | web_request |</text>
        <text y="80" fill="#2563EB">                database_download | recon_probe |</text>
        <text y="100" fill="#2563EB">                ot_command | mqtt_command",</text>
        <text y="125" fill="#059669">  "user_id": "sarah_security",</text>
        <text y="145" fill="#059669">  "ip_address": "192.168.1.100",</text>
        <text y="165" fill="#059669">  "location": "Jakarta, ID",</text>
        <text y="185" fill="#059669">  "status": "success | failed",</text>
        <text y="215" fill="#D97706">  // Metadata Opsional Telemetri Hardware OT:</text>
        <text y="235" fill="#D97706">  "protocol": "MQTT",</text>
        <text y="255" fill="#D97706">  "target_device": "CRAC-AC-CENTRAL-01",</text>
        <text y="275" fill="#D97706">  "command": "POWER_OFF | STATUS_REPORT"</text>
        <text y="300">}</text>
      </g>
    </g>

    <!-- Right Column: 5 Gatekeeper Checks -->
    <g id="gatekeeper-card" data-pptx-bounds="650 135 558 520">
      <rect x="650" y="135" width="558" height="520" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
      <rect x="650" y="135" width="558" height="42" rx="8" fill="#FEF2F2"/>
      <text x="674" y="162" font-size="15" font-weight="bold" fill="#991B1B">5 Ketahanan Gatekeeper (Validasi Negatif)</text>
      
      <g id="checks-list" transform="translate(674 200)">
        <text y="10" font-size="13" font-weight="bold" fill="#991B1B">1. Format IPv4 Strict</text>
        <text y="30" font-size="12" fill="#475569">Menolak string rusak atau bukan 4 oktet desimal (misal 999.999.999.999).</text>
        
        <text y="70" font-size="13" font-weight="bold" fill="#991B1B">2. Missing / Null Mandatory Fields</text>
        <text y="90" font-size="12" fill="#475569">Menolak jika user_id, ip_address, atau location kosong atau null.</text>
        
        <text y="130" font-size="13" font-weight="bold" fill="#991B1B">3. Past Time Drift Error (> 24 Jam)</text>
        <text y="150" font-size="12" fill="#475569">Mencegah injeksi log basi lampau (seperti baterai CMOS router reset ke 1970) -> HTTP 422.</text>
        
        <text y="190" font-size="13" font-weight="bold" fill="#991B1B">4. Future Clock Drift Error (> 30 Detik)</text>
        <text y="210" font-size="12" fill="#475569">Menolak stempel waktu di masa depan yang melompat dari waktu sistem riil.</text>
        
        <text y="250" font-size="13" font-weight="bold" fill="#991B1B">5. SOAR Active Rejection</text>
        <text y="270" font-size="12" fill="#475569">Jika IP di isolated_hosts atau user di suspended_users, tolak langsung di HTTP 403 Forbidden.</text>

        <rect x="0" y="320" width="510" height="70" rx="6" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="1"/>
        <text x="16" y="345" font-size="12" font-weight="bold" fill="#166534">✔ HASIL AUDIT GATEKEEPER:</text>
        <text x="16" y="370" font-size="12" fill="#166534">100% data cacat &amp; time drift tertolak secara deterministik tanpa crash server.</text>
      </g>
    </g>
"""
    return create_svg_wrapper("content", content)

# ==================== SLIDE 05: CORRELATION ENGINE ====================
def slide_05():
    header = render_header("04 / ATURAN KORELASI (PRD §3C)", "Matriks 7 Aturan Inti Mesin Korelasi (The Brain)", "Stateful sliding-window di memori mengevaluasi urutan event lintas waktu untuk membunyikan alarm.")
    rules = [
        ("Rule 1", "DDoS / Botnet Flood", "TINGGI", "> 10 web_request dari 1 IP dalam rentang 10 detik.", "#D97706"),
        ("Rule 2", "Impossible Travel", "KRITIS", "2 login sukses user sama di 2 negara berbeda selang < 1 jam.", "#DC2626"),
        ("Rule 3", "Distributed Brute Force", "TINGGI", "> 5 login gagal untuk 1 user dari > 3 IP berbeda dalam 1 menit.", "#D97706"),
        ("Rule 4", "Off-Hours Anomaly", "MENENGAH", "Aktivitas login user manusia sukses di luar jam kerja (00:00 - 05:00).", "#2563EB"),
        ("Rule 5", "Data Exfiltration", "KRITIS", "1 user_id download database > 50 kali dalam 1 menit.", "#DC2626"),
        ("APT Watchlist", "Low & Slow APT Correlation", "KRITIS", "Korelasi recon di Cold Storage dengan exploit di Hot Storage via Greylist.", "#7C3AED"),
        ("Rule OT Sabotage", "Datacenter AC Shutdown (MQTT)", "KRITIS", "Perintah POWER_OFF hardware pendingin datacenter via protokol MQTT.", "#DC2626")
    ]
    rows_xml = []
    for idx, (rid, name, sev, cond, color) in enumerate(rules):
        y = 150 + idx * 72
        rows_xml.append(f"""
    <g id="rule-row-{idx+1}" data-pptx-bounds="72 {y} 1136 62">
      <rect x="72" y="{y}" width="1136" height="62" rx="6" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
      <rect x="72" y="{y}" width="8" height="62" rx="4" fill="{color}"/>
      <text x="96" y="{y+26}" font-size="13" font-weight="bold" fill="#1E3A8A">{html.escape(rid)}</text>
      <text x="96" y="{y+46}" font-size="14" font-weight="bold" fill="#0F172A">{html.escape(name)}</text>
      <rect x="420" y="{y+18}" width="90" height="26" rx="4" fill="{color}" fill-opacity="0.1" stroke="{color}" stroke-width="1"/>
      <text x="465" y="{y+35}" font-size="11" font-weight="bold" fill="{color}" text-anchor="middle">{html.escape(sev)}</text>
      <text x="540" y="{y+36}" font-size="13" fill="#475569">{html.escape(cond)}</text>
    </g>""")
    return create_svg_wrapper("content", header + "".join(rows_xml))

# ==================== SLIDE 06: SCENARIOS 1 - 3 ====================
def slide_06():
    header = render_header("05 / SKENARIO INSIDEN (PRD §4)", "Bedah Skenario 1 s/d 3: Trafik Normal, DDoS & Impossible Travel", "Pengujian baseline tanpa false-alarm, serangan volumetrik L7, dan anomali geolokasi identitas.")
    scenarios = [
        ("SKENARIO 1: TRAFIK NORMAL", "Baseline Operasional Sah", [
            "Sumber: sample_logs/web_access_normal_[1..3].log",
            "Aktivitas: Akses portal HR & CRM pada jam wajar.",
            "Target: Bebas alarm palsu (False Positive Zero).",
            "Hasil: 0 Alarm Dipicu (Trafik Lolos Bersih)."
        ], "#059669"),
        ("SKENARIO 2: DDOS / BOTNET FLOOD", "Memicu Rule 1 (Severity: TINGGI)", [
            "Sumber: sample_logs/nginx_ddos_flood_[1..3].log",
            "Serangan: IP penyerang membanjiri > 10 req/10 detik.",
            "Respon: Alarm 'DDoS / Botnet Flood' TINGGI dipicu.",
            "Mitigasi: SOAR Isolate Host memutus penyerang."
        ], "#D97706"),
        ("SKENARIO 3: IMPOSSIBLE TRAVEL", "Memicu Rule 2 (Severity: KRITIS)", [
            "Sumber: sample_logs/vpn_and_gate_access_[1..3].csv",
            "Anomali: RFID tap Jakarta, VPN login Frankfurt (selang 1s).",
            "Kecepatan: Mustahil berpindah ribuan km seketika.",
            "Mitigasi: Memicu alarm Kritis & Suspend User."
        ], "#DC2626")
    ]
    cards_xml = []
    for idx, (title, sub, bullets, color) in enumerate(scenarios):
        x = 72 + idx * 390
        bullets_xml = "".join([f'<text x="{x+20}" y="{260 + b_idx*42}" font-size="12" fill="#334155">• {html.escape(b)}</text>' for b_idx, b in enumerate(bullets)])
        cards_xml.append(f"""
    <g id="scenario-card-{idx+1}" data-pptx-bounds="{x} 135 365 520">
      <rect x="{x}" y="135" width="365" height="520" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
      <rect x="{x}" y="135" width="365" height="50" rx="8" fill="{color}" fill-opacity="0.08"/>
      <rect x="{x}" y="135" width="6" height="520" rx="3" fill="{color}"/>
      <text x="{x+20}" y="165" font-size="14" font-weight="bold" fill="{color}">{html.escape(title)}</text>
      <text x="{x+20}" y="210" font-size="12" font-weight="600" fill="#64748B">{html.escape(sub)}</text>
      <line x1="{x+20}" y1="230" x2="{x+345}" y2="230" stroke="#E2E8F0" stroke-width="1"/>
      {bullets_xml}
    </g>""")
    return create_svg_wrapper("content", header + "".join(cards_xml))

# ==================== SLIDE 07: SCENARIOS 4 - 6 ====================
def slide_07():
    header = render_header("06 / SKENARIO INSIDEN (PRD §4)", "Bedah Skenario 4 s/d 6: Brute Force, Exfiltration & Whitelisting", "Deteksi brute force terdistribusi, ancaman orang dalam (insider threat), dan risiko blind spot whitelisting.")
    scenarios = [
        ("SKENARIO 4: DISTRIBUTED BRUTE FORCE", "Memicu Rule 3 (Severity: TINGGI)", [
            "Sumber: sample_logs/auth_sshd_bruteforce_[1..3].log",
            "Taktik: Tebak password SSH terdistribusi 4 node Tor.",
            "Kriteria: > 5 gagal login untuk 1 user dari > 3 IP.",
            "Hasil: Alarm Distributed Brute Force berbunyi."
        ], "#D97706"),
        ("SKENARIO 5: DATA EXFILTRATION", "Memicu Rule 5 (Severity: KRITIS)", [
            "Sumber: sample_logs/postgres_audit_exfiltration_[1..3].jsonl",
            "Ancaman: Rogue dev unduh PII > 50 kali dalam 1 menit.",
            "Respon: Alarm KRITIS eksfiltrasi data dibunyikan.",
            "Mitigasi: Pembatasan akses DB & suspend akun user."
        ], "#DC2626"),
        ("SKENARIO 6: CARELESS WHITELISTING", "Demonstrasi Fatal Error & Blind Spot", [
            "Konsep: Admin memasukkan IP jahat ke Whitelist.",
            "Dampak: Mesin korelasi MENGABAIKAN log IP tsb.",
            "Edukasi: Membuktikan risiko fatal bypass whitelist.",
            "Pemulihan: Hapus IP dari whitelist memulihkan alarm."
        ], "#7C3AED")
    ]
    cards_xml = []
    for idx, (title, sub, bullets, color) in enumerate(scenarios):
        x = 72 + idx * 390
        bullets_xml = "".join([f'<text x="{x+20}" y="{260 + b_idx*42}" font-size="12" fill="#334155">• {html.escape(b)}</text>' for b_idx, b in enumerate(bullets)])
        cards_xml.append(f"""
    <g id="scenario-card-{idx+4}" data-pptx-bounds="{x} 135 365 520">
      <rect x="{x}" y="135" width="365" height="520" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
      <rect x="{x}" y="135" width="365" height="50" rx="8" fill="{color}" fill-opacity="0.08"/>
      <rect x="{x}" y="135" width="6" height="520" rx="3" fill="{color}"/>
      <text x="{x+20}" y="165" font-size="14" font-weight="bold" fill="{color}">{html.escape(title)}</text>
      <text x="{x+20}" y="210" font-size="12" font-weight="600" fill="#64748B">{html.escape(sub)}</text>
      <line x1="{x+20}" y1="230" x2="{x+345}" y2="230" stroke="#E2E8F0" stroke-width="1"/>
      {bullets_xml}
    </g>""")
    return create_svg_wrapper("content", header + "".join(cards_xml))

# ==================== SLIDE 08: SCENARIOS 7 & 8 ====================
def slide_08():
    header = render_header("07 / SKENARIO INSIDEN (PRD §4)", "Bedah Skenario 7 & 8: Data Cacat & The Low and Slow APT", "Validasi integritas data telemetri dan penanganan serangan berjarak 20 hari melintasi retensi storage.")
    content = header + """
    <!-- Left: Scenario 7 -->
    <g id="sc7-card" data-pptx-bounds="72 135 550 520">
      <rect x="72" y="135" width="550" height="520" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
      <rect x="72" y="135" width="8" height="520" rx="4" fill="#0284C7"/>
      <text x="96" y="175" font-size="16" font-weight="bold" fill="#0F172A">SKENARIO 7: DATA CACAT &amp; TIME DRIFT</text>
      <text x="96" y="200" font-size="13" font-weight="600" fill="#0284C7">Uji Ketahanan Gatekeeper terhadap Log Korup (HTTP 422)</text>
      
      <g id="sc7-body" transform="translate(96 230)">
        <text y="10" font-size="13" fill="#334155">• Sumber: sample_logs/legacy_corrupted_device_[1..3].log</text>
        
        <text y="50" font-size="13" font-weight="bold" fill="#0F172A">Kasus Uji 1 (Malformed JSON):</text>
        <text y="70" font-size="12" fill="#64748B">Data terpotong di tengah transmisi jaringan -> HTTP 422.</text>
        
        <text y="105" font-size="13" font-weight="bold" fill="#0F172A">Kasus Uji 2 (Missing IP):</text>
        <text y="125" font-size="12" fill="#64748B">Log telemetri tanpa atribut alamat IP pengirim -> Ditolak.</text>
        
        <text y="160" font-size="13" font-weight="bold" fill="#0F172A">Kasus Uji 3 (CMOS Battery Reset 1970):</text>
        <text y="180" font-size="12" fill="#64748B">Timestamp reset ke era UNIX 1970 (> 24 jam lampau) -> Ditolak.</text>

        <text y="215" font-size="13" font-weight="bold" fill="#0F172A">Kasus Uji 4 (Future Time Drift):</text>
        <text y="235" font-size="12" fill="#64748B">Jam melompat ke masa depan (> 30s dari waktu nyata) -> Ditolak.</text>
        
        <rect x="0" y="270" width="500" height="60" rx="6" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="1"/>
        <text x="14" y="295" font-size="12" font-weight="bold" fill="#166534">✔ HASIL GATEKEEPER:</text>
        <text x="14" y="315" font-size="12" fill="#166534">100% data cacat ditolak tanpa menyebabkan server crash.</text>
      </g>
    </g>

    <!-- Right: Scenario 8 -->
    <g id="sc8-card" data-pptx-bounds="650 135 558 520">
      <rect x="650" y="135" width="558" height="520" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
      <rect x="650" y="135" width="8" height="520" rx="4" fill="#7C3AED"/>
      <text x="674" y="175" font-size="16" font-weight="bold" fill="#0F172A">SKENARIO 8: THE LOW &amp; SLOW APT</text>
      <text x="674" y="200" font-size="13" font-weight="600" fill="#7C3AED">Jebakan Hot vs Cold Storage &amp; Stateful Watchlist</text>
      
      <g id="sc8-body" transform="translate(674 230)">
        <text y="10" font-size="13" fill="#334155">• Masalah: Log hanya ditahan di Hot Storage 7-14 hari demi biaya.</text>
        <text y="30" font-size="13" fill="#334155">  Serangan APT Hari ke-20 lolos karena recon sudah ke Cold Storage.</text>
        
        <text y="70" font-size="13" font-weight="bold" fill="#0F172A">Alur Serangan Dua Babak:</text>
        <text y="92" font-size="12" fill="#64748B">• Tanggal 1: Penyerang meluncurkan Reconnaissance Probe (/recon).</text>
        <text y="112" font-size="12" fill="#64748B">• Tanggal 20: Penyerang melancarkan Exploit Request ke server.</text>
        
        <text y="155" font-size="13" font-weight="bold" fill="#059669">Solusi Arsitektural Mini-SIEM:</text>
        <text y="177" font-size="12" fill="#475569">1. Saat recon terdeteksi, IP dicatat ke Stateful Watchlist (Greylist).</text>
        <text y="197" font-size="12" fill="#475569">2. Saat exploit tiba di Tanggal 20, alarm APT Kritis dipicu seketika.</text>
        <text y="217" font-size="12" fill="#475569">3. Log historis dari Cold Storage direhidrasi untuk bukti forensik.</text>

        <rect x="0" y="270" width="510" height="60" rx="6" fill="#FAF5FF" stroke="#E9D5FF" stroke-width="1"/>
        <text x="14" y="295" font-size="12" font-weight="bold" fill="#6B21A8">✔ KEUNGGULAN:</text>
        <text x="14" y="315" font-size="12" fill="#6B21A8">Menghilangkan blind spot tanpa memboroskan RAM storage tier.</text>
      </g>
    </g>
"""
    return create_svg_wrapper("content", content)

# ==================== SLIDE 09: SCENARIO 9 OT SABOTAGE ====================
def slide_09():
    header = render_header("08 / SKENARIO INSIDEN (PRD §4)", "Skenario 9: Sabotase Fisik Datacenter - AC Central Shutdown (MQTT)", "Mendeteksi sabotase fasilitas pendingin datacenter melalui protokol MQTT dan respon karantina SOAR.")
    cols = [
        ("1. KONTEKS HARDWARE OT", "#0284C7", [
            "Target Fisik: Pendingin utama datacenter (CRAC-AC-01 / Chiller).",
            "Protokol: MQTT terhubung ke sistem sensor SCADA/BMS.",
            "Dampak: AC mati mendadak menyebabkan kenaikan suhu rak server dan thermal runaway fatal."
        ]),
        ("2. ALUR REPLAY 2 TAHAP", "#D97706", [
            "Tahap 1: Sensor membaca telemetri suhu wajar (18.5°C) & perintah STATUS_REPORT -> Lolos normal.",
            "Tahap 2: Oknum ilegal mengirim perintah sabotase POWER_OFF via topik MQTT crac01/power."
        ]),
        ("3. DETEKSI &amp; RESPON SOAR", "#DC2626", [
            "Deteksi: SIEM mengenali protokol MQTT & hardware pendingin, memicu alarm KRITIS.",
            "Pertahanan Aktif: Analis mengisolasi IP penyerang via SOAR.",
            "Perintah sabotase lanjutan langsung di-drop di Gatekeeper (HTTP 403)!"
        ])
    ]
    cards_xml = []
    for idx, (title, color, bullets) in enumerate(cols):
        x = 72 + idx * 390
        item_y = 230
        lines_xml = []
        for b in bullets:
            b_lines = wrap_text(b, max_chars=36)
            for l_idx, bl in enumerate(b_lines):
                prefix = "• " if l_idx == 0 else "  "
                lines_xml.append(f'<text x="{x+20}" y="{item_y}" font-size="12" fill="#334155">{prefix}{html.escape(bl)}</text>')
                item_y += 20
            item_y += 12
        cards_xml.append(f"""
    <g id="ot-col-{idx+1}" data-pptx-bounds="{x} 135 365 520">
      <rect x="{x}" y="135" width="365" height="520" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
      <rect x="{x}" y="135" width="365" height="48" rx="8" fill="{color}" fill-opacity="0.08"/>
      <rect x="{x}" y="135" width="6" height="520" rx="3" fill="{color}"/>
      <text x="{x+20}" y="165" font-size="14" font-weight="bold" fill="{color}">{html.escape(title)}</text>
      {"".join(lines_xml)}
    </g>""")
    return create_svg_wrapper("content", header + "".join(cards_xml))

# ==================== SLIDE 10: SOAR ACTIVE DEFENSE ====================
def slide_10():
    header = render_header("09 / INCIDENT RESPONSE PLAYBOOKS (PRD §3D)", "SOAR Active Defense: Network Quarantine & Identity Containment", "Respons insiden aktif memutus rantai serangan langsung di level Gatekeeper secara real-time.")
    playbooks = [
        ("1. Network Quarantine (Isolate Host)", "POST /api/soar/isolate", "Analis mengisolasi IP penyerang dari dashboard. Status alert menjadi [CONTAINED] dan buffer korelasi dibersihkan. Seluruh log lanjutan dari IP tersebut ditolak otomatis di Gatekeeper (HTTP 403 HOST_ISOLATED).", "#DC2626"),
        ("2. Identity Containment (Suspend User)", "POST /api/soar/suspend-user", "Untuk insiden kredensial terkompromi (Impossible Travel), akun user dibekukan seketika. Setiap percobaan autentikasi lanjutan ditolak di gerbang Gatekeeper (HTTP 403 USER_SUSPENDED).", "#7C3AED"),
        ("3. Access Restoration (Release Playbook)", "POST /api/soar/release", "Setelah ancaman dinetralisir, analis dapat melepas karantina host atau mengaktifkan kembali akun pengguna dengan satu klik tanpa perlu merestart server SIEM.", "#059669"),
        ("4. Immutable Audit Trail", "GET /api/soar/audit", "Setiap aksi karantina, pembekuan user, dan pemulihan dicatat kronologis dalam jejak audit SOAR (mencakup action, target, alasan, dan stempel waktu ISO UTC) untuk akuntabilitas.", "#0284C7")
    ]
    cards_xml = []
    for idx, (title, ep, desc, color) in enumerate(playbooks):
        y = 135 + idx * 130
        lines = wrap_text(desc, max_chars=85)
        lines_xml = "".join([f'<text x="96" y="{y+66 + i*20}" font-size="13" fill="#475569">{html.escape(l)}</text>' for i, l in enumerate(lines)])
        cards_xml.append(f"""
    <g id="soar-row-{idx+1}" data-pptx-bounds="72 {y} 1136 115">
      <rect x="72" y="{y}" width="1136" height="115" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
      <rect x="72" y="{y}" width="8" height="115" rx="4" fill="{color}"/>
      <text x="96" y="{y+32}" font-size="16" font-weight="bold" fill="#0F172A">{html.escape(title)}</text>
      <rect x="520" y="{y+16}" width="220" height="24" rx="4" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="1"/>
      <text x="532" y="{y+32}" font-size="11" font-family="Consolas, monospace" font-weight="bold" fill="{color}">{html.escape(ep)}</text>
      {lines_xml}
    </g>""")
    return create_svg_wrapper("content", header + "".join(cards_xml))

# ==================== SLIDE 11: AI GOVERNANCE ====================
def slide_11():
    header = render_header("10 / TATA KELOLA AI (PRD §6)", "Arsitektur Pengaman: Human-Supervised AI Adaptation", "Mencegah keracunan model (poisoning) dan pemadaman tak disengaja dengan verifikasi Human-in-the-Loop.")
    content = header + """
    <!-- Top 3 Risks Cards -->
    <g id="risk-1" data-pptx-bounds="72 135 365 160">
      <rect x="72" y="135" width="365" height="160" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
      <rect x="72" y="135" width="6" height="160" rx="3" fill="#DC2626"/>
      <text x="92" y="165" font-size="14" font-weight="bold" fill="#991B1B">1. Concept Drift Poisoning</text>
      <text x="92" y="195" font-size="12" fill="#475569">Penyerang menyuntikkan anomali berfrekuensi</text>
      <text x="92" y="215" font-size="12" fill="#475569">rendah bertahap. AI tanpa supervisi menganggap</text>
      <text x="92" y="235" font-size="12" fill="#475569">tren jahat tersebut sebagai pola normal.</text>
    </g>
    <g id="risk-2" data-pptx-bounds="457 135 365 160">
      <rect x="457" y="135" width="365" height="160" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
      <rect x="457" y="135" width="6" height="160" rx="3" fill="#D97706"/>
      <text x="477" y="165" font-size="14" font-weight="bold" fill="#B45309">2. Self-Inflicted DoS</text>
      <text x="477" y="195" font-size="12" fill="#475569">Aturan adaptif salah mengklasifikasikan lonjakan</text>
      <text x="477" y="215" font-size="12" fill="#475569">checkout promo (Flash Sale) sebagai DDoS,</text>
      <text x="477" y="235" font-size="12" fill="#475569">sehingga memutus pelanggan sah.</text>
    </g>
    <g id="risk-3" data-pptx-bounds="842 135 365 160">
      <rect x="842" y="135" width="365" height="160" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
      <rect x="842" y="135" width="6" height="160" rx="3" fill="#7C3AED"/>
      <text x="862" y="165" font-size="14" font-weight="bold" fill="#6B21A8">3. Pelanggaran Kepatuhan</text>
      <text x="862" y="195" font-size="12" fill="#475569">ISO 27001 melarang keputusan black-box</text>
      <text x="862" y="215" font-size="12" fill="#475569">tanpa tiket persetujuan formal dan verifikator</text>
      <text x="862" y="235" font-size="12" fill="#475569">penanggung jawab yang jelas.</text>
    </g>

    <!-- Bottom 5-Step Safe Cycle -->
    <g id="safe-cycle" data-pptx-bounds="72 315 1136 340">
      <rect x="72" y="315" width="1136" height="340" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
      <rect x="72" y="315" width="1136" height="42" rx="8" fill="#EFF6FF"/>
      <text x="96" y="342" font-size="15" font-weight="bold" fill="#1E3A8A">🏛️ Blueprint 5-Tahap Siklus Aman: Deteksi Anomali hingga Implementasi Produksi</text>
      
      <g id="steps-list" transform="translate(96 380)">
        <text y="15" font-size="13" font-weight="bold" fill="#0F172A">1. Gatekeeper Ingest:</text>
        <text y="35" font-size="12" fill="#64748B">Validasi deterministik di gerbang (Tolak HTTP 422 jika format atau timestamp rusak).</text>

        <text y="70" font-size="13" font-weight="bold" fill="#0F172A">2. Dead-Letter Queue (DLQ):</text>
        <text y="90" font-size="12" fill="#64748B">Payload anomali baru diisolasi ke antrean karantina tanpa mengganggu pipeline utama.</text>

        <text y="125" font-size="13" font-weight="bold" fill="#0F172A">3. AI Suggestion Engine:</text>
        <text y="145" font-size="12" fill="#64748B">Sintesis pola klaster anomali dan perumusan 'Candidate Rule' secara terprogram.</text>

        <text y="180" font-size="13" font-weight="bold" fill="#0F172A">4. Canary Replay Test:</text>
        <text y="200" font-size="12" fill="#64748B">Pengujian regresi aturan pada 30 hari data historis; auto-rollback jika False Positive > 2%.</text>

        <text y="235" font-size="13" font-weight="bold" fill="#059669">5. HITL Approval (Shadow Mode):</text>
        <text y="255" font-size="12" fill="#059669">Aturan berjalan di mode bayangan hingga Lead Analis menyetujui promosi aturan ke produksi.</text>
      </g>
    </g>
"""
    return create_svg_wrapper("content", content)

# ==================== SLIDE 12: INTEGRATION SYLLABUS ====================
def slide_12():
    header = render_header("11 / PRASYARAT INTEGRASI (PRD §7)", "Prasyarat Integrasi Infrastruktur: Universal Ingestion Syllabus", "Empat tahapan persiapan fondasi data, standarisasi protokol, sinkronisasi NTP, dan konteks bisnis.")
    steps = [
        ("Tahap 1: Fondasi Bahan Baku Log", [
            "Anatomi Log: Membedakan Event, Payload, dan Metadata.",
            "Log Lifecycle: Titik lahir -> Forwarding -> Hot Storage -> Cold Archive.",
            "Kalkulasi EPS: Menghitung beban volume agar buffer korelasi tidak overflow."
        ], "#0284C7"),
        ("Tahap 2: Standarisasi Bahasa", [
            "RFC 5424 Syslog: Format pembungkus standar (Timestamp, Host, Severity).",
            "Kepatuhan NIST SP 800-92: Wajib catat login gagal & eskalasi privilese.",
            "OCSF / CIM Schema: Menyatukan field multi-vendor ke satu taksonomi."
        ], "#2563EB"),
        ("Tahap 3: Prasyarat Jaringan", [
            "Sinkronisasi Waktu Sentral (NTP): Seluruh server merujuk waktu atomik UTC.",
            "Log Forwarder: Menggunakan Fluentd / Logstash terdistribusi di tiap host.",
            "Noise Filtering: Membuang ping rutin internal di level forwarder."
        ], "#D97706"),
        ("Tahap 4: Konteks Bisnis", [
            "Asset Management: Klasifikasi kekritisan server inti vs WiFi publik.",
            "Definisi Use Case: Merumuskan skenario deteksi ancaman sebelum live.",
            "SOP & Eskalasi: Penetapan PIC tim penanggung jawab saat alarm berbunyi."
        ], "#059669")
    ]
    cards_xml = []
    for idx, (title, bullets, color) in enumerate(steps):
        col = idx % 2
        row = idx // 2
        x = 72 + col * 580
        y = 135 + row * 260
        bullets_xml = "".join([f'<text x="{x+20}" y="{y+75 + b_idx*45}" font-size="12" fill="#334155">• {html.escape(b)}</text>' for b_idx, b in enumerate(bullets)])
        cards_xml.append(f"""
    <g id="syl-card-{idx+1}" data-pptx-bounds="{x} {y} 556 240">
      <rect x="{x}" y="{y}" width="556" height="240" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
      <rect x="{x}" y="{y}" width="8" height="240" rx="4" fill="{color}"/>
      <text x="{x+20}" y="{y+36}" font-size="15" font-weight="bold" fill="#0F172A">{html.escape(title)}</text>
      <line x1="{x+20}" y1="{y+50}" x2="{x+536}" y2="{y+50}" stroke="#E2E8F0" stroke-width="1"/>
      {bullets_xml}
    </g>""")
    return create_svg_wrapper("content", header + "".join(cards_xml))

# ==================== SLIDE 13: STORAGE ARCHITECTURE ====================
def slide_13():
    header = render_header("12 / ARSITEKTUR STORAGE (PRD §8)", "Arsitektur Storage Bertingkat: Hot Storage vs Cold Storage", "Mengatasi dilema biaya dan latensi pencarian data dalam mendeteksi ancaman APT jangka panjang.")
    content = header + """
    <!-- Left: The Brute Force Fallacy -->
    <g id="bf-card" data-pptx-bounds="72 135 550 520">
      <rect x="72" y="135" width="550" height="520" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
      <rect x="72" y="135" width="8" height="520" rx="4" fill="#DC2626"/>
      <text x="96" y="175" font-size="16" font-weight="bold" fill="#991B1B">⚠️ Limitasi Linier (The Brute-Force Fallacy)</text>
      <text x="96" y="200" font-size="13" font-weight="600" fill="#64748B">Mengapa memperbesar Hot Storage hingga 90 hari itu gagal?</text>
      
      <g id="bf-body" transform="translate(96 230)">
        <text y="15" font-size="13" font-weight="bold" fill="#0F172A">1. Biaya Eksponensial:</text>
        <text y="35" font-size="12" fill="#64748B">Menyimpan petabyte log mentah di tier RAM/NVMe SSD menaikkan biaya</text>
        <text y="53" font-size="12" fill="#64748B">infrastruktur data secara membengkak tak terkendali.</text>

        <text y="90" font-size="13" font-weight="bold" fill="#0F172A">2. Degradasi Latensi Kueri:</text>
        <text y="110" font-size="12" fill="#64748B">Indeks pencarian yang membesar menurunkan performa evaluasi aturan</text>
        <text y="128" font-size="12" fill="#64748B">korelasi dari &lt; 10ms menjadi hitungan detik hingga menit.</text>

        <text y="165" font-size="13" font-weight="bold" fill="#0F172A">3. Rasio Noise-to-Signal Tinggi:</text>
        <text y="185" font-size="12" fill="#64748B">98% data adalah telemetri rutin; mengalokasikan tier premium untuk</text>
        <text y="203" font-size="12" fill="#64748B">data non-kritis memboroskan anggaran keamanan secara signifikan.</text>
      </g>
    </g>

    <!-- Right: Mini-SIEM Dual Solutions -->
    <g id="sol-card" data-pptx-bounds="650 135 558 520">
      <rect x="650" y="135" width="558" height="520" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
      <rect x="650" y="135" width="8" height="520" rx="4" fill="#059669"/>
      <text x="674" y="175" font-size="16" font-weight="bold" fill="#065F46">✔ Solusi Arsitektural Mini-SIEM</text>
      <text x="674" y="200" font-size="13" font-weight="600" fill="#059669">Stateful Tracking &amp; Rehidrasi Log Terarah</text>
      
      <g id="sol-body" transform="translate(674 230)">
        <text y="15" font-size="13" font-weight="bold" fill="#0F172A">1. Stateful Entity Tracking (Lightweight Memory):</text>
        <text y="35" font-size="12" fill="#475569">Alih-alih menahan puluhan GB log mentah, SIEM hanya menyimpan status:</text>
        <rect x="0" y="45" width="510" height="32" rx="4" fill="#F1F5F9"/>
        <text x="10" y="66" font-size="11" font-family="Consolas, monospace" fill="#1E3A8A">{"ip": "198.51.100.77", "risk": "HIGH", "reason": "recon_day_1"}</text>
        <text y="95" font-size="12" fill="#64748B">Jejak memori minimal ini dipertahankan lintas siklus retensi.</text>

        <text y="140" font-size="13" font-weight="bold" fill="#0F172A">2. Cold Log Rehydration (On-Demand Forensic):</text>
        <text y="160" font-size="12" fill="#475569">Saat exploit tiba di Hari ke-20, sistem mengekstraksi log dari arsip:</text>
        <rect x="0" y="170" width="510" height="32" rx="4" fill="#F1F5F9"/>
        <text x="10" y="191" font-size="11" font-family="Consolas, monospace" fill="#1E3A8A">cold_s3://logs/{yyyy}/{mm}/{dd}/{ip_hash}/</text>
        <text y="220" font-size="12" fill="#64748B">Log ditarik kembali ke memori aktif untuk rekonstruksi Kill Chain.</text>
      </g>
    </g>
"""
    return create_svg_wrapper("content", content)

# ==================== SLIDE 14: ROADMAP ====================
def slide_14():
    header = render_header("13 / ROADMAP PRODUK (PRD §9)", "Roadmap Ekosistem SIEM & Matriks PM 13 Fitur", "Pentahapan fitur dari pondasi MVP, intelijen analitik, hingga otomasi tingkat lanjut.")
    phases = [
        ("MVP v1: Foundation (Fitur 1 - 6)", [
            "1. Log Ingestion Engine (Critical)",
            "2. Data Parsing & Normalization (Critical)",
            "3. Hot Storage & Indexing (Critical)",
            "4. Search & Query Interface (High)",
            "5. Rule-Based Alerting (High)",
            "6. Basic Dashboard & Reporting (Medium)"
        ], "#0284C7"),
        ("Phase 2: Intelligence (Fitur 7 - 10)", [
            "7. Correlation Engine (High - Stateful)",
            "8. Threat Intel Integration (High - IoC)",
            "9. Incident & Case Management (Medium)",
            "10. Cold Storage / Archiving (Retensi 1-7 Thn)"
        ], "#7C3AED"),
        ("Phase 3: Advanced (Fitur 11 - 13)", [
            "11. UEBA (Behavioral ML Model)",
            "12. SOAR (Automated Playbooks)",
            "13. AI Adaptive Rule Generator",
            "    (DLQ, Canary Replay, & HITL Approval)"
        ], "#059669")
    ]
    cards_xml = []
    for idx, (pname, plist, color) in enumerate(phases):
        x = 72 + idx * 390
        bullets_xml = "".join([f'<text x="{x+20}" y="{205 + b_idx*26}" font-size="11" fill="#334155">• {html.escape(b)}</text>' for b_idx, b in enumerate(plist)])
        cards_xml.append(f"""
    <g id="phase-card-{idx+1}" data-pptx-bounds="{x} 135 365 240">
      <rect x="{x}" y="135" width="365" height="240" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.2"/>
      <rect x="{x}" y="135" width="365" height="38" rx="8" fill="{color}" fill-opacity="0.08"/>
      <rect x="{x}" y="135" width="6" height="240" rx="3" fill="{color}"/>
      <text x="{x+20}" y="160" font-size="13" font-weight="bold" fill="{color}">{html.escape(pname)}</text>
      {bullets_xml}
    </g>""")
    
    bottom_pm = """
    <!-- Bottom PM Dependency Box -->
    <g id="pm-dependency" data-pptx-bounds="72 395 1136 260">
      <rect x="72" y="395" width="1136" height="260" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
      <rect x="72" y="395" width="1136" height="40" rx="8" fill="#F8FAFC"/>
      <text x="96" y="420" font-size="14" font-weight="bold" fill="#0F172A">💡 Tiga Prinsip Rantai Dependensi Manajemen Produk (PM Logic)</text>
      
      <g id="pm-points" transform="translate(96 455)">
        <text y="10" font-size="13" font-weight="bold" fill="#1E3A8A">1. Fondasi Data Sebelum Analitik Lanjut:</text>
        <text y="30" font-size="12" fill="#475569">Ingestion dan Hot Storage harus stabil sebelum UEBA aktif. Tanpa data historis terstandarisasi, model perilaku tidak memiliki baseline yang andal.</text>

        <text y="70" font-size="13" font-weight="bold" fill="#1E3A8A">2. Pengendalian Risiko Sebelum Otomasi Penuh:</text>
        <text y="90" font-size="12" fill="#475569">SOAR diimplementasikan pada Phase 3 setelah Case Management matang. Mitigasi otomatis tanpa akurasi tinggi berisiko memblokir trafik operasional sah.</text>

        <text y="130" font-size="13" font-weight="bold" fill="#1E3A8A">3. Keseimbangan Performa &amp; Efisiensi Biaya:</text>
        <text y="150" font-size="12" fill="#475569">Pemisahan Hot Storage dan Cold Archive menjaga performa korelasi real-time optimal sekaligus mengendalikan anggaran.</text>
      </g>
    </g>
"""
    return create_svg_wrapper("content", header + "".join(cards_xml) + bottom_pm)

# ==================== SLIDE 15: QA & CONCLUSION ====================
def slide_15():
    header = render_header("14 / KESIMPULAN & QA (PRD §5)", "Verifikasi Kualitas (29 Tests Passed) & Kesimpulan Strategis", "Seluruh fungsionalitas tervalidasi secara otomatis melalui pengujian regresi deterministik.")
    content = header + """
    <!-- Green Hero Badge -->
    <g id="qa-badge" data-pptx-bounds="72 135 1136 95">
      <rect x="72" y="135" width="1136" height="95" rx="8" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.5"/>
      <rect x="72" y="135" width="10" height="95" rx="4" fill="#059669"/>
      <text x="100" y="172" font-size="18" font-weight="bold" fill="#166534">✔ PYTEST STATUS: 29 PASSED (100% SUCCESS RATE IN 2.06s)</text>
      <text x="100" y="202" font-size="13" fill="#15803D">Rangkaian pengujian mencakup validasi skema negatif, korelasi sliding window, siklus hidup SOAR, dan skenario OT MQTT.</text>
    </g>

    <!-- 4 Conclusion Cards -->
    <g id="c-1" data-pptx-bounds="72 250 1136 85">
      <rect x="72" y="250" width="1136" height="85" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
      <rect x="72" y="250" width="8" height="85" rx="4" fill="#0284C7"/>
      <text x="96" y="280" font-size="15" font-weight="bold" fill="#0F172A">1. Keandalan Gatekeeper Terbukti</text>
      <text x="96" y="308" font-size="13" fill="#475569">Validasi ketat kontrak skema data dan audit time drift mencegah polusi data telemetri sebelum masuk ke mesin korelasi.</text>
    </g>
    <g id="c-2" data-pptx-bounds="72 350 1136 85">
      <rect x="72" y="350" width="1136" height="85" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
      <rect x="72" y="350" width="8" height="85" rx="4" fill="#2563EB"/>
      <text x="96" y="380" font-size="15" font-weight="bold" fill="#0F172A">2. Deteksi Multi-Vektor Lengkap</text>
      <text x="96" y="408" font-size="13" fill="#475569">Mencakup spektrum serangan siber modern: DDoS L7, anomali identitas fisik vs remote, eksfiltrasi database, hingga sabotase fisik OT/IoT.</text>
    </g>
    <g id="c-3" data-pptx-bounds="72 450 1136 85">
      <rect x="72" y="450" width="1136" height="85" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
      <rect x="72" y="450" width="8" height="85" rx="4" fill="#059669"/>
      <text x="96" y="480" font-size="15" font-weight="bold" fill="#0F172A">3. SOAR Active Defense Menghentikan Serangan</text>
      <text x="96" y="508" font-size="13" fill="#475569">SOC tidak hanya pasif memantau grafik melainkan mampu melakukan Network Quarantine dan User Suspension secara real-time di level Gatekeeper.</text>
    </g>
    <g id="c-4" data-pptx-bounds="72 550 1136 85">
      <rect x="72" y="550" width="1136" height="85" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
      <rect x="72" y="550" width="8" height="85" rx="4" fill="#7C3AED"/>
      <text x="96" y="580" font-size="15" font-weight="bold" fill="#0F172A">4. Rekomendasi Skalabilitas Produksi</text>
      <text x="96" y="608" font-size="13" fill="#475569">Migrasi stateful store ke Redis/Kafka untuk jutaan EPS, integrasi LLM Agent untuk playbook auto-remediation, dan ekspansi protokol OT (Modbus, BACnet).</text>
    </g>
"""
    return create_svg_wrapper("ending", content)

def main():
    slides = [
        ("01_cover.svg", slide_01()),
        ("02_product_overview.svg", slide_02()),
        ("03_architecture.svg", slide_03()),
        ("04_data_contract.svg", slide_04()),
        ("05_correlation_matrix.svg", slide_05()),
        ("06_scenarios_1_3.svg", slide_06()),
        ("07_scenarios_4_6.svg", slide_07()),
        ("08_scenarios_7_8.svg", slide_08()),
        ("09_scenario_9_ot.svg", slide_09()),
        ("10_soar_defense.svg", slide_10()),
        ("11_ai_governance.svg", slide_11()),
        ("12_integration_syllabus.svg", slide_12()),
        ("13_storage_architecture.svg", slide_13()),
        ("14_product_roadmap.svg", slide_14()),
        ("15_qa_conclusion.svg", slide_15())
    ]
    for filename, svg_str in slides:
        out_path = os.path.join(SVG_DIR, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_str)
        print(f"[OK] Authored SVG: {out_path}")
    print(f"\nSuccessfully generated {len(slides)} SVG slides in {SVG_DIR}")

if __name__ == "__main__":
    main()
