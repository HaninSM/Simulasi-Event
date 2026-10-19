# 🛡️ Mini-SIEM Simulator (V1.0 - Full Scenario Edition)

Aplikasi simulasi **Security Information and Event Management (SIEM)** berskala kecil berbasis API yang dibangun menggunakan **FastAPI**, **Pydantic**, dan **HTML5/CSS3/Vanilla JS (SOC Dark Command Center)**.

Sistem ini mendemonstrasikan secara *real-time* bagaimana pusat komando operasi keamanan (SOC):
1. Menerima dan memvalidasi log telemetri (*Gatekeeper Ingestion*).
2. Mendeteksi anomali dan serangan siber melalui mesin korelasi berbasis aturan (*Rule-based Correlation Engine*).
3. Mengurangi *Alert Fatigue* dengan debouncing cerdas.
4. Memitigasi data kotor dan *Time Drift Error* (HTTP 422).
5. Memvisualisasikan bahaya fatal dari **Careless Whitelisting** (celah *Blind Spot* buatan).

---

## 📋 Daftar Isi
1. [Spesifikasi Kontrak Data](#-spesifikasi-kontrak-data)
2. [5 Aturan Mesin Korelasi](#-5-aturan-mesin-korelasi)
3. [Instalasi & Persiapan Lingkungan](#-instalasi--persiapan-lingkungan)
4. [Menjalankan Server & Dashboard](#-menjalankan-server--dashboard)
5. [Panduan Step-by-Step Menjalankan PoC Skenario 1 s/d 7](#-panduan-step-by-step-menjalankan-poc-skenario-1-sd-7)
   - [Skenario 1: Trafik Normal (Baseline)](#skenario-1-trafik-normal-baseline)
   - [Skenario 2: DDoS / Botnet Attack (Rule 1 - TINGGI)](#skenario-2-ddos--botnet-attack-rule-1---tinggi)
   - [Skenario 3: Impossible Travel (Rule 2 - KRITIS)](#skenario-3-impossible-travel-rule-2---kritis)
   - [Skenario 4: Distributed Brute Force (Rule 3 - TINGGI)](#skenario-4-distributed-brute-force-rule-3---tinggi)
   - [Skenario 5: Data Exfiltration / Insider Threat (Rule 5 - KRITIS)](#skenario-5-data-exfiltration--insider-threat-rule-5---kritis)
   - [Skenario 6: Careless Whitelisting (Fatal Error / Blind Spot Demo)](#skenario-6-careless-whitelisting-fatal-error--blind-spot-demo)
   - [Skenario 7: Data Cacat & Time Drift (Gatekeeper Negative Testing)](#skenario-7-data-cacat--time-drift-gatekeeper-negative-testing)
6. [Otomasi Pengujian (Automated Unit & Integration Tests)](#-otomasi-pengujian-automated-unit--integration-tests)
7. [Daftar Endpoint API SIEM](#-daftar-endpoint-api-siem)
8. [Struktur Direktori Proyek](#-struktur-direktori-proyek)

---

## 📑 Spesifikasi Kontrak Data
Setiap log yang dikirim ke `POST /api/ingest` wajib memenuhi format JSON berikut:

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

*Jika data tidak mematuhi kontrak atau mengalami selisih waktu > 24 jam / masa depan, sistem secara otomatis merespons dengan **HTTP 422 (Unprocessable Entity)**.*

---

## 🧠 5 Aturan Mesin Korelasi
| ID Aturan | Nama Aturan | Tingkat Keparahan | Logika / Kondisi Pemicu |
| :--- | :--- | :--- | :--- |
| **Rule 1** | **DDoS / Botnet** | **TINGGI** | > 10 `web_request` dari 1 `ip_address` yang sama dalam rentang 10 detik. |
| **Rule 2** | **Impossible Travel** | **KRITIS** | 2 `login_attempt` sukses dari 1 `user_id` yang sama, namun di `location` berbeda dalam waktu < 1 jam. |
| **Rule 3** | **Distributed Brute Force** | **TINGGI** | > 5 `login_attempt` gagal untuk 1 `user_id` yang sama, berasal dari > 3 `ip_address` berbeda dalam 1 menit. |
| **Rule 4** | **Off-Hours Anomaly** | **MENENGAH** | Aktivitas `status: success` oleh user manusia yang terjadi di luar jam kerja (00:00 - 05:00 waktu lokal). |
| **Rule 5** | **Data Exfiltration** | **KRITIS** | 1 `user_id` melakukan `database_download` > 50 kali dalam rentang 1 menit. |

---

## 💻 Instalasi & Persiapan Lingkungan

### 1. Prasyarat
*   Python 3.10 atau lebih baru.
*   Peramban web modern (Google Chrome, Edge, Firefox).

### 2. Instalasi Dependensi
Jalankan perintah berikut di PowerShell atau Command Prompt pada direktori `CommandCenter`:
```powershell
pip install -r requirements.txt
```

Paket yang terpasang meliputi:
*   `fastapi`: Framework API asinkron berperforma tinggi.
*   `uvicorn[standard]`: ASGI web server.
*   `pydantic`: Validasi kontrak data dan sanitasi input.
*   `requests` & `httpx`: Klien HTTP untuk simulator dan test suite.
*   `pytest`: Framework pengujian unit & integrasi otomatis.

---

## 🚀 Menjalankan Server & Dashboard

### Cara Cepat (One-Click)
Cukup klik ganda file berikut di File Explorer:
*   [`run_server.bat`](file:///c:/Users/ZYREX/Documents/CommandCenter/run_server.bat)

### Cara Manual via Terminal
Buka PowerShell di folder proyek dan jalankan:
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Setelah server aktif, buka peramban Anda ke tautan berikut:
*   🖥️ **Live SOC Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
*   📖 **Dokumentasi Interaktif OpenAPI (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Dashboard akan otomatis melakukan sinkronisasi data (*polling*) setiap **2 detik** ke API SIEM.

---

## 🎯 Panduan Step-by-Step Menjalankan PoC Skenario 1 s/d 7

Buka jendela terminal kedua (PowerShell atau Command Prompt) dengan server tetap menyala di jendela pertama. 

Anda dapat menjalankan skenario melalui:
1. **Script CLI Simulator**: `python simulator.py`
2. **One-Click Batch**: `run_simulator.bat`
3. **Web UI Dashboard**: Mengklik langsung tombol pada panel *"Quick Scenario Launcher"* di sisi kanan halaman web.

---

### Skenario 1: Trafik Normal (Baseline)

#### Tujuan
Membuktikan bahwa aktivitas normal sehari-hari karyawan tidak memicu alarm palsu (*False Positive*).

#### Cara Eksekusi
```powershell
python simulator.py --scenario 1
```

#### Apa yang Terjadi?
1. Simulator mengirimkan 4 event berturut-turut dari user karyawan yang berbeda:
   * `alice_hr`: `login_attempt` sukses dari `192.168.1.101`.
   * `bob_eng`: `web_request` sukses dari `192.168.1.102`.
   * `charlie_sales`: `web_request` sukses dari `192.168.1.103`.
   * `alice_hr`: `web_request` sukses dari `192.168.1.101`.
2. SIEM menerima setiap log dengan respons `HTTP 201 Created` (`"alerts_triggered": 0`).

#### Hasil di Dashboard Web
* Counter **Ingested Logs** bertambah menjadi `4`.
* Counter **Total Alerts** tetap `0`.
* Panel **Recent Ingestion Stream** menampilkan keempat event dengan badge hijau `SUCCESS`.

---

### Skenario 2: DDoS / Botnet Attack (Rule 1 - TINGGI)

#### Tujuan
Membuktikan deteksi otomatis serangan flooding HTTP dari satu IP dalam jendela waktu 10 detik.

#### Kriteria Pemicu
`> 10 web_request` dari 1 IP address dalam waktu $\le$ 10 detik.

#### Cara Eksekusi
```powershell
python simulator.py --scenario 2
```

#### Apa yang Terjadi?
1. Simulator menembakkan 15 event `web_request` cepat dari IP `45.33.32.156` (jeda waktu hanya 80 ms per request).
2. Request ke-1 s/d ke-10 diterima normal sebagai akumulasi volume trafik.
3. Pada **request ke-11**, ambang batas 10 request dalam 10 detik terlampaui!
4. Mesin Korelasi langsung membangkitkan alarm:
   * **Rule**: `DDoS / Botnet`
   * **Severity**: `TINGGI`
   * **Detail**: Tercatat 11 request dalam jendela 10 detik dari IP `45.33.32.156`.

#### Hasil di Dashboard Web
* Counter **High Alerts (TINGGI)** bertambah +1.
* Kartu alarm berwarna jingga (**TINGGI**) muncul di puncak *Live Feed*, mencantumkan stempel waktu dan ID insiden.

---

### Skenario 3: Impossible Travel (Rule 2 - KRITIS)

#### Tujuan
Mendeteksi anomali perpindahan lokasi fisik akun yang mustahil secara geografis dalam waktu singkat (indikasi peretasan kredensial / *session hijacking*).

#### Kriteria Pemicu
`2 login_attempt` dengan status `success` untuk user yang sama di lokasi berbeda dalam waktu < 1 jam.

#### Cara Eksekusi
```powershell
python simulator.py --scenario 3
```

#### Apa yang Terjadi?
1. Simulator mengirim event login sukses untuk user `sarah_security` dari lokasi **"Jakarta, ID"** (`IP: 103.24.56.12`).
2. Tepat 1 detik kemudian, simulator mengirim event login sukses kedua untuk user yang sama (`sarah_security`) dari lokasi **"Frankfurt, DE"** (`IP: 185.190.140.2`).
3. Mesin korelasi membandingkan stempel waktu dan lokasi dengan riwayat login sebelumnya. Selisih waktu tercatat hanya ~1 detik untuk jarak ribuan kilometer!
4. Alarm tingkat tertinggi langsung dipicu:
   * **Rule**: `Impossible Travel`
   * **Severity**: `KRITIS`

#### Hasil di Dashboard Web
* Counter **Critical Alerts (KRITIS)** bertambah +1.
* Kartu alarm muncul dengan **efek animasi berkedip merah terang (*pulsating critical alert*)**, memberikan peringatan visual instan bagi operator SOC.

---

### Skenario 4: Distributed Brute Force (Rule 3 - TINGGI)

#### Tujuan
Mendeteksi serangan penebakan kata sandi terdistribusi (*Distributed Password Spraying*) yang disebar melalui beberapa IP proxy/Tor untuk mengelabui deteksi single-IP.

#### Kriteria Pemicu
`> 5 login_attempt` berstatus `failed` untuk user yang sama dari `> 3 IP address` berbeda dalam 60 detik.

#### Cara Eksekusi
```powershell
python simulator.py --scenario 4
```

#### Apa yang Terjadi?
1. Simulator mengirim 8 percobaan login gagal untuk target user `admin_vault` dari 5 alamat IP berbeda (`198.51.100.11` s/d `198.51.100.15`).
2. Hingga percobaan ke-5, sistem masih mengumpulkan bukti telemetri.
3. Pada **percobaan ke-6**, dua kriteria terpenuhi:
   * Total kegagalan: 6 (melebihi batas > 5).
   * Jumlah IP unik: 5 (melebihi batas > 3).
4. Mesin korelasi memicu alarm:
   * **Rule**: `Distributed Brute Force`
   * **Severity**: `TINGGI`
   * **Detail**: Daftar seluruh IP sumber penyerang dicatat dalam metadata alert.

#### Hasil di Dashboard Web
* Counter **High Alerts (TINGGI)** bertambah +1.
* Panel alert menampilkan detail seluruh daftar IP yang terlibat dalam serangan distributed brute force tersebut.

---

### Skenario 5: Data Exfiltration / Insider Threat (Rule 5 - KRITIS)

#### Tujuan
Mendeteksi aksi pencurian atau pengunduhan basis data massal oleh orang dalam (*malicious insider*).

#### Kriteria Pemicu
`1 user_id` mengeksekusi `database_download` `> 50 kali` dalam jendela waktu 1 menit.

#### Cara Eksekusi
```powershell
python simulator.py --scenario 5
```

#### Apa yang Terjadi?
1. Simulator mengirim 55 event `database_download` berturut-turut untuk user internal `rogue_dev_alex` dari IP lokal `10.0.8.21`.
2. Pada **unduhan ke-51**, batas aman 50 unduhan per menit terlampaui.
3. Alarm darurat dibangkitkan:
   * **Rule**: `Data Exfiltration / Insider Threat`
   * **Severity**: `KRITIS`

#### Hasil di Dashboard Web
* Counter **Critical Alerts (KRITIS)** bertambah.
* Alarm merah berkedip muncul memperingatkan operator bahwa potensi kebocoran data massal sedang berlangsung.

---

### Skenario 6: Careless Whitelisting (Fatal Error / Blind Spot Demo)

#### Tujuan
Mendemonstrasikan risiko keamanan siber paling berbahaya: **kelalaian tim operasi saat memasukkan IP ke whitelist**, yang menyebabkan SIEM mengalami kebutaan total (*Fatal Blind Spot*).

#### Logika Eksperimen
1. Kapten SIEM memasukkan IP penyerang (`203.0.113.88`) ke dalam Whitelist (misalnya dengan dalih "IP vendor terpercaya / bypass testing").
2. Hacker kemudian melancarkan serangan DDoS masif (15 request bertubi-tubi) melalui IP tersebut.
3. Karena IP tersebut di-whitelist, Mesin Korelasi **mengabaikan log tersebut sepenuhnya**.

#### Cara Eksekusi
```powershell
python simulator.py --scenario 6
```

#### Apa yang Terjadi di Terminal?
```text
>>> Skenario 6: Careless Whitelisting (Fatal Error / Blind Spot Demo)
1. Memasukkan IP 203.0.113.88 ke Whitelist SIEM (dalih: IP VIP/Vendor)...
  [+] IP 203.0.113.88 sekarang resmi di-whitelist.
2. Hacker sekarang menyerang melalui IP 203.0.113.88 (mengirim rentetan serangan DDoS)...

  Hasil Pengecekan Mesin Korelasi:
  Total Serangan Terkirim: 15 request cepat
  Total Alarm yang Dipicu SIEM: 0 alarm
  [FATAL ERROR CONFIRMED] Mesin Korelasi sepenuhnya BUTA karena IP di-whitelist!
[OK] Skenario 6 berhasil mendemonstrasikan bahaya Careless Whitelisting.
```

#### Pembuktian di Dashboard Web
1. Lihat tabel **Active Whitelisted IPs**: IP `203.0.113.88` terdaftar.
2. Periksa **Recent Ingestion Stream**: 15 request masuk tercatat di log.
3. Periksa **Real-Time Alerts**: **TIDAK ADA ALARM APAPUN YANG DIPICU!**
4. *Uji Pemulihan*: Klik tombol **🗑️ Hapus** pada IP tersebut di tabel Whitelist dashboard, lalu tembakkan serangan lagi. Alarm DDoS seketika berbunyi normal kembali!

---

### Skenario 7: Data Cacat & Time Drift (Gatekeeper Negative Testing)

#### Tujuan
Membuktikan ketahanan gerbang masuk SIEM (*Gatekeeper*) dalam menolak data kotor (*malformed JSON*) dan log dengan anomali waktu (*Time Drift Error*), serta menjamin server SIEM **tidak crash**.

#### Kasus Uji Negatif yang Ditembakkan:
1. **JSON Kosong pada Field Wajib**: Field `ip_address` bernilai `""`.
2. **Format IP Rusak**: Nilai `999.999.999.999` (bukan format IPv4 valid).
3. **Time Drift Lampau (> 24 Jam)**: Nilai timestamp tahun 1970 (`1970-01-01T00:00:00Z`).
4. **Time Drift Masa Depan**: Nilai timestamp +1 tahun dari sekarang.

#### Cara Eksekusi
```powershell
python simulator.py --scenario 7
```

#### Apa yang Terjadi?
```text
>>> Skenario 7: Data Cacat & Time Drift (Negative Testing & Robustness)
Memastikan Gatekeeper SIEM menolak data kotor dengan HTTP 422 tanpa menyebabkan crash.
  [PASS] JSON tanpa IP Address (Field Wajib Kosong) -> HTTP 422 (Ditolak Sesuai Spesifikasi)
  [PASS] Format IP Bukan IPv4 ('not-an-ip') -> HTTP 422 (Ditolak Sesuai Spesifikasi)
  [PASS] Time Drift Error: Tahun 1970 (> 24 Jam Lalu) -> HTTP 422 (Ditolak Sesuai Spesifikasi)
  [PASS] Time Drift Error: Dari Masa Depan (+1 Tahun) -> HTTP 422 (Ditolak Sesuai Spesifikasi)
  [+] Health Check: SIEM tetap stabil, aktif dan responsif (No Crash)!
[OK] Hasil Skenario 7: Seluruh tes negatif lulus validasi gatekeeper.
```

*SIEM tetap aktif 100%, metrik server berjalan normal, dan data kotor tidak mencemari database in-memory.*

---

### 🌟 Menjalankan Tur Lengkap (Semua 7 Skenario Sekaligus)
Jika Anda ingin mendemonstrasikan seluruh skenario secara berurutan dalam satu kali klik:
```powershell
python simulator.py --all
```
Perintah ini akan:
1. Mereset memori SIEM.
2. Menjalankan Skenario 1 s/d 7 secara sekuensial dengan jeda waktu 1 detik.
3. Memberikan laporan ringkasan keberhasilan pengujian di akhir proses.

---

## 🧪 Otomasi Pengujian (Automated Unit & Integration Tests)

Untuk memvalidasi integritas kode secara otomatis tanpa perlu membuka peramban, jalankan rangkaian uji otomatis menggunakan `pytest`:

```powershell
pytest test_siem.py -v
```

### Hasil Eksekusi Uji Otomatis:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1
collected 12 items

test_siem.py::test_missing_ip_address_rejected PASSED                    [  8%]
test_siem.py::test_invalid_ipv4_rejected PASSED                          [ 16%]
test_siem.py::test_time_drift_past_rejected PASSED                       [ 25%]
test_siem.py::test_time_drift_future_rejected PASSED                     [ 33%]
test_siem.py::test_invalid_event_type_rejected PASSED                    [ 41%]
test_siem.py::test_rule_1_ddos_detection PASSED                          [ 50%]
test_siem.py::test_rule_2_impossible_travel PASSED                       [ 58%]
test_siem.py::test_rule_3_distributed_brute_force PASSED                 [ 66%]
test_siem.py::test_rule_4_off_hours_anomaly PASSED                       [ 75%]
test_siem.py::test_rule_5_data_exfiltration PASSED                       [ 83%]
test_siem.py::test_careless_whitelisting_blinds_correlation_engine PASSED [ 91%]
test_siem.py::test_stats_and_reset_endpoints PASSED                      [100%]

======================== 12 passed in 1.90s ========================
```

---

## 📡 Daftar Endpoint API SIEM

| Method | Endpoint | Deskripsi | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Melayani web dashboard HTML/JS/CSS | `200 OK` |
| `POST` | `/api/ingest` | Menerima & memvalidasi log telemetri, memicu alarm | `201 Created` / `422 Unprocessable` |
| `GET` | `/api/alerts` | Mengambil daftar alarm aktif (bisa difilter `severity`) | `200 OK` |
| `GET` | `/api/logs` | Mengambil 15 log raw terbaru yang di-ingest | `200 OK` |
| `GET` | `/api/stats` | Mengambil statistik agregasi metrik SOC | `200 OK` |
| `POST` | `/api/whitelist` | Menambahkan IP ke daftar pengecualian (*Blind Spot*) | `200 OK` |
| `GET` | `/api/whitelist` | Melihat daftar IP yang di-whitelist | `200 OK` |
| `DELETE` | `/api/whitelist/{ip}`| Menghapus IP dari whitelist | `200 OK` / `404 Not Found` |
| `POST` | `/api/reset` | Mereset seluruh log, alert, dan whitelist in-memory | `200 OK` |

---

## 📁 Struktur Direktori Proyek

```
CommandCenter/
├── app/
│   ├── __init__.py          # Modul Python app
│   ├── main.py              # Definisi router FastAPI, CORS, & integrasi static files
│   ├── models.py            # Model Pydantic, IPv4 validator, & time drift rule
│   ├── engine.py            # Mesin korelasi 5 rules, windowing event, & whitelist
│   └── static/
│       ├── index.html       # Antarmuka Command Center SOC
│       ├── style.css        # Tema cyberpunk dark & animasi berkedip merah KRITIS
│       └── app.js           # Polling real-time 2s & handler skenario
├── simulator.py             # Script simulator interaktif 7 skenario serangan
├── test_siem.py             # Test suite 12 unit/integration test otomatis
├── requirements.txt         # Daftar dependensi Python
├── run_server.bat           # Launcher server satu-klik
├── run_simulator.bat        # Launcher simulator satu-klik
├── mini_siem_product_requirements_document.md # Dokumen PRD asli
└── README.md                # Panduan teknis lengkap & PoC skenario
```

---

## 🛡️ Catatan Tambahan untuk Demonstrasi
*   **Tombol Reset**: Setiap kali Anda ingin memulai demonstrasi bersih dari awal, tekan tombol **🔄 Reset SIEM State** di bilah navigasi dashboard atau jalankan `python simulator.py --reset`.
*   **Pengujian Browser Mandiri**: Anda tidak harus menggunakan terminal untuk demonstrasi; tombol skenario di sebelah kanan dashboard web terhubung langsung ke API ingestion yang sama.
