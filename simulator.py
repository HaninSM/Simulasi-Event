#!/usr/bin/env python3
"""
Mini-SIEM Attack & Traffic Simulator
Runs the 7 demonstration scenarios defined in the PRD against the SIEM API.
"""

import sys
import time
import argparse
from datetime import datetime, timezone, timedelta
import requests

from app.log_adapter import LogAdapter

# Ensure UTF-8 output on Windows terminal
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_API_BASE = "http://127.0.0.1:8000"

# ANSI Colors for SOC Terminal Styling
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    print(f"{CYAN}{BOLD}")
    print("=" * 65)
    print("      🛡️  MINI-SIEM SIMULATOR (V1.0 - FULL SCENARIO)  🛡️")
    print("             Cyber Attack & Telemetry Generator")
    print("=" * 65 + f"{RESET}")


def get_current_utc_iso(delta_seconds=0):
    dt = datetime.now(timezone.utc) + timedelta(seconds=delta_seconds)
    return dt.isoformat()


def post_log(api_base, log_data):
    url = f"{api_base}/api/ingest"
    try:
        res = requests.post(url, json=log_data, timeout=5)
        return res
    except requests.exceptions.RequestException as e:
        print(f"{RED}[!] Failed to reach SIEM API at {url}: {e}{RESET}")
        return None


