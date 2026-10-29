import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    engine.clear_all()
    yield
    engine.clear_all()


def get_iso_now(delta_seconds=0):
    dt = datetime.now(timezone.utc) + timedelta(seconds=delta_seconds)
    return dt.isoformat()


# ---------------- 1. GATEKEEPER & VALIDATION (HTTP 422) ----------------

def test_missing_ip_address_rejected():
    payload = {
        "timestamp": get_iso_now(),
        "event_type": "web_request",
        "user_id": "test_user",
        "ip_address": "",
        "location": "Jakarta",
        "status": "success"
    }
    response = client.post("/api/ingest", json=payload)
    assert response.status_code == 422


def test_null_ip_address_rejected():
    # Skenario Negatif: Server lama mengirim log dengan ip_address: null
    payload = {
        "timestamp": get_iso_now(),
        "event_type": "web_request",
        "user_id": "legacy_server_01",
        "ip_address": None,
        "location": "Server Room A",
        "status": "success"
    }
    response = client.post("/api/ingest", json=payload)
    assert response.status_code == 422


def test_missing_ip_key_completely_rejected():
    # Skenario Negatif: Server lama mengirim log tanpa atribut ip_address sama sekali
    payload = {
        "timestamp": get_iso_now(),
        "event_type": "web_request",
        "user_id": "legacy_server_02",
        "location": "Server Room A",
        "status": "success"
    }
    response = client.post("/api/ingest", json=payload)
    assert response.status_code == 422


def test_truncated_malformed_json_rejected():
    # Skenario Negatif: Jaringan putus di tengah jalan sehingga JSON terpotong (syntax rusak)
    raw_truncated_payload = '{"timestamp": "2026-10-20T03:00:00Z", "event_type": "web_request", "user_id": "legacy'
    response = client.post(
        "/api/ingest",
        content=raw_truncated_payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


def test_invalid_ipv4_rejected():
    payload = {
        "timestamp": get_iso_now(),
        "event_type": "web_request",
        "user_id": "test_user",
        "ip_address": "999.999.999.999",
        "location": "Jakarta",
        "status": "success"
    }
    response = client.post("/api/ingest", json=payload)
    assert response.status_code == 422


def test_time_drift_cmos_battery_reset_1970_rejected():
    # Skenario Negatif: Baterai CMOS server HRD habis, jam me-reset ke tahun 1970 (> 24 jam lampau)
    payload = {
        "timestamp": "1970-01-01T00:00:00Z",
        "event_type": "login_attempt",
        "user_id": "hrd_staff_budi",
        "ip_address": "192.168.1.50",
        "location": "Kantor HRD",
        "status": "success"
    }
    response = client.post("/api/ingest", json=payload)
    assert response.status_code == 422
    assert "Time Drift Error" in response.text


def test_time_drift_future_rejected():
    # Far in future
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    payload = {
        "timestamp": future_time,
        "event_type": "login_attempt",
        "user_id": "future_user",
        "ip_address": "192.168.1.1",
        "location": "Jakarta",
        "status": "success"
    }
    response = client.post("/api/ingest", json=payload)
    assert response.status_code == 422
    assert "Time Drift Error" in response.text


def test_invalid_event_type_rejected():
    payload = {
        "timestamp": get_iso_now(),
        "event_type": "unauthorized_command",
        "user_id": "user1",
        "ip_address": "192.168.1.1",
        "location": "Jakarta",
        "status": "success"
    }
    response = client.post("/api/ingest", json=payload)
    assert response.status_code == 422


# ---------------- 2. RULE 1: DDOS / BOTNET ----------------

def test_rule_1_ddos_detection():
    ip = "45.33.32.156"
    alerts_seen = 0

    # Send 15 requests in rapid succession
    for i in range(15):
        payload = {
            "timestamp": get_iso_now(),
            "event_type": "web_request",
            "user_id": f"bot_{i}",
            "ip_address": ip,
            "location": "Unknown",
            "status": "success"
        }
        res = client.post("/api/ingest", json=payload)
        assert res.status_code == 201
        alerts_seen += res.json().get("alerts_triggered", 0)

    assert alerts_seen >= 1
    alerts = client.get("/api/alerts").json()
    assert any(a["rule_name"] == "DDoS / Botnet" and a["severity"] == "TINGGI" for a in alerts)


# ---------------- 3. RULE 2: IMPOSSIBLE TRAVEL ----------------

def test_rule_2_impossible_travel():
    user = "alice_exec"

    # Login 1 in Jakarta
    res1 = client.post("/api/ingest", json={
        "timestamp": get_iso_now(-5),
        "event_type": "login_attempt",
        "user_id": user,
        "ip_address": "103.24.56.12",
        "location": "Jakarta, ID",
        "status": "success"
    })
    assert res1.status_code == 201
    assert res1.json()["alerts_triggered"] == 0

    # Login 2 in Frankfurt (< 1 hour later)
    res2 = client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "login_attempt",
        "user_id": user,
        "ip_address": "185.190.140.2",
        "location": "Frankfurt, DE",
        "status": "success"
    })
    assert res2.status_code == 201
    assert res2.json()["alerts_triggered"] >= 1

    alerts = client.get("/api/alerts").json()
    assert any(a["rule_name"] == "Impossible Travel" and a["severity"] == "KRITIS" for a in alerts)


