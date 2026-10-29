import ipaddress
from datetime import datetime, timezone, timedelta
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


EventType = Literal["login_attempt", "web_request", "database_download", "recon_probe"]
EventStatus = Literal["success", "failed"]
SeverityLevel = Literal["KRITIS", "TINGGI", "MENENGAH"]


class LogEvent(BaseModel):
    timestamp: datetime
    event_type: EventType
    user_id: str = Field(..., min_length=1)
    ip_address: str
    location: str = Field(..., min_length=1)
    status: EventStatus

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


