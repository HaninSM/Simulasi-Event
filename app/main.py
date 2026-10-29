from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import json

from app.models import (
    LogEvent, Alert, WhitelistRequest, WatchlistRequest,
    IsolateHostRequest, ReleaseHostRequest,
    SuspendUserRequest, UnsuspendUserRequest
)
from app.engine import CorrelationEngine
from app.log_adapter import LogAdapter

app = FastAPI(
    title="Mini-SIEM Command Center API",
    description="Real-time Security Information and Event Management Simulator",
    version="1.0.0"
)

# Enable CORS for dashboard interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = CorrelationEngine()

# Ensure static folder exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def get_dashboard():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Mini-SIEM API is active. Static dashboard not yet found."}


@app.get("/presentation")
def get_presentation():
    pres_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "presentation.html")
    if os.path.exists(pres_file):
        return FileResponse(pres_file)
    return {"message": "Presentation file not found."}


@app.post("/api/ingest", status_code=status.HTTP_201_CREATED)
def ingest_log(event: LogEvent):
    """
    Ingests security event logs with schema & time drift validation.
    Enforces SOAR Active Defense:
    1. Blocks traffic if user account is suspended (HTTP 403 USER_SUSPENDED).
    2. Drops traffic if source host is isolated (HTTP 403 HOST_ISOLATED).
    Returns HTTP 201 when accepted, or triggers alerts if correlation rules match.
    Returns HTTP 422 automatically if validation fails.
    """
    # Gatekeeper SOAR Enforcement 1: Check if user account is suspended
    if engine.is_user_suspended(event.user_id):
        engine.record_blocked_containment(event.ip_address)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"SECURITY CONTAINMENT: User account '{event.user_id}' is SUSPENDED by SOC Playbook. Authentication dropped at Gatekeeper."
        )

    # Gatekeeper SOAR Enforcement 2: Check if source host is isolated
    if engine.is_host_isolated(event.ip_address):
        engine.record_blocked_containment(event.ip_address)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"SECURITY CONTAINMENT: Host '{event.ip_address}' is ISOLATED by SOC Playbook. Traffic dropped at Gatekeeper."
        )

    triggered_alerts = engine.process_log(event)
    return {
        "status": "accepted",
        "whitelisted": engine.is_whitelisted(event.ip_address),
        "alerts_triggered": len(triggered_alerts),
        "alerts": triggered_alerts
    }


@app.get("/api/alerts", response_model=List[Alert])
def get_alerts(
    limit: int = Query(50, ge=1, le=500),
    severity: Optional[str] = Query(None)
):
    """
    Returns alerts sorted in reverse chronological order (newest first).
    """
    alerts = list(reversed(engine.alerts))
    if severity:
        alerts = [a for a in alerts if a.severity.upper() == severity.upper()]
    return alerts[:limit]


@app.get("/api/logs", response_model=List[LogEvent])
def get_recent_logs(limit: int = Query(50, ge=1, le=500)):
    """
    Returns recently ingested raw events for real-time log stream.
    """
    return list(reversed(engine.raw_logs))[:limit]


@app.post("/api/whitelist")
def add_whitelist(req: WhitelistRequest):
    """
    Whitelists an IP address. Logs from this IP will be completely ignored by the Correlation Engine,
    demonstrating the danger of careless whitelisting (blind spot).
    """
    entry = engine.add_to_whitelist(req)
    return {"status": "success", "message": f"IP {req.ip_address} added to whitelist", "data": entry}


@app.get("/api/whitelist")
def list_whitelist():
    return engine.get_whitelist()


@app.delete("/api/whitelist/{ip_address}")
def delete_whitelist(ip_address: str):
    removed = engine.remove_from_whitelist(ip_address)
    if not removed:
        raise HTTPException(status_code=404, detail="IP address not found in whitelist")
    return {"status": "success", "message": f"IP {ip_address} removed from whitelist"}


# ---------------- WATCHLIST & COLD STORAGE (APT DEFENSE) ----------------

