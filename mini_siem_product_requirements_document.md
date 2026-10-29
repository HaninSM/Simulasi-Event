# 📄 PRD.md: Mini-SIEM Simulator (V2.0 - Real Log Replay & Advanced Threat Edition)

## 1. Ringkasan Produk
**Mini-SIEM** adalah aplikasi simulasi *Security Information and Event Management* berskala kecil berbasis API. Sistem ini dirancang untuk mendemonstrasikan secara *real-time* bagaimana pusat komando operasi keamanan (SOC):
1. Menerima, memvalidasi, dan menormalisasi log telemetri heterogen (*Gatekeeper Ingestion*).
2. Membaca format log autentik dunia nyata (Nginx/Apache Combined, Linux Syslog RFC 3164, RFID Access CSV, PostgreSQL PGAudit JSONL) melalui Universal Log Adapter.
3. Mendeteksi anomali melalui mesin korelasi berbasis aturan (*Rule-based Correlation Engine*).
4. Menangani *Alert Fatigue* dengan debouncing cerdas.
5. Memitigasi kegagalan transmisi data cacat dan *Time Drift Error* (HTTP 422).
6. Mengungkap bahaya *Blind Spot* akibat *Careless Whitelisting* dan serangan *Low & Slow APT* (tantangan *Hot vs Cold Storage*).

## 2. Spesifikasi Data (Data Contracts)
Semua log yang masuk ke sistem (Ingestion) wajib memenuhi format JSON kanonikal berikut. Sistem Gatekeeper akan menolak data yang tidak mematuhi kontrak ini:
```json
{
  "timestamp": "YYYY-MM-DDThh:mm:ssZ",
  "event_type": "login_attempt | web_request | database_download",
  "user_id": "string (non-empty)",
  "ip_address": "string (IPv4)",
  "location": "string (non-empty)",
  "status": "success | failed"
}
```

## 3. Fitur Utama & Kriteria Penerimaan

### Fitur A: API Ingestion & Validasi (Gatekeeper)
* Menerima log melalui `POST /api/ingest`.
* **Validasi Negatif:** Sistem merespons HTTP 422 (*Unprocessable Entity*) dan menolak log jika:
  * Format JSON rusak (sintaks terputus) atau atribut wajib (seperti IP) hilang/bernilai `null`.
  * Format IP bukan IPv4 valid (misal: `999.999.999.999`).
  * `timestamp` berasal dari lebih dari 24 jam lampau atau masa depan (*Time Drift Error*).

### Fitur B: Universal Log Adapter & Real-World Log Replay
* Modul `app/log_adapter.py` membaca berkas log fisik dari direktori `sample_logs/`:
  * `web_access_normal.log`: Format standar Nginx/Apache Combined Log.
  * `nginx_ddos_flood.log`: Telemetri akses web HTTP flooding L7.
  * `vpn_and_gate_access.csv`: Log akses fisik kartu RFID pintu vs login VPN luar negeri.
  * `auth_sshd_bruteforce.log`: Format Syslog Linux RFC 3164 `/var/log/auth.log` dari multi-IP.
  * `postgres_audit_exfiltration.jsonl`: Telemetri audit query database PostgreSQL PGAudit.
  * `careless_whitelist_attack.log`: Log akses web dari IP yang telah masuk daftar whitelist ceroboh.
  * `legacy_corrupted_device.log`: Telemetri anomali (IP null, IP 999.x, JSON truncated, reset jam CMOS 1970).
  * `apt_recon_and_exploit.log`: Jejak pengintaian awal vs serangan eksploitasi berjarak 20 hari.
* **Dynamic Timestamp Shifting:** Mengonversi timestamp historis secara dinamis relatif terhadap waktu nyata sistem (`NOW()`) saat di-replay, sehingga data audit asli tetap utuh sekaligus lolos Gatekeeper Time Drift Check dan memicu sliding windows korelasi.
* Endpoint `POST /api/simulator/replay?scenario={1..8}`: Menjalankan eksekusi replay langsung di sisi backend untuk CLI maupun Dashboard Browser.