# ---------------- 4. RULE 3: DISTRIBUTED BRUTE FORCE ----------------

def test_rule_3_distributed_brute_force():
    user = "admin_target"
    ips = ["198.51.100.1", "198.51.100.2", "198.51.100.3", "198.51.100.4"]

    # Send 7 failed logins across 4 distinct IPs
    for i in range(7):
        res = client.post("/api/ingest", json={
            "timestamp": get_iso_now(),
            "event_type": "login_attempt",
            "user_id": user,
            "ip_address": ips[i % len(ips)],
            "location": "Unknown",
            "status": "failed"
        })
        assert res.status_code == 201

    alerts = client.get("/api/alerts").json()
    assert any(a["rule_name"] == "Distributed Brute Force" and a["severity"] == "TINGGI" for a in alerts)


# ---------------- 5. RULE 4: OFF-HOURS ANOMALY ----------------

def test_rule_4_off_hours_anomaly():
    # Construct a timestamp at 02:30 AM local time
    local_now = datetime.now()
    off_hours_dt = local_now.replace(hour=2, minute=30, second=0)
    # Convert to UTC
    off_hours_utc = off_hours_dt.astimezone(timezone.utc)

    # Human user activity in off-hours
    res = client.post("/api/ingest", json={
        "timestamp": off_hours_utc.isoformat(),
        "event_type": "login_attempt",
        "user_id": "human_staff",
        "ip_address": "192.168.1.55",
        "location": "HQ Office",
        "status": "success"
    })
    assert res.status_code == 201
    alerts = client.get("/api/alerts").json()
    assert any(a["rule_name"] == "Off-Hours Anomaly" and a["severity"] == "MENENGAH" for a in alerts)

    # Machine/service user activity should NOT trigger Off-Hours Anomaly
    engine.clear_all()
    res_machine = client.post("/api/ingest", json={
        "timestamp": off_hours_utc.isoformat(),
        "event_type": "login_attempt",
        "user_id": "svc_backup_agent",
        "ip_address": "192.168.1.55",
        "location": "HQ Office",
        "status": "success"
    })
    assert res_machine.status_code == 201
    assert res_machine.json()["alerts_triggered"] == 0


# ---------------- 6. RULE 5: DATA EXFILTRATION ----------------

def test_rule_5_data_exfiltration():
    user = "insider_dave"
    for _ in range(55):
        res = client.post("/api/ingest", json={
            "timestamp": get_iso_now(),
            "event_type": "database_download",
            "user_id": user,
            "ip_address": "10.0.1.50",
            "location": "Internal Office",
            "status": "success"
        })
        assert res.status_code == 201

    alerts = client.get("/api/alerts").json()
    assert any(a["rule_name"] == "Data Exfiltration / Insider Threat" and a["severity"] == "KRITIS" for a in alerts)


# ---------------- 7. CARELESS WHITELISTING (FATAL BLIND SPOT) ----------------

def test_careless_whitelisting_blinds_correlation_engine():
    attacker_ip = "203.0.113.88"

    # Add attacker IP to whitelist
    wl_res = client.post("/api/whitelist", json={
        "ip_address": attacker_ip,
        "reason": "Whitelisted for testing blind spot"
    })
    assert wl_res.status_code == 200

    # Ingest 15 DDoS requests from the whitelisted IP
    for i in range(15):
        res = client.post("/api/ingest", json={
            "timestamp": get_iso_now(),
            "event_type": "web_request",
            "user_id": f"bot_{i}",
            "ip_address": attacker_ip,
            "location": "Unknown",
            "status": "success"
        })
        assert res.status_code == 201
        assert res.json()["whitelisted"] is True
        assert res.json()["alerts_triggered"] == 0

    # Alerts must remain 0 because correlation engine ignored it!
    alerts = client.get("/api/alerts").json()
    assert len(alerts) == 0

    # Remove from whitelist
    del_res = client.delete(f"/api/whitelist/{attacker_ip}")
    assert del_res.status_code == 200

    # Now the same attack will trigger an alert!
    for i in range(15):
        client.post("/api/ingest", json={
            "timestamp": get_iso_now(),
            "event_type": "web_request",
            "user_id": f"bot_{i}",
            "ip_address": attacker_ip,
            "location": "Unknown",
            "status": "success"
        })
    alerts_after = client.get("/api/alerts").json()
    assert len(alerts_after) >= 1


