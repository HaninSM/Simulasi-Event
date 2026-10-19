import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Set, Optional
from collections import defaultdict

from app.models import LogEvent, Alert, WhitelistRequest


class CorrelationEngine:
    def __init__(self):
        # Whitelisted IP addresses: ip_address -> dict(reason, added_at)
        self.whitelist: Dict[str, dict] = {}
        
        # In-memory storage for logs and alerts
        self.raw_logs: List[LogEvent] = []
        self.alerts: List[Alert] = []

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

    def clear_all(self):
        self.raw_logs.clear()
        self.alerts.clear()
        self.web_requests_by_ip.clear()
        self.successful_logins_by_user.clear()
        self.failed_logins_by_user.clear()
        self.db_downloads_by_user.clear()
        self.alert_cooldowns.clear()

    def process_log(self, event: LogEvent) -> List[Alert]:
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

        # --- Rule 1: DDoS / Botnet (Level: TINGGI) ---
        # > 10 web_request from 1 ip_address in 10 seconds
        if event.event_type == "web_request":
            bucket = self.web_requests_by_ip[event.ip_address]
            bucket.append((ts_utc, event))
            # Prune older than 10 seconds
            cutoff = ts_utc - timedelta(seconds=10)
            bucket = [entry for entry in bucket if entry[0] >= cutoff]
            self.web_requests_by_ip[event.ip_address] = bucket

            if len(bucket) > 10:
                alert = self._create_alert(
                    rule_name="DDoS / Botnet",
                    severity="TINGGI",
                    description=f"DDoS/Botnet pattern detected: {len(bucket)} web requests from IP {event.ip_address} within 10s.",
                    ip_address=event.ip_address,
                    user_id=event.user_id,
                    details={
                        "request_count": len(bucket),
                        "window_seconds": 10,
                        "ip_address": event.ip_address
                    },
                    cooldown_key=f"ddos_{event.ip_address}",
                    cooldown_seconds=5,
                    ref_time=ts_utc
                )
                if alert:
                    triggered_alerts.append(alert)

        # --- Rule 2: Impossible Travel (Level: KRITIS) ---
        # 2 login_attempt success from same user_id, but different location within < 1 hour (3600s)
        if event.event_type == "login_attempt" and event.status == "success":
            user_logins = self.successful_logins_by_user[event.user_id]
            cutoff = ts_utc - timedelta(hours=1)
            # Find any recent login within < 1 hour with different location
            for prev_ts, prev_event in reversed(user_logins):
                if prev_ts >= cutoff:
                    if prev_event.location.strip().lower() != event.location.strip().lower():
                        time_diff = abs((ts_utc - prev_ts).total_seconds())
                        alert = self._create_alert(
                            rule_name="Impossible Travel",
                            severity="KRITIS",
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
                            cooldown_seconds=10,
                            ref_time=ts_utc
                        )
                        if alert:
                            triggered_alerts.append(alert)
                        break

            user_logins.append((ts_utc, event))
            # Prune older than 1 hour
            self.successful_logins_by_user[event.user_id] = [e for e in user_logins if e[0] >= cutoff]

        # --- Rule 3: Distributed Brute Force (Level: TINGGI) ---
        # > 5 login_attempt failed for 1 user_id, from > 3 different ip_address in 1 minute (60s)
        if event.event_type == "login_attempt" and event.status == "failed":
            failed_bucket = self.failed_logins_by_user[event.user_id]
            failed_bucket.append((ts_utc, event))
            cutoff = ts_utc - timedelta(seconds=60)
            failed_bucket = [e for e in failed_bucket if e[0] >= cutoff]
            self.failed_logins_by_user[event.user_id] = failed_bucket

            unique_ips = {e[1].ip_address for e in failed_bucket}
            if len(failed_bucket) > 5 and len(unique_ips) > 3:
                alert = self._create_alert(
                    rule_name="Distributed Brute Force",
                    severity="TINGGI",
                    description=(
                        f"Distributed brute force attack detected for user '{event.user_id}': "
                        f"{len(failed_bucket)} failed attempts originating from {len(unique_ips)} distinct IPs within 60s."
                    ),
                    ip_address=event.ip_address,
                    user_id=event.user_id,
                    details={
                        "failed_attempts": len(failed_bucket),
                        "unique_ip_count": len(unique_ips),
                        "source_ips": list(unique_ips),
                        "window_seconds": 60
                    },
                    cooldown_key=f"bruteforce_{event.user_id}",
                    cooldown_seconds=10,
                    ref_time=ts_utc
                )
                if alert:
                    triggered_alerts.append(alert)

        # --- Rule 4: Off-Hours Anomaly (Level: MENENGAH) ---
        # Activity status: success (non-machine) outside working hours (00:00 - 05:00 local time)
        if event.status == "success":
            machine_users = {"system", "machine", "cron", "service", "daemon", "backup", "internal_bot"}
            is_machine = (
                event.user_id.lower() in machine_users 
                or event.user_id.lower().startswith(("svc_", "sys_", "bot_"))
            )
            
            if not is_machine:
                # Check local time hour (convert event timestamp to local system time or check local hour)
                # Event timestamp local hour
                local_dt = event.timestamp.astimezone() if event.timestamp.tzinfo else event.timestamp
                hour = local_dt.hour
                if 0 <= hour < 5:
                    alert = self._create_alert(
                        rule_name="Off-Hours Anomaly",
                        severity="MENENGAH",
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
                        cooldown_seconds=10,
                        ref_time=ts_utc
                    )
                    if alert:
                        triggered_alerts.append(alert)

        # --- Rule 5: Data Exfiltration / Insider Threat (Level: KRITIS) ---
        # 1 user_id performs database_download > 50 times in 1 minute (60s)
        if event.event_type == "database_download":
            db_bucket = self.db_downloads_by_user[event.user_id]
            db_bucket.append((ts_utc, event))
            cutoff = ts_utc - timedelta(seconds=60)
            db_bucket = [e for e in db_bucket if e[0] >= cutoff]
            self.db_downloads_by_user[event.user_id] = db_bucket

            if len(db_bucket) > 50:
                alert = self._create_alert(
                    rule_name="Data Exfiltration / Insider Threat",
                    severity="KRITIS",
                    description=(
                        f"Potential data exfiltration detected: User '{event.user_id}' executed "
                        f"{len(db_bucket)} database downloads within 60s."
                    ),
                    ip_address=event.ip_address,
                    user_id=event.user_id,
                    details={
                        "download_count": len(db_bucket),
                        "window_seconds": 60,
                        "user_id": event.user_id
                    },
                    cooldown_key=f"exfiltration_{event.user_id}",
                    cooldown_seconds=10,
                    ref_time=ts_utc
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
        ref_time: datetime
    ) -> Optional[Alert]:
        # Check cooldown
        if cooldown_key in self.alert_cooldowns:
            last_alert = self.alert_cooldowns[cooldown_key]
            if (ref_time - last_alert).total_seconds() < cooldown_seconds:
                return None

        self.alert_cooldowns[cooldown_key] = ref_time
        return Alert(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(timezone.utc),
            rule_name=rule_name,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_id=user_id,
            details=details
        )