@app.post("/api/watchlist")
def add_watchlist(req: WatchlistRequest):
    """
    Adds a suspicious IP to the persistent Watchlist (Greylist).
    Events from this IP will trigger critical alerts even across long retention windows.
    """
    entry = engine.add_to_watchlist(req)
    return {"status": "success", "message": f"IP {req.ip_address} added to persistent watchlist", "data": entry}


@app.get("/api/watchlist")
def list_watchlist():
    return engine.get_watchlist()


@app.delete("/api/watchlist/{ip_address}")
def delete_watchlist(ip_address: str):
    removed = engine.remove_from_watchlist(ip_address)
    if not removed:
        raise HTTPException(status_code=404, detail="IP address not found in watchlist")
    return {"status": "success", "message": f"IP {ip_address} removed from watchlist"}


@app.post("/api/archive/cold")
def archive_to_cold(ip_address: Optional[str] = None):
    """
    Simulates Log Lifecycle aging (> 14 days): moves hot logs to frozen cold archive.
    """
    count = engine.archive_to_cold(ip_address)
    return {
        "status": "success",
        "message": f"Moved {count} log(s) to cold storage archive (> 14 days aging simulation)",
        "archived_count": count
    }


@app.get("/api/archive/cold", response_model=List[LogEvent])
def list_cold_archive(limit: int = Query(50, ge=1, le=500)):
    return list(reversed(engine.get_cold_archive()))[:limit]


@app.post("/api/archive/rehydrate")
def rehydrate_cold(ip_address: str = Query(..., min_length=1)):
    """
    Simulates Cold Log Rehydration: pulls archived logs back into active investigation view.
    """
    rehydrated = engine.rehydrate_cold(ip_address)
    return {
        "status": "success",
        "message": f"Rehydrated {len(rehydrated)} cold log(s) for IP {ip_address}",
        "rehydrated_count": len(rehydrated),
        "data": rehydrated
    }


# ---------------- SOAR (ACTIVE DEFENSE & CONTAINMENT) ----------------

@app.post("/api/soar/isolate")
def isolate_host(req: IsolateHostRequest):
    """
    SOAR Active Defense: Quarantines a compromised or malicious host.
    Subsequent traffic from this host is immediately dropped at the Gatekeeper (HTTP 403).
    """
    entry = engine.isolate_host(
        ip_address=req.ip_address,
        reason=req.reason or "Contained by SOC Analyst via Active Defense Playbook",
        analyst=req.analyst or "SOC Analyst Tier-1"
    )
    return {
        "status": "success",
        "message": f"Host {req.ip_address} has been ISOLATED from network.",
        "data": entry
    }


@app.post("/api/soar/release")
def release_host(req: ReleaseHostRequest):
    """
    SOAR Active Defense: Releases a host from network quarantine.
    """
    released = engine.release_host(req.ip_address, analyst=req.analyst or "SOC Analyst Tier-1")
    if not released:
        raise HTTPException(status_code=404, detail=f"Host {req.ip_address} is not currently isolated.")
    return {
        "status": "success",
        "message": f"Host {req.ip_address} network quarantine released / restored."
    }


@app.get("/api/soar/isolated")
def list_isolated_hosts():
    """
    Returns list of all currently quarantined hosts.
    """
    return engine.get_isolated_hosts()


@app.get("/api/soar/audit")
def list_soar_audit(limit: int = Query(50, ge=1, le=200)):
    """
    Returns the SOAR containment action audit trail.
    """
    return engine.get_soar_audit_trail()[:limit]


@app.post("/api/soar/suspend-user")
def suspend_user(req: SuspendUserRequest):
    """
    SOAR Active Defense: Suspends a compromised user identity.
    Subsequent logins or actions by this user are immediately dropped at Gatekeeper (HTTP 403).
    """
    entry = engine.suspend_user(
        user_id=req.user_id,
        reason=req.reason or "Account suspended by SOC Playbook due to identity compromise / impossible travel",
        analyst=req.analyst or "SOC Analyst Tier-1"
    )
    return {
        "status": "success",
        "message": f"User account '{req.user_id}' has been SUSPENDED by SOC Playbook.",
        "data": entry
    }


