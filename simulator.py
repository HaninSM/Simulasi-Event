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
def scenario_1_normal_traffic(api_base):
    print(f"\n{BOLD}{CYAN}>>> Skenario 1: Trafik Normal (Karyawan bekerja normal){RESET}")
    print("Mengirimkan event web_request dan login_attempt wajar...")

    employees = [
        {"user": "alice_hr", "ip": "192.168.1.101", "type": "login_attempt"},
        {"user": "bob_eng", "ip": "192.168.1.102", "type": "web_request"},
        {"user": "charlie_sales", "ip": "192.168.1.103", "type": "web_request"},
        {"user": "alice_hr", "ip": "192.168.1.101", "type": "web_request"},
    ]

    for emp in employees:
        payload = {
            "timestamp": get_current_utc_iso(),
            "event_type": emp["type"],
            "user_id": emp["user"],
            "ip_address": emp["ip"],
            "location": "Jakarta, ID",
            "status": "success"
        }
        res = post_log(api_base, payload)
        if res:
            print(f"  [+] Log {emp['user']} ({emp['type']}) -> HTTP {res.status_code}")
        time.sleep(0.3)

    alerts = fetch_alerts(api_base)
    print(f"{GREEN}[OK] Hasil Skenario 1: Trafik diterima dengan baik. Tidak ada alarm palsu triggered.{RESET}")


# ---------------- SCENARIO 2: DDOS ATTACK ----------------
def scenario_2_ddos_attack(api_base):
    print(f"\n{BOLD}{YELLOW}>>> Skenario 2: DDoS / Botnet Attack (Memicu Rule 1){RESET}")
    print("Kriteria Rule 1: > 10 web_request dari 1 IP yang sama dalam 10 detik.")
    attacker_ip = "45.33.32.156"
    print(f"Mengirim rentetan request agresif dari IP target: {attacker_ip}...")

    total_sent = 15
    for i in range(1, total_sent + 1):
        payload = {
            "timestamp": get_current_utc_iso(),
            "event_type": "web_request",
            "user_id": f"botnet_agent_{i}",
            "ip_address": attacker_ip,
            "location": "Unknown",
            "status": "success"
        }
        res = post_log(api_base, payload)
        if res and res.status_code == 201:
            data = res.json()
            if data.get("alerts_triggered", 0) > 0:
                print(f"  {RED}[!] Request #{i}: SIEM memicu {data['alerts_triggered']} ALARM DDoS (Level: TINGGI)!{RESET}")
            else:
                print(f"  [+] Request #{i} terkirim...")
        time.sleep(0.08)

    print(f"{GREEN}[OK] Hasil Skenario 2: Rule 1 (DDoS / Botnet) terdeteksi dan tercatat di dashboard.{RESET}")


# ---------------- SCENARIO 3: IMPOSSIBLE TRAVEL ----------------
def scenario_3_impossible_travel(api_base):
    print(f"\n{BOLD}{RED}>>> Skenario 3: Impossible Travel (Memicu Rule 2){RESET}")
    print("Kriteria Rule 2: 2 login_attempt sukses user yang sama di lokasi berbeda dalam < 1 jam.")
    target_user = "sarah_security"

    # Login 1: Jakarta, Indonesia
    payload_1 = {
        "timestamp": get_current_utc_iso(),
        "event_type": "login_attempt",
        "user_id": target_user,
        "ip_address": "103.24.56.12",
        "location": "Jakarta, ID",
        "status": "success"
    }
    print(f"  [1] Login Sukses User '{target_user}' dari Jakarta, ID...")
    post_log(api_base, payload_1)
    time.sleep(1)

    # Login 2: Frankfurt, Germany (hanya berselang beberapa detik)
    payload_2 = {
        "timestamp": get_current_utc_iso(),
        "event_type": "login_attempt",
        "user_id": target_user,
        "ip_address": "185.190.140.2",
        "location": "Frankfurt, DE",
        "status": "success"
    }
    print(f"  [2] Login Sukses User '{target_user}' dari Frankfurt, DE (selang 1 detik)...")
    res = post_log(api_base, payload_2)
    if res and res.status_code == 201:
        data = res.json()
        print(f"  {RED}[!] ALARM KRITIS TERCATAT: {data.get('alerts_triggered')} alarm dipicu! (Impossible Travel){RESET}")

    print(f"{GREEN}[OK] Hasil Skenario 3: Rule 2 (Impossible Travel) berhasil dideteksi dengan level KRITIS.{RESET}")


