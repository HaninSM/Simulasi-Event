# 📄 PRD.md: Mini-SIEM Simulator (V2.2 - Enterprise SOC, Real Log Replay & SOAR Active Defense Edition)

## 1. Ringkasan Produk & Latar Belakang Desain

### 1.1 Deskripsi Produk
**Mini-SIEM** adalah aplikasi simulasi *Security Information and Event Management* berskala kecil berbasis API. Sistem ini dirancang untuk mendemonstrasikan secara *real-time* bagaimana pusat komando operasi keamanan (SOC):
1. Menerima, memvalidasi, dan menormalisasi log telemetri heterogen (*Gatekeeper Ingestion*).
2. Membaca format log autentik dunia nyata (Nginx/Apache Combined, Linux Syslog RFC 3164, RFID Access CSV, PostgreSQL PGAudit JSONL, dan MQTT OT JSONL) melalui Universal Log Adapter.
3. Mendeteksi anomali melalui mesin korelasi berbasis aturan (*Rule-based Correlation Engine*).
4. Menangani *Alert Fatigue* dengan debouncing cerdas (*alert cooldown*).
5. Memitigasi kegagalan transmisi data cacat dan *Time Drift Error* (HTTP 422).
6. Mengungkap bahaya *Blind Spot* akibat *Careless Whitelisting* dan serangan *Low & Slow APT* (tantangan *Hot vs Cold Storage*).
7. Menjalankan penanganan insiden aktif melalui **SOAR Playbook (Host Containment / Network Quarantine & User Suspension)** yang memutus paket penyerang di gerbang masuk (*Gatekeeper HTTP 403 Dropped*).
8. Mendeteksi upaya sabotase hardware fisik fasilitas datacenter (AC Central / Chiller) via protokol telemetri IoT/OT (**MQTT**).

### 1.2 Profil Tim Pengembang: "JadiBegini"
Proyek simulasi Mini-SIEM Command Center dikembangkan oleh Tim **JadiBegini**:
* **Bagus Hanindyo Kusuma (Lead)**: Scrum Master & Agile Coach dengan keahlian kepemimpinan *servant leadership*, berpengalaman luas sebagai Program Manager dan IT Project Manager.
* **Anand Ferdiansyah**: Mahasiswa Aktif Program Karyawan di Universitas Pamulang.
* **Fitus Yayan Ofnaio Zebua**: Mahasiswa Aktif Program Karyawan di Universitas Pamulang dan aktif sebagai Driver Grab.

### 1.3 Filosofi & Analogi Fundamental SIEM
* **Analogi Gedung Perkantoran Raksasa:** Gedung bertingkat dengan ratusan pintu, turnstile, dan CCTV tidak mungkin diawasi manual oleh satu satpam. SIEM berfungsi sebagai ruang kendali sentral yang mengonsolidasikan seluruh sensor. Jika kartu akses "Budi" di-tap di turnstile lobi sementara workstation Budi aktif di lantai 15, SIEM langsung membunyikan alarm korelasi.
* **SIEM vs. Antivirus:** Antivirus hanya menjaga satu mesin (*endpoint* lokal). SIEM mengawasi seluruh perimeter dengan menerima telemetri dari antivirus, firewall, switch jaringan, database, dan workstation untuk melihat pola serangan terkoordinasi (*lateral movement*).
* **Security Information ("SI") vs. Event Management ("EM"):** "SI" mengumpulkan arsip historis untuk audit kepatuhan. "EM" menganalisis, memvalidasi aturan, dan mengorelasikan log secara *real-time* saat insiden sedang berlangsung.

---

## 2. Spesifikasi Data (Data Contracts)

Semua log yang masuk ke sistem (Ingestion) wajib memenuhi format JSON kanonikal berikut. Sistem Gatekeeper akan menolak data yang tidak mematuhi kontrak ini:
```json
{
  "timestamp": "YYYY-MM-DDThh:mm:ssZ",
  "event_type": "login_attempt | web_request | database_download | recon_probe | ot_command | mqtt_command",
  "user_id": "string (non-empty)",
  "ip_address": "string (IPv4)",
  "location": "string (non-empty)",
  "status": "success | failed",
  "protocol": "MQTT | Modbus | BACnet (optional)",
  "device_type": "AC_CENTRAL | CRAC | CHILLER (optional)",
  "target_device": "CRAC-AC-CENTRAL-01 (optional)",
  "command": "POWER_OFF | STATUS_REPORT | KILL_SWITCH (optional)",
  "topic": "datacenter/cooling/crac01/power (optional)"
}
```

