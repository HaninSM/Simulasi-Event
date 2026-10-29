# 🛡️ Mini-SIEM Simulator (V2.1 - Real Log Replay & SOAR Active Defense Edition)

Aplikasi simulasi **Security Information and Event Management (SIEM)** berskala kecil berbasis API yang dibangun menggunakan **FastAPI**, **Pydantic**, dan **HTML5/CSS3/Vanilla JS (SOC Dark Command Center)**.

Sistem ini mendemonstrasikan secara *real-time* bagaimana pusat komando operasi keamanan (SOC):
1. Menerima, memvalidasi, dan menormalisasi log telemetri (*Gatekeeper Ingestion*).
2. Membaca format berkas log fisik autentik dunia nyata (Nginx Combined, Linux Syslog, CSV, PGAudit JSONL) via Universal Log Adapter.
3. Mendeteksi anomali dan serangan siber melalui mesin korelasi berbasis aturan (*Rule-based Correlation Engine*).
4. Mengurangi *Alert Fatigue* dengan debouncing cerdas.
5. Memitigasi data kotor dan *Time Drift Error* (HTTP 422).
6. Memvisualisasikan bahaya fatal dari **Careless Whitelisting** (celah *Blind Spot* buatan).
7. Menjawab tantangan *Hot vs Cold Storage* dan mendeteksi serangan **Low & Slow APT** melintasi rentang waktu 20 hari.
8. **SOAR Active Defense & Containment Playbook**: Memungkinkan analis mengisolasi host yang disusupi (*Network Quarantine*) dengan satu klik, memutus total traffic lanjutan di pintu Gatekeeper (**HTTP 403 Forbidden**).

---