# ---------------- 9. SCENARIO 8: LOW & SLOW APT / HOT VS COLD STORAGE ----------------

def test_scenario_8_recon_probe_and_cold_storage_aging():
    attacker_ip = "198.51.100.77"

    # Day 1: Attacker sends reconnaissance probe
    res = client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "recon_probe",
        "user_id": "target_service",
        "ip_address": attacker_ip,
        "location": "External Border Gateway",
        "status": "success"
    })
    assert res.status_code == 201
    assert res.json()["alerts_triggered"] == 1
    assert res.json()["alerts"][0]["rule_name"] == "Reconnaissance Probe"
    assert res.json()["alerts"][0]["severity"] == "MENENGAH"

    # Simulate 14-day Log Lifecycle: Move Day 1 logs to cold archive
    archive_res = client.post(f"/api/archive/cold?ip_address={attacker_ip}")
    assert archive_res.status_code == 200
    assert archive_res.json()["archived_count"] >= 1

    # Verify hot storage is cleared of this log
    hot_logs = client.get("/api/logs").json()
    assert not any(l["ip_address"] == attacker_ip for l in hot_logs)

    # Verify cold storage contains the Day 1 recon log
    cold_logs = client.get("/api/archive/cold").json()
    assert any(l["ip_address"] == attacker_ip and l["event_type"] == "recon_probe" for l in cold_logs)


def test_scenario_8_apt_correlation_blind_spot_without_watchlist():
    attacker_ip = "198.51.100.88"

    # Day 1 Recon probe
    client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "recon_probe",
        "user_id": "target_web",
        "ip_address": attacker_ip,
        "location": "DMZ Gateway",
        "status": "success"
    })

    # 14 days pass -> Archived to cold storage
    client.post(f"/api/archive/cold?ip_address={attacker_ip}")

    # Day 20: Attacker executes single exploit web_request
    # WITHOUT persistent watchlist, correlation fails (treated as an isolated normal request)
    day20_res = client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "web_request",
        "user_id": "api_endpoint",
        "ip_address": attacker_ip,
        "location": "Jakarta DMZ",
        "status": "success"
    })
    assert day20_res.status_code == 201
    # No APT alert triggered because Day 1 was frozen in cold storage
    alerts = day20_res.json()["alerts"]
    assert not any(a["rule_name"] == "APT Low & Slow / Persistent Threat" for a in alerts)


def test_scenario_8_apt_correlation_success_with_persistent_watchlist():
    attacker_ip = "198.51.100.99"

    # Day 1 Recon probe
    client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "recon_probe",
        "user_id": "target_web",
        "ip_address": attacker_ip,
        "location": "DMZ Gateway",
        "status": "success"
    })

    # SOLUTION: Flag IP into persistent Watchlist/Greylist
    wl_res = client.post("/api/watchlist", json={
        "ip_address": attacker_ip,
        "risk_level": "HIGH",
        "reason": "Reconnaissance probe detected on Day 1"
    })
    assert wl_res.status_code == 200

    # 14 days pass -> Day 1 logs moved to Cold Storage
    client.post(f"/api/archive/cold?ip_address={attacker_ip}")

    # Day 20: Attacker returns and launches exploit
    day20_res = client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "web_request",
        "user_id": "admin_portal",
        "ip_address": attacker_ip,
        "location": "Jakarta DMZ",
        "status": "success"
    })
    assert day20_res.status_code == 201
    assert day20_res.json()["alerts_triggered"] >= 1
    apt_alerts = [a for a in day20_res.json()["alerts"] if a["rule_name"] == "APT Low & Slow / Persistent Threat"]
    assert len(apt_alerts) == 1
    assert apt_alerts[0]["severity"] == "KRITIS"

    # Test Cold Log Rehydration: Fetch Day 1 logs for forensic correlation
    rehydrate_res = client.post(f"/api/archive/rehydrate?ip_address={attacker_ip}")
    assert rehydrate_res.status_code == 200
    assert rehydrate_res.json()["rehydrated_count"] >= 1
    assert rehydrate_res.json()["data"][0]["event_type"] == "recon_probe"