---

## 3. Fitur Utama & Kriteria Penerimaan

### Fitur A: API Ingestion & Validasi (Gatekeeper)
* Menerima log melalui `POST /api/ingest`.
* **SOAR Active Enforcement:** 
  * Jika IP pengirim tercatat dalam daftar karantina (`isolated_hosts`), Gatekeeper langsung menolak log dengan status **HTTP 403 (Forbidden: HOST_ISOLATED)** dan menambah metrik *Blocked Containment Traffic*.
  * Jika `user_id` pengirim dibekukan (`suspended_users`), Gatekeeper menolak log dengan status **HTTP 403 (Forbidden: USER_SUSPENDED)**.
* **Validasi Negatif:** Sistem merespons HTTP 422 (*Unprocessable Entity*) dan menolak log jika:
  * Format JSON rusak (sintaks terputus) atau atribut wajib (seperti IP) hilang/bernilai `null`.
  * Format IP bukan IPv4 valid (misal: `999.999.999.999`).
  * `timestamp` berasal dari lebih dari 24 jam lampau atau masa depan (*Time Drift Error*).

### Fitur B: Universal Log Adapter, 27 Variant Sample Logs & Real-World Replay
* Modul `app/log_adapter.py` membaca berkas log fisik dari direktori `sample_logs/`. Masing-masing skenario (1 s/d 9) memiliki **3 varian berkas log realistis** (total 27 berkas):
  * **Skenario 1 (Trafik Normal):** `web_access_normal_1.log` (E-Commerce), `web_access_normal_2.log` (HR Portal), `web_access_normal_3.log` (Support Desk).
  * **Skenario 2 (DDoS Attack):** `nginx_ddos_flood_1.log` (IP `45.33.32.156`), `nginx_ddos_flood_2.log` (IP `194.26.29.112`), `nginx_ddos_flood_3.log` (IP `185.220.101.45`).
  * **Skenario 3 (Impossible Travel):** `vpn_and_gate_access_1.csv` (`sarah_security`: Jakarta vs Frankfurt), `vpn_and_gate_access_2.csv` (`budi_finance`: Surabaya vs Dallas), `vpn_and_gate_access_3.csv` (`ahmad_devops`: Singapore vs Moscow).
  * **Skenario 4 (Distributed Brute Force):** `auth_sshd_bruteforce_1.log` (`admin_corp` via Tor), `auth_sshd_bruteforce_2.log` (`root` via botnet), `auth_sshd_bruteforce_3.log` (`svc_deploy` via Cloud VPS).
  * **Skenario 5 (Data Exfiltration):** `postgres_audit_exfiltration_1.jsonl` (`dev_rogue`), `postgres_audit_exfiltration_2.jsonl` (`contractor_analyst`), `postgres_audit_exfiltration_3.jsonl` (`intern_badactor`).
  * **Skenario 6 (Careless Whitelist):** `careless_whitelist_attack_1.log` (IP `203.0.113.88`), `careless_whitelist_attack_2.log` (IP `198.51.100.50`), `careless_whitelist_attack_3.log` (IP `192.0.2.77`).
  * **Skenario 7 (Data Cacat/Drift):** `legacy_corrupted_device_1.log` (IoT Gateway), `legacy_corrupted_device_2.log` (Branch Router), `legacy_corrupted_device_3.log` (SCADA PLC).
  * **Skenario 8 (Low & Slow APT):** `apt_recon_and_exploit_1.log` (IP `198.51.100.77`), `apt_recon_and_exploit_2.log` (IP `203.0.113.144`), `apt_recon_and_exploit_3.log` (IP `192.0.2.199`).
  * **Skenario 9 (OT Hardware Sabotage - AC Central Shutdown via MQTT):** `mqtt_datacenter_hvac_1.jsonl` (CRAC-AC-CENTRAL-01 / Hall A), `mqtt_datacenter_hvac_2.jsonl` (HVAC-CHILLER-MAIN-02 / Plant), `mqtt_datacenter_hvac_3.jsonl` (PAC-SERVER-ROW-C03 / AI Cluster).