### Fitur C: Mesin Korelasi Berbasis Aturan (The Brain)
Sistem memproses log di memori dan memicu alarm berdasarkan aturan berikut:
1. **DDoS / Botnet (Level: TINGGI):** > 10 `web_request` dari 1 `ip_address` yang sama dalam rentang 10 detik.
2. **Impossible Travel (Level: KRITIS):** 2 `login_attempt` sukses dari 1 `user_id` yang sama di `location` berbeda dalam waktu < 1 jam.
3. **Distributed Brute Force (Level: TINGGI):** > 5 `login_attempt` gagal untuk 1 `user_id` yang sama, berasal dari > 3 `ip_address` berbeda dalam 1 menit.
4. **Off-Hours Anomaly (Level: MENENGAH):** Aktivitas `status: success` oleh pengguna manusia di luar jam operasional kantor (00:00 - 05:00 waktu lokal).
5. **Data Exfiltration / Insider Threat (Level: KRITIS):** 1 `user_id` melakukan `database_download` > 50 kali dalam rentang 1 menit.
6. **Advanced Persistent Threat (APT) / Temporal Correlation:** Korelasi jejak *reconnaissance* dari *Cold Storage* yang diaktifkan kembali (*rehydrated*) terhadap *exploit request* di *Hot Storage* menggunakan tabel stateful *Suspicious Greylist/Watchlist*.

### Fitur D: Dashboard Real-Time & Tuning
* **Live SOC Monitor:** Antarmuka web mengambil data dari `GET /api/alerts` setiap 2 detik.
* **Visualisasi:** Alarm kritis berkedip merah dengan penanda waktu ISO.
* **Careless Whitelisting:** Menyediakan kontrol (`POST /api/whitelist`) untuk mengecualikan IP secara manual, memvisualisasikan terciptanya celah *Blind Spot*.
* **Replay Launcher:** Panel peluncur skenario 1 s/d 8 langsung dari antarmuka web yang terhubung ke physical log replay.

## 4. Daftar Skenario Demonstrasi
1. **Skenario 1 (Trafik Normal):** Replay dari `web_access_normal.log` membuktikan aktivitas sah karyawan tidak memicu alarm (*False Positive zero*).
2. **Skenario 2 (DDoS Attack):** Replay dari `nginx_ddos_flood.log` memicu Rule 1 (DDoS / Botnet).
3. **Skenario 3 (Impossible Travel):** Replay dari `vpn_and_gate_access.csv` memicu Rule 2 (Impossible Travel Jakarta vs Frankfurt).
4. **Skenario 4 (Distributed Brute Force):** Replay dari `auth_sshd_bruteforce.log` memicu Rule 3 (Multi-IP SSH Brute Force).
5. **Skenario 5 (Data Exfiltration):** Replay dari `postgres_audit_exfiltration.jsonl` memicu Rule 5 (Massive database download insider threat).
6. **Skenario 6 (Careless Whitelisting):** Replay dari `careless_whitelist_attack.log` membuktikan IP yang di-whitelist membutakan SIEM.
7. **Skenario 7 (Data Cacat & Time Drift):** Replay dari `legacy_corrupted_device.log` membuktikan Gatekeeper menolak log rusak tanpa membuat server crash (HTTP 422).
8. **Skenario 8 (Low & Slow APT):** Replay dari `apt_recon_and_exploit.log` mendemonstrasikan mitigasi kebutaan korelasi akibat rotasi Hot ke Cold Storage menggunakan persistent watchlist.

## 5. Tumpukan Teknologi (Tech Stack)
* **Backend:** Python 3.11 + FastAPI (Asynchronous, High-Performance, ASGI).
* **Validasi Skema:** Pydantic V2 + RFC 5424/OCSF normalization logic.
* **Adapter & Ingestion:** Universal Log Adapter (`app/log_adapter.py`) dengan regex parser multi-format.
* **Penyimpanan Telemetri:** *In-memory stateful store* (Event cache, Active Alerts, Whitelist, Suspicious Greylist).
* **Frontend:** HTML5 + CSS3 Grid/Flexbox + Vanilla JavaScript (Cyberpunk SOC Dark Theme, tanpa dependencies eksternal).
* **Simulator & Testing:** Python Requests, Pytest test suite (20 automated test cases).
