# 📄 PRD.md: Mini-SIEM Simulator (V2.1 - Real Log Replay & SOAR Active Defense Edition)

## 1. Ringkasan Produk
**Mini-SIEM** adalah aplikasi simulasi *Security Information and Event Management* berskala kecil berbasis API. Sistem ini dirancang untuk mendemonstrasikan secara *real-time* bagaimana pusat komando operasi keamanan (SOC):
1. Menerima, memvalidasi, dan menormalisasi log telemetri heterogen (*Gatekeeper Ingestion*).
2. Membaca format log autentik dunia nyata (Nginx/Apache Combined, Linux Syslog RFC 3164, RFID Access CSV, PostgreSQL PGAudit JSONL) melalui Universal Log Adapter.
3. Mendeteksi anomali melalui mesin korelasi berbasis aturan (*Rule-based Correlation Engine*).
4. Menangani *Alert Fatigue* dengan debouncing cerdas.
5. Memitigasi kegagalan transmisi data cacat dan *Time Drift Error* (HTTP 422).
6. Mengungkap bahaya *Blind Spot* akibat *Careless Whitelisting* dan serangan *Low & Slow APT* (tantangan *Hot vs Cold Storage*).
7. Menjalankan penanganan insiden aktif melalui **SOAR Playbook (Host Containment / Network Quarantine)** yang memutus paket penyerang di gerbang masuk (*Gatekeeper HTTP 403 Dropped*).

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
* **SOAR Active Enforcement:** Jika IP pengirim tercatat dalam daftar karantina (`isolated_hosts`), Gatekeeper langsung menolak log dengan kode status **HTTP 403 (Forbidden)** dan menambah metrik *Blocked Containment Traffic*.
* **Validasi Negatif:** Sistem merespons HTTP 422 (*Unprocessable Entity*) dan menolak log jika:
  * Format JSON rusak (sintaks terputus) atau atribut wajib (seperti IP) hilang/bernilai `null`.
  * Format IP bukan IPv4 valid (misal: `999.999.999.999`).
  * `timestamp` berasal dari lebih dari 24 jam lampau atau masa depan (*Time Drift Error*).

### Fitur B: Universal Log Adapter, 24 Variant Sample Logs & Real-World Replay
* Modul `app/log_adapter.py` membaca berkas log fisik dari direktori `sample_logs/`. Masing-masing skenario (1 s/d 8) memiliki **3 varian berkas log realistis** (total 24 berkas):
  * **Skenario 1 (Trafik Normal):** `web_access_normal_1.log` (E-Commerce), `web_access_normal_2.log` (HR Portal), `web_access_normal_3.log` (Support Desk).
  * **Skenario 2 (DDoS Attack):** `nginx_ddos_flood_1.log` (IP `45.33.32.156`), `nginx_ddos_flood_2.log` (IP `194.26.29.112`), `nginx_ddos_flood_3.log` (IP `185.220.101.45`).
  * **Skenario 3 (Impossible Travel):** `vpn_and_gate_access_1.csv` (`sarah_security`: Jakarta vs Frankfurt), `vpn_and_gate_access_2.csv` (`budi_finance`: Surabaya vs Dallas), `vpn_and_gate_access_3.csv` (`ahmad_devops`: Singapore vs Moscow).
  * **Skenario 4 (Distributed Brute Force):** `auth_sshd_bruteforce_1.log` (`admin_corp` via Tor), `auth_sshd_bruteforce_2.log` (`root` via botnet), `auth_sshd_bruteforce_3.log` (`svc_deploy` via Cloud VPS).
  * **Skenario 5 (Data Exfiltration):** `postgres_audit_exfiltration_1.jsonl` (`dev_rogue`), `postgres_audit_exfiltration_2.jsonl` (`contractor_analyst`), `postgres_audit_exfiltration_3.jsonl` (`intern_badactor`).
  * **Skenario 6 (Careless Whitelist):** `careless_whitelist_attack_1.log` (IP `203.0.113.88`), `careless_whitelist_attack_2.log` (IP `198.51.100.50`), `careless_whitelist_attack_3.log` (IP `192.0.2.77`).
  * **Skenario 7 (Data Cacat/Drift):** `legacy_corrupted_device_1.log` (IoT Gateway), `legacy_corrupted_device_2.log` (Branch Router), `legacy_corrupted_device_3.log` (SCADA PLC).
  * **Skenario 8 (Low & Slow APT):** `apt_recon_and_exploit_1.log` (IP `198.51.100.77`), `apt_recon_and_exploit_2.log` (IP `203.0.113.144`), `apt_recon_and_exploit_3.log` (IP `192.0.2.199`).
  * **Skenario 9 (OT Hardware Sabotage - AC Central Shutdown via MQTT):** `mqtt_datacenter_hvac_1.jsonl` (CRAC-AC-CENTRAL-01 / Hall A), `mqtt_datacenter_hvac_2.jsonl` (HVAC-CHILLER-MAIN-02 / Plant), `mqtt_datacenter_hvac_3.jsonl` (PAC-SERVER-ROW-C03 / AI Cluster).
* **Random Variant Selection & Deterministic Overrides:** Logika pemanggilan simulator secara otomatis memilih acak 1 dari 3 varian berkas log per skenario (`variant=None` -> `random.choice([1, 2, 3])`). Analis juga dapat memilih varian spesifik secara deterministik via query parameter `?variant=1..3` pada API atau flag CLI `--variant 1..3`.
* **Dynamic Timestamp Shifting:** Mengonversi timestamp historis secara dinamis relatif terhadap waktu nyata sistem (`NOW()`) saat di-replay, sehingga data audit asli tetap utuh sekaligus lolos Gatekeeper Time Drift Check dan memicu sliding windows korelasi.
* Endpoint `POST /api/simulator/replay?scenario={1..9}&variant={1..3}`: Menjalankan eksekusi replay langsung di sisi backend untuk CLI maupun Dashboard Browser.

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
9. **Skenario 9 (OT Hardware Sabotage - AC Central Shutdown via MQTT):** Replay dari `mqtt_datacenter_hvac.jsonl` mendemonstrasikan pembacaan status sensor hardware AC Central disusul deteksi perintah ilegal mematikan AC Central di datacenter via protokol MQTT (Rule Kritis OT Sabotage).
10. **Demo SOAR Active Defense:** Menjalankan `python simulator.py --soar` untuk memperagakan isolasi IP `45.33.32.156`, pemutusan traffic penyerang secara instan di Gatekeeper (HTTP 403), dan pemulihan karantina.

## 5. Tumpukan Teknologi (Tech Stack)
* **Backend:** Python 3.11 + FastAPI (Asynchronous, High-Performance, ASGI).
* **Validasi Skema:** Pydantic V2 + RFC 5424/OCSF normalization logic.
* **Adapter & Ingestion:** Universal Log Adapter (`app/log_adapter.py`) dengan regex parser multi-format.
* **Penyimpanan Telemetri:** *In-memory stateful store* (Event cache, Active Alerts, Whitelist, Suspicious Greylist, Isolated Hosts, SOAR Audit Trail).
* **Frontend:** HTML5 + CSS3 Grid/Flexbox + Vanilla JavaScript (Cyberpunk SOC Dark Theme, SOAR Active Panel, tanpa dependencies eksternal).
* **Simulator & Testing:** Python Requests, Pytest test suite (29 automated test cases).