* **Random Variant Selection & Deterministic Overrides:** Simulator otomatis memilih acak 1 dari 3 varian berkas log per skenario (`variant=None` -> `random.choice([1, 2, 3])`). Analis dapat memilih varian spesifik secara deterministik via query parameter `?variant=1..3` atau flag CLI `--variant 1..3`.
* **Dynamic Timestamp Shifting:** Mengonversi timestamp historis secara dinamis relatif terhadap waktu nyata sistem (`NOW()`) saat di-replay, sehingga data audit asli tetap utuh sekaligus lolos Gatekeeper Time Drift Check.
* Endpoint `POST /api/simulator/replay?scenario={1..9}&variant={1..3}`: Replay backend terintegrasi untuk CLI maupun Dashboard Browser.

### Fitur C: Mesin Korelasi Berbasis Aturan (The Brain)
Sistem memproses log di memori dan memicu alarm berdasarkan aturan berikut:
1. **DDoS / Botnet (Level: TINGGI):** > 10 `web_request` dari 1 `ip_address` yang sama dalam rentang 10 detik.
2. **Impossible Travel (Level: KRITIS):** 2 `login_attempt` sukses dari 1 `user_id` yang sama di `location` berbeda dalam waktu < 1 jam.
3. **Distributed Brute Force (Level: TINGGI):** > 5 `login_attempt` gagal untuk 1 `user_id` yang sama, berasal dari > 3 `ip_address` berbeda dalam 1 menit.
4. **Off-Hours Anomaly (Level: MENENGAH):** Aktivitas `status: success` oleh pengguna manusia di luar jam operasional kantor (00:00 - 05:00 waktu lokal).
5. **Data Exfiltration / Insider Threat (Level: KRITIS):** 1 `user_id` melakukan `database_download` > 50 kali dalam rentang 1 menit.
6. **Advanced Persistent Threat (APT) / Temporal Correlation:** Korelasi jejak *reconnaissance* dari *Cold Storage* yang diaktifkan kembali (*rehydrated*) terhadap *exploit request* di *Hot Storage* menggunakan tabel stateful *Suspicious Greylist/Watchlist*.
7. **OT / Industrial Control Sabotage (Level: KRITIS):** Deteksi perintah tidak sah (`POWER_OFF`, `EMERGENCY_SHUTDOWN`, `STOP_COOLING`, `KILL_SWITCH`) via protokol **MQTT** yang menargetkan perangkat hardware pendingin datacenter (AC Central / CRAC / Chiller), yang berpotensi memicu kegagalan termal katastropik (*thermal runaway*).

### Fitur D: SOAR Active Defense (Host & Identity Containment Playbook)
* **Karantina Host Jaringan (`POST /api/soar/isolate`):**
  * Analis dapat mengisolasi host target dengan satu klik langsung dari kartu alert atau panel SOAR.
  * Status alert bertransisi dari `NEW` menjadi `CONTAINED` (animasi kedip darurat dimatikan).
  * Data host yang diisolasi dipurged dari buffer window aktif untuk mencegah ghost correlation.
* **Pembekuan Akun Pengguna (`POST /api/soar/suspend-user`):**
  * Analis dapat membekukan akun user yang terkompromi (misalnya user `sarah_security` pada insiden Impossible Travel).
  * Seluruh aktivitas login lanjutan dari akun tersebut ditolak otomatis di Gatekeeper (**HTTP 403 USER_SUSPENDED**).
* **Pemulihan Akses (`POST /api/soar/release` & `POST /api/soar/unsuspend-user`):**
  * Analis dapat melepas status isolasi host atau mengaktifkan kembali akun user setelah ancaman dinetralisir.