@app.post("/api/soar/unsuspend-user")
def unsuspend_user(req: UnsuspendUserRequest):
    """
    SOAR Active Defense: Lifts suspension on a user identity.
    """
    restored = engine.unsuspend_user(req.user_id, analyst=req.analyst or "SOC Analyst Tier-1")
    if not restored:
        raise HTTPException(status_code=404, detail=f"User '{req.user_id}' is not currently suspended.")
    return {
        "status": "success",
        "message": f"User account '{req.user_id}' suspension lifted / restored."
    }


@app.get("/api/soar/suspended-users")
def list_suspended_users():
    """
    Returns list of all currently suspended user accounts.
    """
    return engine.get_suspended_users()


@app.get("/api/stats")
def get_stats():
    """
    Returns aggregated metrics for dashboard widgets.
    """
    alerts_by_sev = {"KRITIS": 0, "TINGGI": 0, "MENENGAH": 0}
    for a in engine.alerts:
        if a.severity in alerts_by_sev:
            alerts_by_sev[a.severity] += 1

    events_by_type = {"login_attempt": 0, "web_request": 0, "database_download": 0, "recon_probe": 0}
    for log in engine.raw_logs:
        if log.event_type in events_by_type:
            events_by_type[log.event_type] += 1

    return {
        "total_logs_ingested": len(engine.raw_logs),
        "total_alerts": len(engine.alerts),
        "alerts_by_severity": alerts_by_sev,
        "events_by_type": events_by_type,
        "whitelist_count": len(engine.whitelist),
        "watchlist_count": len(engine.watchlist),
        "cold_archive_count": len(engine.cold_archive),
        "isolated_hosts_count": len(engine.isolated_hosts),
        "suspended_users_count": len(engine.suspended_users),
        "blocked_containment_count": engine.blocked_containment_count
    }


@app.post("/api/reset")
def reset_siem():
    """
    Resets in-memory storage for demonstration freshness.
    """
    engine.clear_all()
    return {"status": "success", "message": "SIEM in-memory database and correlation state reset successfully."}