def test_stats_and_reset_endpoints():
    client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "web_request",
        "user_id": "user1",
        "ip_address": "192.168.1.1",
        "location": "Jakarta",
        "status": "success"
    })
    stats = client.get("/api/stats").json()
    assert stats["total_logs_ingested"] >= 1

    reset_res = client.post("/api/reset")
    assert reset_res.status_code == 200

    stats_after = client.get("/api/stats").json()
    assert stats_after["total_logs_ingested"] == 0
    assert stats_after["total_alerts"] == 0


def test_log_adapter_parses_real_sample_files():
    from app.log_adapter import LogAdapter
    for sc in range(1, 9):
        events = LogAdapter.load_scenario_from_file(sc)
        assert len(events) > 0, f"Scenario {sc} sample log failed to load"


def test_api_simulator_replay_scenarios():
    # Test Scenario 1 (Normal)
    client.post("/api/reset")
    r1 = client.post("/api/simulator/replay?scenario=1")
    assert r1.status_code == 200
    assert r1.json()["logs_processed"] == 5
    assert r1.json()["alerts_triggered"] == 0

    # Test Scenario 2 (DDoS from nginx_ddos_flood.log)
    client.post("/api/reset")
    r2 = client.post("/api/simulator/replay?scenario=2")
    assert r2.status_code == 200
    assert r2.json()["logs_processed"] == 15
    assert r2.json()["alerts_triggered"] >= 1
    assert any("DDoS" in a["rule_name"] for a in r2.json()["alerts"])

    # Test Scenario 6 (Careless Whitelisting)
    client.post("/api/reset")
    r6 = client.post("/api/simulator/replay?scenario=6")
    assert r6.status_code == 200
    assert r6.json()["blind_spot_confirmed"] is True
    assert r6.json()["alerts_triggered"] == 0

    # Test Scenario 7 (Corrupted Device Validation)
    r7 = client.post("/api/simulator/replay?scenario=7")
    assert r7.status_code == 200
    assert r7.json()["all_dropped_safely"] is True

    # Test Scenario 8 (APT)
    client.post("/api/reset")
    r8 = client.post("/api/simulator/replay?scenario=8")
    assert r8.status_code == 200
    assert r8.json()["apt_detected"] is True


def test_soar_isolate_host_blocks_subsequent_ingestion_http_403():
    client.post("/api/reset")
    target_ip = "45.33.32.156"

    # 1. Normal ingestion works initially
    res_before = client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "web_request",
        "user_id": "client_tester",
        "ip_address": target_ip,
        "location": "Dallas, US",
        "status": "success"
    })
    assert res_before.status_code == 201

    # 2. SOC Analyst triggers Isolate Host via SOAR
    iso_res = client.post("/api/soar/isolate", json={
        "ip_address": target_ip,
        "reason": "Host exhibiting L7 flood DDoS attack pattern",
        "analyst": "SOC Analyst Tier-2"
    })
    assert iso_res.status_code == 200
    assert iso_res.json()["status"] == "success"
    assert iso_res.json()["data"]["ip_address"] == target_ip

    # 3. Subsequent ingestion from this host must be dropped with HTTP 403 Forbidden
    res_after = client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "web_request",
        "user_id": "attacker_drone",
        "ip_address": target_ip,
        "location": "Dallas, US",
        "status": "success"
    })
    assert res_after.status_code == 403
    assert "ISOLATED" in res_after.json()["detail"]

    # 4. Check stats reflect the quarantined host and blocked traffic
    stats = client.get("/api/stats").json()
    assert stats["isolated_hosts_count"] == 1
    assert stats["blocked_containment_count"] >= 1


def test_soar_release_host_restores_ingestion():
    client.post("/api/reset")
    target_ip = "10.0.8.21"

    # Isolate
    client.post("/api/soar/isolate", json={"ip_address": target_ip, "reason": "Data exfil suspect"})

    # Verify blocked
    res_blocked = client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "database_download",
        "user_id": "dev_suspect",
        "ip_address": target_ip,
        "location": "Internal LAN",
        "status": "success"
    })
    assert res_blocked.status_code == 403

    # Release Host
    rel_res = client.post("/api/soar/release", json={"ip_address": target_ip})
    assert rel_res.status_code == 200
    assert rel_res.json()["status"] == "success"

    # Traffic should now flow normally
    res_restored = client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "database_download",
        "user_id": "dev_suspect",
        "ip_address": target_ip,
        "location": "Internal LAN",
        "status": "success"
    })
    assert res_restored.status_code == 201


