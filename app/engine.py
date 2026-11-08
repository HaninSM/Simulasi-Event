import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Set, Optional
from collections import defaultdict

from app.models import (
    LogEvent, Alert, WhitelistRequest, WatchlistRequest,
    IsolateHostRequest, ReleaseHostRequest,
    SuspendUserRequest, UnsuspendUserRequest,
    DetectionRule, MitreAttack, ThreatIntelData
)
from app.rule_loader import RuleLoader
from app.cti_engine import ThreatIntelEngine


class CorrelationEngine:
    def __init__(self, rules_dir: Optional[str] = None):
        # Detection as Code (Sigma-like YAML rules)
        self.rules_dir = rules_dir
        self.rules: Dict[str, DetectionRule] = {}
        self.load_rules(self.rules_dir)

        # Threat Intelligence & Observable Analyzer Engine (Cortex-style)
        self.cti = ThreatIntelEngine()

        # Whitelisted IP addresses: ip_address -> dict(reason, added_at)
        self.whitelist: Dict[str, dict] = {}
        
        # Stateful Watchlist (Greylist) for Long-Term APT Tracking:
        # ip_address -> dict(risk_level, reason, added_at, probe_count)
        self.watchlist: Dict[str, dict] = {}

        # SOAR State: Active Network Quarantine / Isolated Hosts & Suspended Users
        # ip_address -> dict(ip_address, reason, analyst, isolated_at)
        self.isolated_hosts: Dict[str, dict] = {}
        # user_id -> dict(user_id, reason, analyst, suspended_at)
        self.suspended_users: Dict[str, dict] = {}
        self.soar_audit_trail: List[dict] = []
        self.blocked_containment_count: int = 0

        # In-memory Hot Storage for logs and alerts (Instant Correlation)
        self.raw_logs: List[LogEvent] = []
        self.alerts: List[Alert] = []

        # Cold Storage Archive: Simulates logs moved to frozen storage (> 14 days)
        # Not queried by normal real-time engine unless rehydrated
        self.cold_archive: List[LogEvent] = []

        # Sliding window event buffers for fast correlation:
        # 1. web_requests: ip -> list of (timestamp_utc, LogEvent)
        self.web_requests_by_ip = defaultdict(list)
        # 2. successful_logins: user_id -> list of (timestamp_utc, LogEvent)
        self.successful_logins_by_user = defaultdict(list)
        # 3. failed_logins: user_id -> list of (timestamp_utc, LogEvent)
        self.failed_logins_by_user = defaultdict(list)
        # 4. db_downloads: user_id -> list of (timestamp_utc, LogEvent)
        self.db_downloads_by_user = defaultdict(list)

        # Alert cooldown to prevent flooding identical alerts in rapid succession:
        # key (rule_name, target_id) -> last_alert_time
        self.alert_cooldowns: Dict[str, datetime] = {}

    # --- Detection as Code (Rules Management) ---

    def load_rules(self, rules_dir: Optional[str] = None) -> int:
        """Loads or reloads detection rules from YAML files."""
        if rules_dir:
            self.rules_dir = rules_dir
        self.rules = RuleLoader.load_from_directory(self.rules_dir)
        return len(self.rules)

    def get_rules(self) -> List[dict]:
        """Returns all registered detection rules with full metadata."""
        return [rule.model_dump() for rule in self.rules.values()]

    def get_rule(self, rule_id: str) -> Optional[DetectionRule]:
        return self.rules.get(rule_id)

    def toggle_rule(self, rule_id: str, enabled: bool) -> Optional[dict]:
        """Enables or disables a detection rule dynamically."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = enabled
            return self.rules[rule_id].model_dump()
        return None

    def add_to_whitelist(self, req: WhitelistRequest) -> dict:
        self.whitelist[req.ip_address] = {
            "ip_address": req.ip_address,
            "reason": req.reason or "Manual entry by Captain SIEM",
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        return self.whitelist[req.ip_address]

    def remove_from_whitelist(self, ip_address: str) -> bool:
        if ip_address in self.whitelist:
            del self.whitelist[ip_address]
            return True
        return False

    def get_whitelist(self) -> List[dict]:
        return list(self.whitelist.values())

    def is_whitelisted(self, ip_address: str) -> bool:
        return ip_address in self.whitelist

    # --- Persistent Watchlist & Cold Archive Methods (APT Mitigations) ---

    def add_to_watchlist(self, req: WatchlistRequest) -> dict:
        self.watchlist[req.ip_address] = {
            "ip_address": req.ip_address,
            "risk_level": req.risk_level or "HIGH",
            "reason": req.reason or "Reconnaissance probe detected",
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        return self.watchlist[req.ip_address]

    def remove_from_watchlist(self, ip_address: str) -> bool:
        if ip_address in self.watchlist:
            del self.watchlist[ip_address]
            return True
        return False

    def get_watchlist(self) -> List[dict]:
        return list(self.watchlist.values())

    def is_watchlisted(self, ip_address: str) -> bool:
        return ip_address in self.watchlist

    # --- SOAR (Active Defense & Host Containment) Methods ---

    def isolate_host(
        self,
        ip_address: str,
        reason: str = "Contained by SOC Analyst via Active Defense Playbook",
        analyst: str = "SOC Analyst Tier-1"
    ) -> dict:
        """
        Quarantines a compromised or hostile host.
        Subsequent network requests from this host will be blocked at the Gatekeeper (HTTP 403).
        Transitions matching active alerts to 'CONTAINED' status.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        entry = {
            "ip_address": ip_address,
            "reason": reason,
            "analyst": analyst,
            "isolated_at": now_iso
        }
        self.isolated_hosts[ip_address] = entry

        # Transition active alerts for this IP to CONTAINED
        for a in self.alerts:
            if a.ip_address == ip_address and a.status == "NEW":
                a.status = "CONTAINED"

        # Invalidate/purge isolated host from active sliding correlation buffers
        self.web_requests_by_ip.pop(ip_address, None)
        for u in list(self.successful_logins_by_user.keys()):
            self.successful_logins_by_user[u] = [
                e for e in self.successful_logins_by_user[u] if e[1].ip_address != ip_address
            ]
        for u in list(self.failed_logins_by_user.keys()):
            self.failed_logins_by_user[u] = [
                e for e in self.failed_logins_by_user[u] if e[1].ip_address != ip_address
            ]

        # Record in SOAR audit trail
        audit_entry = {
            "id": str(uuid.uuid4())[:8],
            "action": "ISOLATE",
            "ip_address": ip_address,
            "reason": reason,
            "analyst": analyst,
            "timestamp": now_iso
        }
        self.soar_audit_trail.append(audit_entry)
        if len(self.soar_audit_trail) > 200:
            self.soar_audit_trail.pop(0)

        return entry

    def release_host(self, ip_address: str, analyst: str = "SOC Analyst Tier-1") -> bool:
        """
        Lifts network quarantine on a host, allowing traffic to resume.
        """
        if ip_address in self.isolated_hosts:
            del self.isolated_hosts[ip_address]
            now_iso = datetime.now(timezone.utc).isoformat()
            audit_entry = {
                "id": str(uuid.uuid4())[:8],
                "action": "RELEASE",
                "ip_address": ip_address,
                "reason": "Host quarantine released / restored to network",
                "analyst": analyst,
                "timestamp": now_iso
            }
            self.soar_audit_trail.append(audit_entry)
            if len(self.soar_audit_trail) > 200:
                self.soar_audit_trail.pop(0)
            return True
        return False

    def is_host_isolated(self, ip_address: str) -> bool:
        return ip_address in self.isolated_hosts

    def get_isolated_hosts(self) -> List[dict]:
        return list(self.isolated_hosts.values())

    # --- SOAR User Account Suspension Methods (Identity Defense) ---

    def suspend_user(
        self,
        user_id: str,
        reason: str = "Account suspended by SOC Playbook due to identity compromise / impossible travel",
        analyst: str = "SOC Analyst Tier-1"
    ) -> dict:
        now_iso = datetime.now(timezone.utc).isoformat()
        entry = {
            "user_id": user_id,
            "reason": reason,
            "analyst": analyst,
            "suspended_at": now_iso
        }
        self.suspended_users[user_id] = entry

        # Transition active alerts for this user to CONTAINED
        for a in self.alerts:
            if a.user_id == user_id and a.status == "NEW":
                a.status = "CONTAINED"

        # Invalidate/purge suspended user from active correlation buffers
        self.successful_logins_by_user.pop(user_id, None)
        self.failed_logins_by_user.pop(user_id, None)
        self.db_downloads_by_user.pop(user_id, None)

        # Record in SOAR audit trail
        audit_entry = {
            "id": str(uuid.uuid4())[:8],
            "action": "SUSPEND_USER",
            "target": user_id,
            "reason": reason,
            "analyst": analyst,
            "timestamp": now_iso
        }
        self.soar_audit_trail.append(audit_entry)
        if len(self.soar_audit_trail) > 200:
            self.soar_audit_trail.pop(0)

        return entry

    def unsuspend_user(self, user_id: str, analyst: str = "SOC Analyst Tier-1") -> bool:
        if user_id in self.suspended_users:
            del self.suspended_users[user_id]
            now_iso = datetime.now(timezone.utc).isoformat()
            audit_entry = {
                "id": str(uuid.uuid4())[:8],
                "action": "UNSUSPEND_USER",
                "target": user_id,
                "reason": "Account suspension lifted / restored",
                "analyst": analyst,
                "timestamp": now_iso
            }
            self.soar_audit_trail.append(audit_entry)
            if len(self.soar_audit_trail) > 200:
                self.soar_audit_trail.pop(0)
            return True
        return False

    def is_user_suspended(self, user_id: str) -> bool:
        return user_id in self.suspended_users

    def get_suspended_users(self) -> List[dict]:
        return list(self.suspended_users.values())

    def get_soar_audit_trail(self) -> List[dict]:
        return list(reversed(self.soar_audit_trail))

    def record_blocked_containment(self, ip_address: str):
        self.blocked_containment_count += 1

    def archive_to_cold(self, ip_address: Optional[str] = None) -> int:
        """
        Simulates log lifecycle: moves events from hot storage into frozen cold archive.
        If ip_address is specified, archives only that IP's events. Otherwise archives all.
        """
        if ip_address:
            to_archive = [log for log in self.raw_logs if log.ip_address == ip_address]
            self.raw_logs = [log for log in self.raw_logs if log.ip_address != ip_address]
        else:
            to_archive = list(self.raw_logs)
            self.raw_logs.clear()

        self.cold_archive.extend(to_archive)
        archived_count = len(to_archive)

        # Clear fast-correlation buffers for the archived data
        if ip_address:
            self.web_requests_by_ip.pop(ip_address, None)
            # Find and clear user buffers associated with this IP
            for user_id, events in list(self.successful_logins_by_user.items()):
                self.successful_logins_by_user[user_id] = [e for e in events if e[1].ip_address != ip_address]
            for user_id, events in list(self.failed_logins_by_user.items()):
                self.failed_logins_by_user[user_id] = [e for e in events if e[1].ip_address != ip_address]
        else:
            self.web_requests_by_ip.clear()
            self.successful_logins_by_user.clear()
            self.failed_logins_by_user.clear()
            self.db_downloads_by_user.clear()

        return archived_count

    def rehydrate_cold(self, ip_address: str) -> List[LogEvent]:
        """
        Simulates Cold Log Rehydration: pulls archived logs back into active correlation view
        for deep forensic investigation when an APT trigger matches.
        """
        matching = [log for log in self.cold_archive if log.ip_address == ip_address]
        # Re-inject back into raw_logs
        for log in matching:
            self.raw_logs.append(log)
        return matching

    def get_cold_archive(self) -> List[LogEvent]:
        return list(self.cold_archive)

    def clear_all(self):
        self.raw_logs.clear()
        self.alerts.clear()
        self.cold_archive.clear()
        self.watchlist.clear()
        self.isolated_hosts.clear()
        self.suspended_users.clear()
        self.soar_audit_trail.clear()
        self.blocked_containment_count = 0
        self.web_requests_by_ip.clear()
        self.successful_logins_by_user.clear()
        self.failed_logins_by_user.clear()
        self.db_downloads_by_user.clear()
        self.alert_cooldowns.clear()

    def process_log(self, event: LogEvent) -> List[Alert]:
        # SOAR Containment Enforcement:
        # If host is isolated or user account is suspended, DROP traffic immediately.
        # Do not store in raw logs, do not feed to correlation rules, and do not trigger alerts!
        if self.is_host_isolated(event.ip_address) or self.is_user_suspended(event.user_id):
            self.record_blocked_containment(event.ip_address)
            return []

        # Always store the raw log in ingestion history
        self.raw_logs.append(event)
        
        # Keep maximum 5000 logs in memory for simulation
        if len(self.raw_logs) > 5000:
            self.raw_logs.pop(0)

        # Feature B - Careless Whitelisting check:
        # If IP is whitelisted, the Correlation Engine ignores the log completely (Blind Spot)!
        if self.is_whitelisted(event.ip_address):
            return []

        ts_utc = event.timestamp if event.timestamp.tzinfo else event.timestamp.replace(tzinfo=timezone.utc)
        ts_utc = ts_utc.astimezone(timezone.utc)

        triggered_alerts: List[Alert] = []

        # --- Rule 0 (Stateful APT): Persistent Watchlist Correlation (Level: KRITIS) ---
        # Rule ID: RULE-APT-000
        rule_apt = self.rules.get("RULE-APT-000")
        if (rule_apt is None or rule_apt.enabled) and self.is_watchlisted(event.ip_address):
            watch_info = self.watchlist[event.ip_address]
            alert = self._create_alert(
                rule_name=rule_apt.title if rule_apt else "APT Low & Slow / Persistent Threat",
                severity=rule_apt.severity if rule_apt else "KRITIS",
                description=(
                    f"APT Low & Slow Alert! IP {event.ip_address} previously flagged on Watchlist "
                    f"('{watch_info['reason']}') initiated subsequent event '{event.event_type}'. "
                    f"Cross-retention correlation succeeded via Stateful Watchlist!"
                ),
                ip_address=event.ip_address,
                user_id=event.user_id,
                details={
                    "watchlist_reason": watch_info["reason"],
                    "watchlist_risk": watch_info["risk_level"],
                    "flagged_at": watch_info["added_at"],
                    "current_event": event.event_type,
                    "target_user": event.user_id,
                    "mitigation": "Stateful Greylist & Cold Log Rehydration"
                },
                cooldown_key=f"apt_watch_{event.ip_address}_{event.event_type}",
                cooldown_seconds=rule_apt.cooldown_seconds if rule_apt else 5,
                ref_time=ts_utc,
                rule_id=rule_apt.id if rule_apt else "RULE-APT-000",
                mitre=rule_apt.mitre if rule_apt else None
            )
            if alert:
                triggered_alerts.append(alert)

        # --- Rule: Reconnaissance Probe / Vulnerability Scan (Level: MENENGAH) ---
        # Rule ID: RULE-RECON-007
        rule_recon = self.rules.get("RULE-RECON-007")
        if (rule_recon is None or rule_recon.enabled) and event.event_type == "recon_probe":
            alert = self._create_alert(
                rule_name=rule_recon.title if rule_recon else "Reconnaissance Probe",
                severity=rule_recon.severity if rule_recon else "MENENGAH",
                description=(
                    f"Vulnerability reconnaissance probe detected from IP {event.ip_address} "
                    f"targeting user/service '{event.user_id}' at {event.location}."
                ),
                ip_address=event.ip_address,
                user_id=event.user_id,
                details={
                    "probe_type": "vulnerability_scan",
                    "ip_address": event.ip_address,
                    "user_id": event.user_id,
                    "location": event.location
                },
                cooldown_key=f"recon_{event.ip_address}",
                cooldown_seconds=rule_recon.cooldown_seconds if rule_recon else 5,
                ref_time=ts_utc,
                rule_id=rule_recon.id if rule_recon else "RULE-RECON-007",
                mitre=rule_recon.mitre if rule_recon else None
            )
            if alert:
                triggered_alerts.append(alert)

        # --- Rule 1: DDoS / Botnet (Level: TINGGI) ---
        # Rule ID: RULE-NET-001
        # > 10 web_request from 1 ip_address in 10 seconds
        rule_ddos = self.rules.get("RULE-NET-001")
        if event.event_type == "web_request":
            bucket = self.web_requests_by_ip[event.ip_address]
            bucket.append((ts_utc, event))
            window_sec = (rule_ddos.detection.correlation.window_seconds if rule_ddos and rule_ddos.detection.correlation else 10)
            threshold = (rule_ddos.detection.correlation.min_count if rule_ddos and rule_ddos.detection.correlation and rule_ddos.detection.correlation.min_count else 10)
            
            # Prune older than window
            cutoff = ts_utc - timedelta(seconds=window_sec)
            bucket = [entry for entry in bucket if entry[0] >= cutoff]
            self.web_requests_by_ip[event.ip_address] = bucket

            if (rule_ddos is None or rule_ddos.enabled) and len(bucket) > threshold:
                alert = self._create_alert(
                    rule_name=rule_ddos.title if rule_ddos else "DDoS / Botnet",
                    severity=rule_ddos.severity if rule_ddos else "TINGGI",
                    description=f"DDoS/Botnet pattern detected: {len(bucket)} web requests from IP {event.ip_address} within {window_sec}s.",
                    ip_address=event.ip_address,
                    user_id=event.user_id,
                    details={
                        "request_count": len(bucket),
                        "window_seconds": window_sec,
                        "ip_address": event.ip_address
                    },
                    cooldown_key=f"ddos_{event.ip_address}",
                    cooldown_seconds=rule_ddos.cooldown_seconds if rule_ddos else 5,
                    ref_time=ts_utc,
                    rule_id=rule_ddos.id if rule_ddos else "RULE-NET-001",
                    mitre=rule_ddos.mitre if rule_ddos else None
                )
                if alert:
                    triggered_alerts.append(alert)

        # --- Rule 2: Impossible Travel (Level: KRITIS) ---
        # Rule ID: RULE-AUTH-002
        # 2 login_attempt success from same user_id, but different location within < 1 hour (3600s)
        rule_travel = self.rules.get("RULE-AUTH-002")
        if event.event_type == "login_attempt" and event.status == "success":
            user_logins = self.successful_logins_by_user[event.user_id]
            window_sec = (rule_travel.detection.correlation.window_seconds if rule_travel and rule_travel.detection.correlation else 3600)
            cutoff = ts_utc - timedelta(seconds=window_sec)

            if rule_travel is None or rule_travel.enabled:
                # Find any recent login within window with different location
                for prev_ts, prev_event in reversed(user_logins):
                    if prev_ts >= cutoff and not self.is_host_isolated(prev_event.ip_address):
                        if prev_event.location.strip().lower() != event.location.strip().lower():
                            time_diff = abs((ts_utc - prev_ts).total_seconds())
                            alert = self._create_alert(
                                rule_name=rule_travel.title if rule_travel else "Impossible Travel",
                                severity=rule_travel.severity if rule_travel else "KRITIS",
                                description=(
                                    f"Impossible travel detected for user '{event.user_id}': "
                                    f"Login from '{event.location}' ({event.ip_address}) occurred {time_diff:.0f}s after "
                                    f"login from '{prev_event.location}' ({prev_event.ip_address})."
                                ),
                                ip_address=event.ip_address,
                                user_id=event.user_id,
                                details={
                                    "first_location": prev_event.location,
                                    "first_ip": prev_event.ip_address,
                                    "first_time": prev_ts.isoformat(),
                                    "second_location": event.location,
                                    "second_ip": event.ip_address,
                                    "second_time": ts_utc.isoformat(),
                                    "time_difference_seconds": time_diff
                                },
                                cooldown_key=f"imptravel_{event.user_id}_{event.location}_{prev_event.location}",
                                cooldown_seconds=rule_travel.cooldown_seconds if rule_travel else 10,
                                ref_time=ts_utc,
                                rule_id=rule_travel.id if rule_travel else "RULE-AUTH-002",
                                mitre=rule_travel.mitre if rule_travel else None
                            )
                            if alert:
                                triggered_alerts.append(alert)
                            break

            user_logins.append((ts_utc, event))
            # Prune older than window
            self.successful_logins_by_user[event.user_id] = [e for e in user_logins if e[0] >= cutoff]

        # --- Rule 3: Distributed Brute Force (Level: TINGGI) ---
        # Rule ID: RULE-AUTH-003
        # > 5 login_attempt failed for 1 user_id, from > 3 different ip_address in 1 minute (60s)
        rule_bf = self.rules.get("RULE-AUTH-003")
        if event.event_type == "login_attempt" and event.status == "failed":
            failed_bucket = self.failed_logins_by_user[event.user_id]
            failed_bucket.append((ts_utc, event))
            window_sec = (rule_bf.detection.correlation.window_seconds if rule_bf and rule_bf.detection.correlation else 60)
            threshold_count = (rule_bf.detection.correlation.min_count if rule_bf and rule_bf.detection.correlation and rule_bf.detection.correlation.min_count else 5)
            threshold_unique = (rule_bf.detection.correlation.min_unique_count if rule_bf and rule_bf.detection.correlation and rule_bf.detection.correlation.min_unique_count else 3)

            cutoff = ts_utc - timedelta(seconds=window_sec)
            failed_bucket = [e for e in failed_bucket if e[0] >= cutoff]
            self.failed_logins_by_user[event.user_id] = failed_bucket

            unique_ips = {e[1].ip_address for e in failed_bucket}
            if (rule_bf is None or rule_bf.enabled) and len(failed_bucket) > threshold_count and len(unique_ips) > threshold_unique:
                alert = self._create_alert(
                    rule_name=rule_bf.title if rule_bf else "Distributed Brute Force",
                    severity=rule_bf.severity if rule_bf else "TINGGI",
                    description=(
                        f"Distributed brute force attack detected for user '{event.user_id}': "
                        f"{len(failed_bucket)} failed attempts originating from {len(unique_ips)} distinct IPs within {window_sec}s."
                    ),
                    ip_address=event.ip_address,
                    user_id=event.user_id,
                    details={
                        "failed_attempts": len(failed_bucket),
                        "unique_ip_count": len(unique_ips),
                        "source_ips": list(unique_ips),
                        "window_seconds": window_sec
                    },
                    cooldown_key=f"bruteforce_{event.user_id}",
                    cooldown_seconds=rule_bf.cooldown_seconds if rule_bf else 10,
                    ref_time=ts_utc,
                    rule_id=rule_bf.id if rule_bf else "RULE-AUTH-003",
                    mitre=rule_bf.mitre if rule_bf else None
                )
                if alert:
                    triggered_alerts.append(alert)

        # --- Rule 4: Off-Hours Anomaly (Level: MENENGAH) ---
        # Rule ID: RULE-ANOM-004
        # Activity status: success (non-machine) outside working hours (00:00 - 05:00 local time)
        rule_offhours = self.rules.get("RULE-ANOM-004")
        if (rule_offhours is None or rule_offhours.enabled) and event.status == "success":
            machine_users = {"system", "machine", "cron", "service", "daemon", "backup", "internal_bot"}
            is_machine = (
                event.user_id.lower() in machine_users 
                or event.user_id.lower().startswith(("svc_", "sys_", "bot_"))
            )
            
            if not is_machine:
                local_dt = event.timestamp.astimezone() if event.timestamp.tzinfo else event.timestamp
                hour = local_dt.hour
                start_h = 0
                end_h = 5
                if rule_offhours and rule_offhours.detection.correlation and rule_offhours.detection.correlation.extra_params:
                    start_h = rule_offhours.detection.correlation.extra_params.get("start_hour", 0)
                    end_h = rule_offhours.detection.correlation.extra_params.get("end_hour", 5)

                if start_h <= hour < end_h:
                    alert = self._create_alert(
                        rule_name=rule_offhours.title if rule_offhours else "Off-Hours Anomaly",
                        severity=rule_offhours.severity if rule_offhours else "MENENGAH",
                        description=(
                            f"Off-hours user activity detected: User '{event.user_id}' performed '{event.event_type}' "
                            f"at {local_dt.strftime('%H:%M:%S')} (outside 05:00 - 23:59 operating hours)."
                        ),
                        ip_address=event.ip_address,
                        user_id=event.user_id,
                        details={
                            "event_type": event.event_type,
                            "local_time": local_dt.strftime("%Y-%m-%d %H:%M:%S %Z"),
                            "hour": hour
                        },
                        cooldown_key=f"offhours_{event.user_id}_{hour}",
                        cooldown_seconds=rule_offhours.cooldown_seconds if rule_offhours else 10,
                        ref_time=ts_utc,
                        rule_id=rule_offhours.id if rule_offhours else "RULE-ANOM-004",
                        mitre=rule_offhours.mitre if rule_offhours else None
                    )
                    if alert:
                        triggered_alerts.append(alert)

        # --- Rule 5: Data Exfiltration / Insider Threat (Level: KRITIS) ---
        # Rule ID: RULE-EXFIL-005
        # 1 user_id performs database_download > 50 times in 1 minute (60s)
        rule_exfil = self.rules.get("RULE-EXFIL-005")
        if event.event_type == "database_download":
            db_bucket = self.db_downloads_by_user[event.user_id]
            db_bucket.append((ts_utc, event))
            window_sec = (rule_exfil.detection.correlation.window_seconds if rule_exfil and rule_exfil.detection.correlation else 60)
            threshold = (rule_exfil.detection.correlation.min_count if rule_exfil and rule_exfil.detection.correlation and rule_exfil.detection.correlation.min_count else 50)

            cutoff = ts_utc - timedelta(seconds=window_sec)
            db_bucket = [e for e in db_bucket if e[0] >= cutoff]
            self.db_downloads_by_user[event.user_id] = db_bucket

            if (rule_exfil is None or rule_exfil.enabled) and len(db_bucket) > threshold:
                alert = self._create_alert(
                    rule_name=rule_exfil.title if rule_exfil else "Data Exfiltration / Insider Threat",
                    severity=rule_exfil.severity if rule_exfil else "KRITIS",
                    description=(
                        f"Potential data exfiltration detected: User '{event.user_id}' executed "
                        f"{len(db_bucket)} database downloads within {window_sec}s."
                    ),
                    ip_address=event.ip_address,
                    user_id=event.user_id,
                    details={
                        "download_count": len(db_bucket),
                        "window_seconds": window_sec,
                        "user_id": event.user_id
                    },
                    cooldown_key=f"exfiltration_{event.user_id}",
                    cooldown_seconds=rule_exfil.cooldown_seconds if rule_exfil else 10,
                    ref_time=ts_utc,
                    rule_id=rule_exfil.id if rule_exfil else "RULE-EXFIL-005",
                    mitre=rule_exfil.mitre if rule_exfil else None
                )
                if alert:
                    triggered_alerts.append(alert)

        # --- Rule: OT / Industrial Sabotage: Datacenter AC Central Shutdown (MQTT) (Level: KRITIS) ---
        # Rule ID: RULE-OT-006
        rule_ot = self.rules.get("RULE-OT-006")
        if (rule_ot is None or rule_ot.enabled) and event.event_type in ["ot_command", "mqtt_command"]:
            cmd_upper = (event.command or "").upper()
            topic_str = (event.topic or "").lower()
            target_str = (event.target_device or "").upper()
            device_str = (event.device_type or "").upper()

            is_shutdown_cmd = any(s in cmd_upper for s in ["OFF", "SHUTDOWN", "STOP", "KILL"]) or any(s in topic_str for s in ["power", "control", "set_power"])
            is_ac_device = (
                "AC" in device_str
                or any(k in target_str for k in ["AC", "CRAC", "HVAC", "CHILLER", "COOLING", "PAC"])
                or any(k in topic_str for k in ["cooling", "ac_central", "hvac", "chiller", "crac"])
            )

            if is_shutdown_cmd and (is_ac_device or cmd_upper in ["POWER_OFF", "EMERGENCY_SHUTDOWN", "STOP_COOLING", "KILL_SWITCH", "SHUTDOWN"]):
                protocol = event.protocol or "MQTT"
                target_device = event.target_device or "AC Central Datacenter"
                topic_display = event.topic or "datacenter/cooling/ac_central/power"
                cmd_display = event.command or "POWER_OFF"

                alert = self._create_alert(
                    rule_name=rule_ot.title if rule_ot else "OT Sabotage: Datacenter AC Central Shutdown (MQTT)",
                    severity=rule_ot.severity if rule_ot else "KRITIS",
                    description=(
                        f"CRITICAL OT SABOTAGE ALERT: Perintah tidak sah '{cmd_display}' terdeteksi via protokol {protocol} "
                        f"menargetkan pendingin datacenter '{target_device}' ({topic_display}) di {event.location} "
                        f"dari IP {event.ip_address} (User: {event.user_id}). Bahaya overheating / thermal runaway datacenter terancam!"
                    ),
                    ip_address=event.ip_address,
                    user_id=event.user_id,
                    details={
                        "protocol": protocol,
                        "topic": topic_display,
                        "command": cmd_display,
                        "target_device": target_device,
                        "device_type": event.device_type or "AC_CENTRAL",
                        "facility_impact": "Datacenter Cooling Loss / Thermal Overheating Risk",
                        "status": event.status,
                        "ip_address": event.ip_address,
                        "user_id": event.user_id,
                        "location": event.location
                    },
                    cooldown_key=f"ot_ac_shutdown_{event.ip_address}_{target_device}_{cmd_display}",
                    cooldown_seconds=rule_ot.cooldown_seconds if rule_ot else 5,
                    ref_time=ts_utc,
                    rule_id=rule_ot.id if rule_ot else "RULE-OT-006",
                    mitre=rule_ot.mitre if rule_ot else None
                )
                if alert:
                    triggered_alerts.append(alert)

        # Store triggered alerts in history
        for a in triggered_alerts:
            self.alerts.append(a)
            if len(self.alerts) > 1000:
                self.alerts.pop(0)

        return triggered_alerts

    def _create_alert(
        self,
        rule_name: str,
        severity: str,
        description: str,
        ip_address: Optional[str],
        user_id: Optional[str],
        details: dict,
        cooldown_key: str,
        cooldown_seconds: int,
        ref_time: datetime,
        rule_id: Optional[str] = None,
        mitre: Optional[MitreAttack] = None
    ) -> Optional[Alert]:
        # Check cooldown
        if cooldown_key in self.alert_cooldowns:
            last_alert = self.alert_cooldowns[cooldown_key]
            if (ref_time - last_alert).total_seconds() < cooldown_seconds:
                return None

        self.alert_cooldowns[cooldown_key] = ref_time

        # Automatic CTI Enrichment (Cortex-style observable enrichment)
        cti_data = self.cti.enrich(ip_address) if ip_address else None

        return Alert(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(timezone.utc),
            rule_name=rule_name,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_id=user_id,
            details=details,
            rule_id=rule_id,
            mitre=mitre,
            threat_intel=cti_data
        )
