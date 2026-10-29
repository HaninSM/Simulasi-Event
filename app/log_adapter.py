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
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

SAMPLE_LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_logs")


def get_current_utc_iso(delta_seconds: float = 0) -> str:
    dt = datetime.now(timezone.utc) + timedelta(seconds=delta_seconds)
    return dt.isoformat()


class ScenarioEventList(list):
    """
    Subclass of list holding parsed events, enriched with scenario variant metadata.
    Completely transparent to list operations (len, iteration, indexing).
    """
    def __init__(self, *args, scenario_id: int = 1, variant: int = 1, filename: str = "", description: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self.scenario_id = scenario_id
        self.variant = variant
        self.filename = filename
        self.description = description
        self.source_file = f"sample_logs/{filename}" if filename else ""


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

    VARIANT_CATALOG = {
        1: {
            1: ("web_access_normal_1.log", "E-Commerce Browsing (Alice, Bob, Charlie)"),
            2: ("web_access_normal_2.log", "HR Payroll Portal (Diana, Evan, Frank)"),
            3: ("web_access_normal_3.log", "Customer Support Desk (Grace, Henry, Ivy)")
        },
        2: {
            1: ("nginx_ddos_flood_1.log", "GET /api/v1/search flood from 45.33.32.156"),
            2: ("nginx_ddos_flood_2.log", "POST /auth/login flood from 194.26.29.112"),
            3: ("nginx_ddos_flood_3.log", "GET /checkout/pay flood from 185.220.101.45")
        },
        3: {
            1: ("vpn_and_gate_access_1.csv", "sarah_security: Jakarta ID (103.24.56.12) vs Frankfurt DE (185.190.140.2)"),
            2: ("vpn_and_gate_access_2.csv", "budi_finance: Surabaya ID (182.253.110.15) vs Dallas US (198.51.100.99)"),
            3: ("vpn_and_gate_access_3.csv", "ahmad_devops: Singapore SG (128.199.200.5) vs Moscow RU (95.173.136.80)")
        },
        4: {
            1: ("auth_sshd_bruteforce_1.log", "admin_corp targeted via 4 Tor Exit Nodes"),
            2: ("auth_sshd_bruteforce_2.log", "root targeted via 5 Botnet Proxy IPs"),
            3: ("auth_sshd_bruteforce_3.log", "svc_deploy targeted via 4 Cloud VPS IPs")
        },
        5: {
            1: ("postgres_audit_exfiltration_1.jsonl", "dev_rogue dumping credit_cards table from 10.0.8.21"),
            2: ("postgres_audit_exfiltration_2.jsonl", "contractor_analyst querying customer_pii table from 10.0.9.45"),
            3: ("postgres_audit_exfiltration_3.jsonl", "intern_badactor dumping payroll_salaries table from 10.0.8.88")
        },
        6: {
            1: ("careless_whitelist_attack_1.log", "Whitelisted Partner API (203.0.113.88)"),
            2: ("careless_whitelist_attack_2.log", "Whitelisted Exec Laptop (198.51.100.50)"),
            3: ("careless_whitelist_attack_3.log", "Whitelisted Legacy Monitor (192.0.2.77)")
        },
        7: {
            1: ("legacy_corrupted_device_1.log", "Industrial IoT Gateway (null IP, 1970 reset)"),
            2: ("legacy_corrupted_device_2.log", "Branch Router (truncated JSON, future drift)"),
            3: ("legacy_corrupted_device_3.log", "SCADA PLC Controller (invalid IP string, 48h drift)")
        },
        8: {
            1: ("apt_recon_and_exploit_1.log", "198.51.100.77: Dirbuster /.env vs Log4j RCE"),
            2: ("apt_recon_and_exploit_2.log", "203.0.113.144: Actuator Scan vs Spring4Shell RCE"),
            3: ("apt_recon_and_exploit_3.log", "192.0.2.199: SQLi Recon vs Webshell Upload")
        }
    }

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
    def load_scenario_from_file(cls, scenario_id: int, variant: Optional[int] = None) -> ScenarioEventList:
        """
        Reads actual sample log file from disk and parses it into Mini-SIEM payloads
        with dynamic relative timestamp shifting to match real-time sliding windows.
        If variant is None, randomly selects one of the 3 variant files for that scenario.
        """
        if variant is None or variant not in [1, 2, 3]:
            variant = random.choice([1, 2, 3])

        cat = cls.VARIANT_CATALOG.get(scenario_id, {}).get(variant, (None, ""))
        filename, desc = cat if cat else (None, "")

        file_path = os.path.join(SAMPLE_LOGS_DIR, filename) if filename else ""
        if not os.path.exists(file_path):
            legacy_names = {
                1: "web_access_normal.log",
                2: "nginx_ddos_flood.log",
                3: "vpn_and_gate_access.csv",
                4: "auth_sshd_bruteforce.log",
                5: "postgres_audit_exfiltration.jsonl",
                6: "careless_whitelist_attack.log",
                7: "legacy_corrupted_device.log",
                8: "apt_recon_and_exploit.log"
            }
            filename = legacy_names.get(scenario_id, "")
            file_path = os.path.join(SAMPLE_LOGS_DIR, filename)

        events = []

        if scenario_id == 1:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if l.strip()]
                for idx, line in enumerate(lines):
                    parsed = cls.parse_nginx_line(line)
                    if parsed:
                        parsed["timestamp"] = get_current_utc_iso(delta_seconds=idx * 0.3)
                        events.append(parsed)

        elif scenario_id == 2:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if l.strip()]
                for idx, line in enumerate(lines):
                    parsed = cls.parse_nginx_line(line, default_event_type="web_request")
                    if parsed:
                        parsed["timestamp"] = get_current_utc_iso(delta_seconds=idx * 0.1)
                        events.append(parsed)

        elif scenario_id == 3:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for idx, row in enumerate(reader):
                        parsed = cls.parse_csv_line(row)
                        parsed["timestamp"] = get_current_utc_iso(delta_seconds=idx * 1.0)
                        events.append(parsed)

        elif scenario_id == 4:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if l.strip()]
                for idx, line in enumerate(lines):
                    parsed = cls.parse_auth_sshd_line(line)
                    if parsed:
                        parsed["timestamp"] = get_current_utc_iso(delta_seconds=idx * 0.2)
                        events.append(parsed)

        elif scenario_id == 5:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    for idx, line in enumerate(f):
                        line = line.strip()
                        if line:
                            data = json.loads(line)
                            event = {
                                "timestamp": get_current_utc_iso(delta_seconds=idx * 0.05),
                                "event_type": data.get("event_type", "database_download"),
                                "user_id": data.get("user_id") or data.get("user"),
                                "ip_address": data.get("ip_address") or data.get("client_ip"),
                                "location": data.get("location", "Internal LAN"),
                                "status": data.get("status", "success")
                            }
                            events.append(event)

        elif scenario_id == 6:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if l.strip()]
                for idx, line in enumerate(lines):
                    parsed = cls.parse_nginx_line(line, default_event_type="web_request")
                    if parsed:
                        parsed["timestamp"] = get_current_utc_iso(delta_seconds=idx * 0.1)
                        events.append(parsed)

        elif scenario_id == 7:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            test_item = json.loads(line)
                            events.append(test_item)

        elif scenario_id == 8:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if l.strip() and not l.startswith("#")]
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

        return ScenarioEventList(
            events,
            scenario_id=scenario_id,
            variant=variant,
            filename=filename or "",
            description=desc or ""
        )