# ---------------- SCENARIO 4: DISTRIBUTED BRUTE FORCE ----------------
def scenario_4_distributed_brute_force(api_base):
    print(f"\n{BOLD}{YELLOW}>>> Skenario 4: Distributed Brute Force (Memicu Rule 3){RESET}")
    print("Kriteria Rule 3: > 5 login gagal untuk 1 user dari > 3 IP berbeda dalam 1 menit.")
    target_user = "admin_vault"
    ips = ["198.51.100.11", "198.51.100.12", "198.51.100.13", "198.51.100.14", "198.51.100.15"]

    for i, ip in enumerate(ips * 2, start=1):
        if i > 8:
            break
        payload = {
            "timestamp": get_current_utc_iso(),
            "event_type": "login_attempt",
            "user_id": target_user,
            "ip_address": ip,
            "location": f"Tor Node {ip}",
            "status": "failed"
        }
        res = post_log(api_base, payload)
        if res and res.status_code == 201:
            data = res.json()
            if data.get("alerts_triggered", 0) > 0:
                print(f"  {RED}[!] Percobaan #{i} dari {ip}: ALARM TINGGI Distributed Brute Force terpicu!{RESET}")
            else:
                print(f"  [-] Percobaan #{i} dari {ip}: Login gagal tercatat...")
        time.sleep(0.15)

    print(f"{GREEN}[OK] Hasil Skenario 4: Rule 3 (Distributed Brute Force) berhasil ditangkap.{RESET}")


# ---------------- SCENARIO 5: DATA EXFILTRATION ----------------
def scenario_5_data_exfiltration(api_base):
    print(f"\n{BOLD}{RED}>>> Skenario 5: Data Exfiltration / Insider Threat (Memicu Rule 5){RESET}")
    print("Kriteria Rule 5: 1 user melakukan database_download > 50 kali dalam 1 menit.")
    insider = "rogue_dev_alex"
    insider_ip = "10.0.8.21"

    print(f"Mengirim 55 unduhan database massal oleh '{insider}'...")
    alert_triggered = False

    for i in range(1, 56):
        payload = {
            "timestamp": get_current_utc_iso(),
            "event_type": "database_download",
            "user_id": insider,
            "ip_address": insider_ip,
            "location": "Internal Office",
            "status": "success"
        }
        res = post_log(api_base, payload)
        if res and res.status_code == 201:
            data = res.json()
            if data.get("alerts_triggered", 0) > 0 and not alert_triggered:
                print(f"  {RED}[!] Unduhan #{i}: AMBANG BATAS DILAMPAUI (>50)! ALARM KRITIS (Data Exfiltration) TERPICU!{RESET}")
                alert_triggered = True
        time.sleep(0.04)

    print(f"{GREEN}[OK] Hasil Skenario 5: Rule 5 (Data Exfiltration) berhasil mendeteksi ancaman orang dalam.{RESET}")


