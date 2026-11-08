import ipaddress
from datetime import datetime, timezone, timedelta
from typing import Optional, Literal, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, model_validator


EventType = Literal["login_attempt", "web_request", "database_download", "recon_probe", "ot_command", "mqtt_command"]
EventStatus = Literal["success", "failed"]
SeverityLevel = Literal["KRITIS", "TINGGI", "MENENGAH"]


class MitreAttack(BaseModel):
    tactic: str
    technique_id: str
    technique_name: str


class RuleCorrelation(BaseModel):
    type: str  # "threshold_aggregation" | "impossible_travel" | "watchlist_match" | "single_event" | "off_hours" | "ot_command"
    window_seconds: Optional[int] = 60
    min_count: Optional[int] = None
    group_by: Optional[str] = None
    min_unique_field: Optional[str] = None
    min_unique_count: Optional[int] = None
    extra_params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class RuleDetection(BaseModel):
    event_type: Optional[str] = "any"
    status: Optional[str] = "any"
    correlation: Optional[RuleCorrelation] = None


class DetectionRule(BaseModel):
    id: str
    title: str
    status: str = "production"
    severity: SeverityLevel
    description: str
    mitre: Optional[MitreAttack] = None
    detection: RuleDetection
    cooldown_seconds: int = 10
    enabled: bool = True


class ToggleRuleRequest(BaseModel):
    enabled: bool