## 📋 Daftar Isi
1. [Spesifikasi Kontrak Data](#-spesifikasi-kontrak-data)
2. [5 Aturan Mesin Korelasi & Logika APT](#-5-aturan-mesin-korelasi--logika-apt)
3. [SOAR Active Defense & Host Containment](#-soar-active-defense--host-containment)
4. [Arsitektur Log Adapter & Berkas Sample Logs](#-arsitektur-log-adapter--berkas-sample-logs)
5. [Instalasi & Persiapan Lingkungan](#-instalasi--persiapan-lingkungan)
6. [Menjalankan Server & Dashboard](#-menjalankan-server--dashboard)
7. [Panduan Step-by-Step Menjalankan PoC Skenario 1 s/d 8](#-panduan-step-by-step-menjalankan-poc-skenario-1-sd-8)
   - [Skenario 1: Trafik Normal (Baseline)](#skenario-1-trafik-normal-baseline)
   - [Skenario 2: DDoS / Botnet Attack (Rule 1 - TINGGI)](#skenario-2-ddos--botnet-attack-rule-1---tinggi)
   - [Skenario 3: Impossible Travel (Rule 2 - KRITIS)](#skenario-3-impossible-travel-rule-2---kritis)
   - [Skenario 4: Distributed Brute Force (Rule 3 - TINGGI)](#skenario-4-distributed-brute-force-rule-3---tinggi)
   - [Skenario 5: Data Exfiltration / Insider Threat (Rule 5 - KRITIS)](#skenario-5-data-exfiltration--insider-threat-rule-5---kritis)
   - [Skenario 6: Careless Whitelisting (Fatal Error / Blind Spot Demo)](#skenario-6-careless-whitelisting-fatal-error--blind-spot-demo)
   - [Skenario 7: Data Cacat & Time Drift (Gatekeeper Negative Testing)](#skenario-7-data-cacat--time-drift-gatekeeper-negative-testing)
   - [Skenario 8: The Low & Slow APT (Hot vs Cold Storage & Greylist Demo)](#skenario-8-the-low--slow-apt-hot-vs-cold-storage--greylist-demo)
   - [Demo SOAR: Host Isolation & Active Traffic Dropping](#demo-soar-host-isolation--active-traffic-dropping)
8. [Otomasi Pengujian (Automated Unit & Integration Tests - 24 Passed)](#-otomasi-pengujian-automated-unit--integration-tests---24-passed)
9. [Daftar Endpoint API SIEM & SOAR](#-daftar-endpoint-api-siem--soar)
10. [Struktur Direktori Proyek](#-struktur-direktori-proyek)

---

## 📑 Spesifikasi Kontrak Data
Setiap log yang dikirim ke `POST /api/ingest` wajib memenuhi format JSON kanonikal berikut:

```json
{
  "timestamp": "2026-10-19T16:22:43Z",
  "event_type": "login_attempt | web_request | database_download",
  "user_id": "string (non-empty)",
  "ip_address": "string (IPv4 format)",
  "location": "string (non-empty)",
  "status": "success | failed"
}
```

*Jika data tidak mematuhi kontrak atau mengalami selisih waktu > 24 jam / masa depan, sistem merespons dengan **HTTP 422 (Unprocessable Entity)**. Jika IP pengirim sedang berada dalam status **Network Quarantine (SOAR)**, Gatekeeper langsung menolak dengan **HTTP 403 (Forbidden)**.*

---

## 🧠 5 Aturan Mesin Korelasi & Logika APT
| ID Aturan | Nama Aturan | Tingkat Keparahan | Logika / Kondisi Pemicu |
| :--- | :--- | :--- | :--- |
| **Rule 1** | **DDoS / Botnet** | **TINGGI** | > 10 `web_request` dari 1 `ip_address` yang sama dalam rentang 10 detik. |
| **Rule 2** | **Impossible Travel** | **KRITIS** | 2 `login_attempt` sukses dari 1 `user_id` yang sama, namun di `location` berbeda dalam waktu < 1 jam. |
| **Rule 3** | **Distributed Brute Force** | **TINGGI** | > 5 `login_attempt` gagal untuk 1 `user_id` yang sama, berasal dari > 3 `ip_address` berbeda dalam 1 menit. |
| **Rule 4** | **Off-Hours Anomaly** | **MENENGAH** | Aktivitas `status: success` oleh user manusia yang terjadi di luar jam kerja (00:00 - 05:00 waktu lokal). |
| **Rule 5** | **Data Exfiltration** | **KRITIS** | 1 `user_id` melakukan `database_download` > 50 kali dalam rentang 1 menit. |
| **APT Watchlist** | **Low & Slow APT Correlation**| **KRITIS** | IP yang sebelumnya melakukan *reconnaissance* terdaftar dalam *stateful greylist*. Saat IP tersebut mengirim *exploit request* di masa depan, SIEM merehidrasi riwayat dari *Cold Storage* dan membunyikan alarm APT. |

---

## 🔒 SOAR Active Defense & Host Containment
Mini-SIEM mengintegrasikan kapabilitas **SOAR (Security Orchestration, Automation, and Response)** untuk respons aktif:
1. **Network Quarantine (Isolate Host):**
   * Analis dapat mengeklik tombol **"🔒 Isolate Host"** langsung pada kartu alert di dashboard, atau mengirim permintaan `POST /api/soar/isolate`.
   * Status alert otomatis bertransisi menjadi **`[CONTAINED]`** dan animasi berkedip darurat dinonaktifkan.
2. **Gatekeeper Enforcement (Active Traffic Drop):**
   * Semua paket atau log lanjutan dari host yang telah diisolasi langsung ditolak di pintu masuk Gatekeeper dengan status kode **`HTTP 403 Forbidden`**.
   * Counter *Blocked Traffic (SOAR)* bertambah secara *real-time*.
3. **Audit Trail & Recovery:**
   * Setiap penindakan dicatat dalam riwayat audit SOAR (`GET /api/soar/audit`).
   * Host dapat dilepaskan dari karantina melalui tombol **"🔓 Release Host"** (`POST /api/soar/release`) setelah proses remediasi selesai.

---

## 🔄 Arsitektur Log Adapter & Berkas Sample Logs
Mini-SIEM mengintegrasikan modul **Universal Log Adapter** (`app/log_adapter.py`) yang membaca berkas telemetri autentik dari folder `sample_logs/` dan mengubahnya menjadi format kontrak SIEM:

```
[Raw Log Sources]                 [Universal Log Adapter]               [Gatekeeper & Correlation Engine]
sample_logs/                      app/log_adapter.py                     app/engine.py
├── web_access_normal.log  -----> Nginx Combined Regex Parser --------> POST /api/ingest (Canonical JSON)
├── nginx_ddos_flood.log   -----> HTTP Flood Regex Parser -------------> POST /api/ingest
├── vpn_and_gate_access.csv ----> RFID CSV & Geo Parser ---------------> POST /api/ingest
├── auth_sshd_bruteforce.log ---> Syslog RFC 3164 Regex Parser --------> POST /api/ingest
├── postgres_audit_exfil.jsonl -> PGAudit JSON Lines Parser -----------> POST /api/ingest
├── careless_whitelist.log -----> Whitelist Target Regex --------------> POST /api/ingest
├── legacy_corrupted.log -------> Raw Corrupted Injector --------------> POST /api/ingest (Negative Test)
└── apt_recon_exploit.log ------> Multi-phase APT Parser --------------> POST /api/ingest (Temporal Demo)
```

### Mekanisme Dynamic Timestamp Shifting
`LogAdapter.shift_timestamps_to_now()` menghitung selisih waktu antara entri pertama dalam berkas log dengan waktu saat ini (`NOW()`), lalu memproyeksikan seluruh baris log secara proporsional ke detik berjalan. Hal ini memastikan data mentah asli tetap 100% autentik sekaligus memicu sliding correlation windows tanpa melanggar Gatekeeper Time Drift Check.

---

## 💻 Instalasi & Persiapan Lingkungan

### 1. Prasyarat
* Python 3.10 atau lebih baru.
* Peramban web modern (Google Chrome, Edge, Firefox).

### 2. Instalasi Dependensi
Jalankan perintah berikut di PowerShell atau Command Prompt pada direktori `CommandCenter`:
```powershell
pip install -r requirements.txt
```

Paket yang terpasang meliputi:
* `fastapi`: Framework API asinkron berperforma tinggi.
* `uvicorn[standard]`: ASGI web server.
* `pydantic`: Validasi kontrak data dan sanitasi input.
* `requests` & `httpx`: Klien HTTP untuk simulator dan test suite.
* `pytest`: Framework pengujian unit & integrasi otomatis.

---

## 🚀 Menjalankan Server & Dashboard

### Cara Cepat (One-Click)
Cukup klik ganda file berikut di File Explorer:
* [`run_server.bat`](file:///c:/Users/ZYREX/Documents/CommandCenter/run_server.bat)

### Cara Manual via Terminal
Buka PowerShell di folder proyek dan jalankan:
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Setelah server aktif, buka peramban Anda ke tautan berikut:
* 🖥️ **Live SOC Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* 📖 **Dokumentasi Interaktif OpenAPI (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Dashboard melakukan sinkronisasi data (*polling*) setiap **2 detik** ke API SIEM.

---

## 🎯 Panduan Step-by-Step Menjalankan PoC Skenario 1 s/d 8

Buka jendela terminal kedua dengan server tetap menyala di jendela pertama. 

Anda dapat menjalankan skenario melalui:
1. **Script CLI Simulator**: `python simulator.py --scenario <1-8>`
2. **Demo SOAR Active Defense**: `python simulator.py --soar`
3. **One-Click Batch**: `run_simulator.bat`
4. **Web UI Dashboard**: Mengklik langsung tombol pada panel *"Quick Scenario Launcher"* di sisi kanan halaman web.

---

### Skenario 1: Trafik Normal (Baseline)
* **Sumber Data**: `sample_logs/web_access_normal.log` (Format Nginx/Apache Combined Log)
* **Tujuan**: Membuktikan bahwa aktivitas normal karyawan tidak memicu alarm palsu (*False Positive*).
* **Perintah**: `python simulator.py --scenario 1`

---

### Skenario 2: DDoS / Botnet Attack (Rule 1 - TINGGI)
* **Sumber Data**: `sample_logs/nginx_ddos_flood.log` (Format Nginx HTTP Flood)
* **Tujuan**: Membuktikan deteksi otomatis serangan flooding HTTP dari satu IP (`45.33.32.156`) dalam rentang 10 detik.
* **Perintah**: `python simulator.py --scenario 2`

---

### Skenario 3: Impossible Travel (Rule 2 - KRITIS)
* **Sumber Data**: `sample_logs/vpn_and_gate_access.csv` (Format Telemetri Akses Fisik RFID & VPN Gateway)
* **Tujuan**: Membuktikan korelasi identitas ganda yang mustahil secara fisik (User `budi_finance` tap pintu kantor Jakarta, lalu 2 menit kemudian login VPN dari Frankfurt, Jerman).
* **Perintah**: `python simulator.py --scenario 3`

---

### Skenario 4: Distributed Brute Force (Rule 3 - TINGGI)
* **Sumber Data**: `sample_logs/auth_sshd_bruteforce.log` (Format Linux `/var/log/auth.log` Syslog RFC 3164)
* **Tujuan**: Membuktikan deteksi serangan tebak kata sandi terdistribusi yang menyasar 1 akun target (`admin_corp`) melalui beberapa IP exit node Tor berbeda dalam 1 menit.
* **Perintah**: `python simulator.py --scenario 4`

---

### Skenario 5: Data Exfiltration / Insider Threat (Rule 5 - KRITIS)
* **Sumber Data**: `sample_logs/postgres_audit_exfiltration.jsonl` (Format Audit Query Database PGAudit JSONL)
* **Tujuan**: Membuktikan deteksi orang dalam (*insider threat*) yang mengekstrak data nasabah secara masif (> 50 download query dalam 1 menit).
* **Perintah**: `python simulator.py --scenario 5`

---

### Skenario 6: Careless Whitelisting (Fatal Error / Blind Spot Demo)
* **Sumber Data**: `sample_logs/careless_whitelist_attack.log` (Format Nginx Web Access)
* **Tujuan**: Memperlihatkan bahaya fatal memasukkan IP sembarangan ke dalam whitelist.
* **Perintah**: `python simulator.py --scenario 6`

---

### Skenario 7: Data Cacat & Time Drift (Gatekeeper Negative Testing)
* **Sumber Data**: `sample_logs/legacy_corrupted_device.log` (Telemetri Perangkat Lawas Rusak)
* **Tujuan**: Membuktikan ketangguhan Gatekeeper dalam menolak log format rusak, atribut kosong, dan *Time Drift Error* (baterai CMOS reset ke tahun 1970 atau drift masa depan) dengan respons **HTTP 422** tanpa membuat sistem *crash*.
* **Perintah**: `python simulator.py --scenario 7`

---

### Skenario 8: The Low & Slow APT (Hot vs Cold Storage & Greylist Demo)
* **Sumber Data**: `sample_logs/apt_recon_and_exploit.log` (Telemetri Serangan Bertahap Berjarak 20 Hari)
* **Tujuan**: Mengedukasi tantangan arsitektur *Hot Storage vs Cold Storage* dan mendemonstrasikan mitigasi kebutaan korelasi (*temporal blind spot*).
* **Perintah**: `python simulator.py --scenario 8`

---

### Demo SOAR: Host Isolation & Active Traffic Dropping
* **Tujuan**: Memperagakan penanganan insiden aktif saat analis mengisolasi host yang terinfeksi dan memutus serangannya secara instan.
* **Perintah**:
  ```powershell
  python simulator.py --soar
  ```
* **Alur Eksekusi**:
  1. Simulator menjalankan serangan L7 DDoS dari IP `45.33.32.156`.
  2. SOAR mengeksekusi perintah isolasi jaringan (`POST /api/soar/isolate`).
  3. Simulator mencoba mengirim paket serangan lanjutan dari host tersebut: Gatekeeper langsung menolak dengan status **HTTP 403 Forbidden (HOST ISOLATED)**.
  4. Analis melepas karantina (`POST /api/soar/release`) dan membuktikan aliran trafik kembali normal.

---

### 🌟 Menjalankan Tur Lengkap (Semua 8 Skenario Sekaligus)
Untuk mendemonstrasikan seluruh skenario secara sekuensial dalam satu perintah:
```powershell
python simulator.py --all
```

---

## 🧪 Otomasi Pengujian (Automated Unit & Integration Tests - 24 Passed)

Untuk memvalidasi integritas seluruh fungsionalitas sistem secara otomatis, jalankan rangkaian uji menggunakan `pytest`:

```powershell
pytest test_siem.py -v
```

### Hasil Eksekusi Uji Otomatis:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1
collected 24 items

test_siem.py::test_missing_ip_address_rejected PASSED                    [  4%]
test_siem.py::test_null_ip_address_rejected PASSED                       [  8%]
test_siem.py::test_missing_ip_key_completely_rejected PASSED             [ 12%]
test_siem.py::test_truncated_malformed_json_rejected PASSED              [ 16%]
test_siem.py::test_invalid_ipv4_rejected PASSED                          [ 20%]
test_siem.py::test_time_drift_cmos_battery_reset_1970_rejected PASSED    [ 25%]
test_siem.py::test_time_drift_future_rejected PASSED                     [ 29%]
test_siem.py::test_invalid_event_type_rejected PASSED                    [ 33%]
test_siem.py::test_rule_1_ddos_detection PASSED                          [ 37%]
test_siem.py::test_rule_2_impossible_travel PASSED                       [ 41%]
test_siem.py::test_rule_3_distributed_brute_force PASSED                 [ 45%]
test_siem.py::test_rule_4_off_hours_anomaly PASSED                       [ 50%]
test_siem.py::test_rule_5_data_exfiltration PASSED                       [ 54%]
test_siem.py::test_careless_whitelisting_blinds_correlation_engine PASSED [ 58%]
test_siem.py::test_scenario_8_recon_probe_and_cold_storage_aging PASSED  [ 62%]
test_siem.py::test_scenario_8_apt_correlation_blind_spot_without_watchlist PASSED [ 66%]
test_siem.py::test_scenario_8_apt_correlation_success_with_persistent_watchlist PASSED [ 70%]
test_siem.py::test_stats_and_reset_endpoints PASSED                      [ 75%]
test_siem.py::test_log_adapter_parses_real_sample_files PASSED           [ 79%]
test_siem.py::test_api_simulator_replay_scenarios PASSED                 [ 83%]
test_siem.py::test_soar_isolate_host_blocks_subsequent_ingestion_http_403 PASSED [ 87%]
test_siem.py::test_soar_release_host_restores_ingestion PASSED           [ 91%]
test_siem.py::test_soar_alert_status_transitions_to_contained PASSED     [ 95%]
test_siem.py::test_soar_stats_and_audit_trail PASSED                     [ 92%]
test_siem.py::test_scenario_3_impossible_travel_isolation_blocks_subsequent_replay PASSED [ 96%]
test_siem.py::test_soar_user_suspension_blocks_logins_and_replays PASSED [100%]

======================== 26 passed, 1 warning in 1.10s ========================
```

---

## 📡 Daftar Endpoint API SIEM & SOAR

| Method | Endpoint | Deskripsi | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Melayani web dashboard SOC (HTML/JS/CSS) | `200 OK` |
| `POST` | `/api/ingest` | Menerima & memvalidasi log telemetri, mengevaluasi aturan korelasi, menegakkan karantina SOAR | `201 Created` / `403 Forbidden` / `422 Unprocessable` |
| `GET` | `/api/alerts` | Mengambil daftar alarm aktif (dapat difilter berdasarkan `severity`) | `200 OK` |
| `GET` | `/api/logs` | Mengambil 15 log telemetri terbaru yang berhasil di-ingest | `200 OK` |
| `GET` | `/api/stats` | Mengambil statistik agregasi metrik operasional SOC (termasuk count SOAR) | `200 OK` |
| `POST` | `/api/whitelist` | Menambahkan IP ke daftar pengecualian (*Blind Spot*) | `200 OK` |
| `GET` | `/api/whitelist` | Melihat daftar IP yang saat ini di-whitelist | `200 OK` |
| `DELETE` | `/api/whitelist/{ip}`| Menghapus IP dari daftar whitelist | `200 OK` / `404 Not Found` |
| `POST` | `/api/soar/isolate` | **SOAR Action:** Mengisolasi host mencurigakan dan memutus trafficnya | `200 OK` |
| `POST` | `/api/soar/release` | **SOAR Action:** Melepas status karantina host | `200 OK` / `404 Not Found` |
| `GET` | `/api/soar/isolated` | Mengambil daftar seluruh host yang sedang dikarantina | `200 OK` |
| `POST` | `/api/soar/suspend-user` | **SOAR Action:** Membekukan akun user yang terkompromi (Identity Defense) | `200 OK` |
| `POST` | `/api/soar/unsuspend-user` | **SOAR Action:** Mengaktifkan kembali akun user yang dibekukan | `200 OK` / `404 Not Found` |
| `GET` | `/api/soar/suspended-users` | Mengambil daftar akun user yang sedang dibekukan | `200 OK` |
| `GET` | `/api/soar/audit` | Mengambil riwayat audit log tindakan penanganan SOAR | `200 OK` |
| `POST` | `/api/simulator/replay` | Menjalankan replay otomatis berkas log fisik dari `sample_logs/` (parameter `scenario=1..8`) | `200 OK` / `400 Bad Request` |
| `POST` | `/api/reset` | Mereset seluruh log, alert, whitelist, dan karantina SOAR in-memory | `200 OK` |

---

## 📁 Struktur Direktori Proyek

```
CommandCenter/
├── app/
│   ├── __init__.py          # Modul Python app
│   ├── main.py              # Router FastAPI, endpoint ingestion, SOAR containment, & replay
│   ├── models.py            # Model data Pydantic, schema SOAR, IPv4 validator, & time drift rule
│   ├── engine.py            # Mesin korelasi, debouncing, SOAR state (quarantine & audit trail)
│   ├── log_adapter.py       # Universal Log Adapter: multi-format parser & dynamic timestamp shifter
│   └── static/
│       ├── index.html       # Antarmuka Command Center SOC Dark Theme (dengan SOAR Panel)
│       ├── style.css        # Tata letak grid/flexbox, efek visual alert KRITIS & status CONTAINED
│       └── app.js           # Polling real-time 2s & handler aksi interaktif Isolate/Release Host
├── sample_logs/             # Kumpulan berkas log fisik autentik dunia nyata
│   ├── web_access_normal.log         # Format Nginx/Apache Combined Log
│   ├── nginx_ddos_flood.log          # Format Nginx HTTP Flood
│   ├── vpn_and_gate_access.csv       # Format Akses Fisik RFID & VPN Gateway CSV
│   ├── auth_sshd_bruteforce.log      # Format Linux /var/log/auth.log Syslog RFC 3164
│   ├── postgres_audit_exfiltration.jsonl # Format Audit Query Database PostgreSQL JSONL
│   ├── careless_whitelist_attack.log # Format Nginx Web Access untuk Whitelist Demo
│   ├── legacy_corrupted_device.log   # Telemetri format rusak & Time Drift Error
│   └── apt_recon_and_exploit.log     # Format Jejak APT multi-fase (20 hari)
├── presentation.html        # Slide presentasi interaktif SOC Architecture & Implementation
├── simulator.py             # Script simulator interaktif 8 skenario & demo SOAR containment
├── test_siem.py             # Test suite 26 unit & integration test otomatis (100% passed)
├── requirements.txt         # Daftar dependensi Python
├── run_server.bat           # Launcher server satu-klik
├── run_simulator.bat        # Launcher simulator satu-klik
├── mini_siem_product_requirements_document.md # Dokumen PRD V2.1
└── README.md                # Panduan teknis lengkap & PoC skenario
```

---

## 🛡️ Catatan Tambahan untuk Demonstrasi
* **Tombol Reset**: Setiap kali Anda ingin memulai demonstrasi bersih dari awal, tekan tombol **🔄 Reset SIEM State** di bilah navigasi dashboard atau jalankan `python simulator.py --reset`.
* **Pengujian Fleksibel**: Demonstrasi dapat dijalankan baik melalui terminal (`simulator.py`) maupun melalui antarmuka web browser.