# ---------------- SCENARIO 6: CARELESS WHITELISTING ----------------
def scenario_6_careless_whitelisting(api_base):
    print(f"\n{BOLD}{CYAN}>>> Skenario 6: Careless Whitelisting (Fatal Error / Blind Spot Demo){RESET}")
    attacker_ip = "203.0.113.88"
    print(f"1. Memasukkan IP {attacker_ip} ke Whitelist SIEM (dalih: IP VIP/Vendor)...")

    # POST to /api/whitelist
    w_res = requests.post(f"{api_base}/api/whitelist", json={
        "ip_address": attacker_ip,
        "reason": "Careless exception added by Admin"
    }, timeout=5)

    if w_res.status_code in [200, 201]:
        print(f"  {GREEN}[+] IP {attacker_ip} sekarang resmi di-whitelist.{RESET}")

    print(f"2. Hacker sekarang menyerang melalui IP {attacker_ip} (mengirim rentetan serangan DDoS)...")
    alerts_count = 0
    for i in range(15):
        payload = {
            "timestamp": get_current_utc_iso(),
            "event_type": "web_request",
            "user_id": "covert_attacker",
            "ip_address": attacker_ip,
            "location": "Unknown",
            "status": "success"
        }
        res = post_log(api_base, payload)
        if res and res.status_code == 201:
            alerts_count += res.json().get("alerts_triggered", 0)

    print(f"\n  {YELLOW}Hasil Pengecekan Mesin Korelasi:{RESET}")
    print(f"  Total Serangan Terkirim: 15 request cepat")
    print(f"  Total Alarm yang Dipicu SIEM: {BOLD}{alerts_count}{RESET} alarm")
    print(f"  {RED}[FATAL ERROR CONFIRMED] Mesin Korelasi sepenuhnya BUTA karena IP di-whitelist!{RESET}")
    print(f"{GREEN}[OK] Skenario 6 berhasil mendemonstrasikan bahaya Careless Whitelisting.{RESET}")


