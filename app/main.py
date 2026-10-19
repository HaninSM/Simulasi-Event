from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
import os

from app.models import LogEvent, Alert, WhitelistRequest
from app.engine import CorrelationEngine

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


@app.post("/api/ingest", status_code=status.HTTP_201_CREATED)
def ingest_log(event: LogEvent):
    """
    Ingests security event logs with schema & time drift validation.
    Returns HTTP 201 when accepted, or triggers alerts if correlation rules match.
    Returns HTTP 422 automatically if validation fails.
    """
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


@app.get("/api/stats")
def get_stats():
    """
    Returns aggregated metrics for dashboard widgets.
    """
    alerts_by_sev = {"KRITIS": 0, "TINGGI": 0, "MENENGAH": 0}
    for a in engine.alerts:
        if a.severity in alerts_by_sev:
            alerts_by_sev[a.severity] += 1

    events_by_type = {"login_attempt": 0, "web_request": 0, "database_download": 0}
    for log in engine.raw_logs:
        if log.event_type in events_by_type:
            events_by_type[log.event_type] += 1

    return {
        "total_logs_ingested": len(engine.raw_logs),
        "total_alerts": len(engine.alerts),
        "alerts_by_severity": alerts_by_sev,
        "events_by_type": events_by_type,
        "whitelist_count": len(engine.whitelist)
    }


@app.post("/api/reset")
def reset_siem():
    """
    Resets in-memory storage for demonstration freshness.
    """
    engine.clear_all()
    return {"status": "success", "message": "SIEM in-memory database and correlation state reset successfully."}