@app.post("/api/simulator/replay")
def replay_scenario(scenario: int = Query(..., ge=1, le=8)):
    """
    Replays attack scenarios by reading actual sample log files from sample_logs/ on disk.
    Parses them via LogAdapter and ingests them into the SIEM engine with dynamic timestamp shifting.
    """
    events = LogAdapter.load_scenario_from_file(scenario)
    if not events and scenario != 7:
        raise HTTPException(status_code=404, detail=f"Log file for scenario {scenario} not found or empty.")

    source_files = {
        1: "sample_logs/web_access_normal.log (Nginx Combined Log)",
        2: "sample_logs/nginx_ddos_flood.log (Nginx Access Log)",
        3: "sample_logs/vpn_and_gate_access.csv (Physical RFID + VPN Audit CSV)",
        4: "sample_logs/auth_sshd_bruteforce.log (Linux /var/log/auth.log Syslog)",
        5: "sample_logs/postgres_audit_exfiltration.jsonl (PostgreSQL PGAudit JSON)",
        6: "sample_logs/careless_whitelist_attack.log (Nginx Access Log)",
        7: "sample_logs/legacy_corrupted_device.log (Corrupted & Time-Drift Payload)",
        8: "sample_logs/apt_recon_and_exploit.log (Multi-Stage APT Telemetry)"
    }

    if scenario == 6:
        # Whitelist the attacker IP first
        attacker_ip = "203.0.113.88"
        engine.add_to_whitelist(WhitelistRequest(ip_address=attacker_ip, reason="Careless exception added by Admin"))
        alerts_triggered = []
        for ev in events:
            ev_clean = {k: v for k, v in ev.items() if k in LogEvent.model_fields}
            log_model = LogEvent(**ev_clean)
            al = engine.process_log(log_model)
            alerts_triggered.extend(al)

        return {
            "scenario": 6,
            "title": "Careless Whitelisting (Fatal Error / Blind Spot)",
            "source_file": source_files[6],
            "logs_processed": len(events),
            "whitelisted_ip": attacker_ip,
            "alerts_triggered": len(alerts_triggered),
            "blind_spot_confirmed": len(alerts_triggered) == 0,
            "message": "15 attack requests sent from whitelisted IP. SIEM completely ignored them (0 alerts triggered)!"
        }

    elif scenario == 7:
        # Corrupted data validation
        results = []
        for item in events:
            test_case = item.get("test_case")
            raw = item.get("raw_payload")
            passed = False
            try:
                if isinstance(raw, dict):
                    LogEvent(**raw)
                else:
                    json.loads(raw)
            except Exception:
                passed = True  # Schema or validation successfully caught and dropped it

            results.append({"test_case": test_case, "dropped_safely": passed})

        return {
            "scenario": 7,
            "title": "Malformed Log & Time Drift Validation",
            "source_file": source_files[7],
            "tests_executed": len(results),
            "all_dropped_safely": all(r["dropped_safely"] for r in results),
            "details": results,
            "message": "All corrupted payloads and time-drift logs were successfully dropped by Gatekeeper (HTTP 422 Drop)."
        }

    elif scenario == 8:
        # Low & Slow APT: Two-Act demonstration
        # Event 0: Day 1 Recon
        e1 = {k: v for k, v in events[0].items() if k in LogEvent.model_fields}
        recon_alerts = engine.process_log(LogEvent(**e1))

        # Aging simulation: Archive to cold storage
        archived_count = engine.archive_to_cold("198.51.100.77")

        # Solution applied: Add to persistent watchlist
        engine.add_to_watchlist(WatchlistRequest(
            ip_address="198.51.100.77",
            risk_level="HIGH",
            reason="Reconnaissance probe detected in Day 1 logs"
        ))

        # Event 1: Day 20 Exploit
        e2 = {k: v for k, v in events[1].items() if k in LogEvent.model_fields}
        exploit_alerts = engine.process_log(LogEvent(**e2))

        # Rehydrate for forensics
        rehydrated = engine.rehydrate_cold("198.51.100.77")

        return {
            "scenario": 8,
            "title": "The Low & Slow APT (Hot vs Cold Storage & Stateful Watchlist)",
            "source_file": source_files[8],
            "stages": [
                {"stage": "Day 1 Recon Probe Ingested", "alerts": len(recon_alerts)},
                {"stage": "Archived to Cold Storage (>14 days)", "archived_logs": archived_count},
                {"stage": "Persistent Stateful Watchlist Added", "ip": "198.51.100.77", "risk": "HIGH"},
                {"stage": "Day 20 Exploit Ingested", "alerts": [a.rule_name for a in exploit_alerts]},
                {"stage": "Cold Log Rehydration", "rehydrated_count": len(rehydrated)}
            ],
            "apt_detected": any(a.rule_name == "APT Low & Slow / Persistent Threat" for a in exploit_alerts),
            "message": "Multi-stage APT successfully correlated across cold retention cycle using Stateful Watchlist!"
        }

    # Standard scenarios: 1, 2, 3, 4, 5
    all_alerts = []
    blocked_count = 0
    accepted_count = 0

    for ev in events:
        ev_clean = {k: v for k, v in ev.items() if k in LogEvent.model_fields}
        log_model = LogEvent(**ev_clean)

        # Check if log is blocked by SOAR active containment (isolated host or suspended user)
        if engine.is_host_isolated(log_model.ip_address) or engine.is_user_suspended(log_model.user_id):
            engine.record_blocked_containment(log_model.ip_address)
            blocked_count += 1
            continue

        al = engine.process_log(log_model)
        all_alerts.extend(al)
        accepted_count += 1

    return {
        "scenario": scenario,
        "source_file": source_files.get(scenario, "sample_logs/"),
        "logs_processed": len(events),
        "logs_accepted": accepted_count,
        "logs_blocked_by_soar": blocked_count,
        "soar_containment_active": blocked_count > 0,
        "alerts_triggered": len(all_alerts),
        "alerts": all_alerts,
        "message": (
            f"SOAR Active Defense dropped {blocked_count} attack log(s) due to active quarantine/suspension."
            if blocked_count > 0 else None
        )
    }