class LogEvent(BaseModel):
    timestamp: datetime
    event_type: EventType
    user_id: str = Field(..., min_length=1)
    ip_address: str
    location: str = Field(..., min_length=1)
    status: EventStatus
    protocol: Optional[str] = "MQTT"
    device_type: Optional[str] = None
    target_device: Optional[str] = None
    command: Optional[str] = None
    topic: Optional[str] = None

    @field_validator("ip_address")
    @classmethod
    def validate_ipv4(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("ip_address cannot be empty")
        v = v.strip()
        try:
            addr = ipaddress.IPv4Address(v)
            return str(addr)
        except Exception:
            raise ValueError(f"'{v}' is not a valid IPv4 address")

    @field_validator("user_id", "location")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()

    @model_validator(mode="after")
    def validate_time_drift(self):
        # Normalize timestamp to UTC
        ts = self.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        else:
            ts = ts.astimezone(timezone.utc)

        now = datetime.now(timezone.utc)
        diff = (now - ts).total_seconds()

        # Reject if > 24 hours in the past
        if diff > 86400:
            raise ValueError(f"Timestamp is older than 24 hours ({diff:.0f}s ago). Time Drift Error.")

        # Reject if in the future (> 30s allowance for minor clock skew)
        if diff < -30:
            raise ValueError(f"Timestamp is in the future ({-diff:.0f}s ahead). Time Drift Error.")

        return self


class WhitelistRequest(BaseModel):
    ip_address: str
    reason: Optional[str] = "Manual entry by Captain SIEM"

    @field_validator("ip_address")
    @classmethod
    def validate_ipv4(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("ip_address cannot be empty")
        v = v.strip()
        try:
            addr = ipaddress.IPv4Address(v)
            return str(addr)
        except Exception:
            raise ValueError(f"'{v}' is not a valid IPv4 address")


class WatchlistRequest(BaseModel):
    ip_address: str
    risk_level: Optional[str] = "HIGH"
    reason: Optional[str] = "Reconnaissance probe detected"

    @field_validator("ip_address")
    @classmethod
    def validate_ipv4(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("ip_address cannot be empty")
        v = v.strip()
        try:
            addr = ipaddress.IPv4Address(v)
            return str(addr)
        except Exception:
            raise ValueError(f"'{v}' is not a valid IPv4 address")


class ThreatIntelData(BaseModel):
    ip_address: str
    verdict: str  # "MALICIOUS" | "SUSPICIOUS" | "BENIGN"
    abuse_score: int  # 0 to 100
    threat_actor: Optional[str] = None
    category: str
    asn: str
    country: str
    country_code: str
    flag: str
    indicators: List[str] = Field(default_factory=list)
    last_seen: Optional[str] = None


class Alert(BaseModel):
    id: str
    timestamp: datetime
    rule_name: str
    severity: SeverityLevel
    description: str
    ip_address: Optional[str] = None
    user_id: Optional[str] = None
    status: str = "NEW"  # NEW | CONTAINED | RESOLVED
    details: dict = Field(default_factory=dict)
    rule_id: Optional[str] = None
    mitre: Optional[MitreAttack] = None
    threat_intel: Optional[ThreatIntelData] = None


class IsolateHostRequest(BaseModel):
    ip_address: str
    reason: Optional[str] = "Contained by SOC Analyst via Active Defense"
    analyst: Optional[str] = "SOC Analyst Tier-1"

    @field_validator("ip_address")
    @classmethod
    def validate_ipv4(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("ip_address cannot be empty")
        v = v.strip()
        try:
            addr = ipaddress.IPv4Address(v)
            return str(addr)
        except Exception:
            raise ValueError(f"'{v}' is not a valid IPv4 address")


class ReleaseHostRequest(BaseModel):
    ip_address: str
    analyst: Optional[str] = "SOC Analyst Tier-1"

    @field_validator("ip_address")
    @classmethod
    def validate_ipv4(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("ip_address cannot be empty")
        v = v.strip()
        try:
            addr = ipaddress.IPv4Address(v)
            return str(addr)
        except Exception:
            raise ValueError(f"'{v}' is not a valid IPv4 address")


class SuspendUserRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    reason: Optional[str] = "Account suspended by SOC Analyst due to credential compromise / impossible travel"
    analyst: Optional[str] = "SOC Analyst Tier-1"

    @field_validator("user_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("user_id cannot be empty")
        return v.strip()


class UnsuspendUserRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    analyst: Optional[str] = "SOC Analyst Tier-1"

    @field_validator("user_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("user_id cannot be empty")
        return v.strip()


# ---------------- INCIDENT CASE MANAGEMENT (THEHIVE STANDARD) ----------------

CaseStatus = Literal["OPEN", "IN_PROGRESS", "CLOSED"]
CaseVerdict = Literal["TRUE_POSITIVE", "FALSE_POSITIVE", "BENIGN", "UNDETERMINED"]
CaseTLP = Literal["TLP:WHITE", "TLP:GREEN", "TLP:AMBER", "TLP:RED"]


class CaseObservable(BaseModel):
    type: str  # "ip", "user", "device", "rule"
    value: str
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CaseNote(BaseModel):
    id: str
    timestamp: datetime
    author: str
    content: str


class CaseResolution(BaseModel):
    verdict: CaseVerdict
    summary: str
    closed_at: datetime
    closed_by: str


class IncidentCase(BaseModel):
    id: str  # e.g., "CASE-2026-001"
    title: str
    description: str
    created_at: datetime
    severity: SeverityLevel
    status: CaseStatus = "OPEN"
    assigned_to: Optional[str] = "SOC Analyst Tier-1"
    tlp: CaseTLP = "TLP:AMBER"
    linked_alert_ids: List[str] = Field(default_factory=list)
    observables: List[CaseObservable] = Field(default_factory=list)
    notes: List[CaseNote] = Field(default_factory=list)
    resolution: Optional[CaseResolution] = None


class EscalateAlertRequest(BaseModel):
    alert_id: str
    title: Optional[str] = None
    analyst: Optional[str] = "SOC Analyst Tier-1"
    severity: Optional[SeverityLevel] = None
    tlp: Optional[CaseTLP] = "TLP:AMBER"
    initial_note: Optional[str] = None


class AddCaseNoteRequest(BaseModel):
    author: Optional[str] = "SOC Analyst Tier-1"
    content: str = Field(..., min_length=1)


class UpdateCaseStatusRequest(BaseModel):
    status: CaseStatus
    verdict: Optional[CaseVerdict] = None
    summary: Optional[str] = None
    analyst: Optional[str] = "SOC Analyst Tier-1"

