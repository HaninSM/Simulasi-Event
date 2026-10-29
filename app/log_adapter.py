"""
Mini-SIEM Universal Log Adapter & Parser
Reads heterogeneous raw log formats from sample_logs/ and converts them
into the unified Mini-SIEM JSON Data Contract with dynamic timestamp shifting.
"""

import os
import re
import csv
import io
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

SAMPLE_LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_logs")


def get_current_utc_iso(delta_seconds: float = 0) -> str:
    dt = datetime.now(timezone.utc) + timedelta(seconds=delta_seconds)
    return dt.isoformat()


class LogAdapter:
    """
    Parses heterogeneous external application logs into Mini-SIEM LogEvent schema:
    {
        "timestamp": ISO8601 string,
        "event_type": "login_attempt" | "web_request" | "database_download" | "recon_probe",
        "user_id": str,
        "ip_address": str,
        "location": str,
        "status": "success" | "failed"
    }
    """

    # Nginx / Apache Combined Log Regex:
    # 192.168.1.101 - alice_hr [29/Oct/2026:08:15:20 +0000] "POST /api/v1/auth/login HTTP/1.1" 200 482 "..." "..."
    NGINX_REGEX = re.compile(
        r'^(?P<ip>\S+)\s+\S+\s+(?P<user>\S+)\s+\[(?P<time>[^\]]+)\]\s+"(?P<method>[A-Z]+)\s+(?P<path>\S+)[^"]*"\s+(?P<status>\d{3})\s+(?P<bytes>\d+)(?:\s+"(?P<referer>[^"]*)"\s+"(?P<ua>[^"]*)")?(?:\s+(?P<extra>.*))?$'
    )

    # Linux auth.log Syslog Regex:
    # Oct 29 10:14:01 srv-core sshd[4102]: Failed password for invalid user admin_vault from 198.51.100.11 port 41232 ssh2
    AUTH_LOG_REGEX = re.compile(
        r'Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>\S+) port \d+ ssh2'
    )

    @classmethod
    def parse_nginx_line(cls, line: str, default_event_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        match = cls.NGINX_REGEX.match(line)
        if not match:
            # Fallback simple whitespace split for custom logs
            parts = line.split()
            if len(parts) >= 6:
                return {
                    "ip_address": parts[0],
                    "user_id": parts[2] if parts[2] != "-" else "anonymous",
                    "event_type": default_event_type or "web_request",
                    "location": "DMZ Edge",
                    "status": "success"
                }
            return None

        data = match.groupdict()
        user = data["user"] if data["user"] != "-" else "anonymous"
        status_code = int(data["status"])
        status_str = "success" if status_code < 400 else "failed"

        path = data.get("path", "")
        extra = (data.get("extra") or "").strip()

        # Determine event_type
        if default_event_type:
            event_type = default_event_type
        elif "recon_probe" in extra or "probe" in path:
            event_type = "recon_probe"
        elif "login" in path or "auth" in path:
            event_type = "login_attempt"
        else:
            event_type = "web_request"

        location = "DMZ Edge"
        if "DMZ" in extra:
            location = "DMZ Edge Gateway"
        elif "corp" in (data.get("referer") or ""):
            location = "Internal Office"

        return {
            "ip_address": data["ip"],
            "user_id": user,
            "event_type": event_type,
            "location": location,
            "status": status_str,
            "raw_line": line
        }

    @classmethod
    def parse_auth_sshd_line(cls, line: str) -> Optional[Dict[str, Any]]:
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        match = cls.AUTH_LOG_REGEX.search(line)
        if not match:
            return None

        data = match.groupdict()
        return {
            "ip_address": data["ip"],
            "user_id": data["user"],
            "event_type": "login_attempt",
            "location": f"Tor Node {data['ip']}",
            "status": "failed",
            "raw_line": line
        }

    @classmethod
    def parse_csv_line(cls, row: Dict[str, str]) -> Dict[str, Any]:
        return {
            "timestamp": row.get("timestamp"),
            "user_id": row.get("user_id"),
            "ip_address": row.get("ip_address"),
            "location": row.get("location"),
            "event_type": row.get("event_type", "login_attempt"),
            "status": row.get("status", "success")
        }

    @classmethod
    def load_scenario_from_file(cls, scenario_id: int) -> List[Dict[str, Any]]:
        """
        Reads actual sample log file from disk and parses it into Mini-SIEM payloads
        with dynamic relative timestamp shifting to match real-time sliding windows.
        """
        events = []

        if scenario_id == 1:
            # Skenario 1: Trafik Normal (web_access_normal.log)
            file_path = os.path.join(SAMPLE_LOGS_DIR, "web_access_normal.log")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if l.strip()]
                for idx, line in enumerate(lines):
                    parsed = cls.parse_nginx_line(line)
                    if parsed:
                        parsed["timestamp"] = get_current_utc_iso(delta_seconds=idx * 0.3)
                        events.append(parsed)

        elif scenario_id == 2:
            # Skenario 2: DDoS Attack (nginx_ddos_flood.log)
            file_path = os.path.join(SAMPLE_LOGS_DIR, "nginx_ddos_flood.log")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if l.strip()]
                for idx, line in enumerate(lines):
                    parsed = cls.parse_nginx_line(line, default_event_type="web_request")
                    if parsed:
                        # Pack 15 requests into a 3-second window
                        parsed["timestamp"] = get_current_utc_iso(delta_seconds=idx * 0.1)
                        events.append(parsed)

        elif scenario_id == 3:
            # Skenario 3: Impossible Travel (vpn_and_gate_access.csv)
            file_path = os.path.join(SAMPLE_LOGS_DIR, "vpn_and_gate_access.csv")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for idx, row in enumerate(reader):
                        parsed = cls.parse_csv_line(row)
                        # Event 1 at T=0, Event 2 at T+1 second
                        parsed["timestamp"] = get_current_utc_iso(delta_seconds=idx * 1.0)
                        events.append(parsed)

        elif scenario_id == 4:
            # Skenario 4: Distributed Brute Force (auth_sshd_bruteforce.log)
            file_path = os.path.join(SAMPLE_LOGS_DIR, "auth_sshd_bruteforce.log")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if l.strip()]
                for idx, line in enumerate(lines):
                    parsed = cls.parse_auth_sshd_line(line)
                    if parsed:
                        parsed["timestamp"] = get_current_utc_iso(delta_seconds=idx * 0.2)
                        events.append(parsed)

        elif scenario_id == 5:
            # Skenario 5: Data Exfiltration (postgres_audit_exfiltration.jsonl)
            file_path = os.path.join(SAMPLE_LOGS_DIR, "postgres_audit_exfiltration.jsonl")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    for idx, line in enumerate(f):
                        line = line.strip()
                        if line:
                            data = json.loads(line)
                            event = {
                                "timestamp": get_current_utc_iso(delta_seconds=idx * 0.05),
                                "event_type": data.get("event_type", "database_download"),
                                "user_id": data.get("user_id"),
                                "ip_address": data.get("ip_address"),
                                "location": data.get("location", "Internal LAN"),
                                "status": data.get("status", "success")
                            }
                            events.append(event)

        elif scenario_id == 6:
            # Skenario 6: Careless Whitelisting (careless_whitelist_attack.log)
            file_path = os.path.join(SAMPLE_LOGS_DIR, "careless_whitelist_attack.log")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if l.strip()]
                for idx, line in enumerate(lines):
                    parsed = cls.parse_nginx_line(line, default_event_type="web_request")
                    if parsed:
                        parsed["timestamp"] = get_current_utc_iso(delta_seconds=idx * 0.1)
                        events.append(parsed)

        elif scenario_id == 7:
            # Skenario 7: Corrupted Data & Time Drift (legacy_corrupted_device.log)
            file_path = os.path.join(SAMPLE_LOGS_DIR, "legacy_corrupted_device.log")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            test_item = json.loads(line)
                            events.append(test_item)

        elif scenario_id == 8:
            # Skenario 8: Low & Slow APT (apt_recon_and_exploit.log)
            file_path = os.path.join(SAMPLE_LOGS_DIR, "apt_recon_and_exploit.log")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if l.strip() and not l.startswith("#")]
                # Line 0: Recon probe (Day 1)
                # Line 1: Exploit request (Day 20)
                if len(lines) >= 2:
                    p1 = cls.parse_nginx_line(lines[0], default_event_type="recon_probe")
                    if p1:
                        p1["timestamp"] = get_current_utc_iso(0)
                        p1["stage"] = "day_1_recon"
                        events.append(p1)

                    p2 = cls.parse_nginx_line(lines[1], default_event_type="web_request")
                    if p2:
                        p2["timestamp"] = get_current_utc_iso(1)
                        p2["stage"] = "day_20_exploit"
                        events.append(p2)

        return events