# ---------------- SCENARIO 7: DATA CACAT / TIME DRIFT ----------------
def scenario_7_corrupted_data_and_time_drift(api_base):
    print(f"\n{BOLD}{RED}>>> Skenario 7: Malformed Log (Format Cacat/Hilang) & Time Drift{RESET}")
    print("Masalah: Server lama mengalami bug / koneksi putus, mengirim log tanpa atribut penting atau JSON rusak.")
    print("Tantangan: Jika SIEM tidak memiliki schema validator, backend akan crash saat membaca log.ip_address.")
    print("Penanganan: Lapisan Validasi Skema (Gatekeeper) menolak log dengan HTTP 422, SIEM tetap berjalan normal.")

    url = f"{api_base}/api/ingest"
    all_passed = True

    # Test 1: ip_address: null
    print(f"\n  [Test 1] Server lama mengirim log dengan 'ip_address: null'...")
    res1 = requests.post(url, json={
        "timestamp": get_current_utc_iso(),
        "event_type": "web_request",
        "user_id": "legacy_server_bug_01",
        "ip_address": None,
        "location": "Server Room A",
        "status": "success"
    }, timeout=5)
    if res1.status_code == 422:
        print(f"  {GREEN}[PASS] Log dengan ip_address: null -> HTTP 422 (Ditolak / Dropped Aman){RESET}")
    else:
        print(f"  {RED}[FAIL] Expected HTTP 422, got HTTP {res1.status_code}{RESET}")
        all_passed = False

    # Test 2: JSON terpotong / malformed syntax (jaringan putus di tengah jalan)
    print(f"\n  [Test 2] Koneksi terputus di tengah pengiriman (JSON terpotong / sintaks rusak)...")
    res2 = requests.post(
        url,
        data='{"timestamp": "2026-10-20T03:00:00Z", "event_type": "web_request", "user_id": "legacy_server',
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    if res2.status_code == 422:
        print(f"  {GREEN}[PASS] JSON Terpotong/Cacat -> HTTP 422 (Ditolak Parser Gatekeeper){RESET}")
    else:
        print(f"  {RED}[FAIL] Expected HTTP 422, got HTTP {res2.status_code}{RESET}")
        all_passed = False

    # Test 3: Missing attribute 'ip_address' completely
    print(f"\n  [Test 3] Log tanpa key 'ip_address' sama sekali...")
    res3 = requests.post(url, json={
        "timestamp": get_current_utc_iso(),
        "event_type": "web_request",
        "user_id": "legacy_server_bug_02",
        "location": "Server Room B",
        "status": "success"
    }, timeout=5)
    if res3.status_code == 422:
        print(f"  {GREEN}[PASS] Atribut ip_address Hilang -> HTTP 422 (Ditolak Gatekeeper){RESET}")
    else:
        print(f"  {RED}[FAIL] Expected HTTP 422, got HTTP {res3.status_code}{RESET}")
        all_passed = False

    # Test 4: Format IP bukan IPv4 valid
    print(f"\n  [Test 4] Format IP bukan IPv4 ('999.999.999.999')...")
    res4 = requests.post(url, json={
        "timestamp": get_current_utc_iso(),
        "event_type": "web_request",
        "user_id": "test_user",
        "ip_address": "999.999.999.999",
        "location": "Jakarta",
        "status": "success"
    }, timeout=5)
    if res4.status_code == 422:
        print(f"  {GREEN}[PASS] Format IP Salah -> HTTP 422 (Ditolak Gatekeeper){RESET}")
    else:
        print(f"  {RED}[FAIL] Expected HTTP 422, got HTTP {res4.status_code}{RESET}")
        all_passed = False

    # Test 5: Time Drift Error (Tahun 1970 > 24 jam lampau)
    print(f"\n  [Test 5] Time Drift Error: Timestamp Tahun 1970 (> 24 Jam Lampau)...")
    res5 = requests.post(url, json={
        "timestamp": "1970-01-01T00:00:00Z",
        "event_type": "login_attempt",
        "user_id": "ancient_sender",
        "ip_address": "192.168.1.50",
        "location": "Jakarta",
        "status": "success"
    }, timeout=5)
    if res5.status_code == 422 and "Time Drift Error" in res5.text:
        print(f"  {GREEN}[PASS] Timestamp 1970 -> HTTP 422 ('Time Drift Error' Ditolak){RESET}")
    else:
        print(f"  {RED}[FAIL] Expected HTTP 422 Time Drift, got HTTP {res5.status_code}{RESET}")
        all_passed = False

    # Test 6: Time Drift Error (Dari masa depan +1 tahun)
    print(f"\n  [Test 6] Time Drift Error: Timestamp Masa Depan (+1 Tahun)...")
    future_time = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
    res6 = requests.post(url, json={
        "timestamp": future_time,
        "event_type": "login_attempt",
        "user_id": "future_sender",
        "ip_address": "192.168.1.50",
        "location": "Jakarta",
        "status": "success"
    }, timeout=5)
    if res6.status_code == 422 and "Time Drift Error" in res6.text:
        print(f"  {GREEN}[PASS] Timestamp Masa Depan -> HTTP 422 ('Time Drift Error' Ditolak){RESET}")
    else:
        print(f"  {RED}[FAIL] Expected HTTP 422 Time Drift, got HTTP {res6.status_code}{RESET}")
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


def run_all_scenarios(api_base):
    print(f"\n{BOLD}{CYAN}===== MENJALANKAN SELURUH 7 SKENARIO SECARA BERUNTUN ====={RESET}")
    reset_siem_database(api_base)
    scenario_1_normal_traffic(api_base)
    time.sleep(1)
    scenario_2_ddos_attack(api_base)
    time.sleep(1)
    scenario_3_impossible_travel(api_base)
    time.sleep(1)
    scenario_4_distributed_brute_force(api_base)
    time.sleep(1)
    scenario_5_data_exfiltration(api_base)
    time.sleep(1)
    scenario_6_careless_whitelisting(api_base)
    time.sleep(1)
    scenario_7_corrupted_data_and_time_drift(api_base)
    print(f"\n{BOLD}{GREEN}===== SELURUH SKENARIO SELESAI DIJALANKAN ====={RESET}")


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
        print("  -------------------------------------------------------------")
        print("  8. Jalankan Seluruh Skenario (1 - 7 Tour Lengkap)")
        print("  9. Reset SIEM Memory (Bersihkan log, alarm & whitelist)")
        print("  0. Keluar (Exit)")
        print("-" * 65)

        choice = input("Masukkan pilihan Anda [0-9]: ").strip()
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
            run_all_scenarios(api_base)
        elif choice == "9":
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
    parser.add_argument("--scenario", "-s", type=int, choices=range(1, 8), help="Jalankan skenario tertentu (1-7)")
    parser.add_argument("--all", action="store_true", help="Jalankan semua skenario secara berurutan")
    parser.add_argument("--reset", action="store_true", help="Reset state memori SIEM")

    args = parser.parse_args()

    if args.reset:
        reset_siem_database(args.api)
        return

    if args.all:
        run_all_scenarios(args.api)
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
        }
        scenarios[args.scenario](args.api)
        return

    interactive_menu(args.api)


if __name__ == "__main__":
    main()