def test_soar_alert_status_transitions_to_contained():
    client.post("/api/reset")
    attacker_ip = "45.33.32.156"

    # Trigger DDoS alert (Scenario 2)
    client.post("/api/simulator/replay?scenario=2")
    alerts_before = client.get("/api/alerts").json()
    assert len(alerts_before) >= 1
    assert any(a["ip_address"] == attacker_ip and a["status"] == "NEW" for a in alerts_before)

    # Isolate the host
    client.post("/api/soar/isolate", json={"ip_address": attacker_ip, "reason": "DDoS remediation"})

    # Check alert status transitioned to CONTAINED
    alerts_after = client.get("/api/alerts").json()
    contained_alerts = [a for a in alerts_after if a["ip_address"] == attacker_ip]
    assert len(contained_alerts) >= 1
    assert all(a["status"] == "CONTAINED" for a in contained_alerts)


def test_soar_stats_and_audit_trail():
    client.post("/api/reset")
    test_ip = "192.168.100.50"

    client.post("/api/soar/isolate", json={"ip_address": test_ip, "reason": "Malware beacon"})
    audit_log = client.get("/api/soar/audit").json()
    assert len(audit_log) >= 1
    assert audit_log[0]["action"] == "ISOLATE"
    assert audit_log[0]["ip_address"] == test_ip

    client.post("/api/soar/release", json={"ip_address": test_ip})
    audit_after = client.get("/api/soar/audit").json()
    assert audit_after[0]["action"] == "RELEASE"

    # Reset clears isolated state
    client.post("/api/reset")
    stats = client.get("/api/stats").json()
    assert stats["isolated_hosts_count"] == 0
    assert stats["blocked_containment_count"] == 0


def test_scenario_3_impossible_travel_isolation_blocks_subsequent_replay():
    client.post("/api/reset")
    # 1. Replay Scenario 3 first time: triggers Impossible Travel alert
    r1 = client.post("/api/simulator/replay?scenario=3")
    assert r1.status_code == 200
    assert r1.json()["alerts_triggered"] == 1
    frankfurt_ip = "185.190.140.2"

    # 2. Isolate the Frankfurt host (SOAR Action)
    iso_res = client.post("/api/soar/isolate", json={
        "ip_address": frankfurt_ip,
        "reason": "Impossible travel VPN host"
    })
    assert iso_res.status_code == 200

    # 3. Replay Scenario 3 again: Frankfurt host is isolated, so event is blocked!
    r2 = client.post("/api/simulator/replay?scenario=3")
    assert r2.status_code == 200
    assert r2.json()["logs_blocked_by_soar"] >= 1
    assert r2.json()["soar_containment_active"] is True
    # Crucial assertion: NO new alert is triggered because the second leg was blocked!
    assert r2.json()["alerts_triggered"] == 0


def test_soar_user_suspension_blocks_logins_and_replays():
    client.post("/api/reset")
    target_user = "sarah_security"

    # 1. Suspend the compromised user account via SOAR
    sus_res = client.post("/api/soar/suspend-user", json={
        "user_id": target_user,
        "reason": "Compromised credentials flagged by impossible travel"
    })
    assert sus_res.status_code == 200
    assert sus_res.json()["status"] == "success"

    # 2. Ingestion attempt by this user is rejected with HTTP 403 USER_SUSPENDED
    ingest_res = client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "login_attempt",
        "user_id": target_user,
        "ip_address": "103.24.56.12",
        "location": "Jakarta ID",
        "status": "success"
    })
    assert ingest_res.status_code == 403
    assert "SUSPENDED" in ingest_res.json()["detail"]

    # 3. Replay Scenario 3: all events belong to sarah_security, so both are blocked!
    replay_res = client.post("/api/simulator/replay?scenario=3")
    assert replay_res.status_code == 200
    assert replay_res.json()["logs_blocked_by_soar"] == 2
    assert replay_res.json()["alerts_triggered"] == 0

    # 4. Unsuspend the user
    unsus_res = client.post("/api/soar/unsuspend-user", json={"user_id": target_user})
    assert unsus_res.status_code == 200

    # 5. Normal login restores
    restore_res = client.post("/api/ingest", json={
        "timestamp": get_iso_now(),
        "event_type": "login_attempt",
        "user_id": target_user,
        "ip_address": "103.24.56.12",
        "location": "Jakarta ID",
        "status": "success"
    })
    assert restore_res.status_code == 201

