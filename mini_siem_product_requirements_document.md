# 📄 PRD.md: Mini-SIEM Simulator (V1.0 - Full Scenario Edition)

## 1. Ringkasan Produk
**Mini-SIEM** adalah aplikasi simulasi *Security Information and Event Management* berskala kecil berbasis API. Sistem ini dirancang untuk mendemonstrasikan secara *real-time* bagaimana pusat komando keamanan siber menerima log, mendeteksi anomali melalui mesin korelasi, menangani *alert fatigue*, dan memitigasi kegagalan pengiriman data kotor.

## 2. Spesifikasi Data (Data Contracts)
Semua log yang masuk ke sistem (Ingestion) wajib menggunakan format JSON berikut. Sistem akan menolak data yang tidak mematuhi kontrak ini.
```json
{
  "timestamp": "YYYY-MM-DDThh:mm:ssZ",
  "event_type": "login_attempt | web_request | database_download",
  "user_id": "string",
  "ip_address": "string (IPv4)",
  "location": "string",
  "status": "success | failed"
}
```

## 3. Fitur Utama & Kriteria Penerimaan

### Fitur A: API Ingestion & Validasi (Gatekeeper)
*   Menerima log melalui `POST /api/ingest`.
*   **Validasi Negatif:** Sistem akan merespons HTTP 422 (Unprocessable Entity) dan menolak log jika:
    *   Format JSON rusak atau kolom wajib (seperti IP) kosong.
    *   `timestamp` berasal dari lebih dari 24 jam yang lalu atau dari masa depan (*Time Drift Error*).

### Fitur B: Mesin Korelasi Berbasis Aturan (The Brain)
Sistem memproses log di memori dan memicu alarm berdasarkan 5 aturan berikut:
1.  **DDoS / Botnet (Level: TINGGI):** > 10 `web_request` dari 1 `ip_address` yang sama dalam 10 detik.
2.  **Impossible Travel (Level: KRITIS):** 2 `login_attempt` sukses dari 1 `user_id` yang sama, namun di `location` berbeda dalam waktu < 1 jam.
3.  **Distributed Brute Force (Level: TINGGI):** > 5 `login_attempt` gagal untuk 1 `user_id` yang sama, berasal dari > 3 `ip_address` berbeda dalam 1 menit.
4.  **Off-Hours Anomaly (Level: MENENGAH):** Aktivitas `status: success` (selain mesin) yang terjadi di luar jam kerja (00:00 - 05:00 waktu lokal).
5.  **Data Exfiltration / Insider Threat (Level: KRITIS):** 1 `user_id` melakukan `database_download` > 50 kali dalam 1 menit.

### Fitur C: Dashboard Real-Time & Tuning
*   **Live Monitor:** Halaman web HTML/JS mengambil data dari `GET /api/alerts` setiap 2 detik.
*   **Visualisasi:** Alarm kritis berwarna merah berkedip dengan cap waktu.
*   **Careless Whitelisting:** Menyediakan *input form* (`POST /api/whitelist`) bagi Kapten SIEM untuk memasukkan IP secara manual. IP yang terdaftar di sini akan diabaikan oleh Mesin Korelasi (menciptakan celah *Blind Spot* yang disengaja untuk tujuan edukasi/demo).

## 4. Daftar Skenario Demonstrasi
Skrip eksternal (`simulator.py`) akan menyediakan tombol/fungsi untuk menembakkan 7 skenario berikut ke API SIEM:
1.  **Trafik Normal:** Karyawan bekerja seperti biasa (Tidak ada alarm).
2.  **DDoS Attack:** Ribuan *request* dari 1 IP (Memicu Rule 1).
3.  **Impossible Travel:** Peretasan dengan IP beda benua dalam hitungan detik (Memicu Rule 2).
4.  **Distributed Brute Force:** Serangan kata sandi dari banyak IP secara pelan (Memicu Rule 3).
5.  **Data Exfiltration:** Orang dalam mengunduh database massal (Memicu Rule 5).
6.  **Careless Whitelisting (Fatal Error):** Mendemonstrasikan bahwa melakukan *whitelist* pada satu IP akan membutakan SIEM ketika *hacker* menyusup via IP tersebut.
7.  **Data Cacat / Time Drift (Negative Test):** Mengirim JSON tanpa IP dan JSON dengan tahun 1970. Memastikan SIEM tidak *crash*.

## 5. Tumpukan Teknologi (Tech Stack)
*   **Backend:** Python 3 + FastAPI (Asynchronous, performa tinggi, *built-in validation* dengan Pydantic).
*   **Database:** *In-memory variables* (list/dict) khusus untuk simulasi ringan.
*   **Frontend:** HTML5 + Vanilla JavaScript + CSS murni (Tanpa framework, *plug-and-play*).
*   **Simulator:** Python *requests script*.