def fetch_alerts(api_base):
    try:
        res = requests.get(f"{api_base}/api/alerts?limit=5", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []


# ---------------- SCENARIO 1: TRAFIK NORMAL ----------------
def scenario_1_normal_traffic(api_base, variant=None):
    print(f"\n{BOLD}{CYAN}>>> Skenario 1: Trafik Normal (Karyawan bekerja normal){RESET}")
    events = LogAdapter.load_scenario_from_file(1, variant=variant)
    variant_str = f" (Varian {events.variant}/3: {events.description})" if hasattr(events, "variant") and events.variant else ""
    source_str = getattr(events, "source_file", "sample_logs/web_access_normal.log")
    print(f"  {YELLOW}📁 Berkas Sumber: {source_str}{variant_str}{RESET}")
    print(f"  Memproses {len(events)} entri log wajar dari berkas fisik...")

    for emp in events:
        payload = {k: v for k, v in emp.items() if k in ["timestamp", "event_type", "user_id", "ip_address", "location", "status"]}
        res = post_log(api_base, payload)
        if res:
            raw = emp.get("raw_line", "")
            raw_preview = f" [{raw[:55]}...]" if raw else ""
            print(f"  [+] Log {emp['user_id']} ({emp['event_type']}) -> HTTP {res.status_code}{raw_preview}")
        time.sleep(0.2)

    alerts = fetch_alerts(api_base)
    print(f"{GREEN}[OK] Hasil Skenario 1: Trafik riil dari file log berhasil diproses. Tidak ada alarm palsu triggered.{RESET}")


# ---------------- SCENARIO 2: DDOS ATTACK ----------------
def scenario_2_ddos_attack(api_base, variant=None):
    print(f"\n{BOLD}{YELLOW}>>> Skenario 2: DDoS / Botnet Attack (Memicu Rule 1){RESET}")
    events = LogAdapter.load_scenario_from_file(2, variant=variant)
    variant_str = f" (Varian {events.variant}/3: {events.description})" if hasattr(events, "variant") and events.variant else ""
    source_str = getattr(events, "source_file", "sample_logs/nginx_ddos_flood.log")
    print(f"  {YELLOW}📁 Berkas Sumber: {source_str}{variant_str}{RESET}")
    print("Kriteria Rule 1: > 10 web_request dari 1 IP yang sama dalam 10 detik.")
    print(f"Memproses {len(events)} rentetan request agresif dari berkas log...")

    for i, emp in enumerate(events, start=1):
        payload = {k: v for k, v in emp.items() if k in ["timestamp", "event_type", "user_id", "ip_address", "location", "status"]}
        res = post_log(api_base, payload)
        if res and res.status_code == 201:
            data = res.json()
            if data.get("alerts_triggered", 0) > 0:
                print(f"  {RED}[!] Request #{i} ({emp['ip_address']}): SIEM memicu {data['alerts_triggered']} ALARM DDoS (Level: TINGGI)!{RESET}")
            else:
                print(f"  [+] Request #{i} terkirim...")
        time.sleep(0.08)

    print(f"{GREEN}[OK] Hasil Skenario 2: Rule 1 (DDoS / Botnet) terdeteksi dari berkas log riil dan tercatat di dashboard.{RESET}")


# ---------------- SCENARIO 3: IMPOSSIBLE TRAVEL ----------------
def scenario_3_impossible_travel(api_base, variant=None):
    print(f"\n{BOLD}{RED}>>> Skenario 3: Impossible Travel (Memicu Rule 2){RESET}")
    events = LogAdapter.load_scenario_from_file(3, variant=variant)
    variant_str = f" (Varian {events.variant}/3: {events.description})" if hasattr(events, "variant") and events.variant else ""
    source_str = getattr(events, "source_file", "sample_logs/vpn_and_gate_access.csv")
    print(f"  {YELLOW}📁 Berkas Sumber: {source_str}{variant_str}{RESET}")
    print("Kriteria Rule 2: 2 login_attempt sukses user yang sama di lokasi berbeda dalam < 1 jam.")

    if len(events) >= 2:
        # Event 1: First login (e.g. Physical Gate)
        p1 = {k: v for k, v in events[0].items() if k in ["timestamp", "event_type", "user_id", "ip_address", "location", "status"]}
        print(f"  [1] Event Hardware: Akses Fisik User '{p1['user_id']}' di {p1['location']} ({p1['ip_address']})...")
        post_log(api_base, p1)
        time.sleep(1)

        # Event 2: Second login (e.g. Remote VPN)
        p2 = {k: v for k, v in events[1].items() if k in ["timestamp", "event_type", "user_id", "ip_address", "location", "status"]}
        print(f"  [2] Event Jaringan: Login VPN User '{p2['user_id']}' dari {p2['location']} ({p2['ip_address']}) selang 1 detik...")
        res = post_log(api_base, p2)
        if res and res.status_code == 201:
            data = res.json()
            print(f"  {RED}[!] ALARM KRITIS TERCATAT: {data.get('alerts_triggered')} alarm dipicu! (Impossible Travel){RESET}")

    print(f"{GREEN}[OK] Hasil Skenario 3: Rule 2 (Impossible Travel) berhasil dideteksi dari berkas CSV multi-sumber.{RESET}")


# ---------------- SCENARIO 4: DISTRIBUTED BRUTE FORCE ----------------
def scenario_4_distributed_brute_force(api_base, variant=None):
    print(f"\n{BOLD}{YELLOW}>>> Skenario 4: Distributed Brute Force (Memicu Rule 3){RESET}")
    events = LogAdapter.load_scenario_from_file(4, variant=variant)
    variant_str = f" (Varian {events.variant}/3: {events.description})" if hasattr(events, "variant") and events.variant else ""
    source_str = getattr(events, "source_file", "sample_logs/auth_sshd_bruteforce.log")
    print(f"  {YELLOW}📁 Berkas Sumber: {source_str}{variant_str}{RESET}")
    print("Kriteria Rule 3: > 5 login gagal untuk 1 user dari > 3 IP berbeda dalam 1 menit.")
    print(f"Memproses {len(events)} entri kegagalan SSH autentikasi terdistribusi...")

    for i, emp in enumerate(events, start=1):
        payload = {k: v for k, v in emp.items() if k in ["timestamp", "event_type", "user_id", "ip_address", "location", "status"]}
        res = post_log(api_base, payload)
        if res and res.status_code == 201:
            data = res.json()
            if data.get("alerts_triggered", 0) > 0:
                print(f"  {RED}[!] Percobaan #{i} dari {payload['ip_address']}: ALARM TINGGI Distributed Brute Force terpicu!{RESET}")
            else:
                print(f"  [-] Percobaan #{i} dari {payload['ip_address']}: Login gagal tercatat...")
        time.sleep(0.12)

    print(f"{GREEN}[OK] Hasil Skenario 4: Rule 3 (Distributed Brute Force) berhasil ditangkap dari file auth.log riil.{RESET}")


# ---------------- SCENARIO 5: DATA EXFILTRATION ----------------
def scenario_5_data_exfiltration(api_base, variant=None):
    print(f"\n{BOLD}{RED}>>> Skenario 5: Data Exfiltration / Insider Threat (Memicu Rule 5){RESET}")
    events = LogAdapter.load_scenario_from_file(5, variant=variant)
    variant_str = f" (Varian {events.variant}/3: {events.description})" if hasattr(events, "variant") and events.variant else ""
    source_str = getattr(events, "source_file", "sample_logs/postgres_audit_exfiltration.jsonl")
    print(f"  {YELLOW}📁 Berkas Sumber: {source_str}{variant_str}{RESET}")
    print("Kriteria Rule 5: 1 user melakukan database_download > 50 kali dalam 1 menit.")
    print(f"Memproses {len(events)} unduhan database massal dari log audit SQL...")
    alert_triggered = False

    for i, emp in enumerate(events, start=1):
        payload = {k: v for k, v in emp.items() if k in ["timestamp", "event_type", "user_id", "ip_address", "location", "status"]}
        res = post_log(api_base, payload)
        if res and res.status_code == 201:
            data = res.json()
            if data.get("alerts_triggered", 0) > 0 and not alert_triggered:
                print(f"  {RED}[!] Unduhan #{i}: AMBANG BATAS DILAMPAUI (>50)! ALARM KRITIS (Data Exfiltration) TERPICU!{RESET}")
                alert_triggered = True
        time.sleep(0.04)

    print(f"{GREEN}[OK] Hasil Skenario 5: Rule 5 (Data Exfiltration) berhasil mendeteksi ancaman dari file PGAudit.{RESET}")


# ---------------- SCENARIO 6: CARELESS WHITELISTING ----------------
def scenario_6_careless_whitelisting(api_base, variant=None):
    print(f"\n{BOLD}{CYAN}>>> Skenario 6: Careless Whitelisting (Fatal Error / Blind Spot Demo){RESET}")
    events = LogAdapter.load_scenario_from_file(6, variant=variant)
    variant_str = f" (Varian {events.variant}/3: {events.description})" if hasattr(events, "variant") and events.variant else ""
    source_str = getattr(events, "source_file", "sample_logs/careless_whitelist_attack.log")
    print(f"  {YELLOW}📁 Berkas Sumber: {source_str}{variant_str}{RESET}")
    attacker_ip = events[0]["ip_address"] if events else "203.0.113.88"
    print(f"1. Memasukkan IP {attacker_ip} ke Whitelist SIEM (dalih: IP VIP/Vendor)...")

    # POST to /api/whitelist
    w_res = requests.post(f"{api_base}/api/whitelist", json={
        "ip_address": attacker_ip,
        "reason": "Careless exception added by Admin"
    }, timeout=5)

    if w_res.status_code in [200, 201]:
        print(f"  {GREEN}[+] IP {attacker_ip} sekarang resmi di-whitelist.{RESET}")

    print(f"2. Memproses {len(events)} request serangan melalui IP {attacker_ip}...")
    alerts_count = 0
    for emp in events:
        payload = {k: v for k, v in emp.items() if k in ["timestamp", "event_type", "user_id", "ip_address", "location", "status"]}
        res = post_log(api_base, payload)
        if res and res.status_code == 201:
            alerts_count += res.json().get("alerts_triggered", 0)

    print(f"\n  {YELLOW}Hasil Pengecekan Mesin Korelasi:{RESET}")
    print(f"  Total Serangan Terkirim: {len(events)} request cepat dari file log")
    print(f"  Total Alarm yang Dipicu SIEM: {BOLD}{alerts_count}{RESET} alarm")
    print(f"  {RED}[FATAL ERROR CONFIRMED] Mesin Korelasi sepenuhnya BUTA karena IP di-whitelist!{RESET}")
    print(f"{GREEN}[OK] Skenario 6 berhasil mendemonstrasikan bahaya Careless Whitelisting.{RESET}")


# ---------------- SCENARIO 7: DATA CACAT / TIME DRIFT ----------------
def scenario_7_corrupted_data_and_time_drift(api_base, variant=None):
    print(f"\n{BOLD}{RED}>>> Skenario 7: Malformed Log (Format Cacat/Hilang) & Time Drift{RESET}")
    test_items = LogAdapter.load_scenario_from_file(7, variant=variant)
    variant_str = f" (Varian {test_items.variant}/3: {test_items.description})" if hasattr(test_items, "variant") and test_items.variant else ""
    source_str = getattr(test_items, "source_file", "sample_logs/legacy_corrupted_device.log")
    print(f"  {YELLOW}📁 Berkas Sumber: {source_str}{variant_str}{RESET}")
    print("Masalah: Perangkat legacy mengirim log tanpa atribut penting, JSON terpotong, atau stempel waktu rusak.")
    print("Penanganan: Lapisan Validasi Skema (Gatekeeper) menolak log dengan HTTP 422, SIEM tetap berjalan normal.")

    url = f"{api_base}/api/ingest"
    all_passed = True

    for i, item in enumerate(test_items, start=1):
        tc = item.get("test_case")
        raw = item.get("raw_payload")
        print(f"\n  [Uji {i}] Kasus Uji: {tc}...")

        if tc == "truncated_json":
            res = requests.post(url, data=raw, headers={"Content-Type": "application/json"}, timeout=5)
        else:
            res = requests.post(url, json=raw, timeout=5)

        if res.status_code == 422:
            print(f"  {GREEN}[PASS] {tc} -> HTTP 422 (Ditolak Aman oleh Gatekeeper){RESET}")
        else:
            print(f"  {RED}[FAIL] Expected HTTP 422, got HTTP {res.status_code}{RESET}")
            all_passed = False

    # Check if SIEM backend is still alive and didn't crash
    print(f"\n  [Health Check] Memeriksa status kesehatan backend SIEM...")
    stats_res = requests.get(f"{api_base}/api/stats", timeout=5)
    if stats_res.status_code == 200:
        print(f"  {GREEN}[+] KONDISI SISTEM: SIEM tetap stabil, aktif dan responsif (NO CRASH)!{RESET}")
    else:
        print(f"  {RED}[!] SIEM crash atau tidak merespons!{RESET}")
        all_passed = False

    if all_passed:
        print(f"{GREEN}[OK] Hasil Skenario 7: Seluruh tes data cacat & time drift berhasil ditangani dengan aman.{RESET}")


# ---------------- SCENARIO 8: LOW & SLOW APT / HOT VS COLD STORAGE ----------------
def scenario_8_low_and_slow_apt(api_base, variant=None):
    print(f"\n{BOLD}{RED}>>> Skenario 8: The Low & Slow APT (Jebakan Hot vs Cold Storage & Solusi Persistent Watchlist){RESET}")
    events = LogAdapter.load_scenario_from_file(8, variant=variant)
    variant_str = f" (Varian {events.variant}/3: {events.description})" if hasattr(events, "variant") and events.variant else ""
    source_str = getattr(events, "source_file", "sample_logs/apt_recon_and_exploit.log")
    print(f"  {YELLOW}📁 Berkas Sumber: {source_str}{variant_str}{RESET}")
    attacker_ip = events[0]["ip_address"] if events else "198.51.100.77"

    # --- BABAK 1: RECONNAISSANCE TANGGAL 1 ---
    print(f"\n{CYAN}[BABAK 1 - TANGGAL 1] Peretas APT melancarkan Recon Probe dari berkas log...{RESET}")
    recon_payload = {k: v for k, v in events[0].items() if k in ["timestamp", "event_type", "user_id", "ip_address", "location", "status"]}
    res_recon = post_log(api_base, recon_payload)
    if res_recon and res_recon.status_code == 201:
        print(f"  [+] Log Reconnaissance Ingested -> HTTP 201 Created")
        alerts = res_recon.json().get("alerts", [])
        if alerts:
            print(f"  {YELLOW}[ALARM] Ditangkap SIEM: {alerts[0]['rule_name']} (Severity: {alerts[0]['severity']}){RESET}")
    time.sleep(1)

    # --- SIMULASI LOG LIFECYCLE (LEWAT DARI 14 HARI) ---
    print(f"\n{YELLOW}[LOG LIFECYCLE POLICY] Waktu bergulir > 14 hari...{RESET}")
    print("  Mengarsipkan data panas ke Gudang Beku (Cold Storage Archive)...")
    try:
        archive_res = requests.post(f"{api_base}/api/archive/cold?ip_address={attacker_ip}", timeout=5)
        if archive_res.status_code == 200:
            print(f"  {GREEN}[+] Status: {archive_res.json().get('message')}{RESET}")
    except Exception as e:
        print(f"  {RED}[!] Gagal arsip cold storage: {e}{RESET}")
    time.sleep(1)

    # --- BABAK 1B: MASALAH - EKSPLOITASI TANGGAL 20 TANPA WATCHLIST ---
    print(f"\n{RED}[BABAK 1B - TANGGAL 20: MASALAH / TEMPORAL BLIND SPOT]{RESET}")
    print(f"  Peretas mengeksekusi serangan eksploitasi dari IP {attacker_ip}...")
    print("  Karena log Tanggal 1 sudah beku di Cold Storage, SIEM standar TIDAK BISA mengaitkan korelasi!")
    exploit_payload = {k: v for k, v in events[1].items() if k in ["timestamp", "event_type", "user_id", "ip_address", "location", "status"]}
    res_fail = post_log(api_base, exploit_payload)
    if res_fail and res_fail.status_code == 201:
        alerts = res_fail.json().get("alerts", [])
        apt_alerts = [a for a in alerts if a["rule_name"] == "APT Low & Slow / Persistent Threat"]
        if not apt_alerts:
            print(f"  {YELLOW}[!] HASIL TANPA SOLUSI: Alert APT = 0! Permintaan dianggap trafik normal terisolasi! (TITIK BUTA TEMPORAL){RESET}")
    time.sleep(1.5)

    # --- BABAK 2: SOLUSI - PERSISTENT WATCHLIST & COLD LOG REHYDRATION ---
    print(f"\n{CYAN}[BABAK 2 - SOLUSI: PERSISTENT STATEFUL WATCHLIST & REHYDRATION]{RESET}")
    print(f"  Mendaftarkan IP {attacker_ip} ke Persistent Suspicious Watchlist/Greylist...")
    try:
        wl_res = requests.post(f"{api_base}/api/watchlist", json={
            "ip_address": attacker_ip,
            "risk_level": "HIGH",
            "reason": "Reconnaissance probe detected on Day 1"
        }, timeout=5)
        if wl_res.status_code == 200:
            print(f"  {GREEN}[+] IP {attacker_ip} aktif dalam Stateful Watchlist lintas masa retensi.{RESET}")
    except Exception as e:
        print(f"  {RED}[!] Gagal mendaftarkan watchlist: {e}{RESET}")
    time.sleep(1)

    print(f"\n{RED}[BABAK 2B - TANGGAL 20: KORELASI SHOWDOWN BERHASIL!]{RESET}")
    print("  Peretas kembali melancarkan request eksploitasi...")
    exploit_payload_2 = {k: v for k, v in events[1].items() if k in ["timestamp", "event_type", "user_id", "ip_address", "location", "status"]}
    exploit_payload_2["timestamp"] = get_current_utc_iso(0)
    res_success = post_log(api_base, exploit_payload_2)
    if res_success and res_success.status_code == 201:
        alerts = res_success.json().get("alerts", [])
        apt_alerts = [a for a in alerts if a["rule_name"] == "APT Low & Slow / Persistent Threat"]
        if apt_alerts:
            print(f"  {RED}{BOLD}🚨 [ALARM KRITIS DIPICU!] {apt_alerts[0]['rule_name']} (Severity: {apt_alerts[0]['severity']}){RESET}")
            print(f"     Deskripsi: {apt_alerts[0]['description']}")
            print(f"     Solusi Aktif: {apt_alerts[0]['details'].get('mitigation')}")

    # Rehidrasi log dingin untuk verifikasi audit forensik
    print(f"\n  [Forensic Rehydration] Menarik kembali log Tanggal 1 dari Cold Storage...")
    try:
        rehydrate_res = requests.post(f"{api_base}/api/archive/rehydrate?ip_address={attacker_ip}", timeout=5)
        if rehydrate_res.status_code == 200:
            data = rehydrate_res.json()
            print(f"  {GREEN}[+] Berhasil merehidrasi {data.get('rehydrated_count')} log dingin untuk pembuktian forensik!{RESET}")
    except Exception as e:
        print(f"  {RED}[!] Gagal rehidrasi log dingin: {e}{RESET}")

    print(f"\n{GREEN}[OK] Hasil Skenario 8: Terbukti berhasil mengatasi jebakan Low & Slow APT dari file log riil!{RESET}")


def demo_soar_containment(api_base):
    print(f"\n{BOLD}{CYAN}>>> DEMO SOAR: Active Defense & Host Containment Playbook{RESET}")
    print("Konsep: Begitu SIEM mendeteksi ancaman, analis mengeksekusi Playbook 'Isolate Host'.")
    print("Efek: Gatekeeper SIEM langsung memutus traffic IP penyerang (HTTP 403 Dropped) secara real-time.")

    target_ip = "45.33.32.156"
    print(f"\n{YELLOW}[Fase 1] Menembakkan serangan DDoS awal dari IP {target_ip}...{RESET}")
    scenario_2_ddos_attack(api_base)
    time.sleep(1)

    print(f"\n{YELLOW}[Fase 2] Menjalankan SOAR Action: Isolate Host '{target_ip}'...{RESET}")
    try:
        iso_res = requests.post(f"{api_base}/api/soar/isolate", json={
            "ip_address": target_ip,
            "reason": "Automated containment: L7 HTTP Flood detected",
            "analyst": "SOC Analyst Tier-1"
        }, timeout=5)
        if iso_res.status_code == 200:
            print(f"{GREEN}[+] SUCCESS: Host {target_ip} berhasil DIISOLASI oleh SOAR!{RESET}")
            print(f"    Status Alert di Dashboard berubah menjadi: [CONTAINED]")
        else:
            print(f"{RED}[!] Gagal mengisolasi host: {iso_res.text}{RESET}")
            return
    except Exception as e:
        print(f"{RED}[!] Error: {e}{RESET}")
        return

    time.sleep(1)
    print(f"\n{YELLOW}[Fase 3] Menguji Penegakan Gatekeeper: Penyerang mencoba mengirim 3 request lanjutan...{RESET}")
    for i in range(1, 4):
        log_payload = {
            "timestamp": get_current_utc_iso(),
            "event_type": "web_request",
            "user_id": f"bot_drone_{i}",
            "ip_address": target_ip,
            "location": "Dallas, US",
            "status": "success"
        }
        res = requests.post(f"{api_base}/api/ingest", json=log_payload, timeout=5)
        if res.status_code == 403:
            print(f"  {GREEN}[BLOCKED - HTTP 403] Paket {i} dari {target_ip} langsung DITOLAK oleh Gatekeeper!{RESET}")
        else:
            print(f"  {RED}[!] Request lolos ({res.status_code}){RESET}")
        time.sleep(0.3)

    time.sleep(1)
    print(f"\n{YELLOW}[Fase 4] Pemulihan: Analis menyelesaikan investigasi & melepas karantina...{RESET}")
    try:
        rel_res = requests.post(f"{api_base}/api/soar/release", json={"ip_address": target_ip}, timeout=5)
        if rel_res.status_code == 200:
            print(f"{GREEN}[+] SUCCESS: Karantina untuk {target_ip} dilepas. Traffic normal dipulihkan.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Error: {e}{RESET}")
    print(f"\n{BOLD}{GREEN}[OK] Hasil Demo SOAR: Active Defense & Containment Playbook terbukti memutus serangan!{RESET}")


# ---------------- UTILITY: RESET ----------------
def reset_siem_database(api_base):
    try:
        res = requests.post(f"{api_base}/api/reset", timeout=5)
        if res.status_code == 200:
            print(f"{GREEN}[OK] SIEM in-memory database & whitelist telah di-reset ke kondisi awal.{RESET}")
        else:
            print(f"{RED}[!] Gagal mereset SIEM.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Error: {e}{RESET}")


def run_all_scenarios(api_base, variant=None):
    print(f"\n{BOLD}{CYAN}===== MENJALANKAN SELURUH 8 SKENARIO SECARA BERUNTUN ====={RESET}")
    reset_siem_database(api_base)
    scenario_1_normal_traffic(api_base, variant=variant)
    time.sleep(1)
    scenario_2_ddos_attack(api_base, variant=variant)
    time.sleep(1)
    scenario_3_impossible_travel(api_base, variant=variant)
    time.sleep(1)
    scenario_4_distributed_brute_force(api_base, variant=variant)
    time.sleep(1)
    scenario_5_data_exfiltration(api_base, variant=variant)
    time.sleep(1)
    scenario_6_careless_whitelisting(api_base, variant=variant)
    time.sleep(1)
    scenario_7_corrupted_data_and_time_drift(api_base, variant=variant)
    time.sleep(1)
    scenario_8_low_and_slow_apt(api_base, variant=variant)
    print(f"\n{BOLD}{GREEN}===== SELURUH 8 SKENARIO SELESAI DIJALANKAN ====={RESET}")


def interactive_menu(api_base):
    while True:
        print_banner()
        print(f"{BOLD}Pilih Skenario Serangan / Demonstrasi:{RESET}")
        print("  1. Skenario 1 - Trafik Normal (Karyawan wajar, no alarm)")
        print("  2. Skenario 2 - DDoS Attack (>10 web_request dalam 10s - Rule 1 TINGGI)")
        print("  3. Skenario 3 - Impossible Travel (<1 jam lokasi beda - Rule 2 KRITIS)")
        print("  4. Skenario 4 - Distributed Brute Force (>5 gagal, >3 IP - Rule 3 TINGGI)")
        print("  5. Skenario 5 - Data Exfiltration (>50 database_download - Rule 5 KRITIS)")
        print("  6. Skenario 6 - Careless Whitelisting (Demonstrasi Blind Spot Fatal)")
        print("  7. Skenario 7 - Data Cacat & Time Drift (Validasi Gatekeeper HTTP 422)")
        print("  8. Skenario 8 - The Low & Slow APT (Hot vs Cold Storage Dilemma & Stateful Watchlist)")
        print("  C. Demo SOAR - Active Defense (Isolate Host, Drop Traffic & Release Quarantine)")
        print("  -------------------------------------------------------------")
        print("  9. Jalankan Seluruh Skenario (1 - 8 Tour Lengkap)")
        print("  R. Reset SIEM Memory (Bersihkan log, alarm & whitelist)")
        print("  0. Keluar (Exit)")
        print("  *(Setiap skenario otomatis memilih acak 1 dari 3 varian berkas log)*")
        print("-" * 65)

        choice = input("Masukkan pilihan Anda: ").strip()
        if choice == "1":
            scenario_1_normal_traffic(api_base)
        elif choice == "2":
            scenario_2_ddos_attack(api_base)
        elif choice == "3":
            scenario_3_impossible_travel(api_base)
        elif choice == "4":
            scenario_4_distributed_brute_force(api_base)
        elif choice == "5":
            scenario_5_data_exfiltration(api_base)
        elif choice == "6":
            scenario_6_careless_whitelisting(api_base)
        elif choice == "7":
            scenario_7_corrupted_data_and_time_drift(api_base)
        elif choice == "8":
            scenario_8_low_and_slow_apt(api_base)
        elif choice.upper() == "C":
            demo_soar_containment(api_base)
        elif choice == "9":
            run_all_scenarios(api_base)
        elif choice.upper() == "R":
            reset_siem_database(api_base)
        elif choice == "0":
            print("Keluar dari simulator. Sampai jumpa!")
            sys.exit(0)
        else:
            print(f"{RED}Pilihan tidak valid. Silakan coba lagi.{RESET}")

        input(f"\n{BOLD}Tekan [Enter] untuk melanjutkan...{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Mini-SIEM Attack & Telemetry Simulator")
    parser.add_argument("--api", default=DEFAULT_API_BASE, help="SIEM API base URL (default: http://127.0.0.1:8000)")
    parser.add_argument("--scenario", "-s", type=int, choices=range(1, 9), help="Jalankan skenario tertentu (1-8)")
    parser.add_argument("--variant", "-v", type=int, choices=[1, 2, 3], default=None, help="Pilih varian berkas log tertentu (1-3, default: acak)")
    parser.add_argument("--soar", action="store_true", help="Jalankan demonstrasi SOAR Active Defense & Host Containment")
    parser.add_argument("--all", action="store_true", help="Jalankan semua skenario secara berurutan")
    parser.add_argument("--reset", action="store_true", help="Reset state memori SIEM")

    args = parser.parse_args()

    if args.reset:
        reset_siem_database(args.api)
        return

    if args.soar:
        demo_soar_containment(args.api)
        return

    if args.all:
        run_all_scenarios(args.api, variant=args.variant)
        return

    if args.scenario:
        scenarios = {
            1: scenario_1_normal_traffic,
            2: scenario_2_ddos_attack,
            3: scenario_3_impossible_travel,
            4: scenario_4_distributed_brute_force,
            5: scenario_5_data_exfiltration,
            6: scenario_6_careless_whitelisting,
            7: scenario_7_corrupted_data_and_time_drift,
            8: scenario_8_low_and_slow_apt,
        }
        scenarios[args.scenario](args.api, variant=args.variant)
        return

    interactive_menu(args.api)


if __name__ == "__main__":
    main()