* **Audit Trail Feed (`GET /api/soar/audit`):**
  * Menyajikan riwayat jejak audit eksekusi playbook SOAR untuk akuntabilitas operasional SOC.

### Fitur E: Dashboard Real-Time & Tuning
* **Live SOC Monitor:** Antarmuka web mengambil data dari `GET /api/alerts` setiap 2 detik.
* **Visualisasi Insiden:** Alarm kritis berkedip merah dengan penanda waktu ISO; alert yang telah diisolasi ditandai dengan badge `[CONTAINED]` berlatar tenang.
* **Panel SOAR Terintegrasi:** Menampilkan daftar host yang sedang dikarantina beserta audit trail tindakan analis.
* **Careless Whitelisting:** Menyediakan kontrol (`POST /api/whitelist`) untuk mengecualikan IP secara manual, memvisualisasikan terciptanya celah *Blind Spot*.
* **Replay Launcher:** Panel peluncur skenario 1 s/d 9 langsung dari antarmuka web yang terhubung ke physical log replay.

---

## 4. Daftar Skenario Demonstrasi

1. **Skenario 1 (Trafik Normal):** Replay dari `web_access_normal.log` membuktikan aktivitas sah karyawan tidak memicu alarm (*False Positive zero*).
2. **Skenario 2 (DDoS Attack):** Replay dari `nginx_ddos_flood.log` memicu Rule 1 (DDoS / Botnet).
3. **Skenario 3 (Impossible Travel):** Replay dari `vpn_and_gate_access.csv` memicu Rule 2 (Impossible Travel Jakarta vs Frankfurt).
4. **Skenario 4 (Distributed Brute Force):** Replay dari `auth_sshd_bruteforce.log` memicu Rule 3 (Multi-IP SSH Brute Force).
5. **Skenario 5 (Data Exfiltration):** Replay dari `postgres_audit_exfiltration.jsonl` memicu Rule 5 (Massive database download insider threat).
6. **Skenario 6 (Careless Whitelisting):** Replay dari `careless_whitelist_attack.log` membuktikan IP yang di-whitelist membutakan SIEM (*Blind Spot fatal*).
7. **Skenario 7 (Data Cacat & Time Drift):** Replay dari `legacy_corrupted_device.log` membuktikan Gatekeeper menolak log rusak tanpa membuat server crash (HTTP 422).
8. **Skenario 8 (Low & Slow APT):** Replay dari `apt_recon_and_exploit.log` mendemonstrasikan mitigasi kebutaan korelasi akibat rotasi Hot ke Cold Storage menggunakan persistent watchlist.
9. **Skenario 9 (OT Hardware Sabotage - AC Central Shutdown via MQTT):** Replay dari `mqtt_datacenter_hvac.jsonl` mendemonstrasikan pembacaan status sensor hardware AC Central disusul deteksi perintah ilegal mematikan AC Central di datacenter via protokol MQTT (Rule Kritis OT Sabotage).
10. **Demo SOAR Active Defense:** Menjalankan `python simulator.py --soar` untuk memperagakan isolasi IP `45.33.32.156`, pemutusan traffic penyerang secara instan di Gatekeeper (HTTP 403), dan pemulihan karantina.

---

## 5. Tumpukan Teknologi (Tech Stack)

* **Backend:** Python 3.11 + FastAPI (Asynchronous, High-Performance, ASGI).
* **Validasi Skema:** Pydantic V2 + RFC 5424/OCSF normalization logic.
* **Adapter & Ingestion:** Universal Log Adapter (`app/log_adapter.py`) dengan regex parser multi-format.
* **Penyimpanan Telemetri:** *In-memory stateful store* (Event cache, Active Alerts, Whitelist, Suspicious Greylist, Isolated Hosts, SOAR Audit Trail).
* **Frontend:** HTML5 + CSS3 Grid/Flexbox + Vanilla JavaScript (Cyberpunk SOC Dark Theme, SOAR Active Panel, tanpa dependencies eksternal).
* **Simulator & Testing:** Python Requests, Pytest test suite (29 automated test cases).

---

## 6. Tata Kelola & Arsitektur Pengaman (AI & Human-in-the-Loop)

