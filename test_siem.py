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


def test_time_drift_past_rejected():
    # 1970 timestamp (> 24 hours ago)
    payload = {
        "timestamp": "1970-01-01T00:00:00Z",
        "event_type": "web_request",
        "user_id": "ancient_user",
        "ip_address": "192.168.1.1",
        "location": "Jakarta",
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


# ---------------- 8. STATS & RESET ----------------

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
