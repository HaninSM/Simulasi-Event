# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Primary User**: SOC Analyst & Incident Responder bertugas memantau keamanan sistem secara real-time, mengidentifikasi anomali, menganalisis korelasi insiden, dan mengeksekusi tindakan mitigasi aktif (SOAR) dalam hitungan detik.
- **Secondary Users**: IT Security Lead & Auditor Keamanan yang meninjau jejak audit (*audit trails*), mengevaluasi aturan deteksi, serta mengelola pengecualian (*whitelist tuning*) dengan pertimbangan risiko *blind spot*.

## Product Purpose

Menyediakan sistem pusat komando keamanan siber (*Mini-SIEM Command Center*) terpadu yang memadukan pengawasan log real-time dengan kemampuan respons otomatis dan aktif (*SOAR Closed-Loop Defense*). Produk ini bertujuan memangkas *Mean Time to Detect* (MTTD) dan *Mean Time to Respond* (MTTR) tanpa memerlukan biaya dan kompleksitas platform SIEM enterprise yang membengkak.

## Positioning

**Closed-Loop Active Defense (SOAR)**: Tidak seperti dasbor monitoring pasif yang hanya menumpuk peringatan tanpa daya tindak, Mini-SIEM Command Center menghubungkan deteksi insiden langsung dengan gerbang pertahanan aktif (*Gatekeeper*). Operator dapat langsung mengkarantina IP host atau menangguhkan akun user dengan penolakan instan (HTTP 403 Forbidden) di lapisan proksi, diperkaya dengan Cyber Threat Intelligence (CTI AbuseIPDB) dan simulator pengujian skenario serangan bawaan.

## Operating Context

- **Environment**: Konsol monitoring SOC (layar command center 24/7 di bawah pencahayaan redup atau workstation analis keamanan).
- **Workflows**:
  1. Monitoring aliran log masuk dan feed peringatan insiden secara kontinu.
  2. Evaluasi ancaman menggunakan pengayaan CTI (negara, ASN, skor abuse, aktor ancaman).
  3. Eksekusi karantina SOAR terhadap host atau penangguhan akun yang terinfeksi.
  4. Pengujian dan validasi aturan korelasi melalui Interactive Scenario Simulator.
  5. Penyetelan daftar putih (*whitelist tuning*) untuk mencegah *false positives* dengan pemahaman risiko celah keamanan (*detection blind spot*).

## Capabilities and Constraints

- **Confirmed Capabilities**:
  - Mesin korelasi 6 rule ancaman utama: SSH Brute Force (`RULE-BRUTE-001`), SQL Injection (`RULE-SQLI-002`), Impossible Travel (`RULE-TRAVEL-003`), Off-Hours Anomaly (`RULE-ANOM-004`), OT Sensor/AC Sabotage (`RULE-OT-005`), dan High Volume Data Exfiltration (`RULE-EXFIL-006`).
  - Mitigasi SOAR aktif: Isolasi Host (IP quarantine) dan Penangguhan Akun Pengguna (User suspend) yang terintegrasi dengan Gatekeeper HTTP 403 middleware.
  - Dual-Mode Incident Stream (UI/UX Pro Max): Peralihan instan antara linimasa kronologis vertikal dan peringkat keparahan tertinggi (*Highest Severity Ranking: KRITIS &rarr; TINGGI &rarr; MENENGAH*) lengkap dengan sub-filter chips dan persistensi state di `localStorage`.
  - Anti-Cache Architecture: Versioning query parameter (`?v=2.4.2`), global button CSS reset, dan FastAPI anti-cache middleware response header untuk menjamin konsistensi rendering UI di semua peramban.
  - Whitelist IP bypass korelasi dengan peringatan risiko *detection blind spot*.
  - Simulator skenario serangan interaktif terpadu untuk pengujian instan (9 skenario autentik & demo SOAR).
  - Audit trail forensik yang mencatat seluruh aksi SOAR dan modifikasi whitelist.
  - Arsitektur: Backend FastAPI (Python 3.11), Database in-memory stateful store, Frontend Vanilla JS/HTML5/CSS3 tanpa ketergantungan runtime npm/node.
- **Constraints**:
  - Single-instance in-memory stateful store (belum mendukung cluster multi-node enterprise).
  - Refresh data polling HTTP 2 detik berbasis client-side dengan optimalisasi background pause.

## Brand Commitments

- **Nama**: Mini-SIEM Command Center / SentinelAI
- **Voice & Tone**: Presisi, tenang, tegas, teknis militer/SOC (*mission-critical, decisive, zero-nonsense*).
- **Identitas Visual**: SOC Dark Command Center (`#0a0e17` deep terminal, aksen cyan, status badges terkalibrasi, tipografi teknis sans-serif `IBM Plex Sans` dipadukan dengan `Fira Code` monospace).

## Evidence on Hand

- Implementasi backend lengkap pada [`app/main.py`](file:///d:/Simulasi-Event/app/main.py), [`app/engine.py`](file:///d:/Simulasi-Event/app/engine.py), dan [`app/models.py`](file:///d:/Simulasi-Event/app/models.py).
- Antarmuka frontend mandiri pada [`app/static/index.html`](file:///d:/Simulasi-Event/app/static/index.html), [`app/static/style.css`](file:///d:/Simulasi-Event/app/static/style.css), dan [`app/static/app.js`](file:///d:/Simulasi-Event/app/static/app.js).
- Suite pengujian otomasi 41 test cases di [`test_siem.py`](file:///d:/Simulasi-Event/test_siem.py) (100% lulus).
- Pemindaian detektor Impeccable: 0 errors, 0 warnings pada seluruh file frontend utama.

## Product Principles

1. **Closed-Loop Over Pure Visibility**: Deteksi tanpa opsi aksi mitigasi instan adalah separuh keamanan. Setiap insiden kritis harus memiliki tombol penanganan langsung yang berdampak deterministik.
2. **Zero Operator Ambiguity**: Tingkat keparahan (Kritis, Tinggi, Menengah), skor reputasi CTI, dan status karantina harus langsung terbaca dalam hitungan detik tanpa analis harus membuka tab eksternal.
3. **Auditability By Default**: Setiap tindakan tanggap insiden dan modifikasi konfigurasi pertahanan wajib memiliki jejak audit forensik yang transparan dan dapat dipertanggungjawabkan.
4. **Low-Friction Resilience**: Antarmuka harus tetap efisien saat menangani ratusan event, tidak menguras bandwidth saat berada di latar belakang, dan ramah aksesibilitas di semua perangkat (mouse, keyboard, touch screen).

## Accessibility & Inclusion

- Memenuhi standar WCAG AA dengan rasio kontras warna teks ≥ 4.5:1 terhadap latar belakang gelap.
- Navigasi keyboard komprehensif dengan WAI-ARIA focus trap pada modal dialog, penutupan `Escape` global, dan `focus-visible` offset jelas.
- Mendukung preferensi `prefers-reduced-motion` dan target sentuh minimal 44px pada layar sentuh (*coarse pointers*).