### 6.1 Tiga Risiko Kritis "Self-Adapting SIEM" Tanpa Supervisi
Jika SIEM diizinkan memodifikasi atau membuat aturan deteksi secara otonom tanpa validasi analis, timbul 3 risiko fatal:
1. **Risiko Keamanan (*Concept Drift / Data Poisoning*):** Penyerang APT menyuntikkan anomali berfrekuensi rendah secara bertahap (10 file $\rightarrow$ 500 file/minggu). Model AI menganggap kenaikan volume ini sebagai tren operasional sah, sehingga serangan skala penuh diklasifikasikan sebagai normal.
2. **Risiko Operasional (*Self-Inflicted DoS*):** Aturan adaptif salah mengklasifikasikan lonjakan transaksi kampanye promosi diskon (*flash sale*) sebagai serangan DDoS, memicu mitigasi otomatis yang memblokir transaksi pelanggan sah.
3. **Kepatuhan Audit & Regulasi (*Black-Box Decision*):** Standar tata kelola seperti **ISO/IEC 27001** dan **PCI-DSS** mewajibkan setiap perubahan aturan firewall memiliki riwayat deterministik dan tiket persetujuan formal (*change management*).

### 6.2 Blueprint Siklus Aman: "Human-Supervised Adaptation"
Model pengawasan terarah menghubungkan AI generator aturan dengan otoritas analis:
```
[1. Gatekeeper Ingest] -> Drop HTTP 422 jika format cacat
         ↓
[2. Dead-Letter Queue (DLQ)] -> Payload anomali baru diisolasi ke antrean karantina
         ↓
[3. AI Suggestion Engine] -> Sintesis pola anomali & rumuskan Candidate Rule
         ↓
[4. Canary Replay Test] -> Uji aturan pada data historis 30 hari (Rollback otomatis jika FP > 2%)
         ↓
[5. HITL Approval (Lead Analis)] -> Analis menyetujui di konsol SOC sebelum promosi ke produksi
```
* **Shadow Rule Mode:** Aturan baru berjalan dalam mode bayangan (*shadow mode*) untuk mencatat evaluasi tanpa memblokir trafik produksi sampai disetujui.

---

## 7. Prasyarat Integrasi Infrastruktur (Universal Ingestion Syllabus)

Untuk mengintegrasikan beragam sumber log dunia nyata (kamera, turnstile RFID, sensor IoT/OT, database, firewall) ke dalam SIEM, organisasi wajib memenuhi 4 pilar silabus:

### 7.1 Fondasi Bahan Baku Log (Log Foundation)
* **Anatomi Log:** Membedakan antara *Event* (kejadian tercatat), *Payload* (isi data utama), dan *Metadata* (atribut keterangan tambahan).
* **Siklus Hidup Log (*Log Lifecycle*):** Titik lahir log $\rightarrow$ Mekanisme forwarding $\rightarrow$ Buffering/Queueing $\rightarrow$ Hot Storage $\rightarrow$ Cold Archive.
* **Kalkulasi EPS (*Events Per Second*):** Menghitung kapasitas volume masuk untuk mencegah crash pada mesin korelasi akibat lonjakan trafik di atas estimasi.

### 7.2 Standarisasi & Bahasa Internasional
* **Standar Protokol (RFC 5424):** Menerapkan format pembungkus pesan Syslog standar: Timestamp, Hostname, Severity Level, dan Message Payload.
* **Pedoman Kepatuhan (NIST SP 800-92 & ISO 27002):** Menetapkan peristiwa wajib catat: kegagalan login, eskalasi hak akses (*privilege escalation*), dan error sistem.
* **Skema Data Universal (OCSF / CIM):** Menyeragamkan penamaan atribut multi-vendor (misal: menyatukan field `SrcIP` dan `Client_Address` menjadi `src_endpoint.ip`).

### 7.3 Prasyarat Infrastruktur Jaringan
* **Sinkronisasi Waktu Sentral (NTP - Network Time Protocol):** Syarat mutlak utama. Seluruh router, firewall, dan server wajib merujuk ke sumber waktu atomik UTC yang sama. Deviasi waktu 1 detik dapat merusak korelasi urutan kejadian (*time drift error*).
* **Arsitektur Agregator (Log Forwarder):** Menggunakan stasiun pengumpul log terdistribusi (Logstash/Fluentd) di tiap cabang jaringan guna menghindari bottleneck koneksi langsung ke server SIEM sentral.
* **Penyaringan Kebisingan (*Noise Filtering*):** Memfilter log repetitif non-kritis (seperti ping rutin jaringan internal) pada level forwarder sebelum membebani storage SIEM.

### 7.4 Prasyarat Bisnis & Konteks Operasional
* **Inventarisasi Aset (*Asset Management*):** Memetakan klasifikasi aset (membedakan IP server pembayaran inti dari WiFi publik tamu) agar tingkat keparahan alarm (*Severity*) ditentukan secara proporsional.
* **Definisi Use Case:** Menetapkan skenario deteksi spesifik sebelum operasional (misal: memicu alert kritis jika terdeteksi 5 kali gagal login VPN luar negeri di luar jam kerja).
* **SOP & Eskalasi Bertingkat:** Menetapkan alur eskalasi penanggung jawab saat alarm berstatus kritis terpicu (Tim Jaringan, Tim Aplikasi, atau Lead Analis SOC).

---

## 8. Arsitektur Storage Bertingkat: Hot Storage vs. Cold Storage

### 8.1 Limitasi Skalabilitas Linier (*The Brute-Force Fallacy*)
Asumsi umum mengusulkan: *"Jika peretas menyerang di Hari ke-20, perbesar masa retensi Hot Storage menjadi 30 atau 90 hari."* Pendekatan ini memicu kegagalan:
1. **Biaya Eksponensial:** Menyimpan petabyte log mentah di media RAM/NVMe SSD instan menaikkan biaya infrastruktur secara tidak proporsional.
2. **Degradasi Latensi Kueri:** Indeks pencarian yang membengkak menurunkan performa evaluasi aturan korelasi secara drastis (dari < 10ms menjadi hitungan detik).
3. **Noise-to-Signal Tinggi:** Sebagian besar volume data adalah telemetri rutin; mengalokasikan tier premium untuk data non-kritis memboroskan anggaran.

### 8.2 Dua Solusi Arsitektural Mini-SIEM
1. **Stateful Entity Tracking (Lightweight Long-Term Memory):**
   * Alih-alih menahan puluhan gigabyte data mentah, SIEM menyimpan satu baris JSON status di tabel persisten:
     `{"ip": "198.51.100.77", "risk": "HIGH", "score": 85, "reason": "recon_day_1"}`.
   * Jejak memori minimal ini dipertahankan lintas siklus retensi untuk dicocokkan saat entitas bersangkutan aktif kembali pada Hari ke-20.
2. **Cold Log Rehydration (On-Demand Forensic):**
   * Saat eksploitasi terverifikasi di Hari ke-20, sistem secara terarah mengekstraksi log terkait dari arsip dingin:
     `cold_s3://logs/{yyyy}/{mm}/{dd}/{ip_hash}/`.
   * Log ditarik kembali ke memori aktif analis untuk rekonstruksi linimasa serangan (*Kill Chain Reconstruction*) tanpa perlu melakukan full-table scan pada seluruh arsip.

---

## 9. Roadmap Produk & Matriks Dependensi Ekosistem SIEM (13 Fitur)

Pengembangan ekosistem SIEM dirancang dalam 3 fase berbasis dependensi teknis dan justifikasi manajemen produk (PM):

| Fase | No | Nama Fitur | Deskripsi Teknis | Dependensi | Prioritas | Justifikasi PM & Dampak |
| :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| **MVP v1 (Foundation)** | 1 | **Log Ingestion Engine** | Syslog, REST API, & Webhook listeners untuk menerima raw payload. | *None (Pondasi)* | **Critical** | Sumber data primer. Seluruh engine pemrosesan membutuhkan aliran log masuk. |
| | 2 | **Data Parsing & Normalization** | Standardisasi log heterogen ke dalam skema terpadu JSON Data Contract. | Log Ingestion | **Critical** | Format terstandarisasi memastikan integritas kueri dan evaluasi rule deteksi. |
| | 3 | **Hot Storage & Indexing** | Penyimpanan cepat berbasis indeks terbalik untuk jendela retensi aktif 14-30 hari. | Normalization | **Critical** | Memungkinkan evaluasi kueri analitik dan korelasi berlatensi rendah (< 10ms). |
| | 4 | **Search & Query Interface** | Antarmuka pengguna/API untuk kueri filter telemetri dan investigasi manual. | Hot Storage | **High** | Menyediakan visibilitas investigasi bagi analis keamanan saat menangani anomali. |
| | 5 | **Rule-Based Alerting** | Mekanisme notifikasi berbasis aturan ambang batas statis (misal: 5 login gagal/menit). | Search Interface | **High** | Otomasi peringatan dini untuk pola ancaman deterministik berfrekuensi tinggi. |
| | 6 | **Basic Dashboard & Reporting** | Visualisasi matriks EPS, distribusi sumber log, dan ringkasan status alert. | Search Interface | **Medium** | Memberikan visibilitas operasional bagi SOC Manager dan pemangku kepentingan. |
| **Phase 2 (Intelligence)** | 7 | **Correlation Engine** | Deteksi pola serangan kompleks lintas sumber dan rentang waktu (Stateful tracking). | Rule Alerting | **High** | Komponen inti deteksi ancaman berantai (recon ke eksploitasi) lintas retensi. |
| | 8 | **Threat Intel (TI) Integration** | Pencocokan feed reputasi IoC (IP buruk, domain C2, hash malware) pada streaming log. | Correlation Engine | **High** | Memperkaya telemetri internal dengan basis data intelijen ancaman global. |
| | 9 | **Incident & Case Management** | Sistem pencatatan tiket terpadu untuk alokasi, pelacakan, dan audit investigasi insiden. | Alerting | **Medium** | Standardisasi tata kelola eskalasi dan dokumentasi audit kepatuhan. |
| | 10 | **Cold Storage / Archiving** | Arsip terkompresi berbiaya rendah untuk retensi kepatuhan regulasi jangka panjang. | Hot Storage | **Medium** | Efisiensi anggaran penyimpanan jangka panjang (1 sampai 7 tahun). |
| **Phase 3 (Advanced)** | 11 | **UEBA (User & Entity Behavior)** | Model pembelajaran mesin untuk mendeteksi anomali perilaku kredensial sah. | Correlation & History | **High** | Identifikasi ancaman internal (*insider threat*) berbasis baseline data historis. |
| | 12 | **SOAR (Automated Response)** | Eksekusi playbook respon terprogram (seperti isolasi IP dan suspensi user di Gatekeeper). | Case Management & TI | **High** | Memangkas *Mean Time to Remediate* (MTTR) melalui mitigasi otomatis terverifikasi. |
| | 13 | **AI Adaptive Rule Generator** | Isolasi anomali ke DLQ, sintesis Shadow Rule via AI, validasi Canary Replay pada data 30 hari, & otorisasi HITL. | Correlation, Hot Storage 30 Hari, & TI | **High** | Pencegahan false positive massal melalui validasi historis dan otorisasi lead analis. |

### 9.1 Tiga Prinsip Rantai Dependensi Produk
1. **Fondasi Data Sebelum Analitik Lanjut:** Fase Ingestion, Normalisasi, dan Penyimpanan 30 hari harus stabil sebelum mengaktifkan UEBA. Tanpa data historis terstandarisasi, model perilaku tidak memiliki baseline yang andal.
2. **Pengendalian Risiko Sebelum Otomasi Penuh:** SOAR diimplementasikan pada Phase 3 setelah Case Management dan Threat Intel terverifikasi. Mitigasi otomatis tanpa akurasi tinggi berisiko memblokir trafik operasional yang sah.
3. **Keseimbangan Performa & Efisiensi Biaya:** Pemisahan Hot Storage (Phase 1) dan Cold Archive (Phase 2) menjaga performa korelasi real-time tetap optimal sekaligus mengendalikan biaya penyimpanan jangka panjang.
